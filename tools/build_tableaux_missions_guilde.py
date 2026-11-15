#!/usr/bin/env python3
"""Genere les deux tableaux de mission de la salle des Missions.

Contraste voulu
---------------
Le decor de la Guilde est brun-orange : dominante `#68482f` aux murs,
`#d08733` au parquet, luminance moyenne 105. Un tableau dessine dans ces
teintes se confond avec le mur — c'est le defaut des `pmu_tableau_quetes_*`
deja presents, dont le bois reprend exactement la palette ambiante.

Les deux tableaux prennent donc le contre-pied :

* **valeur** : panneau creme a luminance 205-230, soit deux fois le mur ;
* **teinte** : creme/ardoise/vermillon pour l'un, vert-de-gris/parchemin/jade
  pour l'autre, tous froids ou neutres face a l'orange ;
* **lien** : le seul emprunt au decor est l'or de la Guilde (`#e59b3c`,
  `#f6c152`), en clous et en filet, pour que l'objet appartienne au lieu
  sans s'y dissoudre.

Rendu en pixel art strict : pas d'antialiasing, contour d'un pixel, deux ou
trois tons par matiere.

Usage : python3 tools/build_tableaux_missions_guilde.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "art/guilde_destiny_reseau/tableaux_missions"
BANQUE = RACINE / "game/Content/Tile/Destiny_Guilde_Immobilier.tile"


# --- palette ---------------------------------------------------------------

OR = {"clair": "#f6c152", "moyen": "#e59b3c", "sombre": "#8b4b1e"}

CREME = {"clair": "#fffaf0", "moyen": "#f2e4c6", "ombre": "#d8c19a",
         "creux": "#b89a72", "cadre": "#3a2318", "cadre_clair": "#5c3a24"}

VERMILLON = {"clair": "#e2675c", "moyen": "#c8453c", "sombre": "#8e2721"}

ARDOISE = {"encre": "#3f5670", "ligne": "#6d8299"}

VERT_DE_GRIS = {"pale": "#cfe9e1", "clair": "#9ad0c6", "moyen": "#6aa79e", "ombre": "#46786f",
                "creux": "#2f5850", "cadre": "#142922", "cadre_clair": "#24463c"}

PARCHEMIN = {"clair": "#f8ecca", "moyen": "#e7d3a8", "ombre": "#c7ae82"}

JADE = {"clair": "#6fbb8f", "moyen": "#4f9a72", "sombre": "#2f6b4d"}

PINS = ["#4f8f5a", "#4a6fa8", "#c8453c", "#e59b3c"]


# --- petit moteur de pixel art ---------------------------------------------


def toile(largeur: int, hauteur: int):
    im = Image.new("RGBA", (largeur, hauteur), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def rect(d, x0, y0, x1, y1, couleur):
    """Rectangle plein, bornes incluses."""
    if x1 < x0 or y1 < y0:
        return
    d.rectangle([x0, y0, x1, y1], fill=couleur)


def cadre(d, x0, y0, x1, y1, exterieur, interieur):
    """Contour d'un pixel a l'exterieur, rien a l'interieur."""
    rect(d, x0, y0, x1, y1, exterieur)
    rect(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, interieur)


def bevel(d, x0, y0, x1, y1, clair, sombre):
    """Lumiere en haut et a gauche, ombre en bas et a droite."""
    d.line([(x0, y0), (x1 - 1, y0)], fill=clair)
    d.line([(x0, y0), (x0, y1 - 1)], fill=clair)
    d.line([(x1, y0), (x1, y1)], fill=sombre)
    d.line([(x0, y1), (x1, y1)], fill=sombre)


def clous(d, x0, y0, x1, y1, marge=3):
    """Quatre clous d'or aux angles, comme les pentures de la Guilde."""
    for cx in (x0 + marge, x1 - marge):
        for cy in (y0 + marge, y1 - marge):
            d.point((cx, cy), fill=OR["sombre"])
            d.point((cx, cy - 1), fill=OR["moyen"])
            d.point((cx - 1, cy), fill=OR["moyen"])


# --- tableau 1 : panneau de missions ---------------------------------------


