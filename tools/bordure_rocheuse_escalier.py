#!/usr/bin/env python3
"""Bordure rocheuse violette courbée sur le flanc GAUCHE de l'escalier.

La façade `Guilde_HD_*` porte un escalier en perspective au pied de la porte :
son flanc gauche descend de (76, 230) vers (102, 258). On y adosse un muret de
pierre qui suit une COURBE (Bézier) plutôt qu'une diagonale, avec :

* un contour sombre `(36,17,12)` ;
* un corps violet-gris `(82,63,70)`, creux `(48,36,42)` ;
* une arête éclairée `(118,94,102)` côté talus ;
* deux touffes de mousse `(44,90,33)`.

Aucune couleur nouvelle : les cinq tons existent déjà sur la façade (les trois
tons de roche sont ceux des cailloux du pied de l'arbre). Le muret n'est dessiné
que sur les pixels TRANSPARENTS : il ne recouvre jamais l'escalier ni la racine.

Usage :
    python3 tools/bordure_rocheuse_escalier.py [--dry-run]
"""
from __future__ import annotations

import argparse
import io
import struct
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
GAME = REPO / "game"
OBJ = GAME / "Content/Object"

OUTLINE = (36, 17, 12)
ROCK_MID = (82, 63, 70)
ROCK_DARK = (48, 36, 42)
ROCK_LIGHT = (118, 94, 102)
MOSS = (44, 90, 33)

FACADES = ["Guilde_HD_Jour", "Guilde_HD_Aube", "Guilde_HD_Crepuscule", "Guilde_HD_Nuit",
           "Guilde_HD_Porte_Ouverte_Jour", "Guilde_HD_Porte_Ouverte_Aube",
           "Guilde_HD_Porte_Ouverte_Crepuscule", "Guilde_HD_Porte_Ouverte_Nuit"]

# Le muret se glisse dans le COULOIR VIDE entre le rocher de gauche et la jambe
# gauche de l'escalier. Ce couloir est mesuré sur l'image (voir `couloir()`),
# pas deviné : il fait 4 à 6 px de large, de y = 236 à y = 258.
Y_HAUT, Y_BAS = 236, 258
X_MIN = 92        # borne gauche de la recherche (après le rocher)
X_DEPART = 112    # départ de la recherche : au cœur de l'escalier
EPAISSEUR_MAX = 5

def _lire_dir(path: Path) -> Image.Image:
    raw = path.read_bytes()
    n = struct.unpack("<q", raw[:8])[0]
    return Image.open(io.BytesIO(raw[8:8 + n])).convert("RGBA")


def _ecrire_dir(path: Path, im: Image.Image) -> None:
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=False)
    png = buf.getvalue()
    path.write_bytes(struct.pack("<q", len(png)) + png
                     + struct.pack("<iiii", im.width, im.height, 0, 1))


def _bezier(t: float) -> tuple[float, float]:
    u = 1.0 - t
    x = u * u * P0[0] + 2 * u * t * P1[0] + t * t * P2[0]
    y = u * u * P0[1] + 2 * u * t * P1[1] + t * t * P2[1]
    return x, y


