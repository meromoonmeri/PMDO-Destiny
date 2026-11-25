#!/usr/bin/env python3
"""Prepare a texture-free geography stencil and EoS style-only crops for image-guided art."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

D=Path(__file__).resolve().parents[1]; S=D/'Sources'; U=D.parent
M=U/'Terres-EoS-Magenta'/'Sources'
index=np.asarray(Image.open(M/'Index-terres-validees.png')); ground=index>0
water=np.asarray(Image.open(M/'Eaux-validees.png'))>0
H,W=index.shape; Y,X=np.mgrid[:H,:W]
key=[255,0,255]; n=Image.Resampling.NEAREST
meta=json.loads((U/'Sources'/'Geographie.json').read_text());choice=json.loads((M/'Placement-valide.json').read_text())
base=[(206,174,94),(199,173,104),(209,183,106),(203,150,77),(207,175,96),(208,174,96)]
biomes={'rock':(183,150,80),'forest':(157,154,77),'pine':(157,153,88),'snow':(210,217,213),'ice':(179,193,194),
        'meadow':(212,184,96),'petal':(185,136,75),'clay':(173,110,66),'salt':(228,210,149),
        'sand':(221,185,107),'marsh':(154,146,91),'ember':(172,121,75),'tropic':(164,149,88)}
geo=np.zeros((H,W,3),np.uint8)+np.asarray(key,np.uint8)
for r,b in zip(meta['regions'],base):
 mask=index==r['num']; a=np.zeros((H,W,3),np.float32)+b
 for x,y,rx,ry,k in r['fields']:
  f=np.clip(1.19-((X-x)/rx)**2-((Y-y)/ry)**2,0,.85)[...,None]; a=a*(1-f)+f*np.array(biomes[k])
 if r['id']=='reve':
  # Small guide for the known tree footprint, not final art. Only interior colors change.
  f=np.clip(1.16-((X-150)/11)**2-((Y-540)/12)**2,0,1)[...,None];a=a*(1-f*.59)+f*.59*np.array([165,144,69])
 geo[mask]=a[mask].astype('uint8')
for i,p in enumerate(meta['ilots'],101):geo[index==i]=biomes[p[4]]
dist=nd.distance_transform_edt(ground);geo[(dist<=1)&ground]=[139,92,49]
wcol=np.asarray(Image.open(M/'Eaux-de-reference.png').convert('RGBA'))
# With the coastline locked, draw the exact preexisting water areas as the only liquid-blue in the guide.
geo[water]=wcol[water,:3]
# One uniform artboard with margin; no symbols, imported shores, labels or background.
canvas=Image.new('RGB',(1152,768),tuple(key));canvas.paste(Image.fromarray(geo),(20,18));canvas.save(S/'Layout-NT-verrouille.png',optimize=True)
# A separate starting-isle stencil preserves precise anchors; artwork size is judged against an 88px island at native scale.
rev=Image.new('RGB',(224,224),tuple(key));part=Image.fromarray(geo[451:627,70:246]);rev.paste(part,(24,24));rev.resize((896,896),n).save(S/'Reverie-gabarit.png',optimize=True)
# True S01P01A map terrain, as documented in Carte-Miracle-EoS. No old contour may be used.
ref=Image.open(U.parent/'Carte-Miracle-EoS'/'Calques'/'Carte-DS-S01P01A.png').convert('RGB')
ref.crop((198,73,386,227)).resize((752,616),n).save(S/'EoS-Matiere-et-echelle.png',optimize=True)
ref.crop((247,104,364,187)).resize((585,415),n).save(S/'EoS-Lozanges-et-bosquets.png',optimize=True)
# This cold sample contains only a few chiseled icy ridges, not the full old island.
ref.crop((67,275,133,299)).resize((396,144),n).save(S/'EoS-Cretes-froides.png',optimize=True)
user=Image.open(Path.home()/'uploads'/'image-11.png').convert('RGB')
user.crop((308,114,545,308)).resize((474,388),n).save(S/'EoS-Detail-fourni.png',optimize=True)
print('Generated exact-geometry guide',canvas.size,'and pure art references.')