def tableau_missions() -> Image.Image:
    """72x64. Panneau creme, bandeau vermillon, notes punaisees."""
    l, h = 72, 64
    im, d = toile(l, h)

    # cadre de noyer, puis panneau creme
    rect(d, 0, 0, l - 1, h - 1, CREME["cadre"])
    rect(d, 1, 1, l - 2, h - 2, CREME["cadre_clair"])
    rect(d, 2, 2, l - 3, h - 3, CREME["cadre"])
    rect(d, 3, 3, l - 4, h - 4, CREME["moyen"])
    bevel(d, 3, 3, l - 4, h - 4, CREME["clair"], CREME["ombre"])

    # bandeau vermillon avec filet d'or
    rect(d, 5, 5, l - 6, 15, VERMILLON["moyen"])
    rect(d, 5, 5, l - 6, 6, VERMILLON["clair"])
    rect(d, 5, 15, l - 6, 15, VERMILLON["sombre"])
    d.line([(6, 10), (l - 7, 10)], fill=OR["moyen"])

    # embleme de la Guilde : un losange d'or, lisible a l'echelle 1
    cx = l // 2
    for i, demi in enumerate((1, 2, 3, 4)):
        rect(d, cx - demi, 12 - i, cx + demi, 12 - i, OR["moyen"])
        rect(d, cx - demi, 12 + i, cx + demi, 12 + i, OR["moyen"])
    rect(d, cx - 2, 11, cx, 13, OR["clair"])
    d.point((cx - 1, 12), fill=VERT_DE_GRIS["creux"])

    # trois notes punaisees
    notes = [
        (6, 19, 30, 34, 1),
        (36, 19, 65, 32, 0),
        (6, 37, 32, 55, 2),
        (36, 36, 65, 55, 3),
    ]
    for x0, y0, x1, y1, pin in notes:
        rect(d, x0, y0, x1, y1, CREME["creux"])            # ombre portee
        rect(d, x0, y0 - 1, x1 - 1, y1 - 1, CREME["clair"])
        d.line([(x0, y1 - 1), (x1 - 1, y1 - 1)], fill=CREME["ombre"])
        # lignes d'ecriture
        for yy in range(y0 + 4, y1 - 2, 4):
            d.line([(x0 + 3, yy), (x1 - 4, yy)], fill=ARDOISE["ligne"])
        # titre plus court
        d.line([(x0 + 3, y0 + 1), (x0 + 10, y0 + 1)], fill=ARDOISE["encre"])
        # punaise
        rect(d, (x0 + x1) // 2, y0 - 1, (x0 + x1) // 2 + 1, y0, PINS[pin])
        d.point(((x0 + x1) // 2, y0 - 2), fill=CREME["clair"])

    clous(d, 0, 0, l - 1, h - 1, marge=4)
    return im


# --- tableau 2 : registre de guilde ----------------------------------------


def tableau_registre() -> Image.Image:
    """64x72. Vert-de-gris, deux parchemins suspendus, sceau d'or."""
    l, h = 64, 72
    im, d = toile(l, h)

    rect(d, 0, 0, l - 1, h - 1, VERT_DE_GRIS["cadre"])
    rect(d, 1, 1, l - 2, h - 2, VERT_DE_GRIS["cadre_clair"])
    rect(d, 2, 2, l - 3, h - 3, VERT_DE_GRIS["cadre"])
    rect(d, 3, 3, l - 4, h - 4, VERT_DE_GRIS["clair"])
    bevel(d, 3, 3, l - 4, h - 4, VERT_DE_GRIS["pale"], VERT_DE_GRIS["ombre"])

    # filet d'or interieur
    cadre(d, 6, 6, l - 7, h - 7, OR["sombre"], VERT_DE_GRIS["clair"])

    # barre de suspension
    rect(d, 8, 9, l - 9, 11, VERT_DE_GRIS["creux"])
    d.line([(8, 9), (l - 9, 9)], fill=OR["moyen"])

    # deux parchemins suspendus
    for x0, x1, bas in ((10, 28, h - 22), (34, 52, h - 16)):
        # cordon
        for y in range(12, 16):
            d.point(((x0 + x1) // 2, y), fill=OR["sombre"])
        rect(d, x0, 16, x1, bas, PARCHEMIN["ombre"])
        rect(d, x0, 16, x1 - 1, bas - 1, PARCHEMIN["moyen"])
        d.line([(x0, 16), (x1 - 1, 16)], fill=PARCHEMIN["clair"])
        # rouleau du bas
        rect(d, x0 - 1, bas, x1, bas + 2, PARCHEMIN["ombre"])
        d.line([(x0 - 1, bas), (x1, bas)], fill=PARCHEMIN["clair"])
        # texte
        for yy in range(20, bas - 3, 4):
            d.line([(x0 + 3, yy), (x1 - 4, yy)], fill=ARDOISE["ligne"])
        d.line([(x0 + 3, 18), (x0 + 11, 18)], fill=ARDOISE["encre"])
        # ruban de jade
        rect(d, x0 + 1, bas - 8, x1 - 1, bas - 7, JADE["sombre"])
        rect(d, x0 + 1, bas - 8, x1 - 1, bas - 8, JADE["clair"])

    # sceau de la Guilde, en bas
    sx, sy = l // 2, h - 12
    rect(d, sx - 4, sy - 4, sx + 4, sy + 4, JADE["sombre"])
    rect(d, sx - 3, sy - 3, sx + 3, sy + 3, JADE["moyen"])
    d.line([(sx - 3, sy - 3), (sx + 3, sy - 3)], fill=JADE["clair"])
    rect(d, sx - 1, sy - 2, sx + 1, sy + 2, OR["moyen"])
    d.point((sx, sy), fill=OR["clair"])

    clous(d, 0, 0, l - 1, h - 1, marge=5)
    return im


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    objets = {
        "guilde_tableau_missions": tableau_missions(),
        "guilde_tableau_registre": tableau_registre(),
    }
    manifest = {}
    for nom, im in objets.items():
        chemin = SORTIE / f"{nom}.png"
        im.save(chemin)
        manifest[nom] = {"w": im.width, "h": im.height, "fichier": chemin.name}
        print(f"{nom}: {im.width}x{im.height} -> {chemin}")
    (SORTIE / "manifest_tableaux.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
