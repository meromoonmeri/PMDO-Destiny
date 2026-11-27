#!/usr/bin/env python3
"""Prototype Psycho-Pulvérisation EX, installation temporaire dans la copie PMDO."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil,random,math
H=Path('/home/user');R=H/'Capacites-Z';G=H/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Psycho-Pulverisation-EX/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);v=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');return v.crop(v.getbbox())
def scale(im,w,h):return im.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.NEAREST)
def paste(im,p,w,h,x,y,a=255):
 if a<=0 or w<=0 or h<=0:return
 s=scale(p,w,h);s.putalpha(s.getchannel('A').point(lambda v:v*a//255));im.alpha_composite(s,(round(x-w/2),round(y-h/2)))
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(28,25,35,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for i,f in enumerate(frames):control.alpha_composite(f,(i*N,0))
 control.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(p,G/'Content/Particle'/p.name)
ring=cut('source-anneau-psy.png',90);burst=cut('source-impact-psy.png',80)
# Concentration au lancement : couronne elliptique derrière le lanceur.
N=96;frames=[]
for t in range(22):
 im=Image.new('RGBA',(N,N));k=min(1,(t+1)/5)*min(1,(22-t)/5);w=48+int(5*math.sin(t*.4));paste(im,ring,w,round(w*.55),48,58,int(210*k));d=ImageDraw.Draw(im)
 for j in range(5):
  x=int(48+27*math.cos(j*math.tau/5+t*.24));y=int(54+14*math.sin(j*math.tau/5+t*.24));a=int(210*k);d.line((x-2,y,x+2,y),fill=(242,144,255,a));d.line((x,y-2,x,y+2),fill=(242,144,255,a))
 frames.append(im)
bank('PsychoEXV2_Concentration',frames,N)
# Déformation suggérée : maillage spatio-psychique qui se tord autour de la cible.
# Il s'agit d'une superposition animée, sans déformation des pixels du décor par shader.
N=112;frames=[]
for t in range(48):
 im=Image.new('RGBA',(N,N));d=ImageDraw.Draw(im)
 if t<30:
  fade=min(1,(t+1)/4)*min(1,(30-t)/5);phase=t*.34;strength=fade*(.55+.45*math.sin(t*.23)**2)
  # lignes parallèles fléchies et tordues, comme une lentille spatio-temporelle
  def warp(x,y):
   r=math.sqrt(x*x+y*y); influence=math.exp(-(r/29)**2);a=1.15*strength*influence*math.sin(phase+r*.11); sc=1+.35*strength*influence*math.cos(phase+r*.15)
   return (56+(x*math.cos(a)-y*math.sin(a))*sc,56+(x*math.sin(a)+y*math.cos(a))*sc)
  for axis in (0,1):
   for v in (-36,-24,-12,0,12,24,36):
    pts=[]
    for u in range(-44,45,2):pts.append(warp(u,v) if axis==0 else warp(v,u))
    d.line(pts,fill=(211,133,255,int(85*fade)),width=1)
  # des ondulations non circulaires se contractent autour de la cible
  for j in range(3):
   pts=[];rr=14+j*9+4*math.sin(phase+j*.9)
   for h in range(49):
    ang=h*math.tau/48;rad=rr*(1+.13*math.sin(ang*3+phase));pts.append((56+rad*math.cos(ang),56+rad*.72*math.sin(ang)))
   d.line(pts,fill=(250,153,255,int((150-j*20)*fade)),width=1)
  if 8<t<28:paste(im,ring,30+5*math.sin(phase),25+3*math.cos(phase),56,56,int(85*fade))
 if 27<=t<43:
  k=t-27;size=[8,15,25,35,44,52,58,60,58,54,49,43,37,30,23,14][k];alpha=240 if k<7 else max(0,240-(k-6)*25);paste(im,burst,size,size,56,56,alpha);d=ImageDraw.Draw(im)
  for j in range(7):
   angle=j*math.tau/7+.22;rad=5+k*2;x=round(56+rad*math.cos(angle));y=round(56+rad*math.sin(angle));d.polygon([(x,y-3),(x+2,y),(x,y+3),(x-2,y)],fill=(238,123,255,alpha))
 frames.append(im)
bank('PsychoEXV2_Impact',frames,N)
# Quelques fragments roses dans un voile global transparent qui glisse doucement.
rng=random.Random(921);tex=Image.new('RGBA',(256,144));d=ImageDraw.Draw(tex)
for i in range(30):
 x=rng.randrange(4,252);y=rng.randrange(4,140);sz=rng.choice([1,2,3]);c=rng.choice([(214,92,255,105),(245,142,255,110),(139,99,255,95)]);d.polygon([(x,y-sz*2),(x+sz,y),(x,y+sz*2),(x-sz,y)],fill=c)
name='PsychoEXV2_Fragment';tex.save(P/(name+'.png'));b=io.BytesIO();tex.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',256,144,0,1));shutil.copy2(p,G/'Content/BG'/p.name)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=P/'shattered_psyche-original.json'
if orig.exists():o=json.loads(orig.read_text())
else:o=read('shattered_psyche');orig.write_text(json.dumps(o,ensure_ascii=False,indent=2))
z=copy.deepcopy(o);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=85
ref=json.loads((R/'Prototypes/Impact-Choupinova/Generation-PMDO/twinkle_tackle-v2-test-only.json').read_text())['Object'];a['HitboxAction']=copy.deepcopy(ref['HitboxAction']);fx=a['HitboxAction']['ActionFX'];fx['Sound']='DUN_Psybeam';em=fx['Emitter'];em['Anim']['AnimIndex']=name;em['Anim']['Alpha']=200;em['Movement']={'X':42,'Y':-18};em['TotalTime']=180;em['FadeIn']=12;em['FadeOut']=24;em['Layer']=4
hit=copy.deepcopy(ref['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='PsychoEXV2_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Delay']=70;hit['Sound']='DUN_Psycho_Boost';a['Data']['HitFX']=hit
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'PsychoEXV2_Concentration','ArgTable':'{}'}}]
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'shattered_psyche-v2-test-only.json').write_text(s);(G/'Data/Skill/shattered_psyche.json').write_text(s)
e=G/'Data/Script/origin/event_battle.lua';bak=H/'.cache/destiny-test/event-battle-avant-psycho-ex-v2.lua'
if not bak.exists():shutil.copy2(e,bak)
shutil.copy2(bak,e)
with e.open('a') as f:f.write('\n'+(R/'Sources/psycho-ex-v2-concentration.lua').read_text())
print('Concentration, fragments globaux, contraction et éclats ; fiche expérimentale')
