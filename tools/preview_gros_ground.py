#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aperçu d'un .rsground TROP GROS pour `preview_maps.py` (ex. 330 Mo).

`preview_maps.py` fait `json.loads` sur la carte entière : au-delà de ~250 Mo la
désérialisation dépasse la RAM (2 Go ici) et le processus est tué par le noyau
(SIGKILL, sortie 137). Ce script produit la même image, mais sans jamais
matérialiser la carte : le fichier est mappé (mmap) et découpé au niveau C par
des expressions régulières, puis les cellules sont rendues au fil de l'eau.

Découpage :
- `"Tiles": [ ... ]` -> un bloc par calque de tuiles ;
- dans un bloc, chaque cellule commence à `"Layers": [` ;
- dans une cellule, l'ordre du fichier donne les sous-calques : `"Sheet"` puis
  `"TexLoc" {"X","Y"}` (première pose = Frames[0], comme le moteur) ;
- la grille est déduite de la première colonne (nombre de cellules = hauteur),
  la largeur venant du nombre total de cellules du calque.

Fonds, décorations et ordre des calques suivent les mêmes conventions que
`preview_maps.py`. Entités et animation ne sont pas rendues : aperçu statique.

Usage :
    python tools/preview_gros_ground.py <carte.rsground> <sortie.png>
"""
from __future__ import annotations

import json
import mmap
import re
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preview_maps as pm  # noqa: E402  (SheetReader, DirReader, find_file, paste_over, localized_name)

RE_SHEET = re.compile(rb'"Sheet"\s*:\s*"([^"]*)"')
RE_TEXLOC = re.compile(rb'"TexLoc"\s*:\s*\{[^{}]*?"X"\s*:\s*(-?\d+)[^{}]*?"Y"\s*:\s*(-?\d+)')
RE_CELL = re.compile(rb'"Layers"\s*:\s*\[')
RE_TILES = re.compile(rb'"Tiles"\s*:\s*\[')
RE_VISIBLE = re.compile(rb'"Visible"\s*:\s*(true|false)')


def bloc(buf, start, open_c=None, close_c=None):
    """Extrait le texte du premier objet/tableau équilibré à partir de `start`."""
    if open_c is None:  # détection : la valeur peut être un objet ou un tableau
        while buf[start] in (0x20, 0x09, 0x0D, 0x0A):
            start += 1
        open_c = bytes(buf[start:start + 1])
        close_c = b"}" if open_c == b"{" else b"]"
    depth = 0
    i = start
    n = len(buf)
    in_str = False
    while i < n:
        c = buf[i]
        if in_str:
            if c == 0x5C:
                i += 2
                continue
            if c == 0x22:
                in_str = False
            i += 1
            continue
        if c == 0x22:
            in_str = True
        elif c == open_c[0]:
            depth += 1
        elif c == close_c[0]:
            depth -= 1
            if depth == 0:
                return bytes(buf[start:i + 1])
        i += 1
    raise ValueError("bloc non équilibré")


def champ(buf, nom):
    """Valeur simple d'un champ racine : nombre, booléen ou chaîne."""
    m = re.search(rb'"%s"\s*:\s*(-?\d+|true|false|"(?:[^"\\]|\\.)*")' % nom.encode(), buf)
    if not m:
        return None
    v = m.group(1)
    if v.startswith(b'"'):
        return v[1:-1].decode("utf-8", "replace")
    return v.decode()


def position(buf, nom):
    m = re.search(rb'"%s"\s*:\s*(?=[\{\[])' % nom.encode(), buf)
    return m.end() if m else None


