#!/usr/bin/env python3
"""Vérifie les raccordements de Bois Perdus et les ressources de la statue."""
from pathlib import Path
import json
import struct
import sys

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
assert floor_names == ['Bois Perdus\n{0}F', 'Bois Perdus\nB{0}F']
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
cinematique = (GAME / 'Data/Script/destiny/cinematique.lua').read_text(encoding='utf-8')
# Conventions partagées du PMD Cutscene Guide : portraits bas gauche/droite
# en miroir, respiration de 20 frames et rotations de groupe désynchronisées.
assert 'UI:SetSpeakerLoc(p[1], p[2])' in cinematique
assert 'standard = {8, 132, false}' in cinematique
assert 'droite = {256, 132, true}' in cinematique
assert 'function cinematique.TournerGroupe' in cinematique
assert 'function cinematique.RegarderGroupe' in cinematique
assert 'GAME:WaitFrames(frames or 20)' in cinematique
scene = (GAME / 'Data/Script/destiny/ground/cliffdaytest_nuit/init.lua').read_text(encoding='utf-8')
assert 'SOUND:PlayBGM' not in scene
assert 'GROUND:MoveToPosition(partenaire' in scene
assert 'Pichu_Home_Door' in scene and 'Pichu_Crossroads' in scene
assert 'Dazzling_Exit_East' in scene and 'chemin de l’est' in scene
assert 'LostWoodTutorialDone' not in scene
assert "require 'destiny.cinematique'" in scene
assert 'GAME:MoveCamera(raccord_est_x, route_est_y + 12, 92, false)' in scene
assert 'GAME:MoveCamera(entree.Position.X - 40, route_est_y + 12, 220, false)' in scene
assert '\\n Au bout' not in scene and '\\n personne' not in scene
quiz = (GAME / 'Data/Script/destiny/ground/personality_test/init.lua').read_text(encoding='utf-8')
assert quiz.index('SOUND:FadeOutBGM(60)') < quiz.index("Une faille s'ouvre dans le rêve")
assert "PrologueHeros = 'a_voir'" in quiz
assert "EnterGroundMap('reverie', 'zrv2_zone_reveil_nuit', 'reveil')" in quiz
reverie = json.loads((GAME / 'Data/Zone/reverie.json').read_text(encoding='utf-8-sig'))['Object']
assert reverie['GroundMaps'][10] == 'zrv2_zone_reveil_nuit'
reveil = (GAME / 'Data/Script/destiny/ground/reveil_nuit/init.lua').read_text(encoding='utf-8')
for phrase in ('…Où suis-je ?', 'Tout est flou… Je ne me souviens de rien.',
               '…Sauf d’une chose.', 'Mon prénom…'):
    assert phrase in reveil
