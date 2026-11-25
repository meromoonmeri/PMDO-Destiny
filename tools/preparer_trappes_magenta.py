#!/usr/bin/env python3
"""Sources générées sur magenta → plaques 96×80 sur une seule grille native.

Réduction uniforme par vote de matière (extérieur / lèvre / cavité), couleur
calculée *uniquement* sur la lèvre. Pas de filtre entre deux matières. Puis
palette du biome, alpha binaire et nettoyage des îlots/pixels orphelins.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as nd
from dojo_dtef import Dtef
from dojo_reverie_types import TYPES

SOURCES = dict(normal='prairie',fire='forge',water='maree',grass='foret',electric='forge',ice='maree',
               fighting='sables',poison='foret',ground='sables',flying='sables',psychic='cristal',
               bug='foret',rock='sables',ghost='cristal',dragon='cristal',dark='foret',steel='acier',fairy='lucioles')
W,H,CX,CY = 96,80,48,40
WEIGHTS=np.array([.27,.62,.11]); FOUR=nd.generate_binary_structure(2,1); EIGHT=np.ones((3,3),bool)


def biggest(a):
    ids,n=nd.label(a,structure=EIGHT)
    if not n: raise ValueError('Matière absente de la découpe')
    count=np.bincount(ids.ravel());count[0]=0
    return ids==count.argmax()


def classes_source(source):
    a=np.array(Image.open(source).convert('RGB'),dtype=np.int16)
    r,g,b=np.moveaxis(a,-1,0)
    mag=(r>138)&(b>138)&(r-g>74)&(b-g>74)
    liseret=nd.binary_dilation(mag,iterations=2)&(r>g*1.20)&(b>g*1.20)&(np.minimum(r,b)>90)
    lit=~(mag|liseret)
    rocher=biggest(lit)
    puits=biggest(nd.binary_fill_holes(rocher)&~lit)
    yy,xx=np.where(rocher); ph,pw=np.where(puits)
    assert len(pw)>400 and np.ptp(pw)>np.ptp(xx)*.22,source
    scale=max((np.ptp(xx)+1)/80,(np.ptp(yy)+1)/43)
    sy=np.round(ph.mean()+(np.arange(H+1)-CY-.5)*scale).astype(int).clip(0,a.shape[0])
    sx=np.round(pw.mean()+(np.arange(W+1)-CX-.5)*scale).astype(int).clip(0,a.shape[1])
    # Recherche sur la même grille pour chaque calque. Aucun rééchantillonnage
    # non uniforme même lorsque la source est presque carrée.
    aout=np.zeros((H,W,3),np.uint8); out=np.zeros((H,W),np.uint8)
    for y in range(H):
        for x in range(W):
            box=np.s_[sy[y]:sy[y+1],sx[x]:sx[x+1]]; nr=rocher[box]; npuit=puits[box]
            counts=(nr.size-int(nr.sum()+npuit.sum()),int(nr.sum()),int(npuit.sum()))
            k=int(np.argmax(counts))
            if not counts[k]: continue
            out[y,x]=k
            if k==1: aout[y,x]=np.rint(a[box][nr].mean(axis=0)).astype(np.uint8)
    out[(out==1)&~biggest(out==1)]=0
    out[(out==2)&~biggest(out==2)]=0
    solid=biggest(out!=0)
    out[~solid]=0
    assert out[CY,CX]==2 and np.all(out[[0,-1]]==0) and np.all(out[:,[0,-1]]==0)
    return aout,out


def ramp(dtef,biome,kind):
    c=[]
    for layers in dtef.variants(biome,kind,255):
        for lay in layers:
            f=lay['Frames'][0]
            if f['Sheet']:
                a=np.asarray(dtef.image(f));c.append(a[a[:,:,3]==255,:3])
    a=np.concatenate(c)
    keep=np.ones(len(a),bool)
    r,g,b=a.T.astype(np.int16)
    keep &= ~((r>130)&(b>130)&(r-g>60)&(b-g>60))
    assert keep.any(),biome
    return a[keep]


def couleurs(a,mat,dtef,biome,source):
    sol=ramp(dtef,biome,'floor'); paroi=ramp(dtef,biome,'wall')
    pal=np.unique(np.concatenate((sol,paroi)),axis=0).astype(float)
    # Le massif reste pierre / plante / métal, mais ses rampes de lumière
    # viennent du sol et de la paroi de CE biome, pas du dojo qui l'héberge.
    pixels=a[mat==1]; srgb=np.array(Image.fromarray(pixels.reshape(1,-1,3)).quantize(
        colors=22,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB'))[0].astype(float)
    lc=srgb@WEIGHTS; low,high=np.quantile(lc,[.015,.98]); z=np.clip((lc-low)/max(1,high-low),0,1)
    lc_native=pal@WEIGHTS; low_n,high_n=np.quantile(np.concatenate((sol,paroi))@WEIGHTS,[.06,.94]);
    low_n=max(25,low_n*.78); high_n=max(low_n+62,high_n)
    anchor=np.median(paroi,axis=0)*.72+np.median(sol,axis=0)*.28
    lum=low_n+z*(high_n-low_n);w=0.52 if source in ('prairie','foret','lucioles') else .30
    orig=srgb-lc[:,None]; base=anchor-anchor@WEIGHTS
    candidates=(lum[:,None]+base*(1-w)+orig*w).clip(0,255)
    dist=((candidates[:,None,:]-pal[None,:,:])**2)@WEIGHTS
    dist+=.38*(lum[:,None]-lc_native[None,:])**2
    shades=pal[dist.argmin(axis=1)].astype(np.uint8)
    a[mat==1]=shades
    return anchor.astype(int)


def nettoyer_pixels(a,mat):
    """Efface les points déconnectés et la poussière d'un pixel entre clusters."""
    old=a.copy(); lone=0
    for y,x in zip(*np.where(mat==1)):
        p=old[y,x]; around=[old[y+dy,x+dx] for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)) if mat[y+dy,x+dx]==1]
        if len(around)<3 or any(np.array_equal(s,p) for s in around): continue
        colors,cnts=np.unique(around,axis=0,return_counts=True)
        if cnts.max()>=3:
            a[y,x]=colors[cnts.argmax()];lone+=1
    return lone


