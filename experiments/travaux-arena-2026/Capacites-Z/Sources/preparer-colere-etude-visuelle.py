#!/usr/bin/env python3
"""Étude visuelle indépendante : lances et explosion autour de Tokorico."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,math,struct,numpy as np,subprocess
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Colere-du-Gardien-d-Alola/Generation-PMDO';C=H/'.cache/destiny-test/colere-frames';C.mkdir(exist_ok=True)
N=128;T=180

def clean(path):
 a=np.array(Image.open(path).convert('RGB'));r,g,b=(a[:,:,i].astype('int16') for i in range(3));green=(g>70)&(g>r*1.22)&(g>b*1.22);v=Image.fromarray(np.dstack([a,np.uint8(~green)*255]),'RGBA');return v.crop(v.getbbox())
spear=clean(P/'Sources/lance-lumiere.png').resize((13,53),Image.Resampling.NEAREST)
blast=clean(P/'Sources/explosion-lumiere.png')
b=(G/'Content/Particle/Moonlight_Sparkles.dir').read_bytes();l=struct.unpack_from('<q',b)[0];v=Image.open(io.BytesIO(b[8:8+l])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',b,l+8);spark=[v.crop((i*w,0,(i+1)*w,h)) for i in range(count)]
hero=Image.open(P/'Sources/tokorico-natif.png').convert('RGBA');bg=Image.open(H/'.cache/destiny-test/fond-colere.png').convert('RGB').crop((153,9,225,81)).resize((24,24),Image.Resampling.NEAREST)
back=[];front=[]
positions=[(-34,-10),(-20,-22),(19,-22),(34,-10),(-40,8),(40,8),(-25,20),(25,20)]
def paste(dst,img,x,y,alpha=1):
 if alpha<=0:return
 im=img.copy()
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda a:int(a*alpha)))
 dst.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
for t in range(T):
 a=Image.new('RGBA',(N,N));f=Image.new('RGBA',(N,N))
 if 0<=t<105:
  for j,(x,y) in enumerate(positions):
   age=t-(11+j*8);layer=a if y<0 else f
   if 0<=age<19:
    if age<8:
     # La lance arrive du haut, sans extrémité posée avant l'impact.
     paste(layer,spear,64+x,64+y-26-(8-age)*8)
    else:
     fade=max(0,1-(age-8)/11);paste(layer,spear,64+x,64+y-26,fade)
     if age-8<len(spark):paste(layer,spark[age-8].resize((25,25),Image.Resampling.NEAREST),64+x,64+y,fade)
  if t>18 and t<95:paste(a,spark[(t//4)%len(spark)].resize((56,56),Image.Resampling.NEAREST),64,64,.5)
 if 82<=t<143:
  age=t-82;size=min(116,int(16+age*8)) if age<16 else 116+min(10,(age-16)//4)
  alpha=min(1,(143-t)/18)
  paste(f,blast.resize((size,size),Image.Resampling.NEAREST),64,64,alpha)
  if age<8:
   d=ImageDraw.Draw(f);radius=max(1,16-age*2);d.ellipse((64-radius,64-radius,64+radius,64+radius),fill=(255,255,235,240))
 back.append(a);front.append(f)
 # Maquette de composition : sol et sprite natifs, pas une capture du moteur.
 scene=Image.new('RGBA',(160,120))
 for yy in range(0,120,24):
  for xx in range(0,160,24):scene.paste(bg,(xx,yy))
 scene.alpha_composite(a,(16,-4));scene.alpha_composite(hero,(80-hero.width//2,60-hero.height//2));scene.alpha_composite(f,(16,-4))
 scene.convert('RGB').resize((640,480),Image.Resampling.NEAREST).save(C/f'{t:03}.png')
def bank(frames,name):
 sheet=Image.new('RGBA',(N*T,N*8))
 for i,im in enumerate(frames):
  for d in range(8):sheet.alpha_composite(im,(i*N,d*N))
 z=io.BytesIO();sheet.save(z,format='PNG',optimize=True);raw=z.getvalue();(P/name).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T))
bank(back,'Colere_Lances_Arriere.dir');bank(front,'Colere_Lances_Explosion_Avant.dir')
for frames,name in [(back,'lances-arriere-180-images.png'),(front,'lances-explosion-avant-180-images.png')]:
 sheet=Image.new('RGBA',(N*10,N*18))
 for i,im in enumerate(frames):sheet.alpha_composite(im,((i%10)*N,(i//10)*N))
 sheet.save(P/name,optimize=True)
print('Séquence créée : 180 images, deux banques, sol et personnage natifs.')
