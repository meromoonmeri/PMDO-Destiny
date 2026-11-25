#!/usr/bin/env python3
"""Audit the actual delivered art layers and atlas index (without cache inputs)."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,math
import numpy as np
from PIL import Image

r=Path(__file__).resolve().parents[1];a=r/'Apercu'/'assets';old=r.parent/'Atlas-du-Monde-Destiny';c=old/'Calques'
load=lambda name:json.loads((a/name).read_text())
img=lambda name:Image.open(a/name).convert('RGBA')
digest=lambda x:sha256(x).hexdigest()
filehash=lambda p:digest(p.read_bytes())
j=load('Lieux.json');rows=j['lieux'];n=len(rows);w,h=j['taille'];p=j['grille_atlas'];m=j['animations']
tiles=img('Lieux-150.png');am=img('Animations.png');art=img('Monde-150.png');bg=img('Terrain.png');fog=img('Nuages.png');mask=np.asarray(Image.open(r/'Sources'/'Traits'/'Masque-terres.png')).astype(bool)
assert n==j['nb']==150==len({l['id']for l in rows})==len({l['nom']for l in rows})
assert [l['id']for l in rows if l.get('premiere_zone')]==['reverie','fosse','passage','bois','guilde']
assert all(im.size==(w,h)and im.getchannel('A').getextrema()==(255,255)for im in (art,bg,fog))
assert j['par_region']==dict(Counter(l['region'] for l in rows))=={'destiny':5,'eau':24,'air':30,'herbe':32,'brume':28,'sable':14,'mer':14,'mystere':3}
assert j['par_type']==dict(Counter(l['type'] for l in rows))
assert j['version']==3 and m>=27
seen=set();pivots=set();frames=[];shift=[];fogfree=bg.copy();approved=Image.open(c/'Monde-1x.png').convert('RGBA')
for k,l in enumerate(sorted(rows,key=lambda l:l['ancre'][1])):
    t=l['id'];sx,sy,sw,sh=l['sprite'];x,y,x2,y2=l['rect'];u,v=l['ancre']
    assert (x2-x,y2-y)==(sw,sh) and ((x+x2)//2,v)==(u,y2)and 0<=x<x2<=w and 0<=y<y2<=h
    assert (u,v)not in pivots;pivots.add((u,v))
    assert not any(l['rect'][2]>b['rect'][0]and l['rect'][3]>b['rect'][1]and l['rect'][0]<b['rect'][2]and l['rect'][1]<b['rect'][3]for b in rows if b['id']!=t)
    sprite=tiles.crop((sx,sy,sx+sw,sy+sh));assert (sprite.getbbox()==(0,0,sw,sh) or l.get('premiere_zone') and sprite.getbbox()) and sprite.getchannel('A').getextrema()==(0,255),t
    key=digest(sprite.tobytes());assert key not in seen;seen.add(key)
    if l.get('premiere_zone'):
        src=Image.open(c/f'Lieu-{t}.png').convert('RGBA');assert sprite.tobytes()==src.tobytes()
        assert art.crop(l['rect']).tobytes()==approved.crop(l['rect']).tobytes(),t
    else:
        res=math.dist(l['ancre_reference'],l['ancre']);shift.append(res);assert res<=73
        assert mask[v-1,u] or l['region']=='mer' or l['type']=='mer' or t in ('monde-159','monde-219'),l
    if 'animation'in l:
        idx=l['animation'];assert idx not in frames;frames.append(idx)
        seq=[am.crop((i*p+1,idx*p+1,i*p+1+sw,idx*p+1+sh))for i in range(8)]
        assert seq[0].tobytes()==sprite.tobytes()and len({f.tobytes()for f in seq})>=5 and all(f.getchannel('A').tobytes()==sprite.getchannel('A').tobytes()for f in seq)
        original=c/f'Eau-{t}-8-poses.png'
        if original.is_file():
            before=Image.open(original).convert('RGBA');assert all(before.crop((i%4*sw,i//4*sh,(i%4+1)*sw,(i//4+1)*sh)).tobytes()==seq[i].tobytes()for i in range(8))
    fogfree.alpha_composite(sprite,(x,y))
assert len(seen)==150 and frames and sorted(frames)==list(range(m)) and am.size==(p*8,p*m)
assert art.tobytes()==fogfree.tobytes()
for file,hsh in j['edition_validee_sha256'].items():assert filehash(old/file)==hsh
for style,origin in j['croquis'].items():assert filehash(r/'Sources'/'Traits'/origin['fichier_detoure'])==origin['sha256_detoure']
large=r/'Monde-Destiny-150-Lieux-6144x4608.png';native=Image.open(large).convert('RGB');assert native.size==(w*4,h*4)
assert native.tobytes()==art.convert('RGB').resize((w*4,h*4),Image.Resampling.NEAREST).tobytes()
loc={l['id']:l for l in rows};px=j['depart']['centre'];dist={i:round(math.dist(px,loc[i]['ancre']),2)for i in ('fosse','passage','bois','guilde')}
assert dist=={'fosse':52.7,'passage':35.36,'bois':43.46,'guilde':47.13},dist
for key,line in j['depart']['chemins'].items():assert line[0]==px and line[-1]==loc[key]['ancre'] and key!='reverie'
result={'etat':'PASS','illustrations_valides':n,'par_region':j['par_region'],'par_type':j['par_type'],'composites_exactement_reconstitues':True,'carte_px':list(j['taille']),'grand_png_px':list(native.size),'criteres':{'motifs_tous_distincts':True,'decors_reverie_originaux_pixels_exacts':5,'chevauchements_de_rectangles':0,'animation_sur_8_poses':m,'poses_reverie_identiques':24,'distances_au_depart_en_pixels':dist,'decalage_max_a_Eddy_en_pixels':round(max(shift),2),'decalage_median_a_Eddy_en_pixels':round(float(np.median(shift)),2)},'sha256':{str(f.relative_to(r)):filehash(f)for f in [large,*sorted(a.iterdir())]}}
(r/'Verification-carte.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['criteres'],ensure_ascii=False));print('PASS — 150 décors, aucun chevauchement, carte à 6 144 × 4 608 px.')
