#!/usr/bin/env python3
# Prototype de banc ; les sprites de rocher sont générés, les intermédiaires composés.
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Apocalypse-Gigalithique/Generation-PMDO';N=96

def cut(name):
 im=Image.open(P/name).convert('RGB').resize((64,64),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>120)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45)
 return Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA')
rock=cut('rocher-intact.png');broken=cut('rocher-fissure.png');frames=[]
def scene(y=None,stone=rock,radius=0,parts=None,alpha=255):
 im=Image.new('RGBA',(N,N));draw=ImageDraw.Draw(im);draw.ellipse((28,61,68,70),fill=(25,23,28,140))
 if radius:
  draw.ellipse((48-radius,65-radius//4,48+radius,65+radius//4),outline=(206,195,169,200),width=2)
 if y is not None:im.alpha_composite(stone,(16,y))
 if parts:
  for box,x,y2 in parts:
   chunk=broken.crop(box);chunk.putalpha(chunk.getchannel('A').point(lambda q:q*alpha//255));im.alpha_composite(chunk,(x,y2))
 return im
frames.append(scene());frames.append(scene(-54));frames.append(scene(-42));frames.append(scene(-28));frames.append(scene(-10));frames.append(scene(6));frames.extend([scene(8,radius=27),scene(8,radius=36),scene(8,broken,38),scene(8,broken,42)])
# Découpe en quartiers de la même roche fissurée : morceaux qui s'écartent puis disparaissent.
for k in range(6):
 dx=3*k;dy=2*k;parts=[((0,0,32,32),16-dx,8-dy),((32,0,64,32),48+dx,8-dy),((0,32,32,64),16-dx,40+dy),((32,32,64,64),48+dx,40+dy)]
 frames.append(scene(radius=max(0,40-4*k),parts=parts,alpha=max(0,255-k*45)))
frames.append(Image.new('RGBA',(N,N)))
name='Gigalithe_IA';sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(28,25,35,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0));f.save(P/f'frame-{i:02}.png')
check.convert('RGB').resize((N*len(frames)*2,N*2),Image.Resampling.NEAREST).save(P/'progression-controle.png');sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'continental_crush-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('continental_crush');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
act=copy.deepcopy(read('rock_slide')['Object']['HitboxAction']);act['Range']=2;act['HitTiles']=False;act['TargetAlignments']=4;act['LagBehindTime']=0;act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};act['ActionFX']['Sound']='DUN_Rock_Slide'
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=3;hit['Emitter']['LocHeight']=4;hit['Sound']='DUN_Rock_Smash';a['HitboxAction']=act;a['Data']['HitFX']=hit
text=json.dumps(z,indent=2,ensure_ascii=False);(P/'continental_crush-test-only.json').write_text(text);(G/'Data/Skill/continental_crush.json').write_text(text)
print(len(frames),'poses ; OffsetAction Sides centre à 2 cases')