class Rendu:
    def __init__(self):
        self.sheets = {}
        self.tiles = {}
        self.cells = {}
        self.missing_sheets = set()
        self.missing_tiles = 0
        self.pastes = 0

    def tile(self, sheet, tx, ty):
        key = (sheet, tx, ty)
        if key in self.tiles:
            return self.tiles[key]
        rd = self.sheets.get(sheet, 0)
        if rd == 0:
            path = pm.find_file([pm.GAME_TILE, pm.BASE_TILE], f"{sheet}.tile")
            rd = pm.SheetReader(path) if path else None
            if rd is None:
                self.missing_sheets.add(sheet)
            self.sheets[sheet] = rd
        tim = rd.get_tile(tx, ty) if rd else None
        if tim is None:
            self.missing_tiles += 1
        self.tiles[key] = tim
        return tim

    def cellule(self, cle, cell):
        img = self.cells.get(cle)
        if img is not None or cle in self.cells:
            return img
        for sheet, sx, sy in cle:
            tim = self.tile(sheet, sx, sy)
            if tim is None:
                continue
            if tim.size != (cell, cell):
                tim = tim.resize((cell, cell), Image.NEAREST)
            img = tim.copy() if img is None else Image.alpha_composite(img, tim)
        self.cells[cle] = img
        return img


