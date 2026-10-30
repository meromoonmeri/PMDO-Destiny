#!/usr/bin/env python3
"""Ajoute des TileSheets à Content/Tile/index.idx (format TileGuide de RogueEssence).

Format (RogueEssence/Content/Indices/TileIndex.cs) :

    TileGuide.Save   : int32 count, puis pour chaque entrée :
                         string  clé             (BinaryWriter.Write(string) = LEB128 + UTF-8)
                         TileIndexNode :
                             int32 TileSize
                             int32 nPositions
                             nPositions × (int32 x, int32 y, int64 offset)

Le même TileIndexNode est écrit en tête de chaque fichier .tile ; il suffit donc
de le relire pour construire l'entrée correspondante, sans réécrire le .tile.
"""
import struct
import sys
from pathlib import Path


def read_7bit_string(buf, pos):
    length = 0
    shift = 0
    while True:
        b = buf[pos]
        pos += 1
        length |= (b & 0x7F) << shift
        if not b & 0x80:
            break
        shift += 7
    return buf[pos:pos + length].decode("utf-8"), pos + length


def write_7bit_string(text):
    data = text.encode("utf-8")
    n = len(data)
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            break
    return bytes(out) + data


def parse_guide(buf, offset=0):
    """Retourne (noms, fin_du_bloc) sans matérialiser les positions."""
    count = struct.unpack_from("<i", buf, offset)[0]
    pos = offset + 4
    names = []
    for _ in range(count):
        name, pos = read_7bit_string(buf, pos)
        names.append(name)
        tilesize, npos = struct.unpack_from("<ii", buf, pos)
        pos += 8 + npos * 16          # x:int32, y:int32, offset:int64
    return names, pos


def read_tile_header(path):
    """Relit le TileIndexNode écrit en tête d'un .tile et le renvoie tel quel."""
    buf = path.read_bytes()
    if len(buf) < 8:
        raise ValueError(f"{path.name}: fichier trop court")
    tilesize, npos = struct.unpack_from("<ii", buf, 0)
    if tilesize <= 0 or npos < 0 or 8 + npos * 16 > len(buf):
        raise ValueError(f"{path.name}: en-tête de tuiles invalide")
    return buf[:8 + npos * 16]


def main(index_path, tile_dir):
    index_path = Path(index_path)
    tile_dir = Path(tile_dir)
    buf = index_path.read_bytes()
    names, end_of_entries = parse_guide(buf)
    existing = set(names)

    additions = []
    for tile in sorted(tile_dir.glob("*.tile")):
        if tile.stem in existing:
            continue
        additions.append((tile.stem, read_tile_header(tile)))

    if not additions:
        print("aucun TileSheet à ajouter")
        return 0

    out = bytearray()
    out += struct.pack("<i", len(names) + len(additions))
    out += buf[4:end_of_entries]          # entrées existantes, telles quelles
    for name, node in additions:
        out += write_7bit_string(name)
        out += node
    if end_of_entries != len(buf):
        raise SystemExit("index.idx contient des octets inattendus après les entrées")
    index_path.write_bytes(out)
    print(f"{len(additions)} TileSheets ajoutés à {index_path} "
          f"({len(names)} → {len(names) + len(additions)} entrées, "
          f"{len(buf)} → {len(out)} octets)")
    for name, _ in additions:
        print("   +", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
