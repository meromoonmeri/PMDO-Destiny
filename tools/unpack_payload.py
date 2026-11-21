#!/usr/bin/env python3
"""Reconstitue les fichiers volumineux non versionnés, sans écraser une édition.

Les dix variantes de Réverie Town ont onze calques, et la limite sud
s'arrête après la maison ronde. Chaque carte est restaurée et vérifiée
(SHA-256 et taille) depuis le payload versionné.

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
    'payload/reverie_centre.rsground.gz': ('game/Data/Ground/reverie_centre.rsground', '230c472c42c65920f4d665061dcfae0b4ed0e0c304f393ac12d68571f672d180', 29357578),
    'payload/reverie_nord.rsground.gz': ('game/Data/Ground/reverie_nord.rsground', 'acd7498bb0555c1d3df2942c48208647aaabcb9ccb0f44b63bbadf3f8324e40a', 29357576),
    'payload/WaterfallVillageCapital.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital.rsground', 'cce59f4ca65f3ac8c8f841fc94d7a3e734d0bb301a335af1925fd40252d07a06', 29363257),
    'payload/reverie_residentiel.rsground.gz': ('game/Data/Ground/reverie_residentiel.rsground', 'eaf10c381e454a120b78d2cdf6debddf0e8da34a14a660f123750630c3fe2196', 29335309),
    'payload/reverie_etang.rsground.gz': ('game/Data/Ground/reverie_etang.rsground', '2543f49a70ebffa2476239ae531bcc387ee41adc250d1faa644ab997601e4334', 29329634),
    'payload/reverie_centre_Dev.rsground.gz': ('game/Data/Ground/reverie_centre_Dev.rsground', '8f8c81b41696abd142356f6bee8cca442ff835ab3e33ed5ceb194aaa08c7831a', 29357582),
    'payload/reverie_nord_Dev.rsground.gz': ('game/Data/Ground/reverie_nord_Dev.rsground', 'ebd70cdeb2f6c7dcb288bb174137dca94d54b54040ee460909e24053798811a5', 29357580),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital_Dev.rsground', '7b44bb73349b22d5ff9ef712e7f5da94ec25ca6acd97635739d311f211940caa', 29363261),
    'payload/reverie_residentiel_Dev.rsground.gz': ('game/Data/Ground/reverie_residentiel_Dev.rsground', '20795f653bdbfafb392b2dddbdd0ca498ff5a465818fd8d2549c0a89327b5a9e', 29335313),
    'payload/reverie_etang_Dev.rsground.gz': ('game/Data/Ground/reverie_etang_Dev.rsground', '2b4525b1b70e59d33c7d78496e037984b3291267c1823b1efd44486f23d0f3a1', 29329638),
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
