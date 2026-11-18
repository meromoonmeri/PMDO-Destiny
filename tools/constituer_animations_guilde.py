#!/usr/bin/env python3
"""Constitue les animations de corps des dix membres de la Guilde.

Même principe que la Team Dazzling (`art/sprites/team_dazzling_pose_v2/`) : on
récupère les animations dessinées par SpriteCollab, on les range par membre dans
`art/sprites/guilde_effectif_v1/<dex>_<Nom>/` (AnimData.xml + trio
`<Anim>-Anim/Shadow/Offsets.png`) et on note ce qui existe, pour pouvoir les
injecter dans les `.chara` avec `tools/ajouter_pose_chara.py`.

Pourquoi ces quatre animations :

    Eat   (FrameType 48)  le corps mâche pendant l'émote `eating`
    Wake  (FrameType 47)  le réveil de la tournée du matin
    Sleep (FrameType  3)  le dormeur avant la cloche
    Pose  (FrameType 50)  la pose de service, base de la pose « façon Audino »

Les FrameType sont lus dans `base/Base/GFXParams.xml` (ordre des <Action>), jamais
codés en dur : c'est la clé que comprend `CharSheet`.

    python tools/constituer_animations_guilde.py            # télécharge et range
    python tools/constituer_animations_guilde.py --hors-ligne   # range depuis le cache
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / 'art/sprites/guilde_effectif_v1'
CACHE = Path(os.environ.get('SPRITECOLLAB_CACHE', Path.home() / '.cache/spritecollab'))
GFX = RACINE / 'base/Base/GFXParams.xml'
URL = 'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite/{}/{}'

# Membre (id du script) : (nom de dossier, numéro national)
MEMBRES = {
    'Gardevoir': ('0282_Gardevoir', '0282'),
    'Canarticho': ('0083_Canarticho', '0083'),
    'Simisage': ('0512_Simisage', '0512'),
    'Melofee': ('0035_Melofee', '0035'),
    'Cizayox': ('0212_Cizayox', '0212'),
    'Noctali': ('0197_Noctali', '0197'),
    'Dimoret': ('0461_Dimoret', '0461'),
    'Draby': ('0371_Draby', '0371'),
    'Pandespiegle': ('0674_Pandespiegle', '0674'),
    'Capumain': ('0190_Capumain', '0190'),
}

ANIMATIONS = ['Eat', 'Wake', 'Sleep', 'Pose']

# Recettes des animations dérivées, quand SpriteCollab ne dessine pas l'animation
# pour l'espèce. Elles partent toutes de la planche de l'espèce elle-même, donc
# le style et l'échelle restent ceux du Pokémon ; c'est une solution d'attente,
# pas un dessin original.
# Membres sans Eat d'origine chez SpriteCollab : on le dessine ici. La bouchée
# est dite par les yeux qui se ferment, seule animation de visage fiable à cette
# échelle — SpriteCollab n'a aucune image à bouche ouverte pour ces espèces
# (Hurt et Charge ne font que décaler le sprite d'un pixel).
EAT_DESSINE = {'Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret',
               'Pandespiegle'}

# Membres dont le Eat reprend *aussi* le mouvement de Chapignon (Breloom, n° 286) :
# alternance d'une pose de face et d'une pose tournée plus étroite. Les sprites
# restent ceux de l'espèce, seul le mouvement est emprunté.
EAT_BRELOOM = {'Simisage', 'Gardevoir', 'Dimoret', 'Cizayox', 'Melofee'}
# Bouches dessinées à la main, relevées sur les planches de SpriteCollab :
# (x, y) du coin haut-gauche de l'ouverture, largeur, hauteur, couleur intérieure.
# L'ouverture reçoit un contour noir d'un pixel : c'est ce contour qui la fait
# lire comme une bouche plutôt que comme une tache.
BOUCHES = {
    'Gardevoir':   {'x': 14, 'y': 12, 'largeur': 3, 'hauteur': 2, 'interieur': (86, 28, 36)},
    'Canarticho':  {'x': 10, 'y': 13, 'largeur': 3, 'hauteur': 2, 'interieur': (86, 28, 36)},
    'Simisage':    {'x': 14, 'y': 18, 'largeur': 4, 'hauteur': 2, 'interieur': (88, 40, 12)},
    'Melofee':     {'x': 14, 'y': 19, 'largeur': 3, 'hauteur': 2, 'interieur': (86, 28, 36)},
    'Cizayox':     {'x': 13, 'y': 29, 'largeur': 4, 'hauteur': 2, 'interieur': (86, 28, 36)},
    'Dimoret':     {'x': 14, 'y': 16, 'largeur': 4, 'hauteur': 2, 'interieur': (86, 28, 36)},
    'Pandespiegle':{'x': 11, 'y': 16, 'largeur': 4, 'hauteur': 2, 'interieur': (86, 28, 36)},
}

BRELOOM_DEX = '0286'
BRELOOM = 'Breloom'

RECETTES = {
    'Eat': "balancement de l'Idle joué à 4 ticks par image (mâchoire rapide) — 2 à 4 images",
    'Eat_breloom': ("mouvement de Chapignon transposé : Idle puis Idle tourné "
                    "(largeur réduite et recentrée comme chez lui), à son rythme"),
    'Eat_dessine': ("bouchée dessinée à la main sur l'Idle de l'espèce : bouche "
                    "ouverte une image sur deux, au rythme 6-8-6-8"),
    'Wake': "Sleep image 1, Sleep image 1 inclinée d'1 px, puis Idle image 1 — 3 images de 6, 6, 10 ticks",
    'Pose': "Idle image 1 tenue — 1 image de 30 ticks",
}
# Ce que chaque animation sert dans le mod, pour le README.
ROLES = {
    'Eat': "corps qui mâche pendant l'émote `eating`",
    'Wake': 'réveil de la tournée du matin (`guilde_reveil`)',
    'Sleep': 'dormeur avant la cloche',
    'Pose': "pose de service (mécanisme de la pose d'Audino)",
}


# --------------------------------------------------------------------------- #
#  Animation dérivée                                                          #
# --------------------------------------------------------------------------- #
def lire(chemin: Path) -> Image.Image:
    return Image.open(chemin).convert('RGBA')


def decouper(planche: Image.Image, largeur: int, hauteur: int) -> list[list[Image.Image]]:
    """Découpe une planche SpriteCollab en rangées de directions puis en images."""
    lignes = planche.height // hauteur
    colonnes = planche.width // largeur
    return [[planche.crop((c * largeur, r * hauteur, (c + 1) * largeur, (r + 1) * hauteur))
             for c in range(colonnes)] for r in range(lignes)]


def glisser(image: Image.Image, dx: int, dy: int) -> Image.Image:
    """Glisse le contenu dans la cellule, sans déborder."""
    sortie = Image.new('RGBA', image.size, (0, 0, 0, 0))
    sortie.paste(image, (dx, dy))
    return sortie


def centrer(image: Image.Image, largeur: int, hauteur: int) -> Image.Image:
    """Centre une image d'une autre taille dans une cellule cible."""
    sortie = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
    sortie.paste(image, ((largeur - image.width) // 2, hauteur - image.height))
    return sortie


def deriver(anim: str, dossier_source: Path, dossier_cible: Path,
            largeur: int, hauteur: int) -> list[int] | None:
    """Fabrique `<anim>-Anim/Shadow/Offsets.png` à partir de l'Idle de l'espèce.

    Renvoie les durées (ticks) des images produites, ou None si la source manque.
    """
    idle_png = dossier_source / 'Idle-Anim.png'
    if not idle_png.exists():
        return None
    idle = decouper(lire(idle_png), largeur, hauteur)
    durees: list[int] = []
    images: list[list[Image.Image]] = []

    if anim == 'Eat':
        # On réutilise le balancement de l'Idle, joué plus vite : la mâchoire
        # bouge sans jamais rogner les pieds (aucun décalage hors cellule).
        for rangee in idle:
            cycle = [image for image in rangee[:3]]
            if len(cycle) == 1:
                cycle = [cycle[0], glisser(cycle[0], 0, 1)]
            images.append(cycle)
        durees = [4] * len(images[0])
    elif anim == 'Pose':
        durees = [30]
        for rangee in idle:
            images.append([rangee[0]])
    elif anim == 'Wake':
        sommeil_png = dossier_source / 'Sleep-Anim.png'
        if not sommeil_png.exists():
            return None
        # La cellule du sommeil est celle d'AnimData.xml (souvent plus petite que
        # l'Idle), et sa planche ne contient pas forcément les huit directions.
        largeur_s, hauteur_s, _ = cellule(dossier_source / 'AnimData.xml', 'Sleep')
        if largeur_s == 0:
            return None
        sommeil = decouper(lire(sommeil_png), largeur_s, hauteur_s)
        durees = [6, 6, 10]
        for rangee in idle:
            images.append(rangee)  # remplacé juste après, longueurs alignées plus bas
        def remplissage(image: Image.Image) -> int:
            return sum(1 for p in image.getdata() if p[3] > 0)

        images = []
        for index, rangee in enumerate(idle):
            rangee_sommeil = sommeil[min(index, len(sommeil) - 1)]
            # Certaines planches de sommeil ont une première image vide : on
            # prend celle qui porte réellement le dessin.
            dessin = max(rangee_sommeil, key=remplissage)
            premiere = centrer(dessin, largeur, hauteur)
            images.append([premiere, glisser(premiere, 0, 1), rangee[0]])
    else:
        return None

    # Assemblage : une rangée par direction, dans l'ordre SpriteCollab.
    nb_images = len(durees)
    planche = Image.new('RGBA', (largeur * nb_images, hauteur * len(images)), (0, 0, 0, 0))
    for r, rangee in enumerate(images):
        for c, image in enumerate(rangee):
            planche.paste(image, (c * largeur, r * hauteur))
    planche.save(dossier_cible / f'{anim}-Anim.png')

    # Marqueurs : ceux de l'Idle conviennent (mêmes cellules, même ancrage).
    for suffixe in ('Shadow', 'Offsets'):
        source = dossier_source / f'Idle-{suffixe}.png'
        if source.exists():
            (dossier_cible / f'{anim}-{suffixe}.png').write_bytes(source.read_bytes())
    return durees


def aligner_rangee(rangee: list[Image.Image], largeur: int, hauteur: int) -> list[Image.Image]:
    """Recale les images d'une rangée sur les pieds et l'axe de la première.

    Les images d'Idle de SpriteCollab flottent : chez Cizayox le bas du sprite
    passe de la ligne 41 à la 32 d'une image à l'autre. Sans recalage, le `Eat`
    sauterait d'un pixel ou deux en boucle ; ici toutes les images partagent le
    même sol et le même axe, seul le mouvement voulu subsiste.
    """
    reference = rangee[0].getbbox()
    if not reference:
        return rangee
    sol, axe = reference[3], (reference[0] + reference[2]) / 2
    alignees = []
    for image in rangee:
        boite = image.getbbox()
        case = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
        if boite:
            centre = (boite[0] + boite[2]) / 2
            case.paste(image, (int(round(axe - centre)), sol - boite[3]))
        alignees.append(case)
    return alignees


def dessiner_bouche(image: Image.Image, bouche: dict) -> Image.Image:
    """Dessine une bouche ouverte à la place indiquée par `BOUCHES`.

    L'ouverture est remplie d'une couleur sombre et cernée de noir : sans ce
    contour, à cette échelle, deux pixels sombres se lisent comme une tache et
    non comme une bouche. Le dessin ne s'applique que là où le sprite est
    opaque — on ne peint jamais dans le vide autour du Pokémon.
    """
    sortie = image.copy()
    x0, y0 = bouche['x'], bouche['y']
    largeur, hauteur = bouche['largeur'], bouche['hauteur']

    def peindre(x: int, y: int, couleur: tuple[int, int, int]) -> None:
        if 0 <= x < sortie.width and 0 <= y < sortie.height:
            if image.getpixel((x, y))[3] > 40:
                sortie.putpixel((x, y), (*couleur, 255))

    for x in range(x0, x0 + largeur):
        for y in range(y0, y0 + hauteur):
            peindre(x, y, bouche['interieur'])
    # contour : un pixel de noir tout autour de l'ouverture
    for x in range(x0 - 1, x0 + largeur + 1):
        peindre(x, y0 - 1, (0, 0, 0))
        peindre(x, y0 + hauteur, (0, 0, 0))
    for y in range(y0 - 1, y0 + hauteur + 1):
        peindre(x0 - 1, y, (0, 0, 0))
        peindre(x0 + largeur, y, (0, 0, 0))
    return sortie


def mouvement_breloom(cache: Path, hors_ligne: bool) -> dict | None:
    """Mesure le `Eat` de Chapignon : géométrie image par image et durées.

    Renvoie {images, durees, largeurs: [ratio par image], decalages: [dx par image]}
    ou None si la source est indisponible. Tout est mesuré sur la planche, rien
    n'est écrit à la main : si SpriteCollab retouche Chapignon, la transposition
    suit.
    """
    dossier = cache / BRELOOM
    dossier.mkdir(parents=True, exist_ok=True)
    # La planche de référence est aussi versionnée dans art/sprites/... : la
    # transposition reste reproductible sans réseau.
    reference = SORTIE / 'references' / '0286_Breloom'
    for fichier in ('AnimData.xml', 'Eat-Anim.png'):
        if telecharger(BRELOOM_DEX, fichier, dossier / fichier, hors_ligne):
            reference.mkdir(parents=True, exist_ok=True)
            (reference / fichier).write_bytes((dossier / fichier).read_bytes())
        elif (reference / fichier).exists():
            (dossier / fichier).write_bytes((reference / fichier).read_bytes())
        else:
            return None
    largeur, hauteur, images = cellule(dossier / 'AnimData.xml', 'Eat')
    if largeur == 0:
        return None
    for noeud in ET.parse(dossier / 'AnimData.xml').iter('Anim'):
        if (noeud.findtext('Name') or '').lower() == 'eat':
            durees = [int(d.text) for d in noeud.findall('Durations/Duration')]
            break
    else:
        return None

    planche = lire(dossier / 'Eat-Anim.png')
    cases = [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)) for i in range(images)]
    boites = [case.getbbox() for case in cases]
    reference = boites[0]
    largeur_ref = reference[2] - reference[0]
    centre_ref = (reference[0] + reference[2]) / 2
    ratios, decalages = [], []
    for boite in boites:
        largeur_case = boite[2] - boite[0]
        ratios.append(round(largeur_case / largeur_ref, 4) if largeur_ref else 1.0)
        decalages.append(round((boite[0] + boite[2]) / 2 - centre_ref))
    return {'images': images, 'durees': durees[:images], 'ratios': ratios, 'decalages': decalages}


