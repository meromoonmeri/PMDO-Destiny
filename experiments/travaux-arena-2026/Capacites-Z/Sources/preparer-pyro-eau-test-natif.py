#!/usr/bin/env python3
"""Génère deux fiches d'essai à puissance fixe. UNIQUEMENT copie locale jetable."""
from pathlib import Path
import copy,json,shutil
R=Path(__file__).resolve().parent.parent;G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'
def read(name):return json.loads((G/'Data/Skill'/f'{name}.json').read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
shadow=read('shadow_ball')['Object'];fire=read('fire_blast')['Object'];water=read('water_pulse')['Object'];head=read('head_smash')['Object']
for name,folder in [('inferno_overdrive','Pyro-Explosion-Cataclysmique'),('hydro_vortex','Super-Tourbillon-Abyssal')]:
 p=R/'Prototypes'/folder/'V2-PMDO';backup=p/(name+'-original.json')
 if backup.exists():orig=json.loads(backup.read_text(encoding='utf-8'))
 else:orig=read(name);dump(backup,orig)
 obj=copy.deepcopy(orig);a=obj['Object'];a['Released']=True;a['BaseCharges']=1
 for st in a['Data']['SkillStates']:
  if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=100
 a['Data']['Category']=2
 if name=='inferno_overdrive':
  act=copy.deepcopy(shadow['HitboxAction']);act['Anim']['AnimIndex']='Pyro_PMDO_Projectile';act['Anim']['FrameTime']=3;act['Range']=4;act['Speed']=10;act['StopAtWall']=True;act['StopAtHit']=True;act['TargetAlignments']=4;act['HitTiles']=False;act['ActionFX']['Sound']='DUN_Fire_Blast'
  hit=copy.deepcopy(fire['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='Pyro_PMDO_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Emitter']['LocHeight']=8;hit['Sound']='DUN_Blast_Burn'
 else:
  act=copy.deepcopy(water['HitboxAction']);act['Range']=4;act['StopAtHit']=True;act['StopAtWall']=True;act['HitTiles']=False;act['TargetAlignments']=4;act['ActionFX']['Sound']='DUN_Water_Gun_3'
  hit=copy.deepcopy(head['Data']['HitFX']);hit['Delay']=0;hit['Sound']='DUN_Whirlpool'
  for k,side in [('AnimBack','Arriere'),('AnimFront','Avant')]:hit['Emitter'][k]['Anim']['AnimIndex']='Tourbillon_PMDO_'+side
 a['HitboxAction']=act;a['Data']['HitFX']=hit
 dump(p/(name+'-test-only.json'),obj);dump(G/'Data/Skill'/f'{name}.json',obj)
 for f in p.glob('*.dir'):shutil.copy2(f,G/'Content/Particle'/f.name)
 print(name,'préparé en copie, source conservée')
