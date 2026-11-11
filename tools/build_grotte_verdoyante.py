#!/usr/bin/env python3
"""Construit et assemble les données du donjon Grotte Verdoyante (9 étages) :

1. game/Data/Ground/ewc3_entree_waterfall_cave.rsground (remappage TexLoc -> HEAD)
2. game/Data/Ground/fgv1_fin_grotte_vasques.rsground (remappage TexLoc -> HEAD)
3. game/Content/Tile/FGV1_VASQUES_BASE_24.tile (tuiles 24x24 animées 12 phases)
4. game/Data/Map/end_grotte_verdoyante.rsmap (arène Boss 9F sur fgv1_fin_grotte_vasques)
5. game/Data/Zone/grotte_verdoyante.json (donjon 9 étages : 1F-8F procédural + 9F Boss)
6. game/Data/Zone/index.idx (entrée grotte_verdoyante ajoutée proprement)

Dépendances CI uniquement : stdlib + Pillow (aucun numpy/scipy).
"""

from __future__ import annotations

import hashlib
import io
import json
import struct
import subprocess
import sys
from collections import deque
from pathlib import Path
from PIL import Image

DEFAULT_WT = Path(__file__).resolve().parents[1]
DEFAULT_GIT = Path('/home/user/.grotte_git')
MAP_W, MAP_H = 96, 72
MAP24_W, MAP24_H = 32, 24


def load_tile_from_source(root: Path, git_repo: Path | None, ref: str, sheet: str) -> tuple[int, dict[tuple[int, int], bytes], dict[str, tuple[int, int]]]:
    rel = f'game/Content/Tile/{sheet}.tile'
    disk = root / rel
    if ref == 'HEAD' and disk.is_file():
        raw = disk.read_bytes()
    else:
        if git_repo is None or not git_repo.exists():
            raise FileNotFoundError(f'Impossible de lire {ref}:{rel}')
        raw = subprocess.check_output(['git', '-C', str(git_repo), 'show', f'{ref}:{rel}'])
    ts, count = struct.unpack_from('<ii', raw, 0)
    tiles: dict[tuple[int, int], bytes] = {}
    blobs: dict[str, tuple[int, int]] = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        ln = struct.unpack_from('<q', raw, off)[0]
        blob = raw[off + 8:off + 8 + ln]
        tiles[(tx, ty)] = blob
        h = hashlib.sha256(blob).hexdigest()
        blobs.setdefault(h, (tx, ty))
    return ts, tiles, blobs


def unpremultiply_im(im: Image.Image) -> Image.Image:
    im = im.convert('RGBA')
    px = bytearray(im.tobytes())
    for k in range(0, len(px), 4):
        a = px[k + 3]
        if 0 < a < 255:
            px[k] = min(255, round(px[k] * 255.0 / a))
            px[k + 1] = min(255, round(px[k + 1] * 255.0 / a))
            px[k + 2] = min(255, round(px[k + 2] * 255.0 / a))
        elif a == 0:
            px[k] = px[k + 1] = px[k + 2] = 0
    return Image.frombytes('RGBA', im.size, bytes(px))


def premultiply_im(im: Image.Image) -> Image.Image:
    im = im.convert('RGBA')
    px = bytearray(im.tobytes())
    for k in range(0, len(px), 4):
        a = px[k + 3]
        if 0 < a < 255:
            af = a / 255.0
            px[k] = min(255, round(px[k] * af))
            px[k + 1] = min(255, round(px[k + 1] * af))
            px[k + 2] = min(255, round(px[k + 2] * af))
        elif a == 0:
            px[k] = px[k + 1] = px[k + 2] = 0
    return Image.frombytes('RGBA', im.size, bytes(px))