def machoire_breloom(rangee_idle: list[Image.Image], largeur: int, hauteur: int,
                     mouvement: dict) -> list[Image.Image]:
    """Applique le mouvement de Chapignon à l'Idle de l'espèce.

    Pour chaque image du cycle : on prend une image d'Idle, puis on lui applique
    la largeur relative et le recentrage mesurés chez Chapignon (pieds au sol,
    aucune coupe : la réduction ne fait que rétrécir horizontalement).
    """
    images: list[Image.Image] = []
    for index in range(mouvement['images']):
        source = rangee_idle[index % len(rangee_idle)]
        ratio = mouvement['ratios'][index]
        decalage = mouvement['decalages'][index]
        largeur_vue = max(1, int(round(source.width * ratio)))
        if ratio < 1.0:
            reduite = source.resize((largeur_vue, hauteur), Image.NEAREST)
        else:
            reduite = source
        boite = source.getbbox()
        axe = (boite[0] + boite[2]) / 2 if boite else largeur / 2
        case = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
        case.paste(reduite, delta := (int(round(axe - largeur_vue / 2 + decalage)), 0))
        images.append(case)
    return images


def ajouter_entrees_animdata(chemin: Path, ajouts: dict[str, tuple[int, list[int]]],
                             largeur: int, hauteur: int) -> None:
    """Ajoute les animations dérivées à AnimData.xml (Index libres, durées données)."""
    arbre = ET.parse(chemin)
    racine = arbre.getroot()
    anims = racine.find('Anims')
    utilises = set()
    for noeud in anims.findall('Anim'):
        index = noeud.findtext('Index')
        if index is not None:
            utilises.add(int(index))
    libre = max(utilises) + 1 if utilises else 0
    existants = {(noeud.findtext('Name') or '').lower() for noeud in anims.findall('Anim')}

    for anim, (nb, durees) in ajouts.items():
        if anim.lower() in existants:
            continue
        noeud = ET.SubElement(anims, 'Anim')
        ET.SubElement(noeud, 'Name').text = anim
        ET.SubElement(noeud, 'Index').text = str(libre)
        libre += 1
        ET.SubElement(noeud, 'FrameWidth').text = str(largeur)
        ET.SubElement(noeud, 'FrameHeight').text = str(hauteur)
        durees_noeud = ET.SubElement(noeud, 'Durations')
        for duree in durees:
            ET.SubElement(durees_noeud, 'Duration').text = str(duree)
    arbre.write(chemin, encoding='utf-8', xml_declaration=True)