def detourer(path,dtef,biome,source):
    a,mat=classes_source(path); anchor=couleurs(a,mat,dtef,biome,source); fixes=nettoyer_pixels(a,mat)
    color=(anchor*.14+np.array([8,6,14])*.86).astype(np.uint8)
    for y,x in zip(*np.where(mat==2)):
        # Deux marches d'obscurité en aplats, aucun alpha ni dégradé au bord.
        a[y,x]=np.minimum(color+(4 if y<CY-2 else (1 if y<CY+3 else 0)),255)
    base=np.zeros((H,W,4),np.uint8);base[mat!=0,:3]=a[mat!=0];base[mat!=0,3]=255
    near=np.zeros_like(base)
    for x in range(W):
        yy=np.flatnonzero(mat[:,x]==2)
        if len(yy):
            ind=np.flatnonzero(mat[yy[-1]+1:,x]==1)+yy[-1]+1
        elif CX-40<=x<=CX+40:
            ind=np.flatnonzero(mat[CY+4:,x]==1)+CY+4
        else:
            continue
        near[ind,x,:]=base[ind,x,:]
    assert 0<np.count_nonzero(near[:,:,3])<np.count_nonzero(base[:,:,3])
    stats={'source':path.name,'sha256_brut':hashlib.sha256(path.read_bytes()).hexdigest(),
           'pixels_isoles_corriges':fixes,'pixels_levre':int((mat==1).sum()),'pixels_puits':int((mat==2).sum()),
           'tons':len(np.unique(base[base[:,:,3]>0,:3],axis=0))}
    return Image.fromarray(base),Image.fromarray(near),stats


def generer(bruts,data,out):
    out.mkdir(parents=True,exist_ok=True)
    d=Dtef(data); report={}
    for typ,_,_,biome,*_ in TYPES:
        f=SOURCES[typ]; base,rebord,stats=detourer(bruts/f'{f}-trou.png',d,biome,f)
        base.save(out/f'{typ}_sol.png',optimize=True);rebord.save(out/f'{typ}_rebord.png',optimize=True)
        report[typ]={'biome':biome,**stats}
    (out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('18 ouvertures, 8 sources générées, 2 plans séparés par ouverture ;',
          sum(v['pixels_isoles_corriges'] for v in report.values()),'pixels isolés corrigés après réduction.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bruts',type=Path,required=True)
    p.add_argument('--donnees',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();generer(a.bruts,a.donnees,a.out)
