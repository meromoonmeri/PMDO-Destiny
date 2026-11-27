#!/usr/bin/env python3
"""Canon Blindé V2 : ressources animées et fiche de banc, sans installation."""
from pathlib import Path
from PIL import Image, ImageDraw
import io,struct,math,json,copy,numpy as np
P=Path(__file__).resolve().parent; BASE=P.parent; G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'

def png(im):
 s=io.BytesIO();im.save(s,format='PNG',optimize=True);return s.getvalue()
def native(name):
 b=(G/'Content/Particle'/f'{name}.dir').read_bytes();n=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+n])).convert('RGBA');w,h,dirs,count=struct.unpack_from('<iiii',b,8+n);assert dirs==0
 return [im.crop((w*i,0,w*(i+1),h)) for i in range(count)]
def clean(path,size=128):
 im=Image.open(path).convert('RGB');im.thumbnail((size,size),Image.Resampling.NEAREST);a=np.asarray(im).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];bg=(g>90)&(g>r+45)&(g>b+45);out=Image.fromarray(np.dstack((a.astype('uint8'),np.where(bg,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def paste(dst,src,x,y,w,h,alpha=1,angle=0):
 if min(w,h)<1 or alpha<=0:return
 im=src.resize((int(w),int(h)),Image.Resampling.NEAREST)
 if angle:im=im.rotate(angle,resample=Image.Resampling.NEAREST,expand=True)
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda a:int(a*min(1,max(0,alpha)))))
 dst.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
def bank(name,frames):
 w,h=frames[0].size;sheet=Image.new('RGBA',(w*len(frames),h));preview=Image.new('RGBA',(w*8,h*math.ceil(len(frames)/8)))
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*w,0));preview.alpha_composite(f,((i%8)*w,(i//8)*h))
 b=png(sheet);(P/(name+'.dir')).write_bytes(struct.pack('<q',len(b))+b+struct.pack('<iiii',w,h,0,len(frames)));preview.save(P/(name+'-planche.png'))

flame=clean(P/'Sources/etincelle-feu.png',64);flamejet=clean(BASE/'Sources/flamme-rayon.png',128)
# Pulsation au centre et trois vagues de particules progressant réellement vers le lanceur.
charge=[]
for t in range(78):
 f=Image.new('RGBA',(160,160));draw=ImageDraw.Draw(f);env=min(1,(t+1)/7,(78-t)/8);pulse=(1+math.sin(t*math.tau/18))/2
 # Aura translucide derrière Carmadura ; l'image est jouée sur la couche arrière.
 for rad,alpha in [(25+8*pulse,24),(17+6*pulse,45),(9+4*pulse,90)]:
  r=int(rad);a=int(alpha*env);draw.ellipse((80-r,80-r,80+r,80+r),fill=(a,int(a*.40),int(a*.04),a))
 for wave,start in enumerate((0,20,40,57)):
  age=t-start
  if not 0<=age<25:continue
  progress=age/24
  for j in range(8):
   a=math.tau*j/8+wave*.37+progress*.3
   radius=70*(1-progress)+11
   x=80+math.cos(a)*radius;y=80+math.sin(a)*radius*.70
   size=8+int(5*(1-progress)+3*pulse);opacity=env*min(1,(age+1)/4,(25-age)/4)
   paste(f,flame,x,y,size,size,opacity,angle=-(a*180/math.pi)+45)
 # Un noyau minuscule seulement, pour ne pas cacher le personnage.
 if t>50:paste(f,flame,80,80,10+6*pulse,10+6*pulse,env*.65)
 charge.append(f)
bank('CanonBlindeV2_Charge',charge)
# Corps du rayon : 112 pixels contre 32 pour Ultralaser natif. La largeur est graphique.
N=16;W=112;sheet=Image.new('RGBA',(N*W,225));rect=[]
for part in range(3):
 for t in range(N):
  f=Image.new('RGBA',(W,112 if part!=1 else 1));pulse=math.sin(t*math.tau/N)
  if part==0:paste(f,flamejet,56,55,75+7*pulse,108)
  elif part==2:paste(f,flamejet,56,55,67+6*pulse,106)
  else:
   for x in range(W):
    a=abs((x-55.5)/(51+2*pulse));c=(255,255,230,255) if a<.20 else (255,222,58,255) if a<.40 else (255,141,8,255) if a<.65 else (224,54,4,255) if a<.87 else (137,22,2,210) if a<.96 else (0,0,0,0);f.putpixel((x,0),c)
  y=[0,112,113][part];sheet.alpha_composite(f,(t*W,y));rect.append((t*W,y,W,f.height))
b=png(sheet);(P/'CanonBlindeV2_Rayon.beam').write_bytes(struct.pack('<q',len(b))+b+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',N));sheet.save(P/'CanonBlindeV2_Rayon-planche.png')
# Réutilisation des vraies 15 images de l'explosion de Destruction.
expl=native('Explosion');flames=native('Flamethrower');column=native('Fire_Column_Ranger');impact=[]
# Détonations en grappes, échelonnées comme l'émetteur circulaire de Destruction.
clusters=[(0,0,0,116),(-38,-9,5,96),(35,-20,8,101),(-26,33,10,92),(36,30,13,100),(1,-44,15,90)]
for t in range(68):
 f=Image.new('RGBA',(200,200))
 for x,y,start,size in clusters:
  age=t-start
  if 0<=age<45:
   frame=expl[min(14,age//3)]
   paste(f,frame,100+x,100+y,size,size)
 # L'animation native de flammes accompagne la détonation, sans remplacer son mouvement.
 for x,y,start,size in [(-50,3,9,64),(40,-18,12,72),(5,37,16,68),(-12,-45,21,58)]:
  age=t-start
  if 0<=age<36:paste(f,flames[min(11,age//3)],100+x,100+y,size,size)
 if 10<=t<52:paste(f,column[min(6,(t-10)//6)],100,100,94,94,.55)
 impact.append(f)
bank('CanonBlindeV2_DestructionFeu',impact)
# Reprise de la fiche V1 : mêmes effets, seule la chorégraphie change.
z=json.loads((BASE/'armor_cannon-v1-test-only.json').read_text());o=z['Object'];act=o['HitboxAction'];act['Anim']['AnimIndex']='CanonBlindeV2_Rayon';act['Anim']['FrameTime']=2
act['PreActions']=[{'Delay':78,'AbsoluteDelay':False,'Sound':'DUN_Flamethrower','Emitter':{'$type':'RogueEssence.Content.SingleEmitter, RogueEssence','LocHeight':0,'finished':False,'Offset':0,'Anim':{'$type':'RogueEssence.Content.StaticAnim, RogueEssence','Anim':{'AnimIndex':'CanonBlindeV2_Charge','FrameTime':1,'StartFrame':-1,'EndFrame':-1,'AnimDir':-1,'Alpha':255,'AnimFlip':0},'TotalTime':0,'Cycles':1,'FrameOffset':0},'Layer':0,'UseDest':False},'ScreenMovement':{'MinShake':0,'MaxShake':0,'MaxShakeTime':0}}]
(P/'armor_cannon-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Charge 78 images, rayon 112 px / 16 images, Destruction de feu 68 images.')
