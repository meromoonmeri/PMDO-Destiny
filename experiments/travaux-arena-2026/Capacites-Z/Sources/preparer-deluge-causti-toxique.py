#!/usr/bin/env python3
"""Banc isolé Déluge Causti-Toxique : pluie et éclaboussures Poison."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil,random,math
H=Path('/home/user');R=H/'Capacites-Z';G=H/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Deluge-Causti-Toxique/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);res=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');return res.crop(res.getbbox())
def scale(i,w,h):return i.resize((max(1,w),max(1,h)),Image.Resampling.NEAREST)
def savebank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));preview=Image.new('RGBA',(N*len(frames),N),(30,27,35,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for i,f in enumerate(frames):preview.alpha_composite(f,(i*N,0))
 preview.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(p,G/'Content/Particle'/p.name)
drop=cut('source-goutte-acide.png',70);splash=cut('source-eclaboussure-acide.png',80);drop=scale(drop,17,29)
N=112;frames=[]
for t in range(40):
 im=Image.new('RGBA',(N,N));d=ImageDraw.Draw(im)
 # Une mare de poison grossit sous la cible, puis disparaît avec le déluge.
 if t>=7:
  op=min(150,(t-7)*28, max(0,(40-t)*20));rx=min(32,(t-7)*4);ry=max(1,rx//3)
  d.ellipse((56-rx,61-ry,56+rx,61+ry),fill=(92,16,146,op),outline=(201,57,232,op))
  for k in range(2):
   rr=rx-(k*6); yy=max(1,rr//3)
   if rr>4:d.arc((56-rr,61-yy,56+rr,61+yy),0,320,fill=(226,75,244,op),width=1)
 for j,(off,dx) in enumerate([(0,-8),(5,5),(10,0)]):
  q=t-off
  if 0<=q<9: im.alpha_composite(drop,(56+dx-8,-24+q*6))
  if 9<=q<23:
   k=q-9;w=[12,20,27,34,40,45,48,48,46,43,38,32,25,16][k];h=round(w*.70);sp=scale(splash,w,h);alpha=255 if k<8 else max(0,255-(k-7)*39);sp.putalpha(sp.getchannel('A').point(lambda a:a*alpha//255));im.alpha_composite(sp,(56+dx-w//2,57-h//2))
 if t>13:
  for k in range(5):
   x=56+int(24*math.sin(k*2.3));y=62-int((t*2+k*7)%24);a=min(170,(40-t)*14)
   if a>0:d.ellipse((x-1,y-1,x+1,y+1),fill=(233,129,246,a))
 frames.append(im)
savebank('DelugeToxique_Impact',frames,N)
# Overlay alpha animé à la manière d'une pluie diagonale traversant tout le cadre.
rng=random.Random(581);tex=Image.new('RGBA',(256,144));d=ImageDraw.Draw(tex)
for i in range(76):
 x=rng.randrange(256);y=rng.randrange(144);length=rng.randrange(3,9);c=rng.choice([(205,85,240,110),(156,56,198,100),(237,133,255,95)]);d.line((x,y,x-2,y+length),fill=c,width=1)
name='DelugeToxique_Pluie';tex.save(P/(name+'.png'));b=io.BytesIO();tex.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',256,144,0,1));shutil.copy2(p,G/'Content/BG'/p.name)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
original_path=P/'acid_downpour-original.json'
if original_path.exists(): original=json.loads(original_path.read_text())
else:
 original=read('acid_downpour');original_path.write_text(json.dumps(original,ensure_ascii=False,indent=2))
z=copy.deepcopy(original);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=85
ref=json.loads((R/'Prototypes/Impact-Choupinova/Generation-PMDO/twinkle_tackle-v2-test-only.json').read_text())['Object'];a['HitboxAction']=copy.deepcopy(ref['HitboxAction']);fx=a['HitboxAction']['ActionFX'];fx['Sound']='DUN_Gastro_Acid';em=fx['Emitter'];em['Anim']['AnimIndex']=name;em['Anim']['Alpha']=230;em['Movement']={'X':-50,'Y':290};em['TotalTime']=190;em['FadeIn']=12;em['FadeOut']=24;em['Layer']=4
hit=copy.deepcopy(ref['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='DelugeToxique_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Delay']=46;hit['Sound']='DUN_Sludge';a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'acid_downpour-test-only.json').write_text(s);(G/'Data/Skill/acid_downpour.json').write_text(s)
print('Pluie globale + impact : 40 poses, fiche de banc préparée')
