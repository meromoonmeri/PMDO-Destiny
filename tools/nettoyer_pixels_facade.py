#!/usr/bin/env python3
"""Nettoyage des pixels parasites de la façade `Guilde_HD_*`.

Défaut relevé sur les captures du joueur : de petits **éclats bleu-violet**
(teinte de la pierre des cailloux) semés au milieu du bois chaud — sur les
poutres, les linteaux, la porte. Ils n'ont rien à voir avec les vrais cailloux
du pied de l'arbre, qui sont de vraies pierres appareillées avec des reflets
orangés.

Méthode
-------
La détection se fait sur la version **Jour**, seule ambiance où la teinte
pierre se distingue sans ambiguïté du bois. Le masque est ensuite appliqué aux
**quatre** ambiances : les sprites sont des recoloriages du même dessin, les
coordonnées sont donc identiques.

Un amas est retenu si :
  * 2 à 12 px (un éclat, pas un caillou) ;
  * teinte froide : b >= g, b >= r-14, peu saturée ;
  * voisinage chaud (bois) à plus de 70 %, ou vert (feuillage) à plus de 55 % ;
  * **aucun reflet orangé clair à proximité** — sur cette façade, tout vrai
    caillou est surmonté d'un éclat orangé : c'est la signature qui distingue
    une pierre d'une salissure.

Garde-fou supplémentaire : aucun pixel du masque ne peut être à moins de 5 px
d'une composante froide de plus de 12 px (les cailloux du pied de l'arbre).

Le pixel est remplacé par la couleur voisine dominante **elle aussi non froide** :
un éclat ne peut pas être « réparé » par un autre éclat.
L'alpha n'est jamais modifié : la silhouette reste exactement celle du DS.

Le script est idempotent : relancé sur une façade déjà nettoyée, il ne change
plus rien.

Usage :
    python3 tools/nettoyer_pixels_facade.py [--dry-run]
"""
from __future__ import annotations

import argparse
import io
import struct
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = Path(__file__).resolve().parents[1]
OBJ = REPO / "game/Content/Object"

# (référence pour la détection, [ambiances à corriger])
PAIRES = [
    ("Guilde_HD_Jour", ["Guilde_HD_Jour", "Guilde_HD_Aube",
                        "Guilde_HD_Crepuscule", "Guilde_HD_Nuit"]),
    ("Guilde_HD_Porte_Ouverte_Jour", ["Guilde_HD_Porte_Ouverte_Jour",
                                      "Guilde_HD_Porte_Ouverte_Aube",
                                      "Guilde_HD_Porte_Ouverte_Crepuscule",
                                      "Guilde_HD_Porte_Ouverte_Nuit"]),
]

OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
TAILLE_MIN, TAILLE_MAX = 2, 12
MARGE = 4
SEUIL_CHAUD = 0.70
SEUIL_VERT = 0.55
DIST_CAILLOU = 5.0
TAILLE_CAILLOU = 12


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


def _masques(a: np.ndarray):
    op = a[..., 3] > 0
    r = a[..., 0].astype(int); g = a[..., 1].astype(int); b = a[..., 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    froid = (b >= g - 1) & (b >= r - 14) & ((mx - mn) <= 34) & op
    chaud = (r >= b + 18) & op
    vert = (g >= r + 10) & (g >= b + 10) & op
    # reflet de pierre : sur cette façade, TOUT vrai caillou est surmonté d'un
    # éclat orangé clair. C'est la signature qui distingue une pierre d'une
    # salissure bleu-violet perdue au milieu du bois.
    reflet = (r >= 190) & (g >= 105) & (g <= 185) & (b <= 110) & op
    return froid, chaud, vert, reflet


def masque_eclats(a: np.ndarray) -> np.ndarray:
    """Masque des éclats de pierre isolés dans le bois ou le feuillage."""
    froid, chaud, vert, reflet = _masques(a)
    h, w = froid.shape
    lab, n = ndimage.label(froid)
    m = np.zeros_like(froid)
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if not (TAILLE_MIN <= len(ys) <= TAILLE_MAX):
            continue
        y0, y1 = max(0, ys.min() - MARGE), min(h, ys.max() + MARGE + 1)
        x0, x1 = max(0, xs.min() - MARGE), min(w, xs.max() + MARGE + 1)
        z = lab[y0:y1, x0:x1] == i
        if not (~z).any():
            continue
        if reflet[y0:y1, x0:x1][~z].any():
            continue                   # c'est un vrai caillou : il a son reflet
        fc = chaud[y0:y1, x0:x1][~z].mean()
        fv = vert[y0:y1, x0:x1][~z].mean()
        if fc > SEUIL_CHAUD or fv > SEUIL_VERT:
            m |= (lab == i)
    return m


def proteger_cailloux(a: np.ndarray, masque: np.ndarray) -> np.ndarray:
    """Retire du masque tout ce qui est proche d'un vrai caillou."""
    froid, _, _, _ = _masques(a)
    lab, n = ndimage.label(froid)
    if n == 0:
        return masque
    tailles = ndimage.sum(froid, lab, range(1, n + 1))
    gros = np.isin(lab, np.where(np.array(tailles) > TAILLE_CAILLOU)[0] + 1)
    dist = ndimage.distance_transform_edt(~gros)
    return masque & (dist >= DIST_CAILLOU)


def reparer(a: np.ndarray, masque: np.ndarray) -> tuple[np.ndarray, int]:
    """Remplace chaque éclat par la couleur voisine dominante non froide."""
    out = a.copy()
    h, w = out.shape[:2]
    rgb = out[..., :3].astype(np.int32)
    op = out[..., 3] > 0
    froid, _, _, _ = _masques(out)
    lab, n = ndimage.label(masque)
    poses = 0
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if not len(ys):
            continue
        comp = lab == i
        voisins = []
        for dy, dx in OFFSETS:
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
            for py, px in zip(yy[ok], xx[ok]):
                if comp[py, px] or not op[py, px] or froid[py, px]:
                    continue          # jamais un autre éclat comme référence
                voisins.append(tuple(int(v) for v in rgb[py, px]))
        if not voisins:
            continue
        dom = np.array(Counter(voisins).most_common(1)[0][0], np.int32)
        for py, px in zip(ys, xs):
            rgb[py, px] = dom
            poses += 1
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return out, poses


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    total = 0
    for ref, cibles in PAIRES:
        p_ref = OBJ / f"{ref}.dir"
        if not p_ref.exists():
            print(f"[--] {ref} absent")
            continue
        a_ref = np.array(_lire_dir(p_ref))
        masque = proteger_cailloux(a_ref, masque_eclats(a_ref))
        print(f"[REF] {ref:34s} {int(masque.sum()):4d} px dans le masque")
        for nom in cibles:
            p = OBJ / f"{nom}.dir"
            im = _lire_dir(p)
            arr, n = reparer(np.array(im), masque)
            total += n
            if not args.dry_run:
                _ecrire_dir(p, Image.fromarray(arr, "RGBA"))
            print(f"[OK ] {nom:34s} {n:4d} px réparés")
    print(f"TOTAL : {total} pixels réparés")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
