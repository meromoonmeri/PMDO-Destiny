#!/usr/bin/env python3
"""Clean the generated textures, fit the two rising chains and pack an 8 px-aligned atlas."""
import argparse
import base64
import hashlib
import json
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[1]
PROJECT = OUT.parent
PREVIEW = PROJECT / 'Guilde-Destiny-Bourgeons-PMD.html'
MARK = '<script id="donnees" type="application/json">'
ID = 'guilde_destiny_accueil'
SOURCE = 'https://projectpokemon.org/home/gallery/image/77345-g01p01a2png/'
REF_HASH = '5e8f9b94482389a60aeb28033a8d467d4c86fd8341dcd2db443d08aad8f1e62a'
TILESHEET = OUT / 'Tilesheet-Chaines-Escalier.png'
CELL = (48, 56)
VIEW = dict(x=198, y=66, w=116, h=88)
MASTERS = OUT / 'Maitres'


def page():
    head, tail = PREVIEW.read_text(encoding='utf8').split(MARK, 1)
    data, tail = tail.split('</script>', 1)
    return head, json.loads(data), tail


def load(data):
    return Image.open(BytesIO(base64.b64decode(data.rsplit(',', 1)[-1]))).convert('RGBA')


def pack(img):
    b = BytesIO(); img.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')


def save(path, im):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, 'PNG', optimize=True)


def key(path, size, temper=None):
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)
    r, g, b = a.transpose(2, 0, 1)
    fg = ~((r > 99) & (b > 96) & (r - g > 33) & (b - g > 26))
    a[~fg] = 0
    im = Image.fromarray(np.dstack((a.astype(np.uint8), fg.astype(np.uint8) * 255)))
    im = im.crop(im.getbbox()).resize(size, Image.Resampling.BOX)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] >= 106, 255, 0)
    if temper is not None:
        a[..., :3] = np.rint(np.clip(a[..., :3] * temper, 0, 255)).astype(np.uint8)
    a[..., :3] = np.round(a[..., :3].astype(float) / 4).clip(0, 63).astype(np.uint8) * 4
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a)


def prepare(directory):
    save(MASTERS / 'Potelet.png', key(directory / 'Potelet.png', (9, 23), (1, .94, .88)))
    save(MASTERS / 'Chaine-droite.png', key(directory / 'Maillons.png', (40, 6), (.88, .91, .95)))


def stamp(bits, palette):
    return Image.fromarray(np.asarray([[palette.get(k, (0, 0, 0, 0)) for k in row] for row in bits], np.uint8))


def wall_mount(chain):
    # Clip one generated oval and mount it under two rivets on a small slate plate.
    metal = {'a': (48, 38, 36, 255), 'b': (66, 63, 62, 255),
             'c': (99, 97, 90, 255), 'd': (142, 134, 117, 255)}
    plate = stamp(['.aaa..','acbba.','abdbba','abcbba','abbbba','abbbba','abcbba','acabba','.aaaa.'], metal)
    link = chain.crop((0, 0, 8, chain.height)).resize((5, 5), Image.Resampling.NEAREST)
    plate.alpha_composite(link, (1, 2))
    return plate


def rising_chain(im, high, low):
    # Inverse map each sprite pixel to the textured chain's arc, including a small
    # outward sag. Part of each end is hidden under the fixed iron collar.
    a = np.array(im)
    high, low = (np.asarray(x, dtype=float) for x in (high, low))
    t = np.linspace(0, 1, 161)
    path = high + t[:, None] * (low - high) + (np.sin(np.pi * t) ** 1.4)[:, None] * (-1.45, .75)
    tangent = np.gradient(path, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    normals = np.stack((tangent[:, 1], -tangent[:, 0]), axis=1)
    arclength = np.insert(np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1)), 0, 0)
    u = np.rint(arclength * (im.width - 1) / arclength[-1]).astype(int)
    x, y = np.floor(path.min(0) - 4).astype(int)
    r, b = np.ceil(path.max(0) + 5).astype(int)
    pixels = np.zeros((b - y, r - x, 4), np.uint8)
    for yy in range(y, b):
        for xx in range(x, r):
            q = (xx + .5, yy + .5); delta = q - path
            j = np.einsum('ij,ij->i', delta, delta).argmin()
            v = int(np.floor(np.dot(delta[j], normals[j]) + im.height / 2))
            at_end = (j == 0 and np.dot(delta[j], tangent[j]) < -.65) or (j == len(t) - 1 and np.dot(delta[j], tangent[j]) > .65)
            if not at_end and 0 <= v < im.height:
                pixels[yy-y, xx-x] = a[v, u[j]]
    sprite = Image.fromarray(pixels)
    l, t, r, b = sprite.getbbox()
    return sprite.crop((l, t, r, b)), (int(x + l), int(y + t))


def crop_assembled(entries):
    ox = min(x for _, (x,y) in entries); oy = min(y for _, (x,y) in entries)
    mx = max(x + im.width for im,(x,y) in entries); my = max(y + im.height for im,(x,y) in entries)
    layer = Image.new('RGBA', (mx - ox, my - oy))
    for im, (x,y) in entries:
        layer.alpha_composite(im, (x-ox,y-oy))
    return layer, (ox,oy)


def shaded(im, lut):
    a = np.array(im); m = np.asarray(lut, dtype=np.uint8)
    for k in range(3):
        a[..., k] = m[k, a[..., k]]
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a)


