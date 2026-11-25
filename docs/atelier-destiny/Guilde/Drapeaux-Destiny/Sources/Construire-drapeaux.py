#!/usr/bin/env python3
"""Post-process six generated Destiny ornaments into isolated 1× sprites and four palettes."""
from pathlib import Path
from io import BytesIO
import base64,csv,hashlib,json,zipfile
import numpy as np
from PIL import Image
from scipy import ndimage as nd

S=Path(__file__).resolve().parent; O=S.parent; G=O.parent; W=Path.home()/'.cache/drapeaux-destiny'; B=W/'bruts'
STOCK=G/'Guilde-Destiny-Lianes-et-PMU-100.html'; NEW=G/'Guilde-Destiny-Drapeaux-et-Lianes.html'
OPEN='<script id="donnees" type="application/json">'; CELL=(160,112); TONES=(12,40,78,118,159,203,248)
MODELES=[
 ('D01-Banniere-murale','banniere','Bannière murale',(40,66),True),
 ('D02-Drapeau-sur-hampe','hampe','Drapeau sur hampe',(67,80),False),
 ('D03-Gonfanon','gonfanon','Gonfanon de cérémonie',(45,90),False),
 ('D04-Guirlande-de-fanions','fanions','Guirlande de fanions',(144,40),True),
 ('D05-Tenture-de-salle','tenture','Tenture de salle',(104,54),True),
 ('D06-Ecu-mural','ecu','Écu mural',(43,46),True),
]

