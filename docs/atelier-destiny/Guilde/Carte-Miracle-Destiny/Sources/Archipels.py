"""Place the four generated static island assets into clear water without moving existing lands."""
from hashlib import sha256
from PIL import Image
from scipy import ndimage as nd
import numpy as np

N=Image.Resampling.NEAREST
ST=np.ones((3,3),np.uint8)
CONFIG=[
 {'id':'volcans','name':'Archipel volcanique','file':'Volcan-et-Cratere.png','width':106,'near':(226,56),'port':(.56,.85),'nature':'EoS · adaptation','biome':'Basalte, cendres et lave'},
 {'id':'coraux','name':'Atoll des Coraux','file':'Atoll-des-Coraux.png','width':99,'near':(1004,665),'port':(.31,.86),'nature':'Création Destiny','biome':'Lagon et récif corallien'},
 {'id':'amethystes','name':'Île des Améthystes','file':'Ile-des-Amethystes.png','width':84,'near':(477,413),'port':(.18,.74),'nature':'Création Destiny','biome':'Contreforts et cristaux lilas'},
 {'id':'petales','name':'Bois des Pétales','file':'Bois-des-Petales.png','width':91,'near':(986,56),'port':(.45,.84),'nature':'Création Destiny','biome':'Bosquets de fleurs et terrasses ocre'},
]

def trim(path,width):
 raw=np.array(Image.open(path).convert('RGB'));r,g,b=np.moveaxis(raw.astype('int16'),-1,0)
 key=(r>163)&(b>151)&(g<.64*np.minimum(r,b))&(np.abs(r-b)<110)
 lab,num=nd.label(~key,structure=ST);s=np.bincount(lab.ravel());s[0]=0
 m=np.isin(lab,np.flatnonzero(s>=max(60,s.max()*.001)))
 # The matte is exterior. Recover enclosed purple crystal pigments: their bright red/blue
 # channels can resemble the key, but the original violet has green above the magenta matte.
 interior=nd.binary_fill_holes(m,structure=ST)&~m
 m|=interior&(g>=62)
 ii,jj=np.nonzero(m);x1,y1,x2,y2=int(jj.min()),int(ii.min()),int(jj.max()+1),int(ii.max()+1)
 rgb=raw[y1:y2,x1:x2].copy();m=m[y1:y2,x1:x2]
 # Key cleanup at the edge only. Interior lilac crystal pigments are not replaced.
 dist=nd.distance_transform_edt(m);R,G,B=np.moveaxis(rgb.astype('int16'),-1,0)
 spill=m&(dist<7)&(R-G>32)&(B-G>20)&(B>95)&(abs(R-B)<120)
 if spill.any():
  near=nd.distance_transform_edt(~(m&~spill),return_distances=False,return_indices=True)
  rgb[spill]=rgb[near[0][spill],near[1][spill]]
 cut=np.dstack((rgb,m.astype(np.uint8)*255));cut[~m]=0
 return Image.fromarray(cut).resize((width,round(width*cut.shape[0]/cut.shape[1])),N)

def place(labels,features,generations,calques):
 H,W=labels.shape;orig=labels.copy();out=labels.copy();occupied=out>0
 for q in features.values():
  occupied[q['y']:q['y']+q['h'],q['x']:q['x']+q['w']]=True
 grp=calques/'Archipels';grp.mkdir(exist_ok=True)
 combined=Image.new('RGBA',(W,H));blocked=np.zeros((H,W),dtype=bool);answers=[];label=101
 for spec in CONFIG:
  p=generations/'Archipels'/spec['file'];im=trim(p,spec['width']);w,h=im.size;m=np.asarray(im)[...,3]>0
  d=nd.distance_transform_edt(~occupied);ax,ay=spec['near'];x0,y0=ax-w//2,ay-h//2
  pairs=sorted((dx*dx+dy*dy,x0+dx,y0+dy) for dx in range(-82,83,2) for dy in range(-56,57,2))
  for _,x,y in pairs:
   if not(22<=x<=W-w-22 and 21<=y<=H-h-21):continue
   near=float(d[y:y+h,x:x+w][m].min())
   if near>=10:break
  else:raise AssertionError(f'Pas de placement marin libre pour {spec["id"]}')
  aux,_=nd.label(m,structure=ST);cnt=np.bincount(aux.ravel());cnt[0]=0
  order=np.argsort(cnt)[::-1];ids=[];new=out[y:y+h,x:x+w]
  for i in order:
   if not cnt[i]:continue
   new[aux==i]=label;ids.append(label);label+=1
  visible=np.array(im);r,g,b=np.moveaxis(visible[...,:3].astype('int16'),-1,0)
  if spec['id']=='coraux':
   # This lagoon is visible art but not traversable terrain. On-foot routes follow the sand.
   blue=(g-r>23)&(b-r>25)&(b>=g-14)
   blocked[y:y+h,x:x+w]|=m&blue
  if spec['id']=='petales':
   blocked[y:y+h,x:x+w]|=m&(g-r>25)&(b-r>25)&(b>=g-14)
  if spec['id']=='volcans':
   lava=(r>105)&(r-g>43)&(r-b>53)
   blocked[y:y+h,x:x+w]|=m&lava
  occupied[y:y+h,x:x+w]|=m
  combined.alpha_composite(im,(x,y));im.save(grp/spec['file'],optimize=True)
  # Companion magenta art is exported from the generated sprite, not reillustrated.
  chroma=Image.new('RGB',im.size,(255,0,255));chroma.paste(im,mask=im.getchannel('A'))
  chroma.save(grp/(p.stem+'-Magenta.png'),optimize=True)
  answers.append({'id':spec['id'],'name':spec['name'],'nature':spec['nature'],'biome':spec['biome'],'file':f'Archipels/{spec["file"]}',
      'x':x,'y':y,'w':w,'h':h,'main':ids[0],'components':ids,'port_souhaite':[round(x+spec['port'][0]*w),round(y+spec['port'][1]*h)],
      'distance_min_du_decor_existant_px':round(near,2),'sha256_du_brut':sha256(p.read_bytes()).hexdigest()})
 combined.save(calques/'06-Archipels.png',optimize=True)
 addition=out>=101;assert np.array_equal(addition,np.asarray(combined)[...,3]>0) and not np.any(addition&(orig>0))
 assert np.array_equal(out[orig>0],orig[orig>0]);return combined,out,blocked,answers
