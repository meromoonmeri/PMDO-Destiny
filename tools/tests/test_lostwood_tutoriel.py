#!/usr/bin/env python3
"""Vérifie les raccordements de Lost Wood et les ressources de la statue."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
zone = json.loads((GAME / 'Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))['Object']
segments = zone['Segments']
assert len(segments) == 2
floors = segments[0]['Floors']
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

# Le segment 1 est le chemin du retour : mêmes générateurs, ordre inverse.
reverse_floors = segments[1]['Floors']
assert len(reverse_floors) == 7
for n, floor in enumerate(reverse_floors, 1):
    events = [s['Value'] for s in floor['GenSteps']
              if s['Value']['$type'].startswith('RogueEssence.LevelGen.MapEffectStep')]
    starts = events[0]['Effect']['OnMapStarts']
    assert starts[0]['Value']['ArgTable'] == '{ Etage = %d }' % (8 - n)

# Convention PMDO : l'aller monte en 1F→7F avec stairs_go_up,
# le retour descend en étages négatifs B1F→B7F avec stairs_go_down.
def _find_steps(node, needle):
    found = []
    if isinstance(node, dict):
        if needle in node.get('$type', ''):
            found.append(node)
        for value in node.values():
            found.extend(_find_steps(value, needle))
    elif isinstance(node, list):
        for value in node:
            found.extend(_find_steps(value, needle))
    return found

def _count_strings(node, expected):
    if node == expected:
        return 1
    if isinstance(node, dict):
        return sum(_count_strings(value, expected) for value in node.values())
    if isinstance(node, list):
        return sum(_count_strings(value, expected) for value in node)
    return 0

floor_names = []
for segment in segments:
    name_steps = _find_steps(segment['ZoneSteps'], 'FloorNameDropZoneStep')
    assert len(name_steps) == 1
    floor_names.append(name_steps[0]['Name']['DefaultText'])
assert floor_names == ['Lost Wood\n{0}F', 'Lost Wood\nB{0}F']
for segment, expected_stairs in ((segments[0], 'stairs_go_up'), (segments[1], 'stairs_go_down')):
    stairs_steps = _find_steps(segment['Floors'], 'FloorStairsStep')
    assert len(stairs_steps) == 7
    assert [step['Exits'][0]['Tile']['ID'] for step in stairs_steps] == [expected_stairs] * 7
assert _count_strings(segments[0]['Floors'], 'stairs_secret_up') == 2
assert _count_strings(segments[1]['Floors'], 'stairs_secret_down') == 2
assert _count_strings(segments[1]['Floors'], 'stairs_secret_up') == 0

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
assert 'Dazzling_Exit_East' in scene and 'chemin de l’est' in scene
assert 'LostWoodTutorialDone' not in scene
quiz = (GAME / 'Data/Script/destiny/ground/personality_test/init.lua').read_text(encoding='utf-8')
assert quiz.index('SOUND:FadeOutBGM(60)') < quiz.index("Une faille s'ouvre dans le rêve")
assert "PrologueHeros = 'a_voir'" in quiz
assert "EnterGroundMap('reverie', 'zrv2_zone_reveil_nuit', 'reveil')" in quiz
reverie = json.loads((GAME / 'Data/Zone/reverie.json').read_text(encoding='utf-8-sig'))['Object']
assert reverie['GroundMaps'][10] == 'zrv2_zone_reveil_nuit'
reveil = (GAME / 'Data/Script/destiny/ground/reveil_nuit/init.lua').read_text(encoding='utf-8')
for phrase in ('Où suis-je…', 'Qui suis-je…', 'Tout me semble si flou…', 'J’ai sommeil…'):
    assert phrase in reveil
assert "MRKR('reveil')" in reveil and "MRKR('entrance')" in reveil
assert 'points_scene()' in reveil and 'dans les fleurs' in reveil
# Viewport 320×240 : ouverture Y=136 et panorama Y=152 pour garder lune,
# sommet et mer dans le cadre, avec des travelings rejoints explicitement.
assert 'camera_ouverture_y = point_reveil.Position.Y - 104' in reveil
assert 'camera_panorama_y = point_reveil.Position.Y - 88' in reveil
assert 'camera_approche_y = point_reveil.Position.Y + 48' in reveil
assert 'TASK:BranchCoroutine' in reveil and 'TASK:JoinCoroutines' in reveil
assert reveil.count('lancer_camera(') >= 8 and 'attendre_camera(travelling_final)' in reveil
zrv2_script = (GAME / 'Data/Script/destiny/ground/zrv2_zone_reveil_nuit/init.lua').read_text(encoding='utf-8')
assert "require 'destiny.ground.reveil_nuit.init'" in zrv2_script
assert "EnterDungeon('lost_wood', 1, 0, 0" in reveil
zone_script = (GAME / 'Data/Script/destiny/zone/lost_wood/init.lua').read_text(encoding='utf-8')
assert 'segmentID == 1' in zone_script
assert zone_script.count("GAME:EnterZone('reverie', -1, 10, 0)") == 2
assert "GAME:EnterZone('destiny_cliff_tests', -1, 0, 0)" in zone_script
cliff_jour = (GAME / 'Data/Script/destiny/ground/cliffdaytest/init.lua').read_text(encoding='utf-8')
assert 'SceneArriveeDestiny' in cliff_jour
assert 'tatie Kangourex' in cliff_jour and 'guildes' in cliff_jour
assert 'RencontreTeamDazzling' in cliff_jour and 'Sparkle_RSE' in cliff_jour
assert 'meneuse de la' in cliff_jour and 'saluer l’affiche' in cliff_jour
assert 'héros muet' in cliff_jour and 'TeamDazzlingRencontree' in cliff_jour
assert "CH('Pichu')" not in cliff_jour and 'PichuDazzling' not in cliff_jour
assert 'GarderCheminSud' in scene
assert 'Je ne vais pas me dégonfler' in scene and 'Il faut que je sois courageux' in scene
for ground_name in ('cliffdaytest', 'cliffdaytest_nuit'):
    ground = json.loads((GAME / f'Data/Ground/{ground_name}.rsground').read_text(encoding='utf-8-sig'))['Object']
    entities = ground['Entities'][0]
    assert ground['Music'] == 'Cliff Camp.ogg'
    assert entities['MapChars'] == []
    assert [(s['EntName'], s['NPCChar']['BaseForm']['Species']) for s in entities['Spawners']] == [
        ('Adagio', 'tsareena'), ('Sonata', 'lopunny'), ('Aria', 'mawile')]
mer = (GAME / 'Content/Sound/Battle/Destiny_Falaise_Mer.ogg').read_bytes()
assert mer.startswith(b'OggS') and b'vorbis' in mer
assert "parler(hero" not in (GAME / 'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf-8')
print('OK : prologue, aller, retour inverse 7→1, arrivée au jour, Team Dazzling, tutoriel et statue.')
