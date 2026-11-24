#!/usr/bin/env python3
"""Pack every independent furnishing from the existing workshop, PMU kit and Destiny .dir bank.
8 poses per object, reusable native dimensions and pivot metadata. Sources are read-only.
"""
from pathlib import Path
from collections import Counter
from functools import cache
from itertools import chain
from io import BytesIO
import base64,zipfile,hashlib,re,struct,json,sys,unicodedata
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];G=ROOT.parent;PREV=G/'Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html';KIT=G/'PMU-Orientations/Kit-Destiny-PMU-8-orientations.zip'
W=Path.home()/'.cache/atelier-destiny-8-sens';K=W/'Kit';K.mkdir(parents=True,exist_ok=True);A=K/'Atelier';A.mkdir(exist_ok=True);R=Path.home()/'.cache/fenetres-jeu-destiny/runtime-077/Content/Object'
P=G/'PMU-Orientations/Sources';sys.path.insert(0,str(P));from Volumes import view,flat,DIRS,Model
from Reconstituer import build,THICKNESS
from Produire import trim


def h(x):return hashlib.sha256(x).hexdigest()
def dump(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def compact(a):return json.dumps(a,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def raw_b64(s):return base64.b64decode(s.split(',')[-1])
def img(b):return Image.open(BytesIO(b)).convert('RGBA')
def img64(s):return img(raw_b64(s))
def png(a):b=BytesIO();a.save(b,format='PNG',compress_level=6);return b.getvalue()
def uri(b,t='png'):return f'data:image/{t};base64,'+base64.b64encode(b).decode()
def norm(n):return re.sub('[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',str(n).lower()) if not unicodedata.combining(c)))

def prev():return json.loads(re.search(r'<script id="donnees"[^>]*>(.*?)</script>',PREV.read_text(),re.S)[1])

class Pages:
    """Small on-demand atlases; avoid 8,000 files / duplicate sprites. Transparent gutters."""
    def __init__(self,s=1536):self.s=s;self.p=Image.new('RGBA',(s,s));self.i=0;self.x=self.y=2;self.row=0;self.box={};self.entries=[]
    def finish(self):
        if max(self.y,self.row)<=2:return
        a=self.p.crop((0,0,self.s,self.y+self.row+2));b=png(a);n=f'Page-{self.i:02d}.js';(A/n).write_text(f'window.bankPage({self.i},{compact(uri(b))});',encoding='ascii');self.entries.append({'page':self.i,'file':'Atelier/'+n,'w':a.width,'h':a.height,'sha256':h(b)});
        self.i+=1;self.p=Image.new('RGBA',(self.s,self.s));self.x=self.y=2;self.row=0
    def sprite(self,a,p):
        a=a.convert('RGBA');w,t=a.size;x,y=p;assert a.getbbox() and -w<=x<=w*2 and -t<=y<=t*2
        eid=(a.size,h(a.tobytes()));r=self.box.get(eid)
        if r is None:
            if self.x+w+2>self.s:self.x=2;self.y+=self.row+2;self.row=0
            if self.y+t+2>self.s:self.finish()
            assert w+4<self.s and t+4<self.s
            r=[self.i,self.x,self.y,w,t];self.p.paste(a,(self.x,self.y));self.box[eid]=r;self.x+=w+2;self.row=max(self.row,t)
        return r+list(p)

M={}

