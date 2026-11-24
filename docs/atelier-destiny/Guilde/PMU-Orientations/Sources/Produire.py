#!/usr/bin/env python3
"""Make the 8-direction PNGs from the audited .dir bank and the four new keyed studies."""
import argparse
from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import struct
from time import monotonic

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from Reconstituer import build, caption, pieces, CATEGORY, WALL, NEW
from Volumes import DIRS, TRIG, K, flat, view, composite

ROOT=Path(__file__).resolve().parents[1]
W=Path(os.environ.get('PMU_TRAVAIL',Path.home()/'.cache/pmu-orientations'));W.mkdir(parents=True,exist_ok=True)
R=Path(os.environ.get('PMU_077_OBJETS',Path.home()/'.cache/fenetres-jeu-destiny/runtime-077/Content/Object'))
CHOIX={'Pupitre-aux-cartes':(35,26),'Chariot-a-the':(41,None),'Grainotheque':(25,None),'Horloge-lunaire':(15,None)}
FAMILIES=['Mob','Cpt','DecA','DecB','Guilde','Accessoires isolés','IA','Créations inédites']
FR=['Face','Avant droit','Profil droit','Arrière droit','Dos','Arrière gauche','Profil gauche','Avant gauche']
NAV=['↓','↘','→','↗','↑','↖','←','↙']

