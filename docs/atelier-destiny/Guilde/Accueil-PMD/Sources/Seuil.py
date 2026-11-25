#!/usr/bin/env python3
"""Adapt the genuine PMU doormat and the raster light of G01P02A to Destiny's south threshold."""
import base64
import hashlib
import json
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
SOURCE = ROOT / 'Guilde-Destiny-Bourgeons-PMD.html'
MARK = '<script id="donnees" type="application/json">'
ID = 'guilde_destiny_accueil'
ORIGINAL = 'https://projectpokemon.org/home/gallery/image/77350-g01p02apng/'
REF_HASH = '2bd9bf5a11a2ef3a861e4ba8f48468f20d06ba177a765ccd370d4ca9f1e387b9'
PHASE_LIGHT = (1, .84, .76, .53)
REFERENCE_DETAIL = (160, 203, 248, 259)
REFERENCE_LIGHT = (171, 227, 237, 255)


def read_page(path=SOURCE):
    head, tail = path.read_text(encoding='utf-8').split(MARK, 1)
    raw, tail = tail.split('</script>', 1)
    return head, json.loads(raw), tail


def decode(uri):
    return Image.open(BytesIO(base64.b64decode(uri.rsplit(',', 1)[-1]))).convert('RGBA')


def pack(img):
    f = BytesIO()
    img.save(f, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(f.getvalue()).decode('ascii')


def colour(img, scheme):
    lut = np.asarray(scheme['lut'], dtype=np.uint8)
    p = np.array(img)
    for j in range(3):
        p[..., j] = lut[j, p[..., j]]
    p[p[..., 3] == 0] = 0
    return Image.fromarray(p)


def opening(r, cx, bottom):
    # This is the visible floor span, not the narrower 8-pixel tile trigger.
    base, front = (np.array(decode(r[k])) for k in ('base', 'front'))
    paper = base[0, 0, :3]
    floor = (base[..., 3] > 0) & (base[..., :3] != paper).any(2) & (front[..., 3] == 0)
    assert floor[bottom - 1, cx] and not floor[bottom, cx]
    row = floor[bottom - 1]
    left, right = np.flatnonzero(~row[:cx])[-1] + 1, cx + np.flatnonzero(~row[cx:])[0]
    sill = bottom - 1
    while np.array_equal(base[sill - 1, cx], base[bottom - 1, cx]):
        sill -= 1
    assert (int(left), int(right), sill) == (224, 288, 349)
    return int(left), int(right), sill, floor


def doormat(item, w, h):
    # Rebuild the PMU weave to size, without stretching the chequered selvedges.
    # The 1-pixel contact seams sit under the frames, not over them.
    src = np.array(decode(item['m'][0])); cloth = src[:24, :40].copy()
    assert src.shape == (26, 42, 4) and (cloth[..., 3] == 255).all()
    xs = np.r_[0:5, 5 + np.arange(w - 12) % 30, 35:40]
    ys = np.r_[0:5, 5 + np.arange(h - 10) % 14, 19:24]
    p = cloth[ys[:, None], xs].copy()
    p[5:-5, 5:-5, :3] = (226, 74, 59)
    for old, new in [((226, 74, 59), (223, 88, 73)), ((246, 82, 66), (243, 105, 85)),
                     ((246, 98, 106), (248, 124, 107))]:
        p[(p[..., :3] == old).all(2), :3] = new
    border = np.zeros((h + 1, w, 4), np.uint8)
    border[:h, 1:-1] = p
    border[:h, (0, -1)] = (51, 27, 16, 132)
    border[h, 1:-1] = (49, 25, 13, 103)
    rug = Image.fromarray(border)
    a = np.array(Image.open(OUT / 'Reference/Motif-aile-Halcyon.png').convert('RGB'))
    motif = (a != (142, 44, 34)).any(2)
    wing = Image.fromarray(np.dstack((a * motif[..., None], motif.astype(np.uint8) * 255)))
    emblem_w = (w // 2) - 2
    wing = wing.crop(wing.getbbox()).resize((emblem_w, emblem_w // 2), Image.Resampling.NEAREST)
    rug.alpha_composite(wing, ((w - wing.width) // 2, (h - wing.height) // 2 - 2))
    return rug


def light_map(ref):
    # G01P02A has a painted, static halo, not a separate animatable light asset.
    # Isolate the actual two pink raster arches by their palette.
    a = np.array(ref.crop(REFERENCE_LIGHT).convert('RGB'))
    g = np.arange(a.shape[0])[:, None] + REFERENCE_LIGHT[1]
    bands = np.zeros(a.shape[:2], np.uint8)
    for tone in [(239, 151, 143), (255, 159, 151), (255, 175, 167)]:
        bands[(a == tone).all(2) & (g <= 244)] = 1
    bands[(a == (255, 207, 199)).all(2) & (g <= 244)] = 2
    lp = (g >= 248) & (a[..., 0] == 255) & (a[..., 1] >= 223) & (a[..., 2] >= 191)
    bands[lp] = 3
    # Decontaminate the apron edge: translucent cream instead of blue from the reference surround.
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[bands == 1] = (249, 244, 250, 97)
    out[bands == 2] = (255, 245, 238, 191)
    out[lp, :3] = a[lp]
    out[lp, 3] = np.where(a[lp, 1] >= 247, 252, 216)
    for edge, opacity in [((79, 79, 87), 40), ((111, 103, 103), 67), ((159, 143, 103), 104),
                          ((183, 175, 167), 148), ((223, 207, 199), 200)]:
        mask = (g >= 251) & (a == edge).all(2)
        out[mask] = (255, 245, 227, opacity)
        bands[mask] = 4
    # The original lip follows the lower fringe; recover its bright checker pixels as a veil.
    beads = (g >= 244) & (g < 248) & (a == (255, 255, 247)).all(2)
    out[beads] = (255, 253, 235, 102)
    bands[beads] = 4
    assert (bands == 1).sum() > 390 and (bands == 2).sum() > 320 and (bands == 3).sum() > 350
    return out, bands, {str(i): int((bands == i).sum()) for i in range(1, 5)}


def fit_light(raw, bands, rug, ry, sill, bottom):
    # Fit the arches to the weave and the bright lip to the wood edge independently.
    # One resize of the whole halo would place the lip relative to the carpet again.
    w, h = rug.size
    arch_raster = Image.fromarray(np.where(np.isin(bands, (1, 2))[..., None], raw, 0))
    arches = arch_raster.crop(arch_raster.getbbox())
    y = ry + round(.33 * (h - 1))
    lip_y = sill - 4
    assert lip_y + 7 == bottom
    arch = arches.resize((w - 12, lip_y - y), Image.Resampling.NEAREST)
    lip = np.array(Image.fromarray(raw[-7:]).resize((w, 7), Image.Resampling.NEAREST))
    # The top of the spill rests on the trim. Its white edge is on the last plank.
    lip[..., 3] = np.rint(lip[..., 3] * np.asarray([.32, .51, .70, .93, 1, 1, 1])[:, None])
    light = Image.new('RGBA', (w, bottom - y))
    light.alpha_composite(arch, (6, 0))
    light.alpha_composite(Image.fromarray(lip), (0, lip_y - y))
    a = np.array(light)[..., 3]
    assert a.max() >= 250 and np.nonzero(a >= 250)[0].min() + y == sill
    return light, y


def build(d):
    path = OUT / 'Reference/G01P02A-Entree.png'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == REF_HASH
    ref = Image.open(path).convert('RGBA'); assert ref.size == (408, 312)
    r = next(r for r in d['rooms'] if r['id'] == ID)
    item = next(a for a in d['catalog'] if a['id'] == 'paillasson_rouge')
    assert item['sheet'] == 'Guilde_Imm_pmu_paillasson_rouge'
    x, gy, w, h = next(g for g in r['gates'] if g['id'] == 'SortieGuilde')['rect']
    bottom = gy + h; cx = x + w // 2
    assert (x, gy, w, h, bottom) == (232, 336, 48, 16, 352) and r['south']['bottom'] == bottom
    left, right, sill, visible_floor = opening(r, cx, bottom)
    width = right - left
    depth = round(width * .56)
    rx, ry = left, sill - depth
    rug = doormat(item, width, depth)
    raw, bands, counts = light_map(ref)
    light, ly = fit_light(raw, bands, rug, ry, sill, bottom)
    def floor_check(asset, xx, yy):
        j, i = np.nonzero(np.asarray(asset)[..., 3])
        assert ((xx + i >= left) & (xx + i < right) & (yy + j < bottom)).all()
        assert visible_floor[yy + j, xx + i].all()
    floor_check(rug, rx, ry); floor_check(light, left, ly)
    area = dict(x=left, y=ry, w=width, h=bottom - ry)
    phases = []
    for i, level in enumerate(PHASE_LIGHT):
        palette = d['nuits'][r['nuit']] if i == 3 else d['lumieres'][r['nuit']][i]
        a = np.array(light); a[..., 3] = np.rint(a[..., 3] * level)
        if i in (1, 2, 3):
            # Dim only the threshold transfer, not the room or its night foliage.
            a[..., 2] = np.rint(a[..., 2] * (1, .982, .946, .915)[i])
        phases.append([[rx, ry, pack(colour(rug, palette))], [left, ly, pack(Image.fromarray(a))]])
    OUT.joinpath('Calques').mkdir(exist_ok=True)
    rug.save(OUT / 'Calques/Tapis-PMU-Seuil.png', optimize=True)
    light.save(OUT / 'Calques/Halo-G01P02A-Seuil.png', optimize=True)
    ref_detail = ref.crop(REFERENCE_DETAIL)
    ref_detail.save(OUT / 'Reference/Detail-G01P02A.png', optimize=True)
    data = dict(id=ID, phases=phases, reference=pack(ref_detail),
                detail=dict(x=cx - 44, y=bottom - 48, w=88, h=56))
    report = dict(salle=ID, sortie=dict(id='SortieGuilde', rect=[x, gy, w, h], bottom=bottom),
                  seuil_visible=dict(zone=area, largeur=width, premiere_ligne_derniere_planche=sill,
                                    dernier_pixel_y=bottom-1),
                  reference=dict(carte='G01P02A', url=ORIGINAL, sha256=REF_HASH,
                                 cadrage_halo=REFERENCE_LIGHT, pixels_par_classe=counts),
                  tapis=dict(atlas=item['sheet'], motif='œuf ailé de la variante Halcyon rubis',
                             rect=[rx, ry, *rug.size], lisiere_bas_y=ry + depth - 1),
                  halo=dict(rect=[left, ly, *light.size], gains=PHASE_LIGHT, animation=False,
                            ancrage_bord_clair_y=sill,
                            pixels_au_sol=int((np.asarray(light)[..., 3] > 0).sum())),
                  hors_plancher=0, entree_modifiee_dans_le_jeu=False,
                  couches_atelier_ajoutees=0)
    return data, report


def write_report(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    _, d, _ = read_page()
    _, report = build(d)
    write_report('Index-seuil.json', report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
