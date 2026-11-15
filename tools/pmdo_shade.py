"""Re-shading « PMDO enrichi » depuis les formes DS.

Principe : le masque alpha (donc la silhouette DS) n'est JAMAIS touché.
Chaque région de couleur plate reçoit un volume propre (occlusion de bord + lumière
du haut), puis la couleur est remontée/descendue le long d'une micro-ramp : les
aplats deviennent des dégradés.

Deux garde-fous ajoutés après repérage en jeu :
  * `relief` : les bois SOMBRES ne reçoivent pas de relief. Sans ce facteur, le
    grain rond du plafond de l'accueil (couleur 64,31,17) était éclairci par
    endroits et se transformait en taches lumineuses circulaires ;
  * le fond marron du plan (#68482F) est restitué octet pour octet.
"""
import numpy as np
from scipy import ndimage

LUM = np.array([0.299, 0.587, 0.114], np.float32)


def _lum(c):
    return float(np.dot(np.asarray(c, np.float32), LUM))


def backdrop_mask(rgba):
    """Le fond marron #68482F (vide du plan) ne doit jamais être ombré."""
    rgb = rgba[..., :3].astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    vals, counts = np.unique(key[rgba[..., 3] > 0], return_counts=True)
    if len(vals) == 0:
        return np.zeros(rgba.shape[:2], bool)
    dom = vals[np.argmax(counts)]
    r, g, b = (dom >> 16) & 255, (dom >> 8) & 255, dom & 255
    return ((np.abs(rgb[..., 0] - r) <= 2) & (np.abs(rgb[..., 1] - g) <= 2)
            & (np.abs(rgb[..., 2] - b) <= 2) & (rgba[..., 3] > 0))


def region_field(rgba, kind):
    """Champ d'éclairage : volume par région (architecture) + gradient vertical."""
    mask = rgba[..., 3] > 0
    h, w = mask.shape
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return np.zeros((h, w), np.float32), mask

    rgb = rgba[..., :3].astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    s_region = np.zeros((h, w), np.float32)

    use_region = {"walls": True, "supports": True, "fringe": True, "floor": False}.get(kind, True)
    if use_region:
        for kid in np.unique(key[mask]):
            sel = (key == kid) & mask
            if sel.sum() < 5:
                continue
            dist = ndimage.distance_transform_edt(sel)
            dmax = dist.max()
            # strie fine (1-2 px d'épaisseur) : le relief y créerait une crête
            # claire en ligne -> on la laisse plate, elle garde son rôle de grain.
            if dmax < 3.0:
                continue
            depth = (dist / dmax).astype(np.float32)
            s_region = np.where(sel, (depth - 0.42) * 1.35, s_region)
        # les stries du bois sont des régions d'1 px : sans lissage elles se
        # cassent en bruit de quantification -> on lisse le volume des régions.
        sigma = {"walls": 6.0, "supports": 5.0, "fringe": 3.0}.get(kind, 0.0)
        if sigma > 0:
            m = mask.astype(np.float32)
            num = ndimage.gaussian_filter(s_region * m, sigma, mode="nearest")
            den = ndimage.gaussian_filter(m, sigma, mode="nearest")
            s_region = np.where(den > 1e-6, num / np.maximum(den, 1e-6), 0.0)

    # gradient vertical global (lumière chaude venant du haut)
    y0, y1 = float(ys.min()), float(ys.max())
    Y = np.repeat(((np.arange(h, dtype=np.float32) - y0) / max(1.0, y1 - y0))[:, None], w, axis=1)
    top = (1.0 - Y) * 2.0 - 1.0
    # Amplitude très basse : sur une grande surface plate, un gradient même
    # faible finit par franchir un palier de la rampe et laisse une BANDE
    # horizontale visible (repérée sur les murs de l'accueil). Le volume vient
    # donc du relief local + de l'occlusion, pas d'un dégradé d'ensemble.
    amp = {"floor": 0.10, "walls": 0.16, "supports": 0.18, "fringe": 0.08}.get(kind, 0.14)
    s = s_region * 1.05 + top * amp

    # occlusion de silhouette (le pourtour de la salle s'assombrit)
    ao = np.exp(-ndimage.distance_transform_edt(mask) / 4.0).astype(np.float32)
    s = s - ao * {"floor": 0.16, "walls": 0.34, "supports": 0.38, "fringe": 0.14}.get(kind, 0.28)
    s[backdrop_mask(rgba)] = 0.0
    return np.clip(s / 1.45, -1.0, 1.0).astype(np.float32), mask


