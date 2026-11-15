#!/usr/bin/env python3
"""Refait les 4 ambiances des fenêtres de la Guilde Destiny (56 `.dir`).

Défaut corrigé
--------------
Le générateur d'origine classait les pixels « bois » en comparant la fenêtre au
décor brut de la pièce (`diff < 22`) ou par une règle de couleur. Dans l'accueil,
le ciel de jour est crème et le décor aussi : **toute la baie** était classée
bois, donc jamais pré-compensée ni variée — jour, aube, crépuscule et nuit
sortaient quasi identiques (seuls 7,6 % des pixels changeaient).

Séparation retenue (structurelle)
---------------------------------
Est verre ce qui n'est pas orange chaud (`r - g >= 25`), en ne gardant que les
composantes connexes qui **ne touchent pas le bord** : le cadre et les meneaux
touchent toujours le bord, ils sont donc exclus mécaniquement. Vérifié
visuellement sur les 13 fenêtres sources.

Pré-compensation
----------------
`GroundObject.DrawPreview` multiplie tout objet par `WorldAmbianceTint` quand
`SetDestinyAmbiance(moment, true)` est actif. On raisonne donc en couleur
**effective** (ce que voit le joueur) puis on divise par la teinte pour obtenir
la couleur à stocker : `stocké = cible / wt`. Conséquence assumée : la nuit, la
vitre ne peut pas dépasser le plafond (97,118,159) — on s'en approche, ce qui
donne déjà un contraste de ~2,3 avec le mur.

Le cadre, lui, n'est **jamais** retouché : il conserve l'art DS de l'ambiance.

Usage
-----
    python3 tools/refaire_fenetres_ambiances.py --dry-run   # rendus de contrôle
    python3 tools/refaire_fenetres_ambiances.py             # écrit game/
"""
from __future__ import annotations

import argparse
import io
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

GAME = REPO / "game"
OBJ_DIR = GAME / "Content/Object"
DS_DIR = Path("/var/tmp/dsall")                      # décors de référence (673e05b)
SRC = Path("/home/user/guilde_destiny_reseau/objets_pmdo/fenetres")
CONTROL = Path("/var/tmp/work/fenetres_controle")

AMBIANCES = ("jour", "aube", "crepuscule", "nuit")
WORLD_TINTS = {
    "jour": np.array([255.0, 255.0, 255.0]),
    "aube": np.array([224.0, 203.0, 212.0]),
    "crepuscule": np.array([179.0, 146.0, 173.0]),
    "nuit": np.array([97.0, 118.0, 159.0]),
}

# Dégradés de ciel en couleur EFFECTIVE (haut -> bas), 4 tons pixel-art.
RAMPS = {
    "jour":      [(255, 250, 206), (251, 238, 178), (240, 217, 152), (216, 188, 126)],
    "aube":      [(250, 216, 208), (241, 189, 184), (227, 160, 160), (201, 132, 140)],
    "crepuscule": [(150, 140, 190), (198, 141, 151), (232, 152, 106), (240, 172, 92)],
    "nuit":      [(80, 100, 140), (66, 85, 126), (52, 70, 108), (38, 54, 88)],
}
STAR = (255, 255, 255)          # plafonne au maximum atteignable la nuit


def nom_dir(tag: str, side: str, amb: str, miroir: bool = False) -> str:
    if tag == "01_accueil":
        return f"Guilde_Fenetre_Accueil_{side}_{amb.capitalize()}"
    return f"Guilde_Fenetre_{tag}_{side}{'_Miroir' if miroir else ''}_{amb.capitalize()}"


def masque_verre(jour: np.ndarray) -> np.ndarray:
    """Verre = composantes non-orange qui ne touchent pas le bord de l'image."""
    r, g = jour[..., 0].astype(int), jour[..., 1].astype(int)
    op = jour[..., 3] > 0
    candidat = op & ~((r - g) >= 25)
    lab, n = ndimage.label(candidat)
    bord = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))) - {0}
    garde = sorted(set(range(1, n + 1)) - bord)
    return np.isin(lab, garde)


def gradient(verre: np.ndarray, ramp: list[tuple[int, int, int]]) -> np.ndarray:
    """Applique le dégradé vertical du ciel sur le masque de verre."""
    out = np.zeros(verre.shape + (3,), np.float32)
    ys, xs = np.where(verre)
    if not len(ys):
        return out
    y0, y1 = float(ys.min()), float(ys.max())
    t = np.clip((np.arange(verre.shape[0], dtype=np.float32) - y0) / max(1.0, y1 - y0), 0, 1)
    pal = np.array(ramp, np.float32)
    xs4 = np.array([0.0, 0.36, 0.70, 1.0])
    grad = np.stack([np.interp(t, xs4, pal[:, c]) for c in range(3)], axis=1)
    out[:] = grad[:, None, :]
    return out


