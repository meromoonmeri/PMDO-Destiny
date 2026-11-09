from pathlib import Path
import io,gzip,struct,ijson,collections,json
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent;BASE=R/'base';COR=R/'corrections-escalier-en-cours';pts=[(648,312),(648,416),(664,288),(856,288),(872,328),(880,376),(888,416)];times=list(range(0,721,10));cache={};banks={}
def tile(ref):
 name=ref.get('Sheet','');xy=ref['TexLoc'];key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key not in cache:
  if name not in banks:
   path=COR/'game/Content/Tile'/f'{name}.tile';path=path if path.exists() else BASE/'game/Content/Tile'/f'{name}.tile';b=path.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8;d={}
   for i in range(n):
    x,y,o=struct.unpack_from('<iiq',b,8+16*i);d[x,y]=o
   banks[name]=b,d
  b,d=banks[name];o=d[xy['X'],xy['Y']];n=struct.unpack_from('<q',b,o)[0];cache[key]=Image.open(io.BytesIO(b[o+8:o+8+n])).convert('RGBA')
 return cache[key]
# 48×40 px, avec les décors au-dessus et toutes les couches, 73 moments du PPCM.
def render(path):
 result=[[Image.new('RGBA',(48,40)) for t in times] for _ in pts]
 with gzip.open(path,'rb') as f:
  f.read(3)
  for layer in ijson.items(f,'Object.Layers.item'):
   for q,(sx,sy) in enumerate(pts):
    x0,y0=sx-8,sy-16
    for x in range(x0//8,(x0+48)//8):
     for y in range(y0//8,(y0+40)//8):
      for a in layer['Tiles'][x][y].get('Layers',[]):
       frames=a.get('Frames',[]);duration=a.get('FrameLength',60)
       if not frames:continue
       for it,t in enumerate(times):
        im=tile(frames[(t//duration)%len(frames)])
        if im:result[q][it].alpha_composite(im,(x*8-x0,y*8-y0))
 return result
before=render(BASE/'payload/reverie_centre.rsground.gz');after=render(COR/'payload/reverie_centre.rsground.gz');mask=np.asarray(Image.open('original-pierre-frame-1.png'))[:,:,3]>0;base=np.asarray(Image.open('original-pierre-frame-0.png'))[:,:,3]>0;ripple=mask&(~base)
# Différences autorisées : bandes coupées et exactement les 27 pixels natifs de vague,
# dans chaque région et chaque instant. Les personnages ne sont pas dans ce rendu.
sums=[]
for q,p in enumerate(pts):
 allowed=np.zeros((40,48),bool);x0,y0=p[0]-8,p[1]-16
 # Les crops proches peuvent aussi contenir un fragment de la pierre voisine.
 for sx,sy in pts:
  for y in range(4,16):
   for x in (sx,sx+1):
    dx,dy=x-x0,sy+y-y0
    if 0<=dx<48 and 0<=dy<40:allowed[dy,dx]=True
  for yy,xx in zip(*np.where(ripple)):
   dx,dy=sx+xx-x0,sy-8+yy-y0
   if 0<=dx<48 and 0<=dy<40:allowed[dy,dx]=True
 for it,t in enumerate(times):
  a=np.asarray(before[q][it]);b=np.asarray(after[q][it]);d=np.any(a!=b,axis=2)
  if np.any(d&(~allowed)):
   ys,xs=np.where(d&(~allowed));raise AssertionError((p,t,list(zip(xs.tolist(),ys.tolist()))[:10]))
  sums.append(int(d.sum()))
# Les 9 images sources restent bien reconnues dans les sept cases, en plus des animations antérieures.
with gzip.open(COR/'payload/reverie_centre.rsground.gz','rb') as f:
 f.read(3)
 for l in ijson.items(f,'Object.Layers.item'):
  if l['Name']!='Objects':continue
  for sx,sy in pts:
   for cx in range(4):
    a=[a for a in l['Tiles'][sx//8+cx][(sy+8)//8]['Layers'] if a.get('Frames') and a['Frames'][0]['Sheet']=='Reverie_Ondulations_Rochers_056']
    assert len(a)==1 and len(a[0]['Frames'])==9 and a[0]['FrameLength']==10
# GIF 7 pierres (même durée effective) avant et après, chaque colonne un instant.
outframes=[]
for it,t in enumerate(times[:9]):
 board=Image.new('RGB',(7*144,2*120),(28,36,40))
 for q in range(7):
  for row,imgs in enumerate([before,after]):board.paste(imgs[q][it].convert('RGB').resize((144,120),Image.Resampling.NEAREST),(q*144,row*120))
 outframes.append(board)
outframes[0].save(R/'pierres-avant-apres-9-phases.gif',save_all=True,append_images=outframes[1:],duration=167,loop=0,optimize=False)
print('PASS :',len(pts),'pierres,',len(times),'instants ; toutes les modifications sont dans les bandes ou les 27 pixels de vague natifs ; différences par image',min(sums),max(sums),flush=True)
