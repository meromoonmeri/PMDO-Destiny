#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prolonge les chemins de Waterfall Village dans la plaine sud.

Constat : les deux chemins qui descendent des ponts s'arrêtent à la ligne 368 et
la plaine n'a aucune voie sur 130 lignes. Les chemins du nord sont dessinés avec
la planche `INVERSEPATHWAY`, mais dans des calques situés **sous** le calque 27
(le remplissage de gazon de la plaine) : les y dessiner ne servirait à rien,
le gazon les recouvrirait.

Méthode retenue : on relève des **empreintes** de chemin sur les routes déjà
posées par l'auteur (même planche, même largeur, mêmes bords), et on les
réécrit dans le calque 33 — celui que l'auteur utilise déjà pour les amorces
sous les ponts, et qui passe au-dessus du remplissage. Aucune tuile inventée,
aucune planche ajoutée, l'herbe de la plaine n'est pas touchée.

Usage :
    python dessiner_chemins.py <source.rsground> <sortie.rsground>
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editer_ground as eg  # ouvrir / Calque / reecrire

CIBLE = 33          # calque 33 : au-dessus du remplissage de gazon
GAUCHE = 26         # route verticale du pont ouest
DROITE = 3          # route verticale du pont est

# --- empreintes relevées sur la carte (voir docs/AMELIORATION_WVC_SUD.md)
# Tronçons étroits (7 cases avec les berges), juste au nord des ponts : c'est la
# largeur des amorces déjà posées au sud de la rivière (tx 11..14 et 86..89).
EMP_GAUCHE = (9, 336, 16, 349)      # calque 26, route du pont ouest
EMP_DROITE = (84, 336, 91, 349)     # calque 3, route du pont est
# Route est-ouest : lignes 196..200 au nord (5 lignes), prise sur 50 cases à
# l'intérieur d'un tronçon droit pour éviter les embouts arrondis.
HORIZ_LIGNES = (196, 197, 198, 199, 200)
HORIZ_X = (40, 90)
VIDE = (b'{\r\n"AutoTileset": "",\r\n"Associates": [],\r\n"Layers": [],'
        b'\r\n"NeighborCode": -1\r\n}')

BAS = 494           # dernière ligne dessinée (carte de 500 lignes)
TY_ROUTE_H = 427    # haut de la grande route est-ouest


def poser(calques, mm, src_layer, emp, dx, dy, n_x=1, n_y=1, pas_x=0, pas_y=0, vides=False):
    """Écrit une empreinte dans le calque cible, répétée n_x fois en x / n_y en y."""
    x0, y0, x1, y1 = emp
    source = calques[src_layer]
    cible = calques[CIBLE]
    n = 0
    for j in range(n_y):
        for i in range(n_x):
            ox = dx + i * (pas_x or (x1 - x0))
            oy = dy + j * (pas_y or (y1 - y0))
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    dxc, dyc = ox + xx - x0, oy + yy - y0
                    if not (0 <= dxc < eg.NX and 0 <= dyc < eg.NY):
                        continue          # hors carte : on rogne proprement
                    t = source.lire(mm, xx, yy)
                    if not vides and t == VIDE:
                        continue          # on ne perce pas les autres chemins
                    if cible.lire(mm, dxc, dyc) == t:
                        continue
                    cible.ecrire(dxc, dyc, t)
                    n += 1
    return n


def plus_longue_plage(calque, mm, ty, tx_min=0, tx_max=200):
    """Plus longue suite de cases non vides sur une ligne — sert à choisir une empreinte sans trou."""
    meilleur = (0, None)
    debut = None
    for tx in range(tx_min, tx_max + 1):
        vide = tx >= tx_max or calque.lire(mm, tx, ty) == VIDE
        if not vide and debut is None:
            debut = tx
        elif vide and debut is not None:
            if tx - debut > meilleur[0]:
                meilleur = (tx - debut, debut)
            debut = None
    return meilleur


