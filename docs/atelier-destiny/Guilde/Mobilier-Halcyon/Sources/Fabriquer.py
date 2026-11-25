#!/usr/bin/env python3
"""Teintes Destiny sur les objets Halcyon en RGBA natif, matériaux indépendants."""
from pathlib import Path
from PIL import Image
from collections import Counter
import csv, hashlib, json
import numpy as np

S = Path(__file__).resolve().parent
O = S.parent

CREME = ['594329', '806a4d', 'b49a71', 'dec9a3', 'fbf2da']
HAY = ['44361d', '6b542f', 'a08b53', 'c7af72', 'e6d097']
EAU = ['1a2e37', '375563', '527c86', '7ba5ad', 'b4cdd0']
STONE = ['2b272e', '4b4248', '6e6266', '988887', 'c3adab']
LUMA = np.array([.2126,.7152,.0722])
VECT = np.array([0,.25,.50,.75,1.])
FRINGE = ['d4cba8', 'eeeed4', 'a89f8e']
REGLAGES = {
    'bois':(.04,.97), 'tissu':(.08,.93), 'trame':(.45,.65), 'herald':(.23,.72),
    'frange':(.34,.97), 'galon':(.28,.97), 'metal':(.06,.98), 'pierre':(.10,.90),
    'feuille':(.03,1.), 'papier':(.43,.995), 'vitre':(.20,.92), 'paille':(.12,.98),
    'ceramique':(.06,.97), 'encre':(.10,.93), 'cercles':(.06,.44), 'ombre':(0,0), 'baie':(0,0),
}
CREDITS = 'Halcyon (Palika) · décors intérieurs crédités à D4yz et Edan Momu dans le dépôt ; teintes Destiny.'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rgb(color):
    return [int(color[i:i+2],16) for i in (0,2,4)]


def ramp(colors):
    return np.array([rgb(c) for c in colors],dtype=float)


def cables(p):
    wood,cloth,metal,leaf=map(ramp,(p['bois'],p['tissu'],p['metal'],p['feuille']))
    leaf=np.stack([np.interp(VECT,[0,.5,1],leaf[:,i]) for i in range(3)],axis=1)
    creme,straw,water,stone=map(ramp,(CREME,HAY,EAU,STONE))
    blend=lambda a,b,t:a*(1-t)+b*t
    return {'bois':wood,'tissu':cloth,'trame':cloth,'herald':cloth,'frange':blend(metal,creme,.63),
            'galon':blend(metal,creme,.23),'metal':metal,'pierre':blend(blend(wood,metal,.59),stone,.24),
            'feuille':leaf,'papier':blend(creme,metal,.12),'vitre':blend(water,cloth,.37),
            'paille':blend(straw,blend(wood,cloth,.36),.63),'ceramique':blend(cloth,metal,.29),'encre':blend(wood,cloth,.52),
            'cercles':blend(wood,metal,.29)}


