#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonde : affiche la pile de tuiles d'une case (tx, ty) pour chaque calque.

Sert à comprendre où vivent le sol, les chemins et la végétation avant d'éditer.
Usage : python probe_cell.py <fichier.rsground> tx ty [tx ty ...]
"""
import mmap
import re
import sys
from pathlib import Path

NX, NY = 200, 500
RE_TILES = re.compile(rb'"Tiles"\s*:\s*\[')
RE_CELL = re.compile(rb'"Layers"\s*:\s*\[')
RE_SHEET = re.compile(rb'"Sheet"\s*:\s*"([^"]*)"')
RE_TEXLOC = re.compile(rb'"TexLoc"\s*:\s*\{[^{}]*?"X"\s*:\s*(-?\d+)[^{}]*?"Y"\s*:\s*(-?\d+)')
RE_NOM = re.compile(rb'"Name"\s*:\s*"([^"]*)"')


def calques(mm):
    pos = [m.start() for m in RE_TILES.finditer(mm)]
    out = []
    for i, a in enumerate(pos):
        b = pos[i + 1] if i + 1 < len(pos) else len(mm)
        nom = RE_NOM.search(bytes(mm[max(0, a - 400):a]))
        out.append((i, nom.group(1).decode() if nom else '?', a, b))
    return out


def pile(mm, a, b, tx, ty):
    cells = [m.start() for m in RE_CELL.finditer(mm, a, b)]
    k = tx * NY + ty
    if k >= len(cells):
        return []
    c = cells[k]
    fin = cells[k + 1] if k + 1 < len(cells) else b
    txt = bytes(mm[c:fin])
    if b'"Layers": []' in txt:
        return []
    subs = []
    for m in RE_TEXLOC.finditer(txt):
        avant = txt[:m.start()]
        s = RE_SHEET.findall(avant)
        subs.append((s[-1].decode() if s else '?', int(m.group(1)), int(m.group(2))))
    return subs


def main():
    p = Path(sys.argv[1])
    coords = [(int(sys.argv[i]), int(sys.argv[i + 1])) for i in range(2, len(sys.argv) - 1, 2)]
    with open(p, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        for tx, ty in coords:
            print(f'\n=== case ({tx}, {ty}) — px ({tx * 8}, {ty * 8}) ===')
            for i, nom, a, b in calques(mm):
                s = pile(mm, a, b, tx, ty)
                if s:
                    print(f'  calque {i:2d} {nom[:26]:26} : ' + ' | '.join(f'{sh}@{x},{y}' for sh, x, y in s))
        mm.close()


if __name__ == '__main__':
    sys.exit(main())
