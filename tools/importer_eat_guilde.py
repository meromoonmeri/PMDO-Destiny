#!/usr/bin/env python3
"""Importe Eat dans les formes normales réellement utilisées au réfectoire.

Idempotent : conserve les vrais Eat déjà présents et ne touche à aucun blob
existant des autres formes. L'index du mod doit pointer aux nouveaux offsets,
y compris pour un Pokémon dont la planche de base n'avait pas d'override.
"""
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from ajouter_pose_chara import add_animation, parse_blob
from fusionner_conteneurs_pmd import ensure, fallback, load_container, read_node, write_container, write_node

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'art/sprites/guilde_effectif_v1'
BASE = ROOT / 'base/Content/Chara'
QUETE = ROOT / 'game/Content/Chara'
FEMELLES = {'Gardevoir', 'Melofee', 'Dimoret', 'Capumain'}


def groupes_eat(blob, action):
    """Renvoie uniquement les séquences d'un Eat de corps, jamais un alias."""
    data = parse_blob(blob)
    piste = data['groups'].get(action)
    if not piste or piste['copy'] >= 0 or len(piste['seqs']) not in (1, 8):
        return None
    for seq in piste['seqs']:
        dessins = set()
        for x, y, duree, flip, ox, oy, *_ in seq:
            tw, th = data['tw'], data['th']
            cell = data['image'].crop((x * tw, y * th, (x + 1) * tw, (y + 1) * th))
            if duree <= 0 or not cell.getbbox():
                return None
            dessins.add((cell.tobytes(), flip, ox, oy))
        if len(dessins) < 2:
            return None
    return piste['seqs']


def main():
    manifeste = json.loads((SOURCES / 'MANIFESTE.json').read_text(encoding='utf-8'))
    noms = [a.findtext('Name') for a in ET.parse(ROOT / 'base/Base/GFXParams.xml').findall('./Actions/Action')]
    action = noms.index('Eat')
    assert manifeste['frameTypes']['Eat'] == action
    index_path = QUETE / 'index.idx'
    brut = index_path.read_bytes()
    index, fin = read_node(brut)
    assert fin == len(brut), index_path
    imports = []
    for membre, spec in manifeste['membres'].items():
        dex = int(spec['dex'])
        genre = 2 if membre in FEMELLES else 1
        dest = QUETE / f'{dex}.chara'
        source = dest if dest.exists() else BASE / dest.name
        conteneur = load_container(source, 'Chara')
        feuille = fallback(conteneur, 0, 0, genre)
        seqs = groupes_eat(feuille, action)
        if seqs is None:
            feuille, _ = add_animation(feuille, SOURCES / spec['dossier'], 'Eat', action, reindex=True)
            seqs = groupes_eat(feuille, action)
            assert seqs, f'{membre} doit réellement bouger dans chaque direction'
            ensure(conteneur, (0, 0, genre)).payload = feuille
            imports.append((dex, dest, conteneur))
            decision = 'importé'
        else:
            decision = 'conservé'
        print(membre, decision, f'[{dex}/0/0/{genre}]',
              f'{len(seqs)} direction(s) · {len(seqs[0])} images · {sum(f[2] for f in seqs[0])} ticks')
    # Valider les dix feuilles avant d’écrire le moindre conteneur.
    if not imports:
        return
    for dex, dest, conteneur in imports:
        write_container(dest, conteneur)
        index.kids[dex] = conteneur
    out = io.BytesIO()
    write_node(index, out)
    index_path.write_bytes(out.getvalue())


if __name__ == '__main__':
    main()
