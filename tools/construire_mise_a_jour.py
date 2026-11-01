#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit le paquet de mise à jour depuis la version publiée précédente.

Compare `git diff <étiquette précédente>..HEAD` et emballe les fichiers
d'installation modifiés sous PMDO-Destiny/ (même racine que le ZIP complet),
avec MANIFEST.txt : SHA-256 de chaque entrée + fichiers supprimés depuis la
version précédente.

Usage :
  python3 tools/construire_mise_a_jour.py --prev v0.3.4-dev-foret
  python3 tools/construire_mise_a_jour.py --prev v0.3.4-dev-foret --version 0.3.5-dev-quiz
"""
import argparse
import hashlib
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Fichiers du dépôt livrés dans l'installation (voir tools/build_windows.py).
RACINE_INSTALL = 'game/'


def lire_version() -> str:
    return (ROOT / 'VERSION').read_text(encoding='utf-8').strip()


def nom_install(depots: str) -> str | None:
    """Chemin du dépôt → chemin dans l'installation, ou None si non livré."""
    if depots.startswith(RACINE_INSTALL):
        return 'PMDO-Destiny/' + depots[len(RACINE_INSTALL):]
    if depots == 'docs/LISEZ_MOI_WINDOWS.txt':
        return 'PMDO-Destiny/LISEZ_MOI.txt'
    return None


def diff_depuis(prev: str) -> list[tuple[str, str]]:
    """[(statut, chemin)] modifiés depuis l'étiquette (git diff --name-status)."""
    brut = subprocess.run(
        ['git', 'diff', '--name-status', f'{prev}..HEAD', '--',
         'game', 'docs/LISEZ_MOI_WINDOWS.txt'],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    sortie = []
    for ligne in brut.splitlines():
        if not ligne.strip():
            continue
        statut, chemin = ligne.split('\t')[:2]
        sortie.append((statut, chemin))
    return sortie


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def construire(prev: str, version: str | None = None) -> Path:
    version = version or lire_version()
    modifs = diff_depuis(prev)
    if not modifs:
        raise SystemExit(f'Aucun fichier d\'installation modifié depuis {prev}.')
    manifeste = [f'PAQUET DE MISE À JOUR {version} (depuis {prev})', '']
    supprimes = []
    dest = ROOT / 'dist' / f'PMDO-Destiny-Mise-a-jour-{version}.zip'
    dest.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for statut, chemin in modifs:
            cible = nom_install(chemin)
            if cible is None:
                continue
            if statut.startswith('D'):
                supprimes.append(chemin)
                continue
            contenu = (ROOT / chemin).read_bytes()
            if chemin == 'docs/LISEZ_MOI_WINDOWS.txt':
                # Tamponner la version dans le LISEZ_MOI livré.
                texte = contenu.decode('utf-8')
                texte = re.sub(r'^Version .* — Windows x64$',
                               f'Version {version} — Windows x64',
                               texte, count=1, flags=re.M)
                contenu = texte.replace('\n', '\r\n').encode('utf-8')
            zf.writestr(cible, contenu)
            manifeste.append(f'{sha256(contenu)}  {cible}')
        if supprimes:
            manifeste += ['', 'SUPPRIMÉS DEPUIS LA VERSION PRÉCÉDENTE (les retirer à la main) :']
            manifeste += ['  ' + s for s in supprimes]
        manifeste += ['', f'{len(modifs)} entrée(s) modifiée(s) depuis {prev}.']
        zf.writestr('MANIFEST.txt', '\r\n'.join(manifeste) + '\r\n')
    print(f'Paquet : {dest} ({dest.stat().st_size / 1048576:.1f} MiB, '
          f'{len(modifs)} fichier(s) modifié(s))')
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prev', required=True, help='Étiquette publiée précédente (ex. v0.3.4-dev-foret).')
    parser.add_argument('--version', help='Version du paquet (défaut : fichier VERSION).')
    args = parser.parse_args()
    construire(args.prev, args.version)


if __name__ == '__main__':
    main()
