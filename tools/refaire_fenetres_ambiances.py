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
    # BANDES PLATES et non un dégradé continu : un ciel en pixel art doit
    # compter 4 tons francs. L'interpolation donnait ~90 teintes voisines, ce
    # qui se lisait comme un « flou de filtre » une fois posé sur les murs.
    seuils = np.array([0.18, 0.53, 0.85], np.float32)
    idx = np.digitize(t, seuils).astype(np.int32)
    grad = pal[idx]
    out[:] = grad[:, None, :]
    return out


def etoiles(verre: np.ndarray, base: np.ndarray, seed: int = 20260201) -> np.ndarray:
    """Étoiles en AMAS de 3 à 6 px, strictement à l'intérieur du verre.

    Deux défauts corrigés par rapport à la version précédente :
    * les étoiles isolées d'1 px apparaissaient comme des « pixels parasites »
      blancs sur la vitre -> ce sont maintenant de petites constellations ;
    * le halo gaussien débordait du verre et bavait sur le cadre (visible en
      haut de la baie de l'accueil) -> il est remplacé par une diffusion
      limitée aux 4 voisins qui sont eux aussi du verre.
    """
    rng = np.random.default_rng(seed)
    # marge de 2 px : aucun amas ne touche le cadre
    interieur = ndimage.binary_erosion(verre, np.ones((3, 3), bool), iterations=2)
    ys, xs = np.where(interieur)
    if not len(ys):
        return base
    out = base.copy()
    h, w = verre.shape
    n_amas = max(4, int(verre.sum() / 700))
    pris = np.zeros_like(verre)
    halo = np.array([44, 52, 74], np.float32)

    for i in rng.choice(len(ys), size=min(n_amas, len(ys)), replace=False):
        y0, x0 = int(ys[i]), int(xs[i])
        if pris[max(0, y0 - 2):y0 + 3, max(0, x0 - 2):x0 + 3].any():
            continue
        taille = int(rng.integers(3, 7))
        amas = [(y0, x0)]
        frontiere = [(y0, x0)]
        while len(amas) < taille and frontiere:
            k = int(rng.integers(0, len(frontiere)))
            cy, cx = frontiere.pop(k)
            dy, dx = [(0, 1), (0, -1), (1, 0), (-1, 0)][int(rng.integers(0, 4))]
            ny_, nx_ = cy + dy, cx + dx
            if not (0 <= ny_ < h and 0 <= nx_ < w) or not interieur[ny_, nx_]:
                continue
            if (ny_, nx_) in amas:
                continue
            amas.append((ny_, nx_)); frontiere.append((ny_, nx_))
        for py, px in amas:
            out[py, px] = STAR
            pris[py, px] = True
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                yy, xx = py + dy, px + dx
                if 0 <= yy < h and 0 <= xx < w and verre[yy, xx] and not pris[yy, xx] and \
                        tuple(out[yy, xx]) != STAR:
                    out[yy, xx] = np.minimum(out[yy, xx] + halo * 0.5, 255)
    return out


def palette_cadre(base_name: str, verre: np.ndarray, n: int = 14) -> np.ndarray:
    """Palette de bois du cadre (14 tons), commune aux 4 ambiances.

    Les PNG sources des fenêtres sont peints avec des dégradés lisses : 1885
    couleurs pour un sprite de 48x88. Posé à côté des murs DS (une dizaine de
    tons francs), cela se lisait comme un filtre flou, avec des liserés clairs
    et sombres sur les arêtes. On ré-extrait donc la palette réelle du cadre par
    coupe médiane, puis on y ramène chaque pixel : bois franc, bords nets.
    """
    px = []
    for amb in AMBIANCES:
        a = np.array(Image.open(SRC / f"{base_name}_{amb.capitalize()}.png").convert("RGBA"))
        sel = (a[..., 3] > 0) & ~verre
        px.append(a[sel][:, :3])
    px = np.concatenate(px)
    if not len(px):
        return np.zeros((1, 3), np.uint8)
    # uniquement des tons BOIS : les PNG d'ambiance contiennent des pixels de
    # ciel bleu nuit qui, laissés dans la palette, ressortaient sur le cadre.
    px = px[px[:, 0].astype(int) >= px[:, 2].astype(int)]
    if not len(px):
        return np.zeros((1, 3), np.uint8)
    bande = Image.fromarray(px[None, :, :].astype(np.uint8), "RGB")
    q = bande.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[: n * 3], np.uint8).reshape(-1, 3)
    return pal


def appliquer_palette(rgba: np.ndarray, palette: np.ndarray, verre: np.ndarray) -> np.ndarray:
    """Ramène les pixels de CADRE à la palette (le verre est laissé de côté)."""
    out = rgba.copy()
    sel = (rgba[..., 3] > 0) & ~verre
    if not sel.any() or not len(palette):
        return out
    px = rgba[sel][:, :3].astype(np.int32)
    d = ((px[:, None, :] - palette[None, :, :].astype(np.int32)) ** 2).sum(axis=2)
    out[sel, :3] = palette[np.argmin(d, axis=1)]
    # élimine les pixels isolés nés de la quantification.
    # `donor=sel` est INDISPENSABLE : sans lui, un pixel de cadre prenait la
    # couleur d'un pixel de VERRE voisin et laissait des bleu nuit dans le bois.
    from speckle import clean
    out, _ = clean(out, max_area=1, tol=0.0, iters=2, donor=sel)
    return out


def construire(tag: str, side: str, echelle: int, dry: bool) -> dict:
    base_name = f"Guilde_Fenetre_{tag}_{side}"
    src_jour = Image.open(SRC / f"{base_name}_Jour.png").convert("RGBA")
    jour = np.array(src_jour)
    verre = masque_verre(jour)

    rendus: dict[str, np.ndarray] = {}
    lums: dict[str, float] = {}
    CONTROL.mkdir(parents=True, exist_ok=True)
    palette = palette_cadre(base_name, verre)

    for amb in AMBIANCES:
        wt = WORLD_TINTS[amb] / 255.0
        brut = np.array(Image.open(SRC / f"{base_name}_{amb.capitalize()}.png").convert("RGBA"))
        # cadre re-quantifié sur la palette commune aux 4 ambiances
        brut = appliquer_palette(brut, palette, verre)
        cible = gradient(verre, RAMPS[amb])
        if amb == "nuit":
            cible = etoiles(verre, cible)
        # couleur à stocker pour obtenir `cible` après le filtre moteur
        stocke = np.clip(np.round(cible / wt[None, None, :]), 0, 255)

        out = brut.copy()                        # cadre DS intact, alpha DS intact
        out[..., :3][verre] = stocke[verre].astype(np.uint8)
        im = Image.fromarray(out, "RGBA")
        if echelle != 1:
            # agrandissement net : chaque pixel DS devient un bloc de 3x3
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
    ("01_accueil", "Gauche", 1),
    ("01_accueil", "Droite", 1),
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
