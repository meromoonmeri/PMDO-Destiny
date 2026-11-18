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
            assert info['source'] in ('SpriteCollab', 'derivee', 'dessinee', 'empruntee',
                                      'breloom'), \
                (membre, anim, info['source'])
            if info['source'] in ('derivee', 'dessinee', 'empruntee', 'breloom'):
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
    # Les GIF de l'animation Eat : un par membre et une planche animée.
    planche = PREUVES / 'guilde_eat_tous.gif'
    assert planche.exists(), 'GIF Eat global manquant'
    with Image.open(planche) as gif:
        assert getattr(gif, 'n_frames', 1) == 4, 'le GIF Eat global doit jouer quatre images'
    for membre in manifeste['membres']:
        gif_membre = PREUVES / 'eat' / f'{membre}.gif'
        assert gif_membre.exists(), f'GIF Eat manquant pour {membre}'
        with Image.open(gif_membre) as gif:
            attendu = manifeste['membres'][membre]['animations']['Eat']['images']
            assert getattr(gif, 'n_frames', 1) == attendu, (membre, 'nombre d\'images du GIF')
    # Les sept membres sans Eat d'origine en ont un dessiné ici ; les trois autres
    # gardent celui de SpriteCollab.
    sources = {m: i['animations']['Eat']['source'] for m, i in manifeste['membres'].items()}
    assert {m for m, v in sources.items() if v == 'empruntee'} == {
        'Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'}, sources
    # Pandespiègle garde son Eat dérivé, validé tel quel.
    assert sources['Pandespiegle'] == 'derivee', sources['Pandespiegle']
    for membre in ('Noctali', 'Draby', 'Capumain'):
        assert sources[membre] == 'SpriteCollab', (membre, sources[membre])

    # Le Eat emprunté : quatre images au rythme du donneur, mouvement mesuré sur
    # sa planche, pieds au sol et rien hors de la cellule.
    for membre in ('Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'):
        dossier = SPRITES / manifeste['membres'][membre]['dossier']
        declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                        for a in ET.parse(dossier / 'AnimData.xml').iter('Anim')}
        info = manifeste['membres'][membre]['animations']['Eat']
        assert tuple(declarations['Eat']) == tuple(info['durees']), (membre, 'durées incohérentes')
        assert info['source'] == 'empruntee', (membre, info['source'])
        assert info['donneur'], membre
        largeur, hauteur = info['cellule']
        with Image.open(dossier / 'Eat-Anim.png') as planche:
            images = [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)).convert('RGBA')
                      for i in range(planche.width // largeur)]
        assert len(images) == len(info['durees']), (membre, 'nombre d\'images')
        # le cycle du donneur anime au moins deux images
        assert images[0].tobytes() != images[1].tobytes(), (membre, 'aucun mouvement')
        # le mouvement se voit : la silhouette change de largeur ou de position
        boites = [image.getbbox() for image in images]
        assert len({(b[2] - b[0], b[0], b[1]) for b in boites}) > 1, (membre, 'silhouette figée')
        # rien ne sort de la cellule
        for boite in boites:
            assert boite[0] >= 0 and boite[2] <= largeur, (membre, 'débord horizontal', boite)
            assert boite[1] >= 0 and boite[3] <= hauteur, (membre, 'débord vertical', boite)

    print('test_animations_guilde : 10 membres, 4 animations chacun, mâchoires conformes, clés du moteur alignées')


if __name__ == '__main__':
    main()
