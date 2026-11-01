#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les sprites pixel-art de l'étoile du quiz de personnalité.

Produit dans game/Content/BG/ :
  * quiz_star_lumiere_1.dir  — lumières éparses qui scintillent (4 frames) ;
  * quiz_star_lumiere_2.dir  — les lumières convergent vers le centre (4 frames) ;
  * quiz_star_lumiere_3.dir  — le cœur de l'étoile commence à naître (4 frames) ;
  * quiz_star_<type>.dir     — étoile finale à la couleur du type (2 frames,
                               un clignotement léger) pour chaque Element du jeu.

Format .dir (DirSheet.Save de RogueEssence) :
  [int64 png_len][PNG RGBA][int32 tileW, tileH, rotate, frames]
Les frames sont disposées en une seule ligne (TotalX = frames, TotalY = 1) :
DrawDir(frame) dessine la tuile (frame % TotalX, frame / TotalX).

Le rendu est déterministe (positions fixes, pas d'aléatoire d'exécution) :
relancer le script régénère exactement les mêmes pixels. Un test compare
les pixels des .dir versionnés à ceux régénérés.

Usage : python3 tools/generer_etoile_quiz.py [dossier_sortie]
"""
import io
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / 'game' / 'Content' / 'BG'

# Taille finale (plein écran PMDO 320x240), dessinée en 160x120 puis ×2
# pour un rendu « pixel art » grossier et net.
W160, H160 = 160, 120
SCALE = 2
TILE_W, TILE_H = W160 * SCALE, H160 * SCALE
CX, CY = W160 // 2, H160 // 2

# Couleurs des types (Element1) — hex alignés sur quiz_data.couleurs_types.
COULEURS_TYPES = {
    'normal':   '#A8A878',
    'fire':     '#F08030',
    'water':    '#6890F0',
    'grass':    '#78C850',
    'electric': '#F8D030',
    'ice':      '#98D8D8',
    'fighting': '#C03028',
    'poison':   '#A040A0',
    'ground':   '#E0C068',
    'flying':   '#A890F0',
    'psychic':  '#F85888',
    'bug':      '#A8B820',
    'rock':     '#B8A038',
    'ghost':    '#705898',
    'dragon':   '#7038F8',
    'dark':     '#705848',
    'steel':    '#B8B8D0',
    'fairy':    '#EE99AC',
    'none':     '#9098A0',
}

LUMIERE = (255, 244, 200, 255)      # lumière chaude du quiz
NOYAU = (255, 252, 235, 255)        # cœur blanc de l'étoile


def _hex_rgb(hex_couleur):
    h = hex_couleur.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _moteurs_deterministes():
    """Positions fixes des lumières (aucune aléatoire d'exécution)."""
    # (dx, dy) en 160-space, choisis une fois pour toutes.
    disperses = [
        (-42, -28), (38, -34), (-30, 32), (44, 26), (-52, 4), (50, -6),
        (-12, -44), (10, 42), (-46, -14), (34, 12), (-8, 46), (16, -40),
        (-56, 22), (56, -24), (-36, -3), (28, -18), (-22, 18), (6, 30),
    ]
    # cibles (en éventail près du centre)
    proches = [
        (-9, -6), (7, -8), (-6, 7), (8, 5), (-2, -10), (2, 9), (-11, 2),
        (11, -1), (4, -3), (-4, 2), (0, -7), (-7, -9), (9, 8), (-3, 11),
        (5, 12), (-12, -4), (12, 3), (-1, 4), (3, -12), (-8, 6),
    ]
    return disperses, proches


def _canvas():
    return Image.new('RGBA', (W160, H160), (0, 0, 0, 0))


def _monte(img):
    return img.resize((TILE_W, TILE_H), Image.NEAREST)


def _point(draw, x, y, taille, couleur):
    draw.rectangle([x, y, x + taille - 1, y + taille - 1], fill=couleur)


def frame_lumiere_1(i):
    """14 lumières dispersées qui scintillent."""
    img = _canvas()
    draw = ImageDraw.Draw(img)
    disperses, _ = _moteurs_deterministes()
    alphas = (110, 165, 225, 255)
    for k, (dx, dy) in enumerate(disperses[:14]):
        a = alphas[(k + i) % 4]
        couleur = LUMIERE[:3] + (a,)
        _point(draw, CX + dx, CY + dy, 2, couleur)
        if (k + i) % 4 == 0:
            _point(draw, CX + dx - 2, CY + dy - 2, 1, LUMIERE[:3] + (a,))
            _point(draw, CX + dx + 3, CY + dy + 3, 1, LUMIERE[:3] + (a,))
    return _monte(img)


def frame_lumiere_2(i):
    """20 lumières qui convergent vers le centre (arrivée à la frame 3)."""
    img = _canvas()
    draw = ImageDraw.Draw(img)
    disperses, proches = _moteurs_deterministes()
    alphas = (170, 210, 240, 255)
    for k in range(20):
        dx, dy = disperses[k % len(disperses)]
        tx, ty = proches[k % len(proches)]
        av = (i + 1) / 4.0
        x = int(round(CX + dx + (tx - dx) * av))
        y = int(round(CY + dy + (ty - dy) * av))
        a = alphas[(k + i) % 4]
        _point(draw, x, y, 2, LUMIERE[:3] + (a,))
    return _monte(img)


def frame_lumiere_3(i):
    """Le cœur de l'étoile naît : halo central + rayons + dernières lumières."""
    img = _canvas()
    draw = ImageDraw.Draw(img)
    _, proches = _moteurs_deterministes()
    for k, (dx, dy) in enumerate(proches[:10]):
        x, y = CX + int(dx * 1.3), CY + int(dy * 1.3)
        _point(draw, x, y, 2, LUMIERE[:3] + (210,))
    rayons = 6 + i * 2  # les rayons s'allongent
    for ang_x, ang_y in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        for p in range(8, 8 + rayons):
            x = CX + ang_x * p
            y = CY + ang_y * p
            a = max(60, 255 - p * 16)
            _point(draw, x, y, 1, LUMIERE[:3] + (a,))
    for r, a in ((9 + i * 2, 90), (6 + i, 170), (3 + i, 255)):
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], fill=NOYAU[:3] + (a,))
    return _monte(img)


