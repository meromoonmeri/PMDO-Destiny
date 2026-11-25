#!/usr/bin/env python3
"""Rend l'Accueil de la Guilde net : reconstruction de la banque + du ground.

Probleme
--------
`guilde_destiny_accueil` est la seule salle de la Guilde dont l'art a ete
fabrique en agrandissant x3 un dessin 512x384 avec `Image.Resampling.LANCZOS`
(cf. `00_accueil_1536x1152_base.png`).  Lanczos melange les pixels voisins :
chaque trait est entoure d'un degrade, la salle entiere parait floue, et
l'art introduit 22 couleurs qui n'existent pas dans la source.  Sa carte fait
192x144 cases de 8 px : aucun agrandissement ne peut la rendre nette, il faut
repartir de la source 1x et la redessiner a la bonne echelle.

Solution
--------
`Scale3x` (Mazzoleni) agrandit x3 sans interpoler : chaque pixel source est
recopie tel quel, seuls les coins des diagonales sont arrondis avec la couleur
d'un voisin immediat.  Le resultat est du pixel art franc -- 171 couleurs,
exactement la palette de la source, aucun degrade.

Puis on recompile la banque de tuiles 8x8 depuis cet art (une tuile par bloc
distinct, sans deduplication hasardeuse) et on reassigne le ground : le
calque `Floor` porte toute l'image, les calques `Walls` / `Shadows` /
`Supports` qui la redessinaient par morceaux sont vides.  Le calque de
verdure et les fenetres `.dir` ne sont pas touches.

Usage :
    python3 tools/nettete_accueil_guilde.py --check     # diagnostic seul
    python3 tools/nettete_accueil_guilde.py --apply     # reconstruit
"""

from __future__ import annotations

import argparse
import io
import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RACINE = Path(__file__).resolve().parents[1]
SOURCE_1X = RACINE / "art/guilde_destiny_reseau/cartes_base_sans_decors/01_accueil_1x_base.png"
ART_1526 = RACINE / "art/guilde_destiny_reseau/cartes_base_sans_decors/00_accueil_1536x1152_base.png"
BANQUE = RACINE / "game/Content/Tile/Destiny_Guilde_Accueil.tile"
GROUND = RACINE / "game/Data/Ground/guilde_destiny_accueil.rsground"

TUILE = 8
COLONNES = 64
CALQUES_FUSIONNES = (0, 1, 2, 7)   # Floor + Walls + Shadows + Supports
CALQUE_VERDURE = 4
MANIFEST = Path("/home/user/guilde_destiny_reseau/objets_pmdo/manifest_decors_pmdo.json")
BUILD = RACINE / "tools/build_guilde_destiny_reseau.py"


# --- agrandissement --------------------------------------------------------


