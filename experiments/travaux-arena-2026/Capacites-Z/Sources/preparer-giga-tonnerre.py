#!/usr/bin/env python3
"""Banc Giga-Tonnerre ; installer uniquement dans copie, après sauvegarde."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,math,json,copy,shutil
H=Path.home();R=H/'Capacites-Z';G=H/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Giga-Tonnerre/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.array(im);v=a.astype('int16');bg=(v[:,:,1]>125)&(v[:,:,1]>v[:,:,0]+45)&(v[:,:,1]>v[:,:,2]+45);o=Image.fromarray(np.dstack((a,np.where(bg,0,255).astype('uint8'))),'RGBA');return o.crop(o.getbbox())
def paste(im,p,w,h,x,y,alpha=255):
 if alpha<=0:return
 s=p.resize((int(w),int(h)),Image.Resampling.NEAREST);s.putalpha(s.getchannel('A').point(lambda v:v*alpha//255));im.alpha_composite(s,(round(x-w/2),round(y-h/2)))
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(28,25,35,255))
 for r in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,r*N))
 for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0))
 check.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)))
bolt=cut('source-eclair-prismatique.png',120);burst=cut('source-impact-prismatique.png',100)
N=112;frames=[]
for t in range(32):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f);k=min(1,(t+1)/5,(32-t)/6);r=int(15+5*math.sin(t*.27));a=int(180*k)
 d.ellipse((56-r,54-r,56+r,54+r),fill=(255,220,55,int(40*k)),outline=(255,245,143,a),width=2)
 for j,c in enumerate([(255,210,80,a),(93,222,255,a),(255,120,211,a),(189,120,255,a)]):
  theta=j*math.pi/2+t*.2;x=56+int((r+9)*math.cos(theta));y=54+int((r+9)*math.sin(theta));d.line((x-2,y,x+2,y),fill=c,width=2);d.line((x,y-2,x,y+2),fill=c,width=2)
 if t>9:
  for j in range(3):
   angle=35+110*j+t*3;pic=bolt.rotate(angle,resample=Image.Resampling.NEAREST,expand=True);paste(f,pic,27,27,56+19*math.cos(angle*math.pi/180),54+19*math.sin(angle*math.pi/180),int(180*k))
 frames.append(f)
bank('GigaTonnerre_Charge',frames,N)
N=144;frames=[]
for t in range(34):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 if 1<=t<18:
  k=t-1;alpha=255 if k<9 else max(0,255-(k-8)*30);paste(f,bolt,40,102,72,44,alpha)
 if 5<=t<29:
  k=t-5;size=min(78,15+k*7);alpha=255 if k<12 else max(0,255-(k-11)*21);paste(f,burst,size,size,72,78,alpha);d=ImageDraw.Draw(f)
  r=min(55,8+k*3);d.ellipse((72-r,84-r//3,72+r,84+r//3),outline=(255,223,86,max(0,220-k*9)),width=2)
 frames.append(f)
bank('GigaTonnerre_Impact',frames,N)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=P/'ten_million_volt_thunderbolt-original.json';o=json.loads(orig.read_text(encoding='utf-8-sig')) if orig.exists() else read('ten_million_volt_thunderbolt');
if not orig.exists(): orig.write_text(json.dumps(o,ensure_ascii=False,indent=2))
z=copy.deepcopy(o);a=z['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(read('thunderbolt')['Object']['HitboxAction']);act.update(Rays=1,Range=3,Speed=8,StopAtHit=True,StopAtWall=True,HitTiles=False);act['CharAnimData']['ActionType']=5;act['Emitter']={'$type':'RogueEssence.Content.EmptyAttachEmitter, RogueEssence'};act['PreActions']=[];act['ActionFX']['Sound']='DUN_Shock_Wave';a['HitboxAction']=act
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='GigaTonnerre_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Delay']=45;hit['AbsoluteDelay']=True;hit['Sound']='DUN_Thunder';a['Data']['HitFX']=hit
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'GigaTonnerre_Charge','ArgTable':'{}'}}]
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'ten_million_volt_thunderbolt-test-only.json').write_text(s)
# Approximative red cap on only the five standing frames. It is a temporary edit of native Pikachu, not a new form.
p=G/'Content/Chara/25.chara';raw=p.read_bytes()
for pos in (124,67697):
 n=struct.unpack_from('<q',raw,pos)[0];im=Image.open(io.BytesIO(raw[pos+8:pos+8+n])).convert('RGBA');offpos=pos+8+n;w,h,shadow,count=struct.unpack_from('<iiii',raw,offpos);offs=[struct.unpack_from('<iiiiiiii',raw,offpos+16+i*32) for i in range(count)];d=ImageDraw.Draw(im)
 for x,y in [(0,0),(3,0),(6,0),(9,0),(1,1)]:
  hx,hy=offs[y*(im.width//w)+x][2:4];cx=x*w+w//2+hx;top=y*h+h//2+hy-9
  d.polygon([(cx-5,top+3),(cx-4,top+1),(cx-2,top),(cx+3,top),(cx+5,top+2),(cx+5,top+4),(cx-5,top+4)],fill=(98,20,33,255));d.rectangle((cx-4,top+1,cx+4,top+3),fill=(228,58,66,255));d.line((cx-4,top+4,cx+5,top+4),fill=(49,68,117,255));d.line((cx-1,top+1,cx+1,top+1),fill=(255,245,222,255))
 b=io.BytesIO();im.save(b,format='PNG',optimize=True);new=b.getvalue();assert len(new)<=n
 raw=raw[:pos]+struct.pack('<q',n)+new+bytes(n-len(new))+raw[pos+8+n:]
(P/'25-banc-casquette-poses-statiques.chara').write_bytes(raw)
print('Fiche, banques et sprite de banc prêts ; aucune copie installée.')
