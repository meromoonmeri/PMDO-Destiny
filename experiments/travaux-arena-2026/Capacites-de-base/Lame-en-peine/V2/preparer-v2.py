#!/usr/bin/env python3
"""Lame en Peine V2 : rémanences et lacérations spatiales, pour le banc isolé."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,math,json,copy,shutil
P=Path(__file__).resolve().parent;BASE=P.parent;G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'

def clean(p,n):
 im=Image.open(p).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.asarray(im).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];mask=(g>100)&(g>r+45)&(g>b+45);out=Image.fromarray(np.dstack((a.astype('uint8'),np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def paste(c,im,x,y,w,h,alpha=1,angle=0,flip=False):
 if min(w,h)<1 or alpha<=0:return
 v=im.resize((int(w),int(h)),Image.Resampling.NEAREST)
 if flip:v=v.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if angle:v=v.rotate(angle,Image.Resampling.NEAREST,expand=True)
 if alpha<1:
  a=np.asarray(v).copy();a[:,:,:3]=(a[:,:,:3].astype('float32')*alpha).astype('uint8');a[:,:,3]=(a[:,:,3].astype('float32')*alpha).astype('uint8');v=Image.fromarray(a,'RGBA')
 c.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def bank(name,fs):
 w,h=fs[0].size;sheet=Image.new('RGBA',(w*len(fs),h));preview=Image.new('RGBA',(w*8,h*math.ceil(len(fs)/8)))
 for i,f in enumerate(fs):sheet.alpha_composite(f,(i*w,0));preview.alpha_composite(f,((i%8)*w,(i//8)*h))
 b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,0,len(fs)));preview.save(P/(name+'-planche.png'))
def sprites():
 b=(G/'Content/Chara/937.chara').read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n');n=struct.unpack_from('<q',b,i-8)[0];im=Image.open(io.BytesIO(b[i:i+n])).convert('RGBA');w,h,_,_=struct.unpack_from('<iiii',b,i+n)
 poses=[]
 for row,col in [(2,1),(2,4),(2,7),(3,4),(4,0),(4,3),(5,2),(5,5)]:
  v=im.crop((col*w,row*h,(col+1)*w,(row+1)*h));poses.append(v.crop(v.getbbox()))
 return poses
slash=clean(P/'Sources/coupure-spatiale.png',140);rift=clean(P/'Sources/faille-impact.png',120);wisp=clean(BASE/'Sources/feu-follet-sombre.png',64);pose=sprites()
N=160;T=96;frames=[]
# Une grille spatiale naît de coups successifs, pas de traits statiques posés d'emblée.
segments=[]
for direction in (1,-1):
 for j,offset in enumerate((-48,-24,0,24,48)):
  if direction==1:pt=(20,35+offset,140,125+offset)
  else:pt=(20,125+offset,140,35+offset)
  segments.append((pt,14+j*5+(3 if direction<0 else 0)))
for t in range(T):
 f=Image.new('RGBA',(N,N));draw=ImageDraw.Draw(f)
 # Flammes spectrales et véritables images natives de Malvalame utilisées en rémanence.
 for wave in range(10):
  age=t-(3+wave*5)
  if not 0<=age<12:continue
  a=math.tau*(wave%8)/8+.2;x=80+math.cos(a)*55;y=80+math.sin(a)*42
  fade=min(1,(age+1)/2,(12-age)/6)
  for lag in (2,1):
   if age>=lag:
    tx=x-math.cos(a)*lag*4;ty=y-math.sin(a)*lag*3;paste(f,pose[wave%len(pose)],tx,ty,27,32,fade*(.16 if lag==2 else .28),flip=wave%2==1)
  paste(f,pose[wave%len(pose)],x,y,29,34,fade*.76,flip=wave%2==1)
  paste(f,wisp,x+math.sin(a)*12,y+math.cos(a)*8,14,16,fade*.7)
 # Lacérations en diagonales croisées, générées et maintenues brièvement avant l'éclatement.
 draw=ImageDraw.Draw(f)
 for (x1,y1,x2,y2),start in segments:
  age=t-start
  if not 0<=age<45:continue
  grow=min(1,(age+1)/3);endx=x1+(x2-x1)*grow;endy=y1+(y2-y1)*grow;fade=min(1,(45-age)/10)
  # couleurs prémultipliées : les halos restent transparents en jeu.
  draw.line((x1,y1,endx,endy), fill=(int(34*fade),int(5*fade),int(48*fade),int(230*fade)),width=5)
  draw.line((x1,y1,endx,endy), fill=(int(120*fade),int(35*fade),int(190*fade),int(240*fade)),width=3)
  draw.line((x1,y1,endx,endy), fill=(int(238*fade),int(208*fade),int(255*fade),int(255*fade)),width=1)
 for j,start in enumerate((17,26,35,44,53)):
  age=t-start
  if 0<=age<12:
   grow=min(1,(age+1)/3);fade=min(1,(12-age)/5);paste(f,slash,80+(j-2)*6,80+(j%2)*3,106*grow,106*grow,fade*.8,flip=j%2==1)
 if 61<=t<90:
  age=t-61;size=24+min(age*9,100);fade=min(1,(age+1)/4,(29-age)/10);paste(f,rift,80,80,size,size,fade*.8)
 for j in range(5):
  age=t-(10+j*8)
  if 0<=age<48:
   a=j*math.tau/5+age*.08;r=30+age*.35;x=80+math.cos(a)*r;y=80+math.sin(a)*r*.65
   paste(f,wisp,x,y,13,15,min(1,(age+1)/5,(48-age)/9)*.8)
 frames.append(f)
bank('LameEnPeineV2_Slashes',frames)
shutil.copy2(BASE/'LameEnPeine_Charge.dir',P/'LameEnPeine_Charge.dir')
z=json.loads((BASE/'bitter_blade-v1-test-only.json').read_text());o=z['Object'];fx=o['Data']['HitFX'];fx['Emitter']['Anim']['Anim']['AnimIndex']='LameEnPeineV2_Slashes';fx['Delay']=T;fx['Sound']='DUN_Night_Slash';fx['ScreenMovement']={'MinShake':0,'MaxShake':2,'MaxShakeTime':20};(P/'bitter_blade-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Lacérations spatiales 96 images, rémanences de sprites PMDO, fiche de banc créée.')