def scale3x(image: Image.Image) -> Image.Image:
    """Agrandit x3 sans interpoler (Scale3x, Andrea Mazzoleni)."""
    a = np.asarray(image.convert("RGBA"))
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    A, B, C = p[0:-2, 0:-2], p[0:-2, 1:-1], p[0:-2, 2:]
    D, E, F = p[1:-1, 0:-2], p[1:-1, 1:-1], p[1:-1, 2:]
    G, H, I = p[2:, 0:-2], p[2:, 1:-1], p[2:, 2:]

    def eq(x, y):
        return np.all(x == y, axis=2)

    bH, dF, dB, bF = eq(B, H), eq(D, F), eq(D, B), eq(B, F)
    dH, hF = eq(D, H), eq(H, F)
    eC, eA, eG, eI = eq(E, C), eq(E, A), eq(E, G), eq(E, I)
    garde = (~bH) & (~dF)

    def m(sel):
        return (garde & sel)[:, :, None]

    sortie = np.empty((a.shape[0] * 3, a.shape[1] * 3, 4), dtype=np.uint8)

    def poser(k, valeur):
        sortie[(k // 3)::3, (k % 3)::3] = valeur

    poser(0, np.where(m(dB), D, E))
    poser(1, np.where(m((dB & ~eC) | (bF & ~eA)), B, E))
    poser(2, np.where(m(bF), F, E))
    poser(3, np.where(m((dB & ~eG) | (dH & ~eA)), D, E))
    poser(4, E)
    poser(5, np.where(m((bF & ~eI) | (hF & ~eC)), F, E))
    poser(6, np.where(m(dH), D, E))
    poser(7, np.where(m((dH & ~eI) | (hF & ~eG)), H, E))
    poser(8, np.where(m(hF), F, E))
    return Image.fromarray(sortie)


# --- banque de tuiles ------------------------------------------------------


def ecrire_banque(chemin: Path, tuiles: dict[tuple[int, int], Image.Image]) -> None:
    """Format `.tile` de PMDO : entete + table (x, y, offset) + PNG concatenes."""
    elements = sorted(tuiles.items(), key=lambda kv: (kv[0][1], kv[0][0]))
    entete = struct.pack("<ii", TUILE, len(elements))
    table, corps = b"", b""
    position = 8 + 16 * len(elements)
    for (tx, ty), im in elements:
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        png = buf.getvalue()
        table += struct.pack("<iiq", tx, ty, position)
        corps += struct.pack("<q", len(png)) + png
        position += 8 + len(png)
    chemin.write_bytes(entete + table + corps)


def recompiler(art: Image.Image) -> tuple[dict, int]:
    """Decoupe l'art en tuiles 8x8 et renvoie (tuiles, index par case)."""
    nx, ny = art.width // TUILE, art.height // TUILE
    tuiles: dict[tuple[int, int], Image.Image] = {}
    empreintes: dict[bytes, tuple[int, int]] = {}
    index: dict[tuple[int, int], tuple[int, int]] = {}
    px = art.load()
    for cy in range(ny):
        for cx in range(nx):
            bloc = art.crop((cx * TUILE, cy * TUILE, cx * TUILE + TUILE, cy * TUILE + TUILE))
            cle = bloc.tobytes()
            if cle in empreintes:
                index[(cx, cy)] = empreintes[cle]
                continue
            position = (len(tuiles) % COLONNES, len(tuiles) // COLONNES)
            tuiles[position] = bloc
            empreintes[cle] = position
            index[(cx, cy)] = position
    return tuiles, len(tuiles)


def cellule(tx: int, ty: int, planche: str) -> dict:
    return {"AutoTileset": "", "Associates": [],
            "Layers": [{"Frames": [{"Sheet": planche,
                                    "TexLoc": {"X": tx, "Y": ty}}],
                        "FrameLength": 60}],
            "NeighborCode": -1}


CELLULE_VIDE = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}


# --- commandes -------------------------------------------------------------


def diagnostic() -> int:
    """Dit si la banque de l'Accueil est nette, sans rien modifier."""
    source = Image.open(SOURCE_1X).convert("RGBA")
    attendu = scale3x(source)
    blocs = set()
    for cy in range(attendu.height // TUILE):
        for cx in range(attendu.width // TUILE):
            blocs.add(attendu.crop((cx * TUILE, cy * TUILE,
                                    cx * TUILE + TUILE, cy * TUILE + TUILE)).tobytes())

    sys.path.insert(0, str(RACINE / "tools"))
    from lib_tiles import read_tilesheet

    _, tuiles = read_tilesheet(BANQUE)
    nettes = sum(1 for im in tuiles.values() if im.tobytes() in blocs)
    total = len(tuiles)
    part = nettes / total * 100 if total else 0.0
    print(f"source 1x      : {source.size[0]}x{source.size[1]}, "
          f"{len(np.unique(np.asarray(source).reshape(-1, 4), axis=0))} couleurs")
    print(f"banque actuelle: {total} tuiles, dont {nettes} blocs exacts de "
          f"l'agrandissement net ({part:.1f} %)")
    if part > 95.0:
        print("=> la banque de l'Accueil est nette.")
        return 0
    print("=> la banque est interpolee (Lanczos) : relancer avec --apply.")
    return 1


def regenerer_fenetres() -> int:
    """Reecrit les 8 `.dir` de fenetres de l'Accueil en Scale3x.

    Le build officiel les agrandissait x3 en LANCZOS puis appliquait un
    « sharpen » local : 15 164 couleurs pour 144x264 px, un bruit de degrade
    sur chaque vitre.  Scale3x redonne une image nette a 171 couleurs.
    La pre-compensation d'ambiance (`SetDestinyAmbiance`) est conservee.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_guilde", BUILD)
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    compte = 0
    for slot in manifest["fenetres_par_salle"]["01_accueil"]:
        cote = slot["slot"]
        for amb in build.AMBIANCES:
            src = Image.open(slot["ambiances"][amb]["png"]).convert("RGBA")
            up = scale3x(src)
            comp = build.precompensate_window_for_engine(up, amb)
            nom = f"Guilde_Fenetre_Accueil_{cote}_{amb.capitalize()}.dir"
            build.write_dir(RACINE / "game/Content/Object" / nom,
                            comp, up.width, up.height, 0, 1)
            compte += 1
            print(f"  {nom:44s} {up.width}x{up.height} "
                  f"{len(np.unique(np.asarray(up).reshape(-1, 4), axis=0))} couleurs")
    return compte


def appliquer() -> int:
    source = Image.open(SOURCE_1X).convert("RGBA")
    art = scale3x(source)
    print(f"agrandissement Scale3x : {source.size[0]}x{source.size[1]} -> "
          f"{art.size[0]}x{art.size[1]}")

    tuiles, nb = recompiler(art)
    ecrire_banque(BANQUE, tuiles)
    print(f"banque recompilee : {nb} tuiles uniques "
          f"({BANQUE.stat().st_size / 1e6:.1f} Mo)")

    # index (case de la carte) -> (tuile de la planche)
    index = {}
    empreintes = {}
    for cy in range(art.height // TUILE):
        for cx in range(art.width // TUILE):
            bloc = art.crop((cx * TUILE, cy * TUILE,
                             cx * TUILE + TUILE, cy * TUILE + TUILE))
            cle = bloc.tobytes()
            if cle not in empreintes:
                empreintes[cle] = (len(empreintes) % COLONNES,
                                   len(empreintes) // COLONNES)
            index[(cx, cy)] = empreintes[cle]

    d = json.loads(GROUND.read_text(encoding="utf-8-sig"))
    o = d["Object"]
    nx, ny = len(o["obstacles"]), len(o["obstacles"][0])
    assert (nx, ny) == (art.width // TUILE, art.height // TUILE), \
        f"carte {nx}x{ny} vs art {art.width // TUILE}x{art.height // TUILE}"

    # On preserve le calque `Supports` : il porte les racines du premier plan,
    # qui doivent passer DEVANT les personnages.  Les cases qu'il occupait
    # recoivent la tuile nette et sont retirees du calque de fond, si bien que
    # la composition reste exactement l'art -- sans perdre la profondeur.
    support = CALQUES_FUSIONNES[-1]
    cases_supports = set()
    for cx, colonne in enumerate(o["Layers"][support]["Tiles"]):
        for cy, cell in enumerate(colonne):
            if cell.get("Layers"):
                cases_supports.add((cx, cy))
    print(f"  cases du calque Supports conservees : {len(cases_supports)}")

    fond, avant = CALQUES_FUSIONNES[0], CALQUES_FUSIONNES[:-1]
    for li in CALQUES_FUSIONNES:
        if li == fond:
            o["Layers"][li]["Tiles"] = [
                [dict(CELLULE_VIDE) if (cx, cy) in cases_supports
                 else cellule(*index[(cx, cy)], "Destiny_Guilde_Accueil")
                 for cy in range(ny)]
                for cx in range(nx)
            ]
        elif li == support:
            o["Layers"][li]["Tiles"] = [
                [cellule(*index[(cx, cy)], "Destiny_Guilde_Accueil")
                 if (cx, cy) in cases_supports else dict(CELLULE_VIDE)
                 for cy in range(ny)]
                for cx in range(nx)
            ]
        else:
            o["Layers"][li]["Tiles"] = [
                [dict(CELLULE_VIDE) for _ in range(ny)] for _ in range(nx)
            ]
        etat = ("premier plan" if li == support else
                "rempli" if li == fond else "vide")
        print(f"  calque {li} {o['Layers'][li]['Name']!r:24s} {etat}")

    # format compact : le ground d'origine est sur une seule ligne (18,8 Mo) ;
    # indent=1 le ferait doubler de volume sans rien apporter au moteur.
    GROUND.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    print(f"ground reecrit : {GROUND.stat().st_size / 1e6:.1f} Mo")

    print("fenetres de l'Accueil :")
    regenerer_fenetres()
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.apply:
        sys.exit(appliquer())
    sys.exit(diagnostic())
