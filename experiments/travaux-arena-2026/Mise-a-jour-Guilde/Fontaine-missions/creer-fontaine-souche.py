from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
im=Image.open(p/'fontaine-pmd-nouveau-design-generation.png').convert('RGBA')
a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>105)&(b>85)&(r-g>50)&(b-g>40),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((72,52),Image.Resampling.NEAREST);can=Image.new('RGBA',(72,52));can.alpha_composite(im,((72-im.width)//2,(52-im.height)//2));can.save(p/'Souche-base.png');can.resize((864,624),Image.Resampling.NEAREST).save(p/'Souche-base-zoom.png')
print(im.size)
from PIL import ImageDraw
import math
base=can.copy(); px=base.load()
# Remove generated static splash only inside the flat water; preserve wood and the vertical stream.
water=px[33,20]
for y in range(18,24):
 for x in range(38,51):
  c=px[x,y]
  if c[3] and c[1]>150 and c[2]>125 and c[0]>100 and x!=43: px[x,y]=water
frames=[]
for k in range(12):
 f=base.copy(); d=ImageDraw.Draw(f)
 # Two concentric ripples, each reappearing when its radius has faded to zero.
 for off in (0,6):
  q=((k+off)%12)/12
  rx=1+int(q*6); ry=max(1,round(rx*.38)); fade=1-q
  color=tuple(round(water[i]+(target-water[i])*.55*fade) for i,target in enumerate((166,239,221)))+(255,)
  cx,cy=43,20
  # broken ellipse highlights are clipped by the bowl and remain entirely in the water
  for j in range(24):
   theta=2*math.pi*j/24
   if j in (2,3,10,11,14,15,22,23): continue
   x=round(cx+rx*math.cos(theta));y=round(cy+ry*math.sin(theta))
   if 37<=x<=50 and 18<=y<=23 and x!=43: d.point((x,y),fill=color)
 # tiny moving light on the existing stream, preserving its silhouette
 for y in range(13,19):
  if (y-k)%6 in (0,1): d.point((43,y),fill=(160,236,219,255))
 frames.append(f);f.save(p/f'Souche-animation-{k+1:02}.png')
sheet=Image.new('RGBA',(72*len(frames),52))
for i,f in enumerate(frames): sheet.alpha_composite(f,(72*i,0))
sheet.save(p/'Souche-tilesheet-12-images.png')
# GIF preview uses opaque neutral backdrop, with nearest-neighbour enlarged pixels.
preview=[]
for f in frames:
 b=Image.new('RGBA',f.size,(31,29,55,255));b.alpha_composite(f);preview.append(b.convert('RGB').resize((432,312),Image.Resampling.NEAREST))
preview[0].save(p/'Souche-animation-apercu.gif',save_all=True,append_images=preview[1:],duration=100,loop=0,disposal=2,optimize=False)
print('12 frames, 72x52, 100ms')
