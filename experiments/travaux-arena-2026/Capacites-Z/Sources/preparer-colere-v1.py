#!/usr/bin/env python3
"""Prépare les banques et la fiche jetable Colère du Gardien d'Alola."""
from pathlib import Path
from PIL import Image
import json,struct,io
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Colere-du-Gardien-d-Alola/Generation-PMDO'
for src,name in [('Colere_Lances_Arriere.dir','ColereV1_Arriere.dir'),('Colere_Lances_Explosion_Avant.dir','ColereV1_Avant.dir')]:
 b=(P/src).read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,n=struct.unpack_from('<iiii',b,8+k);assert n==180
 out=Image.new('RGBA',(w*60,h*8))
 for i in range(60):
  frame=im.crop((w*i*3,0,w*(i*3+1),h))
  for d in range(8):out.alpha_composite(frame,(w*i,h*d))
 z=io.BytesIO();out.save(z,format='PNG',optimize=True);raw=z.getvalue();(P/name).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4,60))
a=json.loads((G/'Data/Skill/guardian_of_alola.json').read_text(encoding='utf-8-sig'));o=a['Object'];o['Released']=True;o['Data']['SkillStates']=[]
o['Data']['OnHits']=[{'Key':{'str':[-1]},'Value':{'$type':'PMDC.Dungeon.CutHPDamageEvent, PMDC','HPFraction':4}}]
o['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'ColereV1_Charge','ArgTable':'{}'}}]
(P/'guardian_of_alola-v1-test-only.json').write_text(json.dumps(a,indent=2,ensure_ascii=False))
print('Banques 60 poses et fiche native 3/4 produites.')
