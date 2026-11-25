#!/usr/bin/env python3
"""Protection des anciens indices après retrait des intérieurs de guilde."""
from pathlib import Path
import json,subprocess,shutil
R=Path(__file__).resolve().parents[2];game=R/'game';zone=json.loads((game/'Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf8'))['Object']['GroundMaps'];assert zone[13:15]==['guild_storage_room','guild_heros_room'] and zone[15:19]==['ledian_dojo','dojo_ossatueur','dojo_kingambit','reverie_hutte_aquatique']
for nom in ['guild_heros_room','guild_storage_room']:
 g=json.loads((game/'Data/Ground'/f'{nom}.rsground').read_text(encoding='utf-8-sig'))['Object'];assert g['AssetName']==nom and len(g['Layers'])==1 and len(g['Layers'][0]['Tiles'])==44 and all(len(c)==44 for c in g['Layers'][0]['Tiles']);assert not g['Decorations'] and not g['Entities'][0]['MapChars'] and not g['Entities'][0]['GroundObjects'];assert all(not t['Layers'] for col in g['Layers'][0]['Tiles'] for t in col);assert any(m['EntName']=='Main_Entrance_Marker' for m in g['Entities'][0]['Markers'])
 s=(game/'Data/Script/destiny/ground'/nom/'init.lua').read_text(encoding='utf8');assert f'function {nom}.Enter(map) sortir() end' in s and f'function {nom}.GameLoad(map) sortir() end' in s and "GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)" in s
for mask in ['Guild_Heros_Room_*.tile','Guild_Storage_Room_*.tile']:assert not list((game/'Content/Tile').glob(mask)),mask
assert (game/'Content/Tile/Guild_First_Floor.tile').is_file()
lua=shutil.which('lua5.4')
if lua:subprocess.run([lua,str(R/'tools/tests/test_retrait_guilde.lua'),str(R)],check=True)
else:print('Lua 5.4 absent : test de logique Lua ignoré sur cet hôte.')
print('Intérieurs retirés ; indices et récupération technique présents (sauvegardes réelles à tester).')
