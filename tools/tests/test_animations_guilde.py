#!/usr/bin/env python3
"""Vérifie les animations de corps des dix membres (art/sprites/guilde_effectif_v1)."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'art/sprites/guilde_effectif_v1'
PREUVES = ROOT / 'art/previews/guilde_effectif_v1'
GFX = ROOT / 'base/Base/GFXParams.xml'
MANIFESTE = SPRITES / 'MANIFESTE.json'
ATTENDUES = ['Eat', 'Wake', 'Sleep', 'Pose']


def types_animation() -> dict[str, int]:
    """FrameType de chaque animation, dans l'ordre des <Action> de GFXParams.xml.

    C'est la clé que lit CharSheet : elle doit rester alignée sur le moteur, donc
    on la recalcule ici plutôt que de la croire sur parole.
    """
    actions = ET.parse(GFX).getroot().find('Actions')
    noms = [a.findtext('Name') for a in actions.findall('Action')]
    return {nom: index for index, nom in enumerate(noms) if nom}


def main() -> None:
    manifeste = json.loads(MANIFESTE.read_text(encoding='utf-8'))
    types = types_animation()

    # Les quatre clés du manifeste doivent correspondre au moteur.
    for anim in ATTENDUES:
        assert manifeste['frameTypes'][anim] == types[anim], (anim, manifeste['frameTypes'][anim], types[anim])
    assert types['Eat'] == 48 and types['Wake'] == 47 and types['Pose'] == 50 and types['Sleep'] == 3, \
        {a: types[a] for a in ATTENDUES}

    assert len(manifeste['membres']) == 10, len(manifeste['membres'])

    for membre, infos in manifeste['membres'].items():
        dossier = SPRITES / infos['dossier']
        assert dossier.is_dir(), dossier
        arbre = ET.parse(dossier / 'AnimData.xml')
        declarations = {a.findtext('Name'): a for a in arbre.iter('Anim')}

        for anim in ATTENDUES:
            assert anim in infos['animations'], f'{membre} : {anim} annoncée manquante'
            info = infos['animations'][anim]
            assert info['source'] in ('SpriteCollab', 'derivee', 'dessinee', 'breloom'), \
                (membre, anim, info['source'])
            if info['source'] in ('derivee', 'dessinee', 'breloom'):
                assert info.get('recette'), f'{membre} : recette non documentée pour {anim}'

            png = dossier / f'{anim}-Anim.png'
            assert png.exists(), png
            for marqueur in ('Shadow', 'Offsets'):
                assert (dossier / f'{anim}-{marqueur}.png').exists(), f'{png.name} sans marqueurs {marqueur}'

            declaration = declarations.get(anim)
            assert declaration is not None, f'{membre} : {anim} absente d’AnimData.xml'
            largeur = int(declaration.findtext('FrameWidth'))
            hauteur = int(declaration.findtext('FrameHeight'))
            durees = [int(d.text) for d in declaration.findall('Durations/Duration')]
            assert [largeur, hauteur] == info['cellule'], (membre, anim, largeur, hauteur, info['cellule'])

            with Image.open(png) as image:
                assert image.width % largeur == 0, (membre, anim, image.width, largeur)
                assert image.height % hauteur == 0, (membre, anim, image.height, hauteur)
                images = image.width // largeur
            assert images == len(durees) == info['images'], (membre, anim, images, len(durees), info['images'])

        indexes = [int(d.findtext('Index')) for d in declarations.values() if d.findtext('Index')]
        assert len(indexes) == len(set(indexes)), f'{membre} : Index SpriteCollab dupliqués'

    assert (PREUVES / 'guilde_repas.gif').exists(), 'aperçu animé manquant'
    with Image.open(PREUVES / 'guilde_repas.gif') as gif:
        assert getattr(gif, 'n_frames', 1) >= 6, 'GIF trop court'
    assert (PREUVES / 'guilde_animations_planche.png').exists(), 'planche de contrôle manquante'
    # Répartition demandée : cinq membres sur le mouvement de Chapignon, un
    # composé (Canarticho), un dérivé validé (Pandespiègle), trois SpriteCollab.
    sources = {m: i['animations']['Eat']['source'] for m, i in manifeste['membres'].items()}
    assert sources['Pandespiegle'] == 'derivee', sources['Pandespiegle']
    assert {m for m, v in sources.items() if v == 'breloom'} == {
        'Simisage', 'Gardevoir', 'Dimoret', 'Cizayox', 'Melofee'}, sources
    assert {m for m, v in sources.items() if v == 'dessinee'} == {'Canarticho'}, sources
    for membre in ('Noctali', 'Draby', 'Capumain'):
        assert sources[membre] == 'SpriteCollab', (membre, sources[membre])

    # Le mouvement de Chapignon garde son rythme 6-8-6-8 sur les cinq membres.
    for membre in ('Simisage', 'Gardevoir', 'Dimoret', 'Cizayox', 'Melofee'):
        declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                        for a in ET.parse(SPRITES / manifeste['membres'][membre]['dossier']
                                          / 'AnimData.xml').iter('Anim')}
        assert declarations['Eat'] == [6, 8, 6, 8], (membre, declarations['Eat'])

    print('test_animations_guilde : 10 membres, 4 animations chacun, mâchoires conformes, clés du moteur alignées')


if __name__ == '__main__':
    main()
