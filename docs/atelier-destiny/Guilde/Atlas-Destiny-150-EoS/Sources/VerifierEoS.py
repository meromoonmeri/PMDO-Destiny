#!/usr/bin/env python3
"""Verify that the delivered map really uses the 8 original plates, no recoloring."""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1];A=R/'Apercu'/'assets';O=R.parent/'Atlas-Destiny-150'/'Apercu'/'assets';j=json.loads((A/'Lieux.json').read_text());o=json.loads((O/'Lieux.json').read_text())
fn=R/'Sources'/'Reference-EoS.png';orig=Image.open(fn).convert('RGB');sheet=Image.open(A/'Feuillets-EoS.png').convert('RGB');nt=j['eos']['nb_feuillets'];nw,nh=j['eos']['taille_native'];scale=j['eos']['echelle'];w,h=j['taille'];nn=Image.Resampling.NEAREST
sf=lambda p:sha256(p.read_bytes()).hexdigest()
assert sf(fn)==j['eos']['source_sha256'];assert nt==8 and (nw,nh)==(504,336) and (w,h)==(nw*scale,nh*scale)==(1512,1008)
assert (nw*4,nh*2)==sheet.size
exact=[]
for k,b in enumerate(j['eos']['cadrages_source']):
    sx,sy=k%4*nw,k//4*nh;n=orig.crop(b);p=sheet.crop((sx,sy,sx+nw,sy+nh));assert n.size==(nw,nh)
    assert n.tobytes()==p.tobytes(),k;exact.append(p)
assert len({p.tobytes()for p in exact})==8
base=Image.open(A/'Terrain.png').convert('RGB');monde=Image.open(A/'Monde-150.png').convert('RGB');native=Image.open(R/'Fond-EoS-Original-504x336.png').convert('RGB')
assert exact[-1].tobytes()==native.tobytes() and base.tobytes()==native.resize((1512,1008),nn).tobytes()
assert (A/'Lieux-150.png').read_bytes()==(O/'Lieux-150.png').read_bytes()
rows=j['lieux'];by={p['id']:p for p in o['lieux']};assert j['nb']==len(rows)==150==len({p['nom'] for p in rows})
assert j['par_region']==dict(Counter(p['region']for p in rows))
art=Image.open(A/'Vignettes-carte.png').convert('RGBA');final=base.convert('RGBA');ani=Image.open(A/'Animations.png').convert('RGBA');nnm=set();occ=np.zeros((h,w),bool);disp=np.stack([np.asarray(p) for p in exact]);diffs=[]
for p in sorted(rows,key=lambda p:p['ancre'][1]):
    old=by[p['id']];assert (p['nom'],p['sprite'],p['type'])==(old['nom'],old['sprite'],old['type'])
    assert p['apparition'] in range(8)
    uv=p['carte'];x,y,ww,hh=uv;u,v,e,f=p['rect'];assert 0<=u<e<w and 0<=v<f<h and (e-u,f-v)==(ww,hh) and ww<=36
    patch=art.crop((x,y,x+ww,y+hh));assert patch.getbbox();pixels=patch.getchannel('A').getextrema();assert pixels[1]>0
    assert not occ[v:f,u:e].any();occ[v:f,u:e]=True
    u0,v0,u1,v1=[i//3 for i in (u,v,e,f)];m=np.mean(np.all(disp[:,v0-1:v1+1,u0-1:u1+1]==disp[7,v0-1:v1+1,u0-1:u1+1],axis=3),axis=(1,2));assert min(m[p['apparition']:])>=.89
    if p.get('premiere_zone'):
        assert p['apparition']==0 and np.hypot(p['ancre'][0]-j['depart']['centre'][0],p['ancre'][1]-j['depart']['centre'][1])<150
    if 'animation' in p:
        i=p['animation'];nnm.add(i);n=j['grille_atlas'];c=[ani.crop((k*n+1,i*n+1,k*n+1+ww,i*n+1+hh))for k in range(8)]
        assert len({z.tobytes()for z in c})>1 and c[0].tobytes()==patch.tobytes()
    final.alpha_composite(patch,(u,v))
assert sorted(nnm)==list(range(j['animations'])) and ani.size==(8*j['grille_atlas'],j['animations']*j['grille_atlas'])
assert final.convert('RGB').tobytes()==monde.tobytes()
land=np.asarray(base);complete=np.asarray(monde);assert np.array_equal(land[~occ],complete[~occ]);modified=int(np.any(land!=complete,axis=2).sum())
file=R/'Monde-Destiny-EoS-6048x4032.png';big=Image.open(file).convert('RGB');assert big.size==(nw*12,nh*12) and big.tobytes()==monde.resize(big.size,nn).tobytes()
paths=Image.open(A/'Chemins.png');assert paths.size==(w,h) and paths.mode=='RGBA' and len(j['depart']['chemins'])==4
assert [p['id']for p in rows if p.get('premiere_zone')]==['reverie','fosse','passage','bois','guilde']
res={'etat':'PASS','feuillets_EoS_exacts':nt,'fond_reference_identique':True,'taille_native':[nw,nh],'carte_px':[w,h],'grand_png_px':list(big.size),'lieux':j['nb'],'miniatures_index_identiques':150,'surfaces_de_vignettes_sans_chevauchement':True,'part_du_fond_restante_visible_pct':100-round(100*modified/(w*h),2),'lieux_dans_la_premiere_zone':5,'animations':j['animations'],'apparentes_par_feuillet':dict(sorted(Counter(p['apparition']for p in rows).items())),'par_region':j['par_region'],'fichiers_sha256':{str(p.relative_to(R)):sf(p)for p in [fn,file,*sorted(A.iterdir())]}}
(R/'Verification-carte.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in res.items()if k!='fichiers_sha256'})
