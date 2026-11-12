#!/usr/bin/env python3
"""Construit Plage Sablefin (4 ambiances Réverie) et le donjon Passage Aquatique (10 étages + map de fin) :

1. game/Content/Tile/Destiny_Plage_Sablefin_{Jour,Aube,Crepuscule,Nuit}.tile
   (tuiles 8x8 dédupliquées, 34 phases d'écume/vagues sans mixels, LUT Aube/Crépuscule/Nuit + ciel dégradé)
2. game/Data/Ground/plage_sablefin_{jour,aube,crepuscule,nuit}.rsground (88x59 tuiles 8px = 704x472)
3. game/Data/Ground/passage_aquatique_fond.rsground (19x20 tuiles 24px = 456x480, BeachCavePit 23 phases, collisions 57x60)
4. game/Data/Zone/passage_aquatique.json (1F-3F beach_cave, 4F-6F craggy_coast, 7F-8F brine_cave, 9F-10F lower_brine_cave)
5. game/Data/Zone/index.idx + game/Content/Tile/index.idx

Dépendances CI uniquement : stdlib + Pillow (aucun numpy/scipy).
"""

from __future__ import annotations

import hashlib
import io
import json
import struct
import subprocess
import sys
import zipfile
from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw

DEFAULT_WT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = Path('/home/user/beach_layers_v1_sans_mixels.zip')

BEACH_TW, BEACH_TH = 88, 59
BEACH_W, BEACH_H = BEACH_TW * 8, BEACH_TH * 8  # 704 x 472
FRAME_COUNT = 34
WAVE_FRAME_LENGTH = 4  # 4 ticks (~66.7 ms), fidèle au rythme 70 ms validé

# Multiplicateurs exacts de GroundMap.cs (WorldAmbianceTint)
AMBIANCES = (
    ('jour', 'Jour', (255, 255, 255), 'Surrounded Sea.ogg'),
    ('aube', 'Aube', (224, 203, 212), 'On the Beach at Dusk.ogg'),
    ('crepuscule', 'Crepuscule', (179, 146, 173), 'On the Beach at Dusk.ogg'),
    ('nuit', 'Nuit', (97, 118, 159), 'At the End of the Day.ogg'),
)

# Les 4 bandes exactes de 01_ciel (Jour -> Aube / Crépuscule / Nuit calibrées sur FALAISE_PROMONTOIRE_*_CIEL)
SKY_BANDS_JOUR = (
    (141, 210, 249),
    (161, 225, 248),
    (180, 236, 246),
    (202, 243, 245),
)
SKY_MAPS = {
    'jour': {c: c for c in SKY_BANDS_JOUR},
    'aube': dict(zip(SKY_BANDS_JOUR, ((118, 144, 222), (147, 158, 207), (177, 172, 193), (206, 186, 178)))),
    'crepuscule': dict(zip(SKY_BANDS_JOUR, ((114, 98, 178), (155, 110, 151), (197, 122, 123), (238, 134, 96)))),
    'nuit': dict(zip(SKY_BANDS_JOUR, ((6, 14, 54), (13, 30, 78), (21, 46, 102), (28, 62, 126)))),
}


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
        if im.getchannel('A').getbbox() is None:
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
        ch = struct.pack('<q', len(blob)) + blob
        chunks.append(ch)
        cur += len(ch)
    with dest.open('wb') as f:
        f.write(struct.pack('<ii', tile_size, count))
        for (tx, ty, _), off in zip(items, offsets):
            f.write(struct.pack('<iiq', tx, ty, off))
        for ch in chunks:
            f.write(ch)


def load_tile_sheet(tile_dir: Path, sheet: str) -> tuple[int, dict[tuple[int, int], Image.Image]]:
    raw = (tile_dir / f'{sheet}.tile').read_bytes()
    ts, count = struct.unpack_from('<ii', raw, 0)
    out: dict[tuple[int, int], Image.Image] = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        ln = struct.unpack_from('<q', raw, off)[0]
        im = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert('RGBA')
        # unpremultiply si alpha partiel
        px = bytearray(im.tobytes())
        for k in range(0, len(px), 4):
            a = px[k + 3]
            if 0 < a < 255:
                px[k] = min(255, round(px[k] * 255.0 / a))
                px[k + 1] = min(255, round(px[k + 1] * 255.0 / a))
                px[k + 2] = min(255, round(px[k + 2] * 255.0 / a))
        out[(tx, ty)] = Image.frombytes('RGBA', im.size, bytes(px))
    return ts, out