def write_json(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def cut_magenta(rgb):
 r,g,b=rgb.astype(np.int16).transpose(2,0,1);return (r>24)&(r>g+15)&(b>g+7)&(2*b>r)

def make_base(name,cap):
 raw=(B/(name+'.png')).read_bytes();rgb=np.array(Image.open(BytesIO(raw)).convert('RGB'))
 key=cut_magenta(rgb);lab,n=nd.label(~key,np.ones((3,3)));counts=np.bincount(lab.ravel());counts[0]=0
 best=np.argsort(counts)[::-1];assert counts[best[0]]>12000
 if name.startswith('D03'):
  # The generator returned three passes instead of one asset. Select the middle gonfalon and discard the others.
  large=[i for i in best[:3] if counts[i]>.5*counts[best[0]]];assert len(large)==3
  mainid=sorted(large,key=lambda i:np.median(np.where(lab==i)[1]))[1]
 else:
  mainid=best[0];assert counts[mainid]/(~key).sum()>.94,(name,counts[mainid],(~key).sum())
 matte=lab==mainid
 if np.count_nonzero(~key&~matte)<200:
  matte|=(~key)&(nd.distance_transform_edt(~matte)<=max(4,rgb.shape[0]//100))
 y,x=np.where(matte);x0,y0,x1,y1=map(int,(x.min(),y.min(),x.max()+1,y.max()+1));assert 0<x0<x1<rgb.shape[1] and 0<y0<y1<rgb.shape[0],name
 a=np.zeros((*rgb.shape[:2],4),np.uint8);a[matte,:3]=rgb[matte];a[matte,3]=255;im=Image.fromarray(a[y0:y1,x0:x1]);scale=min(cap[0]/im.width,cap[1]/im.height)
 im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.BOX);a=np.array(im)
 inside=(a[:,:,3]>=(88 if name.startswith('D04') else 112));stray=inside&cut_magenta(a[:,:,:3]);assert stray.sum()<=max(2,inside.sum()*.005)
 inside&=~stray;a[inside,3]=255;a[~inside]=0;y,x=np.where(inside);a=a[y.min():y.max()+1,x.min():x.max()+1]
 assert not (cut_magenta(a[:,:,:3])&(a[:,:,3]>0)).any(),name
 return a,dict(generation=name,sha256=sha(raw),rectangle_brut=[x0,y0,x1-x0,y1-y0],indice_composante=1 if name.startswith('D03') else 0)

def recolor(a,ident,p):
 rgb=a[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1);mask=a[:,:,3]>0;Y=.299*r+.587*g+.114*b;h,w=mask.shape;y,x=np.indices(mask.shape);x=x/w;y=y/h
 # Constrain coloured cloth/lacquer by both its hue and position. The ochre Destiny mark and its gold braid remain gold in all four versions.
 region={'banniere':y>.080,'hampe':(y>.095)&(y<.49)&(x>.20),'gonfanon':(y>.095)&(y<.71),'fanions':y>.18,'tenture':y>.093,'ecu':(y>.14)&(y<.90)&(x>.10)&(x<.90)}[ident]
 ratio=(r-g)/np.maximum(r-b,1.)
 strength=np.clip((ratio-.52)/.135,0.,1.)*np.clip((r-g-9)/15,0,1)*region*mask
 gold=mask&(r-b>35)&(g>120)&(ratio<.48)
 wood=mask&(r-b>14)&(r>g+4)&(g>=b)&~gold
 ink=mask&(Y<33);wood=wood&~ink;strength[ink]*=.70
 woods=np.asarray(p['bois']);tissus=np.asarray(p['textile']);shadow=np.clip(Y+.11*(r-Y),0,255)
 timber=np.stack([np.interp(Y,TONES,woods[:,i]) for i in range(3)],2)
 textile=np.stack([np.interp(shadow,TONES,tissus[:,i]) for i in range(3)],2)
 wood_strength=(.59 if p['id']=='ardoise' else .51)*wood*(1-strength)
 strength*=.95
 color=(rgb*(1-wood_strength[:,:,None])+timber*wood_strength[:,:,None]);color=color*(1-strength[:,:,None])+textile*strength[:,:,None]
 q=a.copy();q[:,:,:3]=np.clip(np.rint(color),0,255).astype(np.uint8);q[~mask]=0
 assert (strength>.50).sum()>mask.sum()*.09,(ident,p['id'],int((strength>.50).sum()),mask.sum())
 assert np.array_equal(q[:,:,3],a[:,:,3]);return q

def png(a):
 f=BytesIO();Image.fromarray(a).save(f,'PNG',optimize=True);return f.getvalue()

def patch(t,old,new):
 assert t.count(old)==1,old
 return t.replace(old,new,1)

def atlas(extra):
 raw=STOCK.read_bytes();source=raw.decode('utf-8');head,old=source.split(OPEN,1);body,tail=old.split('</script>',1);d=json.loads(body);dupe={**d,'catalog':d['catalog']+extra}
 assert len({a['id'] for a in dupe['catalog']})==len(dupe['catalog'])==157
 for prop in ('rooms','nuits','lumieres','lianes'):assert dupe[prop]==d[prop]
 head=patch(head,'<title>Destiny · Lianes de Reverie &amp; mobilier PMU</title>','<title>Destiny · Drapeaux, étendards et lianes</title>')
 head=patch(head,'<strong>100</strong><span>VARIANTES</span>','<strong>24</strong><span>ORNEMENTS</span>')
 head=patch(head,'Des lianes inspirées de Reverie suivent les boiseries. À la nuit, leurs bourgeons éclairent murs et planchers. À toi de placer le mobilier.', 'Drapeaux, gonfanons, fanions et tentures inspirés de l’emblème de la guilde. Les lianes de Reverie éclairent toujours les boiseries en Nuit. À toi de placer les ornements.')
 head=patch(head,'<option value="pmu100">100 variantes</option>', '<option value="drapeaux" selected>Drapeaux et tentures · 24</option><option value="pmu100">100 variantes PMU</option>')
 head=patch(head,'id="catalog-count">100','id="catalog-count">24')
 head=patch(head,'Les 100 variantes et les lianes ne sont pas exportées vers Destiny.', 'Les 100 variantes, les nouveaux ornements et les lianes ne sont pas exportés vers Destiny.')
 tail=patch(tail,"collection:'pmu100',palette:'tout',lianes:true", "collection:'drapeaux',palette:'tout',lianes:true")
 tail=patch(tail,'pmd-destiny:guilde:lianes-pmu100:077:v1','pmd-destiny:guilde:drapeaux-lianes:077:v1')
 tail=patch(tail,"'Indisponible avec les 100 variantes d’atelier.'", "'Indisponible avec les nouvelles variantes et les ornements d’atelier.'")
 (NEW).write_text(head+OPEN+json.dumps(dupe,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+tail,encoding='utf-8')
 assert STOCK.read_bytes()==raw

def main():
 palettes=json.loads((G/'Objets-PMU-100/Index-100.json').read_bytes())['palettes'];assert len(palettes)==4
 dest=O/'PNG';dest.mkdir(parents=True,exist_ok=True)
 planche=Image.new('RGBA',(6*CELL[0],4*CELL[1]));chart=[];extra=[];hashes=set();valid={}
 for j,(src,ident,label,maxi,mural) in enumerate(MODELES):
  a,origin=make_base(src,maxi);print(label,a.shape[1],a.shape[0],flush=True)
  for i,p in enumerate(palettes):
   aid='destiny_'+ident+'_'+p['id'];b=recolor(a,ident,p);h,w=b.shape[:2];cx,cy=j*CELL[0],i*CELL[1];x,y=cx+(CELL[0]-w)//2,cy+(CELL[1]-h)//2
   assert cx<x<x+w<cx+CELL[0] and cy<y<y+h<cy+CELL[1];planche.paste(Image.fromarray(b),(x,y));data=png(b);digest=sha(data);assert digest not in hashes;hashes.add(digest)
   f=f'{j+1:02}-{ident}-{p["id"]}.png';(dest/f).write_bytes(data);number=i*6+j+1
   entry=dict(numero=number,id=aid,nom=label,palette=p['nom'],palette_id=p['id'],fichier='PNG/'+f,cellule=[cx,cy,*CELL],rectangle=[x,y,w,h],mural=mural,ancre=[w//2,h-3],sha256=digest,source=origin)
   chart.append(entry);extra.append(dict(n=number,id=aid,label=label+' · '+p['nom'],category='panneaux' if mural else 'meubles',wall=mural,w=w,h=h,palette=p['id'],collection='drapeaux',previewOnly=True,m=[base64.b64encode(data).decode('ascii')]))
  valid[ident]=a[:,:,3]
 chart.sort(key=lambda c:c['numero']);extra.sort(key=lambda r:r['n']);assert [c['numero'] for c in chart]==list(range(1,25))
 sheet=O/'Tilesheet-Drapeaux-Destiny-24.png';planche.save(sheet,optimize=True);a=np.asarray(Image.open(sheet).convert('RGBA'));occupied=np.zeros(a.shape[:2],bool)
 for row in chart:
  x,y,w,h=row['rectangle'];q=np.array(Image.open(O/row['fichier']).convert('RGBA'));assert np.array_equal(q,a[y:y+h,x:x+w]);assert not occupied[y:y+h,x:x+w].any();occupied[y:y+h,x:x+w]=True
 assert not a[~occupied,3].any()
 write_json(O/'Index-drapeaux.json',dict(total=24,modeles=6,palettes=[p['nom'] for p in palettes],grille=[6,4],cellule_px=list(CELL),taille_px=list(planche.size),tuile_logique_px=8,sprites=chart))
 with (O/'Index-drapeaux.csv').open('w',encoding='utf-8-sig',newline='') as f:
  cw=csv.writer(f,delimiter=';');cw.writerow(['N°','Nom','Palette','x','y','Largeur','Hauteur','Fichier']);cw.writerows([q['numero'],q['nom'],q['palette'],*q['rectangle'],q['fichier']] for q in chart)
 atlas(extra)
 kit=O/'Kit-Drapeaux-Destiny-24.zip'
 with zipfile.ZipFile(kit,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in (O/'Lisez-moi.md',sheet,O/'Index-drapeaux.json',O/'Index-drapeaux.csv',NEW):z.write(p,p.name)
  for row in chart:z.write(O/row['fichier'],row['fichier'])
 with zipfile.ZipFile(kit) as z:
  assert z.testzip() is None and len([n for n in z.namelist() if n.startswith('PNG/')])==24
  for row in chart:assert sha(z.read(row['fichier']))==row['sha256']
 print('PASS · 6 créations générées × 4 palettes · 24 sprites isolés · atelier indépendant.',flush=True)
if __name__=='__main__':main()
