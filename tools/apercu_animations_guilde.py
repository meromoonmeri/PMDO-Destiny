#!/usr/bin/env python3
"""Aperçus animés des animations de corps de la Guilde.

Même esprit que `art/previews/team_dazzling_cliff_scene/` : un GIF qui montre ce
que verra le joueur, étoiles `Lucky_Chant_Star_Yellow` comprises, et une planche
fixe de contrôle.

Sources : `art/sprites/guilde_effectif_v1/` (AnimData.xml + `<Anim>-Anim.png`),
l'émote `eating` du mod et la particule d'étoile du jeu de base.

    python tools/apercu_animations_guilde.py
"""
from __future__ import annotations

import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from xml.etree import ElementTree as ET

RACINE = Path(__file__).resolve().parents[1]
SPRITES = RACINE / 'art/sprites/guilde_effectif_v1'
PREUVES = RACINE / 'art/previews/guilde_effectif_v1'
EMOTE = RACINE / 'game/Content/Particle/Emote_Eating.dir'
GIF = PREUVES / 'guilde_repas.gif'
PLANCHE = PREUVES / 'guilde_animations_planche.png'

ECHELLE = 2
CELLULE = 104
ECART = 10
POLICE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
POLICE_TEXTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def lire_dir(chemin: Path) -> tuple[list[Image.Image], int, int]:
    octets = chemin.read_bytes()
    (taille,) = struct.unpack('<q', octets[:8])
    planche = Image.open(io.BytesIO(octets[8:8 + taille])).convert('RGBA')
    largeur, hauteur, _dirs, images = struct.unpack('<iiii', octets[8 + taille:8 + taille + 16])
    return [planche.crop((i * largeur, 0, (i + 1) * largeur, hauteur)) for i in range(images)], largeur, hauteur


def animation(dossier: Path, nom: str) -> tuple[list[Image.Image], list[int], int, int] | None:
    """Images de la direction « vers le bas » (rangée 0) et leurs durées."""
    png = dossier / f'{nom}-Anim.png'
    xml = dossier / 'AnimData.xml'
    if not png.exists() or not xml.exists():
        return None
    for noeud in ET.parse(xml).iter('Anim'):
        if (noeud.findtext('Name') or '').lower() == nom.lower():
            largeur = int(noeud.findtext('FrameWidth'))
            hauteur = int(noeud.findtext('FrameHeight'))
            durees = [int(d.text) for d in noeud.findall('Durations/Duration')]
            break
    else:
        return None
    planche = Image.open(png).convert('RGBA')
    images = planche.width // largeur
    rangee = planche.crop((0, 0, images * largeur, hauteur))
    return ([rangee.crop((i * largeur, 0, (i + 1) * largeur, hauteur)) for i in range(images)],
            durees[:images] or [6] * images, largeur, hauteur)


