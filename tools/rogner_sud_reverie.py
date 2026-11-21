#!/usr/bin/env python3
"""Recadre les 10 cartes après la maison ronde (grille 8 px, même origine).

Usage : python tools/rogner_sud_reverie.py ANCIEN_PAYLOAD NOUVEAU_PAYLOAD
Ne remplace ni la source ni un fichier existant. Le SHA du lot d'origine
borne chaque entrée : ce n'est pas un outil de rognage générique.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

from polish_reverie_raccords import MAPS, compact, compter_pistes, parts, tracks

RANGS = 372  # Y = 2 976 px ; devant la porte de la maison, on peut encore circuler.
AVANT = 500
PREMIER_SOMMET_FORET = 367
BANQUE_ARBRES = 'Reverie_Geo_09_Decors_sous'


def raccourcir(raw):
    avant, couches, fin = parts(raw)
    if not avant.startswith(b'\xef\xbb\xbf'):
        raise ValueError('Encodage de la carte de départ inattendu')
    a = avant.index(b'"obstacles":') + len(b'"obstacles":')
    b = avant.index(b',"rand":', a)
    cols = json.loads(avant[a:b])
    assert len(cols) == 200 and all(len(c) == AVANT for c in cols)
    for col in cols:
        del col[RANGS:]
        # Une limite physique, même dans les modes où la caméra ne borne pas le héros.
        col[-1]['Tags'] = 1
    entites = json.loads(b'{'+fin[1:-1])['Entities']
    for couche in entites:
        for cle in ('MapChars', 'GroundObjects', 'Spawners', 'Markers'):
            for ent in couche.get(cle, []):
                pos = ent.get('Collider') or ent.get('serializationLoc')
                assert pos is not None and pos['Y'] + pos.get('Height', 16) <= (RANGS - 1)*8, ent['EntName']
    return avant[:a] + compact(cols) + avant[b:], couches, fin


def rogner_calques(raw):
    couches = json.loads(raw)
    assert len(couches) == 11 and couches[4]['Name'] == 'Objects Under'
    retires = 0
    for i, l in enumerate(couches):
        assert len(l['Tiles']) == 200 and all(len(c) == AVANT for c in l['Tiles'])
        for col in l['Tiles']:
            del col[RANGS:]
            if i != 4:
                continue
            # Couronnes du premier rang d'arbres qui débordent dans l'herbe :
            # enlever seulement ces fragments, pas les troncs du rang près de la maison.
            for y in range(PREMIER_SOMMET_FORET, RANGS):
                cell = col[y]
                ts = tracks(cell)
                propre = [t for t in ts if not (len(t['Frames']) == 1 and
                          t['Frames'][0]['Sheet'] == BANQUE_ARBRES and
                          t['Frames'][0]['TexLoc']['Y'] <= 4)]
                if len(propre) != len(ts):
                    retires += len(ts) - len(propre)
                    cell['Layers'] = propre
    assert retires > 0
    return compact(couches), retires, [compter_pistes(l['Tiles']) for l in couches]


def main(source, out):
    assert source.resolve() != out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = [n + '.rsground.gz' for n in MAPS]
    if any((out/n).exists() for n in names):
        raise SystemExit('Destination existante : aucun écrasement.')
    reference = Path(__file__).with_name('reverie_sud_reference.json')
    digests = json.loads(reference.read_text(encoding='utf-8'))['origine']
    metadata = {'rangées': RANGS, 'cartes': {}}
    ancien_visuel = None
    for name, n in zip(MAPS, names):
        raw = gzip.decompress((source/n).read_bytes())
        if hashlib.sha256(raw).hexdigest() != digests[name]:
            raise SystemExit(f'Carte de départ non reconnue : {n}')
        debut, calques, fin = raccourcir(raw)
        del raw
        if ancien_visuel is None:
            nouveau_visuel, retraits, pistes = rogner_calques(calques)
            ancien_visuel = calques
            metadata.update(retraits=retraits, pistes=pistes)
        else:
            assert calques == ancien_visuel, n
        raw = debut + nouveau_visuel + fin
        (out/n).write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
        metadata['cartes'][name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'octets': len(raw)}
        print(name, len(raw), file=sys.stderr)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('out', type=Path)
    args = p.parse_args()
    main(args.source, args.out)
