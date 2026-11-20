#!/usr/bin/env python3
"""Vérifie la structure complète et les scripts du donjon Fosse Cascade (9 étages, boss Kabutops)."""
from __future__ import annotations

import io
import json
import struct
from collections import deque
from pathlib import Path
from PIL import Image, ImageStat

from executer_lua import run

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_ground_moteur import prepare, rendu, preserver_pixels
from build_grotte_verdoyante import garde_kabuto, BOSS_START, TEAM_START

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
BASE = ROOT / 'base'


def load_tile_headers(sheet_dir: Path, sheet: str) -> dict[tuple[int, int], bytes]:
    raw = (sheet_dir / f'{sheet}.tile').read_bytes()
    ts, cnt = struct.unpack_from('<ii', raw, 0)
    out = {}
    for i in range(cnt):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        ln = struct.unpack_from('<q', raw, off)[0]
        out[(tx, ty)] = raw[off + 8:off + 8 + ln]
    return out


def check_ground_tiles(rsground_path: Path) -> dict:
    doc = json.loads(rsground_path.read_text(encoding='utf-8-sig'))
    obj = doc['Object']
    assert obj['AssetName'] == rsground_path.stem
    assert obj['Released'] is True
    assert obj['EdgeView'] == 1
    tile_cache: dict[str, dict[tuple[int, int], bytes]] = {}
    missing = 0
    for lyr in obj['Layers']:
        for col in lyr['Tiles']:
            for cell in col:
                for sub in cell.get('Layers', []):
                    frs = sub.get('Frames', [])
                    if frs and (not isinstance(sub.get('FrameLength'), int) or sub['FrameLength'] <= 0):
                        raise AssertionError(f'FrameLength invalide dans {rsground_path.name}')
                    for fr in frs:
                        sh = fr.get('Sheet')
                        if not sh:
                            continue
                        if sh not in tile_cache:
                            d = GAME / 'Content/Tile' if (GAME / 'Content/Tile' / f'{sh}.tile').is_file() else BASE / 'Content/Tile'
                            assert (d / f'{sh}.tile').is_file(), f'Planche manquante: {sh}'
                            tile_cache[sh] = load_tile_headers(d, sh)
                        loc = (fr['TexLoc']['X'], fr['TexLoc']['Y'])
                        if loc not in tile_cache[sh]:
                            missing += 1
    assert missing == 0, f'{rsground_path.name}: {missing} TexLoc manquants'
    return obj


# Départ au sud, en deux files autour des virages du sable, et arrivée de Lyra
# en sens inverse. Les mêmes jalons sont attendus dans le test du script Lua.
TRAJETS_SUD = (
    ((244, 420), (276, 376), (280, 352), (280, 288)),
    ((280, 288), (268, 352), (264, 376), (232, 420), (216, 456), (200, 496)),
    ((280, 256), (292, 352), (288, 376), (256, 420), (240, 456), (224, 496)),
    ((248, 260), (264, 276), (268, 352), (264, 376), (232, 420), (216, 456), (208, 464)),
    ((312, 260), (300, 268), (292, 352), (288, 376), (256, 420), (240, 456), (232, 464)),
)


def positions_sur_trajet(*ancres: tuple[int, int]):
    # Interpolation par axe dominant, comme AnimateToPositionGroundAction.
    for (x0, y0), (x1, y1) in zip(ancres, ancres[1:]):
        d = max(1, abs(x1 - x0), abs(y1 - y0))
        for i in range(d + 1):
            yield round(x0 + (x1 - x0) * i / d), round(y0 + (y1 - y0) * i / d)