def poser(cellule: Image.Image, sprite: Image.Image, emote: Image.Image | None) -> None:
    """Pose le sprite au sol de la cellule et l'émote au-dessus de la tête."""
    sol = cellule.height - 12
    facteur = min((CELLULE - 24) / sprite.width, (CELLULE - 30) / sprite.height)
    vue = sprite.resize((int(sprite.width * facteur), int(sprite.height * facteur)), Image.NEAREST)
    x = (cellule.width - vue.width) // 2
    cellule.paste(vue, (x, sol - vue.height), vue)
    if emote is not None:
        ev = emote.resize((emote.width * ECHELLE, emote.height * ECHELLE), Image.NEAREST)
        cellule.paste(ev, ((cellule.width - ev.width) // 2,
                           sol - vue.height - 6 - ev.height // 2), ev)


def main() -> None:
    PREUVES.mkdir(parents=True, exist_ok=True)
    manifeste = json.loads((SPRITES / 'MANIFESTE.json').read_text(encoding='utf-8'))
    emotes, _l, _h = lire_dir(EMOTE)

    membres = []
    for membre, infos in manifeste['membres'].items():
        dossier = SPRITES / infos['dossier']
        mange = animation(dossier, 'Eat') or animation(dossier, 'Idle')
        pose = animation(dossier, 'Pose') or animation(dossier, 'Idle')
        reveil = animation(dossier, 'Wake')
        membres.append((membre, infos, mange, pose, reveil))

    colonnes, lignes = 5, 2
    largeur = colonnes * (CELLULE + ECART) + ECART
    hauteur = lignes * (CELLULE + 26 + ECART) + ECART + 34
    fond = (16, 22, 28)

    def image(indice: int, pour_gif: bool) -> Image.Image:
        img = Image.new('RGB', (largeur, hauteur), fond)
        d = ImageDraw.Draw(img)
        titre = ImageFont.truetype(POLICE, 13)
        d.text((ECART + 2, 8), 'Guilde de Réverie Town — le repas : animation de corps + émote eating',
               font=titre, fill=(232, 238, 244))
        for index, (membre, infos, mange, pose, reveil) in enumerate(membres):
            rangee, colonne = divmod(index, colonnes)
            x = ECART + colonne * (CELLULE + ECART)
            y = 34 + ECART + rangee * (CELLULE + 26 + ECART)
            cellule = Image.new('RGBA', (CELLULE, CELLULE + 4), (24, 33, 41, 255))
            images, durees, _lw, _lh = mange
            sprites = images * 3                      # trois tours de mâchoire
            sprite = sprites[indice % len(sprites)]
            # images 4 à 6 de l'émote : celles où les miettes se voient
            emote = emotes[3 + (indice // 2) % (len(emotes) - 3)]
            poser(cellule, sprite, emote)
            img.paste(cellule, (x, y))
            d.text((x + 2, y + CELLULE + 6), membre, font=titre, fill=(200, 216, 228))
            source = infos['animations']['Eat']['source']
            libelle = {'derivee': 'Eat dérivée', 'dessinee': 'Eat composée',
                       'breloom': 'Eat Chapignon'}.get(source, 'Eat SpriteCollab')
            d.text((x + 2, y + CELLULE + 19), libelle,
                   font=ImageFont.truetype(POLICE_TEXTE, 10), fill=(140, 160, 176))
        return img

    # GIF : 8 images, 90 ms
    images = [image(i, True) for i in range(8)]
    images[0].save(GIF, save_all=True, append_images=images[1:], duration=90, loop=0, optimize=True)

    # Planche fixe : repas, pose, réveil de chaque membre
    case_l, case_h = CELLULE, CELLULE + 24
    planche = Image.new('RGB', (ECART + 3 * (case_l + ECART) + 190, 40 + len(membres) * (case_h + 6)), fond)
    d = ImageDraw.Draw(planche)
    fonte = ImageFont.truetype(POLICE, 13)
    petite = ImageFont.truetype(POLICE_TEXTE, 11)
    d.text((ECART, 12), "Animations de corps — repas · pose de service · réveil", font=fonte,
           fill=(232, 238, 244))
    for titre, colonne in (('Eat', 0), ('Pose', 1), ('Wake', 2)):
        d.text((190 + ECART + colonne * (case_l + ECART), 12), titre, font=petite, fill=(126, 217, 176))
    for index, (membre, infos, mange, pose, reveil) in enumerate(membres):
        y = 40 + index * (case_h + 6)
        d.text((ECART, y + 26), membre, font=fonte, fill=(232, 238, 244))
        d.text((ECART, y + 44), {'derivee': 'Eat dérivée', 'dessinee': 'Eat composée',
                                 'breloom': 'Eat Chapignon'}.get(
            infos['animations']['Eat']['source'], 'Eat SpriteCollab'), font=petite, fill=(140, 160, 176))
        for colonne, anim in enumerate((mange, pose, reveil)):
            x = 190 + ECART + colonne * (case_l + ECART)
            cellule = Image.new('RGBA', (case_l, case_h), (24, 33, 41, 255))
            if anim is None:
                planche.paste(cellule.convert('RGB'), (x, y))
                continue
            images_anim, _d, _w, _h = anim
            emote = emotes[2] if colonne == 0 else None
            poser(cellule, images_anim[0], emote)
            planche.paste(cellule, (x, y))
    planche.save(PLANCHE)
    print(GIF)
    print(PLANCHE)


if __name__ == '__main__':
    main()