def build(d):
    r = next(r for r in d['rooms'] if r['id'] == ID)
    assert (r['w'],r['h']) == (512,384)
    gate = next(g for g in r['gates'] if g['id'] == 'EscalierNord')['rect']
    assert gate == [232,104,48,16] and d['seuil_accueil']['id'] == ID
    post = Image.open(MASTERS / 'Potelet.png').convert('RGBA')
    chain = Image.open(MASTERS / 'Chaine-droite.png').convert('RGBA')
    mount = wall_mount(chain)
    shadow = stamp(['..lllllll..','.lllllllll.','..lllllll..','....lll....'], {'l':(51,24,12,61)})
    # The lower foot is on the landing, the upper end is fixed into the inside
    # face of the existing newel. The centre never crosses the six clear tiles.
    post_xy, mount_xy = (211,123), (225,98)
    high, low = (228.5,102.5), (218.5,133.5)
    incline, inc_xy = rising_chain(chain, high, low)
    left, left_xy = crop_assembled([(shadow,(210,143)), (incline,inc_xy), (post,post_xy), (mount,mount_xy)])
    reflect = lambda im: im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    mirror_point = lambda p: (r['w'] - p[0], p[1])
    mirror_origin = lambda im,xy: (r['w'] - xy[0] - im.width,xy[1])
    right, right_xy = reflect(left), mirror_origin(left,left_xy)
    front = np.array(load(r['front']))[..., 3]
    base = np.array(load(r['base']))
    for im,(x,y) in ((left,left_xy),(right,right_xy)):
        jj,ii = np.nonzero(np.asarray(im)[...,3]); xx=x+ii; yy=y+jj
        assert not ((xx>=232)&(xx<280)).any(), (x,y)
        assert not front[yy, xx].any()
        assert ((base[yy, xx,:3] != base[0,0,:3]).any(axis=1)&(base[yy,xx,3]>0)).all()
        assert ((xx>=VIEW['x'])&(xx<VIEW['x']+VIEW['w'])&(yy>=VIEW['y'])&(yy<VIEW['y']+VIEW['h'])).all()
        assert yy.max()<154
    phase_bits = []
    for p in range(4):
        pal = d['nuits'][r['nuit']] if p==3 else d['lumieres'][r['nuit']][p]
        phase_bits.append([[*xy,pack(shaded(im,pal['lut']))] for im,xy in ((left,left_xy),(right,right_xy))])
    # Top row: loose parts. Bottom row: rises (both sides), then ready-to-place rails.
    entries = [
        ('Potelet-de-pied',post,{'pied':[4,22],'attache':[7,10]}),
        ('Anneau-mural',mount,{'attache':[3.5,4.5]}),
        ('Chaine-de-palier',chain,{'du':[0,3],'au':[40,3]}),
        ('Ombre-de-pied',shadow,{'pied':[5,2]}),
        ('Chaine-montee-G',incline,{'haut':[high[0]-inc_xy[0],high[1]-inc_xy[1]],'bas':[low[0]-inc_xy[0],low[1]-inc_xy[1]]}),
        ('Chaine-montee-D', reflect(incline), {'haut':[inc_xy[0]+incline.width-high[0],high[1]-inc_xy[1]],'bas':[inc_xy[0]+incline.width-low[0],low[1]-inc_xy[1]]}),
        ('Barriere-G',left,{'origine_accueil':list(left_xy),'ancrage_haut':list(high),'ancrage_bas':list(low),'pied':[215,145]}),
        ('Barriere-D',right,{'origine_accueil':list(right_xy),'ancrage_haut':list(mirror_point(high)),'ancrage_bas':list(mirror_point(low)),'pied':[296,145]}),
    ]
    assert len(entries)==8
    atlas = Image.new('RGBA',(4*CELL[0],2*CELL[1])); cells=[]
    for i,(name,im,anchors) in enumerate(entries):
        u,v = i%4*CELL[0],i//4*CELL[1]
        x,y = u+(CELL[0]-im.width)//2,v+(CELL[1]-im.height)//2
        assert im.width<=CELL[0]-4 and im.height<=CELL[1]-4
        atlas.alpha_composite(im,(x,y))
        save(OUT / 'Calques' / f'{name}.png', im)
        cells.append(dict(id=name,case=[u,v,*CELL],sprite=[x,y,*im.size],reperes=anchors))
    for cell,(_,original,_) in zip(cells,entries,strict=True):
        x,y,w,h = cell['sprite']; assert np.array_equal(atlas.crop((x,y,x+w,y+h)),original)
    save(TILESHEET,atlas)
    path = OUT/'Reference/G01P01A2-Entree-fermee.png'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == REF_HASH
    ref = Image.open(path).convert('RGBA').crop((150,121,330,315))
    data = dict(id=ID, vue=VIEW, phases=phase_bits, planche=pack(atlas), reference=pack(ref))
    report = dict(planche=TILESHEET.name, taille=list(atlas.size), grille_px=8, cases_px=list(CELL), sprites=cells,
                  origine=dict(carte='G01P01A2', url=SOURCE, sha256=REF_HASH,
                    observation='Chevalets de bois à attaches sombres devant la porte fermée ; les chaînes inclinées sont une adaptation.'),
                  escalier=dict(salle=ID, acces='EscalierNord', rectangle=gate, largeur_libre=48, sens='entrée nord'),
                  peinture=dict(ambiance='Jour · sprites détourés à 1×', source='Potelet et maillons générés, ajustés au plan'),
                  tapis_halo_sud_inchanges=True, occlusion_du_passage=0, modifications_jeu=False)
    (OUT / 'Index-tilesheet.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data, report


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--ia',type=Path);args=p.parse_args()
    if args.ia: prepare(args.ia)
    _, d, _=page(); layer, report=build(d)
    print(f"PASS · {len(report['sprites'])} sprites · {report['taille']} · EscalierNord libre sur {report['escalier']['largeur_libre']} px.")
