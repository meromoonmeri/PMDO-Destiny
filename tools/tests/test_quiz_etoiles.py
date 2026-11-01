#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests des sprites pixel-art de l'étoile du quiz (Content/BG/quiz_star_*.dir).

Vérifie :
  * la structure DirSheet de chaque .dir (format engine DirSheet.Save) ;
  * que la régénération via tools/generer_etoile_quiz.py redonne exactement
    les mêmes pixels (le rendu est déterministe) ;
  * la cohérence des couleurs de types avec quiz_data.lua (couleurs_types).
"""
import importlib.util
import io
import re
import struct
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent.parent
BG = ROOT / 'game' / 'Content' / 'BG'
QUIZ_DATA = ROOT / 'game' / 'Data' / 'Script' / 'destiny' / 'ground' / 'personality_test' / 'quiz_data.lua'

LUMIERES = ['quiz_star_lumiere_1', 'quiz_star_lumiere_2', 'quiz_star_lumiere_3']
TYPES = ['normal', 'fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison',
         'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark',
         'steel', 'fairy', 'none']


def charge_dir(path):
    """Décode un .dir → (frames PIL, tile_w, tile_h, rotate, nb_frames)."""
    raw = path.read_bytes()
    (png_len,) = struct.unpack_from('<q', raw, 0)
    assert 8 + png_len + 16 == len(raw), f'taille incohérente : {path}'
    assert raw[8:10] == b'\x89P', f'signature PNG absente : {path}'
    tile_w, tile_h, rotate, nb = struct.unpack_from('<iiii', raw, 8 + png_len)
    feuille = Image.open(io.BytesIO(raw[8:8 + png_len])).convert('RGBA')
    assert feuille.width == tile_w * nb and feuille.height == tile_h, \
        f'grille incohérente : {path}'
    frames = [feuille.crop((tile_w * i, 0, tile_w * (i + 1), tile_h)) for i in range(nb)]
    return frames, tile_w, tile_h, rotate, nb


def test_structure_dirsheet():
    for nom in LUMIERES + [f'quiz_star_{t}' for t in TYPES]:
        path = BG / f'{nom}.dir'
        assert path.is_file(), f'DirSheet manquant : {nom}.dir'
        frames, tile_w, tile_h, rotate, nb = charge_dir(path)
        assert (tile_w, tile_h) == (320, 240), f'{nom} : tuile {tile_w}x{tile_h}'
        assert rotate == 0, f'{nom} : rotate != None'
        assert nb == len(frames)
        # les paliers d'animation sont bouclés sur 4 frames, les étoiles sur 2
        attendu = 4 if nom in LUMIERES else 2
        assert nb == attendu, f'{nom} : {nb} frames != {attendu}'
        # l'étoile a un cœur blanc, le fond reste transparent
        coin = frames[0].getpixel((2, 2))
        assert coin[3] == 0, f'{nom} : fond non transparent {coin}'
        if nom not in LUMIERES:
            centre = frames[0].getpixel((160, 120))
            assert centre == (255, 255, 255, 255), f'{nom} : cœur absent {centre}'


def test_regeneration_deterministe():
    """Le générateur doit redonner les pixels versionnés à l'identique."""
    spec = importlib.util.spec_from_file_location(
        'generer_etoile_quiz', ROOT / 'tools' / 'generer_etoile_quiz.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lots = module.construire_frames()
    assert sorted(lots) == sorted(LUMIERES + [f'quiz_star_{t}' for t in TYPES])
    for nom, frames_attendus in lots.items():
        frames, _, _, _, nb = charge_dir(BG / f'{nom}.dir')
        assert nb == len(frames_attendus), f'{nom} : nombre de frames'
        for i, (attendu, obtenu) in enumerate(zip(frames_attendus, frames)):
            ecart = ImageChops.difference(attendu, obtenu)
            assert ecart.getbbox() is None, f'{nom} frame {i} : pixels différents'
    # et la réécriture complète du dossier temporaire fonctionne
    with tempfile.TemporaryDirectory() as tmp:
        module.main(tmp)
        assert (Path(tmp) / 'quiz_star_fire.dir').is_file()


def test_couleurs_synchro():
    """Les hex de quiz_data.couleurs_types = ceux du générateur."""
    texte = QUIZ_DATA.read_text(encoding='utf-8')
    bloc = texte.split('quiz_data.couleurs_types = {', 1)[1].split('\n}', 1)[0]
    paires = dict(re.findall(r'\["(\w+)"\]\s*=\s*\{\s*hex\s*=\s*"(#\w{6})"', bloc))
    assert set(paires) == set(TYPES), f'types désynchronisés : {sorted(paires)}'
    spec = importlib.util.spec_from_file_location(
        'generer_etoile_quiz', ROOT / 'tools' / 'generer_etoile_quiz.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for type_id, hex_quiz in paires.items():
        assert module.COULEURS_TYPES[type_id].upper() == hex_quiz.upper(), \
            f'{type_id} : {hex_quiz} != {module.COULEURS_TYPES[type_id]}'


def main():
    test_structure_dirsheet()
    test_regeneration_deterministe()
    test_couleurs_synchro()
    print('test_quiz_etoiles : OK')


if __name__ == '__main__':
    main()
