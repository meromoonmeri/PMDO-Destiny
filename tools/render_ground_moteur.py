#!/usr/bin/env python3
"""Aperçu « en jeu » hors moteur : rejoue le pipeline de dessin de RogueEssence.

Ordre réel (BaseGroundScene.DrawGame) :
    Background (LayeredBG : ciel + nuages)  ->  calques de tuiles visibles

Différence avec tools/preview_maps.py (qui sert à l'inventaire des cartes) :
  * les couches `Background` / `LayeredBG` sont dessinées, avec leur MapLoc ;
  * les nuages `RepeatX` sont répétés et défilent selon `BGMovement.X` (px/s) ;
  * chaque calque de tuiles est pris à sa phase d'animation réelle
    (FrameLength en frames de 1/60 s ; la mer de cliffdaytest a 8 phases à 10) ;
  * une case absente de sa planche `.tile` dessine le damier d'erreur du moteur
    (`GraphicsManager.GetTile` -> `BaseSheet.LoadError()` -> defaultTex 32x32),
    exactement comme en jeu. C'est ce que le correctif de `cliffdaytest` a retiré.

Usage :
    python3 tools/render_ground_moteur.py cliffdaytest --out /tmp/apercu
    python3 tools/render_ground_moteur.py cliffdaytest --anime --duree 3 --fps 10
    python3 tools/render_ground_moteur.py cliffdaytest_aube --bande 300 --anime
    python3 tools/render_ground_moteur.py end_grotte_verdoyante --arene --echelle 2

Sortie PNG ou WebP animé sans perte à taille native, ou agrandissement
par facteur entier sans filtre. Les planches .tile gardent leur taille (8/24 px).

Aucune dépendance hors Pillow.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TICK_HZ = 7200          # FRAME_TICKS_PER_FRAME (120) * 60 fps
DEF = None


def damier(taille: int = 32, cell: int = 8) -> Image.Image:
    im = Image.new('RGBA', (taille, taille), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for i in range(taille // cell):
        for j in range(taille // cell):
            if (i % 2 == 0) == (j % 2 == 0):
                d.rectangle([i * cell, j * cell, i * cell + cell - 1, j * cell + cell - 1],
                            fill=(255, 0, 255, 255))
    return im


def default_tex() -> Image.Image:
    global DEF
    if DEF is None:
        DEF = damier()
    return DEF


class Planches:
    _slots: dict[str, tuple[bytes | None, dict]] = {}
    _tiles: dict[tuple, Image.Image | None] = {}

    @classmethod
    def slots(cls, nom: str):
        if nom in cls._slots:
            return cls._slots[nom]
        for base in ('game/Content/Tile', 'base/Content/Tile'):
            p = ROOT / base / f'{nom}.tile'
            if p.is_file():
                raw = p.read_bytes()
                _, cnt = struct.unpack_from('<ii', raw, 0)
                pos = {(x, y): o for x, y, o in
                       (struct.unpack_from('<iiq', raw, 8 + 16 * i) for i in range(cnt))}
                cls._slots[nom] = (raw, pos)
                return cls._slots[nom]
        cls._slots[nom] = (None, {})
        return cls._slots[nom]

    @classmethod
    def tuile(cls, nom: str, tx: int, ty: int):
        key = (nom, tx, ty)
        if key in cls._tiles:
            return cls._tiles[key]
        raw, pos = cls.slots(nom)
        img = None
        off = pos.get((tx, ty))
        if raw is not None and off:
            try:
                ln = struct.unpack_from('<q', raw, off)[0]
                png = raw[off + 8:off + 8 + ln]
                t = struct.unpack_from('<i', raw, 0)[0]
                full = Image.open(io.BytesIO(png)).convert('RGBA')
                if full.size == (t, t):
                    img = full
            except Exception:
                img = None
        cls._tiles[key] = img
        return img


class Dir:
    _cache: dict[tuple, Image.Image | None] = {}

    @classmethod
    def frame(cls, nom: str, index: int = 0):
        if (nom, index) in cls._cache:
            return cls._cache[(nom, index)]
        img = None
        p = ROOT / 'game/Content/BG' / f'{nom}.dir'
        if not p.is_file():
            p = ROOT / 'base/Content/BG' / f'{nom}.dir'
        if p.is_file():
            raw = p.read_bytes()
            ln = struct.unpack_from('<q', raw, 0)[0]
            tw, th, _rot, frames = struct.unpack_from('<iiii', raw, 8 + ln)
            atlas = Image.open(io.BytesIO(raw[8:8 + ln])).convert('RGBA')
            idx = index % max(1, frames)
            cols = max(1, atlas.width // tw)
            cx, cy = (idx % cols) * tw, (idx // cols) * th
            img = atlas.crop((cx, cy, cx + tw, cy + th))
        cls._cache[(nom, index)] = img
        return img


def coller(canvas: Image.Image, img: Image.Image | None, x: int, y: int) -> None:
    if img is None:
        return
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.width, x + img.width), min(canvas.height, y + img.height)
    if x1 <= x0 or y1 <= y0:
        return
    piece = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    region = canvas.crop((x0, y0, x1, y1))
    canvas.paste(Image.alpha_composite(region, piece), (x0, y0))


def charge(nom: str, *, arene: bool = False) -> dict:
    p = ROOT / (f'game/Data/Map/{nom}.rsmap' if arene else f'game/Data/Ground/{nom}.rsground')
    return json.loads(p.read_text(encoding='utf-8-sig'))['Object']


def _fond(o: dict):
    bg = o.get('Background') or {}
    subs = bg.get('Layers')
    ents = [c.get('BG') for c in subs if isinstance(c, dict)] if isinstance(subs, list) else [bg]
    for b in ents:
        if not isinstance(b, dict):
            continue
        idx = (b.get('BGAnim') or {}).get('AnimIndex') or ''
        if not idx:
            continue
        img = Dir.frame(idx, 0)
        if img is not None:
            yield img, b


def _calque(o: dict, layer: dict, cell: int, W: int, H: int, index: int) -> Image.Image:
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for tx, col in enumerate(layer.get('Tiles') or []):
        for ty, t in enumerate(col):
            for sub in (t.get('Layers') or []):
                frs = sub.get('Frames') or []
                if not frs:
                    continue
                fr = frs[index % len(frs)]
                img = Planches.tuile(fr.get('Sheet') or '', fr['TexLoc']['X'], fr['TexLoc']['Y'])
                if img is not None:
                    coller(canvas, img, tx * cell, ty * cell)
    return canvas


def prepare(o: dict, *, arene: bool = False) -> dict:
    # Les étages emploient GraphicsManager.TileSize, pas le TexSize du ground.
    cell = 24 if arene else int(o.get('TexSize') or 1) * 8
    layers = [l for l in (o.get('Layers') or []) if l.get('Visible', True)]
    ref = next((l.get('Tiles') for l in layers if l.get('Tiles')), None) or []
    W, H = len(ref) * cell, (len(ref[0]) if ref else 0) * cell
    plans = []
    for l in layers:
        maxf = 1
        fl = 10
        for col in (l.get('Tiles') or []):
            for c in col:
                for s in c.get('Layers', []):
                    maxf = max(maxf, len(s.get('Frames') or []))
                    fl = int(s.get('FrameLength') or 10)
        plans.append((l, maxf, fl, {}))
    return dict(cell=cell, W=W, H=H, plans=plans, o=o)


def rendu(p: dict, tick: int) -> tuple[Image.Image, int]:
    o, cell, W, H = p['o'], p['cell'], p['W'], p['H']
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    seconde = tick // TICK_HZ

    for img, b in _fond(o):
        mvt = b.get('BGMovement') or {}
        bx = int((b.get('MapLoc') or {}).get('X', 0)) + int(mvt.get('X', 0)) * int(seconde)
        by = int((b.get('MapLoc') or {}).get('Y', 0)) + int(mvt.get('Y', 0)) * int(seconde)
        if b.get('RepeatX'):
            x = bx % img.width - img.width
            while x < W:
                coller(canvas, img, x, by)
                x += img.width
        else:
            coller(canvas, img, bx, by)

    erreurs = 0
    for layer, maxf, fl, cache in p['plans']:
        idx = 0 if (maxf <= 1 or fl <= 0) else int(tick // (fl * 120) % maxf)
        if idx not in cache:
            cache[idx] = _calque(o, layer, cell, W, H, idx)
        coller(canvas, cache[idx], 0, 0)

    # comptage des damiers d'erreur (une case orpheline = un damier en jeu)
    for layer, _m, _f, _c in p['plans']:
        for col in (layer.get('Tiles') or []):
            for c in col:
                for s in c.get('Layers', []):
                    for fr in (s.get('Frames') or [])[:1]:
                        raw, pos = Planches.slots(fr.get('Sheet') or '')
                        if raw is not None and (fr['TexLoc']['X'], fr['TexLoc']['Y']) not in pos:
                            erreurs += 1
    return canvas, erreurs


def preserver_pixels(im: Image.Image, echelle: int = 1) -> Image.Image:
    """Jamais de rééchantillonnage non entier ni de couleur interpolée."""
    if not isinstance(echelle, int) or echelle < 1:
        raise ValueError('échelle entière positive requise')
    if echelle == 1:
        return im
    return im.resize((im.width * echelle, im.height * echelle), Image.Resampling.NEAREST)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cartes', nargs='+', help='nom(s) de carte sans extension')
    ap.add_argument('--arene', action='store_true', help='rendre les calques de tuiles d’un .rsmap (sans combattants)')
    ap.add_argument('--echelle', type=int, choices=(1, 2, 3, 4), default=1, help='rapport entier, 1 = taille originale')
    ap.add_argument('--out', default=None, help='dossier de sortie')
    ap.add_argument('--anime', action='store_true', help='produire un WebP animé')
    ap.add_argument('--duree', type=float, default=3.0, help='durée (s) du WebP animé')
    ap.add_argument('--fps', type=int, default=10)
    ap.add_argument('--bande', type=int, default=0,
                    help='ne garder que les N premiers pixels de haut (0 = carte entière)')
    args = ap.parse_args()

    out = Path(args.out) if args.out else ROOT / 'art/previews/cliffdaytest_4_ambiances'
    out.mkdir(parents=True, exist_ok=True)

    for nom in args.cartes:
        o = charge(nom, arene=args.arene)
        p = prepare(o, arene=args.arene)
        if args.anime:
            n = max(1, int(args.duree * args.fps))
            frames = []
            for i in range(n):
                im, _ = rendu(p, int(i * TICK_HZ / args.fps))
                im = im.convert('RGB')
                if args.bande:
                    im = im.crop((0, 0, im.width, args.bande))
                frames.append(preserver_pixels(im, args.echelle))
            dest = out / f'anime_{nom}.webp'
            frames[0].save(dest, save_all=True, append_images=frames[1:],
                           duration=int(1000 / args.fps), loop=0, format='WEBP',
                           lossless=True, method=5)
            print(f'{nom}: {n} images -> {dest}')
        else:
            im, err = rendu(p, 0)
            dest = out / f'carte_{nom}.png'
            im = preserver_pixels(im.convert('RGB'), args.echelle)
            im.save(dest, optimize=True)
            print(f'{nom}: {im.width}x{im.height}px, {err} case(s) orpheline(s) -> {dest}')


if __name__ == '__main__':
    main()
