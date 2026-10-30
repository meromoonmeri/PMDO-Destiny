#!/usr/bin/env python3
"""Reconstitue les fichiers trop volumineux pour GitHub à partir de payload/*.gz.

Actuellement : game/Data/Ground/WaterfallVillageCapital.rsground (233 727 831 octets,
carte native de meromoonmeri/town02, fournie compressée : 1,5 Mo). Le SHA-256 du fichier
reconstitué est vérifié ; il correspond à l'objet LFS d'origine de town02.
"""
import gzip, hashlib, shutil, sys
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
        if dst_p.is_file() and dst_p.stat().st_size == size and sha256(dst_p) == digest:
            print(f'OK (déjà présent) {dst}')
            continue
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(src_p, 'rb') as f_in, open(dst_p, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out, 1 << 20)
        got = sha256(dst_p)
        if got != digest or dst_p.stat().st_size != size:
            print(f'ERREUR {dst}: sha256 {got} attendu {digest}')
            ok = False
        else:
            print(f'OK (reconstitué) {dst} ({size} octets)')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
