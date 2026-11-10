#!/usr/bin/env python3
"""Reconstitue les fichiers volumineux non versionnés, sans écraser une édition.

WaterfallVillageCapital.rsground est la carte de Réverie Town (base town02, rivières animées 0.3.7, collisions et PNJ corrigés 0.3.8) :
Carte de jeu (11 couches) et copie d’édition (11 couches expérimentales) reconstituées depuis l'archive Git. Son SHA-256 est vérifié.

L'index des planches (`game/Content/Tile/index.idx`) dépasse lui aussi la
limite GitHub des fichiers ordinaires, mais il est entièrement dérivé des
en-têtes des fichiers `.tile` versionnés : il est donc régénéré par
`tools/build_tile_index.py` plutôt que stocké dans `payload/`.
"""
import gzip
import hashlib
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = {
    'payload/reverie_centre.rsground.gz': ('game/Data/Ground/reverie_centre.rsground', '6dceae6de31f29bf405ca4b2befd2484002248d6f6d7e203cd511ed9fe9c03d2', 36677579),
    'payload/reverie_nord.rsground.gz': ('game/Data/Ground/reverie_nord.rsground', '0f1cbc928ad7e0147502f4b60e9b45c8d78e5c0dabef4741ef1b08693f7233e7', 36677577),
    'payload/WaterfallVillageCapital.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital.rsground', 'd7ad3e979d37fd0d47a269ca492f1f7923718a0b9358113792c9db75d2b03af1', 36683258),
    'payload/reverie_residentiel.rsground.gz': ('game/Data/Ground/reverie_residentiel.rsground', 'f6685f7b611e086cc1dc26d3e5e5654fd26af5500eca1a4c8af06050a7f9e9e7', 36655310),
    'payload/reverie_etang.rsground.gz': ('game/Data/Ground/reverie_etang.rsground', 'a7bf78a6700daff7fce6882bc2830d0fbc30905810f9632d4952a948e4e09afd', 36649635),
    'payload/reverie_centre_Dev.rsground.gz': ('game/Data/Ground/reverie_centre_Dev.rsground', '549d86fc068f4703e511c9b68f67234537fa1b6d9baa228d6390b0aae3dad3a6', 36677583),
    'payload/reverie_nord_Dev.rsground.gz': ('game/Data/Ground/reverie_nord_Dev.rsground', 'cc863b7274c4395de666f61f7f577ec935bc111e3ee2bd7cfe8564ce0a48567e', 36677581),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital_Dev.rsground', 'fe9ffcce61256c96fc5598e338e05892a3cd335f112593070864c0936cee0eec', 36683262),
    'payload/reverie_residentiel_Dev.rsground.gz': ('game/Data/Ground/reverie_residentiel_Dev.rsground', 'eb365b233564f725bb8aef9299b19b39924ac12004f6a395b8ec34d62d559482', 36655314),
    'payload/reverie_etang_Dev.rsground.gz': ('game/Data/Ground/reverie_etang_Dev.rsground', 'aca36851bd8a0abec35679205200a0134e90fdecee3e3b5198670475007ed5e5', 36649639),
}
TILE_INDEX = 'game/Content/Tile/index.idx'
BUILD_TILE_INDEX = 'tools/build_tile_index.py'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_tile_index() -> bool:
    """Régénère l'index des planches s'il est absent, sans écraser un index divergent."""
    index_p = ROOT / TILE_INDEX
    script_p = ROOT / BUILD_TILE_INDEX
    tile_dir = index_p.parent
    # Les tests unitaires du payload travaillent dans un arbre temporaire sans
    # planches ni constructeur d'index : ne rien y générer.
    if not tile_dir.is_dir() or not script_p.is_file():
        return True
    if not any(tile_dir.glob('*.tile')):
        return True
    args = [sys.executable, str(script_p)]
    if index_p.is_file():
        args.append('--check')
    result = subprocess.run(args, cwd=ROOT, check=False)
    if result.returncode == 0:
        state = 'déjà présent' if '--check' in args else 'régénéré'
        print(f'OK ({state}) {TILE_INDEX}')
        return True
    if index_p.is_file():
        print(f'ERREUR {TILE_INDEX} existe mais diffère des en-têtes .tile : aucun écrasement. '
              'Relancez tools/build_tile_index.py après vérification des planches.')
    else:
        print(f'ERREUR impossible de régénérer {TILE_INDEX}')
    return False


def main():
    ok = True
    for src, (dst, digest, size) in PAYLOADS.items():
        src_p, dst_p = ROOT / src, ROOT / dst
        if dst_p.exists():
            if dst_p.is_file() and dst_p.stat().st_size == size and sha256(dst_p) == digest:
                print(f'OK (déjà présent) {dst}')
            else:
                print(f'ERREUR {dst} existe et diffère de la carte native : aucun écrasement. '
                      'Comparez ou déplacez votre fichier avant de réessayer.')
                ok = False
            continue
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        created = False
        try:
            # xb protège aussi contre la création concurrente d'un fichier utilisateur.
            with gzip.open(src_p, 'rb') as f_in, open(dst_p, 'xb') as f_out:
                created = True
                shutil.copyfileobj(f_in, f_out, 1 << 20)
            got = sha256(dst_p)
            if got != digest or dst_p.stat().st_size != size:
                print(f'ERREUR {dst}: sha256 {got} attendu {digest}')
                dst_p.unlink()
                ok = False
            else:
                print(f'OK (reconstitué) {dst} ({size} octets)')
        except (OSError, EOFError, zlib.error) as exc:
            if created:
                dst_p.unlink(missing_ok=True)
            print(f'ERREUR {dst}: {exc}')
            ok = False
    ok = ensure_tile_index() and ok
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
