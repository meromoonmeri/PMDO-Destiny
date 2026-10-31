#!/usr/bin/env python3
"""Reconstitue les fichiers volumineux depuis payload/*.gz, sans écraser une édition.

WaterfallVillageCapital.rsground est la carte native de meromoonmeri/town02 :
233 727 831 octets reconstitués depuis l'archive Git. Son SHA-256 est vérifié.
"""
import gzip
import hashlib
import shutil
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = {
    'payload/WaterfallVillageCapital.rsground.gz': (
        'game/Data/Ground/WaterfallVillageCapital.rsground',
        'afc5081f7348b2afed306953bf5e66a358e442cb00f93fa139ec239cf94c98ee', 233727831),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


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
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
