#!/usr/bin/env python3
"""Vérifie l'emote de repas « eating » (calquée sur Halcyon) et l'effectif de la Guilde."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
EMOTE_JSON = ROOT / 'game/Data/Emote/eating.json'
EMOTE_INDEX = ROOT / 'game/Data/Emote/index.idx'
EMOTE_DIR = ROOT / 'game/Content/Particle/Emote_Eating.dir'
SCRIPT = ROOT / 'game/Data/Script/destiny/guilde_effectif.lua'

# Les 9 emotes d'origine du PMDO, qui doivent rester visibles une fois
# l'index du mod composé par-dessus celui de base.
BASE_EMOTES = ['angry', 'exclaim', 'glowing', 'happy', 'notice', 'question',
               'shock', 'sweatdrop', 'sweating']


def infos_dir(chemin: Path) -> tuple[int, int, int, int]:
    """(largeur, hauteur, directions, images) d'un DirSheet de particule."""
    octets = chemin.read_bytes()
    assert len(octets) > 12, chemin
    (taille_png,) = struct.unpack('<q', octets[:8])
    assert octets[8:16] == b'\x89PNG\r\n\x1a\n', f'PNG attendu dans {chemin.name}'
    offset = 8 + taille_png
    largeur, hauteur, dirs, frames = struct.unpack('<iiii', octets[offset:offset + 16])
    return largeur, hauteur, dirs, frames


def verifier_donnee() -> None:
    donnee = json.loads(EMOTE_JSON.read_text(encoding='utf-8-sig'))
    assert donnee['Version'], 'Version obligatoire'
    obj = donnee['Object']
    assert obj['$type'] == 'RogueEssence.Data.EmoteData, RogueEssence', obj['$type']
    assert obj['Name']['DefaultText'] == 'Eating'
    assert obj['LocHeight'] == 10, 'hauteur calquée sur Halcyon (10)'
    anim = obj['Anim']
    assert anim['AnimIndex'] == 'Emote_Eating'
    assert anim['FrameTime'] == 3, 'cadence Halcyon'
    assert anim['StartFrame'] == -1 and anim['EndFrame'] == -1, 'toute l\'animation'
    assert anim['AnimDir'] == 0, 'vers le bas'
    assert anim['Alpha'] == 255 and anim['AnimFlip'] == 0

    index = json.loads(EMOTE_INDEX.read_text(encoding='utf-8-sig'))
    cles = [k for k in index['Object'] if not k.startswith('$')]
    assert cles == ['eating'], cles
    entree = index['Object']['eating']
    assert entree['Released'] is True
    assert entree['Name']['DefaultText'] == 'Eating'
    assert entree['SortOrder'] == 9, 'après les neuf emotes de base'

    base = json.loads((ROOT / 'base/Data/Emote/index.idx').read_text(encoding='utf-8-sig'))
    base_cles = sorted(k for k in base['Object'] if not k.startswith('$'))
    assert base_cles == BASE_EMOTES, base_cles
    # L'index du mod ne doit jamais masquer une émote de base : l'unicité de la
    # clé ajoutée suffit, le moteur compose clé par clé.
    assert 'eating' not in base_cles, 'eating ne doit pas déjà exister dans base'


def verifier_asset() -> None:
    assert EMOTE_DIR.exists(), 'Emote_Eating.dir doit accompagner la donnée'
    largeur, hauteur, dirs, frames = infos_dir(EMOTE_DIR)
    assert (largeur, hauteur) == (32, 32), (largeur, hauteur)
    assert dirs == 0, 'planche unique, sans directions'
    assert frames == 6, frames


def verifier_script() -> None:
    source = SCRIPT.read_text(encoding='utf-8')
    for attendu in ('EMOTE_REPAS', 'MEMBRES', 'ORDRE', 'TEAM_STAR',
                    'Manger', 'Repas', 'FinRepas', 'Poser', 'PoseDeService'):
        assert attendu in source, f'{attendu} manquant dans guilde_effectif.lua'
    assert "EMOTE_REPAS = 'eating'" in source
    # La pose de Mélofée reprend le mécanisme d'Audino dans Halcyon.
    assert 'PoseGroundAction' in source, 'pose via PoseGroundAction'
    # Le chargement effectif du module (test Lua) garantit qu'aucun identifiant
    # accentué ne casse le parseur ; les libellés français restent dans les
    # chaînes, jamais dans les noms de variables.
    assert 'Maîtresse de guilde' in source, 'libellés français conservés'
    run(Path(__file__).with_suffix('.lua'), ROOT)


def verifier_refectoire() -> None:
    source = (ROOT / 'game/Data/Script/destiny/ground/guilde_destiny_refectoire/init.lua'
              ).read_text(encoding='utf-8')
    assert "require 'destiny.guilde_effectif'" in source
    assert source.count('guilde_effectif.RepasImmediat') == 3, 'Init, Enter et GameLoad'


def main() -> None:
    verifier_donnee()
    verifier_asset()
    verifier_script()
    verifier_refectoire()
    print('test_guilde_effectif : donnée, asset, script et comportement OK')


if __name__ == '__main__':
    main()
