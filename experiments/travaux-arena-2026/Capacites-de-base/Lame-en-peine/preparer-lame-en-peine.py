#!/usr/bin/env python3
"""Prototype Lame en Peine : séquences de charge et d'entailles en copie de banc."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-de-base/Lame-en-peine'

def clean(n,limit=96):
 im=Image.open(P/'Sources'/n).convert('RGB');im.thumbnail((limit,limit),Image.Resampling.NEAREST);a=np.asarray(im).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 mask=(g>100)&(g>r+45)&(g>b+45);v=Image.fromarray(np.dstack((a.astype('uint8'),np.where(mask,0,255).astype('uint8'))),'RGBA');return v.crop(v.getbbox())
def native(n):
 b=(G/'Content/Particle'/(n+'.dir')).read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',b,k+8);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(count)]
def paste(canvas,sprite,x,y,w,h,alpha=1,angle=0):
 if w<1 or h<1 or alpha<=0:return
 v=sprite.resize((int(w),int(h)),Image.Resampling.NEAREST)
 if angle:v=v.rotate(angle,resample=Image.Resampling.NEAREST,expand=True)
 if alpha<1:v.putalpha(v.getchannel('A').point(lambda a:round(a*max(0,min(1,alpha)))))
 canvas.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def bank(name,frames,dirs=False):
 w,h=frames[0].size;rows=8 if dirs else 1;sheet=Image.new('RGBA',(w*len(frames),h*rows));preview=Image.new('RGBA',(w*8,h*math.ceil(len(frames)/8)))
 for i,frame in enumerate(frames):
  preview.alpha_composite(frame,((i%8)*w,(i//8)*h))
  for j in range(rows):
   f=frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if dirs and j in (1,2,3) else frame
   sheet.alpha_composite(f,(w*i,h*j))
 bio=io.BytesIO();sheet.save(bio,format='PNG',optimize=True);raw=bio.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4 if dirs else 0,len(frames)));preview.save(P/(name+'-planche.png'))
blade=clean('lame-dimensionnelle.png');flame=clean('feu-follet-sombre.png',64);wisp=native('Will_O_Wisp')
# Flammes autour de Malvalame, progression d'apparition puis extinction.
fs=[]
for t in range(48):
 f=Image.new('RGBA',(96,96));env=min(1,t/7,(47-t)/7)
 for j in range(4):
  ang=j*math.tau/4+t*.12;r=29-4*math.sin(t*.1);x=48+math.cos(ang)*r;y=50+math.sin(ang)*r*.48
  size=13+int(3*(1+math.sin(t*.5+j)));paste(f,flame,x,y,size,size*1.3,env*.9)
 if t<36:paste(f,wisp[min(len(wisp)-1,t//4)],48,54,50,50,env*.7)
 fs.append(f)
bank('LameEnPeine_Charge',fs,True)
# Entailles successives : trois arcs décalés et de tailles différentes pour suggérer la profondeur.
fs=[]
for t in range(48):
 f=Image.new('RGBA',(112,112))
 for j,(x,y,angle) in enumerate([(42,61,25),(56,54,-25),(70,48,20)]):
  age=t-(j*6)
  if 0<=age<21:
   appear=min(1,(age+1)/4);fade=min(1,(21-age)/7);size=16+int(59*appear);width=int(size*(.72+.24*math.sin(age*.17)))
   # Reprise translucide, plus petite et décalée, puis tranchant net au premier plan.
   paste(f,blade,x-4,y+4,max(1,width-7),max(1,size-7),fade*.38,angle)
   paste(f,blade,x,y,width,size,fade,angle)
 for j in range(4):
  age=t-(3+j*3)
  if 0<=age<34:
   angle=j*math.tau/4+t*.12;r=13+age*.8;x=56+math.cos(angle)*r;y=59+math.sin(angle)*r*.7-age*.22
   fade=min(1,(age+1)/5,(34-age)/7);size=12+2*math.sin(t*.5+j)
   paste(f,flame,x,y,size,size*1.3,fade*.95)
 if t<32:paste(f,wisp[min(len(wisp)-1,t//4)],56,59,62,62,min(1,t/3,(32-t)/6)*.8)
 fs.append(f)
bank('LameEnPeine_Entailles',fs,True)
def read(n):return json.loads((G/'Data/Skill'/(n+'.json')).read_text(encoding='utf-8-sig'))
orig=read('bitter_blade');z=copy.deepcopy(orig);o=z['Object'];o['Released']=True;o['Name']['LocalTexts']['fr']='Lame en Peine';o['Desc']['LocalTexts']['fr']='Entaille la cible et restaure au lanceur la moitié des dégâts infligés.'
o['Data']['SkillStates']=[{'$type':'PMDC.Dungeon.ContactState, PMDC'},{'$type':'PMDC.Dungeon.BladeState, PMDC'},{'$type':'PMDC.Dungeon.HealState, PMDC'},{'$type':'RogueEssence.Dungeon.BasePowerState, RogueEssence','Power':90}]
o['Data']['AfterActions']=[{'Key':{'str':[0]},'Value':{'$type':'PMDC.Dungeon.HPDrainEvent, PMDC','DrainFraction':2}}]
# Emprunter au moteur ses émetteurs et sons Feu/ombre ; pas de changement de portée.
ref=read('dragon_pulse')['Object']; act=o['HitboxAction'];charge=copy.deepcopy(ref['Data']['HitFX']);charge['Emitter']={'$type':'RogueEssence.Content.SingleEmitter, RogueEssence','LocHeight':0,'finished':False,'Offset':0,'Anim':{'$type':'RogueEssence.Content.StaticAnim, RogueEssence','Anim':{'AnimIndex':'LameEnPeine_Charge','FrameTime':1,'StartFrame':-1,'EndFrame':-1,'AnimDir':-1,'Alpha':255,'AnimFlip':0},'TotalTime':0,'Cycles':1,'FrameOffset':0},'Layer':2,'UseDest':False};charge['Delay']=40;charge['Sound']='DUN_Will-O-Wisp';act['PreActions']=[charge];act['ActionFX']['Sound']='DUN_Night_Slash';act['CharAnimData']={'$type':'RogueEssence.Dungeon.CharAnimFrameType, RogueEssence','ActionType':10}
hit=copy.deepcopy(charge);hit['Emitter']['Anim']['Anim']['AnimIndex']='LameEnPeine_Entailles';hit['Emitter']['Anim']['Anim']['FrameTime']=1;hit['Delay']=48;hit['Sound']='DUN_Shadow_Force';o['Data']['HitFX']=hit
(P/'bitter_blade-original.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2));(P/'bitter_blade-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('Deux banques de 48 images et fiche de banc avec absorption native, non installées.')