def masses(a, modele):
    recette=modele['materiau'];rr,gg,bb,aa=a.astype(int).transpose(2,0,1);ok=aa>0
    y,x=np.indices(ok.shape); height,width=ok.shape
    warm=(rr>gg+16)&(gg>bb+7);red=(rr>gg+40)&(rr>bb+27)&(gg<rr*.62)&(rr>80);blue=(bb>rr+18)&(bb>gg+4);aqua=(gg>rr+8)&(bb>rr+8);green=(gg>rr+7)&(gg>bb+9)
    sat=np.maximum.reduce([rr,gg,bb])-np.minimum.reduce([rr,gg,bb]); light=np.minimum.reduce([rr,gg,bb]);orange=(rr>gg+18)&(bb<gg*.83)
    code=(rr<<16)|(gg<<8)|bb
    colors=lambda ss:np.isin(code,[int(c,16) for c in ss.split()])
    role=np.full(ok.shape,'bois',dtype='<U10');role[~ok]=''
    def put(label,m):role[m&ok]=label
    if recette in ('rug','herald'):
        put('trame' if recette=='rug' else 'herald',ok)
        put('frange',colors(' '.join(FRINGE)))
        if recette=='herald':put('galon',(rr>160)&(gg>150)&(bb<145))
    elif recette=='banner':
        put('tissu',y>=35);put('bois',(y<39)&(rr>=gg+10)&(bb>10))
        put('galon',(y>=45)&(rr>150)&(gg>130)&(rr>gg*.9))
    elif recette=='board':
        put('papier',(light>=100)&(sat<104)&(x>=9)&(x<47)&(y>=8)&(y<31))
        put('galon',colors('d89830 d08828 e0a038 f0b848 a87830'))
    elif recette=='counter':
        put('pierre',ok);put('metal',(x>39)&(y<=15)&(gg>=rr-65)&((gg-bb>30)|(light>185)|colors('5d3d0b 975d12')))
    elif recette=='table':
        put('ceramique',colors('e0e868 d8e060 c8c858 e8e890 d8d858'))
        put('galon',colors('d8a048 b8a848')&(y<10))
        put('ombre',aa<128)
    elif recette=='desk':
        put('papier',(sat<95)&(y<55)&(y>2)&(x>10)&(x<37)&((light>54)|colors('000000')))
        put('tissu',blue|(colors('870000 b71f1f 000087 ffc700 e78700')&(y<64)))
        put('encre',colors('572f27 6f473f 7f574f 9f7787 b78f8f 976f57 a7875f'))
    elif recette=='chest':
        put('metal',ok);put('tissu',green|blue|aqua|((sat>12)&(rr<110)&(gg>rr+3)&(gg>bb*.9)))
    elif recette=='treasure':
        put('metal',((sat<53)&(rr>130)&(gg>108))|colors('755827'))
        put('baie',(y>height*.31)&(red|green|blue|((rr>170)&(gg>150)&(rr-gg<45))))
    elif recette in ('apples','stock'):
        put('baie',red|green|blue|colors('c63918 782018 b01810 d03028 f86060'))
        if recette=='stock':put('ceramique',(x<34)&(y<31)&(gg>bb+10)&(rr>100))
    elif recette=='barrel':
        # Teinte sombre des cercles indépendamment des douves.
        put('cercles',colors('523908 634210 634a31 735a3a'))
    elif recette=='window':
        put('vitre',aqua|blue|(bb>rr-6)&(gg>rr+4))
    elif recette in ('plant','ivy'):
        put('feuille',green|((recette=='ivy')&(~red)&(~aqua)&(gg>=rr-2)))
        if recette=='plant':put('tissu',(y<height*.74)&((rr>gg+14)&(bb>gg-6)&(rr>65)))
        if recette=='plant' and modele['id']=='fleurs-metano':
            put('tissu',(y<14)&((rr>gg+15)&(bb>gg-24)));put('feuille',(gg>=rr-3)&(y<13)&(~red))
    elif recette=='cups':
        put('ceramique',ok);put('vitre',aqua|blue);put('galon',(rr>160)&(gg>140)&(rr<gg+66)&(bb<125))
    elif recette=='pouch':
        put('frange',ok);put('tissu',green);put('metal',sat<33)
    elif recette.startswith('basket'):
        put('ceramique',ok)
        if recette=='basket_red':put('baie',(y<=11)&(red|green|colors('ceffbd c63918 ad9c29 b5bd63')))
        elif recette=='basket_blue':put('baie',blue|aqua|colors('fffffe'))
        else:
            put('baie',(red|green|blue|aqua|((rr>=180)&(gg>=140)&(rr-gg<48)))&(y<(height-6)))
    elif recette=='bag':
        put('frange',ok);put('tissu',red|colors('b74f3f cf6757 973f37'))
    elif recette=='linen':
        put('frange',ok);put('tissu',orange|(gg-bb>50));put('encre',(rr<85)&(gg<69))
    elif recette=='book':
        put('papier',ok);put('tissu',red|colors('870000 b71f1f'));put('encre',colors('000000 676787'))
    elif recette=='straw':put('paille',ok)
    elif recette=='bench':
        centre=(x>15)&(x<width-15);put('tissu',centre&colors('f76545 ee2e3d ee9f4d eec24d'))
        put('feuille',(~centre)&(y>=12)&green)
        put('papier',(~centre)&(y>=12)&(sat<65)&(light>165))
        put('ceramique',(~centre)&(y>=17)&(rr>gg+12)&(~green))
    elif recette=='stump':
        centre=(x>=13)&(x<=33)&(y>=9)&(y<=26)
        put('feuille',green)
        put('baie',centre&(red|green|colors('202800 131900')))
        put('baie',colors('c80000'))
    assert (role[ok]!='').all() and (role[~ok]=='').all()
    return role


def appliquer(a,model,p,roles=None):
    roles=masses(a,model) if roles is None else roles
    dst=a.copy();shades=cables(p)
    for material,colors in shades.items():
        mask=roles==material
        if not mask.any():continue
        source=a[mask,:3];indices,inv=np.unique(source,axis=0,return_inverse=True)
        lum=indices@LUMA
        if len(lum)==1:
            t=np.full_like(lum,.58)
        else:
            # Un peu de rang pour ne pas perdre des nuances fines de texture.
            order=np.argsort(lum,kind='stable');rank=np.empty(len(lum));rank[order]=np.linspace(0,1,len(lum))
            t=.83*(lum-lum.min())/max(1e-6,lum.max()-lum.min())+.17*rank
            t=t**.98
        a0,b0=REGLAGES[material];t=a0+(b0-a0)*t
        if material=='papier' and model['materiau'] in ('desk','book'):
            t=.19+.80*((lum/255.)**.72)
        vals=np.array([np.interp(t,VECT,colors[:,i]) for i in range(3)]).T
        dst[mask,:3]=np.clip(np.rint(vals[inv]),0,255).astype(np.uint8)
    assert np.array_equal(a[...,3],dst[...,3]) and (dst[dst[...,3]==0]==0).all()
    return dst


def sha(b):return hashlib.sha256(b).hexdigest()