def save_tile_sheet(dest: Path, tile_size: int, tiles: dict[tuple[int, int], Image.Image]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    items: list[tuple[int, int, bytes]] = []
    for tx, ty in sorted(tiles.keys()):
        im = tiles[(tx, ty)].convert('RGBA')
        alpha = im.getchannel('A')
        if alpha.getbbox() is None:
            continue
        pim = premultiply_im(im)
        buf = io.BytesIO()
        pim.save(buf, format='PNG')
        items.append((tx, ty, buf.getvalue()))
    count = len(items)
    header_size = 8 + 16 * count
    chunks: list[bytes] = []
    offsets: list[int] = []
    cur = header_size
    for _, _, blob in items:
        offsets.append(cur)
        chunk = struct.pack('<q', len(blob)) + blob
        chunks.append(chunk)
        cur += len(chunk)
    with dest.open('wb') as f:
        f.write(struct.pack('<ii', tile_size, count))
        for (tx, ty, _), off in zip(items, offsets):
            f.write(struct.pack('<iiq', tx, ty, off))
        for ch in chunks:
            f.write(ch)


def remap_ground_from_eeba71b4(
    root: Path, git_repo: Path, gname: str, title_default: str, title_fr: str
) -> tuple[dict, dict[str, dict[tuple[int, int], Image.Image]]]:
    raw = subprocess.check_output(
        ['git', '-C', str(git_repo), 'show', f'origin/eeba71b4:game/Data/Ground/{gname}.rsground']
    ).decode('utf-8-sig')
    doc = json.loads(raw)
    obj = doc['Object']
    obj['AssetName'] = gname
    obj['Released'] = True
    obj['Name'] = {'DefaultText': title_default, 'LocalTexts': {'fr': title_fr}}
    if gname == 'ewc3_entree_waterfall_cave':
        obj['Music'] = 'Lower Spring Cave.ogg'
        obj['Comment'] = 'PMDO 0.8.12. Entrée de la Grotte Verdoyante (cascade fermée / ouverture / ouverte), raccordée à Réverie Town et au 1F.'
        ents = obj['Entities'][0]
        for mk in ents.get('Markers', []):
            if mk.get('EntName') == 'entrance':
                mk['Collider']['Y'] = 544
        def _make_trigger(name: str, x: int, y: int, w: int, h: int) -> dict:
            return {
                'EntName': name,
                'Direction': 0,
                'EntEnabled': True,
                'EntOrder': 0,
                'InteractOrder': 0,
                'triggerType': 2,
                'ObjectAnim': {
                    '$type': 'RogueEssence.Content.ObjAnimData, RogueEssence',
                    'AnimIndex': '', 'FrameTime': 1, 'StartFrame': -1, 'EndFrame': -1,
                    'AnimDir': -1, 'Alpha': 255, 'AnimFlip': 0,
                },
                'Passable': True,
                'CurrentAnim': {
                    '$type': 'RogueEssence.Content.ObjAnimData, RogueEssence',
                    'AnimIndex': '', 'FrameTime': 1, 'StartFrame': -1, 'EndFrame': -1,
                    'AnimDir': -1, 'Alpha': 255, 'AnimFlip': 0,
                },
                'AnimTime': {'Ticks': 0},
                'Cycles': 0,
                'DrawOffset': {'X': 0, 'Y': 0},
                'Collider': {'X': x, 'Y': y, 'Width': w, 'Height': h},
            }
        ents['GroundObjects'] = [
            _make_trigger('SeuilDonjon', 368, 184, 40, 24),
            _make_trigger('SortieRetourReverie', 320, 568, 144, 8),
        ]
    elif gname == 'fgv1_fin_grotte_vasques':
        obj['Music'] = ''
        obj['Comment'] = 'PMDO 0.8.12. Salle des vasques (9F de la Grotte Verdoyante), sauvetage de Nilo et combat contre la Bande des Vasques.'

    sheets = set()
    for lyr in obj['Layers']:
        for col in lyr['Tiles']:
            for cell in col:
                for sub in cell.get('Layers', []):
                    for fr in sub.get('Frames', []):
                        if fr.get('Sheet'):
                            sheets.add(fr['Sheet'])

    old_tiles = {}
    head_tiles_raw = {}
    head_blobs = {}
    decoded_head: dict[str, dict[tuple[int, int], Image.Image]] = {}
    for sh in sorted(sheets):
        _, ot, _ = load_tile_from_source(root, git_repo, 'origin/eeba71b4', sh)
        _, ht, hb = load_tile_from_source(root, git_repo, 'HEAD', sh)
        old_tiles[sh] = ot
        head_tiles_raw[sh] = ht
        head_blobs[sh] = hb
        decoded_head[sh] = {}

    remapped = 0
    missing = 0
    for lyr in obj['Layers']:
        for col in lyr['Tiles']:
            for cell in col:
                for sub in cell.get('Layers', []):
                    for fr in sub.get('Frames', []):
                        sh = fr.get('Sheet')
                        if not sh:
                            continue
                        loc = (fr['TexLoc']['X'], fr['TexLoc']['Y'])
                        blob = old_tiles[sh].get(loc)
                        if blob is None:
                            missing += 1
                            continue
                        if head_tiles_raw[sh].get(loc) != blob:
                            h = hashlib.sha256(blob).hexdigest()
                            new_loc = head_blobs[sh].get(h)
                            if new_loc is None:
                                missing += 1
                                continue
                            fr['TexLoc']['X'], fr['TexLoc']['Y'] = new_loc
                            loc = new_loc
                            remapped += 1
                        if loc not in decoded_head[sh]:
                            decoded_head[sh][loc] = unpremultiply_im(Image.open(io.BytesIO(head_tiles_raw[sh][loc])))

    assert missing == 0, f'{gname}: {missing} tuiles introuvables dans HEAD'
    print(f'[OK] {gname}: sheets={len(sheets)} remapped={remapped} missing={missing}')
    return doc, decoded_head


def build_fgv1_battle_map_and_tiles(root: Path, fgv1_doc: dict, decoded_head: dict[str, dict[tuple[int, int], Image.Image]]) -> None:
    obj = fgv1_doc['Object']
    # Repérer quelles cellules 24x24 ont une animation (L06 ou L07)
    animated_cells: set[tuple[int, int]] = set()
    for li in (6, 7):
        tiles = obj['Layers'][li]['Tiles']
        for x in range(MAP_W):
            for y in range(MAP_H):
                for sub in tiles[x][y].get('Layers', []):
                    if len(sub.get('Frames', [])) > 1:
                        animated_cells.add((x // 3, y // 3))

    # Construire les 12 phases (L06 a 12 frames FrameLength=8 ; L07 a 24 frames FrameLength=4)
    base24: dict[tuple[int, int], Image.Image] = {}
    phase_imgs: list[Image.Image] = []
    for ph in range(12):
        canvas = Image.new('RGBA', (MAP_W * 8, MAP_H * 8), (0, 0, 0, 255))
        for li in range(8):
            if not obj['Layers'][li].get('Visible', True):
                continue
            tiles = obj['Layers'][li]['Tiles']
            for x in range(MAP_W):
                for y in range(MAP_H):
                    for sub in tiles[x][y].get('Layers', []):
                        frs = sub.get('Frames', [])
                        if not frs:
                            continue
                        idx = (ph * 2) % len(frs) if len(frs) == 24 else ph % len(frs)
                        fr = frs[idx]
                        im = decoded_head[fr['Sheet']][(fr['TexLoc']['X'], fr['TexLoc']['Y'])]
                        canvas.alpha_composite(im, (x * 8, y * 8))
        phase_imgs.append(canvas)

    layer0_tiles = [[None for _ in range(MAP24_H)] for _ in range(MAP24_W)]
    for rx in range(MAP24_W):
        for ry in range(MAP24_H):
            if (rx, ry) in animated_cells:
                frames_json = []
                for ph in range(12):
                    crop = phase_imgs[ph].crop((rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24))
                    base24[(rx, ry + MAP24_H * ph)] = crop
                    frames_json.append({'Sheet': 'FGV1_VASQUES_BASE_24', 'TexLoc': {'X': rx, 'Y': ry + MAP24_H * ph}})
                layer0_tiles[rx][ry] = {
                    'AutoTileset': '',
                    'Associates': [],
                    'Layers': [{'Frames': frames_json, 'FrameLength': 8}],
                    'NeighborCode': -1,
                }
            else:
                crop = phase_imgs[0].crop((rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24))
                base24[(rx, ry)] = crop
                layer0_tiles[rx][ry] = {
                    'AutoTileset': '',
                    'Associates': [],
                    'Layers': [{'Frames': [{'Sheet': 'FGV1_VASQUES_BASE_24', 'TexLoc': {'X': rx, 'Y': ry}}], 'FrameLength': 60}],
                    'NeighborCode': -1,
                }

    save_tile_sheet(root / 'game/Content/Tile/FGV1_VASQUES_BASE_24.tile', 24, base24)

    # Grille de tuiles 32x24 alignée sur les obstacles de fgv1_fin_grotte_vasques
    obs = obj['obstacles']
    tiles_grid = []
    floors: set[tuple[int, int]] = set()
    for rx in range(MAP24_W):
        col = []
        for ry in range(MAP24_H):
            blocked = sum(1 for dx in range(3) for dy in range(3) if obs[rx * 3 + dx][ry * 3 + dy]['Tags'] != 0)
            is_floor = (
                ry >= 10
                and blocked < 4
                and not (ry == 18 and rx not in range(13, 20))
                and not (ry >= 19 and rx not in range(14, 18))
            )
            if is_floor:
                floors.add((rx, ry))
            col.append({
                'Data': {
                    'ID': 'floor' if is_floor else 'unbreakable',
                    'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1},
                    'StableTex': False,
                },
                'Effect': {'TileLoc': {'X': rx, 'Y': ry}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
            })
        tiles_grid.append(col)

    # Garantir la zone de départ du combat (16, 18) et les voisins immédiats en floor
    start = (16, 18)
    for sx, sy in [(16, 18), (15, 18), (17, 18), (16, 19), (16, 17), (16, 13), (14, 14), (18, 14), (16, 11)]:
        tiles_grid[sx][sy]['Data']['ID'] = 'floor'
        floors.add((sx, sy))

    # Élaguer toute poche floor déconnectée
    q = deque([start])
    seen = {start}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            np_ = (cx + dx, cy + dy)
            if np_ in floors and np_ not in seen:
                seen.add(np_)
                q.append(np_)
    for rx, ry in floors - seen:
        tiles_grid[rx][ry]['Data']['ID'] = 'unbreakable'

    def tactic_boss(role: str) -> dict:
        is_leader = (role == 'boss')
        return {
            'Name': {'DefaultText': 'Boss' if is_leader else 'Normal Wander', 'LocalTexts': {}},
            'Released': False,
            'Comment': '',
            'ID': 'boss' if is_leader else 'wander_normal',
            'Assignable': False,
            'Plans': [
                {
                    '$type': 'PMDC.Dungeon.AttackFoesPlan, PMDC',
                    'AttackPattern': 4 if is_leader else 2,
                    'PositionPattern': 2 if is_leader else 1,
                    'IQ': 253 if is_leader else 100,
                    'RestrictedMobilityTypes': 0,
                    'RestrictMobilityPassable': False,
                    'AttackRange': 0,
                    'StatusRange': 0,
                    'SelfStatusRange': 4,
                    'AbandonRangeOnHit': True,
                },
                {
                    '$type': 'PMDC.Dungeon.FollowLeaderPlan, PMDC',
                    'IQ': 253 if is_leader else 228,
                    'RestrictedMobilityTypes': 0,
                    'RestrictMobilityPassable': False,
                    'AttackRange': 0,
                    'StatusRange': 0,
                    'SelfStatusRange': 0,
                    'AbandonRangeOnHit': True,
                },
                {
                    '$type': 'PMDC.Dungeon.ExplorePlan, PMDC',
                    'IQ': 253 if is_leader else 228,
                    'RestrictedMobilityTypes': 0,
                    'RestrictMobilityPassable': False,
                    'AttackRange': 0,
                    'StatusRange': 0,
                    'SelfStatusRange': 0,
                    'AbandonRangeOnHit': True,
                },
                {
                    '$type': 'PMDC.Dungeon.WaitPlan, PMDC',
                    'IQ': 253 if is_leader else 228,
                    'RestrictedMobilityTypes': 0,
                    'RestrictMobilityPassable': False,
                    'AttackRange': 0,
                    'StatusRange': 0,
                    'SelfStatusRange': 0,
                    'AbandonRangeOnHit': True,
                },
            ],
        }

    def make_enemy(
        species: str, el1: str, el2: str, gender: int, lv: int,
        x: int, y: int, skills: list[tuple[str, int]], intrinsic: str,
        hp_bonus: int, def_bonus: int, mdef_bonus: int, role: str, nickname: str = ''
    ) -> dict:
        return {
            'Element1': el1,
            'Element2': el2,
            'TurnWait': 0,
            'TurnUsed': False,
            'movementSpeed': 0,
            'dead': False,
            'serializationLoc': {'X': x, 'Y': y},
            'serializationDir': 0,
            'ProxyName': '',
            'ProxySprite': {'Species': '', 'Form': -1, 'Skin': '', 'Gender': -1},
            'CurrentForm': {'Species': species, 'Form': 0, 'Skin': 'normal', 'Gender': gender},
            'ProxyAtk': -1,
            'ProxyDef': -1,
            'ProxyMAtk': -1,
            'ProxyMDef': -1,
            'ProxySpeed': -1,
            'Skills': [
                {'Element': {'SkillNum': sk, 'Charges': ch, 'Enabled': True, 'Sealed': False}, 'BackRef': i}
                for i, (sk, ch) in enumerate(skills)
            ],
            'Intrinsics': [{'Element': {'ID': intrinsic}, 'BackRef': 0}],
            'EquippedItem': {'ID': '', 'Cursed': False, 'HiddenValue': '', 'Amount': 0, 'Price': 0},
            'Absentee': False,
            'ChargeBoost': 0,
            'HP': 120 + hp_bonus,
            'HPRemainder': 0,
            'Fullness': 100,
            'FullnessRemainder': 0,
            'MaxFullness': 100,
            'StatusEffects': {},
            'MissChain': 0,
            'EXPMarked': False,
            'Tactic': tactic_boss(role),
            'Mobility': 0,
            'CantWalk': False,
            'ItemDisabled': False,
            'IntrinsicDisabled': False,
            'CanRemoveStuck': False,
            'StopItemAtHit': False,
            'ForceAI': False,
            'MovesScrambled': False,
            'ChargeSaver': False,
            'WaitToAttack': False,
            'CantInteract': False,
            'EnemyOfFriend': False,
            'AttackFriend': False,
            'TileSight': -1,
            'CharSight': -1,
            'Unidentifiable': False,
            'Unlocatable': False,
            'SeeAllChars': False,
            'SeeItems': False,
            'SeeWallItems': False,
            'SeeTraps': False,
            'CharStates': [],
            'BackRef': {'Index': -1},
            'Nickname': nickname,
            'OriginalUUID': '',
            'OriginalTeam': '',
            'BaseForm': {'Species': species, 'Form': 0, 'Skin': 'normal', 'Gender': gender},
            'Level': lv,
            'EXP': 0,
            'MaxHPBonus': hp_bonus,
            'AtkBonus': 0,
            'DefBonus': def_bonus,
            'MAtkBonus': 0,
            'MDefBonus': mdef_bonus,
            'SpeedBonus': 0,
            'BaseSkills': [
                {'SkillNum': sk, 'Charges': ch, 'CanForget': True}
                for sk, ch in skills
            ],
            'BaseIntrinsics': [intrinsic],
            'FormIntrinsicSlot': -1,
            'Relearnables': {},
            'Discriminator': 0,
            'MetAt': '',
            'MetLoc': {'ID': '', 'StructID': {'Segment': -1, 'ID': -1}, 'EntryPoint': -1},
            'DefeatAt': '',
            'DefeatLoc': {'ID': '', 'StructID': {'Segment': -1, 'ID': -1}, 'EntryPoint': -1},
            'IsFounder': False,
            'IsPartner': False,
            'NameLocked': False,
            'IsFavorite': False,
            'Unrecruitable': True,
            'ActionEvents': [],
            'ScriptVars': None,
        }

    rsmap_doc = {
        'Version': '0.8.12.0',
        'Object': {
            '$type': 'RogueEssence.Dungeon.Map, RogueEssence',
            'Name': {'DefaultText': 'Grotte Verdoyante — Vasques', 'LocalTexts': {'fr': 'Grotte Verdoyante — Vasques'}},
            'Released': True,
            'Comment': 'Arène 9F de Grotte Verdoyante (calquée sur fgv1_fin_grotte_vasques en 32x24 tuiles).',
            'Begun': False,
            'ID': 0,
            'MapTeams': [{
                '$type': 'RogueEssence.Dungeon.ExplorerTeam, RogueEssence',
                'Rank': 'bronze',
                'Players': [
                    make_enemy('crawdaunt', 'water', 'dark', 1, 14, 16, 13,
                               [('bubble_beam', 16), ('pursuit', 16), ('vice_grip', 20), ('taunt', 14)],
                               'shell_armor', 65, 5, 5, 'boss'),
                    make_enemy('corphish', 'water', 'none', 1, 10, 14, 14,
                               [('bubble', 22), ('vice_grip', 22), ('leer', 20), ('harden', 20)],
                               'hyper_cutter', 18, 0, 0, 'normal'),
                    make_enemy('corphish', 'water', 'none', 2, 10, 18, 14,
                               [('bubble', 22), ('vice_grip', 22), ('leer', 20), ('harden', 20)],
                               'shell_armor', 18, 0, 0, 'normal'),
                    make_enemy('masquerain', 'bug', 'flying', 2, 11, 16, 11,
                               [('water_gun', 20), ('quick_attack', 22), ('gust', 20), ('scary_face', 18)],
                               'unnerve', 22, 0, 0, 'normal'),
                ],
                'TeamName': {'DefaultText': 'Bande des Vasques', 'LocalTexts': {'fr': 'Bande des Vasques'}},
                'RankExtra': 0,
                'Fame': 0,
                'Bank': 0,
                'MaxInv': 0,
                'Storage': {},
                'BoxStorage': {},
                'Assembly': [],
                'LeaderIndex': 0,
            }],
            'AllyTeams': [],
            'rand': {'$type': 'RogueElements.ReRandom, RogueElements', 'FirstSeed': 0, 's': [16294208416658607535, 7960286522194355700, 487617019471545679, 17909611376780542444]},
            'AssetName': 'end_grotte_verdoyante',
            'ScriptEvents': {},
            'Music': 'Boss Battle 2.ogg',
            'TileSight': 0,
            'CharSight': 0,
            'Status': {},
            'MapEffect': {
                'UniversalStates': [],
                'BeforeTryActions': [],
                'BeforeActions': [],
                'OnActions': [],
                'BeforeExplosions': [],
                'BeforeHits': [],
                'OnHits': [],
                'OnHitTiles': [],
                'AfterActions': [],
                'ElementEffects': [],
                'OnEquips': [],
                'OnPickups': [],
                'BeforeStatusAdds': [],
                'OnStatusAdds': [],
                'OnStatusRemoves': [],
                'OnMapStatusAdds': [],
                'OnMapStatusRemoves': [],
                'OnMapStarts': [
                    {
                        'Key': {'str': [-15]},
                        'Value': {
                            '$type': 'PMDC.Dungeon.BattlePositionEvent, PMDC',
                            'StartLocs': [
                                {'Loc': {'X': 0, 'Y': 0}, 'Dir': 4},
                                {'Loc': {'X': -1, 'Y': 0}, 'Dir': 4},
                                {'Loc': {'X': 1, 'Y': 0}, 'Dir': 4},
                                {'Loc': {'X': 0, 'Y': 1}, 'Dir': 4},
                            ],
                            'Positions': None,
                        },
                    },
                    {
                        'Key': {'str': [-5]},
                        'Value': {
                            '$type': 'PMDC.Dungeon.BeginBattleEvent, PMDC',
                            'CheckClearStatus': 'map_clear_check',
                        },
                    },
                ],
                'OnTurnStarts': [],
                'OnTurnEnds': [],
                'OnMapTurnEnds': [],
                'OnWalks': [],
                'OnDeaths': [],
                'OnRefresh': [],
                'OnMapRefresh': [],
                'ModifyHPs': [],
                'RestoreHPs': [],
                'InitActionData': [],
            },
            'TeamSpawns': {'$type': 'RogueElements.SpawnList`1[[RogueEssence.LevelGen.TeamSpawner, RogueEssence]], RogueEssence', '$values': []},
            'MoneyAmount': {'Amount': 0},
            'ItemSpawns': {'$type': 'RogueElements.SpawnList`1[[RogueEssence.LevelGen.InvItem, RogueEssence]], RogueEssence', '$values': []},
            'BlankBG': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1},
            'TextureMap': {},
            'Element': 'water',
            'Background': {
                '$type': 'RogueEssence.Dungeon.MapBG, RogueEssence',
                'MapLoc': {'X': 0, 'Y': 0},
                'BGAnim': {'AnimIndex': '', 'FrameTime': 1, 'StartFrame': -1, 'EndFrame': -1, 'AnimDir': -1, 'Alpha': 255, 'AnimFlip': 0},
                'BGMovement': {'X': 0, 'Y': 0},
                'Parallax': '0, 0',
                'RepeatX': False,
                'RepeatY': False,
            },
            'ViewCenter': None,
            'ViewOffset': {'X': 0, 'Y': 0},
            'HideMinimap': False,
            'NoRescue': True,
            'NoSwitching': False,
            'MapTurns': 0,
            'CurrentTurnMap': {'$type': 'RogueEssence.Dungeon.TurnOrderMap, RogueEssence', 'TurnToMap': []},
            'DiscoveryArray': [[0 for _ in range(MAP24_H)] for _ in range(MAP24_W)],
            'Layers': [{
                'Name': 'Vasques — base animée 24 px',
                'Layer': 0,
                'Visible': True,
                'Tiles': layer0_tiles,
            }],
            'Decorations': [],
            'Tiles': tiles_grid,
            'EdgeView': 1,
            'EntryPoints': [{'Loc': {'X': 16, 'Y': 18}, 'Dir': 4}],
            'Items': [],
        },
    }

    map_path = root / 'game/Data/Map/end_grotte_verdoyante.rsmap'
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(json.dumps(rsmap_doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'[OK] end_grotte_verdoyante.rsmap ({len(seen)} tuiles floor connectées) + FGV1_VASQUES_BASE_24.tile ({len(base24)} tuiles)')


def build_zone_grotte_verdoyante(root: Path, git_repo: Path) -> None:
    # Vérifier l'existence de tous les IDs de base référencés
    def base_set(subdir: str) -> set[str]:
        return {
            p.split('/')[-1].rsplit('.', 1)[0]
            for p in subprocess.check_output(['git', '-C', str(git_repo), 'ls-tree', '--name-only', 'HEAD', f'base/Data/{subdir}/']).decode().splitlines()
        }

    base_monsters = base_set('Monster')
    base_skills = base_set('Skill')
    base_intrs = base_set('Intrinsic')
    base_items = base_set('Item')
    base_tiles = base_set('Tile')
    base_autotiles = base_set('AutoTile')
    base_music = {
        p.split('/')[-1]
        for p in subprocess.check_output(['git', '-C', str(git_repo), 'ls-tree', '--name-only', 'HEAD', 'base/Content/Music/']).decode().splitlines()
    }

    def step_tile(tile_id: str) -> dict:
        assert tile_id in base_tiles, f'Tile inconnue: {tile_id}'
        return {'TileLoc': {'X': 0, 'Y': 0}, 'ID': tile_id, 'Revealed': True, 'Owner': 0, 'TileStates': []}

    def gen_floor(idx: int) -> dict:
        # Progression visuelle et structurelle sur 8 étages (1F..8F)
        if idx < 4:
            dtef = ('drenched_bluff_floor', 'drenched_bluff_wall', 'drenched_bluff_secondary', 'tall_grass', 'grass')
            music = 'Limestone Cavern.ogg'
        elif idx < 6:
            dtef = ('deep_limestone_cavern_floor', 'deep_limestone_cavern_wall', 'deep_limestone_cavern_secondary', 'tall_grass_dark', 'water')
            music = 'Lower Spring Cave.ogg'
        else:
            dtef = ('deep_limestone_cavern_floor', 'deep_limestone_cavern_wall', 'deep_limestone_cavern_secondary', 'tall_grass_dark', 'water')
            music = 'Deep Limestone Cavern.ogg'

        assert music in base_music, music
        for at in dtef[:4]:
            assert at in base_autotiles, at

        if idx < 2:
            cw, ch, cx, cy = 7, 7, 4, 4
            init_foes, max_foes, resp = 3 + idx, 10, 42
            water_pct, blobs_max, grass_pct = 10, 4, 18
        elif idx < 4:
            cw, ch, cx, cy = 7, 6, 5, 4
            init_foes, max_foes, resp = 4 + (idx - 2), 12, 36
            water_pct, blobs_max, grass_pct = 12, 5, 22
        elif idx < 6:
            cw, ch, cx, cy = 6, 6, 5, 5
            init_foes, max_foes, resp = 5, 13, 34
            water_pct, blobs_max, grass_pct = 14, 6, 18
        else:
            cw, ch, cx, cy = 6, 6, 6, 5
            init_foes, max_foes, resp = 6, 14, 30
            water_pct, blobs_max, grass_pct = 16, 7, 16

        # Diversité topologique : 1F-2F/6F-7F ramifications naturelles, 3F-4F/8F deux versants, 5F boucle
        generic_rooms = {
            '$type': 'RogueElements.SpawnList`1[[RogueElements.RoomGen`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements]], RogueElements',
            '$values': [
                {
                    'Spawn': {
                        '$type': 'RogueElements.RoomGenBump`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'Width': {'Min': 3, 'Max': 6},
                        'Height': {'Min': 3, 'Max': 6},
                        'BumpPercent': {'Min': 45, 'Max': 55},
                    },
                    'Rate': 10,
                },
                {
                    'Spawn': {
                        '$type': 'RogueElements.RoomGenCave`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'Width': {'Min': 4, 'Max': 6},
                        'Height': {'Min': 4, 'Max': 6},
                    },
                    'Rate': 12,
                },
            ],
        }
        generic_halls = {
            '$type': 'RogueElements.SpawnList`1[[RogueElements.PermissiveRoomGen`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements]], RogueElements',
            '$values': [{
                'Spawn': {
                    '$type': 'RogueElements.RoomGenAngledHall`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'HallTurnBias': 50,
                    'Brush': {'$type': 'RogueElements.DefaultHallBrush, RogueElements'},
                    'Width': {'Min': 0, 'Max': 0},
                    'Height': {'Min': 0, 'Max': 0},
                },
                'Rate': 10,
            }],
        }
        conn_comp = [{'$type': 'PMDC.LevelGen.ConnectivityRoom, PMDC', 'Connection': 1}]

        steps = [
            {
                'Key': {'str': [-6]},
                'Value': {
                    '$type': 'PMDC.LevelGen.MapDataStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], PMDC',
                    'Music': music,
                    'TimeLimit': 1500,
                    'TileSight': 0,
                    'CharSight': 1,
                    'ClampCamera': False,
                },
            },
            {
                'Key': {'str': [-5]},
                'Value': {
                    '$type': 'RogueElements.InitGridPlanStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'CellWidth': cw,
                    'CellHeight': ch,
                    'CellX': cx,
                    'CellY': cy,
                    'CellWall': 1,
                    'Wrap': False,
                },
            },
        ]

        if idx in (2, 3, 7):
            steps.append({
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.GridPathTwoSides`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'GapAxis': 1,
                    'GenericRooms': generic_rooms,
                    'RoomComponents': conn_comp,
                    'GenericHalls': generic_halls,
                    'HallComponents': conn_comp,
                },
            })
            steps.append({
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.ConnectGridBranchStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'ConnectPercent': 75,
                    'Filters': [{'$type': 'RogueElements.RoomFilterComponent, RogueElements', 'Negate': True, 'Components': [{'$type': 'RogueEssence.LevelGen.ImmutableRoom, RogueEssence'}]}],
                    'GenericHalls': generic_halls,
                    'HallComponents': conn_comp,
                },
            })
        elif idx == 4:
            steps.append({
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.GridPathCircle`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'CircleRoomRatio': {'Min': 75, 'Max': 85},
                    'Paths': {'Min': 2, 'Max': 3},
                    'GenericRooms': generic_rooms,
                    'RoomComponents': conn_comp,
                    'GenericHalls': generic_halls,
                    'HallComponents': conn_comp,
                },
            })
        else:
            steps.append({
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.GridPathBranch`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'RoomRatio': {'Min': 80, 'Max': 85},
                    'BranchRatio': {'Min': 10, 'Max': 40},
                    'NoForcedBranches': False,
                    'GenericRooms': generic_rooms,
                    'RoomComponents': conn_comp,
                    'GenericHalls': generic_halls,
                    'HallComponents': conn_comp,
                },
            })

        steps.extend([
            {
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueEssence.LevelGen.CombineGridRoomStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence',
                    'MergeRate': {'Min': 2, 'Max': 5},
                    'Filters': [
                        {'$type': 'RogueElements.RoomFilterComponent, RogueElements', 'Negate': True, 'Components': [{'$type': 'RogueEssence.LevelGen.ImmutableRoom, RogueEssence'}]},
                        {'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1},
                        {'$type': 'RogueElements.RoomFilterDefaultGen, RogueElements', 'Negate': True},
                    ],
                    'RoomComponents': conn_comp,
                    'Combos': [
                        {
                            'Spawn': {
                                'Size': {'X': 2, 'Y': 2},
                                'GiantRoom': {
                                    '$type': 'RogueElements.RoomGenCave`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                                    'Width': {'Min': 9, 'Max': 12},
                                    'Height': {'Min': 9, 'Max': 12},
                                },
                            },
                            'Rate': 10,
                        },
                        {
                            'Spawn': {
                                'Size': {'X': 2, 'Y': 1},
                                'GiantRoom': {
                                    '$type': 'RogueElements.RoomGenCave`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                                    'Width': {'Min': 9, 'Max': 12},
                                    'Height': {'Min': 5, 'Max': 6},
                                },
                            },
                            'Rate': 10,
                        },
                    ],
                },
            },
            {'Key': {'str': [-3]}, 'Value': {'$type': 'RogueElements.DrawGridToFloorStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements'}},
            {'Key': {'str': [-1]}, 'Value': {'$type': 'RogueElements.DrawFloorToTileStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Padding': 1}},
            {'Key': {'str': [0, 1]}, 'Value': {'$type': 'RogueEssence.LevelGen.UnbreakableBorderStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence', 'Thickness': 1}},
            {
                'Key': {'str': [0, 3]},
                'Value': {
                    '$type': 'RogueEssence.AddTunnelStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'TurnLength': {'Min': 3, 'Max': 7},
                    'MaxLength': {'Min': 22, 'Max': 22},
                    'AllowDeadEnd': False,
                    'TraverseFloor': False,
                    'Halls': {'Min': 10, 'Max': 16},
                    'Brush': {'$type': 'RogueElements.DefaultHallBrush, RogueElements'},
                },
            },
            {
                'Key': {'str': [1, 2]},
                'Value': {
                    '$type': 'PMDC.LevelGen.MobSpawnSettingsStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], PMDC',
                    'Priority': {'str': [15]},
                    'Respawn': {'$type': 'PMDC.Dungeon.RespawnFromEligibleEvent, PMDC', 'MaxFoes': max_foes, 'RespawnTime': resp},
                    'MaxFoes': 0,
                    'RespawnTime': 0,
                },
            },
            {
                'Key': {'str': [2]},
                'Value': {
                    '$type': 'RogueElements.FloorStairsStep`3[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.LevelGen.MapGenEntrance, RogueEssence],[RogueEssence.LevelGen.MapGenExit, RogueEssence]], RogueElements',
                    'MinDistance': 3,
                    'Entrances': [{'Loc': {'X': 0, 'Y': 0}, 'Dir': 0}],
                    'Exits': [{'Loc': {'X': 0, 'Y': 0}, 'Tile': step_tile('stairs_go_down')}],
                    'Filters': [
                        {'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1},
                        {'$type': 'RogueElements.RoomFilterComponent, RogueElements', 'Negate': True, 'Components': [{'$type': 'PMDC.LevelGen.BossRoom, PMDC'}]},
                    ],
                },
            },
            {
                'Key': {'str': [3]},
                'Value': {
                    '$type': 'RogueElements.PerlinWaterStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'OrderComplexity': 3,
                    'OrderSoftness': 1,
                    'WaterPercent': {'Min': water_pct, 'Max': water_pct},
                    'Bowl': True,
                    'Terrain': {
                        '$type': 'RogueEssence.Dungeon.Tile, RogueEssence',
                        'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False},
                        'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
                    },
                    'TerrainStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': False, 'Wall': True, 'Blocked': False, 'Not': False},
                },
            },
            {
                'Key': {'str': [3]},
                'Value': {
                    '$type': 'RogueElements.BlobWaterStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Blobs': {'Min': 2, 'Max': blobs_max},
                    'GenerateScale': {'Min': 5, 'Max': 12},
                    'AreaScale': {'Min': 2, 'Max': 5},
                    'BlobStencil': {
                        '$type': 'RogueElements.BlobTilePercentStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'TileStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': False, 'Wall': False, 'Blocked': True, 'Not': True},
                        'Percent': 50,
                    },
                    'Terrain': {
                        '$type': 'RogueEssence.Dungeon.Tile, RogueEssence',
                        'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False},
                        'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
                    },
                    'TerrainStencil': {
                        '$type': 'RogueElements.MultiTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'List': [
                            {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False},
                            {'$type': 'RogueElements.NoChokepointTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'TileStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False}, 'Global': False, 'Negate': True},
                            {'$type': 'RogueEssence.LevelGen.TileEffectStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence', 'Not': True},
                        ],
                        'RequireAny': False,
                    },
                },
            },
            {
                'Key': {'str': [3]},
                'Value': {
                    '$type': 'RogueElements.PerlinWaterStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'OrderComplexity': 4,
                    'OrderSoftness': 0,
                    'WaterPercent': {'Min': grass_pct, 'Max': grass_pct},
                    'Bowl': False,
                    'Terrain': {
                        '$type': 'RogueEssence.Dungeon.Tile, RogueEssence',
                        'Data': {'ID': 'grass', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False},
                        'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
                    },
                    'TerrainStencil': {
                        '$type': 'RogueElements.MultiTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'List': [
                            {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False},
                            {'$type': 'RogueElements.NoChokepointTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'TileStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False}, 'Global': False, 'Negate': True},
                            {'$type': 'RogueEssence.LevelGen.TileEffectStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence', 'Not': True},
                        ],
                        'RequireAny': False,
                    },
                },
            },
            {
                'Key': {'str': [3, 1]},
                'Value': {
                    '$type': 'RogueElements.DropDiagonalBlockStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Terrain': {
                        '$type': 'RogueEssence.Dungeon.Tile, RogueEssence',
                        'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False},
                        'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
                    },
                },
            },
            {
                'Key': {'str': [3, 2]},
                'Value': {
                    '$type': 'RogueElements.EraseIsolatedStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Terrain': {
                        '$type': 'RogueEssence.Dungeon.Tile, RogueEssence',
                        'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False},
                        'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []},
                    },
                },
            },
            {
                'Key': {'str': [4]},
                'Value': {
                    '$type': 'RogueEssence.LevelGen.MapDictTextureStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence',
                    'TextureMap': {
                        'floor': dtef[0],
                        'wall': dtef[1],
                        'unbreakable': dtef[1],
                        'water': dtef[2],
                        'lava': dtef[2],
                        'pit': dtef[2],
                        'water_poison': dtef[2],
                        'grass': dtef[3],
                    },
                    'BlankBG': dtef[1],
                    'LayeredGround': True,
                    'IndependentGround': False,
                    'GroundElement': dtef[4],
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'PMDC.LevelGen.SpacedRoomSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], PMDC',
                    'IncludeHalls': False,
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'Spawn': {
                        '$type': 'RogueElements.PickerSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                        'Picker': {
                            '$type': 'RogueElements.LoopedRand`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                            'Spawner': {
                                '$type': 'RogueElements.SpawnList`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                                '$values': [{'Spawn': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': 'tile_wonder', 'Revealed': True, 'Owner': 0, 'TileStates': []}, 'Rate': 10}],
                            },
                            'AmountSpawner': {'$type': 'RogueElements.RandRange, RogueElements', 'Min': 1, 'Max': 2},
                        },
                    },
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'RogueElements.RandomRoomSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                    'SuccessPercent': 100,
                    'IncludeHalls': False,
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'Spawn': {'$type': 'RogueElements.ContextSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements', 'Amount': {'Min': 3 + idx // 2, 'Max': 6 + idx // 2}},
                },
            },
            {
                'Key': {'str': [6]},
                'Value': {
                    '$type': 'RogueElements.TerminalSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.LevelGen.MoneySpawn, RogueEssence]], RogueElements',
                    'IncludeHalls': False,
                    'Filters': [],
                    'Spawn': {'$type': 'RogueEssence.LevelGen.MoneyDivSpawner`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence', 'DivAmount': {'Min': 2, 'Max': 4}},
                },
            },
            {
                'Key': {'str': [6, 1]},
                'Value': {
                    '$type': 'RogueElements.DueSpawnStep`3[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.InvItem, RogueEssence],[RogueEssence.LevelGen.MapGenEntrance, RogueEssence]], RogueElements',
                    'SuccessPercent': 25,
                    'IncludeHalls': False,
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'Spawn': {'$type': 'RogueElements.ContextSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.InvItem, RogueEssence]], RogueElements', 'Amount': {'Min': 3, 'Max': 6}},
                },
            },
            {
                'Key': {'str': [6, 2]},
                'Value': {
                    '$type': 'RogueEssence.LevelGen.PlaceRandomMobsStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'IncludeHalls': False,
                    'Spawn': {'$type': 'RogueEssence.LevelGen.TeamContextSpawner`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Amount': {'Min': init_foes, 'Max': init_foes + 2}},
                    'Ally': False,
                    'ClumpFactor': 15,
                },
            },
            {
                'Key': {'str': [7]},
                'Value': {'$type': 'RogueElements.DetectIsolatedStairsStep`3[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.LevelGen.MapGenEntrance, RogueEssence],[RogueEssence.LevelGen.MapGenExit, RogueEssence]], RogueElements'},
            },
        ])

        return {'$type': 'RogueEssence.LevelGen.GridFloorGen, RogueEssence', 'GenSteps': steps}

    def mob_entry(species: str, lv_min: int, lv_max: int, skills: list[str], intrinsic: str, rmin: int, rmax: int, rate: int = 10, role: int = 0) -> dict:
        assert species in base_monsters, species
        for sk in skills:
            assert sk in base_skills, sk
        assert intrinsic == '' or intrinsic in base_intrs, intrinsic
        return {
            'Spawn': {
                'Spawn': {
                    'BaseForm': {'Species': species, 'Form': 0, 'Skin': '', 'Gender': -1},
                    'Level': {'Min': lv_min, 'Max': lv_max},
                    'SpecifiedSkills': skills,
                    'Intrinsic': intrinsic,
                    'Tactic': 'wander_dumb',
                    'SpawnConditions': [],
                    'SpawnFeatures': [
                        {'$type': 'PMDC.LevelGen.MobSpawnWeak, PMDC'},
                        {'$type': 'PMDC.LevelGen.MobSpawnMovesOff, PMDC', 'StartAt': 2, 'Remove': False},
                    ],
                },
                'Role': role,
            },
            'Rate': rate,
            'Range': {'Min': rmin, 'Max': rmax},
        }

    def item_entry(item_id: str, rate: int, rmin: int = 0, rmax: int = 8) -> dict:
        assert item_id in base_items, f'Item inconnu: {item_id}'
        return {
            'Spawn': {'ID': item_id, 'Cursed': False, 'HiddenValue': '', 'Amount': 0, 'Price': 0},
            'Rate': rate,
            'Range': {'Min': rmin, 'Max': rmax},
        }

    def spread_item(item_id: str, min_sp: int, max_sp: int) -> dict:
        assert item_id in base_items, item_id
        return {
            '$type': 'RogueEssence.LevelGen.SpreadStepZoneStep, RogueEssence',
            'StepPriority': {'str': [6, 1]},
            'Spawns': {
                '$type': 'RogueElements.SpawnList`1[[RogueElements.IGenStep, RogueElements]], RogueElements',
                '$values': [{
                    'Spawn': {
                        '$type': 'RogueElements.RandomSpawnStep`2[[RogueEssence.LevelGen.ListMapGenContext, RogueEssence],[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                        'Spawn': {
                            '$type': 'RogueElements.PickerSpawner`2[[RogueEssence.LevelGen.ListMapGenContext, RogueEssence],[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                            'Picker': {
                                '$type': 'RogueElements.PresetMultiRand`1[[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                                'ToSpawn': [{
                                    '$type': 'RogueElements.PresetPicker`1[[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                                    'ToSpawn': {'IsMoney': False, 'Cursed': False, 'Value': item_id, 'HiddenValue': '', 'Amount': 0, 'Price': 0, 'TileLoc': {'X': 0, 'Y': 0}},
                                }],
                            },
                        },
                    },
                    'Rate': 10,
                }],
            },
            'SpreadPlan': {
                '$type': 'RogueEssence.LevelGen.SpreadPlanSpaced, RogueEssence',
                'FloorSpacing': {'Min': min_sp, 'Max': max_sp},
                'BeginStart': False,
                'FloorRange': {'Min': 0, 'Max': 8},
            },
            'ModStates': [],
        }

    def trap_entry(tile_id: str, rate: int, rmin: int = 0, rmax: int = 8, revealed: bool = False) -> dict:
        assert tile_id in base_tiles, tile_id
        return {
            'Spawn': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': tile_id, 'Revealed': revealed, 'Owner': 0, 'TileStates': []},
            'Rate': rate,
            'Range': {'Min': rmin, 'Max': rmax},
        }

    zone_steps_s0 = [
        {'$type': 'PMDC.LevelGen.SaveVarsZoneStep, PMDC', 'Priority': {'str': [2, 1]}},
        {
            '$type': 'PMDC.LevelGen.FloorNameDropZoneStep, PMDC',
            'DropPriority': {'str': [-15]},
            'Name': {'DefaultText': 'Grotte Verdoyante\n{0}F', 'LocalTexts': {'fr': 'Grotte Verdoyante\n{0}F'}},
            'Priority': {'str': [-6]},
        },
        {
            '$type': 'RogueEssence.LevelGen.MoneySpawnZoneStep, RogueEssence',
            'Priority': {'str': [1]},
            'StartAmount': {'Min': 95, 'Max': 125},
            'AddAmount': {'Min': 10, 'Max': 15},
            'ModStates': [{'assembly': 'PMDC, Version=0.8.11.0, Culture=neutral, PublicKeyToken=null', 'type': 'PMDC.Dungeon.CoinModGenState'}],
        },
        {
            '$type': 'RogueEssence.LevelGen.ItemSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 1]},
            'Spawns': {
                'necessities': {
                    'Spawns': [
                        item_entry('berry_oran', 16),
                        item_entry('food_apple', 14),
                        item_entry('berry_leppa', 10),
                        item_entry('berry_pecha', 10),
                        item_entry('berry_cheri', 8),
                        item_entry('berry_lum', 12),
                        item_entry('food_apple_big', 6, 3, 8),
                        item_entry('seed_reviver', 5),
                    ],
                },
                'snacks': {
                    'Spawns': [
                        item_entry('seed_blast', 12),
                        item_entry('seed_sleep', 10),
                        item_entry('seed_warp', 10),
                        item_entry('berry_sitrus', 4, 4, 8),
                    ],
                },
                'boosters': {
                    'Spawns': [
                        item_entry('gummi_blue', 8),
                        item_entry('gummi_grass', 8),
                        item_entry('gummi_green', 8),
                        item_entry('gummi_royal', 2, 5, 8),
                    ],
                },
                'throwable': {
                    'Spawns': [
                        item_entry('ammo_geo_pebble', 12),
                        item_entry('ammo_gravelerock', 8, 2, 8),
                        item_entry('ammo_stick', 10),
                        item_entry('wand_lob', 8),
                        item_entry('wand_pounce', 8),
                    ],
                },
                'orbs': {
                    'Spawns': [
                        item_entry('orb_escape', 8),
                        item_entry('orb_cleanse', 8),
                        item_entry('orb_luminous', 8),
                        item_entry('orb_totter', 8),
                        item_entry('orb_slumber', 8),
                    ],
                },
                'tms': {
                    'Spawns': [
                        item_entry('tm_water_pulse', 3, 4, 8),
                        item_entry('tm_giga_drain', 3, 4, 8),
                    ],
                },
            },
        },
        {
            '$type': 'RogueEssence.LevelGen.TeamSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 2]},
            'Spawns': [
                mob_entry('lotad', 8, 9, ['astonish', 'water_gun', 'absorb', 'growl'], 'rain_dish', 0, 4, 12),
                mob_entry('shroomish', 8, 9, ['absorb', 'tackle', 'stun_spore'], 'effect_spore', 0, 4, 12),
                mob_entry('budew', 8, 9, ['absorb', 'growth', 'stun_spore', 'mega_drain'], 'natural_cure', 0, 4, 10),
                mob_entry('zubat', 8, 9, ['leech_life', 'astonish', 'supersonic', 'bite'], 'inner_focus', 0, 5, 10),
                mob_entry('wooper', 8, 9, ['water_gun', 'mud_shot', 'tail_whip'], 'damp', 0, 4, 11),
                mob_entry('surskit', 8, 9, ['bubble', 'quick_attack'], 'swift_swim', 0, 4, 9),
                mob_entry('buizel', 9, 10, ['quick_attack', 'water_gun', 'aqua_jet', 'pursuit'], 'swift_swim', 2, 6, 10),
                mob_entry('shellos', 9, 10, ['mud_slap', 'water_pulse', 'harden'], 'sticky_hold', 2, 6, 10),
                mob_entry('spinarak', 9, 10, ['poison_sting', 'string_shot', 'bug_bite', 'scary_face'], 'swarm', 2, 6, 9),
                mob_entry('corphish', 10, 11, ['bubble', 'vice_grip', 'harden', 'leer'], 'hyper_cutter', 3, 8, 10),
                mob_entry('morelull', 10, 11, ['absorb', 'moonlight', 'stun_spore'], 'illuminate', 3, 8, 9),
                mob_entry('dewpider', 10, 11, ['bubble', 'bug_bite', 'bite'], 'water_bubble', 3, 8, 9),
                mob_entry('lombre', 11, 12, ['bubble_beam', 'mega_drain', 'fake_out', 'astonish'], 'rain_dish', 4, 8, 9),
                mob_entry('croagunk', 11, 12, ['poison_sting', 'mud_slap', 'feint_attack', 'taunt'], 'dry_skin', 4, 8, 9),
                mob_entry('fomantis', 11, 12, ['leafage', 'razor_leaf', 'fury_cutter'], 'leaf_guard', 4, 8, 9),
                mob_entry('golbat', 11, 12, ['wing_attack', 'bite', 'confuse_ray', 'astonish'], 'inner_focus', 5, 8, 8),
                mob_entry('barboach', 11, 12, ['mud_bomb', 'water_gun', 'water_pulse'], 'oblivious', 5, 8, 9),
                mob_entry('yanma', 11, 12, ['quick_attack', 'wing_attack', 'supersonic'], 'speed_boost', 5, 8, 8),
            ],
        },
        spread_item('food_apple', 2, 4),
        spread_item('berry_oran', 2, 4),
        spread_item('berry_leppa', 3, 6),
        {
            '$type': 'RogueEssence.LevelGen.TileSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 3]},
            'Spawns': [
                trap_entry('trap_trip', 10, 0, 8, True),
                trap_entry('trap_mud', 10, 1, 8, False),
                trap_entry('trap_slow', 9, 2, 8, False),
                trap_entry('trap_poison', 8, 3, 8, False),
                trap_entry('trap_slumber', 6, 4, 8, False),
            ],
        },
        {
            '$type': 'RogueEssence.LevelGen.SpreadStepRangeZoneStep, RogueEssence',
            'StepPriority': {'str': [5]},
            'Spawns': [{
                'Spawn': {
                    '$type': 'RogueEssence.LevelGen.ScriptGenStep`1[[RogueEssence.LevelGen.ListMapGenContext, RogueEssence]], RogueEssence',
                    'Script': 'Mysteriosity',
                    'ArgTable': '{BaseChance=5, SegDiff=2}',
                },
                'Rate': 10,
                'Range': {'Min': 0, 'Max': 8},
            }],
            'SpreadPlan': {
                '$type': 'RogueEssence.LevelGen.SpreadPlanSpaced, RogueEssence',
                'FloorSpacing': {'Min': 3, 'Max': 5},
                'BeginStart': False,
                'FloorRange': {'Min': 0, 'Max': 8},
            },
            'ModStates': [],
        },
    ]

    segment0 = {
        '$type': 'RogueEssence.LevelGen.LayeredSegment, RogueEssence',
        'Floors': [gen_floor(i) for i in range(8)],
        'ZoneSteps': zone_steps_s0,
        'IsRelevant': True,
        'Comment': 'Étages 1F à 8F de la Grotte Verdoyante — DTEF drenched_bluff (1F-4F) puis deep_limestone_cavern (5F-8F).',
    }

    segment1 = {
        '$type': 'RogueEssence.LevelGen.LayeredSegment, RogueEssence',
        'Floors': [{
            '$type': 'RogueEssence.LevelGen.LoadGen, RogueEssence',
            'GenSteps': [
                {
                    'Key': {'str': [-7]},
                    'Value': {
                        '$type': 'RogueEssence.LevelGen.MappedRoomStep`1[[RogueEssence.LevelGen.MapLoadContext, RogueEssence]], RogueEssence',
                        'MapID': 'end_grotte_verdoyante',
                    },
                },
                {
                    'Key': {'str': [-6]},
                    'Value': {
                        '$type': 'RogueEssence.LevelGen.MapEffectStep`1[[RogueEssence.LevelGen.MapLoadContext, RogueEssence]], RogueEssence',
                        'Effect': {
                            'UniversalStates': [],
                            'BeforeTryActions': [],
                            'BeforeActions': [],
                            'OnActions': [],
                            'BeforeExplosions': [],
                            'BeforeHits': [],
                            'OnHits': [],
                            'OnHitTiles': [],
                            'AfterActions': [],
                            'ElementEffects': [],
                            'OnEquips': [],
                            'OnPickups': [],
                            'BeforeStatusAdds': [],
                            'OnStatusAdds': [],
                            'OnStatusRemoves': [],
                            'OnMapStatusAdds': [],
                            'OnMapStatusRemoves': [],
                            'OnMapStarts': [],
                            'OnTurnStarts': [],
                            'OnTurnEnds': [],
                            'OnMapTurnEnds': [],
                            'OnWalks': [],
                            'OnDeaths': [],
                            'OnRefresh': [],
                            'OnMapRefresh': [{'Key': {'str': [0]}, 'Value': {'$type': 'PMDC.Dungeon.MapNoRescueEvent, PMDC'}}],
                            'ModifyHPs': [],
                            'RestoreHPs': [],
                            'InitActionData': [],
                        },
                    },
                },
            ],
            'Comment': 'Combat de boss 9F sur end_grotte_verdoyante (arène des vasques).',
        }],
        'ZoneSteps': [
            {'$type': 'PMDC.LevelGen.SaveVarsZoneStep, PMDC', 'Priority': {'str': [2, 1]}},
            {
                '$type': 'PMDC.LevelGen.FloorNameDropZoneStep, PMDC',
                'DropPriority': {'str': [-15]},
                'Name': {'DefaultText': 'Grotte Verdoyante — Vasques\n9F', 'LocalTexts': {'fr': 'Grotte Verdoyante — Vasques\n9F'}},
                'Priority': {'str': [-6]},
            },
        ],
        'IsRelevant': True,
        'Comment': '9e étage : salle des vasques contre la Bande des Vasques (Colhomard).',
    }

    zone_doc = {
        'Version': '0.8.12.0',
        'Object': {
            '$type': 'RogueEssence.Data.ZoneData, RogueEssence',
            'Name': {'DefaultText': 'Grotte Verdoyante', 'LocalTexts': {'fr': 'Grotte Verdoyante'}},
            'Released': True,
            'Comment': 'Grotte Verdoyante (9 étages) — sauvetage de Nilo derrière la cascade (ewc3 -> 1F-8F -> fgv1/boss 9F).',
            'NoEXP': False,
            'ExpPercent': 100,
            'Level': 10,
            'LevelCap': False,
            'KeepSkills': False,
            'TeamRestrict': False,
            'TeamSize': -1,
            'MoneyRestrict': False,
            'BagRestrict': -1,
            'KeepTreasure': False,
            'BagSize': -1,
            'Persistent': False,
            'Rescues': 2,
            'Rogue': 1,
            'Segments': [segment0, segment1],
            'GroundMaps': ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques'],
        },
    }

    zpath = root / 'game/Data/Zone/grotte_verdoyante.json'
    zpath.write_text(json.dumps(zone_doc, ensure_ascii=False, indent=2), encoding='utf-8')

    idx_path = root / 'game/Data/Zone/index.idx'
    idx_doc = json.loads(idx_path.read_text(encoding='utf-8-sig'))
    idx_doc['Object']['grotte_verdoyante'] = {
        '$type': 'RogueEssence.Data.ZoneEntrySummary, RogueEssence',
        'ExpPercent': 100,
        'Level': 10,
        'LevelCap': False,
        'KeepSkills': False,
        'TeamRestrict': False,
        'TeamSize': -1,
        'MoneyRestrict': False,
        'BagRestrict': -1,
        'KeepTreasure': False,
        'BagSize': -1,
        'Rescues': 2,
        'CountedFloors': 9,
        'Rogue': 1,
        'Grounds': ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques'],
        'Maps': [[0, 1, 2, 3, 4, 5, 6, 7], [0]],
        'Name': {'DefaultText': 'Grotte Verdoyante', 'LocalTexts': {'fr': 'Grotte Verdoyante'}},
        'Released': True,
        'Comment': 'Grotte Verdoyante (9 étages) : entrée ewc3_entree_waterfall_cave, 1F-8F DTEF drenched_bluff/deep_limestone_cavern, 9F boss et sauvetage de Nilo sur fgv1_fin_grotte_vasques.',
        'SortOrder': 32,
    }
    idx_path.write_text(json.dumps(idx_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('[OK] grotte_verdoyante.json + Zone/index.idx mis à jour (9 étages)')


def main() -> int:
    root = DEFAULT_WT
    git_repo = DEFAULT_GIT
    args = sys.argv[1:]
    if '--root' in args:
        root = Path(args[args.index('--root') + 1])
    if '--git-repo' in args:
        git_repo = Path(args[args.index('--git-repo') + 1])

    ewc3_doc, _ = remap_ground_from_eeba71b4(
        root, git_repo, 'ewc3_entree_waterfall_cave',
        'Grotte Verdoyante — Entrée', 'Grotte Verdoyante — Entrée',
    )
    (root / 'game/Data/Ground').mkdir(parents=True, exist_ok=True)
    (root / 'game/Data/Ground/ewc3_entree_waterfall_cave.rsground').write_text(
        json.dumps(ewc3_doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
    )

    fgv1_doc, fgv1_decoded = remap_ground_from_eeba71b4(
        root, git_repo, 'fgv1_fin_grotte_vasques',
        'Grotte Verdoyante — Vasques\n9F', 'Grotte Verdoyante — Vasques\n9F',
    )
    (root / 'game/Data/Ground/fgv1_fin_grotte_vasques.rsground').write_text(
        json.dumps(fgv1_doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
    )

    build_fgv1_battle_map_and_tiles(root, fgv1_doc, fgv1_decoded)
    build_zone_grotte_verdoyante(root, git_repo)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
