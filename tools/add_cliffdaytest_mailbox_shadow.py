#!/usr/bin/env python3
"""Ajoute une ombre au sol canonique et centrée sous la boîte aux lettres de cliffdaytest (tx=82..83, ty=57..58).

Respecte intégralement les invariants de tools/tests/test_cliffdaytest_integrite.py :
- Pixels opaques (alpha == 255) sur PICHU_CLIFF_DAY_TERRAIN (couleurs canoniques du panneau Mid Signpost :
  cœur d'ombre (128, 112, 80) et transition d'herbe (152, 136, 48), centrés à x = 7.5 sur la grille 16x16 tx=82..83).
- Propagation par LUTs exactes vers _AUBE_FILTRE, _CREP_FILTRE et _NUIT_FILTRE sur les 4 phases (ty + 99 * p).
- Resynchronisation bit-à-bit de CLIFFDAYTEST_BATTLE_BASE_24.tile via cliffdaytest.rsground Layers[1..3].
"""
from __future__ import annotations

import io
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TILE_DIR = ROOT / "game" / "Content" / "Tile"
GROUND_DIR = ROOT / "game" / "Data" / "Ground"
PHASES = 4
PHASE_STRIDE = 99
MAP_W, MAP_H = 123, 99
MAP24_W, MAP24_H = (MAP_W * 8) // 24, (MAP_H * 8) // 24

SHADOW_CORE = (128, 112, 80, 255)
SHADOW_RIM  = (152, 136, 48, 255)

MAILBOX_SHADOW_PIXELS: dict[tuple[int, int], tuple[int, int, int, int]] = {}
for lx in range(4, 12):
    MAILBOX_SHADOW_PIXELS[(lx, 5)] = SHADOW_RIM if lx in (4, 11) else SHADOW_CORE
for ly in (6, 7):
    for lx in range(2, 14):
        MAILBOX_SHADOW_PIXELS[(lx, ly)] = SHADOW_RIM if lx in (2, 13) else SHADOW_CORE
for lx in range(3, 13):
    MAILBOX_SHADOW_PIXELS[(lx, 8)] = SHADOW_RIM if lx in (3, 12) else SHADOW_CORE
for lx in range(5, 11):
    MAILBOX_SHADOW_PIXELS[(lx, 9)] = SHADOW_RIM


def read_tile_sheet(path: Path) -> tuple[int, dict[tuple[int, int], Image.Image]]:
    data = path.read_bytes()
    tile_size, count = struct.unpack_from("<ii", data, 0)
    entries = [struct.unpack_from("<iiq", data, 8 + i * 16) for i in range(count)]
    tiles: dict[tuple[int, int], Image.Image] = {}
    for tx, ty, off in entries:
        (png_len,) = struct.unpack_from("<q", data, off)
        im = Image.open(io.BytesIO(data[off + 8 : off + 8 + png_len])).convert("RGBA")
        px = bytearray(im.tobytes())
        for k in range(0, len(px), 4):
            a = px[k + 3]
            if 0 < a < 255:
                px[k] = min(255, round(px[k] * 255.0 / a))
                px[k + 1] = min(255, round(px[k + 1] * 255.0 / a))
                px[k + 2] = min(255, round(px[k + 2] * 255.0 / a))
            elif a == 0:
                px[k] = px[k + 1] = px[k + 2] = 0
        tiles[(tx, ty)] = Image.frombytes("RGBA", im.size, bytes(px))
    return tile_size, tiles


def write_tile_sheet(path: Path, tile_size: int, tiles: dict[tuple[int, int], Image.Image]) -> None:
    keys = sorted(tiles.keys(), key=lambda k: (k[1], k[0]))
    blobs: list[bytes] = []
    for k in keys:
        im = tiles[k].convert("RGBA")
        px = bytearray(im.tobytes())
        for idx in range(0, len(px), 4):
            a = px[idx + 3]
            if a == 0:
                px[idx] = px[idx + 1] = px[idx + 2] = 0
            elif a < 255:
                px[idx] = (px[idx] * a + 127) // 255
                px[idx + 1] = (px[idx + 1] * a + 127) // 255
                px[idx + 2] = (px[idx + 2] * a + 127) // 255
        pre = Image.frombytes("RGBA", im.size, bytes(px))
        buf = io.BytesIO()
        pre.save(buf, format="PNG", optimize=False)
        blobs.append(buf.getvalue())

    header = bytearray(struct.pack("<ii", tile_size, len(keys)))
    offset = 8 + 16 * len(keys)
    payload = bytearray()
    for (tx, ty), blob in zip(keys, blobs):
        header.extend(struct.pack("<iiq", tx, ty, offset))
        chunk = struct.pack("<q", len(blob)) + blob
        payload.extend(chunk)
        offset += len(chunk)
    path.write_bytes(bytes(header + payload))


