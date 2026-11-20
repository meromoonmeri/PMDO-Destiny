#!/usr/bin/env python3
"""Antichambre de la Fosse Cascade, en tuiles 8 px (depuis le décor Destiny).

La salle haute reste intacte à (48, 0). L'arène 24 px est composée à partir
exactement de ce rectangle ; les tuiles et collisions supplémentaires sont
propres au ground. Pas de redimensionnement des sprites ni d'asset externe.
"""
from __future__ import annotations

import copy
import json
import math
import random
from pathlib import Path

from PIL import Image

SALLE_W, SALLE_H = 60, 45
DECALAGE_X = 6  # tuiles de 8 px ; aligné avec la grille de 24 px
GROUND_W, GROUND_H = 72, 66
ENTREE = (222, 492)  # ancre du joueur à l'arrivée (coin supérieur gauche)
PLANCHE = 'FGV1_PASSAGE_SUD'

# Profondeur, bord gauche, bord droit du sentier. La roche masque la salle
# au premier plan, le talus s'écarte au coude puis rejoint le goulet existant.
BERGES = ((0, 253, 322), (20, 244, 319), (48, 218, 304), (76, 195, 299),
          (104, 181, 289), (132, 182, 268), (167, 179, 248))


def bords(y: int) -> tuple[float, float]:
    for (y0, l0, r0), (y1, l1, r1) in zip(BERGES, BERGES[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return l0 + (l1 - l0) * t, r0 + (r1 - r0) * t
    return BERGES[-1][1:]


def rectangle_salle(obj: dict) -> None:
    """Récupère la salle originale d'un ground déjà agrandi, avant régénération."""
    for calque in obj['Layers']:
        calque['Tiles'] = [col[:SALLE_H] for col in calque['Tiles'][DECALAGE_X:DECALAGE_X + SALLE_W]]
    obj['obstacles'] = [col[:SALLE_H] for col in obj['obstacles'][DECALAGE_X:DECALAGE_X + SALLE_W]]
    for col in obj['obstacles']:
        for case in col:
            case['Bounds']['X'] -= DECALAGE_X * 8
    for groupe in obj['Entities']:
        for marqueur in groupe['Markers']:
            c = marqueur['Collider']
            c['X'] -= DECALAGE_X * 8
            if marqueur['EntName'] == 'entrance':
                c.update(X=240, Y=344)


def composer_salle(obj: dict, decoded: dict) -> Image.Image:
    fond = Image.new('RGBA', (SALLE_W * 8, SALLE_H * 8), (0, 0, 0, 255))
    for calque in obj['Layers']:
        if not calque.get('Visible', True) or calque['Layer'] == 4:
            continue
        for x, col in enumerate(calque['Tiles']):
            for y, case in enumerate(col):
                for piste in case['Layers']:
                    if piste['Frames']:
                        tr = piste['Frames'][0]
                        if tr['Sheet']:
                            t = tr['TexLoc']
                            fond.alpha_composite(decoded[tr['Sheet']][(t['X'], t['Y'])], (x * 8, y * 8))
    return fond


def miroir(x: int, n: int) -> int:
    x %= 2 * n
    return min(x, 2 * n - x - 1)


def strates(salle: Image.Image, w: int, h: int) -> Image.Image:
    """Soude des échantillons de roche à leur taille native, sans répétition en miroir."""
    # Les deux éboulis bas de la carte originale, hors sable et hors vasque.
    # Les recouvrements de 12 px masquent le raccord entre blocs de strates.
    rng = random.Random(68472)
    surface = Image.new('RGBA', (w, h), (55, 51, 43, 255))
    largeur, hauteur, chevauchement = 72, 48, 12
    for y in range(0, h, hauteur - chevauchement):
        for x in range(0, w, largeur - chevauchement):
            sx = rng.choice((rng.randrange(1, 96), rng.randrange(312, 408)))
            sy = rng.randrange(311, 360 - hauteur + 1)
            piece = salle.crop((sx, sy, sx + largeur, sy + hauteur))
            masque = Image.new('L', piece.size)
            masque.putdata([round(255 * min(1, i / 12 if x else 1, j / 12 if y else 1))
                            for j in range(hauteur) for i in range(largeur)])
            surface.paste(piece, (x, y), masque)
    return surface


def peindre_bords(salle: Image.Image) -> Image.Image:
    """Prolonge la roche et modèle un passage oblique, plus sombre sous le talus."""
    dx = DECALAGE_X * 8
    sw, sh = salle.size
    image = Image.new('RGBA', (GROUND_W * 8, GROUND_H * 8))
    image.paste(salle, (dx, 0))
    src, dst = salle.load(), image.load()
    for y in range(sh):
        for x in range(dx):
            # Cadre rocheux latéral ; le bord de contact reste pixel pour pixel.
            dst[x, y] = src[dx - 1 - x, y]
            dst[dx + sw + x, y] = src[sw - 1 - x, y]

    roches = strates(salle, image.width, image.height - sh).load()
    for y in range(sh, image.height):
        p = y - sh
        l, r = bords(p)
        for x in range(image.width):
            bord = min(x - l, r - x)
            feston = (math.sin(p * .24 + x * .09) * 3.0 + math.sin(p * .53 + x * .22) * 1.5)
            marge = bord + feston
            sable = src[213 + miroir(x + p // 7, 52), 229 + miroir(p + x // 16, 56)][:3]
            roc = roches[x, p][:3]
            grain = ((13 * x + 7 * p) % 11 - 5) / 5  # lisière irrégulière à l'échelle du pixel
            ratio = min(1., max(0., (marge + 2.5 + grain) / 5))
            rgb = tuple(round(a * (1 - ratio) + b * ratio) for a, b in zip(roc, sable))

            # Seulement la jonction (pas la longueur du passage) reprend la
            # tranche du haut ; cela prolonge les pieds des blocs existants.
            if p < 32:
                x0 = x - (l - BERGES[0][1]) if x < (l + r) / 2 else x - (r - BERGES[0][2])
                bord_salle = src[miroir(round(x0) - dx, sw), sh - 1 - p][:3]
                t = p / 32
                t = t * t * (3 - 2 * t)
                rgb = tuple(round(a * (1 - t) + b * t) for a, b in zip(bord_salle, rgb))

            # Deux petites vasques à différentes profondeurs, enchâssées
            # dans la paroi (couleurs du décor, pas de nouvel effet d'eau).
            for cx, cy, ox, oy, rayon_x, rayon_y in ((330, 53, 309, 316, 28, 17),
                                                     (152, 118, 89, 267, 26, 16)):
                if abs(x - cx) < rayon_x and abs(p - cy) < rayon_y and bord < -4:
                    d = ((x - cx) / rayon_x) ** 2 + ((p - cy) / rayon_y) ** 2
                    a = min(1., max(0., (1 - d) * 3))
                    roche_vasque = src[ox + x - cx, oy + p - cy][:3]
                    rgb = tuple(round(u * (1 - a) + v * a) for u, v in zip(rgb, roche_vasque))

            # La lumière fuyante de la salle haute guide le regard ; un
            # liseré d'occlusion irrégulier détache le pied de la paroi.
            ombre = min(1, p / 77) * (0.24 + 0.24 * min(1, max(0, -bord / 76)))
            if marge >= 0:
                ombre += .19 * min(1, p / 48) * max(0., 1 - marge / 16)
            dst[x, y] = (round(rgb[0] * (1 - ombre)), round(rgb[1] * (1 - ombre * .89)),
                         round(rgb[2] * (1 - ombre * .67)), 255)
    return image


def agrandir_ground(root: Path, salle_doc: dict, decoded: dict, sauver_planche) -> None:
    obj = copy.deepcopy(salle_doc['Object'])
    salle = composer_salle(obj, decoded)
    image = peindre_bords(salle)
    planche = {}

    def hors_salle(x, y):
        return not (DECALAGE_X <= x < DECALAGE_X + SALLE_W and y < SALLE_H)

    def vide():
        return {'AutoTileset': '', 'Associates': [], 'Layers': [], 'NeighborCode': -1}

    for i, calque in enumerate(obj['Layers']):
        ancien = calque['Tiles']
        nouveau = []
        for x in range(GROUND_W):
            col = []
            for y in range(GROUND_H):
                if not hors_salle(x, y):
                    col.append(ancien[x - DECALAGE_X][y])
                    continue
                case = vide()
                if i == 0:
                    planche[x, y] = image.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8))
                    case['Layers'].append({'Frames': [{'Sheet': PLANCHE, 'TexLoc': {'X': x, 'Y': y}}], 'FrameLength': 60})
                col.append(case)
            nouveau.append(col)
        calque['Tiles'] = nouveau

    ancien_obs = obj['obstacles']
    obj['obstacles'] = []
    for x in range(GROUND_W):
        col = []
        for y in range(GROUND_H):
            if not hors_salle(x, y):
                case = ancien_obs[x - DECALAGE_X][y]
                case['Bounds']['X'] = x * 8
            else:
                l, r = bords(y * 8 + 4 - SALLE_H * 8)
                ouvert = y >= SALLE_H and l + 2 <= x * 8 + 4 <= r - 2
                case = {'Bounds': {'X': x * 8, 'Y': y * 8, 'Width': 8, 'Height': 8},
                        'Tags': 0 if ouvert else 1}
            col.append(case)
        obj['obstacles'].append(col)

    for groupe in obj['Entities']:
        for marqueur in groupe['Markers']:
            c = marqueur['Collider']
            c['X'] += DECALAGE_X * 8
            if marqueur['EntName'] == 'entrance':
                c.update(X=ENTREE[0], Y=ENTREE[1])
    obj['Comment'] = ('PMDO 0.8.12. Fosse Cascade Fond : antichambre des vasques et sauvetage de Nilo '
                      '(576x528). L’arène native occupe les 480x360 pixels de la salle haute, à x=48.')
    sauver_planche(root / f'game/Content/Tile/{PLANCHE}.tile', 8, planche)
    doc = {**salle_doc, 'Object': obj}
    dest = root / 'game/Data/Ground/fgv1_fin_grotte_vasques.rsground'
    dest.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print('[OK] antichambre des vasques : 72×66 tuiles de 8 px (576×528), arène 480×360 intacte')