def fabriquer(modele, palettes):
    art=O/'PNG-1x'; atlas=O/'Atlas-1x'
    art.mkdir(exist_ok=True);atlas.mkdir(exist_ok=True)
    variants=[]; corpus=set(); sources={};audit=[]
    for m in modele:
        a=np.array(Image.open(O/'Originaux-1x'/(m['id']+'.png')).convert('RGBA'))
        assert sha(a.tobytes()) == m['pixels_sha256'] and a.shape[:2]==(m['rect'][3],m['rect'][2]),m['id']
        sources[m['id']]=(a,masses(a,m))
    assert len({m['pixels_sha256'] for m in modele}) == len(modele)
    for k,p in enumerate(palettes,1):
        dest=art/p['id'];dest.mkdir(exist_ok=True);f_atlas=atlas/(f'{k:02}-{p["id"]}.png')
        case_x,case_y=192,112;cols=7
        can=Image.new('RGBA',(cols*case_x, ((len(modele)+cols-1)//cols)*case_y))
        for i,m in enumerate(modele):
            a,roles=sources[m['id']];result=appliquer(a,m,p,roles);im=Image.fromarray(result)
            sha1=sha(result.tobytes());assert sha1 not in corpus,(m['id'],p['id']);corpus.add(sha1)
            frac=np.count_nonzero(np.any(result!=a,axis=2))/np.count_nonzero(a[...,3])
            assert frac>.27,(m['id'],p['id'],frac)
            out=dest/(m['id']+'.png');im.save(out,optimize=True)
            x=i%cols*case_x+(case_x-im.width)//2;y=i//cols*case_y+case_y-im.height-8
            can.alpha_composite(im,(x,y))
            variants.append({'id':f'halcyon-{m["id"]}-{p["id"]}','modele':m['id'],'nom':m['nom'],'origine':m['origine'],
              'famille':m['famille'],'palette':p['id'],'nom_palette':p['nom'],'w':im.width,'h':im.height,
              'png':out.relative_to(O).as_posix(),'atlas':f_atlas.relative_to(O).as_posix(),'rect_atlas':[x,y,*im.size],
              'rgb_modifie_pct':round(frac*100,1),'sha256':sha(out.read_bytes())})
        can.save(f_atlas,optimize=True)
    bymodel={m['id']:[v for v in variants if v['modele']==m['id']] for m in modele}
    for m in modele:
        a,roles=sources[m['id']];v=bymodel[m['id']];sa=v[0];props={k:int(np.count_nonzero(roles==k)) for k in np.unique(roles) if k}
        imgs=np.stack([np.array(Image.open(O/i['png'])) for i in v],axis=0);rgb=imgs[:,:, :, :3][:, a[...,3]>0].astype(float)
        # Vraies variations, pas une simple différence de somme de contrôle.
        pair=np.array([np.linalg.norm(rgb[i]-rgb[j],axis=-1).mean() for i in range(len(v)) for j in range(i)])
        assert pair.min()>3.,(m['id'],pair.min())
        audit.append(dict(modele=m['id'],distance_rgb_min=round(pair.min(),2),matieres=props))
        for i in v:
            x,y,w,h=i['rect_atlas']; assert (w,h)==(i['w'],i['h'])
            assert np.array_equal(np.asarray(Image.open(O/i['atlas']).crop((x,y,x+w,y+h))), np.asarray(Image.open(O/i['png']))), i['id']
    return variants,audit


def main():
    modele,palettes,refs=(load(S/f) for f in ('Modeles.json','Palettes.json','Provenance-brute.json'))
    variants,audit=fabriquer(modele,palettes);count=Counter(v['origine'] for v in variants)
    data={'format':'destiny-halcyon-rgba-1x-v1','source':{k:refs[k] for k in ('repo','commit')},'credits':CREDITS,
          'models':[{**m,'source_png':f'Originaux-1x/{m["id"]}.png','carte':f'Data/Ground/{m["salle"]}.rsground'} for m in modele],
          'palettes':palettes,'variantes':variants,'comptes':dict(count)}
    (O/'Index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    byid={m['id']:m for m in modele}
    with (O/'Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['identifiant','modèle','famille','origine','palette','largeur_px','hauteur_px','PNG','atlas','x_atlas','y_atlas','carte_source','x_source','y_source','calques_source','planches_source','commit_source'])
        for v in variants:
            m=byid[v['modele']];w.writerow([v['id'],v['nom'],v['famille'],v['origine'],v['nom_palette'],v['w'],v['h'],v['png'],v['atlas'],*v['rect_atlas'][:2],m['salle'],*m['rect'][:2],','.join(k for k,lim in m['calques']),','.join(m['planches']),refs['commit']])
    proof={'etat':'PASS','modeles':len(modele),'palettes':len(palettes),'variantes':len(variants),'provenances':dict(count),
           'alpha':'strictement identique au sprite Halcyon découpé','atlas':'toutes les cellules égales aux PNG','audit':audit}
    (O/'Verification-graphique.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print('PASS ·',len(variants),'PNG uniques et contrôlés ·',dict(count),'·',len(palettes),'atlas transparents')

if __name__=='__main__':main()