def ramp_for(c, steps=4):
    """Micro-ramp : conserve la teinte, étend clair/sombre de façon progressive."""
    c = np.asarray(c, np.float32)
    lit_tint = np.array([255, 232, 168], np.float32)
    dark_tint = np.array([26, 13, 8], np.float32)
    ramp = [tuple(int(v) for v in c)]
    for k in range(1, steps + 1):
        t = (k / steps) ** 0.85
        ramp.append(tuple(int(round(v)) for v in np.clip(c + (lit_tint - c) * 0.30 * t, 0, 255)))
    for k in range(1, steps + 1):
        t = (k / steps) ** 0.85
        ramp.append(tuple(int(round(v)) for v in np.clip(c + (dark_tint - c) * 0.38 * t, 0, 255)))
    return ramp, steps


PRESETS = {
    # `dark` = facteur appliqué au côté sombre : on éclaire franchement, on assombrit peu
    "floor":    dict(steps=3, bands=5, strength=0.85, sat=1.03, dark=0.18),
    "walls":    dict(steps=4, bands=7, strength=1.20, sat=1.05, dark=0.60),
    "supports": dict(steps=4, bands=7, strength=1.20, sat=1.08, dark=0.60),
    "fringe":   dict(steps=4, bands=6, strength=0.80, sat=1.06, dark=0.75),
    "shadows":  dict(steps=2, bands=3, strength=0.35, sat=1.00, dark=1.00),
}


def reskin(rgba, kind, **kw):
    cfg = dict(PRESETS.get(kind, dict(steps=4, bands=7, strength=1.10, sat=1.05)))
    cfg.update(kw)
    return _reskin(rgba, kind, **cfg)


def _reskin(rgba, kind, steps=4, bands=7, strength=1.10, sat=1.05, dark=0.60,
            relief_min=30.0, relief_span=60.0):
    a = rgba.copy()
    bg = backdrop_mask(rgba)
    s, mask = region_field(a, kind)
    if not mask.any():
        return a, 0, 0
    if bands > 1:
        s = np.round(s * bands) / bands
    if sat != 1.0:
        f = a[..., :3].astype(np.float32)
        g = f @ LUM
        f = np.clip(g[..., None] + (f - g[..., None]) * sat, 0, 255)
        a[..., :3] = f.astype(np.uint8)

    rgb = a[..., :3]
    uniq, inv = np.unique(rgb[mask].reshape(-1, 3), axis=0, return_inverse=True)
    bands_u, band_id = np.unique(s[mask], return_inverse=True)

    lut = np.zeros((len(uniq), len(bands_u), 3), np.uint8)
    for ci, c in enumerate(uniq):
        base = np.asarray(c, np.float32)
        bl = _lum(base)
        if bl < 34:                             # contours : on ne les touche pas
            lut[ci, :, :] = base.astype(np.uint8)
            continue
        # pas de relief sur les bois sombres : sinon le grain rond du plafond
        # se transforme en taches lumineuses (repéré en jeu, accueil)
        relief = float(np.clip((bl - relief_min) / relief_span, 0.0, 1.0))
        ramp, k = ramp_for(base, steps=steps)
        for bi, bv in enumerate(bands_u):
            b = float(bv)
            eff = strength * relief if b >= 0 else strength * dark
            t = b * eff * steps
            t = max(-steps, min(steps, t))

            # TON LE PLUS PROCHE, sans interpolation entre deux tons de rampe.
            # L'interpolation créait des dizaines de teintes intermédiaires par
            # couleur de base : à l'écran cela se lisait comme un dégradé flou
            # (« filtre ») au lieu d'un ombrage pixel-art en escalier.
            i = int(round(t))

            def get(idx):
                if idx >= 0:
                    return np.array(ramp[min(idx, steps)], np.float32)
                return np.array(ramp[steps + min(-idx, steps)], np.float32)

            lut[ci, bi] = np.round(get(i)).astype(np.uint8)

    out = lut[inv, band_id]
    flat = a[..., :3].reshape(-1, 3)
    flat[np.where(mask.reshape(-1))[0]] = out
    a[..., :3] = flat.reshape(a.shape[:2] + (3,))
    if bg.any():                                # fond restitué octet pour octet
        a[..., :3][bg] = rgba[..., :3][bg]
    return a, len(uniq), len(np.unique(out.reshape(-1, 3), axis=0))
