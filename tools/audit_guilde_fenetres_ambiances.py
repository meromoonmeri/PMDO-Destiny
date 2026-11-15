#!/usr/bin/env python3
"""AUDIT (lecture seule) — fenêtres et jeux de lumière de la Guilde Destiny.

Vérifie, salle par salle et ambiance par ambiance (`jour`, `aube`, `crepuscule`,
`nuit`) :

  A. Couverture    — chaque fenêtre déclarée dans `guilde_destiny_decors.FENETRES`
                     possède ses 4 `.dir` d'ambiance.
  B. Intégrité     — format `.dir` valide et dimensions == emplacement déclaré.
  C. Variantes     — les 4 ambiances sont réellement distinctes (aucune copie).
  D. Jeu de lumière— la vitre est identifiée comme les pixels qui changent entre
                     `jour` et `nuit`, puis on mesure sa luminance APRÈS le filtre
                     moteur `WorldAmbianceTint` (GroundMap.cs), comparée à celle
                     de la salle. Contrôle de monotonie jour > aube > crépuscule
                     > nuit et du maintien d'un contraste vitre/salle la nuit.
  E. Câblage       — les 15 `init.lua` appellent `AppliquerAmbianceEtFenetres`
                     avec le bon identifiant de salle.

Sortie : rapport JSON + résumé console. Aucune écriture dans `game/`.
"""
from __future__ import annotations

import io
import json
import re
import struct
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
GAME = REPO / "game"
OUT = Path("/home/user/audit_guilde_fenetres")
DS_SRC = Path("/var/tmp/dsall")            # état 673e05b (décors de référence)
TILE = 8
AMB = ["jour", "aube", "crepuscule", "nuit"]
WORLD_TINT = {                             # GroundMap.cs
    "jour": np.array([255.0, 255.0, 255.0]),
    "aube": np.array([224.0, 203.0, 212.0]),
    "crepuscule": np.array([179.0, 146.0, 173.0]),
    "nuit": np.array([97.0, 118.0, 159.0]),
}
SEUIL_CONTRASTE_NUIT = 1.05                 # vitre indistinguable du mur en dessous


def lum(a: np.ndarray) -> np.ndarray:
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def lire_registre() -> dict[str, list[dict]]:
    src = (GAME / "Data/Script/destiny/guilde_destiny_decors.lua").read_text(encoding="utf-8")
    body = src.split("guilde_decors.FENETRES = {", 1)[1].split("\nguilde_decors.PORTE_SALON", 1)[0]
    slots: dict[str, list[dict]] = {}
    cur = None
    for line in body.splitlines():
        m = re.match(r"\s*\['([a-z0-9_]+)'\]\s*=\s*\{", line)
        if m:
            cur = m.group(1)
            slots[cur] = []
            continue
        mm = re.search(
            r"name = '([^']+)'.*?x = (\d+), y = (\d+), w = (\d+), h = (\d+)"
            r".*?jour = '([^']+)'.*?aube = '([^']+)'"
            r".*?crepuscule = '([^']+)'.*?nuit = '([^']+)'", line)
        if mm and cur:
            slots[cur].append(dict(
                name=mm.group(1), x=int(mm.group(2)), y=int(mm.group(3)),
                w=int(mm.group(4)), h=int(mm.group(5)),
                jour=mm.group(6), aube=mm.group(7),
                crepuscule=mm.group(8), nuit=mm.group(9)))
    return slots


def lire_dir(p: Path) -> np.ndarray:
    raw = p.read_bytes()
    ln = struct.unpack_from("<q", raw, 0)[0]
    return np.array(Image.open(io.BytesIO(raw[8:8 + ln])).convert("RGBA"), np.float32)


def charger_banc(nom: str) -> dict:
    raw = (DS_SRC / f"{nom}.tile").read_bytes()
    _ts, n = struct.unpack_from("<ii", raw, 0)
    out = {}
    for i in range(n):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + i * 16)
        l = struct.unpack_from("<q", raw, off)[0]
        out[(tx, ty)] = np.array(Image.open(io.BytesIO(raw[off + 8: off + 8 + l])).convert("RGBA"))
    return out


def _cells(o, li):
    out = {}
    for x, col in enumerate(o["Layers"][li]["Tiles"]):
        for y, cell in enumerate(col):
            tl = cell.get("Layers") or []
            if tl and tl[0].get("Frames"):
                f = tl[0]["Frames"][0]
                out[(x, y)] = (f["Sheet"], f["TexLoc"]["X"], f["TexLoc"]["Y"])
    return out


