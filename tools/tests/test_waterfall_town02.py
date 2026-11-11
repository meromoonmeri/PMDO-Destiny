#!/usr/bin/env python3
"""Vérifie la carte Waterfall Village étendue et ses dépendances town02."""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import mmap
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
BASE = ROOT / 'base'
MAP = GAME / 'Data/Ground/WaterfallVillageCapital.rsground'
PAYLOAD = ROOT / 'payload/WaterfallVillageCapital.rsground.gz'

sys.path.insert(0, str(ROOT / 'tools'))
import unpack_payload


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


# La carte reconstituée doit être exactement celle du payload vérifié.
assert {k:v for k,v in unpack_payload.PAYLOADS.items() if k in ('payload/WaterfallVillageCapital.rsground.gz', 'payload/WaterfallVillageCapital_Dev.rsground.gz')} == {
    'payload/WaterfallVillageCapital.rsground.gz': (
        'game/Data/Ground/WaterfallVillageCapital.rsground',
        '5749bc59440a50a2a257920a923ef01f8e3de2d4a971fd634ffba90896ca2a9c',
        36696423,
    ),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': (
        'game/Data/Ground/WaterfallVillageCapital_Dev.rsground',
        'cb48b98351c903f1780f3afbd3afed98808546fe6e15a1539604b9432f126061',
        36696427,
    )
}
assert set(unpack_payload.PAYLOADS) == {
    'payload/WaterfallVillageCapital.rsground.gz', 'payload/WaterfallVillageCapital_Dev.rsground.gz',
    'payload/reverie_centre.rsground.gz', 'payload/reverie_nord.rsground.gz',
    'payload/reverie_residentiel.rsground.gz', 'payload/reverie_etang.rsground.gz',
    'payload/reverie_centre_Dev.rsground.gz', 'payload/reverie_nord_Dev.rsground.gz',
    'payload/reverie_residentiel_Dev.rsground.gz', 'payload/reverie_etang_Dev.rsground.gz',
}
if not MAP.is_file():
    assert unpack_payload.main() == 0
assert MAP.stat().st_size == 36696423
assert sha256(MAP) == '5749bc59440a50a2a257920a923ef01f8e3de2d4a971fd634ffba90896ca2a9c'
with gzip.open(PAYLOAD, 'rb') as f:
    h = hashlib.sha256()
    size = 0
    for chunk in iter(lambda: f.read(1 << 20), b''):
        h.update(chunk)
        size += len(chunk)
assert size == 36696423
assert h.hexdigest() == '5749bc59440a50a2a257920a923ef01f8e3de2d4a971fd634ffba90896ca2a9c'

