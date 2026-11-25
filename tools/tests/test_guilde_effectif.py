#!/usr/bin/env python3
"""Vérifie les émotes de la Guilde (repas, réveil, calot) et l'effectif."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
EMOTES_DIR = ROOT / 'game/Data/Emote'
EMOTE_INDEX = EMOTES_DIR / 'index.idx'
PARTICULES = ROOT / 'game/Content/Particle'
SCRIPT = ROOT / 'game/Data/Script/destiny/guilde_effectif.lua'
REVEIL = ROOT / 'game/Data/Script/destiny/guilde_reveil.lua'

# Les 9 emotes d'origine du PMDO : elles doivent rester visibles une fois
# l'index du mod composé par-dessus celui de base (le moteur compose clé par clé).
BASE_EMOTES = ['angry', 'exclaim', 'glowing', 'happy', 'notice', 'question',
               'shock', 'sweatdrop', 'sweating']

# clé -> (fichier .dir, images, FrameTime, LocHeight)
ATTENDU = {
    'eating': ('Emote_Eating', 6, 3, 10),
    'reveil': ('Emote_Reveil', 8, 4, 10),
    'pose_infirmiere': ('Emote_Pose_Infirmiere', 4, 12, 6),
}


def entete_dir(chemin: Path) -> tuple[int, int, int, int]:
    """(largeur, hauteur, directions, images) d'un DirSheet de particule."""
    octets = chemin.read_bytes()
    assert len(octets) > 16, chemin
    (taille_png,) = struct.unpack('<q', octets[:8])
    assert octets[8:16] == b'\x89PNG\r\n\x1a\n', f'PNG attendu dans {chemin.name}'
    largeur, hauteur, dirs, frames = struct.unpack('<iiii', octets[8 + taille_png:8 + taille_png + 16])
    return largeur, hauteur, dirs, frames


def verifier_donnees() -> None:
    index = json.loads(EMOTE_INDEX.read_text(encoding='utf-8-sig'))
    cles = [k for k in index['Object'] if not k.startswith('$')]
    assert cles == list(ATTENDU), f'index du mod : {cles}'
    assert index['Object']['$type'].startswith('System.Collections.Generic.Dictionary'), 'type de l\'index'

    for ordre, (cle, (anim, images, frame_time, loc_height)) in enumerate(ATTENDU.items(), start=9):
        donnee = json.loads((EMOTES_DIR / f'{cle}.json').read_text(encoding='utf-8-sig'))
        assert donnee['Version'], cle
        obj = donnee['Object']
        assert obj['$type'] == 'RogueEssence.Data.EmoteData, RogueEssence', cle
        assert obj['LocHeight'] == loc_height, (cle, obj['LocHeight'])
        assert obj['Name']['LocalTexts'].get('fr'), f'nom français manquant : {cle}'
        anim_data = obj['Anim']
        assert anim_data['AnimIndex'] == anim, (cle, anim_data['AnimIndex'])
        assert anim_data['FrameTime'] == frame_time, (cle, anim_data['FrameTime'])
        assert anim_data['StartFrame'] == -1 and anim_data['EndFrame'] == -1, cle
        assert anim_data['AnimDir'] == 0 and anim_data['Alpha'] == 255 and anim_data['AnimFlip'] == 0, cle

        entree = index['Object'][cle]
        assert entree['Released'] is True, cle
        assert entree['SortOrder'] == ordre, (cle, entree['SortOrder'])
        assert entree['Name'] == obj['Name'], cle

    base = json.loads((ROOT / 'base/Data/Emote/index.idx').read_text(encoding='utf-8-sig'))
    base_cles = sorted(k for k in base['Object'] if not k.startswith('$'))
    assert base_cles == BASE_EMOTES, base_cles
    assert not set(ATTENDU) & set(base_cles), 'aucune clé du mod ne doit écraser une émote de base'


def verifier_assets() -> None:
    for cle, (anim, images, _frame_time, _loc_height) in ATTENDU.items():
        chemin = PARTICULES / f'{anim}.dir'
        assert chemin.exists(), f'{anim}.dir manquant pour {cle}'
        largeur, hauteur, dirs, frames = entete_dir(chemin)
        assert (largeur, hauteur) == (32, 32), (anim, largeur, hauteur)
        assert dirs == 0, f'{anim} doit rester sans directions'
        assert frames == images, (anim, frames, images)


def verifier_scripts() -> None:
    source = SCRIPT.read_text(encoding='utf-8')
    for attendu in ('EMOTE_REPAS', 'EMOTE_POSE', 'EMOTE_REVEIL', 'MEMBRES', 'ORDRE', 'TEAM_STAR',
                    'Manger', 'Repas', 'RepasImmediat', 'FinRepas', 'Animer', 'Poser',
                    'Deposer', 'PoseDeService'):
        assert attendu in source, f'{attendu} manquant dans guilde_effectif.lua'
    assert "EMOTE_POSE = 'pose_infirmiere'" in source
    assert "EMOTE_REVEIL = 'reveil'" in source
    # La pose reprend le mécanisme de la pose d'Audino dans Halcyon.
    assert 'PoseGroundAction' in source, 'pose via PoseGroundAction'
    assert 'Maîtresse de guilde' in source, 'libellés français conservés'

    reveil = REVEIL.read_text(encoding='utf-8')
    for attendu in ('Reveiller', 'Tournee', 'SONNERIES', 'EMOTE_REVEIL', "'Sleep'", "'Wake'"):
        assert attendu in reveil, f'{attendu} manquant dans guilde_reveil.lua'
    # Une seule émote à la fois : le calot ne revient qu'après la cloche.
    assert reveil.index('EMOTE_REVEIL') < reveil.rindex('Poser(infirmiere, true)'), \
        'le calot de service doit être reposé après la cloche'

    run(Path(__file__).with_suffix('.lua'), ROOT)
    run(ROOT / 'tools/tests/test_guilde_reveil.lua', ROOT)


def verifier_refectoire() -> None:
    source = (ROOT / 'game/Data/Script/destiny/ground/guilde_destiny_refectoire/init.lua'
              ).read_text(encoding='utf-8')
    assert "require 'destiny.guilde_effectif'" in source
    assert 'InstallerConvive' in source and 'RepasImmediat' in source
    assert source.count('  repas_en_cours()') == 2, 'Enter et GameLoad'
    assert "'_Action'" in source and 'membre.role' in source, 'rôles présentés en jeu'


def main() -> None:
    verifier_donnees()
    verifier_assets()
    verifier_scripts()
    verifier_refectoire()
    print('test_guilde_effectif : émotes, assets, scripts et comportement OK')


if __name__ == '__main__':
    main()