def rendu_salle(rid: str) -> np.ndarray:
    o = json.loads((DS_SRC / f"{rid}.rsground").read_text(encoding="utf-8-sig"))["Object"]
    nx = len(o["obstacles"]); ny = len(o["obstacles"][0])
    banks = {s: charger_banc(s) for s in {v[0] for li in range(len(o["Layers"]))
                                          for v in _cells(o, li).values()}}
    comp = np.zeros((ny * TILE, nx * TILE, 4), np.uint8)
    for li in range(len(o["Layers"])):
        layer = np.zeros_like(comp)
        for (x, y), (sh, tx, ty) in _cells(o, li).items():
            layer[y * TILE:(y + 1) * TILE, x * TILE:(x + 1) * TILE] = banks[sh][(tx, ty)]
        a = layer[..., 3:4].astype(np.float32) / 255.0
        comp[..., :3] = (layer[..., :3] * a + comp[..., :3] * (1 - a)).astype(np.uint8)
        comp[..., 3] = np.maximum(comp[..., 3], layer[..., 3])
    return comp.astype(np.float32)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    slots = lire_registre()
    rooms = [p.stem for p in sorted(DS_SRC.glob("guilde_destiny_*.rsground"))]
    obj_dir = GAME / "Content/Object"

    rapport = {"salles": [], "anomalies": [], "avertissements": [], "resume": {}}
    n_dir = 0
    n_fen = 0

    for rid in rooms:
        comp = rendu_salle(rid)
        masque = comp[..., 3] > 0
        lum_salle = {a: float(lum(np.clip(comp[..., :3] * (WORLD_TINT[a] / 255.0), 0, 255))[masque].mean())
                     for a in AMB}
        init = (GAME / f"Data/Script/destiny/ground/{rid}/init.lua").read_text(encoding="utf-8")
        salle = {
            "id": rid,
            "appels_decors": init.count("AppliquerAmbianceEtFenetres"),
            "id_transmis_correct": f"'{rid}'" in init,
            "lum_salle": {a: round(v, 1) for a, v in lum_salle.items()},
            "monotone": all(lum_salle[AMB[i]] > lum_salle[AMB[i + 1]] for i in range(3)),
            "fenetres": [],
        }
        for s in slots.get(rid, []):
            n_fen += 1
            arrs, manquants = {}, []
            for a in AMB:
                p = obj_dir / f"{s[a]}.dir"
                if p.is_file():
                    arrs[a] = lire_dir(p)
                    n_dir += 1
                else:
                    manquants.append(s[a])
            fen = {"name": s["name"], "x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"],
                   "jour": s["jour"], "aube": s["aube"], "crepuscule": s["crepuscule"],
                   "nuit": s["nuit"]}
            if manquants:
                rapport["anomalies"].append(f"{rid}/{s['name']} : .dir manquant {manquants}")
                fen["complet"] = False
                salle["fenetres"].append(fen)
                continue
            fen["complet"] = True
            tailles = {a: list(arrs[a].shape[1::-1]) for a in AMB}
            fen["tailles"] = tailles
            fen["taille_ok"] = all(tuple(t) == (s["w"], s["h"]) for t in tailles.values())
            if not fen["taille_ok"]:
                rapport["anomalies"].append(f"{rid}/{s['name']} : tailles {tailles} != {s['w']}x{s['h']}")

            diffs = {}
            for i in range(4):
                for j in range(i + 1, 4):
                    a, b = AMB[i], AMB[j]
                    if arrs[a].shape != arrs[b].shape:
                        diffs[f"{a}/{b}"] = None
                        continue
                    d = np.abs(arrs[a][..., :3] - arrs[b][..., :3]).max(axis=2)
                    diffs[f"{a}/{b}"] = int((d > 8).sum())
            fen["pixels_differents"] = diffs
            if any(v == 0 for v in diffs.values() if v is not None):
                rapport["anomalies"].append(f"{rid}/{s['name']} : deux ambiances identiques")

            # vitre = pixels qui changent entre jour et nuit (le cadre ne change pas)
            base = arrs["jour"]
            vitre = (np.abs(arrs["nuit"][..., :3] - base[..., :3]).max(axis=2) > 6) & (base[..., 3] > 0)
            fen["px_vitre"] = int(vitre.sum())
            if not vitre.any():
                rapport["avertissements"].append(f"{rid}/{s['name']} : aucune vitre détectée")
                salle["fenetres"].append(fen)
                continue
            vit = {}
            for a in AMB:
                eff = np.clip(arrs[a][..., :3] * (WORLD_TINT[a] / 255.0)[None, None, :], 0, 255)
                vit[a] = float(lum(eff)[vitre].mean())
            fen["lum_vitre"] = {a: round(v, 1) for a, v in vit.items()}
            fen["contraste_vitre_salle"] = {a: round(vit[a] / max(1e-6, lum_salle[a]), 2) for a in AMB}
            fen["vitre_monotone"] = all(vit[AMB[i]] > vit[AMB[i + 1]] for i in range(3))
            if not fen["vitre_monotone"]:
                rapport["anomalies"].append(f"{rid}/{s['name']} : vitre non monotone sur les ambiances")
            c = fen["contraste_vitre_salle"]["nuit"]
            fen["ressort_la_nuit"] = c >= SEUIL_CONTRASTE_NUIT
            if not fen["ressort_la_nuit"]:
                rapport["avertissements"].append(
                    f"{rid}/{s['name']} : contraste vitre/salle la nuit = {c} (< {SEUIL_CONTRASTE_NUIT})")
            salle["fenetres"].append(fen)
        if salle["appels_decors"] == 0:
            rapport["anomalies"].append(f"{rid} : aucun appel à AppliquerAmbianceEtFenetres")
        if not salle["id_transmis_correct"]:
            rapport["anomalies"].append(f"{rid} : identifiant de salle non transmis")
        if not salle["monotone"]:
            rapport["anomalies"].append(f"{rid} : la salle ne s'assombrit pas de façon monotone")
        rapport["salles"].append(salle)

    # F. Contrôles statiques du câblage d'ambiance
    decors = (GAME / "Data/Script/destiny/guilde_destiny_decors.lua").read_text(encoding="utf-8")
    meteo = (GAME / "Data/Script/destiny/meteo_reverie.lua").read_text(encoding="utf-8")
    scripts = list((GAME / "Data/Script/destiny").rglob("*.lua"))
    ecritures = [str(f.relative_to(GAME)) for f in scripts
                 if "GuildeAmbiance" in f.read_text(encoding="utf-8", errors="ignore")
                 and re.search(r"GuildeAmbiance\s*=", f.read_text(encoding="utf-8", errors="ignore"))]
    rapport["cablage"] = {
        "GuildeAmbiance_lu": "SV.Destiny.GuildeAmbiance" in decors,
        "GuildeAmbiance_ecrit_par": ecritures,
        "meteo_ignore_interieurs": "not exterieurs[map.AssetName]" in meteo,
        "reevaluation": [m for m in ("Init", "Enter", "GameLoad")
                         if all(m in (GAME / f"Data/Script/destiny/ground/{r}/init.lua").read_text(encoding="utf-8")
                                for r in rooms)],
    }
    if not ecritures:
        rapport["avertissements"].append(
            "SV.Destiny.GuildeAmbiance est lu mais jamais écrit : l'override d'ambiance "
            "par salle est inopérant (l'ambiance vient toujours de meteo_reverie.Moment()).")
    if "not exterieurs[map.AssetName]" in meteo:
        rapport["avertissements"].append(
            "meteo.Appliquer() sort immédiatement pour les intérieurs : pas de mise à jour "
            "en direct de l'ambiance d'une salle occupée (relue à Init/Enter/GameLoad).")
    rapport["resume"]["avertissements"] = len(rapport["avertissements"])

    sans = [s["id"] for s in rapport["salles"] if not s["fenetres"]]
    rapport["salles_sans_fenetre"] = sans
    rapport["resume"] = {
        "salles": len(rooms),
        "salles_avec_fenetres": len(rooms) - len(sans),
        "salles_sans_fenetre": len(sans),
        "fenetres_declarees": n_fen,
        "fichiers_dir_attendus": n_fen * 4,
        "fichiers_dir_trouves": n_dir,
        "complet_4_ambiances": sum(1 for s in rapport["salles"] for f in s["fenetres"] if f.get("complet")),
        "tailles_ok": sum(1 for s in rapport["salles"] for f in s["fenetres"] if f.get("taille_ok")),
        "variantes_distinctes": sum(1 for s in rapport["salles"] for f in s["fenetres"]
                                    if f.get("pixels_differents") and
                                    all(v and v > 0 for v in f["pixels_differents"].values())),
        "vitres_ressortent_la_nuit": sum(1 for s in rapport["salles"] for f in s["fenetres"]
                                         if f.get("ressort_la_nuit")),
        "anomalies": len(rapport["anomalies"]),
        "avertissements": len(rapport["avertissements"]),
    }
    (OUT / "audit_fenetres.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rapport["resume"], ensure_ascii=False, indent=1))
    for a in rapport["anomalies"]:
        print("  ANOMALIE :", a)
    for a in rapport["avertissements"]:
        print("  AVERTISSEMENT :", a)
    return 0 if not rapport["anomalies"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
