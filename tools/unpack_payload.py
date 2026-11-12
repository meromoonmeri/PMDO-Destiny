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
    'payload/reverie_centre.rsground.gz': ('game/Data/Ground/reverie_centre.rsground', '8838ddf8a0f7edc45a06bdc2ec3fff4049a2417aefbb15bd57cd5873a737d719', 36711659),
    'payload/reverie_nord.rsground.gz': ('game/Data/Ground/reverie_nord.rsground', '889ec72e9688dbc9cf1c2ec80ba4eb1f339b6621adb80f9557b4096eda02ced5', 36711657),
    'payload/WaterfallVillageCapital.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital.rsground', '58133511960b217293e9f8dc9931fe1646ff175c79b04d05dcf665e4b4aca68d', 36717338),
    'payload/reverie_residentiel.rsground.gz': ('game/Data/Ground/reverie_residentiel.rsground', '76f4cc2535c7aa7b37287bb9426d33846422ea242a73b9740e01a6e150f44362', 36689390),
    'payload/reverie_etang.rsground.gz': ('game/Data/Ground/reverie_etang.rsground', '9bf5995348ec60e13002c5b378aa6660702dc27d47fe00db228a1530ac78bc0b', 36683715),
    'payload/reverie_centre_Dev.rsground.gz': ('game/Data/Ground/reverie_centre_Dev.rsground', '72c2b428ed680eea400aceec71ccd10d7d0e2293d3bb5379abf032402d45337e', 36711663),
    'payload/reverie_nord_Dev.rsground.gz': ('game/Data/Ground/reverie_nord_Dev.rsground', 'e05b7a8b334ece08404dae2fc93781a45f3fd79a061fb8f423a2827983c01960', 36711661),
    'payload/WaterfallVillageCapital_Dev.rsground.gz': ('game/Data/Ground/WaterfallVillageCapital_Dev.rsground', 'f9204fd052f347fc8d98a09bf53d7c55cb44b236ac4ac0ba95a92da99dbcecbb', 36717342),
    'payload/reverie_residentiel_Dev.rsground.gz': ('game/Data/Ground/reverie_residentiel_Dev.rsground', '62f3e2d79ab028cd4c4c8d8d723f2276cf471a8631ef8e75790cf2a37e92ba8f', 36689394),
    'payload/reverie_etang_Dev.rsground.gz': ('game/Data/Ground/reverie_etang_Dev.rsground', 'da90e6b61421d66ed903378e94efa89e8a9138c0fc93c0690c56507583cbb636', 36683719),
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
