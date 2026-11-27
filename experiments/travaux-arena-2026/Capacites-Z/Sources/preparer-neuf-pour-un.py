#!/usr/bin/env python3
"""Prototype Neuf pour Un : création uniquement, pas d'installation dans le jeu."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,math,json,copy
H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Neuf-pour-Un/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
names=[(134,'Aquali',(70,180,255)),(135,'Voltali',(255,224,55)),(136,'Pyroli',(255,125,55)),(196,'Mentali',(213,135,255)),(197,'Noctali',(247,212,90)),(470,'Phyllali',(137,224,90)),(471,'Givrali',(126,235,255)),(700,'Nymphali',(255,153,208))]
sprites=[]
for num,name,col in names:
 b=(G/'Content/Chara'/f'{num}.chara').read_bytes();pos=b.find(b'\x89PNG\r\n\x1a\n');assert pos>7
 size=struct.unpack_from('<q',b,pos-8)[0];im=Image.open(io.BytesIO(b[pos:pos+size])).convert('RGBA');w,h,_,_=struct.unpack_from('<iiii',b,pos+size)
 im=im.crop((0,0,w,h));im=im.crop(im.getbbox());im.thumbnail((27,28),Image.Resampling.NEAREST);sprites.append(im)
# Each frame is one shared effect in screen coordinates, not eight map occupants.
N=160;T=72;frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f);cx=80;cy=79
 fade=min(1,(T-t)/8)
 ringalpha=int(120*min(1,t/10)*fade)
 d.ellipse((19,32,141,128),outline=(255,231,169,ringalpha),width=1)
 for j,((num,name,col),sprite) in enumerate(zip(names,sprites)):
  a=-math.pi/2+j*math.tau/8;x=cx+58*math.cos(a);y=cy+46*math.sin(a)+math.sin(t*.13+j)*1.2
  reveal=max(0,min(1,(t-j*3)/6))*fade
  if not reveal:continue
  if t>=32:
   beam=min(1,(t-32)/10);sx=x+(cx-x)*.13;sy=y+(cy-y)*.13;ex=sx+(cx-sx)*beam;ey=sy+(cy-sy)*beam
   d.line((sx,sy,ex,ey),fill=(*col,int(125*reveal)),width=4);d.line((sx,sy,ex,ey),fill=(255,255,239,int(235*reveal)),width=1)
  r=18;d.ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=(*col,int(36*reveal)),outline=(*col,int(160*reveal)),width=1)
  temp=sprite.copy();temp.putalpha(temp.getchannel('A').point(lambda v:int(v*reveal)))
  f.alpha_composite(temp,(round(x-temp.width/2),round(y-temp.height/2)))
  d=ImageDraw.Draw(f)
 if 32<=t<67:
  power=min(1,(t-32)/12,(67-t)/7);r=int(3+8*power)
  d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,244,166,int(200*power)),outline=(255,255,243,int(255*power)),width=2)
  for j in range(8):
   a=math.tau*j/8+t*.08;rr=r+4;px=cx+rr*math.cos(a);py=cy+rr*math.sin(a)
   d.line((px-2,py,px+2,py),fill=(255,255,220,int(230*power)),width=1)
 frames.append(f)
sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*9,N),(25,26,35,255))
for r in range(8):
 for i,im in enumerate(frames):sheet.alpha_composite(im,(N*i,N*r))
for i,t in enumerate([0,9,18,27,36,45,54,63,71]):preview.alpha_composite(frames[t],(N*i,0))
b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();(P/'NeufPourUn_Evolitions.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.convert('RGB').save(P/'progression-neuf-pour-un.png')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=read('extreme_evoboost');(P/'extreme_evoboost-original.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(read('quiver_dance')['Object']['HitboxAction']);act['PreActions']=[];act['CharAnimData']['ActionType']=5;act['ActionFX']['Sound']='DUN_Wish';a['HitboxAction']=act
a['Explosion']['TargetAlignments']=1
sample=copy.deepcopy(read('quiver_dance')['Object']['Data']['OnHits'][0]);a['Data']['OnHits']=[]
for key in ['mod_attack','mod_defense','mod_special_attack','mod_special_defense','mod_speed']:
 e=copy.deepcopy(sample);e['Value']['Stack']=2;e['Value']['StatusID']=key;a['Data']['OnHits'].append(e)
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'NeufPourUn_Visuel','ArgTable':'{}'}}]
a['Data']['HitFX']=copy.deepcopy(read('quiver_dance')['Object']['Data']['HitFX'])
(P/'extreme_evoboost-test-only.json').write_text(json.dumps(z,indent=2,ensure_ascii=False))
print('Neuf pour Un : huit sprites PMDO, 72 images, fiche self + cinq boosts ; aucun jeu modifié.')
