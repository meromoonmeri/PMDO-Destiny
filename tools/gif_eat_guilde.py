#!/usr/bin/env python3
"""GIF des animations `Eat` de la guilde, membre par membre et en planche.

Un GIF par membre dans `art/previews/guilde_effectif_v1/eat/`, plus une planche
animée qui les montre tous côte à côte. Chaque GIF joue la rangée « face au
joueur » (direction 0) au rythme déclaré dans `AnimData.xml`, ralenti pour l'œil :
un tick du jeu dure 1/60 s, illisible en aperçu.

    python3 tools/gif_eat_guilde.py            # tout
    python3 tools/gif_eat_guilde.py Gardevoir  # un seul membre
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parent.parent
SPRITES = RACINE / 'art' / 'sprites' / 'guilde_effectif_v1'
PREUVES = RACINE / 'art' / 'previews' / 'guilde_effectif_v1'
SORTIE = PREUVES / 'eat'

ZOOM = 6                 # agrandissement des pixels
MS_PAR_TICK = 42         # 1 tick de jeu ≈ 17 ms : ralenti ~2,5× pour l'aperçu
FOND = (24, 33, 41)
ENCRE = (205, 225, 240)
GRIS = (140, 160, 176)


def police(taille: int = 14) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', taille)


def images_eat(dossier: Path, manifeste: dict) -> tuple[list[Image.Image], list[int]]:
    """Images de la rangée 0 (face au joueur) et durées en tick."""
    info = manifeste['animations']['Eat']
    largeur, hauteur = info['cellule']
    planche = Image.open(dossier / 'Eat-Anim.png').convert('RGBA')
    nombre = planche.width // largeur
    images = [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)) for i in range(nombre)]
    durees = info.get('durees') or [8] * nombre
    return images, durees[:nombre] if len(durees) >= nombre else [8] * nombre


def recadrer(images: list[Image.Image]) -> list[Image.Image]:
    """Recadre les images sur la boîte qui contient le sprite dans toutes ses images.

    Sans ce recadrage, chaque membre traîne la marge vide de sa cellule et les
    sprites se retrouvent à des hauteurs différentes dans l'aperçu.
    """
    boites = [image.getbbox() for image in images if image.getbbox()]
    if not boites:
        return images
    gauche = min(b[0] for b in boites)
    haut = min(b[1] for b in boites)
    droite = max(b[2] for b in boites)
    bas = max(b[3] for b in boites)
    return [image.crop((gauche, haut, droite, bas)) for image in images]


def vignette(images: list[Image.Image], durees: list[int], nom: str,
             etiquette: str) -> list[Image.Image]:
    """Images prêtes pour le GIF d'un membre : fond, nom, cadrage commun."""
    largeur, hauteur = images[0].size
    case = (largeur * ZOOM, hauteur * ZOOM)
    rendu = []
    images = recadrer(images)
    for image in images:
        cadre = Image.new('RGB', (case[0] + 16, case[1] + 34), FOND)
        grand = image.resize(case, Image.NEAREST)
        cadre.paste(grand, (8, 8), grand)
        dessin = ImageDraw.Draw(cadre)
        dessin.text((8, case[1] + 14), nom, font=police(), fill=ENCRE)
        rendu.append(cadre)
    return rendu


def ecrire_gif(images: list[Image.Image], durees: list[int], chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(chemin, save_all=True, append_images=images[1:],
                   duration=[d * MS_PAR_TICK for d in durees], loop=0, optimize=False)


def planche_commune(membres: list[tuple[str, list[Image.Image], list[int], str]]
                    ) -> None:
    """Un GIF unique : tous les membres côte à côte, alignés sur les pieds."""
    if not membres:
        return
    cellules = [(nom, recadrer(images), durees, etiquette)
                for nom, images, durees, etiquette in membres]
    largeur = max(images[0].width for _, images, _, _ in cellules)
    hauteur = max(images[0].height for _, images, _, _ in cellules)

    colonnes = 5
    lignes = (len(cellules) + colonnes - 1) // colonnes
    cw, ch = largeur * ZOOM + 16, hauteur * ZOOM + 40
    images_gif = []
    for indice in range(4):
        cadre = Image.new('RGB', (colonnes * cw + 8, lignes * ch + 40), FOND)
        dessin = ImageDraw.Draw(cadre)
        dessin.text((8, 10), 'Guilde de Réverie — animation Eat, quatre images',
                    font=police(16), fill=ENCRE)
        for position, (nom_cellule, images, durees, etiquette) in enumerate(cellules):
            x = 8 + (position % colonnes) * cw
            y = 40 + (position // colonnes) * ch
            image = images[indice % len(images)]
            grand = image.resize((image.width * ZOOM, image.height * ZOOM), Image.NEAREST)
            # tous les pieds sur la même ligne de sol
            sol = y + hauteur * ZOOM
            cadre.paste(grand, (x + (largeur * ZOOM - grand.width) // 2, sol - grand.height),
                        grand)
            dessin.text((x + 4, sol + 6), nom_cellule, font=police(), fill=ENCRE)
            dessin.text((x + 4, sol + 22), etiquette, font=police(11), fill=GRIS)
        images_gif.append(cadre)

    ecrire_gif(images_gif, [6, 8, 6, 8], PREUVES / 'guilde_eat_tous.gif')


def main(argv: list[str]) -> int:
    manifeste = json.loads((SPRITES / 'MANIFESTE.json').read_text(encoding='utf-8'))
    demandes = set(argv[1:])
    collecte = []
    for nom, fiche in manifeste['membres'].items():
        if demandes and nom not in demandes:
            continue
        dossier = SPRITES / fiche['dossier']
        images, durees = images_eat(dossier, fiche)
        etiquette = {'dessinee': 'bouchée dessinée', 'derivee': 'Eat dérivé',
                     'SpriteCollab': 'Eat SpriteCollab'}.get(
            fiche['animations']['Eat']['source'], fiche['animations']['Eat']['source'])
        rendu = vignette(images, durees, nom, etiquette)
        ecrire_gif(rendu, durees, SORTIE / f'{nom}.gif')
        collecte.append((nom, images, durees, etiquette))
        print(f'{nom:14s} {len(images)} images · durées {durees} · {etiquette}')

    if not demandes:
        planche_commune(collecte)
        print(PREUVES / 'guilde_eat_tous.gif')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
