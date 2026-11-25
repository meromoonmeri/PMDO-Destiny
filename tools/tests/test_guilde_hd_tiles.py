#!/usr/bin/env python3
"""Vérifie les 4 banques .tile Guilde_HD_* (format PMDO, prémultiplication, alignement)."""
from __future__ import annotations

import io
import struct
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import build_guilde_hd_tiles as builder  # noqa: E402

TILE_DIR = ROOT / 'game' / 'Content' / 'Tile'
SPRITES_DIR = ROOT / 'art' / 'cliff-guilde' / 'sprites'


def read_sheet_pixels(path: Path) -> tuple[int, int, dict[tuple[int, int], Image.Image], Image.Image]:
    raw = path.read_bytes()
    tile_size, count = struct.unpack_from('<ii', raw, 0)
    assert tile_size == builder.TILE_SIZE, (path.name, tile_size)
    tiles: dict[tuple[int, int], Image.Image] = {}
    canvas = Image.new('RGBA', (builder.GRID_W * tile_size, builder.GRID_H * tile_size), (0, 0, 0, 0))
    for i in range(count):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        assert 0 <= tx < builder.GRID_W and 0 <= ty < builder.GRID_H, (path.name, tx, ty)
        assert (tx, ty) not in tiles, (path.name, tx, ty)
        assert 8 + 16 * count <= off <= len(raw) - 8
        ln = struct.unpack_from('<q', raw, off)[0]
        assert 0 < ln <= len(raw) - off - 8
        png = raw[off + 8:off + 8 + ln]
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
        im = Image.open(io.BytesIO(png)).convert('RGBA')
        assert im.size == (tile_size, tile_size)
        # Invariant PMDO : RGBA prémultiplié (r <= a, g <= a, b <= a) et jamais totalement vide
        px = im.tobytes()
        assert any(px[k + 3] > 0 for k in range(0, len(px), 4)), (path.name, tx, ty)
        for k in range(0, len(px), 4):
            a = px[k + 3]
            assert px[k] <= a and px[k + 1] <= a and px[k + 2] <= a, (path.name, tx, ty)
        tiles[(tx, ty)] = im
        canvas.paste(im, (tx * tile_size, ty * tile_size))
    return tile_size, count, tiles, canvas


def main() -> None:
    for amb, bank_name in builder.AMBIANCES:
        tile_path = TILE_DIR / f'{bank_name}.tile'
        assert tile_path.is_file(), f'Banque manquante : {tile_path}'
        tile_size, count, tiles, sheet_img = read_sheet_pixels(tile_path)
        expected = builder.compose_sheet_canvas(amb)
        assert sheet_img.tobytes() == expected.tobytes(), f'Pixels divergents dans {bank_name}.tile'

        # Vérifier l'alignement exact 0.0 px : Guilde en (tx, ty) et Ombre en (tx - 1, ty + 21)
        tx, ty = 10, 10
        comp = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        shadow_crop = sheet_img.crop((0, 34 * tile_size, 34 * tile_size, 46 * tile_size))
        closed_crop = sheet_img.crop((0, 0, 32 * tile_size, 32 * tile_size))
        comp.alpha_composite(shadow_crop, ((tx - 1) * tile_size, (ty + 21) * tile_size))
        comp.alpha_composite(closed_crop, (tx * tile_size, ty * tile_size))

        ref_comp = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        ref_shadow = builder.premultiply(Image.open(SPRITES_DIR / f'guilde_hd_ombre_{amb}.png'))
        ref_closed = builder.premultiply(Image.open(SPRITES_DIR / f'guilde_hd_{amb}.png'))
        ref_x = tx * tile_size - 3
        ref_y = ty * tile_size - 3
        ref_comp.alpha_composite(ref_shadow, (ref_x, ref_y))
        ref_comp.alpha_composite(ref_closed, (ref_x, ref_y))
        assert comp.tobytes() == ref_comp.tobytes(), f'Alignement ombre/guilde imparfait pour {bank_name}'

        # Fermée vs ouverte diffèrent uniquement sur la zone de la porte
        open_crop = sheet_img.crop((34 * tile_size, 0, 66 * tile_size, 32 * tile_size))
        diff_xs = [
            x for y in range(256) for x in range(256)
            if closed_crop.getpixel((x, y)) != open_crop.getpixel((x, y))
        ]
        diff_ys = [
            y for y in range(256) for x in range(256)
            if closed_crop.getpixel((x, y)) != open_crop.getpixel((x, y))
        ]
        assert diff_xs and min(diff_xs) >= 70 and max(diff_xs) <= 185
        assert diff_ys and min(diff_ys) >= 160 and max(diff_ys) <= 240
        print(f'OK {bank_name}.tile : {count} tuiles, RGBA prémultiplié, alignement 0.0 px, porte fermée/ouverte exacte')


if __name__ == '__main__':
    main()
