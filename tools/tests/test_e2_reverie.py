#!/usr/bin/env python3
"""Contrôle la sortie E2 ; tests comportementaux Lua si Lua 5.4 est disponible."""
from pathlib import Path
import json,subprocess,shutil
R=Path(__file__).resolve().parents[2];game=R/'game';city=(game/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8');dev=(game/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');z=(game/'Data/Script/destiny/zone/lost_wood/init.lua').read_text(encoding='utf8');assert city==dev
for snippet in ["sortie.EntName = 'SortieExplorationE2'",'RogueElements.Rect(1584, 1584, 16, 32)',"destinations_reverie = {'lost_wood'}",'GAME:DungeonUnlocked(id)','SV.Destiny.RetourAccompli',"STRINGS:Format('\\\\uE111 ')","STRINGS:Format('\\\\uE10F ')",'SV.Destiny.ExplorationReverie = true','GAME:EnterDungeon(destination.Id, 0, 0, 0']:
 assert snippet in city,snippet
assert 'SortieExplorationE1' not in city
for snippet in ['if SV.Destiny.ExplorationReverie then',"SV.Destiny.ArriveeVille = 'batiment'",'SV.Destiny.RetourBatimentX = 1552','SV.Destiny.RetourBatimentY = 1600',"terminer(result, 'town02_waterfallvillage', 0)","GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)","SV.Destiny.LostWoodTrip = 'rencontre'","SV.Destiny.LostWoodTrip = 'termine'"]:
 assert snippet in z,snippet
index=json.loads((game/'Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object'];assert index['lost_wood']['Released'] and index['lost_wood']['CountedFloors']>0
lua=shutil.which('lua5.4')
if lua:subprocess.run([lua,str(R/'tools/tests/test_e2_reverie.lua'),str(R)],check=True)
else:print('Lua 5.4 absent : tests de logique Lua ignorés sur cet hôte.')
print('Sortie E2 : structure, indicateurs et retour vérifiés ; test en jeu nécessaire.')