def etoiles(verre: np.ndarray, base: np.ndarray, seed: int = 20260201) -> np.ndarray:
    """Quelques étoiles nettes + un halo très léger dans le verre."""
    rng = np.random.default_rng(seed)
    ys, xs = np.where(verre)
    if not len(ys):
        return base
    out = base.copy()
    n = max(5, int(verre.sum() / 320))
    for i in rng.choice(len(ys), size=min(n, len(ys)), replace=False):
        y, x = int(ys[i]), int(xs[i])
        out[y, x] = STAR
    # halo
    star_map = (out.sum(axis=2) >= 3 * 250).astype(np.float32)
    halo = ndimage.gaussian_filter(star_map, 1.2) * 0.55
    out += halo[..., None] * np.array([40, 46, 62], np.float32)[None, None, :]
    return out


def construire(tag: str, side: str, echelle: int, dry: bool) -> dict:
    base_name = f"Guilde_Fenetre_{tag}_{side}"
    jour = np.array(Image.open(SRC / f"{base_name}_Jour.png").convert("RGBA"))
    verre = masque_verre(jour)

    rendus: dict[str, np.ndarray] = {}
    lums: dict[str, float] = {}
    CONTROL.mkdir(parents=True, exist_ok=True)

    for amb in AMBIANCES:
        wt = WORLD_TINTS[amb] / 255.0
        brut = np.array(Image.open(SRC / f"{base_name}_{amb.capitalize()}.png").convert("RGBA"))
        cible = gradient(verre, RAMPS[amb])
        if amb == "nuit":
            cible = etoiles(verre, cible)
        # couleur à stocker pour obtenir `cible` après le filtre moteur
        stocke = np.clip(np.round(cible / wt[None, None, :]), 0, 255)

        out = brut.copy()                        # cadre DS intact, alpha DS intact
        out[..., :3][verre] = stocke[verre].astype(np.uint8)
        im = Image.fromarray(out, "RGBA")
        if echelle != 1:
            im = im.resize((im.width * echelle, im.height * echelle), Image.Resampling.NEAREST)

        arr = np.array(im, np.float32)
        eff = np.clip(arr[..., :3] * wt[None, None, :], 0, 255)
        op = arr[..., 3] > 0
        L = eff[..., 0] * 0.299 + eff[..., 1] * 0.587 + eff[..., 2] * 0.114
        lums[amb] = float(L[op].mean()) if op.any() else 0.0
        rendus[amb] = im
        im.save(CONTROL / f"{base_name}_{amb}.png")

    if not dry:
        for amb in AMBIANCES:
            im = rendus[amb]
            _ecrire_dir(OBJ_DIR / f"{nom_dir(tag, side, amb)}.dir", im)
        # Dortoir Nord 2 : même source, miroir horizontal (cf. build d'origine)
        if tag == "09_dortoir_nord":
            for amb in AMBIANCES:
                im = rendus[amb].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                _ecrire_dir(OBJ_DIR / f"{nom_dir(tag, side, amb, miroir=True)}.dir", im)

    return {"fenetre": base_name, "echelle": echelle,
            "taille": list(rendus["jour"].size), "verre_px": int(verre.sum()),
            "lum_effective": {a: round(lums[a], 1) for a in AMBIANCES}}


def _ecrire_dir(path: Path, im: Image.Image) -> None:
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<q", len(png)) + png
                     + struct.pack("<iiii", im.width, im.height, 0, 1))


FENETRES = [
    ("01_accueil", "Gauche", 3),
    ("01_accueil", "Droite", 3),
    ("02_missions", "Gauche", 1),
    ("02_missions", "Droite", 1),
    ("03_grand_salon_central", "Gauche", 1),
    ("03_grand_salon_central", "Droite", 1),
    ("04_bureau_maitre", "Centre", 1),
    ("05_refectoire", "Gauche", 1),
    ("05_refectoire", "Droite", 1),
    ("06_cuisine", "Gauche", 1),
    ("06_cuisine", "Droite", 1),
    ("09_dortoir_nord", "Centre", 1),
    ("11_chambre_heros", "Centre", 1),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rapport = []
    for tag, side, ech in FENETRES:
        r = construire(tag, side, ech, args.dry_run)
        rapport.append(r)
        print(f"[OK] {r['fenetre']:44s} {r['taille'][0]:4d}x{r['taille'][1]:<4d} éch.{ech} "
              f"verre={r['verre_px']:5d} lum=" + " ".join(f"{k[:3]}={v:5.1f}" for k, v in r["lum_effective"].items()))
    Path("/var/tmp/work/fenetres_rapport.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