def frame_etoile(hex_couleur, i):
    """Étoile finale à 5 branches dans la couleur du type, cœur blanc.

    i = 0 : halo plus large ; i = 1 : halo plus serré (clignotement).
    """
    import math
    r, g, b = _hex_rgb(hex_couleur)
    sombre = (int(r * 0.45), int(g * 0.45), int(b * 0.45), 255)
    img = _canvas()
    draw = ImageDraw.Draw(img)
    # halo diffus : anneaux translucides qui dépassent des pointes
    pour_halo = ((46, 22), (40, 34), (35, 50)) if i == 0 else ((42, 20), (37, 32), (33, 46))
    for rayon, alpha in pour_halo:
        draw.ellipse([CX - rayon, CY - rayon, CX + rayon, CY + rayon],
                     fill=(r, g, b, alpha))

    def etoile(rayon_ext, rayon_int, couleur, ecart=0.0):
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5 + ecart
            rad = rayon_ext if k % 2 == 0 else rayon_int
            pts.append((CX + rad * math.cos(ang), CY + rad * math.sin(ang)))
        draw.polygon(pts, fill=couleur)

    # étoile en deux couches : contour sombre puis remplissage couleur type
    etoile(37, 16, sombre)
    etoile(34, 14, (r, g, b, 255))
    # cœur blanc + reflet intérieur
    etoile(13, 6, NOYAU)
    etoile(6, 3, (255, 255, 255, 255))
    # étincelles aux pointes (frame 0) ou sur les côtés (frame 1)
    if i == 0:
        for dx, dy in ((0, -41), (39, -13), (-39, -13), (24, 33), (-24, 33)):
            _point(draw, CX + dx, CY + dy, 2, (255, 255, 255, 230))
    else:
        for dx, dy in ((-14, -26), (14, -26), (0, 17), (28, 9), (-28, 9)):
            _point(draw, CX + dx, CY + dy, 1, (255, 255, 255, 210))
    return _monte(img)


def construire_frames():
    """Retourne {nom_sans_extension : [frames PIL]}."""
    lots = {
        'quiz_star_lumiere_1': [frame_lumiere_1(i) for i in range(4)],
        'quiz_star_lumiere_2': [frame_lumiere_2(i) for i in range(4)],
        'quiz_star_lumiere_3': [frame_lumiere_3(i) for i in range(4)],
    }
    for type_id, hex_couleur in COULEURS_TYPES.items():
        lots['quiz_star_' + type_id] = [frame_etoile(hex_couleur, i) for i in range(2)]
    return lots


def ecrire_dir(path, frames):
    """Écrit un DirSheet .dir : [int64 png_len][PNG][tileW, tileH, rotate, frames]."""
    n = len(frames)
    sheet = Image.new('RGBA', (TILE_W * n, TILE_H), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (TILE_W * i, 0))
    tampon = io.BytesIO()
    sheet.save(tampon, 'PNG')
    png = tampon.getvalue()
    with open(path, 'wb') as f:
        f.write(struct.pack('<q', len(png)))
        f.write(png)
        f.write(struct.pack('<iiii', TILE_W, TILE_H, 0, n))


def main(out_dir=DEFAULT_OUT):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lots = construire_frames()
    for nom, frames in sorted(lots.items()):
        path = out_dir / (nom + '.dir')
        ecrire_dir(path, frames)
        print(f'{path} ({len(frames)} frames, {TILE_W}x{TILE_H})')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