def shape(row,a):
    s=norm(row.get('halcyon','')+' '+row['id']+' '+row['label'].split('·')[0]);w,t=a.size
    def has(n):return any(re.search(r'\b'+v,s) for v in n.split('|'))
    if has('tapis|paillasson|carpette|rug'):return 'sol'
    if row['wall'] or has('panneau|fanion|enseigne|lierre mural|tabl[e]?au|etoile murale|miroir|horloge mural|lampion mural'):
        if has('tenture|fanion|banniere|drapeau|gonfanon|toile'):return 'toile'
        return 'miroir' if has('miroir') else 'panneau'
    if has('comptoir|counter|service'):return 'bahut'
    if has('biblio|rayon|armoire|fichier'):return 'biblio'
    if has('banquet'):return 'banquet'
    if has('cuisine|fourneau|cheminee|foyer|poele'):return 'foyer'
    if has('bureau|pupitre'):return 'pupitre'
    if has('drapeau|banniere|hampe|gonfanon'):return 'drapeau'
    if has('lit|berceau|paillasse'):return 'lit-long' if w>t*1.9 and t>22 else 'lit'
    if has('table ronde|souche|tonneau|boule|orb|noisette'):return 'souche'
    if has('table|mangeoire|repose'):return 'table'
    if has('banc'):return 'banc'
    if has('fauteuil|siege|canape|coussinet|sofa|chaise|trone'):return 'siege'
    if has('coffre|cassette'):return 'coffre-ouvert' if has('ouvert') else 'coffre'
    if has('caisse|boite|casier|cajot|etagere|reser'):return 'caisse' if has('caisse|boite|cajot') else 'etagere'
    if has('lampe|luminaire|bougie|cand[eé]labre|torche|brasero'):return 'luminaire'
    if has('plante|feuilla|fleur|bouquet|gerbe|vase|pommier'):return 'plante'
    if has('seau|pot|vase|jarre|corbeille|panier|ecuelle'):return 'pot'
    if has('porte|hublot|fenetre|poteau|pilier'):return 'paroi'
    if has('livre|diary|aliment|food|nourriture|journal|fruit|buches|pierre|caillou'):return 'pile'
    if has('linge|paquet|coussin|sac'):return 'coussin'
    if w<=24 or t<=18:return 'relief'
    return 'bahut' if w>t*1.06 else 'relief'


def posed(pic,kind):
    a=np.array(pic);a[a[...,3]==0]=0
    raw,rx,ry=trim(a,0);mask=a[...,3]>=128;v=127 if mask.any() else 0
    core,x,y=trim(a,v);core[core[...,3]<=v]=0
    if core.shape[0]<4 or core.shape[1]<3:kind='sol' if kind=='sol' else 'relief'
    if kind=='sol':
        px,py=core.shape[1]//2,core.shape[0]//2
        res=[flat(core,i) for i in range(8)]
    else:
        gid=(kind,core.shape,h((core[...,3]>0).tobytes()))
        try:
            if gid not in M:
                md=build(core,kind);M[gid]=(md.geom,md.pivot,md.pigment)
            else:
                geom,pivot,mat=M[gid];md=Model(core,geom,pivot,kind,mat)
            res=[view(md,i) for i in range(8)];px,py=md.pivot
            if not all(pic[...,3].any() for pic,*_ in res):raise ValueError('degenerate outline')
        except (ValueError,AssertionError,IndexError) as e:
            # Skin-thin or sub-4 px decorative fragments get a one-pixel relief, not a rotated upright square.
            hh,ww=core.shape[:2];pillar=core[::-1,:,3]>=128
            if not pillar.any():pillar=core[::-1,:,3]>0
            gg=np.zeros((hh,3,ww),dtype=np.uint8);gg[:,1,:]=pillar.astype(np.uint8);md=Model(core,gg,(ww/2,hh-.5),'relief','bois');px,py=md.pivot;res=[view(md,i) for i in range(8)];kind='relief fin'
    res[0]=(raw,np.zeros(raw.shape[:2]),-round(x+px-rx),-round(y+py-ry));return [(Image.fromarray(p),(-i,-j)) for p,d,i,j in res],kind


def read_dir(p):
    b=p.read_bytes();n,=struct.unpack_from('<q',b);w,t,rs,f=struct.unpack_from('<4i',b,n+8);a=np.array(img(b[8:8+n]));al=a[...,3];assert a.shape==(t,w,4) and rs==0 and f==1
    hit=al>0;a[~hit]=0
    if hit.any() and (a[hit,:3]<=al[hit,None]).all():a[hit,:3]=np.clip(np.rint(a[hit,:3].astype(float)*255/al[hit,None]),0,255).astype(np.uint8)
    return Image.fromarray(a),h(b)


