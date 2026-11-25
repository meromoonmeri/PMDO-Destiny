#!/usr/bin/env python3
"""Détoure les trois originaux sur magenta sur une grille native, sans mixels."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd

MOTIFS = {
    'petale-cerisier': (12, 12, ('#8c3f62','#d96e91','#f7b5bf','#fff0dd')),
    'ombre': (19, 28, ('#14121f','#262035','#413555','#664c78')),
    'prisme': (12, 17, ('#432963','#815498','#c997dd','#ffe5fc')),
}


def palette(hexes):
    return [tuple(bytes.fromhex(c[1:])) for c in hexes]


def composante(a):
    labels,n=nd.label(a,structure=np.ones((3,3),bool))
    if not n: raise ValueError('masque vide')
    counts=np.bincount(labels.flat); counts[0]=0
    return labels==counts.argmax()


def preparer(path,w,h,couleurs):
    src=np.array(Image.open(path).convert('RGB'),dtype=np.int16)
    r,g,b=src.transpose(2,0,1)
    mag=(r>138)&(b>138)&(r-g>74)&(b-g>74)
    bord=nd.binary_dilation(mag,iterations=2)&(np.minimum(r,b)>90)&(r>g*1.24)&(b>g*1.24)
    mat=composante(~(mag|bord)); ys,xs=np.where(mat)
    # Un seul facteur pour les deux axes ; votes et moyennes sans alpha croisé.
    k=max((xs.max()-xs.min()+1)/w,(ys.max()-ys.min()+1)/h)
    sx=np.round((xs.min()+xs.max()+1)/2+(np.arange(w+1)-w/2)*k).astype(int)
    sy=np.round((ys.min()+ys.max()+1)/2+(np.arange(h+1)-h/2)*k).astype(int)
    out=np.zeros((h,w,4),np.uint8); valeurs=np.zeros((h,w)); luma=(.26,.62,.12)
    for y in range(h):
        for x in range(w):
            box=np.s_[sy[y]:sy[y+1],sx[x]:sx[x+1]]; m=mat[box]
            if m.sum()<=m.size*.50: continue
            out[y,x,3]=255; valeurs[y,x]=src[box][m].mean(axis=0)@luma
    avant=out[:,:,3]>0
    keep=composante(avant)
    # Rejeter les îlots et les mélanges optiques d'un pixel en dehors du motif.
    out[~keep]=0
    p=palette(couleurs); low,high=np.quantile(valeurs[keep],[.06,.94]); assert high>low
    ix=np.rint(np.clip((valeurs-low)/(high-low),0,1)*(len(p)-1)).astype(int)
    out[keep,:3]=np.array(p,np.uint8)[ix[keep]]
    return Image.fromarray(out), int(np.sum(avant&~keep))


def run(bruts,out):
    out.mkdir(exist_ok=True,parents=True)
    info={}
    for nom,(w,h,pal) in MOTIFS.items():
        p=bruts/f'{nom}.png'
        im,retire=preparer(p,w,h,pal)
        im.save(out/p.name,optimize=True)
        info[nom]=dict(source=p.name,sha256_brut=hashlib.sha256(p.read_bytes()).hexdigest(),grille=[w,h],
                       ilots_supprimes=retire,alpha='binaire',palette=pal)
    (out/'sources.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bruts',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();run(a.bruts,a.out)
