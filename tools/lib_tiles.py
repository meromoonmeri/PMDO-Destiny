"""Helpers de lecture/écriture des banques `.tile` et des `.rsground` (PMDO 0.8.12)."""
from __future__ import annotations

import io
import json
import struct
from pathlib import Path

from PIL import Image

TILE = 8


def read_tilesheet(path):
    raw = Path(path).read_bytes()
    tsize, n = struct.unpack_from("<ii", raw, 0)
    cells = {}
    for i in range(n):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + 16 * i)
        ln = struct.unpack_from("<q", raw, off)[0]
        im = Image.open(io.BytesIO(raw[off + 8: off + 8 + ln])).convert("RGBA")
        cells[(tx, ty)] = im
    return tsize, cells


def write_tilesheet(path, cells, tile_size=TILE):
    items = sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0]))
    header = struct.pack("<ii", tile_size, len(items))
    entries, body = b"", b""
    cur = 8 + 16 * len(items)
    for (tx, ty), im in items:
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=False)
        png = buf.getvalue()
        entries += struct.pack("<iiq", tx, ty, cur)
        body += struct.pack("<q", len(png)) + png
        cur += 8 + len(png)
    Path(path).write_bytes(header + entries + body)
    return len(items)


def load_map(path):
    d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return d, d["Object"]


def save_map(path, d):
    Path(path).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def map_dims(obj):
    nx = len(obj["obstacles"])
    ny = len(obj["obstacles"][0]) if nx else 0
    return nx, ny


def layer_cells(obj, li):
    out = {}
    for x, col in enumerate(obj["Layers"][li]["Tiles"]):
        for y, cell in enumerate(col):
            tl = cell.get("Layers") or []
            if tl and tl[0].get("Frames"):
                f = tl[0]["Frames"][0]
                out[(x, y)] = (f["Sheet"], f["TexLoc"]["X"], f["TexLoc"]["Y"])
    return out


def render_layer(obj, li, banks, nx, ny):
    im = Image.new("RGBA", (nx * TILE, ny * TILE), (0, 0, 0, 0))
    for (x, y), (sheet, tx, ty) in layer_cells(obj, li).items():
        tile = banks[sheet].get((tx, ty))
        if tile is not None:
            im.paste(tile, (x * TILE, y * TILE))
    return im


def render_map(obj, banks, nx, ny):
    comp = Image.new("RGBA", (nx * TILE, ny * TILE), (0, 0, 0, 0))
    for li in range(len(obj["Layers"])):
        comp.alpha_composite(render_layer(obj, li, banks, nx, ny))
    return comp
