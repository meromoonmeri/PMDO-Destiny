#!/usr/bin/env python3
# Cocon Fatal, uniquement dans la copie de banc PMDO.
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Cocon-Fatal/Generation-PMDO';N=80

def cut(filename, box, width=56,height=64):
 im=Image.open(P/filename).convert('RGB')
 if box: im=im.crop(box)
 im=im.resize((width,height),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>120)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45)
 return Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA')
# Même dimension, en conservant les pixels de la pose générée originale.
thread=cut('pose-fils-initiale.png',None,56,58);cocoon=cut('pose-cocon-ferme.png',(0,0,336,384),56,64);crack=cut('pose-cocon-fissure.png',None,56,64);burst=cut('pose-cocon-rupture.png',None,56,64)
def canvas(img, x=12,y=4):
 out=Image.new('RGBA',(N,N));out.alpha_composite(img,(x,y));return out
thread=canvas(thread,12,10);cocoon=canvas(cocoon,12,4);crack=canvas(crack,12,4);burst=canvas(burst,12,4)
frames=[]
# Écheveaux se nouant, puis bandes du cocon qui se tissent de bas en haut.
for height in (17,32,48,64):
 f=Image.new('RGBA',(N,N));portion=thread.copy();portion.paste((0,0,0,0),(0,0,N,max(0,72-height)));f.alpha_composite(portion);frames.append(f)
for height in (15,30,45,64):
 f=thread.copy();part=cocoon.copy();part.paste((0,0,0,0),(0,0,N,max(0,68-height)));f.alpha_composite(part);frames.append(f)
frames.extend([cocoon,cocoon,crack,crack,burst,burst])
# Libération : les deux moitiés s'écartent puis s'estompent.
for dx,alpha in [(3,210),(7,145),(11,70)]:
 f=Image.new('RGBA',(N,N));a=burst.getchannel('A').point(lambda q:q*alpha//255);b=burst.copy();b.putalpha(a);f.alpha_composite(b.crop((0,0,40,80)),(-dx,0));f.alpha_composite(b.crop((40,0,80,80)),(40+dx,0));frames.append(f)
name='Cocon_Fatal_IA';sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(28,25,35,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0));f.save(P/f'frame-{i:02}.png')
check.convert('RGB').resize((N*len(frames)*2,N*2),Image.Resampling.NEAREST).save(P/'progression-controle.png');sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'savage_spin_out-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('savage_spin_out');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
act=copy.deepcopy(read('twister')['Object']['HitboxAction']);act['HitArea']=0;act['Range']=2;act['Speed']=0;act['HitTiles']=False;act['TargetAlignments']=4;act['Emitter']={'$type':'RogueEssence.Content.EmptyCircleSquareEmitter, RogueEssence','LocHeight':0};act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};act['ActionFX']['Sound']='DUN_String_Shot'
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=4;hit['Emitter']['LocHeight']=4;hit['Sound']='DUN_String_Shot_2';a['HitboxAction']=act;a['Data']['HitFX']=hit
text=json.dumps(z,indent=2,ensure_ascii=False);(P/'savage_spin_out-test-only.json').write_text(text);(G/'Data/Skill/savage_spin_out.json').write_text(text)
print(len(frames),'poses ; OffsetAction Tile distance 2')
