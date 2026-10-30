#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Éditeur de .rsground géant, par blocs de cases, en flux.

Pourquoi ce détour : `json.load` sur 330 Mo dépasse la RAM, et réécrire le JSON
par un parseur complet coûterait plusieurs minutes pour 3,7 M de cases. Or une
carte PMDO est une grille de cases **indépendantes** (un objet JSON par case) :
on peut donc travailler au niveau du TEXTE de chaque case.

Primitives :
- chaque case commence par `{\\r\\n"AutoTileset"` — ancrage fiable, y compris
  pour les cases vides (`"Layers": []`) ;
- les séparateurs d'origine (virgule, jointure de colonne) sont conservés tels
  quels : on ne réécrit que le texte des cases, jamais la ponctuation ;
- une couche non modifiée est recopiée octet pour octet (mmap -> fichier).

Contrôle intégrité : `--verifier` réécrit le fichier sans aucune édition et
compare les empreintes SHA-256. Si les deux diffèrent, l'éditeur est faux.

Opérations (fichier JSON de scénario) :
  {"copier": [[tx0, ty0, tx1, ty1, dx, dy, "h|v|hv|non"], ...],
   "remplir": [[tx0, ty0, tx1, ty1, calque, cellule_json], ...]}

Usage :
  python editer_ground.py <source.rsground> <sortie.rsground> [scenario.json]
  python editer_ground.py <source.rsground> --verifier
"""
from __future__ import annotations

import hashlib
import json
import mmap
import re
import sys
from pathlib import Path

NX, NY = 200, 500
RE_TILES = re.compile(rb'"Tiles"\s*:\s*\[')
DEBUT_CASE = re.compile(rb'\{\r\n"AutoTileset"')
RE_NOM = re.compile(rb'"Name"\s*:\s*"([^"]*)"')


class Calque:
    """Un calque de tuiles : positions des cases et texte de chacune."""

    def __init__(self, mm, index, a, b):
        self.index = index
        self.a = a                      # début du champ "Tiles"
        self.b = b                      # début du "Tiles" suivant
        debuts = [m.start() for m in DEBUT_CASE.finditer(mm, a, b)]
        if len(debuts) != NX * NY:
            raise ValueError(f'calque {index} : {len(debuts)} cases au lieu de {NX * NY}')
        self.debuts = debuts
        # fin de chaque case = dernière accolade fermante avant la case suivante
        # (la ponctuation change au saut de colonne : ", \r\n" puis "\r\n], \r\n[\r\n")
        self.fins = []
        for k in range(len(debuts) - 1):
            fin = mm.rfind(b'}', debuts[k], debuts[k + 1])
            if fin < 0:
                raise ValueError(f'calque {index} : case {k} sans accolade fermante')
            self.fins.append(fin + 1)
        queue = mm.find(b'\r\n]\r\n]', self.fins[-1])
        if queue < 0:
            raise ValueError(f'calque {index} : fin de tableau introuvable')
        self.fins.append(queue + 6)
        self.queue = queue
        self.modifie = False
        self.nouveaux = {}

    def lire(self, mm, tx, ty):
        k = tx * NY + ty
        if k in self.nouveaux:
            return self.nouveaux[k]
        return bytes(mm[self.debuts[k]:self.fins[k]])

    def ecrire(self, tx, ty, texte):
        self.nouveaux[tx * NY + ty] = texte if isinstance(texte, bytes) else texte.encode()
        self.modifie = True

    def texte_complet(self, mm):
        """Réassemblage : on garde la ponctuation d'origine, case par case."""
        morceaux = [bytes(mm[self.a:self.debuts[0]])]
        n = len(self.debuts)
        for k in range(n):
            morceaux.append(self.nouveaux.get(k) or bytes(mm[self.debuts[k]:self.fins[k]]))
            if k < n - 1:
                morceaux.append(bytes(mm[self.fins[k]:self.debuts[k + 1]]))
        morceaux.append(bytes(mm[self.fins[-1]:self.b]))
        return b''.join(morceaux)