def check_antichambre(fond: dict) -> None:
    """L'approche est un chemin dans le ground, pas une image ou un zoom."""
    w, h = 72, 66
    assert fond['TexSize'] == 1
    for layer in [*(l['Tiles'] for l in fond['Layers']), fond['obstacles']]:
        assert len(layer) == w and all(len(col) == h for col in layer)
    markers = {m['EntName']: m['Collider'] for group in fond['Entities'] for m in group['Markers']}
    assert markers['entrance'] == {'X': 222, 'Y': 492, 'Width': 16, 'Height': 16}
    obs = fond['obstacles']
    for x, col in enumerate(obs):
        for y, cell in enumerate(col):
            assert cell['Bounds'] == {'X': x * 8, 'Y': y * 8, 'Width': 8, 'Height': 8}
            if x < 6 or x >= 66 or y >= 45:
                assert fond['Layers'][0]['Tiles'][x][y]['Layers'][0]['Frames'][0]['Sheet'] == 'FGV1_PASSAGE_SUD'
            if y >= 45 and (x < 20 or x > 40):
                assert cell['Tags'] != 0, 'les parois latérales ne sont pas praticables'

    def trajet(*ancres: tuple[int, int]) -> None:
        for x, y in positions_sur_trajet(*ancres):
            for col in range(x // 8, (x + 15) // 8 + 1):
                for row in range(y // 8, (y + 15) // 8 + 1):
                    assert obs[col][row]['Tags'] == 0, f'collider 16×16 dans la roche à {x},{y}'

    trajet((222, 492), (246, 436), (292, 368), (292, 220), (292, 244), (290, 242), (292, 244))
    trajet((198, 484), (222, 430), (268, 362), (268, 220), (268, 244), (270, 248), (268, 244))
    trajet((280, 196), (292, 196))
    trajet((280, 244), (280, 244))  # Kabutops ne quitte le milieu que par Tunnel
    trajet((248, 244), (248, 260))
    trajet((312, 244), (312, 260))
    trajet((304, 152), (304, 232), (280, 256))  # Nilo quitte la terrasse et rejoint l’axe
    for jalons in TRAJETS_SUD:
        trajet(*jalons)
    # Le groupe n'est pas masqué sur le plan de découverte ni après la rafale.
    assert 220 + 16 - 216 + 120 < 188
    assert 244 + 16 - 226 + 120 < 188
    assert 332 + 14 + 9 - 246 + 120 < 240  # la terre au sud reste dans le cadre
    assert 292 + 16 - 246 + 120 < 188  # la formation reste lisible pendant le dialogue
    assert 244 + 16 - 242 + 120 < 188  # le trio pendant la réplique de Kabutops
    assert 288 + 16 - 250 + 120 < 188  # Lyra reste au-dessus du texte
    # Nilo est hors de la fenêtre 320×240 pendant le bas du passage.
    assert 372 - 120 > 152 + 16


def main() -> None:
    # 1. Cartes au sol ewc3 & fgv1 + continuité animation cascade L12/L13/L14
    ewc3 = check_ground_tiles(GAME / 'Data/Ground/ewc3_entree_waterfall_cave.rsground')
    fgv1 = check_ground_tiles(GAME / 'Data/Ground/fgv1_fin_grotte_vasques.rsground')
    assert ewc3['Name'] == {'DefaultText': 'Fosse Cascade — Entrée', 'LocalTexts': {'fr': 'Fosse Cascade — Entrée'}}
    assert fgv1['Name'] == {'DefaultText': 'Fosse Cascade Fond', 'LocalTexts': {'fr': 'Fosse Cascade Fond'}}
    check_antichambre(fgv1)
    markers_ewc3 = {m['EntName']: m for m in ewc3['Entities'][0]['Markers']}
    objs_ewc3 = {o['EntName']: o for o in ewc3['Entities'][0]['GroundObjects']}
    assert markers_ewc3['entrance']['Collider']['Y'] == 544
    assert 'SeuilDonjon' in objs_ewc3 and 'SortieRetourReverie' in objs_ewc3
    assert 'Statue_Kangourex' in objs_ewc3
    statue_ewc3 = objs_ewc3['Statue_Kangourex']
    assert statue_ewc3['ObjectAnim']['AnimIndex'] == 'Statue_Kangourex'
    assert statue_ewc3['Passable'] is False and statue_ewc3['triggerType'] == 1
    assert statue_ewc3['Collider'] == {'X': 428, 'Y': 236, 'Width': 24, 'Height': 12}
    # Accès libre devant (432, 248) et à gauche (412, 240) de la statue pour un acteur 16x16
    for ax, ay in ((432, 248), (412, 240)):
        assert all(
            ewc3['obstacles'][cx][cy]['Tags'] == 0
            for cx in range(ax // 8, (ax + 15) // 8 + 1)
            for cy in range(ay // 8, (ay + 15) // 8 + 1)
        ), (ax, ay)
    assert ewc3['Layers'][12]['Visible'] is True and ewc3['Layers'][17]['Visible'] is True
    assert ewc3['Layers'][13]['Visible'] is False and ewc3['Layers'][14]['Visible'] is False and ewc3['Layers'][18]['Visible'] is False

    tile_imgs: dict[str, dict[tuple[int, int], Image.Image]] = {}
    def render_layer(layer_idx: int, fr_idx: int) -> bytes:
        canvas = Image.new('RGBA', (96 * 8, 72 * 8), (0, 0, 0, 0))
        for x, col in enumerate(ewc3['Layers'][layer_idx]['Tiles']):
            for y, cell in enumerate(col):
                for sub in cell.get('Layers', []):
                    frs = sub.get('Frames', [])
                    if not frs:
                        continue
                    fr = frs[fr_idx % len(frs)]
                    sh = fr['Sheet']
                    if sh not in tile_imgs:
                        d = GAME / 'Content/Tile' if (GAME / 'Content/Tile' / f'{sh}.tile').is_file() else BASE / 'Content/Tile'
                        tile_imgs[sh] = {k: Image.open(io.BytesIO(v)).convert('RGBA') for k, v in load_tile_headers(d, sh).items()}
                    canvas.alpha_composite(tile_imgs[sh][(fr['TexLoc']['X'], fr['TexLoc']['Y'])], (x * 8, y * 8))
        return canvas.tobytes()

    assert render_layer(12, 0) == render_layer(13, 0), 'Désaccord pixel L12[0] != L13[0]'
    assert render_layer(13, 23) == render_layer(14, 11), 'Désaccord pixel L13[23] != L14[11]'

    # 2. Planche 24 px et carte de combat 9F end_grotte_verdoyante.rsmap (20x15 = 480x360)
    raw_t24 = (GAME / 'Content/Tile/FGV1_VASQUES_BASE_24.tile').read_bytes()
    ts, cnt24 = struct.unpack_from('<ii', raw_t24, 0)
    assert ts == 24 and cnt24 > 700
    t24_locs = {(tx, ty) for tx, ty, _ in (struct.unpack_from('<iiq', raw_t24, 8 + 16 * i) for i in range(cnt24))}

    rsmap = json.loads((GAME / 'Data/Map/end_grotte_verdoyante.rsmap').read_text(encoding='utf-8-sig'))['Object']
    assert rsmap['AssetName'] == 'end_grotte_verdoyante' and rsmap['NoRescue'] is True
    assert rsmap['Name'] == {'DefaultText': 'Fosse Cascade Fond', 'LocalTexts': {'fr': 'Fosse Cascade Fond'}}
    assert rsmap['Music'] == 'Boss Battle 2.ogg'
    assert rsmap['TileSight'] == 0 and rsmap['CharSight'] == 0 and rsmap['EdgeView'] == 1
    assert rsmap['DiscoveryArray'] == [[2] * 15 for _ in range(20)]
    assert rsmap['MapTeams'][0]['BoxStorage'] == []
    assert rsmap['EntryPoints'] == [{'Loc': {'X': 10, 'Y': 10}, 'Dir': 4}]
    assert TEAM_START == (10, 10)
    boss = rsmap['MapTeams'][0]['Players'][0]['serializationLoc']
    assert boss == {'X': 10, 'Y': 8} and BOSS_START == (10, 8)
    marker = next(e for layer in fgv1['Entities'] for e in layer['Markers'] if e['EntName'] == 'boss')
    anchor = marker['Collider']
    assert (anchor['X'] - 48 + 8, anchor['Y'] + 8) == (boss['X'] * 24 + 12, boss['Y'] * 24 + 12)
    # Le boss est sur le bas des strates et ne rejoint pas la terrasse de Nilo.
    assert anchor['Y'] - 152 >= 40
    for x in range(6 + boss['X'] * 3, 6 + (boss['X'] + 1) * 3):
        for y in range(boss['Y'] * 3, (boss['Y'] + 1) * 3):
            assert fgv1['obstacles'][x][y]['Tags'] == 0
    assert len(rsmap['Layers']) == 2
    assert rsmap['Layers'][0]['Layer'] == 0 and rsmap['Layers'][1]['Layer'] == 4
    for lyr in rsmap['Layers']:
        for rx in range(20):
            for ry in range(15):
                for sub in lyr['Tiles'][rx][ry]['Layers']:
                    for fr in sub['Frames']:
                        assert fr['Sheet'] == 'FGV1_VASQUES_BASE_24'
                        assert (fr['TexLoc']['X'], fr['TexLoc']['Y']) in t24_locs

    floors = {(x, y) for x in range(20) for y in range(15) if rsmap['Tiles'][x][y]['Data']['ID'] == 'floor'}
    q = deque([TEAM_START])
    seen = {TEAM_START}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (cx + dx, cy + dy) in floors and (cx + dx, cy + dy) not in seen:
                seen.add((cx + dx, cy + dy))
                q.append((cx + dx, cy + dy))
    assert floors == seen and len(floors) == 42
    for st in [(10, 12), (9, 12), (11, 12), (10, 13), (10, 10), (8, 9), (12, 9), (10, 7)]:
        assert st in floors, st

    starts = [e['Value']['$type'] for e in rsmap['MapEffect']['OnMapStarts']]
    assert any('BattlePositionEvent' in s for s in starts)
    assert any('BeginBattleEvent' in s for s in starts)
    assert not any('MapTitleDrop' in kind for kind in starts)
    assert (BASE / 'Content/BG/Pre_Battle.dir').is_file()
    assert (BASE / 'Content/Sound/Battle/EVT_Battle_Transition.ogg').is_file()
    assert (BASE / 'Content/BG/White.dir').is_file()
    assert (BASE / 'Content/Particle/Dig.dir').is_file()
    assert (BASE / 'Content/Sound/Battle/DUN_Dig.ogg').is_file()
    assert (BASE / 'Content/Particle/Scratch.dir').is_file()
    assert (BASE / 'Content/Sound/Battle/DUN_Scratch.ogg').is_file()
    assert (BASE / 'Content/Chara/140.chara').is_file()
    assert rsmap['AllyTeams'] == [] and rsmap['Decorations'] == [], 'le spectateur ne change pas les données de l’arène'
    assert (264 // 24, 160 // 24) not in floors, 'la terrasse de Nilo reste en retrait du terrain de combat'

    # Même palette et mêmes pixels entre la salle haute et son arène, sans
    # tronquer à 8 px une case de 24 px. Vérifier aussi une phase animée.
    g, a = prepare(fgv1), prepare(rsmap, arene=True)
    # Les colliders ne suffisent pas : sous une partie des berges dessinées
    # la grille est libre. Vérifier le sable rendu autour du pied des deux
    # jaillissements arrière, à plusieurs phases des tuiles animées.
    departs_sable = ((264, 332), (296, 328))
    def sol_sable(image: Image.Image, x: int, y: int, ample: bool = False) -> None:
        marge = 3 if ample else 1
        sol = ImageStat.Stat(image.crop((x - marge, y + 10, x + 16 + marge, y + 19)).convert('RGB'))
        # Teinte et faible dispersion du sable de cette carte, pas du relief
        # texturé ou de l’eau. Zone de l’ombre et, avec marge, du Tunnel.
        assert sol.extrema[0][0] >= 132 and sol.var[0] < 80 and sol.mean[1] - sol.mean[2] > 45, (x, y, sol.mean)

    for t in (0, 8 * 120, 24 * 120):
        image, erreurs_g = rendu(g, t)
        arene, erreurs_a = rendu(a, t)
        assert erreurs_a == erreurs_g == 0 and arene.size == (480, 360)
        for x, y in (*departs_sable, (280, 244)):
            sol_sable(image, x, y, ample=True)
        for jalons in TRAJETS_SUD:
            for x, y in positions_sur_trajet(*jalons):
                # Le sable est plus sombre au sud. Échantillonner sous
                # l’ombre (12 px), pas au bord du collider (16 px).
                sol = ImageStat.Stat(image.crop((x + 2, y + 10, x + 14, y + 19)).convert('RGB'))
                assert sol.extrema[0][0] >= 95 and sol.var[0] < 80 and sol.mean[1] - sol.mean[2] > 40, (x, y, sol.mean)
        if t == 0:
            image_reference = image
            assert image.crop((48, 0, 528, 360)).tobytes() == arene.tobytes()
    z = preserver_pixels(arene, 2)
    assert z.size == (960, 720) and z.resize(arene.size, Image.Resampling.NEAREST).tobytes() == arene.tobytes()
    assert len(rsmap['MapTeams']) == 1 and rsmap['MapTeams'][0]['LeaderIndex'] == 0
    roster = rsmap['MapTeams'][0]['Players']
    enemies = [(p['BaseForm']['Species'], p['Level']) for p in roster]
    assert enemies == [('kabutops', 14), ('kabuto', 4), ('kabuto', 4), ('kabuto', 3), ('kabuto', 3)], enemies
    assert roster[1:] == garde_kabuto(ROOT, roster[0]), 'les renforts doivent être régénérables sans bonus hérités'
    bornes = [(c['serializationLoc']['X'], c['serializationLoc']['Y'], c['serializationDir']) for c in roster]
    assert bornes == [(10, 8, 0), (8, 9, 7), (11, 9, 1), (9, 12, 4), (10, 12, 4)]
    cases_ennemies = {(x, y) for x, y, _ in bornes}
    assert len(cases_ennemies) == 5 and cases_ennemies <= floors
    positions = next(e['Value'] for e in rsmap['MapEffect']['OnMapStarts'] if 'BattlePositionEvent' in e['Value']['$type'])
    actifs = {(TEAM_START[0] + p['Loc']['X'], TEAM_START[1] + p['Loc']['Y']) for p in positions['StartLocs']}
    assert len(actifs) == 4 and actifs <= floors and not actifs & cases_ennemies
    clear = next(e['Value'] for e in rsmap['MapEffect']['OnMapStarts'] if 'BeginBattleEvent' in e['Value']['$type'])
    assert clear['CheckClearStatus'] == 'map_clear_check'
    # Le détour, l’approche et le recul de peur se font sur du sol libre.
    chemins = (((205, 202), (212, 224), (226, 224), (-6, -4)),
               ((362, 200), (352, 225), (338, 224), (6, -4)),
               (departs_sable[0], (266, 314), (267, 302), (-3, 7)),
               (departs_sable[1], (296, 312), (294, 301), (3, 7)))
    for (depart, passage, menace, (rx, ry)), (x, y, _) in zip(chemins, bornes[1:]):
        cx, cy = 24 * x + 52, 24 * y + 4
        trajet = (depart, passage, menace, (cx, cy), (cx + rx, cy + ry))
        for (sx, sy), (ex, ey) in zip(trajet, trajet[1:]):
            m = max(abs(ex - sx), abs(ey - sy))
            for i in range(m + 1):
                px, py = round(sx + (ex - sx) * i / m), round(sy + (ey - sy) * i / m)
                if depart in departs_sable:
                    sol_sable(image_reference, px, py)
                for tx in range(px // 8, (px + 15) // 8 + 1):
                    for ty in range(py // 8, (py + 15) // 8 + 1):
                        assert fgv1['obstacles'][tx][ty]['Tags'] == 0, f'collider de Kabuto dans le relief à {px},{py}'
    for p in roster:
        assert (BASE / 'Data/Monster' / f"{p['BaseForm']['Species']}.json").is_file()
        assert len(p['BaseSkills']) == len(p['Skills']) == 4, 'quatre slots requis au KO par RestoreForm'
        for i, sk in enumerate(p['Skills']):
            move = sk['Element']['SkillNum']
            assert move == p['BaseSkills'][i]['SkillNum'] and sk['BackRef'] == i
            if move:
                assert (BASE / 'Data/Skill' / f'{move}.json').is_file()
            else:
                assert sk['Element']['Charges'] == p['BaseSkills'][i]['Charges'] == 0
        if p['BaseForm']['Species'] == 'kabuto':
            assert [s['SkillNum'] for s in p['BaseSkills']] == ['scratch', 'harden', '', '']
        for intr in p['Intrinsics']:
            assert (BASE / 'Data/Intrinsic' / f"{intr['Element']['ID']}.json").is_file()

    # 3. Zone grotte_verdoyante.json (9 étages) & index.idx
    zone = json.loads((GAME / 'Data/Zone/grotte_verdoyante.json').read_text(encoding='utf-8-sig'))['Object']
    assert zone['Name'] == {'DefaultText': 'Fosse Cascade', 'LocalTexts': {'fr': 'Fosse Cascade'}}
    assert zone['Released'] is True and len(zone['Segments']) == 2
    assert len(zone['Segments'][0]['Floors']) == 8
    assert len(zone['Segments'][1]['Floors']) == 1
    assert zone['Segments'][0]['ZoneSteps'][1]['Name'] == {'DefaultText': 'Fosse Cascade\n{0}F', 'LocalTexts': {'fr': 'Fosse Cascade\n{0}F'}}
    normal_steps, boss_steps = (segment['ZoneSteps'] for segment in zone['Segments'])
    assert any(s['$type'] == 'PMDC.LevelGen.FloorNameDropZoneStep, PMDC' for s in normal_steps)
    assert not any('FloorNameDrop' in s['$type'] for s in boss_steps), 'carton dynamique dans l’arène'
    assert any('SaveVarsZoneStep' in s['$type'] for s in boss_steps)
    nom_duel = [s['Name'] for s in boss_steps if s['$type'] == 'RogueEssence.LevelGen.FloorNameIDZoneStep, RogueEssence']
    assert nom_duel == [rsmap['Name']], 'le nom du fond doit rester dans le journal'
    boss_gen = zone['Segments'][1]['Floors'][0]['GenSteps']
    assert not any('MapTitleDrop' in s['Value']['$type'] for s in boss_gen)
    assert zone['GroundMaps'] == ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques']
    for i, fl in enumerate(zone['Segments'][0]['Floors']):
        tex_steps = [s['Value'] for s in fl['GenSteps'] if 'MapDictTextureStep' in s['Value']['$type']]
        assert len(tex_steps) == 1
        assert tex_steps[0]['TextureMap']['floor'].startswith('deep_limestone_cavern')
        for at_id in tex_steps[0]['TextureMap'].values():
            assert (BASE / 'Data/AutoTile' / f'{at_id}.json').is_file(), at_id

    zidx = json.loads((GAME / 'Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['grotte_verdoyante']
    assert zidx['Name'] == {'DefaultText': 'Fosse Cascade', 'LocalTexts': {'fr': 'Fosse Cascade'}}
    assert zidx['Released'] is True and zidx['CountedFloors'] == 9
    assert zidx['Maps'] == [[0, 1, 2, 3, 4, 5, 6, 7], [0]]
    assert zidx['Grounds'] == ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques']

    # 4. Vérifications de logique Lua (cascade, zone, boss, post-sauvetage, café, Nilo en ville)
    run(ROOT / 'tools/tests/test_grotte_verdoyante.lua', ROOT)
    run(ROOT / 'tools/tests/test_nilo_temoin.lua', ROOT)
    # 5. Statue-relais Kangourex : le stockage de l'équipe s'ouvre à chaque interaction
    run(ROOT / 'tools/tests/test_statue_kangourex.lua', ROOT)
    print('PASS Fosse Cascade : 9 étages, cascade ewc3, antichambre 576×528, arène 480×360, garde Lv 3/4, scripts Lua et retours vérifiés.')


if __name__ == '__main__':
    main()
