from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
im=Image.open(p/'fontaine-classique-reverie-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>120)&(b>100)&(r-g>50)&(b-g>40),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((72,56),Image.Resampling.NEAREST);can=Image.new('RGBA',(72,56));can.alpha_composite(im,((72-im.width)//2,(56-im.height)//2));can.save(p/'Fontaine-classique-Reverie-base.png');can.resize((720,560),Image.Resampling.NEAREST).save(p/'Fontaine-classique-Reverie-zoom.png');print('taille',im.size)
from PIL import ImageDraw
import math
# The three water colors come from the actual Reverie Geo 03 river sheet.
base=can.copy(); pix=base.load(); surf=(128,216,224,255);dark=(88,176,200,255);bright=(152,232,240,255)
for y in range(8,35):
 for x in range(72):
  r,g,b,a=pix[x,y]
  if a and b>r*1.15 and g>r*1.15:
   if 31<=x<=41 and 10<=y<=21 and r>145: pix[x,y]=bright
   elif y<=13 and r<145: pix[x,y]=dark
   else: pix[x,y]=surf
frames=[]
for k in range(12):
 f=base.copy();d=ImageDraw.Draw(f)
 for offset in (0,6):
  phase=((k+offset)%12)/12
  rx=2+round(phase*16);ry=max(1,round(rx*.43))
  strength=.48*(1-phase)
  col=tuple(round(surf[i]+(bright[i]-surf[i])*strength) for i in range(3))+(255,)
  for j in range(64):
   if j%16 in (0,1,2,8,9):continue
   angle=math.tau*j/64
   x=round(36+rx*math.cos(angle));y=round(22+ry*math.sin(angle))
   if 0<=x<72 and 0<=y<56 and base.getpixel((x,y))==surf and not (33<=x<=38 and y<=21):d.point((x,y),fill=col)
 for y in range(13,20):
  if (y-k)%12 in (0,1):
   for x in (35,36):
    if base.getpixel((x,y)) in (bright,surf):d.point((x,y),fill=(185,244,246,255))
 frames.append(f);f.save(p/f'Fontaine-classique-Reverie-{k+1:02}.png')
sheet=Image.new('RGBA',(72*12,56));prev=[]
for i,f in enumerate(frames):
 sheet.alpha_composite(f,(72*i,0)); bg=Image.new('RGBA',f.size,(31,29,55,255));bg.alpha_composite(f);prev.append(bg.convert('RGB').resize((432,336),Image.Resampling.NEAREST))
sheet.save(p/'Fontaine-classique-Reverie-tilesheet.png');prev[0].save(p/'Fontaine-classique-Reverie-animation.gif',save_all=True,append_images=prev[1:],duration=100,loop=0,disposal=2,optimize=False)
print('12 frames, 72x56, boucle 1.2s')
