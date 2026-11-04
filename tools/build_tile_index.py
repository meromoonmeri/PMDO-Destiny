#!/usr/bin/env python3
"""Regénère game/Content/Tile/index.idx à partir des en-têtes des planches .tile.

Même construction que ImportHelper.BuildTileIndex du moteur (et que le contrôle de
tools/validate.py) : int32 nombre de planches, puis pour chaque planche (ordre trié
par nom, comparaison ordinale) : nom en chaîne .NET (longueur 7 bits + UTF-8) suivi
de la copie exacte de l'en-tête de la planche (int32 TileSize, int32 count,
count × (int32 X, int32 Y, int64 offset)).

Usage : python3 tools/build_tile_index.py [--check]
  --check : ne réécrit rien, compare seulement l'index existant à celui calculé.
"""
import io
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILE_DIR = ROOT / 'game' / 'Content' / 'Tile'


def write_7bit(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def node(path: Path) -> bytes:
    with path.open('rb') as handle:
        raw = handle.read(8)
        if len(raw) != 8:
            raise ValueError(f'planche tronquée : {path}')
        _, count = struct.unpack('<ii', raw)
        body = handle.read(count * 16)
        if len(body) != count * 16:
            raise ValueError(f'en-tête incomplet : {path}')
        return raw + body


def build() -> bytes:
    tiles = sorted(TILE_DIR.glob('*.tile'), key=lambda p: p.stem)
    out = io.BytesIO()
    out.write(struct.pack('<i', len(tiles)))
    for path in tiles:
        name = path.stem.encode('utf-8')
        out.write(write_7bit(len(name)))
        out.write(name)
        out.write(node(path))
    return out.getvalue()


def main() -> int:
    data = build()
    target = TILE_DIR / 'index.idx'
    if '--check' in sys.argv[1:]:
        current = target.read_bytes() if target.is_file() else b''
        if current == data:
            print(f'index.idx conforme ({len(data)} octets, {struct.unpack_from("<i", data)[0]} planches)')
            return 0
        print('index.idx DIFFÈRE de l\'index calculé (relancer sans --check pour le réécrire)')
        return 1
    target.write_bytes(data)
    print(f'index.idx écrit : {len(data)} octets, {struct.unpack_from("<i", data)[0]} planches')
    if len(data) > 100 * 1024 * 1024:
        print('ATTENTION : > 100 Mio — fichier généré ignoré par Git, à ne pas versionner en blob ordinaire')
    return 0


if __name__ == '__main__':
    sys.exit(main())
