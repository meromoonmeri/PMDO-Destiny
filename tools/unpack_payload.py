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
    'payload/reverie_centre.rsground.gz': ('game/Data/Ground/reverie_centre.rsground', '190f3291773ef768c51c717acaaec9607f694efc6b546350019f646850ec9b29', 36683410),
    'payload/reverie_nord.rsground.gz': ('game/Data/Ground/reverie_nord.rsground', '70891375eb5efb6c133ec7e00534f00507304cc9177f0c9382a7b4d3f92286a8', 36683408),
    'payload/WaterfallVillageCapital.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital.rsground', '0ccae5ec698db0cca61a09f5e7c8f01cab5b88f9b87f32354dc2adfe42ede02c', 36689089),
    'payload/reverie_residentiel.rsground.gz': ('game/Data/Ground/reverie_residentiel.rsground', 'eb85f6a90a24f47f525579a599658419769355ddbd280e28ad84b175abd14208', 36661141),
    'payload/reverie_etang.rsground.gz': ('game/Data/Ground/reverie_etang.rsground', 'ba97dc9a91b86ded9ede57fa501f0946c891ee365e38a94407457a622b4654dd', 36655466),
    'payload/reverie_centre_Dev.rsground.gz': ('game/Data/Ground/reverie_centre_Dev.rsground', '39cf6c49a54a896105dc772ae4bc3cb3e234120e95120bd300fa1d2901c15f3d', 36683414),
    'payload/reverie_nord_Dev.rsground.gz': ('game/Data/Ground/reverie_nord_Dev.rsground', 'd6cbe3cbf9851ce167e908910e4509db3e6b81a25c282b2b075ec34431934c8f', 36683412),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital_Dev.rsground', 'cebfae64db4f3c80285e593d8748180f35bfe6c0b16c38ec6c7a25d0bd0a23c2', 36689093),
    'payload/reverie_residentiel_Dev.rsground.gz': ('game/Data/Ground/reverie_residentiel_Dev.rsground', 'ec588fb16cf288bf73da3f4f986cd07b741abb5a0619b8d71466e5b0d2326148', 36661145),
    'payload/reverie_etang_Dev.rsground.gz': ('game/Data/Ground/reverie_etang_Dev.rsground', 'fbf2ac97c940b7d82aac0a0e93c8562965f244e2901215cedafc6bec93fa2cff', 36655470),
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
