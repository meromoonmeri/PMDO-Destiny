#!/usr/bin/env python3
"""Dracacophonie : écailles animées, ondes natives et fiche de banc."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Dracacophonie-Flamboyante/Generation-PMDO';N=96;T=72
im=np.asarray(Image.open(P/'source-eclat-dragon-pmd.png').convert('RGB'));r,g,b=[im[:,:,i].astype('int16') for i in range(3)];mask=(g>55)&(g>r*1.20)&(g>b*1.20);scale=Image.fromarray(np.dstack((im,(~mask).astype('uint8')*255)),'RGBA');scale=scale.crop(scale.getbbox()).resize((10,14),Image.Resampling.NEAREST)
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,k+8);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
wave=native('Wave_Circle_Blue');dragon=native('Dragon_Pulse_Particle_Purple')
def paste(f,v,x,y,alpha=1):
 v=v.copy()
 if alpha<1:v.putalpha(v.getchannel('A').point(lambda q:round(q*max(0,alpha))))
 f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));end=min(1,(T-t)/9)
 for j in range(3):
  age=t-j*12
  if 0<=age<33:
   v=wave[min(10,age//3)].resize((42,42),Image.Resampling.NEAREST);paste(f,v,48,48,min(1,age/4,(33-age)/6)*end)
 for j in range(8):
  age=t-j*3
  if 0<=age<54:
   angle=j*math.tau/8+age*.08;radius=12+age*.48;x=48+math.cos(angle)*radius;y=48+math.sin(angle)*radius*.7
   fade=min(1,age/5,(54-age)/9)*end;v=scale.rotate(-math.degrees(angle),Image.Resampling.NEAREST,expand=True);paste(f,v,x,y,fade)
   if 12<=age<36:paste(f,dragon[(age//3+j)%len(dragon)].resize((8,8),Image.Resampling.NEAREST),x+5,y+3,fade)
 frames.append(f)
sheet=Image.new('RGBA',(N*8,N*9));bank=Image.new('RGBA',(N*T,N*8))
for i,f in enumerate(frames):
 sheet.alpha_composite(f,((i%8)*N,(i//8)*N))
 for j in range(8):bank.alpha_composite(f,(N*i,N*j))
sheet.save(P/'Dracaco-charge-72images.png',optimize=True);b=io.BytesIO();bank.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/'Dracaco_Charge.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T))
z=json.loads((P/'clangorous_soulblaze-ebauche-pmd-non-testee.json').read_text());a=z['Object'];a['HitboxAction']['HitArea']=0
# Les ondes natives de Vibrécaille, sans baisse de Défense. La banque complémentaire est renommée.
a['HitboxAction']['Emitter']['Emitters'][1]['Anims'][0]['Anim']['AnimIndex']='Dracaco_Onde'
a['Explosion']['TargetAlignments']=4
def event(name,priority=0):return {'Key':{'str':[priority]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':name,'ArgTable':'{}'}}
a['Data']['BeforeActions']=[event('Dracaco_Charge')];a['Data']['BeforeHits']=[event('Dracaco_Avant',-20)];a['Data']['OnHits'].append(event('Dracaco_Apres',1))
# Événements natifs Pierre Antique, appliqués une seule fois sous condition.
anc=json.loads((G/'Data/Skill/ancient_power.json').read_text(encoding='utf-8-sig'))['Object'];ev=copy.deepcopy(anc['Data']['AfterActions'][0]['Value']['BaseEvents'][0]['BaseEvents'])
a['Data']['AfterActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.ScriptedConditionEvent, RogueEssence','Script':'Dracaco_BonusSiTouche','ArgTable':'{}','BaseEvents':ev}}]
(P/'clangorous_soulblaze-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));(P/'Dracaco_Onde.dir').write_bytes((P/'Dracaco_Onde_IA.dir').read_bytes());print('72 images et fiche de banc conditionnelle créées.')
