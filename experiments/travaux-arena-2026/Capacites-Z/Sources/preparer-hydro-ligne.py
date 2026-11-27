#!/usr/bin/env python3
# Essai de variante de Super Tourbillon en ligne traversante, inspirée Hydrocanon.
# Uniquement copie isolée ; pas un réglage Z définitif.
from pathlib import Path
import json,copy,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Super-Tourbillon-Abyssal/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
z=json.loads((P/'hydro_vortex-test-only.json').read_text());a=z['Object'];act=copy.deepcopy(read('hydro_pump')['Object']['HitboxAction']);act['Range']=4;act['StopAtHit']=False;act['StopAtWall']=True;act['TargetAlignments']=4;act['HitTiles']=False
# Impact IA déjà créé dans la version précédente ; jet et son de Hydrocanon natifs.
a['HitboxAction']=act;a['Data']['HitFX']['Sound']='DUN_Whirlpool'
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'hydro_vortex-ligne-test-only.json').write_text(s);(G/'Data/Skill/hydro_vortex.json').write_text(s);shutil.copy2(P/'Tourbillon_IA_Impact.dir',G/'Content/Particle/Tourbillon_IA_Impact.dir')
print('Hydro : Range=4, StopAtHit=False, StopAtWall=True, cible ennemi seulement.')