def types_animation() -> dict[str, int]:
    """FrameType de chaque animation, dans l'ordre des <Action> de GFXParams.xml."""
    racine = ET.parse(GFX).getroot()
    actions = racine.find('Actions')
    noms = [a.findtext('Name') for a in actions.findall('Action')]
    return {nom: index for index, nom in enumerate(noms) if nom}


def telecharger(dex: str, fichier: str, destination: Path, hors_ligne: bool) -> bool:
    if destination.exists() and destination.stat().st_size > 0:
        return True
    if hors_ligne:
        return False
    try:
        with urllib.request.urlopen(URL.format(dex, fichier), timeout=30) as reponse:
            destination.write_bytes(reponse.read())
        return True
    except Exception:
        return False


def cellule(animdata: Path, nom: str) -> tuple[int, int, int]:
    """(largeur, hauteur, images) de l'animation dans AnimData.xml."""
    for noeud in ET.parse(animdata).iter('Anim'):
        if (noeud.findtext('Name') or '').lower() == nom.lower():
            return (int(noeud.findtext('FrameWidth')), int(noeud.findtext('FrameHeight')),
                    len(noeud.findall('Durations/Duration')))
    return (0, 0, 0)


def main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument('--hors-ligne', action='store_true',
                           help='ne pas télécharger, ranger seulement ce qui est en cache')
    arguments = analyseur.parse_args()

    types = types_animation()
    SORTIE.mkdir(parents=True, exist_ok=True)
    manifeste = {'animations': ANIMATIONS, 'frameTypes': {a: types.get(a) for a in ANIMATIONS},
                 'membres': {}}

    for membre, (dossier, dex) in MEMBRES.items():
        cache = CACHE / membre
        cache.mkdir(parents=True, exist_ok=True)
        cible = SORTIE / dossier
        # Reconstruction complète : sans cela, une animation dérivée d'un passage
        # précédent serait prise pour une animation SpriteCollab au suivant.
        if cible.exists():
            shutil.rmtree(cible)
        cible.mkdir(parents=True, exist_ok=True)
        source_animdata = cache / 'AnimData.xml'
        if telecharger(dex, 'AnimData.xml', source_animdata, arguments.hors_ligne):
            (cible / 'AnimData.xml').write_bytes(source_animdata.read_bytes())
        for source in ('Idle-Anim.png', 'Idle-Shadow.png', 'Idle-Offsets.png',
                       'Sleep-Anim.png', 'Sleep-Shadow.png', 'Sleep-Offsets.png'):
            telecharger(dex, source, cache / source, arguments.hors_ligne)

        obtenu = {}
        for anim in ANIMATIONS:
            trio = [f'{anim}-Anim.png', f'{anim}-Shadow.png', f'{anim}-Offsets.png']
            for fichier in trio:
                telecharger(dex, fichier, cache / fichier, arguments.hors_ligne)
                if not (cache / fichier).exists():
                    continue
                (cible / fichier).write_bytes((cache / fichier).read_bytes())
            if (cible / f'{anim}-Anim.png').exists():
                largeur, hauteur, images = cellule(cible / 'AnimData.xml', anim)
                obtenu[anim] = {'cellule': [largeur, hauteur], 'images': images,
                                'frameType': types.get(anim), 'source': 'SpriteCollab'}

        # Ce que SpriteCollab ne dessine pas pour cette espèce est dérivé de son
        # propre Idle : les dix membres disposent ainsi des mêmes animations de
        # corps, au style de leur planche. Solutions d'attente, documentées.
        largeur_idle, hauteur_idle, _ = cellule(cible / 'AnimData.xml', 'Idle')
        derivees = {}
        for anim in ANIMATIONS:
            if anim in obtenu or largeur_idle == 0:
                continue
            # Eat : mouvement de Chapignon transposé pour les membres concernés,
            # mâchoire composée pour les autres, balancement d'Idle si validé.
            if anim == 'Eat' and membre in EAT_DESSINE:
                idle_png = cache / 'Idle-Anim.png'
                if not idle_png.exists():
                    continue
                bouche = BOUCHES.get(membre)
                if bouche is None:
                    continue
                rangees = decouper(lire(idle_png), largeur_idle, hauteur_idle)
                durees = [6, 8, 6, 8]
                planche = Image.new('RGBA', (largeur_idle * len(durees),
                                             hauteur_idle * len(rangees)), (0, 0, 0, 0))
                for index, rangee in enumerate(rangees):
                    # Une seule image d'Idle sert de base : les autres images de
                    # l'Idle changent de pose (bras levés, tête plus haute) et la
                    # bouche, placée en coordonnées de cellule, tomberait à côté.
                    base = rangee[0]
                    for colonne in range(len(durees)):
                        image = base
                        if colonne % 2 == 1:      # une image sur deux : bouche ouverte
                            image = dessiner_bouche(image, bouche)
                        planche.paste(image, (colonne * largeur_idle, index * hauteur_idle))
                planche.save(cible / 'Eat-Anim.png')
                for suffixe in ('Shadow', 'Offsets'):
                    origine = cache / f'Idle-{suffixe}.png'
                    if origine.exists():
                        (cible / f'Eat-{suffixe}.png').write_bytes(origine.read_bytes())
                derivees[anim] = (len(durees), durees)
                obtenu[anim] = {'cellule': [largeur_idle, hauteur_idle],
                                'images': len(durees), 'frameType': types.get(anim),
                                'source': 'dessinee', 'recette': RECETTES['Eat_dessine'],
                                'durees': durees, 'bouche': bouche}
                continue
            durees = deriver(anim, cache, cible, largeur_idle, hauteur_idle)
            if durees is None:
                continue
            derivees[anim] = (len(durees), durees)
            obtenu[anim] = {'cellule': [largeur_idle, hauteur_idle], 'images': len(durees),
                            'frameType': types.get(anim), 'source': 'derivee',
                            'recette': RECETTES.get(anim, '')}
        if derivees:
            ajouter_entrees_animdata(cible / 'AnimData.xml', derivees,
                                     largeur_idle, hauteur_idle)

        manifeste['membres'][membre] = {'dossier': dossier, 'dex': dex, 'animations': obtenu}
        symboles = {'SpriteCollab': '', 'derivee': '*', 'dessinee': '†', 'breloom': '‡'}
        marques = ', '.join(a + symboles.get(obtenu[a]['source'], '') for a in sorted(obtenu))
        print(f'{membre:14s} {dossier:18s} {marques or "—"}')

    (SORTIE / 'MANIFESTE.json').write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # --- README, écrit depuis le manifeste pour rester vrai -----------------
    lignes = [
        '# Animations de corps — effectif de la Guilde (v1)',
        '',
        'Même méthode que la Team Dazzling : animations dessinées par SpriteCollab,',
        'rangées ici par membre, prêtes à être injectées dans les `.chara` par',
        '`tools/ajouter_pose_chara.py`. Chaque dossier contient `AnimData.xml` et le',
        'trio `<Anim>-Anim.png`, `<Anim>-Shadow.png`, `<Anim>-Offsets.png` en huit',
        'directions pour les animations réellement disponibles.',
        '',
        '## Clés d\'animation du moteur',
        '',
        'Les `FrameType` viennent de `base/Base/GFXParams.xml` (ordre des `<Action>`) :',
        '',
        '| Animation | FrameType | Usage dans le mod |',
        '|---|---:|---|',
    ]
    for anim in ANIMATIONS:
        lignes.append(f'| `{anim}` | {types.get(anim)} | {ROLES[anim]} |')
    lignes += [
        '',
        '## Disponibilité par membre',
        '',
        '| Membre | Dossier | Cellule | Eat | Wake | Sleep | Pose |',
        '|---|---|---:|---|---|---|---|',
    ]
    for membre, infos in manifeste['membres'].items():
        animations = infos['animations']
        cellules = {tuple(v['cellule']) for v in animations.values()}
        cellule_txt = ' · '.join(f'{l}×{h}' for l, h in sorted(cellules)) or '—'
        marques = []
        for a in ANIMATIONS:
            if a not in animations:
                marques.append('—')
            elif animations[a]['source'] == 'breloom':
                marques.append('Chapignon')
            elif animations[a]['source'] == 'dessinee':
                marques.append('composée')
            elif animations[a]['source'] == 'derivee':
                marques.append('dérivée')
            else:
                marques.append('oui')
        lignes.append(f"| {membre} | `{infos['dossier']}/` | {cellule_txt} | "
                      + ' | '.join(marques) + ' |')
    lignes += [
        '',
        '## Injection dans un `.chara`',
        '',
        '```sh',
        '# le corps mâche pendant l\'émote eating (FrameType 48)',
        'python3 tools/ajouter_pose_chara.py \\',
        '  --chara game/Content/Chara/371.chara \\',
        '  --sprites art/sprites/guilde_effectif_v1/0371_Draby \\',
        '  --anim Eat --frame-type 48 --out /tmp/371.chara',
        '',
        '# le réveil (FrameType 47)',
        'python3 tools/ajouter_pose_chara.py --chara game/Content/Chara/371.chara \\',
        '  --sprites art/sprites/guilde_effectif_v1/0371_Draby \\',
        '  --anim Wake --frame-type 47 --out /tmp/371.chara',
        '',
        '# la pose de service, façon Audino (FrameType 50)',
        'python3 tools/ajouter_pose_chara.py --chara game/Content/Chara/035.chara \\',
        '  --sprites art/sprites/guilde_effectif_v1/0035_Melofee \\',
        '  --anim Pose --frame-type 50 --out /tmp/035.chara',
        '```',
        '',
        'Le conteneur, ses formes et ses autres animations sont conservés ;',
        '`tools/ajouter_pose_chara.py` recadre au contenu, recentre la boîte,',
        'conserve les marqueurs Offsets/Shadow et remet les lignes SpriteCollab dans',
        "l'ordre Dir8 du moteur.",
        '',
        '> Les `.chara` ne sont pas versionnés dans ce dépôt : l\'injection se fait',
        '> sur les fichiers du jeu (ou du payload) et n\'a donc pas pu être rejouée ici.',
        '> Le code du mod, lui, se rabat proprement quand une animation manque',
        '> (`guilde_effectif.Animer` teste `GetReferencedAnimIndex`).',
        '',
        "Les cases **dérivée** sont des animations fabriquées ici à partir de l'Idle de",
        "l'espèce (SpriteCollab ne les dessine pas pour elle) :",
        '',
    ]
    for anim, recette in RECETTES.items():
        lignes.append(f'- `{anim}` — {recette}')
    lignes.append('')
    lignes.append('Les cases **composée** désignent la mâchoire assemblée à partir de')
    lignes.append('')
    lignes.append('## Le `Eat` dessiné')
    lignes.append('')
    lignes.append('Pour ' + ', '.join(sorted(EAT_DESSINE)) + ', SpriteCollab ne dessine')
    lignes.append("aucune animation de repas. La bouchée est donc faite ici : l'Idle de")
    lignes.append("l'espèce et, une image sur deux, une **flexion du corps d'un pixel** —")
    lignes.append("les genoux plient sur la bouchée. Le visage n'est pas retouché : à")
    lignes.append("cette échelle les yeux et les bouches varient trop d'une espèce à")
    lignes.append("l'autre pour qu'un trait placé sans dessin original tombe juste.")
    lignes.append('Le rythme est celui de Chapignon, 6-8-6-8.')
    lignes.append('')
    lignes.append('Les cinq cases à mouvement emprunté prennent aussi la **largeur relative**')
    lignes.append('et le **recentrage** mesurés sur la planche de Chapignon (Breloom, 286) :')
    lignes.append(f"({', '.join(sorted(EAT_BRELOOM))}). Les sprites restent ceux de l'espèce,")
    lignes.append('seul le mouvement est emprunté.')
    lignes.append('garde en revanche le simple balancement, validé tel quel.')
    lignes += [
        '',
        'Elles se remplacent sans rien casser le jour où un vrai dessin existe :',
        'même nom de fichier, même `AnimData.xml`.',
        '',
        'Régénération : `python tools/constituer_animations_guilde.py`',
        '(cache SpriteCollab dans `~/.cache/spritecollab`, surchargeable par',
        '`SPRITECOLLAB_CACHE`).',
    ]
    (SORTIE / 'README.md').write_text('\n'.join(lignes) + '\n', encoding='utf-8')
    print(f"\n{SORTIE/'README.md'}")
    print(f"{SORTIE/'MANIFESTE.json'}")


if __name__ == '__main__':
    main()