def _make_trigger(name: str, x: int, y: int, w: int, h: int, trigger_type: int = 2, passable: bool = True) -> dict:
    return {
        'EntName': name,
        'Direction': 0,
        'EntEnabled': True,
        'EntOrder': 0,
        'InteractOrder': 0,
        'triggerType': trigger_type,
        'ObjectAnim': {
            '$type': 'RogueEssence.Content.ObjAnimData, RogueEssence',
            'AnimIndex': '', 'FrameTime': 1, 'StartFrame': -1, 'EndFrame': -1,
            'AnimDir': -1, 'Alpha': 255, 'AnimFlip': 0,
        },
        'Passable': passable,
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


def _make_marker(name: str, x: int, y: int, direction: int) -> dict:
    return {
        'EntName': name,
        'Direction': direction,
        'EntEnabled': True,
        'EntOrder': 0,
        'InteractOrder': 0,
        'triggerType': 0,
        'Collider': {'X': x, 'Y': y, 'Width': 16, 'Height': 16},
    }


def _pad_to_beach(raw: Image.Image) -> Image.Image:
    im = raw.convert('RGBA')
    if im.size == (BEACH_W, BEACH_H):
        return im
    pad = Image.new('RGBA', (BEACH_W, BEACH_H))
    pad.paste(im, (0, 0))
    right = im.crop((im.width - 1, 0, im.width, im.height))
    for x in range(im.width, BEACH_W):
        pad.paste(right, (x, 0))
    bot = pad.crop((0, im.height - 1, BEACH_W, im.height))
    for y in range(im.height, BEACH_H):
        pad.paste(bot, (0, y))
    return pad


def _tint_tile(im: Image.Image, amb: str, tint: tuple[int, int, int], sky_coords: set[tuple[int, int]] | None = None, cell_xy: tuple[int, int] = (0, 0), night_stars: set[tuple[int, int]] | None = None) -> Image.Image:
    if amb == 'jour':
        return im
    tr, tg, tb = tint
    sky_lut = SKY_MAPS[amb]
    px = bytearray(im.convert('RGBA').tobytes())
    ox, oy = cell_xy[0] * 8, cell_xy[1] * 8
    for py in range(8):
        for px_i in range(8):
            k = (py * 8 + px_i) * 4
            a = px[k + 3]
            if a == 0:
                continue
            gx, gy = ox + px_i, oy + py
            r, g, b = px[k], px[k + 1], px[k + 2]
            is_sky = (sky_coords is not None and (gx, gy) in sky_coords) or (gy < 50 and (r, g, b) in SKY_MAPS['jour'])
            if is_sky and (r, g, b) in sky_lut:
                nr, ng, nb = sky_lut[(r, g, b)]
                if amb == 'nuit' and night_stars and (gx, gy) in night_stars:
                    nr, ng, nb = (232, 240, 255) if ((gx + gy) % 2 == 0) else (176, 196, 248)
                px[k], px[k + 1], px[k + 2] = nr, ng, nb
            else:
                px[k] = min(255, (r * tr + 127) // 255)
                px[k + 1] = min(255, (g * tg + 127) // 255)
                px[k + 2] = min(255, (b * tb + 127) // 255)
    return Image.frombytes('RGBA', (8, 8), bytes(px))


def _load_beach_sources(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        webp = Image.open(io.BytesIO(zf.read('renders/beach_layers_v1/BeachV1_plage_animee.webp')))
        frames: list[Image.Image] = []
        for i in range(webp.n_frames):
            webp.seek(i)
            frames.append(_pad_to_beach(webp))
        assert len(frames) == FRAME_COUNT

        layers = {}
        for name in ('01_ciel', '02_sable', '03_mer', '04_ecume', '05_falaises_fond',
                     '06_vegetation_fond', '07_vegetation_proche', '08_rochers_rivage', '09_ilots'):
            layers[name] = Image.open(io.BytesIO(zf.read(f'renders/beach_layers_v1/import_8px/BeachV1_{name}_pad8.png'))).convert('RGBA')
        ref_pad = Image.open(io.BytesIO(zf.read('renders/beach_layers_v1/import_8px/DSVFS_sans_mixels_pad8.png'))).convert('RGBA')

    assert frames[0].tobytes() == ref_pad.tobytes(), 'Frame 0 paddée doit correspondre à DSVFS_sans_mixels_pad8.png'

    # Construire le calque premier plan des frondaisons de palmiers (Layer 4 = Top)
    # tout en conservant derrière elles le vrai décor (ciel / falaises / sable) sans trous !
    frond_mask = Image.new('L', (BEACH_W, BEACH_H), 0)
    l_vf = layers['06_vegetation_fond']
    l_vp = layers['07_vegetation_proche']
    l_roc = layers['08_rochers_rivage']

    # Fond de repli sous les frondaisons retirées du plan sol (ordre exact sous les feuilles : ciel -> sable -> falaises -> troncs -> rochers)
    under_base = Image.new('RGBA', (BEACH_W, BEACH_H), (0, 0, 0, 0))
    for lname in ('01_ciel', '02_sable', '05_falaises_fond'):
        under_base.alpha_composite(layers[lname])

    top_fronds = Image.new('RGBA', (BEACH_W, BEACH_H), (0, 0, 0, 0))
    top_px = top_fronds.load()
    f0_px = frames[0].load()
    vf_px = l_vf.load()
    vp_px = l_vp.load()
    roc_px = l_roc.load()

    for y in range(BEACH_H):
        for x in range(BEACH_W):
            if roc_px[x, y][3] > 0:
                continue
            in_top_palm = (y < 126 and 294 <= x < 430 and vf_px[x, y][3] > 0)
            in_left_palm = (y < 268 and 18 <= x < 154 and vp_px[x, y][3] > 0)
            in_right_palm = (y < 248 and 648 <= x < BEACH_W and vp_px[x, y][3] > 0)
            if in_top_palm or in_left_palm or in_right_palm:
                top_px[x, y] = f0_px[x, y]
                frond_mask.putpixel((x, y), 255)

    # Remplacer dans base_frame0 les pixels déplacés vers Top par under_base afin qu'aucune feuille ne soit dupliquée
    base_f0 = frames[0].copy()
    bf_px = base_f0.load()
    ub_px = under_base.load()
    for y in range(BEACH_H):
        for x in range(BEACH_W):
            if frond_mask.getpixel((x, y)) > 0:
                # vérifier que under_base est opaque là-dessous (sinon garder f0)
                if ub_px[x, y][3] == 255:
                    bf_px[x, y] = ub_px[x, y]
                else:
                    top_px[x, y] = (0, 0, 0, 0)

    # Vérifier fidélité exacte frame 0 = base_f0 + top_fronds
    recomp = base_f0.copy()
    recomp.alpha_composite(top_fronds)
    assert recomp.tobytes() == frames[0].tobytes(), 'Décomposition Plage Sablefin (base + frondaisons Top) non pixel-identique !'

    # Masque ciel visible (pour dégradés aube/crépuscule/nuit & étoiles)
    ciel_px = layers['01_ciel'].load()
    sky_coords = {
        (x, y)
        for y in range(52)
        for x in range(BEACH_W)
        if ciel_px[x, y][3] > 0 and base_f0.getpixel((x, y))[:3] in SKY_MAPS['jour']
    }
    # Étoiles déterministes 1x1 sur les trouées de ciel nocturne
    night_stars: set[tuple[int, int]] = set()
    for (x, y) in sorted(sky_coords):
        if y <= 40 and ((x * 37 + y * 91) % 89 == 7) and all((x + dx, y + dy) in sky_coords for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            night_stars.add((x, y))

    # Matrice d'obstacles 88x59 (grille 8x8 px) calibrée sur sable + seuil grotte + sortie est
    obs = [[1] * BEACH_TH for _ in range(BEACH_TW)]
    s_px = layers['02_sable'].load()
    f_px = layers['05_falaises_fond'].load()
    w_px = layers['03_mer'].load()
    e_px = layers['04_ecume'].load()
    r_px = layers['08_rochers_rivage'].load()
    i_px = layers['09_ilots'].load()

    for tx in range(BEACH_TW):
        for ty in range(BEACH_TH):
            x0, y0 = tx * 8, ty * 8
            s_cnt = f_cnt = w_cnt = r_cnt = i_cnt = p_cnt = 0
            for yy in range(y0, y0 + 8):
                for xx in range(x0, x0 + 8):
                    if s_px[xx, yy][3] > 0:
                        s_cnt += 1
                    if f_px[xx, yy][3] > 0:
                        f_cnt += 1
                    if w_px[xx, yy][3] > 0 or e_px[xx, yy][3] > 0:
                        w_cnt += 1
                    if r_px[xx, yy][3] > 0:
                        r_cnt += 1
                    if i_px[xx, yy][3] > 0:
                        i_cnt += 1
                    if ((328 <= xx < 392 and 126 <= yy < 152 and vf_px[xx, yy][3] > 0)
                            or (32 <= xx < 120 and 264 <= yy < 300 and vp_px[xx, yy][3] > 0)
                            or (656 <= xx < BEACH_W and 244 <= yy < 292 and vp_px[xx, yy][3] > 0)):
                        p_cnt += 1

            walk = (s_cnt >= 42 and w_cnt <= 4 and r_cnt <= 8 and i_cnt == 0 and f_cnt <= 18 and p_cnt <= 8)
            # Chemin est vers crossroadreverietown2 (x=640..703, y=96..159)
            if 80 <= tx <= 87 and 12 <= ty <= 19 and f_cnt <= 24:
                walk = True
            # Seuil sablonneux devant la grotte nord-ouest (x=56..119, y=108..135)
            if 7 <= tx <= 14 and 13 <= ty <= 16 and not (tx <= 8 and ty >= 16) and (ty >= 14 or tx >= 8):
                walk = True
            # Petits rochers isolés sur le sable : s'assurer qu'ils restent bloqués
            if (21 <= tx <= 22 and ty == 9) or (50 <= tx <= 51 and ty == 20) or (70 <= tx <= 72 and ty == 9):
                walk = False
            obs[tx][ty] = 0 if walk else 1

    # Filtrage strict de connexité 16x16 depuis entrance (640, 120) -> (80, 15)
    def free16(tx: int, ty: int) -> bool:
        if not (0 <= tx <= BEACH_TW - 2 and 0 <= ty <= BEACH_TH - 2):
            return False
        return obs[tx][ty] == 0 and obs[tx + 1][ty] == 0 and obs[tx][ty + 1] == 0 and obs[tx + 1][ty + 1] == 0

    assert free16(80, 15), 'entrance (640, 120) non libre'
    q = deque([(80, 15)])
    reach = {(80, 15)}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in reach and free16(nx, ny):
                reach.add((nx, ny))
                q.append((nx, ny))
    used = {pt for cx, cy in reach for pt in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1))}
    for tx in range(BEACH_TW):
        for ty in range(BEACH_TH):
            if (tx, ty) not in used:
                obs[tx][ty] = 1

    assert (7, 14) in reach and (12, 14) in reach and (86, 15) in reach, 'Chemin grotte/est incomplet sur Plage Sablefin'

    return {
        'frames': frames,
        'base_f0': base_f0,
        'top_fronds': top_fronds,
        'sky_coords': sky_coords,
        'night_stars': night_stars,
        'obs': obs,
    }


def build_plage_sablefin(root: Path, zip_path: Path) -> None:
    src = _load_beach_sources(zip_path)
    frames = src['frames']
    base_f0 = src['base_f0']
    top_fronds = src['top_fronds']
    sky_coords = src['sky_coords']
    night_stars = src['night_stars']
    obs = src['obs']

    # Identifier les cases 8x8 réellement animées entre frames 0..33
    anim_cells: set[tuple[int, int]] = set()
    for ty in range(BEACH_TH):
        for tx in range(BEACH_TW):
            box = (tx * 8, ty * 8, tx * 8 + 8, ty * 8 + 8)
            b0 = frames[0].crop(box).tobytes()
            if any(fr.crop(box).tobytes() != b0 for fr in frames[1:]):
                anim_cells.add((tx, ty))

    # Construire les 4 variantes Jour / Aube / Crépuscule / Nuit
    for amb, amb_cap, tint, music in AMBIANCES:
        sheet_name = f'Destiny_Plage_Sablefin_{amb_cap}'
        stem = f'plage_sablefin_{amb}'
        tile_registry: dict[bytes, tuple[int, int]] = {}
        sheet_imgs: dict[tuple[int, int], Image.Image] = {}

        def register_tile(im8: Image.Image) -> tuple[int, int]:
            if im8.getchannel('A').getbbox() is None:
                return (-1, -1)
            raw = im8.tobytes()
            if raw not in tile_registry:
                idx = len(tile_registry)
                loc = (idx % 64, idx // 64)
                tile_registry[raw] = loc
                sheet_imgs[loc] = im8
            return tile_registry[raw]

        def empty_cell() -> dict:
            return {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}

        def make_cell(loc: tuple[int, int]) -> dict:
            return {
                'AutoTileset': '', 'Associates': [],
                'Layers': [{'Frames': [{'Sheet': sheet_name, 'TexLoc': {'X': loc[0], 'Y': loc[1]}, 'Flip': 0}], 'FrameLength': 1}],
                'NeighborCode': -1,
            }

        def make_anim_cell(locs: list[tuple[int, int]]) -> dict:
            return {
                'AutoTileset': '', 'Associates': [],
                'Layers': [{'Frames': [{'Sheet': sheet_name, 'TexLoc': {'X': lx, 'Y': ly}, 'Flip': 0} for lx, ly in locs], 'FrameLength': WAVE_FRAME_LENGTH}],
                'NeighborCode': -1,
            }

        tiles_base = [[empty_cell() for _ in range(BEACH_TH)] for _ in range(BEACH_TW)]
        tiles_anim = [[empty_cell() for _ in range(BEACH_TH)] for _ in range(BEACH_TW)]
        tiles_top = [[empty_cell() for _ in range(BEACH_TH)] for _ in range(BEACH_TW)]

        for ty in range(BEACH_TH):
            for tx in range(BEACH_TW):
                box = (tx * 8, ty * 8, tx * 8 + 8, ty * 8 + 8)
                if (tx, ty) in anim_cells:
                    locs = []
                    for fi in range(FRAME_COUNT):
                        t_im = _tint_tile(frames[fi].crop(box), amb, tint, sky_coords, (tx, ty), night_stars)
                        locs.append(register_tile(t_im))
                    tiles_anim[tx][ty] = make_anim_cell(locs)
                else:
                    b_im = _tint_tile(base_f0.crop(box), amb, tint, sky_coords, (tx, ty), night_stars)
                    loc = register_tile(b_im)
                    if loc != (-1, -1):
                        tiles_base[tx][ty] = make_cell(loc)

                f_im = top_fronds.crop(box)
                if f_im.getchannel('A').getbbox() is not None:
                    tf_im = _tint_tile(f_im, amb, tint, None, (tx, ty), None)
                    floc = register_tile(tf_im)
                    if floc != (-1, -1):
                        tiles_top[tx][ty] = make_cell(floc)

        save_tile_sheet(root / 'game/Content/Tile' / f'{sheet_name}.tile', 8, sheet_imgs)

        obs_json = [[{'Tags': obs[tx][ty]} for ty in range(BEACH_TH)] for tx in range(BEACH_TW)]
        ground_doc = {
            'Version': '0.8.12.0',
            'Object': {
                '$type': 'RogueEssence.Ground.GroundMap, RogueEssence',
                'AssetName': stem,
                'Released': True,
                'Name': {'DefaultText': 'Plage Sablefin', 'LocalTexts': {'fr': 'Plage Sablefin'}},
                'Comment': f'Plage Sablefin ({amb}) — entrée du Passage Aquatique au sud du carrefour de Réverie Town (704x472, 34 phases, 0 mixel).',
                'Music': music,
                'TexSize': 1,
                'EdgeView': 1,
                'NoSwitching': False,
                'ViewCenter': None,
                'ViewOffset': {'X': 0, 'Y': 0},
                'ActiveChar': None,
                'BlankBG': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1},
                'rand': {'$type': 'RogueElements.ReRandom, RogueElements', 'FirstSeed': 0, 's': [16294208416658607535, 7960286522194355700, 487617019471545679, 17909611376780542444]},
                'Background': {
                    '$type': 'RogueEssence.Dungeon.MapBG, RogueEssence',
                    'MapLoc': {'X': 0, 'Y': 0},
                    'BGAnim': {'AnimIndex': '', 'FrameTime': 1, 'StartFrame': -1, 'EndFrame': -1, 'AnimDir': -1, 'Alpha': 255, 'AnimFlip': 0},
                    'BGMovement': {'X': 0, 'Y': 0},
                    'Parallax': '0, 0',
                    'RepeatX': False,
                    'RepeatY': False,
                },
                'Status': {},
                'Decorations': [],
                'Layers': [
                    {'Name': '00_Plage_Base', 'Layer': 0, 'Visible': True, 'Tiles': tiles_base},
                    {'Name': '01_Vagues_Animes', 'Layer': 0, 'Visible': True, 'Tiles': tiles_anim},
                    {'Name': '02_Palmiers_Premier_Plan', 'Layer': 4, 'Visible': True, 'Tiles': tiles_top},
                ],
                'obstacles': obs_json,
                'Entities': [{
                    'Name': 'New EntLayer',
                    'Visible': True,
                    'MapChars': [],
                    'GroundObjects': [
                        _make_trigger('SortieCarrefour', 688, 96, 16, 64, trigger_type=2, passable=True),
                        _make_trigger('SeuilPassageAquatique', 56, 108, 24, 24, trigger_type=2, passable=True),
                    ],
                    'Spawners': [],
                    'Markers': [
                        _make_marker('Main_Entrance_Marker', 640, 120, 2),
                        _make_marker('entrance', 640, 120, 2),
                        _make_marker('retour_grotte', 96, 112, 6),
                    ],
                }],
            },
        }
        (root / 'game/Data/Ground' / f'{stem}.rsground').write_text(
            json.dumps(ground_doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
        )
        print(f'[OK] {stem}: {len(sheet_imgs)} tuiles 8x8 uniques -> {sheet_name}.tile')


def build_passage_aquatique_fond(root: Path) -> None:
    arch = next((root / 'archive').rglob('*v50812_beach_cave_anse_des_marees.rsground'))
    doc = json.loads(arch.read_text(encoding='utf-8-sig'))
    obj = doc['Object']
    obj['AssetName'] = 'passage_aquatique_fond'
    obj['Released'] = True
    obj['Name'] = {'DefaultText': 'Passage Aquatique — Crique Cachée', 'LocalTexts': {'fr': 'Passage Aquatique — Crique Cachée'}}
    obj['Comment'] = 'Crique finale au bout des 10 étages du Passage Aquatique (BeachCavePit 23 phases, 456x480, collisions sable calibrées).'
    obj['Music'] = 'On the Beach at Dusk.ogg'
    obj['EdgeView'] = 1

    # Rendre la frame 0 exacte de BeachCavePit pour peindre les obstacles 57x60 sur le sable
    _, bcp = load_tile_sheet(root / 'game/Content/Tile', 'BeachCavePit')
    canvas = Image.new('RGB', (19 * 24, 20 * 24))
    lyr0 = obj['Layers'][0]['Tiles']
    for rx in range(19):
        for ry in range(20):
            frs = lyr0[rx][ry]['Layers'][0]['Frames']
            loc = (frs[0]['TexLoc']['X'], frs[0]['TexLoc']['Y'])
            canvas.paste(bcp[loc].convert('RGB'), (rx * 24, ry * 24))

    gw, gh = 57, 60  # 456x480 / 8
    obs = [[1] * gh for _ in range(gw)]
    for tx in range(gw):
        for ty in range(gh):
            sand = 0
            for yy in range(ty * 8, ty * 8 + 8):
                for xx in range(tx * 8, tx * 8 + 8):
                    r, g, b = canvas.getpixel((xx, yy))
                    if r > 155 and r > b + 20 and g > 110:
                        sand += 1
            walk = (sand >= 48) and (136 <= ty * 8 <= 399) and (112 <= tx * 8 <= 343)
            obs[tx][ty] = 0 if walk else 1

    def free16(tx: int, ty: int) -> bool:
        if not (0 <= tx <= gw - 2 and 0 <= ty <= gh - 2):
            return False
        return obs[tx][ty] == 0 and obs[tx + 1][ty] == 0 and obs[tx][ty + 1] == 0 and obs[tx + 1][ty + 1] == 0

    assert free16(27, 43), 'Entrance (220, 344) non libre sur passage_aquatique_fond'
    q = deque([(27, 43)])
    reach = {(27, 43)}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in reach and free16(nx, ny):
                reach.add((nx, ny))
                q.append((nx, ny))
    used = {pt for cx, cy in reach for pt in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1))}
    for tx in range(gw):
        for ty in range(gh):
            if (tx, ty) not in used:
                obs[tx][ty] = 1

    obj['obstacles'] = [[{'Tags': obs[tx][ty]} for ty in range(gh)] for tx in range(gw)]
    obj['Entities'] = [{
        'Name': 'New EntLayer',
        'Visible': True,
        'MapChars': [],
        'GroundObjects': [
            _make_trigger('SortieTunnelSud', 192, 384, 72, 16, trigger_type=2, passable=True),
            _make_trigger('PointVueOcean', 184, 136, 88, 16, trigger_type=1, passable=True),
        ],
        'Spawners': [],
        'Markers': [
            _make_marker('Main_Entrance_Marker', 220, 344, 4),
            _make_marker('entrance', 220, 344, 4),
        ],
    }]
    (root / 'game/Data/Ground/passage_aquatique_fond.rsground').write_text(
        json.dumps(doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
    )
    print(f'[OK] passage_aquatique_fond.rsground ({len(reach)} positions 16x16 connectées)')


def build_zone_passage_aquatique(root: Path) -> None:
    def base_set(subdir: str) -> set[str]:
        return {p.stem for p in (root / 'base/Data' / subdir).glob('*.json')}

    base_monsters = base_set('Monster')
    base_skills = base_set('Skill')
    base_intrs = base_set('Intrinsic')
    base_items = base_set('Item')
    base_tiles = base_set('Tile')
    base_autotiles = base_set('AutoTile')
    all_music = {p.name for p in (root / 'base/Content/Music').glob('*.ogg')} | {p.name for p in (root / 'game/Content/Music').glob('*.ogg')}

    def step_tile(tile_id: str) -> dict:
        assert tile_id in base_tiles, tile_id
        return {'TileLoc': {'X': 0, 'Y': 0}, 'ID': tile_id, 'Revealed': True, 'Owner': 0, 'TileStates': []}

    def gen_floor(idx: int) -> dict:
        if idx < 3:
            dtef = ('beach_cave_floor', 'beach_cave_wall', 'beach_cave_secondary', 'water')
            music = 'Beach Cave.ogg'
            cw, ch, cx, cy = 7, 7, 4, 4
            init_foes, max_foes, resp = 4 + idx // 2, 11, 40
            water_pct, blobs_max = 14, 5
        elif idx < 6:
            dtef = ('craggy_coast_floor', 'craggy_coast_wall', 'craggy_coast_secondary', 'water')
            music = 'Craggy Coast.ogg'
            cw, ch, cx, cy = 7, 6, 5, 4
            init_foes, max_foes, resp = 5 + (idx - 3) // 2, 13, 35
            water_pct, blobs_max = 16, 6
        elif idx < 8:
            dtef = ('brine_cave_floor', 'brine_cave_wall', 'brine_cave_secondary', 'water')
            music = 'Brine Cave.ogg'
            cw, ch, cx, cy = 6, 6, 5, 5
            init_foes, max_foes, resp = 6, 14, 32
            water_pct, blobs_max = 18, 7
        else:
            dtef = ('lower_brine_cave_floor', 'lower_brine_cave_wall', 'lower_brine_cave_secondary', 'water')
            music = 'Lower Brine Cave.ogg'
            cw, ch, cx, cy = 6, 6, 6, 5
            init_foes, max_foes, resp = 7, 15, 28
            water_pct, blobs_max = 20, 8

        assert music in all_music, music
        for at in dtef[:3]:
            assert at in base_autotiles, at

        generic_rooms = {
            '$type': 'RogueElements.SpawnList`1[[RogueElements.RoomGen`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements]], RogueElements',
            '$values': [
                {
                    'Spawn': {
                        '$type': 'RogueElements.RoomGenBump`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'Width': {'Min': 3, 'Max': 6}, 'Height': {'Min': 3, 'Max': 6},
                        'BumpPercent': {'Min': 45, 'Max': 55},
                    },
                    'Rate': 10,
                },
                {
                    'Spawn': {
                        '$type': 'RogueElements.RoomGenCave`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'Width': {'Min': 4, 'Max': 6}, 'Height': {'Min': 4, 'Max': 6},
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
                    'Width': {'Min': 0, 'Max': 0}, 'Height': {'Min': 0, 'Max': 0},
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
                    'Music': music, 'TimeLimit': 1500, 'TileSight': 0, 'CharSight': 1, 'ClampCamera': False,
                },
            },
            {
                'Key': {'str': [-5]},
                'Value': {
                    '$type': 'PMDC.LevelGen.MapEffectStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], PMDC',
                    'Effect': {
                        'UniversalStates': [], 'BeforeTryActions': [], 'BeforeActions': [], 'OnActions': [],
                        'BeforeExplosions': [], 'BeforeHits': [], 'OnHits': [], 'OnHitTiles': [], 'AfterActions': [],
                        'ElementEffects': [], 'OnEquips': [], 'OnPickups': [], 'BeforeStatusAdds': [], 'OnStatusAdds': [],
                        'OnStatusRemoves': [], 'OnMapStatusAdds': [], 'OnMapStatusRemoves': [], 'OnMapStarts': [],
                        'OnTurnStarts': [], 'OnTurnEnds': [], 'OnMapTurnEnds': [], 'OnWalks': [], 'OnDeaths': [],
                        'OnRefresh': [], 'OnMapRefresh': [], 'ModifyHPs': [], 'RestoreHPs': [], 'InitActionData': [],
                    },
                },
            },
            {
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.InitGridPlanStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'CellX': cx, 'CellY': cy, 'CellWidth': cw, 'CellHeight': ch, 'CellWall': 1, 'Wrap': False,
                },
            },
            {
                'Key': {'str': [-4]},
                'Value': {
                    '$type': 'RogueElements.GridPathBranch`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'RoomRatio': {'Min': 75, 'Max': 88},
                    'BranchRatio': {'Min': 10, 'Max': 30},
                    'NoConnect': False,
                    'GenericRooms': generic_rooms, 'GenericHalls': generic_halls,
                    'RoomComponents': conn_comp, 'HallComponents': conn_comp,
                },
            },
            {
                'Key': {'str': [-3]},
                'Value': {
                    '$type': 'PMDC.LevelGen.CombineGridRoomStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], PMDC',
                    'MergeRate': {'Min': 1, 'Max': 2},
                    'GenericRooms': generic_rooms,
                    'RoomComponents': conn_comp,
                },
            },
            {'Key': {'str': [-2]}, 'Value': {'$type': 'RogueElements.DrawGridToFloorStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements'}},
            {'Key': {'str': [0]}, 'Value': {'$type': 'RogueElements.SetSpecialTileStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Tile': {'$type': 'RogueEssence.Dungeon.Tile, RogueEssence', 'Data': {'ID': 'unbreakable', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False}, 'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []}}}},
            {
                'Key': {'str': [1]},
                'Value': {
                    '$type': 'PMDC.LevelGen.FloorStairsStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.MapGenEntrance, RogueEssence],[RogueEssence.Dungeon.MapGenExit, RogueEssence]], PMDC',
                    'Entrances': [{'Loc': {'X': 0, 'Y': 0}, 'Dir': 0}],
                    'Exits': [{'Loc': {'X': 0, 'Y': 0}, 'Tile': step_tile('stairs_go_up')}],
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                },
            },
            {
                'Key': {'str': [2]},
                'Value': {
                    '$type': 'RogueElements.SetGridDefaultsStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'DefaultRatio': {'Min': 35, 'Max': 55},
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                },
            },
            {
                'Key': {'str': [3]},
                'Value': {
                    '$type': 'RogueElements.PerlinWaterStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'OrderComplexity': 4, 'OrderSoftness': 0, 'WaterPercent': {'Min': water_pct, 'Max': water_pct}, 'Bowl': True,
                    'Terrain': {'$type': 'RogueEssence.Dungeon.Tile, RogueEssence', 'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False}, 'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []}},
                    'TerrainStencil': {
                        '$type': 'RogueElements.MultiTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'List': [
                            {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False},
                            {'$type': 'RogueElements.NoChokepointTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'TileStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False}, 'Global': False, 'Negate': True},
                            {'$type': 'RogueEssence.LevelGen.TileEffectStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Not': True},
                        ],
                        'RequireAny': False,
                    },
                },
            },
            {
                'Key': {'str': [3]},
                'Value': {
                    '$type': 'RogueElements.BlobWaterStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Blobs': {'Min': 2, 'Max': blobs_max}, 'AreaScale': {'Min': 12, 'Max': 28}, 'GenerateScale': {'Min': 100, 'Max': 100},
                    'Terrain': {'$type': 'RogueEssence.Dungeon.Tile, RogueEssence', 'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False}, 'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []}},
                    'TerrainStencil': {
                        '$type': 'RogueElements.MultiTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                        'List': [
                            {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False},
                            {'$type': 'RogueElements.NoChokepointTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'TileStencil': {'$type': 'RogueElements.MapTerrainStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Room': True, 'Wall': False, 'Blocked': False, 'Not': False}, 'Global': False, 'Negate': True},
                            {'$type': 'RogueEssence.LevelGen.TileEffectStencil`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements', 'Not': True},
                        ],
                        'RequireAny': False,
                    },
                },
            },
            {
                'Key': {'str': [3, 1]},
                'Value': {
                    '$type': 'RogueElements.DropDiagonalBlockStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Terrain': {'$type': 'RogueEssence.Dungeon.Tile, RogueEssence', 'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False}, 'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []}},
                },
            },
            {
                'Key': {'str': [3, 2]},
                'Value': {
                    '$type': 'RogueElements.EraseIsolatedStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'Terrain': {'$type': 'RogueEssence.Dungeon.Tile, RogueEssence', 'Data': {'ID': 'water', 'TileTex': {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}, 'StableTex': False}, 'Effect': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': '', 'Revealed': False, 'Owner': 0, 'TileStates': []}},
                },
            },
            {
                'Key': {'str': [4]},
                'Value': {
                    '$type': 'RogueEssence.LevelGen.MapDictTextureStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements',
                    'TextureMap': {
                        'floor': dtef[0], 'wall': dtef[1], 'unbreakable': dtef[1],
                        'water': dtef[2], 'lava': dtef[2], 'pit': dtef[2], 'water_poison': dtef[2],
                    },
                    'BlankBG': dtef[1], 'LayeredGround': True, 'IndependentGround': False, 'GroundElement': dtef[3],
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'PMDC.LevelGen.SpacedRoomSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], PMDC',
                    'IncludeHalls': False, 'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'Spawn': {
                        '$type': 'RogueElements.PickerSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                        'Picker': {
                            '$type': 'RogueElements.LoopedRand`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                            'Spawner': {'$type': 'RogueElements.SpawnList`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements', '$values': [{'Spawn': step_tile('tile_wonder'), 'Rate': 10}]},
                            'AmountSpawner': {'$type': 'RogueElements.RandRange, RogueElements', 'Min': 1, 'Max': 2},
                        },
                    },
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'RogueElements.RandomRoomSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                    'Spawn': {
                        '$type': 'RogueElements.PickerSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                        'Picker': {
                            '$type': 'RogueElements.LoopedRand`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements',
                            'Spawner': {'$type': 'RogueElements.SpawnList`1[[RogueEssence.Dungeon.EffectTile, RogueEssence]], RogueElements', '$values': [{'Spawn': step_tile('stairs_back_down'), 'Rate': 10}]},
                            'AmountSpawner': {'$type': 'RogueElements.RandRange, RogueElements', 'Min': 1, 'Max': 1},
                        },
                    },
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'RogueElements.DueSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.LevelGen.MobSpawn, RogueEssence]], RogueElements',
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                },
            },
            {
                'Key': {'str': [5]},
                'Value': {
                    '$type': 'RogueElements.DueSpawnStep`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                    'Filters': [{'$type': 'PMDC.LevelGen.RoomFilterConnectivity, PMDC', 'Connection': 1}],
                },
            },
            {
                'Key': {'str': [6]},
                'Value': {
                    '$type': 'PMDC.LevelGen.MobSpawnSettingsStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], PMDC',
                    'RespawnTime': resp, 'MaxFoes': max_foes,
                    'InitialFoes': {'$type': 'RogueElements.RandRange, RogueElements', 'Min': init_foes, 'Max': init_foes + 2},
                },
            },
        ]

        return {
            '$type': 'RogueEssence.LevelGen.GridFloorGen, RogueEssence',
            'GenSteps': {'$type': 'RogueElements.PriorityList`1[[RogueElements.GenStep`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueElements]], RogueElements', '$values': steps},
            'Comment': f'Passage Aquatique {idx + 1}F ({dtef[0].replace("_floor", "")})',
        }

    def mob_entry(species: str, lv_min: int, lv_max: int, skills: list[str], intr: str, f_min: int, f_max: int, rate: int) -> dict:
        assert species in base_monsters, species
        assert intr in base_intrs, intr
        for sk in skills:
            assert sk in base_skills, sk
        return {
            'Spawn': {
                'BaseForm': {'Species': species, 'Form': 0, 'Skin': 'normal', 'Gender': -1},
                'Level': {'Min': lv_min, 'Max': lv_max},
                'SpecifiedSkills': skills,
                'Intrinsic': intr,
                'SpawnFeatures': [{'$type': 'PMDC.LevelGen.MobSpawnLoc, PMDC', 'Loc': {'X': 0, 'Y': 0}}],
                'Tactic': 'wander_normal',
                'SpawnConditions': [],
            },
            'Rate': rate,
            'Range': {'Min': f_min, 'Max': f_max},
        }

    def item_entry(item_id: str, rate: int, f_min: int = 0, f_max: int = 10) -> dict:
        assert item_id in base_items, item_id
        return {
            'Spawn': {'$type': 'RogueEssence.Dungeon.MapItem, RogueEssence', 'Value': item_id, 'Amount': 0, 'Hidden': False, 'Cursed': False, 'TileLoc': {'X': 0, 'Y': 0}},
            'Rate': rate,
            'Range': {'Min': f_min, 'Max': f_max},
        }

    def item_cat(weight: int, entries: list[dict]) -> dict:
        return {
            'CategoryWeight': weight,
            'ItemSpawns': {
                '$type': 'RogueElements.SpawnRangeList`1[[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                '$values': entries,
            },
        }

    def spread_item(item_id: str, mn: int, mx: int) -> dict:
        assert item_id in base_items, item_id
        return {
            '$type': 'RogueEssence.LevelGen.SpreadStepZoneStep, RogueEssence',
            'StepPriority': {'str': [5]},
            'Spawns': {
                '$type': 'RogueElements.PickerSpawner`2[[RogueEssence.LevelGen.MapGenContext, RogueEssence],[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                'Picker': {
                    '$type': 'RogueElements.LoopedRand`1[[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements',
                    'Spawner': {'$type': 'RogueElements.SpawnList`1[[RogueEssence.Dungeon.MapItem, RogueEssence]], RogueElements', '$values': [{'Spawn': {'$type': 'RogueEssence.Dungeon.MapItem, RogueEssence', 'Value': item_id, 'Amount': 0, 'Hidden': False, 'Cursed': False, 'TileLoc': {'X': 0, 'Y': 0}}, 'Rate': 10}]},
                    'AmountSpawner': {'$type': 'RogueElements.RandRange, RogueElements', 'Min': 1, 'Max': 1},
                },
            },
            'SpreadPlan': {'$type': 'RogueElements.LevelGen.SpreadPlanSpaced, RogueEssence', 'FloorSpacing': {'Min': mn, 'Max': mx}, 'BeginStart': True, 'FloorRange': {'Min': 0, 'Max': 10}},
            'ModStates': [],
        }

    def trap_entry(tile_id: str, rate: int, f_min: int, f_max: int, revealed: bool = False) -> dict:
        assert tile_id in base_tiles, tile_id
        return {
            'Spawn': {'TileLoc': {'X': 0, 'Y': 0}, 'ID': tile_id, 'Revealed': revealed, 'Owner': 0, 'TileStates': []},
            'Rate': rate,
            'Range': {'Min': f_min, 'Max': f_max},
        }

    zone_steps_s0 = [
        {'$type': 'PMDC.LevelGen.SaveVarsZoneStep, PMDC', 'Priority': {'str': [2, 1]}},
        {
            '$type': 'PMDC.LevelGen.FloorNameDropZoneStep, PMDC',
            'DropPriority': {'str': [-15]},
            'Name': {'DefaultText': 'Passage Aquatique\n{0}F', 'LocalTexts': {'fr': 'Passage Aquatique\n{0}F'}},
            'Priority': {'str': [-6]},
        },
        {
            '$type': 'RogueEssence.LevelGen.MoneySpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 1]},
            'StartAmount': {'Min': 15, 'Max': 45},
            'AddAmount': {'Min': 6, 'Max': 15},
            'SpreadPlan': {'$type': 'RogueElements.LevelGen.SpreadPlanSpaced, RogueEssence', 'FloorSpacing': {'Min': 1, 'Max': 1}, 'BeginStart': True, 'FloorRange': {'Min': 0, 'Max': 10}},
            'ModStates': [],
        },
        {
            '$type': 'RogueEssence.LevelGen.ItemSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 1]},
            'Spawns': {
                'food': item_cat(12, [
                    item_entry('food_apple', 14), item_entry('berry_oran', 14), item_entry('berry_leppa', 8),
                    item_entry('berry_pecha', 10), item_entry('berry_cheri', 8), item_entry('berry_lum', 10),
                    item_entry('food_apple_big', 7, 3, 10), item_entry('seed_reviver', 5),
                ]),
                'snacks': item_cat(10, [
                    item_entry('seed_blast', 11), item_entry('seed_sleep', 10), item_entry('seed_warp', 10), item_entry('berry_sitrus', 5, 4, 10),
                ]),
                'boosters': item_cat(5, [
                    item_entry('gummi_blue', 10), item_entry('gummi_clear', 8),
                ]),
                'throwable': item_cat(10, [
                    item_entry('ammo_geo_pebble', 12), item_entry('ammo_gravelerock', 9, 2, 10), item_entry('ammo_iron_thorn', 9, 3, 10),
                    item_entry('wand_pounce', 8), item_entry('wand_slow', 8),
                ]),
                'orbs': item_cat(8, [
                    item_entry('orb_escape', 8), item_entry('orb_cleanse', 8), item_entry('orb_luminous', 8),
                    item_entry('orb_totter', 8), item_entry('orb_slumber', 8),
                ]),
                'tms': item_cat(4, [
                    item_entry('tm_water_pulse', 3, 3, 10), item_entry('tm_rain_dance', 3, 4, 10),
                    item_entry('tm_surf', 2, 6, 10), item_entry('tm_scald', 2, 7, 10),
                ]),
            },
        },
        {
            '$type': 'RogueEssence.LevelGen.TeamSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 2]},
            'Spawns': [
                mob_entry('krabby', 10, 11, ['bubble', 'vice_grip', 'leer', 'mud_shot'], 'hyper_cutter', 0, 4, 12),
                mob_entry('shellder', 10, 11, ['tackle', 'withdraw', 'icicle_spear', 'supersonic'], 'shell_armor', 0, 4, 11),
                mob_entry('wingull', 10, 11, ['water_gun', 'wing_attack', 'supersonic', 'quick_attack'], 'keen_eye', 0, 5, 11),
                mob_entry('wimpod', 10, 11, ['struggle_bug', 'sand_attack'], 'wimp_out', 0, 4, 10),
                mob_entry('wiglett', 10, 11, ['sand_attack', 'water_gun', 'mud_slap', 'aqua_jet'], 'gooey', 0, 5, 10),
                mob_entry('surskit', 10, 11, ['bubble', 'quick_attack', 'bubble_beam'], 'swift_swim', 0, 4, 9),
                mob_entry('squirtle', 10, 12, ['water_gun', 'bubble', 'bite', 'rapid_spin'], 'torrent', 1, 5, 9),
                mob_entry('psyduck', 10, 12, ['water_gun', 'confusion', 'fury_swipes', 'water_pulse'], 'damp', 1, 6, 9),
                mob_entry('buizel', 12, 13, ['quick_attack', 'water_gun', 'aqua_jet', 'pursuit'], 'swift_swim', 3, 7, 10),
                mob_entry('shellos', 12, 13, ['mud_slap', 'water_pulse', 'mud_bomb', 'rain_dance'], 'storm_drain', 3, 7, 10),
                mob_entry('corsola', 12, 14, ['bubble', 'bubble_beam', 'recover', 'ancient_power'], 'natural_cure', 3, 10, 9),
                mob_entry('slowpoke', 12, 14, ['water_gun', 'confusion', 'yawn', 'headbutt'], 'own_tempo', 3, 7, 9),
                mob_entry('corphish', 12, 14, ['bubble_beam', 'vice_grip', 'knock_off', 'protect'], 'hyper_cutter', 3, 8, 9),
                mob_entry('spheal', 12, 14, ['powder_snow', 'water_gun', 'ice_ball', 'rollout'], 'thick_fat', 3, 8, 9),
                mob_entry('oshawott', 12, 14, ['water_gun', 'razor_shell', 'fury_cutter', 'water_pulse'], 'torrent', 3, 8, 8),
                mob_entry('staryu', 13, 15, ['water_gun', 'psywave', 'swift', 'bubble_beam'], 'natural_cure', 5, 10, 9),
                mob_entry('chinchou', 13, 15, ['bubble_beam', 'spark', 'confuse_ray', 'thunder_wave'], 'volt_absorb', 5, 10, 9),
                mob_entry('tentacool', 13, 15, ['poison_sting', 'water_pulse', 'acid_spray', 'wrap'], 'clear_body', 5, 9, 9),
                mob_entry('barboach', 13, 15, ['mud_bomb', 'water_pulse', 'magnitude'], 'oblivious', 5, 9, 9),
                mob_entry('finneon', 13, 15, ['water_gun', 'gust', 'water_pulse', 'rain_dance'], 'swift_swim', 5, 9, 8),
                mob_entry('carvanha', 14, 16, ['bite', 'aqua_jet', 'assurance', 'screech'], 'rough_skin', 6, 10, 9),
                mob_entry('clamperl', 14, 16, ['clamp', 'water_gun', 'whirlpool', 'shell_smash'], 'shell_armor', 6, 10, 8),
                mob_entry('mareanie', 14, 16, ['poison_sting', 'bite', 'venoshock', 'spike_cannon'], 'merciless', 6, 10, 9),
                mob_entry('frillish', 14, 16, ['bubble_beam', 'night_shade', 'water_pulse', 'recover'], 'water_absorb', 7, 10, 9),
                mob_entry('clauncher', 14, 16, ['water_gun', 'vice_grip', 'bubble_beam', 'swords_dance'], 'mega_launcher', 7, 10, 9),
                mob_entry('dewpider', 14, 16, ['bubble_beam', 'bug_bite', 'bite', 'aqua_ring'], 'water_bubble', 7, 10, 8),
            ],
        },
        spread_item('food_apple', 2, 4),
        spread_item('berry_oran', 2, 4),
        spread_item('berry_leppa', 3, 6),
        {
            '$type': 'RogueEssence.LevelGen.TileSpawnZoneStep, RogueEssence',
            'Priority': {'str': [1, 3]},
            'Spawns': [
                trap_entry('trap_trip', 10, 0, 10, True),
                trap_entry('trap_mud', 10, 1, 10, False),
                trap_entry('trap_slow', 9, 2, 10, False),
                trap_entry('trap_gust', 8, 3, 10, False),
                trap_entry('trap_slumber', 7, 4, 10, False),
                trap_entry('trap_warp', 6, 5, 10, False),
            ],
        },
        {
            '$type': 'RogueEssence.LevelGen.SpreadStepRangeZoneStep, RogueEssence',
            'StepPriority': {'str': [5]},
            'Spawns': [{
                'Spawn': {'$type': 'RogueEssence.LevelGen.ScriptGenStep`1[[RogueEssence.LevelGen.ListMapGenContext, RogueEssence]], RogueEssence', 'Script': 'Mysteriosity', 'ArgTable': '{BaseChance=5, SegDiff=2}'},
                'Rate': 10, 'Range': {'Min': 0, 'Max': 10},
            }],
            'SpreadPlan': {'$type': 'RogueEssence.LevelGen.SpreadPlanSpaced, RogueEssence', 'FloorSpacing': {'Min': 3, 'Max': 5}, 'BeginStart': False, 'FloorRange': {'Min': 0, 'Max': 10}},
            'ModStates': [],
        },
    ]

    segment0 = {
        '$type': 'RogueEssence.LevelGen.LayeredSegment, RogueEssence',
        'Floors': [gen_floor(i) for i in range(10)],
        'ZoneSteps': zone_steps_s0,
        'IsRelevant': True,
        'Comment': 'Étages 1F à 10F du Passage Aquatique (beach_cave -> craggy_coast -> brine_cave -> lower_brine_cave) menant à passage_aquatique_fond.',
    }

    grounds = ['plage_sablefin_jour', 'plage_sablefin_aube', 'plage_sablefin_crepuscule', 'plage_sablefin_nuit', 'passage_aquatique_fond']
    zone_doc = {
        'Version': '0.8.12.0',
        'Object': {
            '$type': 'RogueEssence.Data.ZoneData, RogueEssence',
            'Name': {'DefaultText': 'Passage Aquatique', 'LocalTexts': {'fr': 'Passage Aquatique'}},
            'Released': True,
            'Comment': 'Plage Sablefin (4 ambiances Réverie) et donjon Passage Aquatique (10 étages -> passage_aquatique_fond), raccordé au sud de crossroadreverietown2.',
            'NoEXP': False, 'ExpPercent': 100, 'Level': 12, 'LevelCap': False, 'KeepSkills': False,
            'TeamRestrict': False, 'TeamSize': -1, 'MoneyRestrict': False, 'BagRestrict': -1,
            'KeepTreasure': False, 'BagSize': -1, 'Persistent': False, 'Rescues': 2, 'Rogue': 1,
            'Segments': [segment0],
            'GroundMaps': grounds,
        },
    }
    (root / 'game/Data/Zone/passage_aquatique.json').write_text(
        json.dumps(zone_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )

    idx_path = root / 'game/Data/Zone/index.idx'
    idx_doc = json.loads(idx_path.read_text(encoding='utf-8-sig'))
    idx_doc['Object']['passage_aquatique'] = {
        '$type': 'RogueEssence.Data.ZoneEntrySummary, RogueEssence',
        'ExpPercent': 100, 'Level': 12, 'LevelCap': False, 'KeepSkills': False,
        'TeamRestrict': False, 'TeamSize': -1, 'MoneyRestrict': False, 'BagRestrict': -1,
        'KeepTreasure': False, 'BagSize': -1, 'Rescues': 2, 'CountedFloors': 10, 'Rogue': 1,
        'Grounds': grounds,
        'Maps': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]],
        'Name': {'DefaultText': 'Passage Aquatique', 'LocalTexts': {'fr': 'Passage Aquatique'}},
        'Released': True,
        'Comment': 'Plage Sablefin (jour/aube/crépuscule/nuit) + Passage Aquatique (10 étages) menant à passage_aquatique_fond.',
        'SortOrder': 33,
    }
    idx_path.write_text(json.dumps(idx_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('[OK] passage_aquatique.json + Zone/index.idx (10 étages, 5 GroundMaps)')


def main() -> int:
    root = DEFAULT_WT
    zip_path = DEFAULT_ZIP
    args = sys.argv[1:]
    if '--root' in args:
        root = Path(args[args.index('--root') + 1])
    if '--zip' in args:
        zip_path = Path(args[args.index('--zip') + 1])

    if zip_path.is_file():
        build_plage_sablefin(root, zip_path)
    else:
        print(f'[INFO] Archive source absente ({zip_path}) : conservation des planches/cartes Plage Sablefin existantes.')
        for amb, _, _, _ in AMBIANCES:
            assert (root / 'game/Data/Ground' / f'plage_sablefin_{amb}.rsground').is_file()
    build_passage_aquatique_fond(root)
    build_zone_passage_aquatique(root)
    build_idx = root / 'tools/build_tile_index.py'
    if build_idx.is_file():
        subprocess.run([sys.executable, str(build_idx)], cwd=root, check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
