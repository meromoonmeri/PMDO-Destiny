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
# Membres sans Eat d'origine chez SpriteCollab : la bouchée est dessinée ici
# (bouche ouverte + aliment + expression, voir BOUCHEES). Pandespiègle n'en est
# pas : son Eat a été validé tel quel et garde la recette dérivée.
EAT_DESSINE = {'Gardevoir', 'Canarticho', 'Simisage', 'Melofee', 'Cizayox', 'Dimoret'}
EAT_DERIVE_VALIDE = {'Pandespiegle'}

# Membres dont le Eat reprend *aussi* le mouvement de Chapignon (Breloom, n° 286) :
# alternance d'une pose de face et d'une pose tournée plus étroite. Les sprites
# restent ceux de l'espèce, seul le mouvement est emprunté.
# ---------------------------------------------------------------------------
# Animations empruntées : pour chaque membre sans Eat d'origine, un donneur de
# SpriteCollab dont le Eat est réellement une animation de repas (bouche ou bras
# qui travaillent), pris chez un bipède à deux bras de même carrure. On mesure son
# mouvement image par image (largeur, recentrage, enfoncement) et on l'applique
# aux sprites du membre : les dessins restent ceux de l'espèce, le mouvement est
# celui du donneur, mis à son échelle.
# ---------------------------------------------------------------------------
DONNEURS = {
    'Gardevoir':   ('0448', 'Lucario'),    # grand bipède droit : 16 % de largeur en moins
    'Canarticho':  ('0066', 'Machop'),     # bipède trapu qui penche la tête de 2 px
    'Simisage':    ('0453', 'Cradopaud'),  # bipède nerveux : 22 % de largeur en moins
    'Melofee':     ('0296', 'Makuhita'),   # petit bipède rond, les bras montent
    'Cizayox':     ('0448', 'Lucario'),    # même carrure large, mouvement le plus ample
    'Dimoret':     ('0359', 'Absol'),      # svelte, il se penche en avant pour mordre
}
EAT_BRELOOM: set[str] = set()
BRELOOM_DEX = '0286'
BRELOOM = 'Breloom'