def choisir_calque(calques, mm, y0, y1, x0, x1, candidats=(1, 3, 24, 26, 27, 32, 33)):
    """Calque qui couvre le moins de trous sur une fenêtre — évite de percer la route."""
    meilleur = None
    for i in candidats:
        c = calques[i]
        trous = sum(1 for ty in range(y0, y1) for tx in range(x0, x1)
                    if c.lire(mm, tx, ty) == VIDE)
        if meilleur is None or trous < meilleur[1]:
            meilleur = (i, trous)
    return meilleur


def bandes():
    """Emprises des chemins ajoutés, en cases."""
    return [
        (9, 356, 16, 500),                       # route du pont ouest
        (84, 356, 91, 500),                      # route du pont est
        (0, TY_ROUTE_H, 200, TY_ROUTE_H + 5),    # route est-ouest
    ]


def degager(calques, mm, bandes, calques_objets=(34, 35, 36)):
    """Retire les objets (buissons, cailloux) qui empiètent sur un chemin."""
    def sur_chemin(tx, ty):
        return any(x0 <= tx < x1 and y0 <= ty < y1 for x0, y0, x1, y1 in bandes)

    n = 0
    for i in calques_objets:
        c = calques[i]
        vus = set()
        for tx in range(eg.NX):
            for ty in range(eg.NY):
                if (tx, ty) in vus or c.lire(mm, tx, ty) == VIDE:
                    continue
                # composante connexe de l'objet
                comp, pile = [], [(tx, ty)]
                vus.add((tx, ty))
                while pile:
                    x, y = pile.pop()
                    comp.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        v = (x + dx, y + dy)
                        if (0 <= v[0] < eg.NX and 0 <= v[1] < eg.NY and v not in vus
                                and c.lire(mm, *v) != VIDE):
                            vus.add(v)
                            pile.append(v)
                if any(sur_chemin(*p) for p in comp):
                    for p in comp:
                        c.ecrire(p[0], p[1], VIDE)
                        n += 1
    return n


def main(src, dst):
    f, mm, calques, noms = eg.ouvrir(Path(src))
    total = 0

    # 1. la grande route est-ouest, ligne par ligne : chaque ligne vient d'une plage
    #    vérifiée SANS TROU dans le calque source (sinon la répétition perce la route)
    x0, x1 = HORIZ_X
    y0, y1 = HORIZ_LIGNES[0], HORIZ_LIGNES[-1] + 1
    horiz, trous = choisir_calque(calques, mm, y0, y1, x0, x1)
    print(f'  route est-ouest : calque {horiz} ({noms[horiz]}), {trous} trou(s) sur '
          f'{x1 - x0}x{y1 - y0}, répétée depuis ty {TY_ROUTE_H}')
    larg = x1 - x0
    total += poser(calques, mm, horiz, (x0, y0, x1, y1), 0, TY_ROUTE_H,
                   n_x=200 // larg + 1, pas_x=larg - 6)

    # 2. les deux routes verticales, depuis les ponts jusqu'au bord sud
    hauteur = EMP_GAUCHE[3] - EMP_GAUCHE[1]
    n = (BAS - 356) // hauteur + 1
    total += poser(calques, mm, GAUCHE, EMP_GAUCHE, EMP_GAUCHE[0], 356, n_y=n, pas_y=hauteur)
    total += poser(calques, mm, DROITE, EMP_DROITE, EMP_DROITE[0], 356, n_y=n, pas_y=hauteur)

    # 3. dégager les buissons posés sur les nouveaux chemins : on enlève l'objet
    #    entier (toutes ses cases), jamais la moitié d'un buisson.
    total += degager(calques, mm, bandes())

    eg.reecrire(src, dst, calques, mm, None)
    f.close()
    print(f'{dst} : {total} cases écrites dans le calque {CIBLE} ({noms[CIBLE]})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
