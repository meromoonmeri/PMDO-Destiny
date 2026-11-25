#!/usr/bin/env python3
"""Retouche des raccords de Réverie sur la base aa1430c4 (aucun changement de gameplay).

python tools/polish_reverie_raccords.py --source-payload /copie/payload --out /copie/polish

Le résultat est un lot à relire avant intégration. Seul le tableau Layers de
chaque ground est remplacé. Tous les tracés travaillent sur la grille 8 px et
sur le décor déjà publié ; aucune ressource externe n'est requise.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageFilter

from lib_tiles import write_tilesheet
from render_ground_moteur import Planches

ROOT = Path(__file__).resolve().parents[1]
GRASS = 'Reverie_Geo_01_Sol_herbe'
BANK = 'Reverie_Raccords_Polish'
MAPS = tuple(n + suffix for n in ('WaterfallVillageCapital', 'reverie_centre', 'reverie_nord',
                                 'reverie_etang', 'reverie_residentiel') for suffix in ('', '_Dev'))
# Un arbre entier de Réverie : x=1400, y=2856 (donneur, en cases 8 px).
DONOR = (175, 357)
# Origine du dessin complet, avant et après. Seules les cellules du même
# tampon sont retirées : les fleurs, bords de rives et sols en dessous restent.
TREES = ((-2, 297, 0, 64), (-1, 338, 0, 71),
         (195, 319, 190, 38), (192, 337, 190, 64))
SAND_CORE = (248, 216, 152, 255)


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def parts(data):
    a = data.index(b'"Layers":') + len(b'"Layers":')
    b = data.index(b',"AssetName":', a)
    return data[:a], data[a:b], data[b:]


def frame(f):
    return (f['Sheet'], f['TexLoc']['X'], f['TexLoc']['Y'])


def tracks(cell):
    return cell.get('Layers', [])


def tile_frame(sheet, tx, ty):
    return {'Sheet': sheet, 'TexLoc': {'X': tx, 'Y': ty}}


def cell_from(f):
    return {'AutoTileset': '', 'Associates': [],
            'Layers': [{'Frames': [f], 'FrameLength': 60}], 'NeighborCode': -1}


def compter_pistes(grille):
    return sum(len(tracks(cell)) for col in grille for cell in col)


def terrain_tile(cell):
    if not tracks(cell) or any(len(t['Frames']) != 1 for t in tracks(cell)):
        return None
    result = Image.new('RGBA', (8, 8))
    for t in tracks(cell):
        f = frame(t['Frames'][0])
        if f[0]:
            im = Planches.tuile(*f)
            if im is None:
                raise ValueError(f'tuile absente : {f}')
            result.alpha_composite(im)
    return result if result.getextrema()[3] == (255, 255) else None


def jitter(x, y, seed=0):
    return ((x * 374761393 + y * 668265263 + seed * 2246822519) ^ (x * y * 40507)) % 997 / 997


def is_sand(color):
    r, g, b, a = color
    return a == 255 and 208 <= r <= 248 and 144 <= g <= 224 and 80 <= b <= 160 and 8 <= r - g <= 72


def is_grass(color):
    r, g, b, a = color
    return a == 255 and 160 <= r <= 224 and g >= r and g >= 112 + b


def pixel_sable(x, y, d):
    grain = jitter(x, y, 7)
    if d >= 6:
        return (248, 208, 144, 255) if grain < .035 else SAND_CORE
    if d >= 3:
        return (248, 200, 128, 255) if grain < .20 else (248, 208, 144, 255)
    if d >= 1:
        return (240, 192, 120, 255) if grain < .29 else (248, 200, 128, 255)
    return (232, 176, 112, 255) if grain < .31 else (240, 192, 120, 255)


def distance_bord(x, y, points):
    best = -1e9
    for (a, b, r0), (c, d, r1) in zip(points, points[1:]):
        u, v = c - a, d - b
        t = max(0., min(1., ((x - a) * u + (y - b) * v) / (u * u + v * v)))
        best = max(best, r0 + t * (r1 - r0) - math.hypot(x - a - t * u, y - b - t * v))
    return best + .9 * math.sin(x / 6.5 + y / 9.5) + .6 * math.cos(x / 3.6 - y / 4)


def move_trees(grid):
    sx, sy = DONOR
    stamp = {(dx, dy): copy.deepcopy(grid[sx + dx][sy + dy])
             for dx in range(10) for dy in range(9) if tracks(grid[sx + dx][sy + dy])}
    if len(stamp) != 76:
        raise ValueError(f'tampon arbre inattendu ({len(stamp)})')
    moved = []
    for ox, y, nx, expected in TREES:
        removed = 0
        deja_couvert = set()
        for (dx, dy), source in stamp.items():
            x = ox + dx
            if not 0 <= x < len(grid):
                continue
            old = grid[x][y + dy]
            ident = frame(tracks(source)[-1]['Frames'][0])
            move = [t for t in tracks(old) if len(t['Frames']) == 1 and frame(t['Frames'][0]) == ident]
            if move:
                rest = [t for t in tracks(old) if t not in move]
                grid[x][y + dy] = {**old, 'Layers': rest} if rest else {}
                deja_couvert.add((x, y + dy))
                removed += 1
        if removed != expected:
            raise ValueError(f'arbre à {(ox, y)} : {removed} cellules plutôt que {expected}')
        for (dx, dy), source in stamp.items():
            x, yy = nx + dx, y + dy
            old = grid[x][yy]
            if not tracks(old):
                grid[x][yy] = copy.deepcopy(source)
            else:
                # Ne recouvrir aucun autre objet, sauf le paysage précomposé
                # à l'est, qui constitue le fond de la lisière (sans animation).
                if (x, yy) not in deja_couvert and any(
                        len(t['Frames']) != 1 or frame(t['Frames'][0])[0] != 'Reverie_Geo_14_Paysages_composites'
                        for t in tracks(old)):
                    raise ValueError(f'objet voisin dans l’arbre à {(x, yy)}')
                old['Layers'].extend(copy.deepcopy(tracks(source)))
        moved.append({'avant_case': [ox, y], 'apres_case': [nx, y], 'cellules_rognées': removed})
    return moved


def retoucher(layers):
    if [l['Name'] for l in layers[:8]] != ['Base', 'Cliffs', 'River', 'Layer 4', 'Objects Under',
                                           'Objects Under Anim', 'Objects', 'Objects Anim']:
        raise ValueError('calques non reconnus : arrêt avant édition')
    avant = [compter_pistes(calque['Tiles']) for calque in layers]
    base = layers[0]['Tiles']
    count_grass = 0
    for col in base:
        for cell in col:
            for t in tracks(cell):
                if len(t['Frames']) == 1 and frame(t['Frames'][0]) == (GRASS, 39, 218):
                    t['Frames'][0] = tile_frame(GRASS, 477, 189)
                    count_grass += 1
    if count_grass != 7982:
        raise ValueError(f'herbe de référence inattendue : {count_grass}')
    grass = Planches.tuile(GRASS, 477, 189).load()
    arbres = move_trees(layers[6]['Tiles'])
    inks = {}
    dedup = {}
    travaux = []

    def brush(nom, box, paint):
        x0, y0, x1, y1 = box
        pixels = Image.new('RGBA', (x1 - x0, y1 - y0))
        valid = {}
        for tile_x in range(x0 // 8, x1 // 8):
            for tile_y in range(y0 // 8, y1 // 8):
                chip = terrain_tile(base[tile_x][tile_y])
                if chip is not None:
                    valid[tile_x, tile_y] = chip
                    pixels.paste(chip, (tile_x * 8 - x0, tile_y * 8 - y0))
        mask = Image.new('L', pixels.size)
        # Érosion du sable : une teinte pleine au centre n'est pas une rive qu'il
        # faudrait supprimer. On garde les tons de contour au contact de l'herbe.
        px, py = pixels.size
        src = pixels.load()
        mask.putdata([255 if is_sand(src[x, y]) else 0 for y in range(py) for x in range(px)])
        distances = [mask.filter(ImageFilter.MinFilter(1 + 2 * r)).load() for r in (1, 2, 4, 6)]
        n, pistes_regroupees = 0, 0
        for (tx, ty), old in valid.items():
            chip = old.copy()
            p = chip.load()
            for dy in range(8):
                for dx in range(8):
                    x, y = tx * 8 + dx, ty * 8 + dy
                    bord = sum(1 for m in distances if m[x-x0, y-y0])
                    p[dx, dy] = paint(x, y, p[dx, dy], bord)
            if chip.tobytes() == old.tobytes():
                continue
            key = chip.tobytes()
            if key not in dedup:
                index = len(dedup)
                spot = index % 32, index // 32
                dedup[key] = spot
                inks[spot] = chip
            pistes_regroupees += len(tracks(base[tx][ty])) - 1
            base[tx][ty] = cell_from(tile_frame(BANK, *dedup[key]))
            n += 1
        if not n:
            raise ValueError(f'aucune correction à {nom}')
        travaux.append({'nom': nom, 'rectangle_px': box, 'cellules': n,
                        'pistes_statiques_regroupees': pistes_regroupees})

    trajet_cafe = [(546, 1438, 16), (572, 1421, 10), (616, 1420, 10), (686, 1419, 10),
                   (762, 1420, 10), (844, 1419, 10), (913, 1420, 10), (984, 1419, 11),
                   (1014, 1420, 13), (1034, 1429, 15), (1047, 1450, 15),
                   (1048, 1494, 14), (1048, 1525, 14), (1051, 1550, 20)]

    def cafe(x, y, old, _inside):
        # On reprend le long ruban et le coude, pas les massifs, la rive ni
        # la place au sud. Extrémités raccordées sur vingt pixels.
        if not (x >= 552 and 1401 <= y <= 1438 or x >= 1008 and 1401 <= y <= 1543):
            return old
        if not (is_sand(old) or is_grass(old)):
            return old
        if jitter(x, y, 1) >= min(1, (x-552)/16, (1544-y)/14):
            return old
        d = distance_bord(x, y, trajet_cafe)
        if d >= 0 or (-2 < d < 0 and jitter(x, y, 2) > .69):
            return pixel_sable(x, y, d)
        return grass[x % 8, y % 8] if is_sand(old) else old

    brush('Ruban de la terrasse du Café et coude sud', (552, 1400, 1080, 1544), cafe)

    sortie_dojo = [(1455, 579, 17), (1455, 591, 17), (1455, 603, 19), (1457, 621, 23)]

    def dojo(x, y, old, _inside):
        if not (is_sand(old) or is_grass(old)) or jitter(x, y, 3) > min(1, (624-y)/14):
            return old
        d = distance_bord(x, y, sortie_dojo)
        if d > 0 or (-2 < d < 0 and jitter(x, y, 2) > .7):
            return pixel_sable(x, y, d)
        return old

    brush('Raccord du sable au pied de l’escalier est', (1424, 576, 1496, 624), dojo)

    def adoucir_couture(nom, box):
        x0, y0, x1, y1 = box
        def couture(x, y, old, distance):
            if not is_sand(old) or distance < 1:
                return old
            fondu = min(x-x0, x1-1-x, y-y0, y1-1-y) / 8
            if jitter(x, y, 3) >= fondu:
                return old
            # Même transition de couleur de part et d'autre de l'ancienne
            # couture horizontale. Les pixels à l'herbe et les pierres restent.
            return pixel_sable(x, y, (0, 2, 4, 6, 6)[distance])
        brush(nom, box, couture)

    adoucir_couture('Couture sableuse de l’allée ouest', (48, 2328, 136, 2432))
    adoucir_couture('Couture de la place ouest vers le sud', (120, 1224, 200, 1304))
    apres = [compter_pistes(calque['Tiles']) for calque in layers]
    return inks, {'herbe_cellules': count_grass, 'arbres': arbres, 'chemins': travaux,
                  'pistes': {'avant': avant, 'apres': apres}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-payload', type=Path, default=ROOT / 'payload')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    out = args.out
    if (out / 'payload').resolve() == args.source_payload.resolve():
        ap.error('le dossier de sortie doit être distinct des sources')
    (out / 'payload').mkdir(parents=True, exist_ok=True)
    original = gzip.decompress((args.source_payload / f'{MAPS[0]}.rsground.gz').read_bytes())
    _head, old_layers, _tail = parts(original)
    layers = json.loads(old_layers)
    tiles, journal = retoucher(layers)
    new_layers = compact(layers)
    del layers, original
    journal['cartes'] = {}
    for name in MAPS:
        p = args.source_payload / f'{name}.rsground.gz'
        raw = gzip.decompress(p.read_bytes())
        head, chk, tail = parts(raw)
        if chk != old_layers:
            raise ValueError(f'{name} : décor divergent, ne pas propager automatiquement')
        target = head + new_layers + tail
        (out / 'payload' / p.name).write_bytes(gzip.compress(target, compresslevel=6, mtime=0))
        journal['cartes'][name] = {'sha256': hashlib.sha256(target).hexdigest(), 'octets': len(target)}
        del raw, head, chk, tail, target
    bank = out / 'game' / 'Content' / 'Tile' / f'{BANK}.tile'
    bank.parent.mkdir(parents=True, exist_ok=True)
    journal['banque'] = {'nom': BANK, 'cellules': write_tilesheet(bank, tiles)}
    art = out / 'art' / 'reverie' / 'tilesheets' / f'{BANK}.png'
    art.parent.mkdir(parents=True, exist_ok=True)
    atlas = Image.new('RGBA', (256, (max(y for _, y in tiles) + 1) * 8))
    for (x, y), tile in tiles.items():
        atlas.paste(tile, (x * 8, y * 8))
    atlas.save(art)
    (out / 'retouches-reverie.json').write_text(json.dumps(journal, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in journal.items() if k != 'cartes'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