def cm(p,src,prevs):
    raw=[]
    i=0
    with zipfile.ZipFile(KIT) as z:
        j=json.loads(z.read('Index-PMU-8.json'));assert j['nombre']==360
        for row in j['objets']:
            a=img(z.read(row['atlas']['fichier']));vv=[]
            for d in row['vues']:
                x,y,w,t=d['rectangle_atlas'];b=a.crop((x,y,x+w,y+t));vv.append(p.sprite(b,d['pivot']))
            id0=row['id'];rr=src.get(id0);aliases=[rr['id'],id0] if rr else [id0];lab=rr['label'] if rr else row['nom'];id1=rr['id'] if rr else id0
            # Each old Down image is exact. Preserve its catalog alias even when shipped in the PMU bank.
            if rr:
                f0=row['vues'][0];x,y,w,hh=f0['rectangle_atlas'];b=a.crop((x,y,x+w,y+hh));f=img64(rr['m'][0]);f=f.crop(f.getbbox());assert np.array_equal(np.array(f),np.array(b)),id0
            raw.append(dict(id=id1,nom=lab,code=row['repere'],alias=aliases,famille='Immobilier de la guilde' if rr else 'PMU de Destiny',source='PMU 0.7.7 · '+row['famille'],gabarit=row['gabarit'],mur=bool(rr['wall'] if rr else row['fixation']=='mur'),v=vv,plan=row['gabarit']=='sol'))
            prevs.update(aliases)
    return raw


def placed_special(p,D,byid,prevs):
    comp=[]
    for (title,geo,kind,key) in [('Comptoir à cloche en U',D['comptoirs']['orientations'],'comptoir','comptoir-u'),('Étendard au gland',D['extensions']['drapeaux'],'drapeau','etendard')]:
        dct={t['direction']:t for t in geo};vs=[];anim=[];alias=[]
        for dr in DIRS:
            t=dct[dr];id=t['id'];i=byid[id];base=img64(i['m'][0]);x,y=t['pivot'];vs.append(p.sprite(base,(x,y)));alias.append(id)
            if e:=D['etoffes'].get(id):
                atlas=img64(e['s']);fr=[]
                for k in range(e['n']):
                    u,v=k%e['c']*base.width,k//e['c']*base.height;fr.append(p.sprite(atlas.crop((u,v,u+base.width,v+base.height)),(x,y)))
                anim.append([e['dt'],fr])
        prevs.update(alias);comp.append(dict(id=key,nom=title,code=key,alias=alias,famille='Comptoirs & drapeaux',source='8 vues déjà dessinées',gabarit=kind,mur=False,v=vs,anim=anim,plan=False))
    return comp


def rooms(D):
    rooms=[]
    # Native raster + foreground and phase layer, with the prior shelves kept separate in the JSON.
    for r in D['rooms']:
        n=r['id'];front=img64(r['front']);images=[];B=img64(r['base']);assert B.size==(r['w'],r['h'])
        s=D.get('extensions',{}).get('biblio')
        for i in (0,3):
            dst=B.copy()
            if i==3:
                lum=Image.new('RGBA',dst.size,(26,31,60,93));lum.putalpha(dst.getchannel('A').point(lambda a:round(a*.38)));dst.alpha_composite(lum)
            for x,y,src in r['patches'][i]:dst.alpha_composite(img64(src),(x,y))
            if s and n==s['salle']:
                for f in s['slots']:dst.alpha_composite(img64(f['choix'][f['defaut']]['png']),tuple(f['xy']))
            images.append(uri(png(dst)))
        if s and n==s['salle']:
            out=np.array(front);aa=out[...,3]
            for ch in s['slots']:
                x,y=ch['xy'];a0=img64(ch['choix'][ch['defaut']]['png']);z=np.asarray(a0)[...,3]>0;aa[y:y+a0.height,x:x+a0.width][z]=0
            out[aa==0]=0;front=Image.fromarray(out)
        fg=uri(png(front));row=dict(id=n,nom=r['label'],w=r['w'],h=r['h'],sol=r['floor'],seuils=r['gates'],images=images,front=fg)
        q=D['extensions']['foyers']
        if n==q['salle']:
            ur=lambda x:uri(raw_b64(x))
            row['foyers']={'ombre':[*q['ombre'][:2],ur(q['ombre'][2])],'reflets':[[x,y,ur(z)] for x,y,z in q['reflets']],'modules':[[*it['xy'],*it['size'],ur(it['anime'][0]),ur(it['anime'][3])] for it in q['modules']]}
        rooms.append(row)
    return rooms


