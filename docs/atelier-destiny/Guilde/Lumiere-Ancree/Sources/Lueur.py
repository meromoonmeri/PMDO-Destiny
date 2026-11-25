#!/usr/bin/env python3
"""Normalize the generated light painting into a reusable RGBA light matte.

The saved PNG describes the *shape* at full range. Native room masks impose
low actual alpha, the plan occlusions and the wood response when projecting it.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

O = Path(__file__).resolve().parents[1]
ASSET = O / 'Calques' / 'Lueur-Generee.png'
INFO = ASSET.with_suffix('.json')
AMBER = (235, 166, 95)
CORE = (248, 203, 139)
REFLECTION_ALPHA = 25  # <= 9.81%, even at the brightest point of the animation.
CORE_ALPHA = 46        # The already-drawn pixels of the two buds only.
TIP_ALPHA = .105       # Static tint for the other, unlit buds.
CYCLE = dict(ms=9600, milieu=.84, amplitude=.119, harmonique=.034, decalage=.47)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(source):
    """Lift black to alpha zero, recenter by the warm core, preserve asymmetry."""
    source = Path(source)
    with Image.open(source) as im:
        w, h = im.size
        sm = np.asarray(im.convert('L').resize((w // 4, h // 4), Image.Resampling.LANCZOS), dtype=float)
    black = 3.
    top = np.percentile(sm, 99.94)
    assert top > 60 and np.percentile(sm, 50) < 6
    lum = np.maximum(0, sm - black) / (top - black)
    ys, xs = np.where(lum > .014)
    weights = np.power(lum, 7)
    cy, cx = nd.center_of_mass(weights)
    rx = max(cx - xs.min(), xs.max() - cx) * 1.065
    ry = max(cy - ys.min(), ys.max() - cy) * 1.075
    # Subpixel sampling preserves the soft brightest lobe and irregular roll-off.
    yy, xx = np.meshgrid(np.linspace(cy - ry, cy + ry, 105), np.linspace(cx - rx, cx + rx, 161), indexing='ij')
    field = nd.map_coordinates(lum, [yy, xx], order=1, mode='constant', cval=0.)
    y, x = np.meshgrid(np.linspace(-1, 1, 105), np.linspace(-1, 1, 161), indexing='ij')
    feather = np.clip((1 - np.abs(x)) / .11, 0, 1) * np.clip((1 - np.abs(y)) / .11, 0, 1)
    alpha = np.rint(255 * (np.clip(field, 0, 1) ** 1.10) * feather).astype(np.uint8)
    rgba = np.zeros((*alpha.shape, 4), np.uint8)
    rgba[alpha > 0, :3] = AMBER
    rgba[:, :, 3] = alpha
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba).save(ASSET, optimize=True)
    INFO.write_text(json.dumps(dict(provenance='Texture de lumière produite par le générateur d’images',
        sha256_image_generee=sha(source), sha256_masque=sha(ASSET),
        taille_source=[w, h], taille_masque=[161, 105],
        traitement='Luminance → alpha, retrait du fond noir et recentrage sur le cœur ; la faible opacité est réglée lors de la projection.'),
        ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(f'PASS · texture de lumière générée : {ASSET.name} ({ASSET.stat().st_size} o)')


class Matte:
    def __init__(self):
        self.info = json.loads(INFO.read_text(encoding='utf8'))
        assert sha(ASSET) == self.info['sha256_masque']
        with Image.open(ASSET) as im:
            self.field = np.asarray(im.getchannel('A'), dtype=np.float32) / 255
        self.my, self.mx = (np.asarray(self.field.shape) - 1) / 2

    def project(self, x, y, cx, cy, rx, ry, direction, slant=0.):
        # Flip the asymmetric lobe for facing pillars, then shear onto the local surface.
        sy = (y - cy) / ry
        sx = (x - cx - (y - cy) * slant * direction) * direction / rx
        return nd.map_coordinates(self.field, [(1 + sy) * self.my, (1 + sx) * self.mx], order=1, mode='constant', cval=0.)


def level(ms, lamp, cycle=CYCLE):
    theta = 2 * np.pi * (ms % cycle['ms']) / cycle['ms']
    p = lamp['p']
    return cycle['milieu'] + cycle['amplitude'] * np.sin(theta + p) + cycle['harmonique'] * np.sin(2 * theta - p + cycle['decalage'])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage : python Lueur.py <image générée>')
    normalize(sys.argv[1])