def ouvrir(chemin):
    f = open(chemin, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    pos = [m.start() for m in RE_TILES.finditer(mm)]
    calques = []
    for i, a in enumerate(pos):
        b = pos[i + 1] if i + 1 < len(pos) else len(mm)
        calques.append(Calque(mm, i, a, b))
    noms = []
    for c in calques:
        m = RE_NOM.search(bytes(mm[max(0, c.a - 400):c.a]))
        noms.append(m.group(1).decode() if m else f'calque {c.index}')
    return f, mm, calques, noms


RE_OBS = re.compile(rb'"obstacles"\s*:\s*\[')


def lire_obstacles(mm):
    """Renvoie (début, fin, grille) du tableau obstacles — 100 000 petites entrées."""
    m = RE_OBS.search(mm[:400])
    if not m:
        return None
    a = m.end() - 1
    depth, i, ins = 0, a, False
    while i < len(mm):
        c = mm[i]
        if ins:
            if c == 0x5C:
                i += 2
                continue
            if c == 0x22:
                ins = False
        elif c == 0x22:
            ins = True
        elif c == 0x5B:
            depth += 1
        elif c == 0x5D:
            depth -= 1
            if depth == 0:
                return a, i + 1, json.loads(bytes(mm[a:i + 1]))
        i += 1
    return None


def reecrire(chemin_src, chemin_dst, calques, mm, obstacles=None):
    """Réécrit en flux : un remplacement pour les obstacles, un par calque modifié."""
    remplacements = []
    if obstacles is not None:
        a, b, texte = obstacles
        remplacements.append((a, b, texte))
    for c in calques:
        if c.modifie:
            remplacements.append((c.a, c.b, c.texte_complet(mm)))
    remplacements.sort()
    with open(chemin_dst, 'wb') as out:
        curseur = 0
        for a, b, texte in remplacements:
            out.write(mm[curseur:a])
            out.write(texte)
            curseur = b
        out.write(mm[curseur:len(mm)])


def sha(chemin):
    h = hashlib.sha256()
    with open(chemin, 'rb') as f:
        for bloc in iter(lambda: f.read(1 << 22), b''):
            h.update(bloc)
    return h.hexdigest()


def main():
    src = Path(sys.argv[1])
    if '--verifier' in sys.argv:
        dst = Path('/tmp/verif_ground.rsground')
        f, mm, calques, noms = ouvrir(src)
        reecrire(src, dst, calques, mm)
        a, b = sha(src), sha(dst)
        print('source :', a)
        print('réécrit:', b)
        print('IDENTIQUE' if a == b else 'DIVERGENT')
        f.close()
        return 0 if a == b else 1

    dst = Path(sys.argv[2])
    scenario = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else {}
    f, mm, calques, noms = ouvrir(src)
    print(f'{len(calques)} calques lus')
    for i, n in enumerate(noms):
        print(f'  {i:2d} {n}')

    def copier_obstacles(grille, op):
        tx0, ty0, tx1, ty1, dx, dy, mode = op
        w, h = tx1 - tx0, ty1 - ty0
        for j in range(h):
            for i in range(w):
                i2 = w - 1 - i if mode in ('h', 'hv') else i
                j2 = h - 1 - j if mode in ('v', 'hv') else j
                grille[dx + i2][dy + j2] = dict(grille[tx0 + i][ty0 + j])

    def editeur_copier(calques, op):
        tx0, ty0, tx1, ty1, dx, dy, mode = op
        w, h = tx1 - tx0, ty1 - ty0
        touches = 0
        for c in calques:
            for j in range(h):
                for i in range(w):
                    sx, sy = tx0 + i, ty0 + j
                    if mode in ('h', 'hv'):
                        i2 = w - 1 - i
                    else:
                        i2 = i
                    if mode in ('v', 'hv'):
                        j2 = h - 1 - j
                    else:
                        j2 = j
                    texte = c.lire(mm, sx, sy)
                    if texte == c.lire(mm, dx + i2, dy + j2):
                        continue          # rien à changer : on n'occupe pas de mémoire
                    c.ecrire(dx + i2, dy + j2, texte)
                    touches += 1
        return touches

    obs = lire_obstacles(mm)
    grille = obs[2] if obs else None
    VIDE = (b'{\r\n"AutoTileset": "",\r\n"Associates": [],\r\n"Layers": [],'
            b'\r\n"NeighborCode": -1\r\n}')

    def editeur_vider(calques, op):
        tx0, ty0, tx1, ty1, calque = op
        c = calques[calque]
        n = 0
        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                if c.lire(mm, tx, ty) == VIDE:
                    continue
                c.ecrire(tx, ty, VIDE)
                n += 1
        return n

    def editeur_poser(calques, op):
        calque_cible, tx0, ty0, tx1, ty1, calque_src, sx, sy = op
        texte = calques[calque_src].lire(mm, sx, sy)
        c = calques[calque_cible]
        n = 0
        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                if c.lire(mm, tx, ty) == texte:
                    continue
                c.ecrire(tx, ty, texte)
                n += 1
        return n

    total = 0
    for op in scenario.get('vider', []):
        total += editeur_vider(calques, op)
    for op in scenario.get('poser', []):
        total += editeur_poser(calques, op)
    for op in scenario.get('copier', []):
        total += editeur_copier(calques, op)
        if grille is not None:
            copier_obstacles(grille, op)
    obstacles = None
    if grille is not None and scenario.get('copier'):
        a, b, _ = obs
        obstacles = (a, b, json.dumps(grille, separators=(',', ':')).encode())
    reecrire(src, dst, calques, mm, obstacles)
    print(f'écrit {dst} — {total} cases traitées, {sum(c.modifie for c in calques)} calques modifiés')
    f.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