with MAP.open('rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    try:
        sheets = {m.group(1).decode('utf-8') for m in re.finditer(rb'"Sheet":\s*"([^"]+)"', mm)}
        anims = collections.Counter(
            m.group(1).decode('utf-8')
            for m in re.finditer(rb'"AnimIndex":\s*"([^"]+)"', mm)
        )
        def count_mm(pattern: bytes) -> int:
            return len(re.findall(pattern, mm))

        assert count_mm(rb'"Tiles":\s*\[') == 11
        assert count_mm(rb'"EdgeView":1') == 1
        assert count_mm(rb'"EdgeView":0') == 0
        assert count_mm(rb'"AssetName":\s*"WaterfallVillageCapital"') == 1
        for ent in (b'Kecleon', b'Kecleon_Violet', b'Kangourex', b'Drifloon', b'entrance', b'entrance_partner'):
            assert count_mm(rb'"EntName":\s*"' + ent + b'"') == 1, ent
        tail = mm[-2_000_000:].decode('utf-8-sig', errors='ignore')
    finally:
        mm.close()

assert len(sheets) == 27 and {'Reverie_Corrections_Audit', 'Reverie_Raccords_Eau_050', 'Reverie_Herbe_Vagues_051', 'Reverie_Rives_Sable_051', 'Reverie_Berges_053', 'Reverie_Animation_Berge_056', 'Reverie_Animation_Eaux_056', 'Reverie_Fond_Transparences_056', 'Reverie_Ondulations_Rochers_056', 'Reverie_Raccord_Chemin30_056', 'Reverie_Raccord_Escalier_056', 'Reverie_Raccord_Etang_056', 'Reverie_Rochers_Eau_056'} <= sheets, sorted(sheets)
assert {'Reverie_Geo_14_Paysages_composites', 'Reverie_Geo_12_Eaux_frames', 'Reverie_Geo_11_Cascades_frames'} <= sheets
for sheet in sheets:
    assert (GAME / 'Content/Tile' / f'{sheet}.tile').is_file() or (
        BASE / 'Content/Tile' / f'{sheet}.tile'
    ).is_file(), sheet

assert anims == {
    'Flowers_Town_1': 3,
    'Flowers_Tropical_1': 4,
    'Flowers_Tropical_2': 2,
    'Grassy_Bag': 1,
}
for anim in anims:
    assert any(
        (root / 'Content' / folder / f'{anim}.dir').is_file()
        for root in (GAME, BASE)
        for folder in ('Object', 'BG')
    ), anim

# Les 25 habitants sérialisés doivent référencer des espèces/formes livrées.
npcs = re.findall(
    r'"EntName":\s*"([^"]+)".*?"Species":\s*"([^"]+)",\s*"Form":\s*(\d+)',
    tail,
    re.S,
)
assert len(npcs) == 25, npcs
for _ent, species, form in npcs:
    form = int(form)
    data_path = next(
        (p for p in (GAME / 'Data/Monster' / f'{species}.json', BASE / 'Data/Monster' / f'{species}.json') if p.is_file()),
        None,
    )
    assert data_path is not None, species
    data = json.loads(data_path.read_text(encoding='utf-8-sig'))['Object']
    assert form < len(data.get('Forms', [])), (species, form)
    idx = str(data['IndexNum'])
    assert any((root / 'Content/Chara' / f'{idx}.chara').is_file() for root in (GAME, BASE)), species
    assert any((root / 'Content/Portrait' / f'{idx}.portrait').is_file() for root in (GAME, BASE)), species

# Kecleon violet : données, résumé d'index, sprite et portrait town02.
kecleon = json.loads((GAME / 'Data/Monster/kecleon.json').read_text(encoding='utf-8-sig'))['Object']
assert len(kecleon['Forms']) == 2
assert kecleon['Forms'][1]['FormName']['DefaultText'] == 'Purple Kecleon'
monster_index = json.loads((GAME / 'Data/Monster/index.idx').read_text(encoding='utf-8-sig'))['Object']
assert len(monster_index['kecleon']['Forms']) == 2
assert md5(GAME / 'Content/Chara/352.chara') == '0541853000adee497fddf63fdc601fcc'
assert md5(GAME / 'Content/Portrait/352.portrait') == '41b748aaaee075a2497ce2b59828b878'

# Tous les éléments de décoration town02 récupérés avec la carte.
town02_objects = [
    'Anima_Core', 'Anima_Root', 'Anima_Root_Glow', 'Anima_Root_Turnoff',
    'Apricorn_Big', 'Campfire', 'Closed_Guild_Door', 'Core_Activation',
    'Core_Deactivation', 'Diary_Blue_Closing', 'Diary_Blue_Opening',
    'Diary_Red_Closing', 'Diary_Red_Opening', 'Falling_Rock_Shadow', 'Food',
    'Food_Big', 'Food_Flipped', 'Grassy_Bag', 'Hay_Bed', 'Kangaskhan_Rock',
    'Night_Window', 'Paper_1', 'River_Stone_Diamond', 'River_Stone_Round',
    'Spring_Cave_Pit_Big_Lava_Stream', 'Spring_Cave_Pit_Lava_Pool_Connected',
    'Spring_Cave_Pit_Lava_Pool_Disconnected',
    'Spring_Cave_Pit_Small_Lava_Stream', 'Tablette_Zarbi', 'Yellow_Box',
]
for name in town02_objects:
    assert (GAME / 'Content/Object' / f'{name}.dir').is_file(), name
assert len(list((GAME / 'Content/Objects').glob('*.png'))) == 74

# Comptoirs des boutiques (façon Reverie Town) : les six marchands servent
# depuis l’alcôve fermée de leur boutique, derrière un objet-comptoir posé
# sur la devanture, et l’interaction devant le comptoir ouvre leur service.
ville_lua = (GAME / 'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf-8')
comptoirs_attendus = {
    'ComptoirKecleon': 'Kecleon',
    'ComptoirKecleonViolet': 'Kecleon_Violet',
    'ComptoirBanqueMordudor': 'NewObject_3',
    'ComptoirAlakazam': 'NewObject_4',
    'ComptoirKangourex': 'Kangourex',
    'ComptoirForgeTinkaton': 'NewObject_24',
}
for nom_comptoir, marchand in comptoirs_attendus.items():
    assert f"nom = '{nom_comptoir}', marchand = '{marchand}'" in ville_lua, nom_comptoir
for poste in ('poste_x = 504, poste_y = 1040', 'poste_x = 360, poste_y = 1100',
              'poste_x = 940, poste_y = 930', 'poste_x = 1104, poste_y = 992'):
    assert poste in ville_lua, poste
assert ville_lua.count('installer_comptoirs(map)') >= 3  # définition, Init, GameLoad
assert ville_lua.count('placer_marchands_aux_comptoirs()') >= 3
assert ville_lua.index('  placer_marchands_aux_comptoirs()', ville_lua.index('function ville.Init(map)')) < ville_lua.index('  positions_habitants = {}', ville_lua.index('function ville.Init(map)'))
assert "ville[comptoir.nom .. '_Action']" in ville_lua
assert "habitant_du_quartier(map, 'Kecleon', 'kecleon', Gender.Male, 599, 922)" in ville_lua
assert "habitant_du_quartier(map, 'Kangourex', 'kangaskhan', Gender.Female, 940, 930)" in ville_lua
# Les seuils devenus comptoirs n’ouvrent plus sur un intérieur.
for porte_retiree in ('PorteMaisonAlakazam', 'PorteReserveKangourex', 'PorteForgeTinkaton'):
    assert porte_retiree not in ville_lua, porte_retiree

# Tinkaton reste à son échoppe extérieure : à l’ouverture payée, elle se
# retourne vers le nord, abat son Attack, et l’explosion + le tremblement
# d’écran natif partent sur la frame d’impact, avant de revenir au sud.
_frappe = ville_lua[ville_lua.index('local function frapper_boites_forgelina'):
                    ville_lua.index('function ville.NewObject_24_Action')]
assert _frappe.index('Direction.Up, 4') \
    < _frappe.index("GROUND:CharSetAnim(personnage, 'Attack', false)") \
    < _frappe.index('GAME:WaitFrames(16)') \
    < _frappe.index('RogueEssence.Content.ScreenMover(0, 12, 30)') \
    < _frappe.index("SOUND:PlayBattleSE('DUN_Explosion')") \
    < _frappe.index('GAME:WaitFrames(20)') \
    < _frappe.index('GROUND:CharEndAnim(personnage)') \
    < _frappe.index('Direction.Down, 4')
_service_forgelina = ville_lua[ville_lua.index('function ville.NewObject_24_Action'):
                               ville_lua.index('local dialogues_lombre_ludicolo')]
assert _service_forgelina.index('Reculez un peu… et voilà le travail !') \
    < _service_forgelina.index('frapper_boites_forgelina(personnage)') \
    < _service_forgelina.index("SOUND:PlayFanfare('Fanfare/Treasure')") \
    < _service_forgelina.index('UI:SpoilsMenu(tresor)')
from fusionner_conteneurs_pmd import load_container as _load_chara
from ajouter_pose_chara import parse_blob as _parse_chara
_tinkaton_path = next(p for p in (GAME / 'Content/Chara/959.chara', BASE / 'Content/Chara/959.chara') if p.is_file())
_tinkaton_groups = _parse_chara(_load_chara(_tinkaton_path, 'Chara').payload)['groups']
_attack = _tinkaton_groups[5]  # FrameType moteur Attack
_durs_nord = [f[2] for f in _attack['seqs'][4]]  # Dir8.Up = index 4
assert _attack['hit'] == 3 and sum(_durs_nord) == 36
assert sum(_durs_nord[:_attack['hit']]) == 16

# Bassin logique sous la cascade isolee sud-ouest (wf_isol_36, 16x5t en x=32..47, y=255..259) :
# 54 tuiles d'eau Reverie_Geo_03/04/12 en L2, mousse/ombre nettoyees en L6, rocher (43,253) en L7,
# tous les 54 obstacles Tags=1 sous le bassin et bordure est (48..50) libre vers la maison Armulys.
_wvc = json.loads(MAP.read_text(encoding='utf-8-sig'))['Object']
_l2_tiles = _wvc['Layers'][2]['Tiles']
_l6_tiles = _wvc['Layers'][6]['Tiles']
_l7_tiles = _wvc['Layers'][7]['Tiles']
_water_sheets = (
    'Reverie_Geo_03_Rivieres_eau',
    'Reverie_Geo_04_Rives_et_transitions',
    'Reverie_Geo_12_Eaux_frames',
)
_basin_cells = []
for _x in range(32, 48):
    for _y in range(255, 260):
        _sub = _l2_tiles[_x][_y].get('Layers', [])
        if _sub and all(f['Sheet'] in _water_sheets for f in _sub[0].get('Frames', [])):
            _basin_cells.append((_x, _y))
assert len(_basin_cells) == 54, len(_basin_cells)
assert not _l6_tiles[41][258].get('Layers') and not _l6_tiles[42][258].get('Layers')
assert _l7_tiles[43][253].get('Layers')
assert all(_wvc['obstacles'][_x][_y]['Tags'] == 1 for _x, _y in _basin_cells)
assert all(_wvc['obstacles'][_x][_y]['Tags'] == 0 for _x in range(48, 51) for _y in range(254, 260))

print('OK : Waterfall Village étendue, 14 banques Réverie autonomes, habitants, objets, décorations town02 et comptoirs des marchands.')
