#!/usr/bin/env python3
"""Crée les émotes propres à la Guilde de Réverie Town.

Deux émotes sont dessinées ici, image par image, au format du moteur
(`.dir` = Int64 taille + PNG + Int32 largeur, hauteur, directions, images) :

  Emote_Reveil            cloche de réveil qui sonne      (8 images, FrameTime 4)
  Emote_Pose_Infirmiere   calot d'infirmière sur la tête  (4 images, FrameTime 12)

`Emote_Pose_Infirmiere` est la « pose spéciale » de Mélofée, à la manière
d'Audino dans Halcyon : une émote dont la `LocHeight` est réglée bas pour que le
calot se pose sur la tête du personnage au lieu de flotter au-dessus. Le corps,
lui, prend la pose de service (`PoseGroundAction`), exactement comme Halcyon.

Les données (`game/Data/Emote/*.json`) et l'index sont réécrits dans la foulée,
toujours en conservant l'émote `eating` et les neuf émotes de base.

    python tools/creer_emotes_guilde.py            # écrit dans le dépôt
    python tools/creer_emotes_guilde.py --apercu   # + planche de contrôle PNG
"""
from __future__ import annotations

import argparse
import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parents[1]
PARTICULE = RACINE / 'game/Content/Particle'
DONNEES = RACINE / 'game/Data/Emote'
VERSION = '0.8.12.0'

# Palette commune (lisible sur les fonds sombres du jeu).
OR = (240, 196, 112, 255)
OR_CLAIR = (255, 233, 168, 255)
OR_OMBRE = (184, 134, 47, 255)
CONTOUR = (58, 42, 20, 255)
BLANC = (244, 248, 252, 255)
BLANC_OMBRE = (186, 202, 216, 255)
BLEU_CONTOUR = (92, 108, 128, 255)
ROUGE = (214, 64, 64, 255)
ECLAT = (200, 238, 255, 255)
ECLAT2 = (255, 255, 255, 255)


def px(d: ImageDraw.ImageDraw, x: int, y: int, couleur) -> None:
    d.point((x, y), fill=couleur)


def croix(d: ImageDraw.ImageDraw, x: int, y: int, couleur, taille: int = 1) -> None:
    """Petit éclat en croix, sans déborder de la cellule 32x32."""
    for k in range(-taille, taille + 1):
        if 0 <= x + k < 32:
            px(d, x + k, y, couleur)
        if 0 <= y + k < 32:
            px(d, x, y + k, couleur)


# --------------------------------------------------------------------------- #
#  Cloche de réveil                                                           #
# --------------------------------------------------------------------------- #
def image_cloche(sonnerie: int, eclats: tuple[int, int]) -> Image.Image:
    """Une image de la cloche. `sonnerie` 0..3 = amplitude des ondes."""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # anse
    d.rectangle((15, 4, 16, 7), fill=OR_OMBRE)
    d.line((15, 4, 15, 7), fill=CONTOUR)
    d.line((16, 4, 16, 7), fill=CONTOUR)

    # dôme puis jupe évasée : la silhouette d'une cloche, pas d'un cône
    demi_largeurs = {8: 3, 9: 4, 10: 5, 11: 5, 12: 6, 13: 6, 14: 7, 15: 7}
    for y, demi in demi_largeurs.items():
        gauche, droite = 16 - demi, 15 + demi
        d.line((gauche, y, droite, y), fill=OR)
        px(d, gauche, y, CONTOUR)
        px(d, droite, y, CONTOUR)
        px(d, gauche + 1, y, OR_CLAIR)   # reflet à gauche
        px(d, gauche + 2, y, OR_CLAIR)

    # rebord
    d.rectangle((7, 16, 24, 18), fill=OR_CLAIR)
    d.line((7, 16, 24, 16), fill=CONTOUR)
    d.line((7, 18, 24, 18), fill=CONTOUR)
    d.line((7, 16, 7, 18), fill=CONTOUR)
    d.line((24, 16, 24, 18), fill=CONTOUR)
    d.line((9, 17, 22, 17), fill=OR)

    # battant
    d.rectangle((15, 19, 16, 20), fill=OR_OMBRE)
    d.line((15, 21, 16, 21), fill=CONTOUR)

    # ondes sonores : trois traits de chaque côté, de plus en plus loin
    for cote in (-1, 1):
        for i in range(sonnerie):
            x = 16 + cote * (10 + i)
            if 0 <= x < 32:
                for dy in (-3, 0, 3):
                    y = 12 + dy
                    if 0 <= y < 32:
                        px(d, x, y, ECLAT if i < 2 else OR_CLAIR)

    # éclats
    for (x, y) in eclats:
        croix(d, x, y, ECLAT2)
    return img


