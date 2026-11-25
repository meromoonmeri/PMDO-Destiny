#!/usr/bin/env python3
"""Vérifie les dix vrais Eat dans les conteneurs que le moteur va ouvrir."""
from collections import deque
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fusionner_conteneurs_pmd import fallback, load_container, read_node, walk
from importer_eat_guilde import BASE, FEMELLES, QUETE, ROOT, SOURCES, groupes_eat


def lire_index(dossier):
    data = (dossier / 'index.idx').read_bytes()
    index, off = read_node(data)
    assert off == len(data)
    return index.kids


def verifier_eat():
    manifest = json.loads((SOURCES / 'MANIFESTE.json').read_text(encoding='utf-8'))
    index_base, index_jeu = lire_index(BASE), lire_index(QUETE)
    texte = (ROOT / 'game/Data/Script/destiny/guilde_effectif.lua').read_text(encoding='utf-8')
    acteurs = {nom: genre for nom, genre in re.findall(r"id = '(\w+)',[^\n]+\n[^\n]+genre = '([mf])'", texte)}
    assert set(acteurs) == set(manifest['membres']) and len(acteurs) == 10
    assert {nom for nom, genre in acteurs.items() if genre == 'f'} == FEMELLES
    for nom, info in manifest['membres'].items():
        dex = int(info['dex'])
        dossier = QUETE if dex in index_jeu else BASE
        guide = (index_jeu if dex in index_jeu else index_base)[dex]
        fichier = load_container(dossier / f'{dex}.chara', 'Chara')
        # Le guide ne doit pointer ni vers les anciens offsets ni vers un autre sexe.
        assert {p: n.pos for p, n in walk(guide)} == {p: n.pos for p, n in walk(fichier)}, nom
        feuille = fallback(fichier, 0, 0, 2 if acteurs[nom] == 'f' else 1)
        animations = groupes_eat(feuille, manifest['frameTypes']['Eat'])
        assert animations, f'{nom} : le corps ne joue pas de vrai Eat'
        images = info['animations']['Eat']['images']
        assert all(len(seq) == images and sum(f[2] for f in seq) > 0 for seq in animations), nom
    print('10/10 Eat de corps : forme 0, peau normale, sexe réel, index et pixels contrôlés.')


def verifier_placement():
    data = ROOT / 'game/Data'
    carte = json.loads((data / 'Ground/guilde_destiny_refectoire.rsground').read_text(encoding='utf-8-sig'))['Object']
    script = (data / 'Script/destiny/ground/guilde_destiny_refectoire/init.lua').read_text(encoding='utf-8')
    places = {(int(x), int(y)) for x, y in re.findall(r"\{'\w+', (\d+), (\d+), '(?:Down|Up)'\}", script)}
    assert len(places) == 10
    obstacles = carte['obstacles']
    markers = {m['EntName']: (m['Collider']['X'], m['Collider']['Y']) for m in carte['Entities'][0]['Markers']}

    def terrain(x, y):
        a, b = x // 8, y // 8
        return 0 <= a < len(obstacles) - 1 and 0 <= b < len(obstacles[0]) - 1 and all(
            obstacles[c][d]['Tags'] == 0 for c in (a, a + 1) for d in (b, b + 1))

    assert all(terrain(*place) for place in places)
    depart = markers['EntreeEstMarker']
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for a, b in ((x + 8, y), (x - 8, y), (x, y + 8), (x, y - 8)):
            if (a, b) in vus or not terrain(a, b):
                continue
            if any(abs(a - px) < 16 and abs(b - py) < 16 for px, py in places):
                continue
            vus.add((a, b))
            file.append((a, b))
    assert markers['CentreRefectoireMarker'] in vus and (528, 240) in vus
    for x, y in places:
        assert any(p in vus for p in ((x + 16, y), (x - 16, y), (x, y + 16), (x, y - 16))), (x, y)
    print('Les 10 convives et le centre sont accessibles ; le passage reste libre.')


if __name__ == '__main__':
    verifier_eat()
    verifier_placement()
