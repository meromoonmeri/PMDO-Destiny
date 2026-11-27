#!/usr/bin/env python3
"""Construit une fiche EXPÉRIMENTALE seulement dans la copie Destiny de test.
Puissance fixe provisoire, aucune règle Z, ne pas distribuer comme implémentation finale.
"""
import json,copy,shutil
from pathlib import Path
root=Path(__file__).resolve().parent.parent
G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'
def read(n):return json.loads((G/'Data'/'Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
source=read('breakneck_blitz');giga=read('giga_impact')['Object'];flare=read('flare_blitz')['Object'];head=read('head_smash')['Object'];quick=read('quick_attack')['Object']
outdir=root/'Prototypes/Turbo-Charge-Bulldozer/V3-native';before=outdir/'breakneck_blitz-original.json'
if not before.exists():before.write_text(json.dumps(source,indent=2,ensure_ascii=False),encoding='utf-8')
a=source['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(giga['HitboxAction']);act['WideAngle']=0;act['Range']=2;act['StopAtHit']=True;act['StopAtWall']=True;act['Emitter']=copy.deepcopy(quick['HitboxAction']['Emitter'])
pre=copy.deepcopy(flare['HitboxAction']['PreActions'][0]);pre['Delay']=36;pre['Sound']='DUN_Move_Start'
for k,side in [('AnimBack','Arriere'),('AnimFront','Avant')]:pre['Emitter'][k]['Anim']['AnimIndex']='Turbo_V3_Charge_'+side
act['PreActions']=[pre];act['ActionFX']['Sound']='DUN_Giga_Impact';a['HitboxAction']=act
hit=copy.deepcopy(head['Data']['HitFX']);hit['Delay']=0;hit['Sound']='DUN_Hit_Neutral'
for k,side in [('AnimBack','Arriere'),('AnimFront','Avant')]:hit['Emitter'][k]['Anim']['AnimIndex']='Turbo_V3_Impact_'+side
a['Data']['HitFX']=hit
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
# BasePower 100 and category physical are placeholders; official Z strength depends on base move.
out=outdir/'breakneck_blitz-test-only.json';out.write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(out,G/'Data/Skill/breakneck_blitz.json')
for p in outdir.glob('Turbo_V3_*.dir'):shutil.copy2(p,G/'Content/Particle'/p.name)
print('Fiche et banques copiées exclusivement dans',G)
