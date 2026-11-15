"""Nettoyage des pixels parasites d'une image RGBA.

Un « parasite » est un amas de quelques pixels dont la couleur tranche avec tous
ses voisins : il est remplacé par la couleur voisine dominante. L'alpha n'est
jamais modifié (la silhouette doit rester exactement celle du DS).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def clean(rgba: np.ndarray, max_area: int = 3, tol: float = 34.0, iters: int = 2):
    """Remplace les amas <= max_area px trop différents de leurs voisins."""
    a = rgba.copy()
    if a.ndim != 3 or a.shape[2] != 4:
        return a, 0
    h, w = a.shape[:2]
    rgb = a[..., :3].astype(np.int32)
    alpha = a[..., 3]
    op = alpha > 0
    if not op.any():
        return a, 0
    remplaces = 0

    for _ in range(max(1, iters)):
        # clé de couleur -> composantes connexes de couleur EXACTE
        key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
        change = 0
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
                # couleur du pixel
                y0, x0 = int(ys[0]), int(xs[0])
                col = rgb[y0, x0]
                # voisins hors de l'amas
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
                # distance de l'amas à CHAQUE couleur voisine : s'il est proche
                # d'au moins une, ce n'est pas un parasite
                d_min = np.abs(v - col[None, :]).sum(axis=1).min()
                if d_min < tol:
                    continue
                # couleur voisine dominante
                keys = (v[:, 0].astype(np.int32) << 16) | (v[:, 1].astype(np.int32) << 8) | v[:, 2].astype(np.int32)
                vals, counts = np.unique(keys, return_counts=True)
                dom = int(vals[np.argmax(counts)])
                new = np.array([(dom >> 16) & 255, (dom >> 8) & 255, dom & 255], np.int32)
                for py, px in zip(ys, xs):
                    rgb[py, px] = new
                    change += 1
        remplaces += change
        if change == 0:
            break

    a[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    a[..., 3] = alpha
    return a, remplaces
