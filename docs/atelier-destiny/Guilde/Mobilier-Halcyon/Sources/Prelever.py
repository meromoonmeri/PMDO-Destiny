#!/usr/bin/env python3
"""Redécoupe les objets natifs depuis une révision Halcyon épinglée, sans écrire dans le jeu."""
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from io import BytesIO
import argparse, hashlib, json, struct
from PIL import Image
from scipy import ndimage as ndi
import numpy as np

S = Path(__file__).resolve().parent
O = S.parent
MODELES = S / 'Modeles.json'
SOURCE = S / 'Provenance-brute.json'
LAYERS = {'objects-under': 'Objects Under', 'objects': 'Objects', 'objects-over': 'Objects Over', 'floor-decor': 'Floor Decor'}

def ouvre(cache, rel):
    return (cache / rel).read_bytes()

def lire_carte(cache, nom):
    return json.loads(ouvre(cache, f'Data/Ground/{nom}.rsground').decode('utf-8-sig'))['Object']

@lru_cache(maxsize=64)
def lire_tuiles(cache, nom):
    brut = ouvre(cache, f'Content/Tile/{nom}.tile')
    taille, nombre = struct.unpack_from('<ii', brut, 0)
    assert taille == 8
    images = {}
    for k in range(nombre):
        x, y, off = struct.unpack_from('<iiq', brut, 8 + k * 16)
        longueur, = struct.unpack_from('<q', brut, off)
        arr = np.array(Image.open(BytesIO(brut[off+8:off+8+longueur])).convert('RGBA'))
        assert arr.shape == (taille, taille, 4)
        alpha = arr[..., 3]
        part = (alpha > 0) & (alpha < 255)
        arr[part, :3] = np.minimum(255, np.rint(arr[part, :3].astype(float) * 255 / alpha[part, None])).astype(np.uint8)
        arr[alpha == 0] = 0
        if alpha.any():
            images[(x, y)] = Image.fromarray(arr)
    return images

def refs(carte, rect, rules):
    x0, y0, w, h = rect
    for key, limit in rules:
        for l in carte['Layers']:
            if l['Name'] != LAYERS[key]:
                continue
            for x in range(x0//8, (x0+w+7)//8):
                for y in range(y0//8, (min(y0+h, limit or y0+h)+7)//8):
                    for t in l['Tiles'][x][y].get('Layers', []):
                        if t['Frames'] and t['Frames'][0]['Sheet']:
                            f = t['Frames'][0]
                            yield key, limit, x*8, y*8, f['Sheet'], f['TexLoc']['X'], f['TexLoc']['Y']

def extraire(cache, carte, rect, rules, mode):
    # Le canevas est aligné sur les tuiles pour conserver les bords 1×.
    x0, y0, w, h = rect
    X, Y = max(0,x0-1)//8*8, max(0,y0-1)//8*8
    w0, h0 = x0-X+w+8, y0-Y+h+8
    can = Image.new('RGBA', (w0,h0))
    sheets = set()
    for _, max_y, x, y, sheet, ix, iy in refs(carte, [max(0,x0-1),max(0,y0-1), w+(1 if x0 else 0)+1, h+(1 if y0 else 0)+1], rules):
        tuile = lire_tuiles(cache, sheet).get((ix,iy))
        if tuile is None:
            continue
        sheets.add(f'Content/Tile/{sheet}.tile')
        if max_y and y + 8 > max_y:
            tuile = tuile.crop((0,0,8,max_y-y))
        can.alpha_composite(tuile,(x-X,y-Y))
    a = np.array(can.crop((x0-X,y0-Y,x0-X+w,y0-Y+h)))
    if mode == 'isole':
        opaque = a[...,3]>100
        groups, k = ndi.label(opaque, np.ones((3,3)))
        assert k >= 1
        sizes = np.bincount(groups[opaque]); mask = groups == sizes.argmax()
        mask |= (a[...,3]>0) & (~opaque) & ndi.binary_dilation(mask, structure=np.ones((3,3)))
        a[~mask] = 0
    a[a[...,3]==0] = 0
    assert Image.fromarray(a).getbbox() == (0,0,w,h), (rect, sheets, Image.fromarray(a).getbbox())
    return a, sorted(sheets)

def telecharger(cache, manifest):
    def one(reg):
        dest = cache / reg['chemin']
        def ok(b): return len(b) == reg['taille'] and hashlib.sha256(b).hexdigest() == reg['sha256']
        if dest.is_file() and ok(dest.read_bytes()):
            return
        with urlopen(reg['url'], timeout=20) as conn:
            b = conn.read()
        if not ok(b):
            raise ValueError('Empreinte source modifiée : ' + reg['chemin'])
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(b)
    with ThreadPoolExecutor(max_workers=6) as work:
        list(work.map(one, manifest['fichiers']))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/halcyon-mobilier/sources')
    p.add_argument('--telecharger',action='store_true',help='Récupérer les fichiers Halcyon de la révision épinglée, sans les redistribuer dans le kit')
    args=p.parse_args(); cache=args.cache.resolve()
    if args.telecharger: telecharger(cache, json.loads(SOURCE.read_text()))
    out=O/'Originaux-1x';out.mkdir(exist_ok=True)
    modeles=json.loads(MODELES.read_text())
    cartes={}
    for m in modeles:
        salle=m['salle']
        if salle not in cartes:cartes[salle]=lire_carte(cache,salle)
        a, src=extraire(cache,cartes[salle],m['rect'],m['calques'],m['mode'])
        assert src == m['planches']
        assert hashlib.sha256(a.tobytes()).hexdigest()==m['pixels_sha256'], m['id']
        Image.fromarray(a).save(out/(m['id']+'.png'),optimize=True)
    print(len(modeles),'découpes RGBA natives vérifiées')

if __name__ == '__main__':
    main()
