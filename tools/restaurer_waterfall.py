#!/usr/bin/env python3
"""Restaure WaterfallVillageCapital.rsground dans la Quest destiny.

GitHub refuse tout fichier de plus de 100 Mio. Le Ground de la capitale pèse
315 Mio : il est donc stocké ici **compressé sans perte**
(ressources/WaterfallVillageCapital.rsground.gz, 1,9 Mio) et restauré à
l'identique. L'empreinte SHA-256 du fichier produit est vérifiée.

Version restaurée : celle du Drive (330 233 300 o) **étendue au sud** par
tools/editer_ground.py — voir docs/AMELIORATION_WVC_SUD.md.

Usage :
    python tools/restaurer_waterfall.py
"""
import gzip
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ressources" / "WaterfallVillageCapital.rsground.gz"
TARGET = ROOT / "game" / "Data" / "Ground" / "WaterfallVillageCapital.rsground"

# empreinte de la version étendue (Drive + extension du sud), calculée après édition
ATTENDU_SHA256 = "e4ee71d7b8082a361bcae1be909ca77dcb80d162b83dd5c5f411eb7d851f48b3"
TAILLE = 330_482_389


def main() -> int:
    if not SOURCE.is_file():
        print(f"archive absente : {SOURCE}", file=sys.stderr)
        return 1
    if TARGET.is_file():
        digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
        if digest == ATTENDU_SHA256:
            print(f"déjà restauré : {TARGET} ({TARGET.stat().st_size} octets)")
            return 0
        print("un fichier différent existe déjà, il n'est pas écrasé.", file=sys.stderr)
        return 2
    data = gzip.decompress(SOURCE.read_bytes())
    if len(data) != TAILLE:
        print(f"taille inattendue : {len(data)}", file=sys.stderr)
        return 3
    digest = hashlib.sha256(data).hexdigest()
    if digest != ATTENDU_SHA256:
        print(f"empreinte inattendue : {digest}", file=sys.stderr)
        return 4
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(data)
    print(f"restauré : {TARGET} ({len(data)} octets, sha256 vérifié)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
