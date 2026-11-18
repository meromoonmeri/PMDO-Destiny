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
            assert info['source'] in ('SpriteCollab', 'derivee', 'dessinee', 'poses',
                                      'calque', 'breloom'), \
                (membre, anim, info['source'])
            if info['source'] in ('derivee', 'dessinee', 'poses', 'calque', 'breloom'):
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
    # Les six membres sans Eat d'origine enchainent des poses de leur propre
    # planche ; les trois autres gardent celui de SpriteCollab.
    sources = {m: i['animations']['Eat']['source'] for m, i in manifeste['membres'].items()}
    POSES_ATTENDUES = {'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'}
    assert {m for m, v in sources.items() if v == 'poses'} == POSES_ATTENDUES, sources
    # Gardevoir a une animation calquee sur Kirlia, pas une suite de poses.
    assert sources['Gardevoir'] == 'calque', sources['Gardevoir']
    # Pandespiegle garde son Eat derive, valide tel quel.
    assert sources['Pandespiegle'] == 'derivee', sources['Pandespiegle']
    for membre in ('Noctali', 'Draby', 'Capumain'):
        assert sources[membre] == 'SpriteCollab', (membre, sources[membre])

    # Le Eat en poses : quatre images decrites par une sequence nommee dans le
    # manifeste (repos, une pose, une autre, ...). Les durees tiennent dans
    # AnimData.xml, la silhouette bouge dans les huit directions, les images de
    # repos sont identiques entre elles et rien ne sort de la cellule.
    for membre in sorted(POSES_ATTENDUES):
        dossier = SPRITES / manifeste['membres'][membre]['dossier']
        declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                        for a in ET.parse(dossier / 'AnimData.xml').iter('Anim')}
        info = manifeste['membres'][membre]['animations']['Eat']
        assert info['source'] == 'poses', (membre, info['source'])
        assert len(info.get('poses', [])) == 2, (membre, 'deux poses attendues', info.get('poses'))
        for nom_pose in info['poses']:
            animation, index = nom_pose.split()
            assert animation and index.isdigit(), nom_pose
        sequence = info.get('sequence') or []
        assert len(sequence) == info['images'] == len(info['durees']), \
            (membre, 'sequence, images et durees doivent avoir la meme longueur', sequence)
        assert sequence.count('repos') >= 1, (membre, 'le repos doit revenir', sequence)
        assert sum(1 for e in sequence if e != 'repos') >= 2, (membre, 'deux gestes attendus', sequence)
        assert tuple(declarations['Eat']) == tuple(info['durees']), (membre, 'durées incohérentes')
        largeur, hauteur = info['cellule']
        with Image.open(dossier / 'Eat-Anim.png') as planche:
            rangees = [[planche.crop((i * largeur, r * hauteur, (i + 1) * largeur,
                                      (r + 1) * hauteur)).convert('RGBA')
                        for i in range(planche.width // largeur)]
                       for r in range(planche.height // hauteur)]
        assert len(rangees[0]) == info['images'] == len(sequence), (membre, 'nombre d\'images')
        for r, rangee in enumerate(rangees):
            repos = [image for image, etape in zip(rangee, sequence) if etape == 'repos']
            assert len({image.tobytes() for image in repos}) == 1, \
                (membre, r, 'les images de repos doivent etre identiques')
            assert len({image.tobytes() for image in rangee}) >= 3, \
                (membre, r, 'poses trop pauvres')
            for image in rangee:
                boite = image.getbbox()
                assert boite is not None, (membre, r, 'image vide')
                assert boite[0] >= 0 and boite[2] <= largeur, (membre, r, 'débord horizontal', boite)
                assert boite[1] >= 0 and boite[3] <= hauteur, (membre, r, 'débord vertical', boite)

    # L'animation sur mesure de Gardevoir : six images de huit ticks, la cadence
    # des membres valides, et un vrai mouvement dans les huit directions.
    dossier = SPRITES / manifeste['membres']['Gardevoir']['dossier']
    declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                    for a in ET.parse(dossier / 'AnimData.xml').iter('Anim')}
    info = manifeste['membres']['Gardevoir']['animations']['Eat']
    assert info['source'] == 'calque', info['source']
    # la cadence est celle de la reference, et c'est aussi celle des membres
    # valides (Noctali, Draby, Capumain jouent 6, 8, 6 et 8 ticks)
    assert info['durees'] == [6, 8, 6, 8], ('cadence de la reference', info['durees'])
    assert info['images'] == 4, info['images']
    assert info.get('reference', '').endswith('Kirlia'), info.get('reference')
    mesure = info.get('mesure') or []
    assert len(mesure) == info['images'], mesure
    assert mesure[0]['pente'] == 0 and mesure[2]['pente'] == 0, mesure
    assert mesure[1]['pente'] > 0 > mesure[3]['pente'], mesure
    assert tuple(declarations['Eat']) == tuple(info['durees']), 'durées incohérentes'
    largeur, hauteur = info['cellule']
    with Image.open(dossier / 'Eat-Anim.png') as planche:
        rangees = [[planche.crop((i * largeur, r * hauteur, (i + 1) * largeur,
                                  (r + 1) * hauteur)).convert('RGBA')
                    for i in range(planche.width // largeur)]
                   for r in range(planche.height // hauteur)]
    for r, rangee in enumerate(rangees):
        distinctes = {image.tobytes() for image in rangee}
        assert len(distinctes) == 3, ('Gardevoir', r, 'trois images distinctes attendues')
        assert rangee[0].tobytes() == rangee[2].tobytes(), (r, 'les images de repos divergent')
        # la tete bouge vraiment : son sommet change de colonne ou de ligne
        sommets = set()
        for image in rangee:
            boite = image.getbbox()
            assert boite is not None, (r, 'image vide')
            sommets.add((boite[1], boite[2]))
        assert len(sommets) > 1, (r, 'la silhouette ne bouge pas')
        for image in rangee:
            boite = image.getbbox()
            assert boite[0] >= 0 and boite[2] <= largeur, (r, 'débord horizontal', boite)
            assert boite[1] >= 0 and boite[3] <= hauteur, (r, 'débord vertical', boite)

    print('test_animations_guilde : 10 membres, 4 animations chacun, mâchoires conformes, clés du moteur alignées')


if __name__ == '__main__':
    main()
