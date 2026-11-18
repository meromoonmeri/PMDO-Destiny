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
            assert info['source'] in ('SpriteCollab', 'derivee', 'dessinee'), \
                (membre, anim, info['source'])
            if info['source'] in ('derivee', 'dessinee'):
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
    # Les sept membres sans Eat d'origine en ont un dessiné ici ; les trois autres
    # gardent celui de SpriteCollab.
    sources = {m: i['animations']['Eat']['source'] for m, i in manifeste['membres'].items()}
    assert {m for m, v in sources.items() if v == 'dessinee'} == {
        'Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret',
        'Pandespiegle'}, sources
    for membre in ('Noctali', 'Draby', 'Capumain'):
        assert sources[membre] == 'SpriteCollab', (membre, sources[membre])

    # Le Eat dessiné : quatre images au rythme 6-8-6-8, la bouche ouverte une
    # image sur deux. Les images 1 et 3 sont identiques (bouche fermée), 2 et 4
    # aussi (bouche ouverte), et l'ouverture tombe bien dans le sprite.
    for membre in ('Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret',
                   'Pandespiegle'):
        dossier = SPRITES / manifeste['membres'][membre]['dossier']
        declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                        for a in ET.parse(dossier / 'AnimData.xml').iter('Anim')}
        assert declarations['Eat'] == [6, 8, 6, 8], (membre, declarations['Eat'])
        info = manifeste['membres'][membre]['animations']['Eat']
        largeur, hauteur = info['cellule']
        bouche = info['bouche']
        with Image.open(dossier / 'Eat-Anim.png') as planche:
            images = [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)).convert('RGBA')
                      for i in range(planche.width // largeur)]
        assert images[0].tobytes() == images[2].tobytes(), (membre, 'images 1 et 3 différentes')
        assert images[1].tobytes() == images[3].tobytes(), (membre, 'images 2 et 4 différentes')
        assert images[0].tobytes() != images[1].tobytes(), (membre, 'bouche jamais dessinée')
        changees = [(x, y) for x in range(largeur) for y in range(hauteur)
                    if images[0].getpixel((x, y)) != images[1].getpixel((x, y))]
        assert changees, (membre, 'aucun pixel changé')
        x0, y0 = bouche['x'], bouche['y']
        for x, y in changees:
            assert x0 - 1 <= x <= x0 + bouche['largeur'] and y0 - 1 <= y <= y0 + bouche['hauteur'], \
                (membre, 'bouche hors de son cadre', (x, y))
        # l'ouverture est remplie de sa couleur intérieure
        interieurs = [images[1].getpixel((x, y))[:3]
                      for x in range(x0, x0 + bouche['largeur'])
                      for y in range(y0, y0 + bouche['hauteur'])]
        assert tuple(bouche['interieur']) in interieurs, (membre, 'intérieur de la bouche absent')

    print('test_animations_guilde : 10 membres, 4 animations chacun, mâchoires conformes, clés du moteur alignées')


if __name__ == '__main__':
    main()