def main(src, dst):
    t0 = time.time()
    path = Path(src)
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        buf = mm  # le BOM éventuel précède le premier objet : il ne gêne aucun repérage

        tex = int(champ(buf, "TexSize") or 1)
        cell = tex * 8
        asset = champ(buf, "AssetName") or path.stem
        p = position(buf, "Name")
        nom = pm.localized_name(json.loads(bloc(buf, p)) if p is not None else None, path.stem)

        # ---- fonds
        fonds = []
        p = position(buf, "Background")
        if p is not None:
            bg = json.loads(bloc(buf, p))
            couches = bg.get("Layers") if isinstance(bg.get("Layers"), list) else None
            entrees = [c.get("BG") for c in couches if isinstance(c, dict)] if couches else [bg]
            for e in entrees:
                if not isinstance(e, dict):
                    continue
                anim = e.get("BGAnim") or e.get("Anim") or {}
                loc = e.get("MapLoc") or e.get("Loc") or {}
                fonds.append((anim.get("AnimIndex") or "", anim.get("Alpha", 255),
                              int(loc.get("X", 0)), int(loc.get("Y", 0))))

        # ---- décorations
        decors = []
        p = position(buf, "Decorations")
        if p is not None:
            for dl in json.loads(bloc(buf, p)) or []:
                if not isinstance(dl, dict) or not dl.get("Visible", True):
                    continue
                for a in dl.get("Anims") or []:
                    anim = a.get("Anim") or a.get("BGAnim") or {}
                    loc = a.get("Loc") or a.get("MapLoc") or {}
                    decors.append((int(dl.get("Layer", 0)), anim.get("AnimIndex") or "",
                                   anim.get("Alpha", 255), int(loc.get("X", 0)), int(loc.get("Y", 0))))

        blocs = [(m.start(), m.end()) for m in RE_TILES.finditer(buf)]
        if not blocs:
            raise SystemExit("aucun calque de tuiles trouvé")

        # ---- géométrie : hauteur = cellules de la 1re colonne du 1er calque
        rendu = Rendu()

        def frames_dans(a, b):
            """[(pos, ('s', nom)) | (pos, ('t', x, y))] triés, sur l'intervalle [a, b)."""
            ev = [(m.start(), (0, m.group(1).decode("utf-8", "replace"))) for m in RE_SHEET.finditer(buf, a, b)]
            ev += [(m.start(), (1, int(m.group(1)), int(m.group(2)))) for m in RE_TEXLOC.finditer(buf, a, b)]
            ev.sort(key=lambda e: e[0])
            return ev

        def cellules(a, b):
            return [m.start() for m in RE_CELL.finditer(buf, a, b)]

        # première colonne du premier calque
        debut = blocs[0][1]
        pos_cells = cellules(debut, blocs[1][0] if len(blocs) > 1 else len(buf))
        fin_col0 = None
        depth = 0
        j = debut
        vu = False
        while j < len(buf):
            c = buf[j]
            if c == 0x5B:  # [
                depth += 1
                vu = vu or depth == 1
            elif c == 0x5D:  # ]
                depth -= 1
                if vu and depth == 0:
                    fin_col0 = j
                    break
            j += 1
        ny = sum(1 for q in pos_cells if q < fin_col0)
        total = len(pos_cells)
        if ny == 0:
            raise SystemExit("grille illisible")
        nx = round(total / ny)
        map_w, map_h = nx * cell, ny * cell
        print(f"{path.name} : {nx}x{ny} cases, {cell}px -> {map_w}x{map_h}px, {len(blocs)} calques")

        # ---- canevas + fonds
        canvas = Image.new("RGBA", (map_w, map_h), (0, 0, 0, 0))
        for idx, alpha, x, y in fonds:
            img = None
            if idx:
                q = pm.find_file([pm.GAME_BG, pm.BASE_BG, pm.GAME_OBJ, pm.BASE_OBJ], f"{idx}.dir")
                if q is None:
                    rendu.missing_sheets.add(idx)
                else:
                    img = pm.DirReader.frame0(q)
                    if img is not None and 0 <= alpha < 255:
                        img = img.copy()
                        img.putalpha(img.getchannel("A").point(lambda a, al=alpha: a * al // 255))
            if img is not None:
                pm.paste_over(canvas, img, x, y)

        cache_decors = {}

        def decor_img(idx):
            if idx in cache_decors:
                return cache_decors[idx]
            q = pm.find_file([pm.GAME_BG, pm.BASE_BG, pm.GAME_OBJ, pm.BASE_OBJ], f"{idx}.dir")
            if q is None:
                rendu.missing_sheets.add(idx)
            img = pm.DirReader.frame0(q) if q else None
            cache_decors[idx] = img
            return img

        # ---- calques
        rangs = []
        for li, (a, b) in enumerate(blocs):
            fin = blocs[li + 1][0] if li + 1 < len(blocs) else len(buf)
            m = list(RE_VISIBLE.finditer(buf, a, fin))
            visible = True if not m else m[-1].group(1) == b"true"
            rang = li
            r = re.search(rb'"Layer"\s*:\s*(-?\d+)', bytes(buf[a:fin])[:2000])
            if r:
                rang = int(r.group(1))
            rangs.append(rang)
            if not visible:
                continue
            pos = cellules(a, fin)
            ev = frames_dans(a, fin)
            ei = 0
            for k, cpos in enumerate(pos):
                tx, ty = divmod(k, ny)
                fin_c = pos[k + 1] if k + 1 < len(pos) else fin
                cle = []
                sheet = None
                while ei < len(ev) and ev[ei][0] < fin_c:
                    e = ev[ei][1]
                    if e[0] == 0:
                        sheet = e[1]
                    elif sheet:
                        cle.append((sheet, e[1], e[2]))
                    ei += 1
                if not cle:
                    continue
                img = rendu.cellule(tuple(cle), cell)
                if img is not None:
                    pm.paste_over(canvas, img, tx * cell, ty * cell)
                    rendu.pastes += 1
            # décorations du même rang
            for rr, idx, alpha, x, y in decors:
                if rr == rang and idx:
                    img = decor_img(idx)
                    if img is not None:
                        pm.paste_over(canvas, img, x, y)
            print(f"  calque {li:2d} (rang {rang:2d}) {'visible' if visible else 'masqué '} : "
                  f"{len(pos)} cellules, {time.time() - t0:.1f}s")

        rang_max = max(rangs) if rangs else -1
        for rr, idx, alpha, x, y in decors:
            if rr > rang_max and idx:
                img = decor_img(idx)
                if img is not None:
                    pm.paste_over(canvas, img, x, y)
        mm.close()

    out = Path(dst)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(f"\n{out} — {canvas.size[0]}x{canvas.size[1]} px, {out.stat().st_size / 1e6:.2f} Mo")
    print(f"cellules collées : {rendu.pastes} ; tuiles/composants en cache : {len(rendu.cells)}")
    print(f"planches absentes ({len(rendu.missing_sheets)}) : {sorted(rendu.missing_sheets)}")
    print(f"tuiles introuvables : {rendu.missing_tiles} ; durée {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
