#!/usr/bin/env python3
"""Register the four generated extensions on the unmodified DS chart at native scale."""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from ToileEoS import fond, DS, PANELS, EO, W, H, N

D=Path(__file__).resolve().parents[1]; S=Path(__file__).resolve().parent
C=D/'Calques'/'Extension-EoS'; G=D/'Generations'/'Extension-EoS'/'Denses'
S8=np.ones((3,3),bool)

def raster(rgba,mask):
 ans=np.zeros((*mask.shape,4),np.uint8);ans[mask,:3]=rgba[mask];ans[mask,3]=255;return ans

def palette_pos(rgb):
 # Opponent space: put more weight on luminance and green than raw RGB distance.
 r,g,b=np.moveaxis(rgb.astype('float32'),-1,0)
 return np.stack((.34*r+.65*g+.19*b,.52*(r-g),.43*(b-(r+g)/2)),-1)

def run():
 C.mkdir(exist_ok=True,parents=True); ds=Image.open(DS).convert('RGB')
 palette=json.loads((S/'Extension-EoS/Palette-terres-EoS.json').read_text());colors=np.array(palette,dtype='uint8'); lookup=cKDTree(palette_pos(colors))
 sprites=np.asarray(Image.open(S/'Extension-EoS/Motifs-DS-natifs.png').convert('RGBA')).astype('float32')
 def tile(x,y,shape,ox,oy):
  block=sprites[y:y+16,x:x+16,:3]; assert (sprites[y:y+16,x:x+16,3]==255).all()
  h,w=shape;return (block-block.mean((0,1)))[np.ix_((np.arange(h)+oy)%16,(np.arange(w)+ox)%16)]
 def detail(art,m,k0,pos):
  im=art.astype('float32');R,G,B=np.moveaxis(im,-1,0);dist=ndi.distance_transform_edt(m)
  lum=.29*R+.60*G+.11*B;diff=ndi.maximum_filter(lum,3)-ndi.minimum_filter(lum,3)
  flat=np.clip((27-diff)/21.,0.,1.)
  warm=(R>G+8)&(G>B+11)&m&(lum>105);cold=m&~warm
  # Underlay of the actual DS hatching from the user's sheet, sampled only in
  # quiet ground of the generated terrain. Painted landmarks remain intact.
  shade=tile(208 if k0 not in ('jade','sylverive') else 224,112,m.shape,*pos)
  ground=np.maximum(0.,np.minimum(1.,(lum-132)/26.))*warm
  im+=shade*(ground*flat*.96)[...,None]
  rim=m&(dist<=1.42)
  wash=np.maximum(0.,np.minimum(1.,(lum-145)/50.))*warm
  im+=np.dstack((-10*wash,-1*wash,-15*wash))
  # Avoid pink seams from the raw chroma. Set a single ochre ink edge instead
  # of an isometric bevel or a bright beach rim.
  ink=np.array([167,111,47],dtype='float32');alpha=(.46*rim*warm)[...,None]
  im=im*(1-alpha)+ink*alpha
  if k0=='grand-frimas':
   ice=tile(240,112,m.shape,*pos)
   snow=cold&(lum>=196)&(diff<25)&(B-R<29)
   # Restore the actual grey snow ramp, not an even cream or icy white field.
   im[snow]=np.array([199,199,199],dtype='float32')+ice[snow]
   lake=cold&(lum<196)&(lum>128)&(dist>3)&(flat>.40)&(B-R>7)
   # A second genuine DS tile supplies the short staggered glints on the frozen tarn.
   diag=tile(208,112,m.shape,pos[0]+11,pos[1])[...,1]
   im[lake]=[167,191,199]
   im[lake&(diag<-8)]=[143,167,167]
   im[lake&(diag>18)]=[207,207,207]
  return np.clip(im,0,255)
 # Place small decorative motifs directly from the supplied indexed sheet. These
 # do not replace the generated landmarks and have no extra pin attached to them.
 accents={
  'nacrebrune':['arbre','cailloux','eclat'],'sillons':['cailloux','cairn','herbe'],
  'aube':['arbre','herbe','graines'],'grand-frimas':['galets','galets','galets','gel'],
  'cendres':['tison','cailloux','cairn'],'cuivre':['cailloux','cairn','eclat'],
  'sylverive':['arbre','herbe','graines'],'jade':['arbre','graines','eclat']}
 cuts={'arbre':(17,97,24,110),'cailloux':(164,86,187,96),'eclat':(224,80,235,88),
       'cairn':(228,89,239,96),'herbe':(128,84,144,95),'graines':(82,116,86,121),
       'galets':(176,41,191,47),'gel':(55,42,62,47),'tison':(92,128,102,137)}
 lieux=json.loads((S/'Extension-EoS/Lieux.json').read_text())
 def decor(rgba,k):
  a=np.array(rgba);mask=a[...,3]>0; rgb=a[...,:3].astype('float32');h,w=mask.shape
  yy,xx=np.mgrid[:h,:w];seen=np.zeros((h,w),bool); d0=ndi.distance_transform_edt(mask);anchors=[r[3] for r in lieux[k]]
  # Prefer calm ground well outside the generated features in the user's list.
  gap=np.minimum.reduce([(xx-x)**2+(yy-y)**2 for x,y in anchors]);ld=rgb.mean(2);local=ndi.maximum_filter(ld,5)-ndi.minimum_filter(ld,5)
  output=rgba.copy(); desc=[]
  for j,name in enumerate(accents[k]):
   l,t,r,b=cuts[name]; im=Image.fromarray(sprites[t:b,l:r].astype('uint8'));bb=im.getbbox()
   if not bb:continue
   im=im.crop(bb);m=np.asarray(im)[...,3]>0
   well=gap>=9**2;limit=(min(j,2)*18+8);score=local*1.2+.016*((xx-(43*j+23)%w)**2+(yy-(29*j+25)%h)**2)-1.2*np.minimum(d0,11)
   score[~mask|seen|~well| (local>limit+18)]=np.inf
   for index in np.argsort(score.ravel())[:260]:
    cy,cx=np.unravel_index(index,mask.shape)
    if not np.isfinite(score[cy,cx]):break
    x,y=cx-im.width//2,cy-im.height//2
    if x<0 or y<0 or x+im.width>w or y+im.height>h:continue
    sl=np.s_[y:y+im.height,x:x+im.width]
    if not ((d0[sl][m]>1).all() and (gap[sl][m]>=8**2).all() and not seen[sl][m].any()):continue
    output.alpha_composite(im,(int(x),int(y)));seen|=(xx-cx)**2+(yy-cy)**2<13**2;desc.append({'motif':name,'position':[int(x),int(y)]});break
  assert np.array_equal(np.asarray(output)[...,3]>0,mask)
  return output,desc
 def quiet_area(x,m):
  rgb=x.astype('int16');l=rgb[...,0]+2*rgb[...,1]+rgb[...,2]
  same=ndi.maximum_filter(l,7)==ndi.minimum_filter(l,7)
  return int((same&ndi.binary_erosion(m, structure=np.ones((7,7),bool))).sum())
 stack=Image.new('RGBA',(W,H)); manifest={}
 for name,conf in PANELS.items():
  src=G/f'{name}.png'; im=Image.open(src).convert('RGB');x,y,X,Y=conf['cadre'];a=np.array(im.resize((X-x,Y-y),N));r,g,b=np.moveaxis(a.astype('int16'),-1,0)
  key=((r>115)&(b>108)&(r-g>45)&(b-g>38)&(g<.7*np.minimum(r,b)))|((r>72)&(b>82)&(b-g>40)&(r-g>32)&(g<.55*np.minimum(r,b)))
  labels,k=ndi.label(~key,S8); freq=np.bincount(labels.ravel()); objs=ndi.find_objects(labels)
  sides=(set(labels[0])|set(labels[-1])|set(labels[:,0])|set(labels[:,-1]))-{0};parts={k0:[] for k0,_,_ in conf['terres']}
  for j,o in enumerate(objs,1):
   if j in sides or freq[j]<12:continue
   yy,xx=o;cx=x+(xx.start+xx.stop)/2;cy=y+(yy.start+yy.stop)/2
   if ((x==0 and cx>=EO-4) or (x>0 and cx<EO+504+4)) or not 25<=cy<=308:continue
   def dist(spec):
    lx,ty,ww,hh=spec[2];return (max(lx-cx,0,cx-lx-ww)**2+max(ty-cy,0,cy-ty-hh)**2,.08*(lx+ww/2-cx)**2+.08*(ty+hh/2-cy)**2)
   parts[min(conf['terres'],key=dist)[0]].append(j)
  print(name,im.size,[(q,[(i,int(freq[i])) for i in sorted(parts[q],key=lambda j:-freq[j])]) for q in parts]);
  for k0,title,_ in conf['terres']:
   m=np.isin(labels,parts[k0]); assert m.sum()>1400,(name,k0,m.sum()); gy,gx=np.where(m);l,t,u,v=int(gx.min()),int(gy.min()),int(gx.max()+1),int(gy.max()+1)
   m=m[t:v,l:u]; art=a[t:v,l:u].copy();R,G0,B=np.moveaxis(art.astype('float32'),-1,0)
   # Remove the magenta fringe, not the crimson volcanic pigment. A 1-pixel
   # border can also contain compressed mixes with the matte on a generated image.
   dist=ndi.distance_transform_edt(m)
   corrupt=m&(((R-G0>51)&(B-G0>27)&(B>R*.70))|((dist<=1.42)&(R>G0*1.23)&(B>G0*.80)))
   if corrupt.any():
    tmp=ndi.distance_transform_edt(~(m&~corrupt),return_distances=False,return_indices=True);art[corrupt]=art[tmp[0][corrupt],tmp[1][corrupt]]
   pos=[x+l,y+t]; base=np.zeros_like(art);base[m]=colors[lookup.query(palette_pos(art[m]))[1]]
   edited=detail(art,m,k0,pos); colors_out=colors[lookup.query(palette_pos(edited[m]))[1]]
   out=np.zeros((*m.shape,4),np.uint8);out[m,:3]=colors_out;out[m,3]=255
   rgba,dec=decor(Image.fromarray(out),k0);rgba.save(C/(k0+'.png'),optimize=True);stack.alpha_composite(rgba,tuple(pos))
   manifest[k0]={'nom':title,'position':pos,'dimensions':list(rgba.size),'brut':src.relative_to(D).as_posix(),'sha256':sha256(src.read_bytes()).hexdigest(),'silhouettes':len(parts[k0]),'pixels':int(m.sum()),'motifs_reference':dec,'surface_uniforme_7px_avant':quiet_area(base,m),'surface_uniforme_7px_apres':quiet_area(out[...,:3],m)}
 native=fond().convert('RGBA');native.alpha_composite(stack);native=native.convert('RGB')
 assert native.crop((EO,0,EO+504,336)).tobytes()==ds.tobytes()
 native.save(D/'Extension-EoS-Grand-Large.png',optimize=True);stack.save(C/'Terrains.png',optimize=True)
 (C/'Placements.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':run()