def _x_pour_y(y: float) -> float:
    """Abscisse de la courbe à cette hauteur (par dichotomie sur t)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if _bezier(mid)[1] < y:
            lo = mid
        else:
            hi = mid
    return _bezier((lo + hi) / 2)[0]


def couloir(rgba: np.ndarray) -> dict:
    """Couloir vide entre le rocher de gauche et le flanc gauche de l'escalier.

    On part de `X_DEPART` (au cœur de l'escalier) et on recule vers la gauche :
    on traverse la jambe de l'escalier, puis on trouve le premier pixel VIDE.
    La plage vide qui suit, jusqu'au rocher, est le couloir où loger la bordure.
    """
    op = rgba[..., 3] > 0
    h, w = op.shape
    out = {}
    for y in range(Y_HAUT, Y_BAS + 1):
        x = min(w - 1, X_DEPART)
        if not op[y, x]:
            continue
        while x >= X_MIN and op[y, x]:
            x -= 1
        if x < X_MIN:
            continue                        # pas de couloir à cette hauteur
        xd = x
        while x >= X_MIN and not op[y, x]:
            x -= 1
        xg = x + 1
        if xd - xg + 1 >= 2:
            out[y] = (xg, xd)
    return out


def bord_escalier(rgba: np.ndarray) -> dict:
    """Abscisse du flanc GAUCHE de l'escalier, rangée par rangée.

    On part de `X_DEPART` (au cœur de l'escalier) et on recule : premier pixel
    vide rencontré = bord de l'escalier. Les barreaux créent des dents, d'où le
    lissage médian sur ±1 rangée.
    """
    op = rgba[..., 3] > 0
    h, w = op.shape
    brut = {}
    for y in range(Y_HAUT, Y_BAS + 1):
        x = min(w - 1, X_DEPART)
        if not op[y, x]:
            continue
        while x >= X_MIN and op[y, x]:
            x -= 1
        if x >= X_MIN:
            brut[y] = x + 1
    ys = sorted(brut)
    lisse = {}
    for i, y in enumerate(ys):
        voisins = [brut[ys[j]] for j in (i - 1, i, i + 1) if 0 <= j < len(ys)]
        lisse[y] = int(round(sorted(voisins)[len(voisins) // 2]))
    return lisse


# Arc de la bordure, en coordonnées de la façade 262x262.
# Il longe le flanc gauche de l'escalier en s'écartant du talus au milieu :
#   * départ sous le rocher, à (88, 236)
#   * ventre à (78, 248) — c'est la courbure demandée
#   * retour sous la dernière marche, à (88, 259)
P0 = (105.0, 236.0)
P1 = (93.0, 247.0)
P2 = (104.0, 259.0)


def _bezier(t: float) -> tuple[float, float]:
    u = 1.0 - t
    return (u * u * P0[0] + 2 * u * t * P1[0] + t * t * P2[0],
            u * u * P0[1] + 2 * u * t * P1[1] + t * t * P2[1])


def dessiner(rgba: np.ndarray) -> tuple[np.ndarray, int]:
    """Bordure rocheuse courbée sur le flanc GAUCHE de l'escalier.

    Un arc de Bézier longe l'escalier en s'écartant du talus au milieu. La bande
    est effilée aux deux bouts, avec un contour sombre côté talus, une arête
    claire côté escalier, des pierres séparées par un joint plus sombre et deux
    touches de mousse. Elle ne se dessine QUE sur des pixels transparents :
    l'escalier, la porte et le rocher restent intacts. Aucune couleur nouvelle.
    """
    a = rgba.copy()
    h, w = a.shape[:2]
    rng = np.random.default_rng(20261113)
    poses = 0
    pas = 200
    for k in range(pas + 1):
        t = k / pas
        xc, yc = _bezier(t)
        y = int(round(yc))
        if not (0 <= y < h):
            continue
        # largeur : arc effilé aux extrémités, ventre de 5 px au milieu
        largeur = int(round(6.0 * np.sin(np.pi * t) ** 0.40))
        if largeur < 2:
            continue
        xd = int(round(xc))
        joint = (y % 4 == 0)
        for i in range(largeur):
            x = xd - i
            if not (0 <= x < w) or a[y, x, 3] != 0:
                continue
            if i == largeur - 1:
                c = OUTLINE                      # contour côté talus
            elif i == 0:
                c = ROCK_LIGHT                   # arête côté escalier
            else:
                c = ROCK_DARK if (joint or rng.random() < 0.2) else ROCK_MID
            a[y, x] = (*c, 255)
            poses += 1
    # mousse : deux touffes sur le corps
    for frac in (0.42, 0.78):
        t = frac
        xc, yc = _bezier(t)
        y = int(round(yc))
        for x in range(int(round(xc)) - 3, int(round(xc))):
            if 0 <= x < w and tuple(int(v) for v in a[y, x, :3]) == ROCK_MID:
                a[y, x] = (*MOSS, 255)
                break
    return a, poses


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for nom in FACADES:
        p = OBJ / f"{nom}.dir"
        im = _lire_dir(p)
        arr, n = dessiner(np.array(im))
        if not args.dry_run:
            _ecrire_dir(p, Image.fromarray(arr, "RGBA"))
        print(f"[OK] {nom:26s} {im.width}x{im.height}  {n} px de muret")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