# Pensées blanches sur le noir : phrases courtes, sans balise [i], avec le
# fondu d'entrée/sortie des voix-off PMDO (SetAutoFinish), puis retour au
# comportement normal pour les dialogues suivants.
assert 'UI:SetAutoFinish(true)' in reveil and 'UI:SetAutoFinish(false)' in reveil
assert 'WaitShowVoiceOver("[i]' not in reveil
assert "MRKR('reveil')" in reveil and "MRKR('entrance')" in reveil
assert 'points_scene()' in reveil and 'Un jour, je ferai la carte de cette montagne !' in reveil
# Viewport 320×240 : ouverture Y=136 et panorama Y=152 pour garder lune,
# sommet et mer dans le cadre, avec des travelings rejoints explicitement.
assert 'camera_ouverture_y = point_reveil.Position.Y - 104' in reveil
assert 'camera_panorama_y = point_reveil.Position.Y - 88' in reveil
assert 'camera_approche_y = point_reveil.Position.Y + 48' in reveil
assert 'TASK:BranchCoroutine' in reveil and 'TASK:JoinCoroutines' in reveil
assert "require 'destiny.cinematique'" in reveil
assert "cinematique.Dire(partner, emotion, texte, 'droite')" in reveil
assert 'EVT_Emote_Shock' in reveil and 'EVT_Emote_Exclaim_2' in reveil
assert 'cinematique.TournerGroupe' in reveil
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
# Retour des Bois Perdus : prénom dynamique, partenaire devant, maison,
# pensée du héros en italique et gestuelle face à face.
assert 'nom_heros()' in cliff_jour and 'On est arrivés !' in cliff_jour
assert 'tu ne te débrouilles pas trop mal' in cliff_jour
assert "C’est ici que j’habite" in cliff_jour and 'capitale mondiale des explorateurs' in cliff_jour
assert 'Je me demande dans quoi je me suis embarqué…' in cliff_jour
assert 'se_faire_face(partner, hero)' in cliff_jour and "geste_heros(hero, 'idle', partner)" in cliff_jour
assert 'RencontreTeamDazzling' in cliff_jour and 'TeamDazzlingRencontree' in cliff_jour
# Voix hors champ sans portrait, thème social, vraie Pose tenue et petites
# étoiles PMDO autour des trois membres.
assert "UI:SetSpeaker('???'" in cliff_jour and 'Hilarant.' in cliff_jour and 'super entrée' in cliff_jour
assert 'Ne me dis pas que…' in cliff_jour
assert 'Team Dazzling Social.ogg' in cliff_jour
assert 'Lucky_Chant_Star_Yellow' in cliff_jour and 'Sparkle_RSE' not in cliff_jour
assert 'PoseGroundAction' in cliff_jour and "GetAnimIndex('Pose')" in cliff_jour
assert "require 'destiny.cinematique'" in cliff_jour
assert "'droite'" in cliff_jour and "'standard'" in cliff_jour
assert 'GAME:MoveCamera(800, 468, 80, false)' in cliff_jour
assert 'GAME:MoveCamera(720, 672, 190, false)' in cliff_jour
assert 'GROUND:MoveToPosition(sonata, 736, 700, false, 1.5)' in cliff_jour
assert 'poser_dazzling(sonata, false)' in cliff_jour
assert "GROUND:CharSetEmote(partner, 'shock', 1)" in cliff_jour
assert "GROUND:CharSetEmote(hero, 'exclaim', 1)" in cliff_jour
assert 'EVT_Emote_Complain' in cliff_jour
assert 'Réverie Town[color] n’est pas un lieu pour des amateurs' in cliff_jour
assert 'Mais pour qui vous vous prenez ?!' in cliff_jour
assert 'saluer l’affiche' not in cliff_jour and 'héros muet' not in cliff_jour
# Face-à-face et poussée sur les chemins, puis Hide seulement hors champ.
for coordonnees in ('688, 700', '712, 700', '736, 700', '712, 732', '736, 732',
                    '684, 736', '708, 736', '713, 676', 'sud.Position.X'):
    assert coordonnees in cliff_jour
assert "AnimateToPosition(hero, 'Hurt'" in cliff_jour
assert "AnimateToPosition(partner, 'Hurt'" in cliff_jour
for nom in ('Adagio', 'Sonata', 'Aria'):
    assert f"GROUND:Hide('{nom}')" in cliff_jour
musique_dazzling = (GAME / 'Content/Music/Team Dazzling Social.ogg').read_bytes()
assert musique_dazzling.startswith(b'OggS') and b'vorbis' in musique_dazzling
assert b'Encounter! Jacinthe' in musique_dazzling
assert b'LOOPSTART=003079417' in musique_dazzling
assert b'LOOPLENGTH=003135999' in musique_dazzling
# La Pose V2 est un vrai groupe 13 dans le payload normal des trois .chara,
# avec huit directions et les durées SpriteCollab attendues.
sys.path.insert(0, str(ROOT / 'tools'))
from ajouter_pose_chara import parse_blob
from fusionner_conteneurs_pmd import load_container, read_node
index_chara, _ = read_node((GAME / 'Content/Chara/index.idx').read_bytes())
assert {303, 428, 763} <= set(index_chara.kids)
durees_pose = {
    303: [4, 1, 2, 4, 2, 1, 2],
    428: [4, 3, 3, 6],
    763: [4, 4, 6],
}
for dex, durees in durees_pose.items():
    conteneur = load_container(GAME / f'Content/Chara/{dex}.chara', 'Chara')
    groupe_pose = parse_blob(conteneur.payload)['groups'][13]
    assert groupe_pose['copy'] == -1 and len(groupe_pose['seqs']) == 8
    assert all([frame[2] for frame in seq] == durees for seq in groupe_pose['seqs'])
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

