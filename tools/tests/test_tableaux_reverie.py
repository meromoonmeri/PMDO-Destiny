#!/usr/bin/env python3
"""Tableaux et cycle de mission : contrôles et tests Lua quand disponibles."""
from pathlib import Path
import shutil,subprocess
R=Path(__file__).resolve().parents[2];root=R/'game/Data/Script/destiny';city=(root/'ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8');dev=(root/'ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');assert city==dev
for s in ["installer_une_porte(map, 'TableauReverieNord', 144, 400, 56, 48)","installer_une_porte(map, 'TableauReverieCentre', 400, 1512, 48, 56)","function ville.TableauReverieNord_Action",'missions_reverie.OuvrirTableau()',"mission.Etat == 'en_cours' then dests[mission.Zone] = true"]:assert s in city,s
m=(root/'missions_reverie.lua').read_text(encoding='utf8');z=(root/'zone/lost_wood/init.lua').read_text(encoding='utf8')
for s in ['function missions.Jour()', 'function missions.Accepter()', 'function missions.Completer(zone, reussi)', 'function missions.Reclamer()', 'function missions.LireGazette()', 'GAME:AddToPlayerMoneyBank(RECOMPENSE)', "GAME:DungeonUnlocked('lost_wood')", 'destiny().MissionReverie']:assert s in m,s
assert "missions_reverie.Completer('lost_wood', result == RogueEssence.Data.GameProgress.ResultType.Cleared)" in z
lua=shutil.which('lua5.4')
if lua:
 for test in ['test_tableaux_reverie.lua','test_e2_reverie.lua']:subprocess.run([lua,str(R/'tools/tests'/test),str(R)],check=True)
else:print('Lua 5.4 absent : tests comportementaux ignorés sur cet hôte.')
print('Tableaux et mission quotidienne : vérifications structurelles OK ; test en jeu nécessaire.')
