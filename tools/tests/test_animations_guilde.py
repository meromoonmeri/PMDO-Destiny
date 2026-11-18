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
        'Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'}, sources
    # Pandespiègle garde son Eat dérivé, validé tel quel.
    assert sources['Pandespiegle'] == 'derivee', sources['Pandespiegle']
    for membre in ('Noctali', 'Draby', 'Capumain'):
        assert sources[membre] == 'SpriteCollab', (membre, sources[membre])

    # Le Eat dessiné : quatre images au rythme 6-8-6-8, la bouchée une image sur
    # deux. Images 1 et 3 identiques, 2 et 4 aussi, la bouche noire bien posée,
    # l'aliment présent, et rien qui déborde de la cellule.
    for membre in ('Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'):
        dossier = SPRITES / manifeste['membres'][membre]['dossier']
        declarations = {a.findtext('Name'): [int(d.text) for d in a.findall('Durations/Duration')]
                        for a in ET.parse(dossier / 'AnimData.xml').iter('Anim')}
        assert declarations['Eat'] == [6, 8, 6, 8], (membre, declarations['Eat'])
        info = manifeste['membres'][membre]['animations']['Eat']
        largeur, hauteur = info['cellule']
        fiche = info['bouchee']
        with Image.open(dossier / 'Eat-Anim.png') as planche:
            images = [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)).convert('RGBA')
                      for i in range(planche.width // largeur)]
        assert images[0].tobytes() == images[2].tobytes(), (membre, 'images 1 et 3 différentes')
        assert images[0].tobytes() != images[1].tobytes(), (membre, 'bouchée jamais dessinée')
        # image 2 : on mord (aliment présent) ; image 4 : on avale (bouche vide)
        assert images[1].tobytes() != images[3].tobytes(), (membre, 'morsure et déglutition identiques')
        x0, y0, largeur_bouche = fiche['bouche']
        for image in (images[1], images[3]):
            for dx in range(largeur_bouche):
                assert image.getpixel((x0 + dx, y0))[:3] == (0, 0, 0), \
                    (membre, 'lèvre supérieure absente', (x0 + dx, y0))
            assert tuple(fiche['langue']) in [image.getpixel((x0 + dx, y0 + 1))[:3]
                                              for dx in range(largeur_bouche)], \
                (membre, 'langue absente')
        if fiche['aliment']:
            _, ax, ay = fiche['aliment']
            teintes = {tuple(fiche['fruit']), tuple(max(0, c - 70) for c in fiche['fruit']),
                       (87, 87, 87)}
            assert any(images[1].getpixel((ax + dx, ay + dy))[:3] in teintes
                       for dx in range(3) for dy in range(3)), (membre, 'aliment absent')

    print('test_animations_guilde : 10 membres, 4 animations chacun, mâchoires conformes, clés du moteur alignées')


if __name__ == '__main__':
    main()