def images_reveil() -> list[Image.Image]:
    plan = [
        (1, ((4, 8),)),              # la cloche apparaît, une première onde
        (1, ((4, 8), (27, 9))),
        (2, ((3, 9), (28, 8))),
        (3, ((2, 8), (29, 9))),      # apogée de la sonnerie
        (3, ((2, 8), (29, 9))),
        (2, ((3, 9), (28, 8))),
        (1, ((4, 8),)),
        (0, ()),                     # silence avant la reprise
    ]
    return [image_cloche(sonnerie, eclats) for sonnerie, eclats in plan]


# --------------------------------------------------------------------------- #
#  Calot d'infirmière (pose de service de Mélofée)                            #
# --------------------------------------------------------------------------- #
def image_calot(eclats: tuple[int, int], scintille: bool) -> Image.Image:
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # dôme du calot : posé bas dans la cellule pour atterrir sur la tête
    demi_largeurs = {10: 1, 11: 2, 12: 3, 13: 3, 14: 4, 15: 4, 16: 5, 17: 5}
    for y, demi in demi_largeurs.items():
        gauche, droite = 16 - demi, 15 + demi
        d.line((gauche, y, droite, y), fill=BLANC)
        px(d, gauche, y, BLEU_CONTOUR)
        px(d, droite, y, BLEU_CONTOUR)

    # bandeau
    d.rectangle((9, 18, 22, 21), fill=BLANC)
    d.line((9, 18, 22, 18), fill=BLEU_CONTOUR)
    d.line((9, 21, 22, 21), fill=BLEU_CONTOUR)
    d.line((9, 18, 9, 21), fill=BLEU_CONTOUR)
    d.line((22, 18, 22, 21), fill=BLEU_CONTOUR)
    d.line((10, 20, 21, 20), fill=BLANC_OMBRE)

    # croix rouge, bien lisible au centre
    d.rectangle((15, 16, 16, 21), fill=ROUGE)
    d.rectangle((13, 18, 18, 19), fill=ROUGE)
    px(d, 15, 16, (168, 42, 42, 255))
    px(d, 16, 21, (168, 42, 42, 255))

    # éclats
    for (x, y) in eclats:
        croix(d, x, y, ECLAT2 if scintille else ECLAT)
    return img


def images_calot() -> list[Image.Image]:
    plan = [
        ((), False),
        (((6, 13),), True),
        (((6, 13), (25, 14)), True),
        (((25, 14),), False),
    ]
    return [image_calot(eclats, scintille) for eclats, scintille in plan]


# --------------------------------------------------------------------------- #
#  Écriture du .dir + des données                                             #
# --------------------------------------------------------------------------- #
def ecrire_dir(nom: str, images: list[Image.Image]) -> Path:
    largeur, hauteur = images[0].size
    planche = Image.new('RGBA', (largeur * len(images), hauteur), (0, 0, 0, 0))
    for i, image in enumerate(images):
        planche.paste(image, (i * largeur, 0))
    tampon = io.BytesIO()
    planche.save(tampon, format='PNG')
    png = tampon.getvalue()

    chemin = PARTICULE / f'{nom}.dir'
    with chemin.open('wb') as flux:
        flux.write(struct.pack('<q', len(png)))
        flux.write(png)
        flux.write(struct.pack('<iiii', largeur, hauteur, 0, len(images)))
    return chemin


def donnee_emote(nom_affiche: str, nom_fr: str, anim: str, frame_time: int,
                 loc_height: int, commentaire: str) -> dict:
    return {
        'Version': VERSION,
        'Object': {
            '$type': 'RogueEssence.Data.EmoteData, RogueEssence',
            'Name': {'DefaultText': nom_affiche, 'LocalTexts': {'fr': nom_fr}},
            'Comment': commentaire,
            'LocHeight': loc_height,
            'Anim': {
                'AnimIndex': anim, 'FrameTime': frame_time,
                'StartFrame': -1, 'EndFrame': -1, 'AnimDir': 0,
                'Alpha': 255, 'AnimFlip': 0,
            },
        },
    }