def build_channel_luts(day_tiles: dict, amb_tiles: dict) -> tuple[list[int], list[int], list[int]]:
    maps = [defaultdict(Counter) for _ in range(3)]
    for k, d_im in day_tiles.items():
        if k[1] >= PHASE_STRIDE or k not in amb_tiles:
            continue
        db = d_im.tobytes()
        ab = amb_tiles[k].tobytes()
        for i in range(0, len(db), 4):
            if db[i + 3] == 255 and ab[i + 3] == 255:
                for c in range(3):
                    maps[c][db[i + c]][ab[i + c]] += 1
    luts: list[list[int]] = []
    for c in range(3):
        known = {dv: cnt.most_common(1)[0][0] for dv, cnt in maps[c].items()}
        xs = sorted(known)
        lut = []
        for v in range(256):
            if v in known:
                lut.append(known[v])
            elif v < xs[0]:
                lut.append(known[xs[0]])
            elif v > xs[-1]:
                lut.append(known[xs[-1]])
            else:
                lo = max(x for x in xs if x < v)
                hi = min(x for x in xs if x > v)
                t = (v - lo) / (hi - lo)
                lut.append(round(known[lo] * (1 - t) + known[hi] * t))
        luts.append(lut)
    return luts[0], luts[1], luts[2]


def apply_luts_to_tile(im: Image.Image, luts: tuple[list[int], list[int], list[int]]) -> Image.Image:
    rl, gl, bl = luts
    px = bytearray(im.tobytes())
    for i in range(0, len(px), 4):
        if px[i + 3] > 0:
            px[i] = rl[px[i]]
            px[i + 1] = gl[px[i + 1]]
            px[i + 2] = bl[px[i + 2]]
    return Image.frombytes("RGBA", im.size, bytes(px))


def main() -> None:
    ts, sea = read_tile_sheet(TILE_DIR / "PICHU_CLIFF_DAY_SEA.tile")
    _, ter = read_tile_sheet(TILE_DIR / "PICHU_CLIFF_DAY_TERRAIN.tile")
    _, can = read_tile_sheet(TILE_DIR / "PICHU_CLIFF_DAY_CANOPY.tile")

    amb_sheets = {}
    amb_luts = {}
    for suf in ("_AUBE_FILTRE", "_CREP_FILTRE", "_NUIT_FILTRE"):
        _, amb_t = read_tile_sheet(TILE_DIR / f"PICHU_CLIFF_DAY_TERRAIN{suf}.tile")
        amb_sheets[suf] = amb_t
        amb_luts[suf] = build_channel_luts(ter, amb_t)

    for p in range(PHASES):
        y_off = p * PHASE_STRIDE
        sub_imgs = {(dx, dy): ter[(82 + dx, 57 + dy + y_off)].copy() for dx in range(2) for dy in range(2)}
        for (lx, ly), rgba in MAILBOX_SHADOW_PIXELS.items():
            sub_imgs[(lx // 8, ly // 8)].putpixel((lx % 8, ly % 8), rgba)
        for (dx, dy), im_u in sub_imgs.items():
            coord = (82 + dx, 57 + dy + y_off)
            ter[coord] = im_u
            for suf in ("_AUBE_FILTRE", "_CREP_FILTRE", "_NUIT_FILTRE"):
                amb_sheets[suf][coord] = apply_luts_to_tile(im_u, amb_luts[suf])

    write_tile_sheet(TILE_DIR / "PICHU_CLIFF_DAY_TERRAIN.tile", ts, ter)
    for suf, sheet in amb_sheets.items():
        write_tile_sheet(TILE_DIR / f"PICHU_CLIFF_DAY_TERRAIN{suf}.tile", ts, sheet)
    print("[OK] Ombre centrée appliquée sur (82..83, 57..58) x 4 phases x 4 ambiances")

    # Resynchronize CLIFFDAYTEST_BATTLE_BASE_24.tile using cliffdaytest.rsground Layers[1..3]
    bts, battle_tiles = read_tile_sheet(TILE_DIR / "CLIFFDAYTEST_BATTLE_BASE_24.tile")
    day_obj = json.loads((GROUND_DIR / "cliffdaytest.rsground").read_text(encoding="utf-8-sig"))["Object"]
    for ph in range(PHASES):
        comp = Image.new("RGBA", (MAP_W * 8, MAP_H * 8), (0, 0, 0, 0))
        for li in (1, 2, 3):
            tiles = day_obj["Layers"][li]["Tiles"]
            for x in range(MAP_W):
                for y in range(MAP_H):
                    for sub in tiles[x][y].get("Layers", []):
                        frs = sub["Frames"]
                        fr = frs[ph % len(frs)]
                        sh = sea if "SEA" in fr["Sheet"] else (ter if "TERRAIN" in fr["Sheet"] else can)
                        loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                        if loc in sh:
                            comp.alpha_composite(sh[loc], (x * 8, y * 8))
        for rx in range(MAP24_W):
            for ry in range(12, MAP24_H):
                battle_tiles[(rx, ry + MAP24_H * ph)] = comp.crop(
                    (rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24)
                )
    write_tile_sheet(TILE_DIR / "CLIFFDAYTEST_BATTLE_BASE_24.tile", bts, battle_tiles)
    print("[OK] CLIFFDAYTEST_BATTLE_BASE_24.tile resynchronisé bit-à-bit !")


if __name__ == "__main__":
    main()
