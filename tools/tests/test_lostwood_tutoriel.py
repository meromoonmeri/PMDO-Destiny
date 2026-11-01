#!/usr/bin/env python3
"""Vérifie les raccordements de Lost Wood, le prologue et les ressources de la statue."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
zone = json.loads((GAME / 'Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))['Object']
assert zone['Level'] <= 5
team_step = next(z for z in zone['Segments'][0]['ZoneSteps'] if 'TeamSpawnZoneStep' in z['$type'])
for entry in team_step['Spawns']:
    sp = entry['Spawn']['Spawn']
    assert sp['Level']['Max'] <= 4, sp
    assert sp['Intrinsic'] not in ('poison_point', 'effect_spore', ''), sp
    for bad_skill in ('poison_sting', 'stun_spore', 'supersonic', 'comet_punch', 'leech_seed'):
        assert bad_skill not in sp['SpecifiedSkills'], sp

floors = zone['Segments'][0]['Floors']
assert len(floors) == 7
for n, floor in enumerate(floors, 1):
    assert floor['$type'].startswith('RogueEssence.LevelGen.GridFloorGen')
    steps = floor['GenSteps']
    data = [s['Value'] for s in steps if s['Value']['$type'].startswith('PMDC.LevelGen.MapDataStep')]
    assert len(data) == 1 and data[0]['Music'] == 'Tiny Woods.ogg', n
    mobs = [s['Value'] for s in steps if 'PlaceRandomMobsStep' in s['Value']['$type'] and s['Value'].get('Ally') is False]
    assert len(mobs) == 1 and mobs[0]['Spawn']['Amount']['Max'] <= 3, n
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
assert 'function DestinyInverserEscaliersLostWood' in event
assert 'BATTLE_SCRIPT = {}' not in event and 'SINGLE_CHAR_SCRIPT = {}' not in event
assert 'SetSpeaker(' not in event and 'UI:ResetSpeaker()' in event
assert "PlayFanfare('Fanfare/Note')" in event and 'LocalKeyString' in event
assert "'stairs_back_up'" in event and 'SegLoc(0, -1)' in event

quiz = (GAME / 'Data/Script/destiny/ground/personality_test/init.lua').read_text(encoding='utf-8')
assert quiz.index('SOUND:FadeOutBGM(60)') < quiz.index("Une faille s'ouvre dans le rêve")
assert "'zrv2_zone_reveil_nuit'" in quiz
# Quiz PMD : 20 questions sans compteur affiché, révélation par l'étoile
assert '/15)' not in quiz and '/20)' not in quiz and "num .. '/" not in quiz
assert "require 'destiny.ground.personality_test.revelation_etoile'" in quiz
assert 'revelation_etoile.derouler' in quiz
donnees_quiz = (GAME / 'Data/Script/destiny/ground/personality_test/quiz_data.lua').read_text(encoding='utf-8')
assert donnees_quiz.count('texte = "') >= 20  # questions + choix
assert 'couleurs_types' in donnees_quiz
# Les sprites de l'étoile forgée existent bien dans le contenu du jeu
etoiles = sorted((GAME / 'Content/BG').glob('quiz_star_*.dir'))
assert len(etoiles) >= 22, etoiles

reveil = (GAME / 'Data/Script/destiny/ground/zrv2_zone_reveil_nuit/init.lua').read_text(encoding='utf-8')
for extrait in (
    "… Où suis-je… ?",
    "Qui suis-je… ?",
    "Tout me semble si flou…",
    "J'ai sommeil…",
    "NameMenu",
    "joli prénom",
    "équipe d'explorateurs",
    "J'ai des projets haha… ouais t'en fais pas !",
    "capitale des explorateurs",
    "nouvelle histoire commença",
):
    assert extrait in reveil, extrait
assert "EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Home_Door')" in reveil
assert "EnterDungeon('lost_wood', 0, 6, 0" in reveil

scene_nuit = (GAME / 'Data/Script/destiny/ground/cliffdaytest_nuit/init.lua').read_text(encoding='utf-8')
assert 'SOUND:PlayBGM' not in scene_nuit
assert 'GROUND:MoveToPosition(partenaire' in scene_nuit
assert 'Pichu_Home_Door' in scene_nuit and 'Dazzling_Exit_East' in scene_nuit
assert 'Pichu_Crossroads' not in scene_nuit
assert 'LostWoodTutorialDone' not in scene_nuit

scene_jour = (GAME / 'Data/Script/destiny/ground/cliffdaytest/init.lua').read_text(encoding='utf-8')
for sujet in ('orphelin', 'orpheline', 'Tatie Kangourex', 'Réverie Town', 'équipes de secours', "équipes d'explorateurs", 'Guildes'):
    assert sujet in scene_jour, sujet

print('OK : 7 étages, tutoriel neutre aller/retour, sommeil/retrouvailles sur zrv2, départ sur chemin, retour de jour et ressources.')