RECETTES = {
    'Eat': "balancement de l'Idle joué à 4 ticks par image (mâchoire rapide) — 2 à 4 images",
    'Eat_breloom': ("mouvement de Chapignon transposé : Idle puis Idle tourné "
                    "(largeur réduite et recentrée comme chez lui), à son rythme"),
    'Eat_emprunte': ("mouvement du Eat d'un donneur de même carrure, mesuré image "
                     "par image (largeur, recentrage, enfoncement) puis appliqué à "
                     "l'Idle de l'espèce à son échelle"),
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


def _poser(image: Image.Image, x: int, y: int, couleur: tuple[int, int, int],
           libre: bool = False) -> None:
    """Pose un pixel. `libre` autorise le dessin hors de la silhouette."""
    if 0 <= x < image.width and 0 <= y < image.height:
        if libre or image.getpixel((x, y))[3] > 40:
            image.putpixel((x, y), (*couleur, 255))


def mouvement_donneur(dossier: Path) -> list[dict] | None:
    """Mesure le `Eat` d'un donneur : géométrie de chaque image.

    Rend, pour chaque image, la largeur relative, le recentrage et l'enfoncement
    du corps par rapport à la première image — c'est le mouvement utile du
    repas, indépendant des couleurs et du dessin du donneur.
    """
    xml = dossier / 'AnimData.xml'
    planche_png = dossier / 'Eat-Anim.png'
    if not (xml.exists() and planche_png.exists()):
        return None
    largeur, hauteur, _ = cellule(xml, 'Eat')
    if largeur == 0:
        return None
    for noeud in ET.parse(xml).iter('Anim'):
        if (noeud.findtext('Name') or '').lower() == 'eat':
            durees = [int(d.text) for d in noeud.findall('Durations/Duration')]
            break
    else:
        return None
    planche = lire(planche_png)
    nombre = min(len(durees), planche.width // largeur)
    boites = []
    for index in range(nombre):
        case = planche.crop((index * largeur, 0, (index + 1) * largeur, hauteur))
        boites.append(case.getbbox())
    if not all(boites):
        return None
    reference = boites[0]
    largeur_ref = reference[2] - reference[0]
    hauteur_ref = reference[3] - reference[1]
    axe_ref = (reference[0] + reference[2]) / 2
    mouvement = []
    for boite in boites:
        mouvement.append({
            'largeur': (boite[2] - boite[0]) / largeur_ref if largeur_ref else 1.0,
            'hauteur': (boite[3] - boite[1]) / hauteur_ref if hauteur_ref else 1.0,
            'centre': (boite[0] + boite[2]) / 2 - axe_ref,
            'haut': boite[1] - reference[1],
        })
    for index, duree in enumerate(durees[:nombre]):
        mouvement[index]['duree'] = duree
    return mouvement


def appliquer_mouvement(rangee: list[Image.Image], mouvement: list[dict],
                        echelle: float, largeur: int, hauteur: int) -> list[Image.Image]:
    """Applique un mouvement de donneur à la rangée d'Idle d'un membre.

    Le corps est recadré sur lui-même, puis étiré de la largeur et de la hauteur
    relatives mesurées chez le donneur, les pieds restant au sol et l'axe de la
    première image conservé. `echelle` rapporte la taille du membre à celle du
    donneur : un donneur plus grand voit son mouvement réduit d'autant.
    """
    base = aligner_rangee(rangee, largeur, hauteur)
    reference = base[0].getbbox()
    if not reference:
        return base
    sol = reference[3]
    axe = (reference[0] + reference[2]) / 2
    images = []
    for index, etape in enumerate(mouvement):
        source = base[index % len(base)]
        boite = source.getbbox()
        if not boite:
            images.append(source)
            continue
        poids = min(1.0, echelle)
        largeur_vue = max(1, int(round((boite[2] - boite[0]) * (1 + (etape['largeur'] - 1) * poids))))
        hauteur_vue = max(1, int(round((boite[3] - boite[1]) * (1 + (etape['hauteur'] - 1) * poids))))
        corps = source.crop(boite).resize((largeur_vue, hauteur_vue), Image.NEAREST)
        dx = int(round(etape['centre'] * poids))
        dy = int(round(etape['haut'] * poids * 0.5))
        case = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
        # pieds au sol, axe de la première image conservé
        case.paste(corps, (int(round(axe - largeur_vue / 2 + dx)), sol - hauteur_vue + dy))
        images.append(case)
    return images


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
            if anim == 'Eat' and membre in EAT_DERIVE_VALIDE:
                durees = deriver(anim, cache, cible, largeur_idle, hauteur_idle)
                if durees is None:
                    continue
                derivees[anim] = (len(durees), durees)
                obtenu[anim] = {'cellule': [largeur_idle, hauteur_idle], 'images': len(durees),
                                'frameType': types.get(anim), 'source': 'derivee',
                                'recette': RECETTES.get('Eat', ''), 'durees': durees}
                continue
            if anim == 'Eat' and membre in EAT_DESSINE:
                don = DONNEURS.get(membre)
                idle_png = cache / 'Idle-Anim.png'
                if don is None or not idle_png.exists():
                    continue
                dex_don, nom_don = don
                dossier_don = CACHE / f'donneur_{nom_don}'
                dossier_don.mkdir(parents=True, exist_ok=True)
                for fichier in ('AnimData.xml', 'Eat-Anim.png'):
                    if not telecharger(dex_don, fichier, dossier_don / fichier,
                                       arguments.hors_ligne):
                        break
                mouvement = mouvement_donneur(dossier_don)
                if mouvement is None:
                    continue
                # échelle : hauteur du membre / hauteur du donneur
                largeur_don, hauteur_don, _ = cellule(dossier_don / 'AnimData.xml', 'Eat')
                echelle = (hauteur_idle / hauteur_don) if hauteur_don else 1.0
                rangees = decouper(lire(idle_png), largeur_idle, hauteur_idle)
                planche = Image.new('RGBA', (largeur_idle * len(mouvement),
                                             hauteur_idle * len(rangees)), (0, 0, 0, 0))
                for index, rangee in enumerate(rangees):
                    for colonne, image in enumerate(
                            appliquer_mouvement(rangee, mouvement, echelle,
                                                largeur_idle, hauteur_idle)):
                        planche.paste(image, (colonne * largeur_idle, index * hauteur_idle))
                planche.save(cible / 'Eat-Anim.png')
                for suffixe in ('Shadow', 'Offsets'):
                    origine = cache / f'Idle-{suffixe}.png'
                    if origine.exists():
                        (cible / f'Eat-{suffixe}.png').write_bytes(origine.read_bytes())
                durees = [etape['duree'] for etape in mouvement]
                derivees[anim] = (len(durees), durees)
                obtenu[anim] = {'cellule': [largeur_idle, hauteur_idle], 'images': len(durees),
                                'frameType': types.get(anim), 'source': 'empruntee',
                                'recette': RECETTES['Eat_emprunte'], 'durees': durees,
                                'donneur': f'{dex_don} {nom_don}', 'echelle': round(echelle, 2)}
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
    lignes.append('## Le `Eat` emprunté')
    lignes.append('')
    lignes.append('Ces membres n\'ont pas de `Eat` chez SpriteCollab : leur animation')
    lignes.append('emprunte le **mouvement** d\'un donneur de même carrure. Tout est mesuré')
    lignes.append('sur la planche du donneur, image par image : largeur relative, hauteur')
    lignes.append('relative, recentrage, enfoncement. Le résultat est appliqué aux sprites')
    lignes.append('de l\'espèce à son échelle, pieds au sol et axe conservé. Aucun dessin')
    lignes.append('du donneur n\'est repris — seulement son mouvement.')
    lignes.append('')
    lignes.append('| Membre | Donneur | Échelle |')
    lignes.append('|---|---|---:|')
    for membre_don, (dex_don, nom_don) in sorted(DONNEURS.items()):
        fiche_don = manifeste['membres'].get(membre_don, {}).get('animations', {}).get('Eat', {})
        lignes.append(f'| {membre_don} | {nom_don} ({dex_don}) | {fiche_don.get("echelle", "?")} |')
    lignes.append('')
    lignes.append('Pandespiègle garde en revanche le simple balancement, validé tel quel.')
    lignes.append('')
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
