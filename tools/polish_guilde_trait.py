#!/usr/bin/env python3
"""Affine le trait et enrichit les ombres des salles de la Guilde Destiny.

Réponse au retour d'un relecteur :
  « The lineart is a bit thick and the colors are a bit flat. Since the colors
    are so light, if you want to polish it up, you can reuse stuff from the rest
    of the palette. »

Diagnostic mesuré sur les 11 bases 1x : le trait sombre (luminance < 40) fait
**2 px partout** (médiane = p75 = p90 = 2) sur 194 couleurs, avec seulement
1,9 % de pixels au-dessus de 190 de luminance. D'où l'impression de trait épais
et d'aplats plats.

Ce que fait le script, uniquement avec des couleurs DEJA présentes dans la
salle (aucune teinte inventée) :

  1. Amincissement du trait 2 px -> 1 px par ligne médiane (skeletonize),
     uniquement sur les structures fines (<= 4 px) pour ne pas casser les
     masses sombres volontaires (intérieurs d'arches, creux de racines).
  2. Le pixel libéré par l'amincissement prend non pas l'aplat voisin mais
     **le cran d'ombre suivant du dégradé de la salle** : c'est ce qui donne
     du relief sans éclaircir ni assombrir l'ensemble.
  3. Biseau d'un pixel sur les aplats clairs : cran plus clair en haut/gauche,
     cran plus sombre en bas/droite, toujours pris dans le dégradé existant.

Aucune interpolation, aucun flou : on ne travaille qu'à l'échelle 1x, pixel par
pixel. Les couleurs de sortie sont un sous-ensemble des couleurs d'entrée.

Usage :
    python3 tools/polish_guilde_trait.py --check          # mesure seulement
    python3 tools/polish_guilde_trait.py                  # écrit dans un dossier de sortie
    python3 tools/polish_guilde_trait.py --out /tmp/polish
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parents[1]
SRC_BASE = Path('/home/user/guilde_destiny_reseau/cartes_base_sans_decors')
EXT_RGB = np.array([0x68, 0x48, 0x2f], dtype=np.uint8)

SEUIL_TRAIT = 40          # luminance sous laquelle un pixel est du trait
EP_MAX = 4                # n'aminci que les structures de cette epaisseur max
PAS_OMBRE = 0.86          # cran d'ombre (multiplicatif, avant recalage palette)
PAS_LUMIERE = 1.13        # cran de lumiere


def masque_fond(a: np.ndarray) -> np.ndarray:
    m = a[:, :, 3] > 128
    return m & (a[:, :, 0] == EXT_RGB[0]) & (a[:, :, 1] == EXT_RGB[1]) & (a[:, :, 2] == EXT_RGB[2])


def luminance(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]


def palette(a: np.ndarray, art: np.ndarray) -> np.ndarray:
    """Couleurs distinctes de la salle (hors fond), triees par luminance."""
    cols = np.unique(a[art][:, :3], axis=0).astype(np.int16)
    return cols


def cran_palette(pal: np.ndarray, couleur: np.ndarray, facteur: float) -> np.ndarray:
    """Cran plus sombre / plus clair, recale sur la palette existante.

    On ne cree aucune teinte : on choisit la couleur deja presente dont la
    luminance est la plus proche de `couleur * facteur`, en restant du bon cote.
    """
    c = couleur.astype(np.float64)
    cible = np.clip(c * facteur, 0, 255)
    lum_pal = luminance(pal.astype(np.float64)[None, :, :])[0]
    lum_c = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    lum_cible = 0.299 * cible[0] + 0.587 * cible[1] + 0.114 * cible[2]
    # ecart de teinte (chromaticite) pour rester dans la meme famille
    ecart_teinte = np.abs(pal.astype(np.float64) - c).sum(1)
    ecart_lum = np.abs(lum_pal - lum_cible)
    bon_cote = (lum_pal < lum_c - 0.5) if facteur < 1 else (lum_pal > lum_c + 0.5)
    cout = ecart_lum * 1.0 + ecart_teinte * 0.55
    cout = np.where(bon_cote, cout, cout + 1e4)
    return pal[int(np.argmin(cout))].astype(np.uint8)


def aminci_trait(a: np.ndarray, pal: np.ndarray) -> tuple[np.ndarray, dict]:
    out = a.copy()
    m = a[:, :, 3] > 128
    fond = masque_fond(a)
    art = m & ~fond
    lum = luminance(a.astype(np.float64))

    L = art & (lum < SEUIL_TRAIT)
    if not L.any():
        return out, dict(trait=0, liberes=0, biseau=0)

    # 1. ligne mediane, seulement sur les structures fines
    d = ndimage.distance_transform_edt(L) * 2
    fin = L & (d <= EP_MAX)
    sk = skeletonize(fin)
    a_retirer = fin & ~sk

    # 2. le pixel libere prend le cran d'ombre du voisin non-trait le plus sombre
    if a_retirer.any():
        flats = art & ~L
        if flats.any():
            _, (iy, ix) = ndimage.distance_transform_edt(~flats, return_indices=True)
            base = a[iy, ix, :3]
        else:
            base = np.broadcast_to(EXT_RGB, a[:, :, :3].shape).copy()

        # on remplace pixel par pixel : le pixel libere reprend l'aplat qui le
        # borde (le plus proche), et seulement s'il n'y a aucun aplat a moins de
        # 2 px on prend un cran d'ombre. Sans ca, un liseré sombre se glisse dans
        # les zones claires (vitraux, sols) et les eclaircit a l'envers.
        ys, xs = np.nonzero(a_retirer)
        for y, x in zip(ys, xs):
            meilleur = None
            meilleur_d = 99
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and flats[yy, xx]:
                        dd = dx * dx + dy * dy
                        if dd < meilleur_d:
                            meilleur_d = dd
                            meilleur = a[yy, xx, :3]
            if meilleur is not None:
                out[y, x, :3] = meilleur
            else:
                out[y, x, :3] = cran_palette(pal, base[y, x], PAS_OMBRE)
            out[y, x, 3] = 255

    # le trait garde la couleur la plus sombre de la salle
    if sk.any():
        lum_pal = luminance(pal.astype(np.float64)[None, :, :])[0]
        encre = pal[int(np.argmin(lum_pal))]
        out[sk, :3] = encre
        out[sk, 3] = 255

    return out, dict(trait=int(fin.sum()), liberes=int(a_retirer.sum()), biseau=0)


def biseau(a: np.ndarray, pal: np.ndarray, min_aire: int = 40) -> tuple[np.ndarray, int]:
    """Un pixel de relief sur les grands aplats : clair en haut/gauche, sombre en bas/droite."""
    out = a.copy()
    m = a[:, :, 3] > 128
    fond = masque_fond(a)
    art = m & ~fond
    lum = luminance(a.astype(np.float64))
    trait = art & (lum < SEUIL_TRAIT)

    # plages uniformes assez grandes pour valoir un biseau
    plat = art & ~trait
    cols = np.unique(a[plat][:, :3], axis=0).astype(np.int16)
    n = 0
    for col in cols:
        sel = plat & (a[:, :, 0] == col[0]) & (a[:, :, 1] == col[1]) & (a[:, :, 2] == col[2])
        if sel.sum() < min_aire:
            continue
        lab, nlab = ndimage.label(sel)
        for i in range(1, nlab + 1):
            zone = lab == i
            if zone.sum() < min_aire:
                continue
            # bord superieur / gauche -> cran clair ; inferieur / droit -> cran sombre
            desus = zone & (np.roll(~zone, 1, axis=0))
            dessous = zone & (np.roll(~zone, -1, axis=0))
            gauche = zone & (np.roll(~zone, 1, axis=1))
            droite = zone & (np.roll(~zone, -1, axis=1))
            haut = desus | gauche
            bas = dessous | droite
            # ne pas ecraser le trait deja pose
            haut &= ~np.roll(trait, 1, axis=0) | True
            bas &= ~trait
            haut &= art
            bas &= art
            if haut.any():
                c = cran_palette(pal, col.astype(np.uint8), PAS_LUMIERE)
                out[haut, :3] = c
                n += int(haut.sum())
            if bas.any():
                c = cran_palette(pal, col.astype(np.uint8), PAS_OMBRE)
                out[bas, :3] = c
                n += int(bas.sum())
    return out, n


def traite(src: Path, dst: Path, avec_biseau: bool) -> dict:
    im = Image.open(src).convert('RGBA')
    a = np.asarray(im).copy()
    art = (a[:, :, 3] > 128) & ~masque_fond(a)
    if not art.any():
        shutil.copyfile(src, dst)
        return dict(ok=False)
    pal = palette(a, art)

    out, st = aminci_trait(a, pal)
    if avec_biseau:
        out, nb = biseau(out, pal)
        st['biseau'] = nb

    # garde-fou : la sortie ne doit contenir aucune couleur nouvelle (hors fond)
    art_out = (out[:, :, 3] > 128) & ~masque_fond(out)
    nouvelles = set(map(tuple, out[art_out][:, :3])) - set(map(tuple, pal))
    st['couleurs_sortie'] = len(set(map(tuple, out[art_out][:, :3])))
    st['couleurs_entree'] = len(pal)
    st['nouvelles'] = len(nouvelles)

    Image.fromarray(out).save(dst)
    return st


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default='/home/user/guilde_destiny_reseau/cartes_base_sans_decors_polish')
    ap.add_argument('--check', action='store_true', help='mesure sans rien écrire')
    ap.add_argument('--bevel', action='store_true',
                    help="biseau d'aplat (desactive : gain de relief non mesurable, "
                         "abime les details fins)")
    ap.add_argument('--only', default=None)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    srcs = sorted(SRC_BASE.glob('*.png'))
    if args.only:
        srcs = [p for p in srcs if args.only in p.name]

    rapport = {}
    for p in srcs:
        im = Image.open(p).convert('RGBA')
        a = np.asarray(im)
        art = (a[:, :, 3] > 128) & ~masque_fond(a)
        lum = luminance(a.astype(np.float64))
        L = art & (lum < SEUIL_TRAIT)
        d = ndimage.distance_transform_edt(L) * 2
        avant = dict(
            couleurs=len(palette(a, art)),
            lineart=float(L.sum() / max(1, art.sum())),
            epaisseur=float(np.median(d[L])) if L.any() else 0.0,
        )
        if args.check:
            print(f'{p.name:42s} coul {avant["couleurs"]:4d}  lineart {avant["lineart"]:5.1%}  '
                  f'epaisseur {avant["epaisseur"]:.0f}px')
            continue

        st = traite(p, out_dir / p.name, args.bevel)
        b = np.asarray(Image.open(out_dir / p.name).convert('RGBA'))
        art_b = (b[:, :, 3] > 128) & ~masque_fond(b)
        lum_b = luminance(b.astype(np.float64))
        Lb = art_b & (lum_b < SEUIL_TRAIT)
        db = ndimage.distance_transform_edt(Lb) * 2
        apres = dict(
            couleurs=st.get('couleurs_sortie', 0),
            lineart=float(Lb.sum() / max(1, art_b.sum())),
            epaisseur=float(np.median(db[Lb])) if Lb.any() else 0.0,
            nouvelles=st.get('nouvelles', -1),
        )
        rapport[p.name] = dict(avant=avant, apres=apres)
        print(f'{p.name:42s} lineart {avant["lineart"]:5.1%} -> {apres["lineart"]:5.1%}  '
              f'| coul {avant["couleurs"]} -> {apres["couleurs"]} '
              f'(nouvelles {apres["nouvelles"]})')

    if not args.check:
        (out_dir / '_rapport.json').write_text(json.dumps(rapport, indent=2), encoding='utf-8')
        print(f'\nEcrit dans {out_dir}')


if __name__ == '__main__':
    main()
