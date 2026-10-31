#!/usr/bin/env python3
"""Vérifie les raccordements de Lost Wood et les ressources de la statue."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
zone = json.loads((GAME / 'Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))['Object']
floors = zone['Segments'][0]['Floors']
assert len(floors) == 7
for n, floor in enumerate(floors, 1):
    assert floor['$type'].startswith('RogueEssence.LevelGen.GridFloorGen')
    steps = floor['GenSteps']
    data = [s['Value'] for s in steps if s['Value']['$type'].startswith('PMDC.LevelGen.MapDataStep')]
    assert len(data) == 1 and data[0]['Music'] == 'Tiny Woods.ogg', n
    events = [s['Value'] for s in steps if s['Value']['$type'].startswith('RogueEssence.LevelGen.MapEffectStep')]
    assert len(events) == 1 and 'MapGenContext' in events[0]['$type'], n
    starts = events[0]['Effect']['OnMapStarts']
    assert len(starts) == 1 and starts[0]['Value']['Script'] == 'DestinyLostWoodLesson'
    assert starts[0]['Value']['ArgTable'] == '{ Etage = %d }' % n
    assert all(not v for k, v in events[0]['Effect'].items() if k != 'OnMapStarts')

song = (GAME / 'Content/Music/Tiny Woods.ogg').read_bytes()
assert song.startswith(b'OggS') and b'vorbis' in song
assert b'LOOPSTART=176400' in song and b'LOOPLENGTH=1882031' in song
binary = (GAME / 'Content/Object/Statue_Kangourex.dir').read_bytes()
length = struct.unpack_from('<q', binary)[0]
assert binary[8:16] == b'\x89PNG\r\n\x1a\n'
assert struct.unpack_from('<iiii', binary, 8 + length) == (32, 32, 0, 1)
assert len(binary) == 8 + length + 16
assert "require 'destiny.services.statue_kangourex'" in (GAME / 'Data/Script/destiny/main.lua').read_text(encoding='utf-8')
event = (GAME / 'Data/Script/destiny/event.lua').read_text(encoding='utf-8')
assert "require 'destiny.event_battle'" in event  # garder les événements préexistants
assert 'function SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson' in event
assert 'BATTLE_SCRIPT = {}' not in event and 'SINGLE_CHAR_SCRIPT = {}' not in event
scene = (GAME / 'Data/Script/destiny/ground/cliffdaytest_nuit/init.lua').read_text(encoding='utf-8')
assert 'SOUND:PlayBGM' not in scene
assert 'GROUND:MoveToPosition(partenaire' in scene
assert 'Pichu_Home_Door' in scene and 'Pichu_Crossroads' in scene
assert 'LostWoodTutorialDone' not in scene
quiz = (GAME / 'Data/Script/destiny/ground/personality_test/init.lua').read_text(encoding='utf-8')
assert quiz.index('SOUND:FadeOutBGM(60)') < quiz.index("Une faille s'ouvre dans le rêve")
print('OK : 7 étages, 7 événements compatibles, boucle Vorbis, objet .dir et transition.')