def digest(b):return sha256(b).hexdigest()
def js(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def png(a):
    f=BytesIO();Image.fromarray(a).save(f,format='PNG',compress_level=7);return f.getvalue()

def decode(rr):
    name=rr['id'];p=R/(name+'.dir');b=p.read_bytes();assert digest(b)==rr['sha256_dir'],name
    n,=struct.unpack_from('<q',b);sw,sh,d,f=struct.unpack_from('<4i',b,n+8);assert d==0 and f==1
    a=np.asarray(Image.open(BytesIO(b[8:n+8])).convert('RGBA')).copy();assert a.shape==(sh,sw,4)
    al=a[:,:,3].astype(float);keep=al>0;a[~keep]=0
    if np.all(a[keep,:3]<=al[keep,None]):a[keep,:3]=np.clip(np.rint(a[keep,:3].astype(float)*255/al[keep,None]),0,255).astype(np.uint8)
    return a

def trim(a,thr):
    y,x=np.where(a[:,:,3]>thr);assert x.size>0;a0,b0,a1,b1=map(int,(x.min(),y.min(),x.max()+1,y.max()+1));return a[b0:b1,a0:a1].copy(),a0,b0

def keyed(stem,size):
    p=ROOT/'Etudes'/(stem+'.png');raw=p.read_bytes();im=Image.open(BytesIO(raw)).convert('RGB');q=np.asarray(im);r,g,b=q.astype(np.int16).transpose(2,0,1)
    m=(r>95)&(b>99)&(r>1.35*g+24)&(b>1.30*g+19)
    L,n=ndi.label(~m,np.ones((3,3)));n=np.bincount(L.ravel());n[0]=0;body=L==n.argmax()
    assert n.max()>3000 and np.mean(body)<.75,(stem,n.max(),body.mean())
    a=np.zeros((*q.shape[:2],4),np.uint8);a[body,:3]=q[body];a[body,3]=255
    a,x,y=trim(a,127);pic=Image.fromarray(a);pic.thumbnail(size,Image.Resampling.BOX)
    a=np.asarray(pic).copy();bad=a[:,:,3]<135;a[bad]=0;a[~bad,3]=255
    # Preserve clusters; remove half-transparent key fringe before palette reduction.
    a,_,_=trim(a,127);m=a[:,:,3]>127;a=Image.fromarray(a).quantize(116,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).convert('RGBA');a=np.asarray(a).copy();a[~m]=0;a[m,3]=255
    return a,{'etude':p.name,'sha256_etude':digest(raw),'dimensions_etude':list(im.size),'coupe_etude':[x,y],'taille_retenue':[a.shape[1],a.shape[0]]}


def fit_down(m):
    orig=m.ref[:,:,3]>127;recon=m.down[:,:,4]>0
    return round(float(np.count_nonzero(orig&recon)/max(1,np.count_nonzero(orig|recon))),4)

def prepare(row):
    name=row['id'];new=row['famille']=='Créations inédites'
    if new:
        stem=row['etude'];title,mode,size=NEW[stem];depth,top=CHOIX[stem];source,orig=keyed(stem,size)
    else:
        title,mode,depth,top=caption(row);source=decode(row);orig={'fichier':name+'.dir','source_version':'Destiny 0.7.7','sha256_dir':row['sha256_dir'],'dimensions_dir':[source.shape[1],source.shape[0]]}
    raw,rx,ry=trim(source,0);core,cx,cy=trim(source,127);orig['coupe_down']=[rx,ry,raw.shape[1],raw.shape[0]];orig['coupe_opaque']=[cx,cy,core.shape[1],core.shape[0]]
    core[core[:,:,3]<128]=0
    if mode=='sol':
        # The source's drop shadow remains in Down; rotate the clean mat on the XY map in other slots.
        anchor=[round(cx+core.shape[1]//2-rx),round(cy+core.shape[0]//2-ry)]
        sprites=[flat(core,i) for i in range(8)]
        fo=[[(0,0) for _ in range(1)] for i in range(8)]
        sh=np.argwhere(core[:,:,3]>127);sh=sh[::max(1,len(sh)//150)]
        for i,(c,s) in enumerate(TRIG):fo[i]=[[round((x-core.shape[1]/2)*c+(y-core.shape[0]/2)*s),round(-(x-core.shape[1]/2)*s+(y-core.shape[0]/2)*c)] for y,x in sh]
        diag={'methode':'plan_sol','matiere':'surface','score_couverture':1.,'iou_gabarit':1.,'elements':1}
    else:
        parts=pieces(core,name) if mode=='ensemble' else []
        if parts:
            locals=[];hat=[]
            for px,py,a,kind in parts:
                if kind=='sol':
                    xo=px+a.shape[1]//2;yo=py+a.shape[0]//2;model=None
                else:
                    model=build(a,kind);xo=px+model.pivot[0];yo=py+model.pivot[1]
                locals.append((xo,yo,a,model))
            xo=core.shape[1]/2;yo=float(np.median([p[1] for p in locals]))
            sprites=[];fo=[]
            for i,(cs,sn) in enumerate(TRIG):
                tuples=[];feet=[]
                for X,Y,a,model in locals:
                    x=X-xo;y=(Y-yo)/K
                    tu=view(model,i) if model else flat(a,i);tuples.append((tu,x,y))
                    feet.append([round(cs*x+sn*y),round(K*(-sn*x+cs*y))])
                sprites.append(composite(tuples,i));fo.append(feet)
            anchor=[round(cx+xo-rx),round(cy+yo-ry)]
            f=[p[-1].fit for p in locals if p[-1]];is0=[fit_down(p[-1]) for p in locals if p[-1]]
            diag={'methode':'ensemble_de_volumes','matiere':'mixte','score_couverture':round(float(np.mean(f)),4) if f else 1.,'iou_gabarit':round(float(np.mean(is0)),4) if is0 else 1.,'elements':len(locals)}
        else:
            shape=mode if mode!='ensemble' else 'bahut'
            model=build(core,shape,depth,top,strict=new)
            xo,yo=model.pivot;anchor=[round(cx+xo-rx),round(cy+yo-ry)]
            sprites=[view(model,i) for i in range(8)]
            fx,fy=model.foot
            sl=slice(None,None,max(1,len(fx)//120));fx,fy=fx[sl],fy[sl]
            fo=[]
            for c,s in TRIG:
                x=np.rint(fx*c+fy*s).astype(int);y=np.rint(K*(-fx*s+fy*c)).astype(int);fo.append([[a,b] for a,b in sorted(set(zip(x.tolist(),y.tolist())))])
            diag={'methode':'volume_et_textures','matiere':model.pigment,'score_couverture':model.fit,'iou_gabarit':fit_down(model),'elements':1,'modele_px':list(model.geom.shape[::-1])}
    sprites[0]=(raw,np.zeros(raw.shape[:2],np.float32),-anchor[0],-anchor[1]);diag['gabarit']=mode
    return title,mode,orig,diag,sprites,fo


def file_id(row):
    return row['id'].removeprefix('Guilde_PMU_').removeprefix('Guilde_Imm_pmu_').removeprefix('PMU_')

def run(out,fil=None,check=False):
    from itertools import product
    inv=json.loads((ROOT/'Inventaire-sources-PMU.json').read_text())
    rows=inv['objets']+[{'id':'Creation_'+n,'famille':'Créations inédites','etude':n} for n in NEW]
    assert len(rows)==360
    out.mkdir(parents=True,exist_ok=True);indices=[];begin=monotonic()
    for k,r in enumerate(sorted(rows,key=lambda r:(FAMILIES.index(r['famille']),r['id'])),1):
        if fil and file_id(r) not in fil and r['id'] not in fil:continue
        title,mode,orig,diag,sprites,fo=prepare(r);folder=f'PNG/{file_id(r)}';fd=out/folder;fd.mkdir(parents=True,exist_ok=True)
        frames=[];allFit=[]
        for i,(a,dd,x,y) in enumerate(sprites):
            direction=DIRS[i];p=fd/(direction+'.png');bb=png(a);p.write_bytes(bb);pv=[-x,-y];h,w=a.shape[:2]
            assert a[:,:,3].any() and list(a.shape[:2])==list(dd.shape),(r['id'],direction,a.shape,diag)
            assert -w<=pv[0]<=2*w and -h<=pv[1]<=2*h,(r['id'],direction,pv,w,h)
            # Footprint immediately relative to the pivot; can act as placement guide, not collisions.
            f=fo[i];xa=min(p[0] for p in f);xb=max(p[0] for p in f);ya=min(p[1] for p in f);yb=max(p[1] for p in f)
            frames.append({'direction':direction,'fichier':f'{folder}/{p.name}','taille':[w,h],'pivot':pv,'ligne_de_sol':[xa,ya,xb,yb],'sha256':digest(bb)})
        indices.append({'rang':k,'id':r['id'],'repere':file_id(r),'nom':title,'famille':r['famille'],'collection':CATEGORY[mode],'gabarit':mode,'fixation':'mur' if mode in WALL else 'sol','nouvelle_generation':r['famille']=='Créations inédites','ia_existante':r['famille']=='IA','source':orig,'reconstruction':diag,'vues':frames})
        if fil or k%20==0:print(f'{k:>3} · {file_id(r):<40} {mode:<16} {diag["score_couverture"]:.2f} / {diag["iou_gabarit"]:.2f} — {monotonic()-begin:.1f}s',flush=True)
    ct=Counter(r['famille'] for r in indices);rea=Counter(r['reconstruction']['methode'] for r in indices)
    data={'titre':'Destiny · Objets PMU dans les huit sens','portee':'Banque des sprites .dir PMU de Destiny Windows 0.7.7. Le client PMUniverse et ses autres tuiles ne sont pas inclus.','unite':'PNG 1× ; tuile de 8 px ; pivot [x,y] depuis le coin haut gauche (peut être hors image près du sol).','echelle':'Les objets sont conservés à la taille du sprite source ; les volumes sont interprétés.','projection':{'ordre':list(DIRS),'libelles':FR,'fleches':NAV,'coefficient_y':K,'down':'sprite source, transparence recadrée et RGB non prémultiplié','autres':'volumes reconstitués et vues orthographiques texturées; rotation strictement au sol pour les éléments plats'},'nombre':len(indices),'nombre_de_png':8*len(indices),'familles':dict(ct),'methodes':dict(rea),'objets':indices}
    js(out/'Index-PMU-8.json',data)
    print(f'{len(indices)} sources · {len(indices)*8} vues · {dict(rea)} — {monotonic()-begin:.1f}s',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sortie',type=Path,default=W/'Kit');p.add_argument('ids',nargs='*');a=p.parse_args();run(a.sortie,set(a.ids))
