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
    'payload/reverie_centre.rsground.gz': ('game/Data/Ground/reverie_centre.rsground', '0ea0846ca1721211b90487b7266c9d714e1f90c3903f5ec032991542c55dff8b', 36695135),
    'payload/reverie_nord.rsground.gz': ('game/Data/Ground/reverie_nord.rsground', '6e48efb76fd53c3c8e06d7da61a475f7eaf91066637478bbe4bb4f81e1e841e3', 36695133),
    'payload/WaterfallVillageCapital.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital.rsground', '8a4d39115095bb2fa0483069908619d34254189b3a37887ce9d94c267b5b78bf', 36700814),
    'payload/reverie_residentiel.rsground.gz': ('game/Data/Ground/reverie_residentiel.rsground', '558dcfc9b8a002e322f2a44a98aee86500a4010082e9d95c0ea616c0cc1ca614', 36672866),
    'payload/reverie_etang.rsground.gz': ('game/Data/Ground/reverie_etang.rsground', '3c9037b558bba68c6e7bd63e79397c1ab2400e737a88c277bae0d774bbda7a2a', 36667191),
    'payload/reverie_centre_Dev.rsground.gz': ('game/Data/Ground/reverie_centre_Dev.rsground', '483225c884989210093ae948b41cd82ba81c7b77eab4a303deacd6152616a9b8', 36695139),
    'payload/reverie_nord_Dev.rsground.gz': ('game/Data/Ground/reverie_nord_Dev.rsground', '5140ad5ae11ac84f34070e60ece8c6b5ac85521fa15fa0a8117d5b59109f57d0', 36695137),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital_Dev.rsground', 'a942e62b182d5f55904398c87e21664b2e75bddf9abcaeda067a55d8aaf48437', 36700818),
    'payload/reverie_residentiel_Dev.rsground.gz': ('game/Data/Ground/reverie_residentiel_Dev.rsground', '5514fab67e7b697e5a4efde46802018ab04563fb13e7df94dbe837300a318fa9', 36672870),
    'payload/reverie_etang_Dev.rsground.gz': ('game/Data/Ground/reverie_etang_Dev.rsground', '07577084871b4ba6f594a693315611fef9cf61a1f5a2608016cd1f2c69032ccc', 36667195),
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
