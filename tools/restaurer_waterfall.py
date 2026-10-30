#!/usr/bin/env python3
"""Restaure WaterfallVillageCapital.rsground dans la Quest destiny.

GitHub refuse tout fichier de plus de 100 Mio. Le Ground de la capitale pèse
315 Mio : il est donc stocké ici **compressé sans perte**
(ressources/WaterfallVillageCapital.rsground.gz, 2,0 Mio) et restauré à
l'identique. L'empreinte SHA-256 du fichier produit est vérifiée.

Version restaurée : celle du Drive de l'auteur (330 233 300 o), prolongée par
les chemins de la plaine sud (330 315 007 o). L'extension est reproductible :
tools/dessiner_chemins.py applique exactement les mêmes retouches à partir du
fichier du Drive. Voir docs/AMELIORATION_WVC_SUD.md.

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

# empreinte du fichier livré = fichier du Drive + chemins de la plaine sud
ATTENDU_SHA256 = "867a90e78eaf5bb1520d4db4f2e2e82de881f1023e4c5aa1b4410670a9c56777"
TAILLE = 330_315_007
# empreinte du fichier du Drive, avant retouches (contrôle de la source)
SHA_DRIVE = "2268e2696e259bbac012eb0d7ef9b530e2926161c2140b9e346715b2ab4a446a"


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
