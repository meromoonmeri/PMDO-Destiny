#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests du versionnage de l'installation complète et du paquet de mise à jour.

Vérifie : fichier VERSION (source unique) cohérent avec LISEZ_MOI_WINDOWS.txt
et build_windows.py ; extraction des notes de release depuis MISE_A_JOUR.md ;
sélection et contenu du paquet de mise à jour depuis la version précédente.
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import construire_mise_a_jour as cmj  # noqa: E402
import release_notes as rn  # noqa: E402


def test_version_source_unique():
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    assert re.fullmatch(r'v?\d+\.\d+\.\d+[\w.\-]*', version), version
    liasse = (ROOT / 'docs' / 'LISEZ_MOI_WINDOWS.txt').read_text(encoding='utf-8')
    ligne = [l for l in liasse.splitlines() if l.startswith('Version ')]
    assert len(ligne) == 1, ligne
    assert version in ligne[0], f'{version} absente de {ligne[0]!r}'
    assert ligne[0].endswith('— Windows x64')
    build = (ROOT / 'tools' / 'build_windows.py').read_text(encoding='utf-8')
    assert 'read_version' in build and 'PMDO-Destiny-Windows-x64-' in build
    assert "re.subn(r'^Version .* — Windows x64$'" in build
    # alias non versionné pour l'artefact de l'ancien workflow CI
    assert 'PMDO-Destiny-Windows-x64.zip' in build


def test_notes_de_release():
    journal = (ROOT / 'docs' / 'MISE_A_JOUR.md').read_text(encoding='utf-8')
    entries = rn.entrees(journal)
    assert entries, 'journal vide'
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    # VERSION sans « v » (nom d'asset) ; l'entrée du journal porte le tag git.
    assert entries[0][0] in (version, 'v' + version), f'{entries[0][0]} != {version} (dernière entrée)'
    assert entries[0][1].startswith('## ')
    # extraction CLI : la dernière entrée
    sortie = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'release_notes.py')],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert sortie.startswith('## ')
    assert version in sortie.splitlines()[0]


def test_noms_install():
    assert cmj.nom_install('game/Data/Script/destiny/x.lua') == 'PMDO-Destiny/Data/Script/destiny/x.lua'
    assert cmj.nom_install('game/Content/BG/quiz_star_fire.dir') == 'PMDO-Destiny/Content/BG/quiz_star_fire.dir'
    assert cmj.nom_install('docs/LISEZ_MOI_WINDOWS.txt') == 'PMDO-Destiny/LISEZ_MOI.txt'
    assert cmj.nom_install('tools/tests/x.py') is None


def test_paquet_mise_a_jour():
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    # la base publiée est la 0.3.4 ; les avancées quiz + prologue doivent suivre
    modifs = cmj.diff_depuis('v0.3.4-dev-foret')
    chemins = [c for _, c in modifs]
    assert 'game/Data/Script/destiny/ground/personality_test/quiz_data.lua' in chemins
    assert 'game/Data/Script/destiny/ground/personality_test/revelation_etoile.lua' in chemins
    assert 'game/Content/BG/quiz_star_fire.dir' in chemins
    assert not any(c.startswith('tools/') for c in chemins)
    paquet = cmj.construire('v0.3.4-dev-foret', version)
    try:
        with zipfile.ZipFile(paquet) as zf:
            noms = set(zf.namelist())
            assert 'MANIFEST.txt' in noms
            assert 'PMDO-Destiny/Data/Script/destiny/ground/personality_test/quiz_data.lua' in noms
            assert 'PMDO-Destiny/Content/BG/quiz_star_fire.dir' in noms
            liasse = zf.read('PMDO-Destiny/LISEZ_MOI.txt').decode('utf-8')
            assert f'Version {version} — Windows x64' in liasse
            manifeste = zf.read('MANIFEST.txt').decode('utf-8')
            assert version in manifeste and 'v0.3.4-dev-foret' in manifeste
            # chaque entrée a son SHA-256
            entrees_zip = [n for n in noms if n != 'MANIFEST.txt']
            for n in entrees_zip:
                assert n in manifeste, n
    finally:
        paquet.unlink()


def main():
    test_version_source_unique()
    test_notes_de_release()
    test_noms_install()
    test_paquet_mise_a_jour()
    print('test_release_version : OK')


if __name__ == '__main__':
    main()
