#!/usr/bin/env python3
"""Convertit les calques existants de la Source irisée en fonds PMDO 0.8.12.

Aucun dessin n'est recréé : le décor, les 3 + 13 phases d'eau et la planche
originale de 78 phases sont conservés dans art/source_irisee. La vérification
porte sur la recomposition pixel pour pixel de la phase 39 de l'aperçu d'origine.
Nécessite Pillow ; usage : python tools/construire_source_irisee.py
"""
from __future__ import annotations
import hashlib
import io
import math
import struct
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/source_irisee'
OUT = ROOT / 'game/Content/BG'
REFERENCE_RGBA_SHA256 = 'd7279147d176f60a22399d3a8e3258a6f3982b1010d74807f01c081cbe9bf324'


def open_rgba(path):
    with Image.open(path) as im:
        return im.convert('RGBA')


def bounds(images):
    boxes = [im.getchannel('A').getbbox() for im in images]
    boxes = [b for b in boxes if b]
    assert boxes
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def write_dir(name, images, box=None):
    """Format DirSheet.Save du moteur ; atlas rectangulaire sans interpolation."""
    if box is not None:
        images = [im.crop(box) for im in images]
    w, h = images[0].size
    assert all(im.size == (w, h) for im in images)
    columns = max(1, math.ceil(math.sqrt(len(images) * w * h) / w))
    rows = math.ceil(len(images) / columns)
    atlas = Image.new('RGBA', (columns * w, rows * h))
    for i, im in enumerate(images):
        atlas.paste(im, ((i % columns) * w, (i // columns) * h))
    # Le moteur dessine les Grounds en AlphaBlend : son import natif stocke
    # des RGB prémultipliés par l'alpha. Stocker les PNG droits donnerait
    # des bords blancs et une colonne surexposée en jeu.
    r, g, b, a = atlas.split()
    atlas = Image.merge('RGBA', (ImageChops.multiply(r, a),
                                 ImageChops.multiply(g, a),
                                 ImageChops.multiply(b, a), a))
    buf = io.BytesIO()
    atlas.save(buf, format='PNG', optimize=True)
    png = buf.getvalue()
    (OUT / (name + '.dir')).write_bytes(
        struct.pack('<q', len(png)) + png + struct.pack('<iiii', w, h, 0, len(images)))
    print(name, len(images), 'phases,', w, 'x', h, 'pixels, origine', box[:2] if box else (0, 0))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    decor = open_rgba(SOURCE / 'decor_escalier.png')
    nettoyee = open_rgba(SOURCE / 'colonne_nettoyee.png')
    eau = [open_rgba(SOURCE / 'cycle_3' / f'{i:02}.png') for i in range(3)]
    reflet = [open_rgba(SOURCE / 'cycle_13' / f'{i:02}.png') for i in range(13)]
    sheet = open_rgba(SOURCE / 'planche_pulsation_78.png')
    assert decor.size == nettoyee.size == (600, 600)
    assert sheet.size == (1000, 1680)
    colonne = []
    for i in range(78):
        x, y = (i % 10) * 100, (i // 10) * 210
        crop = sheet.crop((x, y, x + 100, y + 210))
        image = Image.new('RGBA', (600, 600))
        image.paste(crop, (250, 0))
        colonne.append(image)
    # RGB fixes, alpha seul varie, et aucun pixel lumineux hors de la zone.
    box = (275, 0, 325, 201)
    for image in colonne:
        assert bounds([image])[0] >= box[0]
        assert bounds([image])[1] >= box[1]
        assert bounds([image])[2] <= box[2]
        assert bounds([image])[3] <= box[3]
    phase = 39
    assembled = decor.copy()
    for layer in (eau[(phase // 2) % 3], reflet[(phase // 2) % 13], nettoyee, colonne[phase]):
        assembled.alpha_composite(layer)
    actual = hashlib.sha256(assembled.tobytes()).hexdigest()
    assert actual == REFERENCE_RGBA_SHA256, f'La composition diffère de la référence : {actual}'
    print('Composition phase 39 : pixels identiques à la référence, SHA-256 RGBA', actual)
    # Positions vérifiées dans destiny_source_irisee.rsground, coordonnées carte.
    assert bounds(eau) == (144, 0, 456, 311)
    assert bounds(reflet) == (240, 281, 360, 302)
    assert bounds([nettoyee]) == box
    write_dir('Source_Irisee_Decor', [decor])
    write_dir('Source_Irisee_Eau', eau, bounds(eau))
    write_dir('Source_Irisee_Reflet', reflet, bounds(reflet))
    write_dir('Source_Irisee_Colonne_Fond', [nettoyee], box)
    write_dir('Source_Irisee_Pulsation', colonne, box)


if __name__ == '__main__':
    main()
