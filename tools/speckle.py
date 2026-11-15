"""Nettoyage des pixels parasites d'une image RGBA.

Un « parasite » est un amas de quelques pixels dont la couleur tranche avec tous
ses voisins : il est remplacé par la couleur voisine dominante. L'alpha n'est
jamais modifié (la silhouette doit rester exactement celle du DS).

`donor` permet de restreindre les donneurs : sur une fenêtre, un pixel de CADRE
ne doit jamais prendre la couleur d'un pixel de VERRE (c'est ce qui semait des
bleu foncé au milieu du bois).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
# 4-voisins : on ne considère pas les diagonales comme des voisins « sûrs »
ORTHO = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _clusters(rgb, op, tol, max_area):
    """Groupes connexes de couleur exacte, de taille <= max_area, trop isolés."""
    h, w = op.shape
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    trouves = []
    for kid in np.unique(key[op]):
        sel = (key == kid) & op
        lab, n = ndimage.label(sel)
        if n == 0:
            continue
        sizes = ndimage.sum(sel, lab, range(1, n + 1))
        for li in np.where(sizes <= max_area)[0]:
            comp = lab == (li + 1)
            ys, xs = np.where(comp)
            if not len(ys):
                continue
            col = rgb[int(ys[0]), int(xs[0])].astype(np.float32)
            voisins = []
            for dy, dx in OFFSETS:
                yy, xx = ys + dy, xs + dx
                ok = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
                for py, px in zip(yy[ok], xx[ok]):
                    if comp[py, px] or not op[py, px]:
                        continue
                    voisins.append(rgb[py, px])
            if not voisins:
                continue
            v = np.array(voisins, np.float32)
            if np.abs(v - col[None, :]).sum(axis=1).min() < tol:
                continue                      # déjà proche d'un voisin : normal
            cles = (v[:, 0].astype(np.int64) << 16) | (v[:, 1].astype(np.int64) << 8) | v[:, 2].astype(np.int64)
            vals, counts = np.unique(cles, return_counts=True)
            dom = int(vals[np.argmax(counts)])
            trouves.append((ys, xs, np.array([(dom >> 16) & 255, (dom >> 8) & 255, dom & 255], np.int32)))
    return trouves


def clean(rgba: np.ndarray, max_area: int = 3, tol: float = 34.0, iters: int = 2,
          donor: np.ndarray | None = None):
    """Remplace les amas <= max_area px trop différents de leurs voisins.

    `donor` (booléen, même taille) limite les couleurs donneuses : par défaut
    toutes les pixels opaques, sur une fenêtre on passe le masque du cadre.
    Les remplacements d'une passe sont calculés puis appliqués d'un bloc, sinon
    les pixels déjà réécrits servaient de référence aux pixels suivants et
    pouvaient injecter une couleur qui n'existait pas dans la palette.
    """
    a = rgba.copy()
    if a.ndim != 3 or a.shape[2] != 4:
        return a, 0
    rgb = a[..., :3].astype(np.int32)
    alpha = a[..., 3]
    op = alpha > 0
    if not op.any():
        return a, 0
    donne = op if donor is None else (op & donor.astype(bool))
    if not donne.any():
        donne = op
    remplaces = 0

    for _ in range(max(1, iters)):
        avant = rgb.copy()
        trouves = _clusters(avant, donne, tol, max_area)
        if not trouves:
            break
        for ys, xs, new in trouves:
            for py, px in zip(ys, xs):
                rgb[py, px] = new
                remplaces += 1

    a[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    a[..., 3] = alpha
    return a, remplaces