def ecrire_donnees(entrees: list[tuple[str, dict]]) -> Path:
    DONNEES.mkdir(parents=True, exist_ok=True)
    for identifiant, donnee in entrees:
        (DONNEES / f'{identifiant}.json').write_text(
            json.dumps(donnee, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Index du mod : il ne porte que les clés ajoutées ; le moteur le compose
    # clé par clé par-dessus l'index de base (9 émotes), rien n'est masqué.
    index = {
        'Version': VERSION,
        'Object': {
            '$type': ('System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],'
                      '[RogueEssence.Data.EntrySummary, RogueEssence]], System.Private.CoreLib'),
        },
    }
    for ordre, (identifiant, donnee) in enumerate(entrees, start=9):
        index['Object'][identifiant] = {
            'Name': donnee['Object']['Name'],
            'Released': True,
            'Comment': donnee['Object']['Comment'],
            'SortOrder': ordre,
        }
    chemin = DONNEES / 'index.idx'
    chemin.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return chemin


def apercu_controle(fichiers: dict[str, list[Image.Image]]) -> Path:
    """Planche de contrôle : chaque image à ×6 sur fond sombre."""
    zoom = 6
    lignes = []
    for nom, images in fichiers.items():
        lignes.append((nom, images))
    largeur_cellule = 32 * zoom + 12
    largeur = 220 + largeur_cellule * max(len(im) for _, im in lignes)
    hauteur = 70 + len(lignes) * (32 * zoom + 46)
    img = Image.new('RGB', (largeur, hauteur), (18, 24, 30))
    d = ImageDraw.Draw(img)
    from PIL import ImageFont
    fonte = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    d.text((20, 20), "Émotes de la Guilde — contrôle des images", font=fonte, fill=(232, 238, 244))
    for ligne, (nom, images) in enumerate(lignes):
        y = 60 + ligne * (32 * zoom + 46)
        d.text((20, y + 40), nom, font=fonte, fill=(126, 217, 176))
        for i, image in enumerate(images):
            x = 220 + i * largeur_cellule
            d.rectangle((x - 4, y - 4, x + 32 * zoom + 4, y + 32 * zoom + 4), fill=(34, 48, 59))
            img.paste(image.resize((32 * zoom, 32 * zoom), Image.NEAREST), (x, y), image.resize((32 * zoom, 32 * zoom), Image.NEAREST))
            d.text((x, y + 32 * zoom + 8), str(i + 1), font=fonte, fill=(143, 166, 184))
    chemin = Path('/tmp/controle_emotes_guilde.png')
    img.save(chemin)
    return chemin


def main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument('--apercu', action='store_true', help='écrit une planche de contrôle PNG')
    arguments = analyseur.parse_args()

    reveil = images_reveil()
    calot = images_calot()

    ecrire_dir('Emote_Reveil', reveil)
    ecrire_dir('Emote_Pose_Infirmiere', calot)

    ecrire_donnees([
        ('eating', json.loads((DONNEES / 'eating.json').read_text(encoding='utf-8'))),
        ('reveil', donnee_emote(
            'Wake Bell', 'Réveil', 'Emote_Reveil', 4, 10,
            "Cloche de réveil de la Guilde, jouée par Mélofée (tournée du matin).")),
        ('pose_infirmiere', donnee_emote(
            'Nurse Cap', "Calot d'infirmière", 'Emote_Pose_Infirmiere', 12, 6,
            "Pose de service de Mélofée : calot posé sur la tête (LocHeight 6), "
            "à la manière de la pose d'Audino dans Halcyon.")),
    ])

    print('game/Content/Particle/Emote_Reveil.dir')
    print('game/Content/Particle/Emote_Pose_Infirmiere.dir')
    print('game/Data/Emote/{eating,reveil,pose_infirmiere}.json + index.idx')
    if arguments.apercu:
        print(apercu_controle({'Emote_Reveil': reveil, 'Emote_Pose_Infirmiere': calot}))


if __name__ == '__main__':
    main()