# Premier combat jouable : Pose relevée, Woosh étoilé et musique au même
# instant, segment donjon sur la version .rsmap de la même falaise.
assert "montrez-moi ce que vous avez dans le ventre" in cliff_jour
assert "Dazzling Fight.ogg" in cliff_jour and "Pre_Battle_Dazzling_Etoiles" in cliff_jour
assert "SOUND:PlayBGM(MUSIQUE_DAZZLING_COMBAT, false)" in cliff_jour
assert "jouer_woosh_dazzling()" in cliff_jour
assert 'GAME:FadeOut(true, 0)' in cliff_jour
assert "GAME:EnterDungeon('dazzling_fight', 0, 0, 0" in cliff_jour
assert "ApresCombatTeamDazzling" in cliff_jour and "TeamDazzlingVictoire" in cliff_jour
zone_dazzling = json.loads((GAME / 'Data/Zone/dazzling_fight.json').read_text(encoding='utf-8-sig'))['Object']
assert zone_dazzling['NoEXP'] is True and len(zone_dazzling['Segments']) == 1
index_zones = json.loads((GAME / 'Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']
assert index_zones['dazzling_fight']['Grounds'] == []
assert index_zones['dazzling_fight']['Maps'] == [[0]]
assert index_zones['dazzling_fight']['CountedFloors'] == 1
segment_dazzling = zone_dazzling['Segments'][0]
assert segment_dazzling['Floors'][0]['GenSteps'][0]['Value']['MapID'] == 'cliffdaytest'
script_zone_dazzling = (GAME / 'Data/Script/destiny/zone/dazzling_fight/init.lua').read_text(encoding='utf-8')
assert "CombatDazzling = 'victoire'" in script_zone_dazzling
assert "CombatDazzling = 'defaite'" in script_zone_dazzling
combat_map = json.loads((GAME / 'Data/Map/cliffdaytest.rsmap').read_text(encoding='utf-8-sig'))['Object']
assert combat_map['AssetName'] == 'cliffdaytest' and combat_map['EdgeView'] == 1
assert len(combat_map['Tiles']) == 41 and len(combat_map['Tiles'][0]) == 33
assert combat_map['EntryPoints'] == [{'Loc': {'X': 29, 'Y': 30}, 'Dir': 4}]
equipe_dazzling = combat_map['MapTeams'][0]['Players']
assert [(p['Nickname'], p['CurrentForm']['Species'], p['Level'], p['serializationLoc'], p['serializationDir']) for p in equipe_dazzling] == [
    ('Adagio', 'tsareena', 32, {'X': 29, 'Y': 29}, 0),
    ('Sonata', 'lopunny', 31, {'X': 30, 'Y': 29}, 0),
    ('Aria', 'mawile', 30, {'X': 28, 'Y': 29}, 0),
]
assert "Dazzling_Exit_East" in cliff_jour and "Réverie Town[color] nous attend" in cliff_jour
effets_combat = [e['Value']['$type'] for e in combat_map['MapEffect']['OnMapStarts']]
assert any('BattlePositionEvent' in t for t in effets_combat)
assert any('BeginBattleEvent' in t for t in effets_combat)
for sheet_name in ('CLIFFDAYTEST_BATTLE_BASE_24', 'CLIFFDAYTEST_BATTLE_FRONT_24'):
    sheet = (GAME / f'Content/Tile/{sheet_name}.tile').read_bytes()
    assert struct.unpack_from('<i', sheet)[0] == 24
# Toute coordonnée référencée par la map doit exister dans sa planche :
# sinon PMDO dessine sa texture d'erreur à la place du ciel.
tile_locs = {}
for sheet_name in ('CLIFFDAYTEST_BATTLE_BASE_24', 'CLIFFDAYTEST_BATTLE_FRONT_24'):
    sheet = (GAME / f'Content/Tile/{sheet_name}.tile').read_bytes()
    _ts, _count = struct.unpack_from('<ii', sheet)
    tile_locs[sheet_name] = {struct.unpack_from('<ii', sheet, 8 + i * 16) for i in range(_count)}
for layer in combat_map['Layers']:
    for col in layer['Tiles']:
        for cell in col:
            for sub in cell['Layers']:
                for fr in sub['Frames']:
                    assert (fr['TexLoc']['X'], fr['TexLoc']['Y']) in tile_locs[fr['Sheet']]
musique_combat = (GAME / 'Content/Music/Dazzling Fight.ogg').read_bytes()
assert musique_combat.startswith(b'OggS') and b'vorbis' in musique_combat
woosh_dazzling = (GAME / 'Content/BG/Pre_Battle_Dazzling_Etoiles.dir').read_bytes()
assert struct.unpack_from('<q', woosh_dazzling)[0] > 0

print('OK : prologue, aller, retour inverse 7→1, arrivée au jour, Team Dazzling (social + combat), tutoriel et statue.')