def main():
    D=prev();B={r['id']:r for r in D['catalog']};seen=set();pg=Pages();src={r['sheet']:r for r in B.values() if 'sheet'in r}
    assert len(src)==33 and len(B)==693
    data=cm(pg,src,seen);data+=placed_special(pg,D,B,seen)
    native=sorted(R.glob('Guilde_Imm*.dir'));assert len(native)==135
    todo=[(r,None) for r in B.values() if r['id'] not in seen]+[(None,p) for p in native if p.stem not in seen]
    for j,(r,file) in enumerate(todo):
        if file:
            I,hh=read_dir(file);code=file.stem;n=code.removeprefix('Guilde_Imm_').replace('_',' ');lab=n.capitalize()
            r={'id':code,'label':lab,'wall':bool(re.search(r'mural|lierre|tenture|banniere',n))};fam='Immobilier natif 0.7.7';source={'fichier':file.name,'sha256_dir':hh}
        else:
            I=img64(r['m'][0]);code=r['id'];lab=r['label'];fam={'halcyon':'Halcyon','metano':'Auberge de Metano','halcyon-ia':'Halcyon · créations','pmu100':'Nuancier PMU','drapeaux':'Comptoirs & drapeaux'}.get(r.get('collection'),'Immobilier de la guilde');source='Atelier Destiny · '+fam
        kind=shape(r,I);V,real=posed(I,kind)
        assert np.array_equal(np.array(V[0][0]),np.array(I.crop(I.getbbox()))),(code,I.size,V[0][0].size)
        e=dict(id=code,nom=lab,code=code,alias=[code],famille=fam,source=source,gabarit=real,mur=bool(r['wall']),v=[pg.sprite(a,ax) for a,ax in V],plan=real=='sol')
        data.append(e);seen.add(code)
        if j%90==0:print(f'{j+1}/{len(todo)} · {code}',flush=True)
    # Derive only after merging aliases. Existing artwork and PNG atlas remain untouched.
    ids=[i['id'] for i in data];assert len(ids)==len(set(ids)) and set(B)<=seen and {p.stem for p in native}<=seen
    assert all(len(t['v'])==8 for t in data)
    pg.finish();roomsdata=rooms(D)
    data.sort(key=lambda e:(e['famille'],norm(e['nom']),e['id']))
    cells={'ids':len(data),'vues':len(data)*8,'catalogue_couvert':len(B),'ressources_Guilde_Imm':len(native),'pmu_repris':360,'familles':dict(Counter(e['famille'] for e in data)),'recettes':dict(Counter(e['gabarit'] for e in data)),'sprites_distincts':len(pg.box),'pages':len(pg.entries),'sha256_atelier_avant':h(PREV.read_bytes()),'sha256_coffret_pmu':h(KIT.read_bytes())}
    packet={'ob':data,'dirs':list(DIRS),'pages':pg.entries,'rooms':roomsdata,'chiffres':cells,'notes':'8 angles dont 7 reconstitués lorsque la source ne possède qu’une vue. Le miroir est indépendant et ancré.'}
    (A/'Banque.js').write_text('window.DESTINY_POSE='+compact(packet)+';\n',encoding='utf8');dump(ROOT/'Releve-Banque.json',cells);print(cells,flush=True)

if __name__=='__main__':main()
