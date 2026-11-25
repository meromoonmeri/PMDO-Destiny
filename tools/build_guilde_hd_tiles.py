#!/usr/bin/env python3
"""Génère les 4 banques de tuiles PMDO ``Guilde_HD_*`` pour le Dev Editor.

Chaque banque ``TileSize = 8`` (grille ``66 × 46`` cases = ``528 × 368 px``)
regroupe, aux coordonnées exactes de l'éditeur PMDO (encodage RGBA
prémultiplié identique à ``TileSheet.Import``) :
  - Guilde porte fermée : cases ``(0..31, 0..31)`` (``256 × 256 px``)
  - Guilde porte ouverte : cases ``(34..65, 0..31)`` (``256 × 256 px``)
  - Ombre au sol séparée : cases ``(0..33, 34..45)`` (``272 × 96 px``),
    centrée avec décalage ``(+5, +3) px`` de sorte qu'un tamponnage de l'ombre
    à ``(tx - 1, ty + 21)`` s'aligne à ``0.0 px`` sous la guilde posée en ``(tx, ty)``.

Usage :
  python3 tools/build_guilde_hd_tiles.py [--check]
"""
from __future__ import annotations

import io
import struct
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES_DIR = ROOT / 'art' / 'cliff-guilde' / 'sprites'
TILE_DIR = ROOT / 'game' / 'Content' / 'Tile'

TILE_SIZE = 8
GRID_W = 66
GRID_H = 46

# Coordonnées exactes dans les planches (en cases 8×8)
CLOSED_ORIGIN = (0, 0)
OPEN_ORIGIN = (34, 0)
SHADOW_ORIGIN = (0, 34)
SHADOW_PAD = (5, 3)  # (-8 + 5 = -3 px ; +168 + 3 = +171 px par rapport à [3..259, 3..259])

AMBIANCES = [
    ('jour', 'Guilde_HD_Jour'),
    ('aube', 'Guilde_HD_Aube_FILTRE'),
    ('crepuscule', 'Guilde_HD_Crep_FILTRE'),
    ('nuit', 'Guilde_HD_Nuit_FILTRE'),
]


def premultiply(im: Image.Image) -> Image.Image:
    rgba = im.convert('RGBA')
    px = bytearray(rgba.tobytes())
    for i in range(0, len(px), 4):
        a = px[i + 3]
        if a == 0:
            px[i] = px[i + 1] = px[i + 2] = 0
        elif a < 255:
            px[i] = (px[i] * a) // 255
            px[i + 1] = (px[i + 1] * a) // 255
            px[i + 2] = (px[i + 2] * a) // 255
    return Image.frombytes('RGBA', rgba.size, bytes(px))


def compose_sheet_canvas(amb: str) -> Image.Image:
    closed = Image.open(SPRITES_DIR / f'guilde_hd_{amb}.png').convert('RGBA')
    opened = Image.open(SPRITES_DIR / f'guilde_hd_porte_ouverte_{amb}.png').convert('RGBA')
    shadow = Image.open(SPRITES_DIR / f'guilde_hd_ombre_{amb}.png').convert('RGBA')

    canvas = Image.new('RGBA', (GRID_W * TILE_SIZE, GRID_H * TILE_SIZE), (0, 0, 0, 0))
    canvas.paste(closed.crop((3, 3, 259, 259)), (CLOSED_ORIGIN[0] * TILE_SIZE, CLOSED_ORIGIN[1] * TILE_SIZE))
    canvas.paste(opened.crop((3, 3, 259, 259)), (OPEN_ORIGIN[0] * TILE_SIZE, OPEN_ORIGIN[1] * TILE_SIZE))
    canvas.paste(
        shadow.crop((0, 174, 262, 262)),
        (SHADOW_ORIGIN[0] * TILE_SIZE + SHADOW_PAD[0], SHADOW_ORIGIN[1] * TILE_SIZE + SHADOW_PAD[1]),
    )
    return premultiply(canvas)


def encode_tile_sheet(canvas: Image.Image) -> tuple[bytes, int]:
    tiles: list[tuple[int, int, bytes]] = []
    for ty in range(GRID_H):
        for tx in range(GRID_W):
            cell = canvas.crop((tx * TILE_SIZE, ty * TILE_SIZE, (tx + 1) * TILE_SIZE, (ty + 1) * TILE_SIZE))
            alpha = cell.getchannel('A')
            if alpha.getextrema()[1] == 0:
                continue
            buf = io.BytesIO()
            cell.save(buf, format='PNG', optimize=True)
            tiles.append((tx, ty, buf.getvalue()))

    count = len(tiles)
    data_offset = 8 + 16 * count
    header = bytearray(struct.pack('<ii', TILE_SIZE, count))
    body = bytearray()
    cur = data_offset
    for tx, ty, png in tiles:
        header += struct.pack('<iiq', tx, ty, cur)
        body += struct.pack('<q', len(png))
        body += png
        cur += 8 + len(png)
    return bytes(header) + bytes(body), count


def main() -> int:
    check_only = '--check' in sys.argv[1:]
    TILE_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for amb, bank_name in AMBIANCES:
        canvas = compose_sheet_canvas(amb)
        out_path = TILE_DIR / f'{bank_name}.tile'
        if check_only:
            if not out_path.is_file():
                print(f'MANQUANT : {out_path}')
                ok = False
                continue
            raw = out_path.read_bytes()
            tile_size, count = struct.unpack_from('<ii', raw, 0)
            if tile_size != TILE_SIZE:
                print(f'ERREUR {bank_name} : TileSize={tile_size} != {TILE_SIZE}')
                ok = False
                continue
            seen = {}
            for i in range(count):
                tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
                ln = struct.unpack_from('<q', raw, off)[0]
                seen[(tx, ty)] = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert('RGBA')
            for ty in range(GRID_H):
                for tx in range(GRID_W):
                    expected = canvas.crop((tx * TILE_SIZE, ty * TILE_SIZE, (tx + 1) * TILE_SIZE, (ty + 1) * TILE_SIZE))
                    if expected.getchannel('A').getextrema()[1] == 0:
                        if (tx, ty) in seen:
                            print(f'ERREUR {bank_name} : case vide présente en {(tx, ty)}')
                            ok = False
                    else:
                        if (tx, ty) not in seen or seen[(tx, ty)].tobytes() != expected.tobytes():
                            print(f'ERREUR {bank_name} : pixels divergents en {(tx, ty)}')
                            ok = False
            print(f'OK (--check) {bank_name}.tile ({count} tuiles)')
        else:
            blob, count = encode_tile_sheet(canvas)
            out_path.write_bytes(blob)
            print(f'ÉCRIT {out_path.relative_to(ROOT)} : {len(blob)} octets, {count} tuiles ({GRID_W}×{GRID_H})')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
