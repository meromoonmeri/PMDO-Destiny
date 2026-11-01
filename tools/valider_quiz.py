#!/usr/bin/env python3
"""Validation ciblée du quiz de personnalité Destiny.

Contrôle, sans lancer PMDO :
  * 20 questions synchronisées en JSON, réponses de 2 à 5 choix ;
  * aucun compteur de progression dans les textes visibles ;
  * les 16 natures gagnent leur test ciblé ;
  * chaque starter conclu a ses quatre calques VFX transparents
    (particules, halo, ondes et étoile en 73 poses), sans fond de secours ;
  * format binaire des DirSheet et alpha prémultiplié des sprites ;
  * présence du suivi de la souris, du clic droit, du portrait et de la
    phrase finale dans le Lua.
"""
from __future__ import annotations

import io
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
CONFIG = GAME / "Data/quiz_personnalite_config.json"
NATURES = GAME / "Data/quiz_personnalite_natures.json"
INIT = GAME / "Data/Script/destiny/ground/personality_test/init.lua"
DATA_LUA = GAME / "Data/Script/destiny/ground/personality_test/quiz_data.lua"
PARTICLE_DIR = GAME / "Content/Particle"
OBJECT_DIR = GAME / "Content/Object"

sys.path.insert(0, str(ROOT / "tools"))
import generer_quiz_destiny as gen  # noqa: E402

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    print(("PASS " if condition else "FAIL ") + message)
    if not condition:
        failures.append(message)


def read_dirsheet(path: Path):
    data = path.read_bytes()
    (png_len,) = struct.unpack_from("<q", data, 0)
    if len(data) != 8 + png_len + 16:
        raise ValueError(f"{path.name}: longueur DirSheet incohérente")
    png = data[8:8 + png_len]
    trailer = struct.unpack_from("<iiii", data, 8 + png_len)
    with Image.open(io.BytesIO(png)) as im:
        atlas = im.copy()
    return atlas, trailer


def frame_alpha_sum(atlas: Image.Image, frame: int, tile_w: int, tile_h: int) -> int:
    cols = atlas.width // tile_w
    x = (frame % cols) * tile_w
    y = (frame // cols) * tile_h
    tile = atlas.crop((x, y, x + tile_w, y + tile_h)).convert("RGBA")
    return int(np.asarray(tile)[..., 3].sum())


def premultiplied_ok(atlas: Image.Image) -> bool:
    arr = np.asarray(atlas.convert("RGBA")).astype(np.int16)
    alpha = arr[..., 3]
    # Tolérance +1 pour les arrondis d'écriture PNG.
    return bool(np.all(arr[..., :3] <= alpha[..., None] + 1))


def visible_lua_without_comments(path: Path) -> str:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        out.append(line)
    return "\n".join(out)


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))["Object"]
    natures_doc = json.loads(NATURES.read_text(encoding="utf-8-sig"))["Object"]
    questions = config.get("Questions", [])
    starters = {s["Id"]: s for s in config.get("Starters", [])}
    natures = [n for n in natures_doc.get("Natures", []) if n.get("Index") != -1]
    order = [n["NomEN"].lower() for n in natures]

    check(len(questions) == 20, f"20 questions ({len(questions)})")
    counts = [len(q.get("Choix", [])) for q in questions]
    check(all(2 <= c <= 5 for c in counts), f"réponses entre 2 et 5 choix : {counts}")
    check(2 in counts and 5 in counts, "au moins une question à 2 choix et une à 5 choix")

    question_texts = [q.get("Texte", "") for q in questions]
    choice_texts = [c.get("Texte", "") for q in questions for c in q.get("Choix", [])]
    check(max(map(len, question_texts), default=0) <= 65, "questions assez courtes pour la boîte PMDO")
    check(max(map(len, choice_texts), default=0) <= 55, "réponses assez courtes pour un menu à 5 choix")

    visible = "\n".join(question_texts + choice_texts)
    counter_re = re.compile(r"(?<!\d)(?:\(?\s*\d+\s*/\s*(?:15|20)\s*\)?)(?!\d)")
    check(counter_re.search(visible) is None, "aucun compteur dans les questions/réponses")

    check(len(natures) == 16, f"16 natures ({len(natures)})")
    check(all(n.get("DescriptionFR") for n in natures), "description FR pour chaque nature")

    report = gen.audit(order, random_runs=5000)
    check(report["questions"] == 20, "le générateur contient aussi 20 questions")
    check(all(report["test_cible_reussi"].values()), "chaque nature gagne son test ciblé")
    theoretical = report["score_max_theorique"]
    check(max(theoretical.values()) - min(theoretical.values()) <= 4,
          f"scores théoriques resserrés ({min(theoretical.values())}–{max(theoretical.values())})")

    json_texts = [(q["texte"], [(t, p) for t, p in q["choix"]]) for q in gen.QUESTIONS]
    config_texts = [
        (q["Texte"], [(c["Texte"], c["Points"]) for c in q["Choix"]])
        for q in questions
    ]
    check(json_texts == config_texts, "généateur et JSON synchronisés")

    mapping = {m["Nature"]: m["Starter"] for m in config.get("Mapping", [])}
    check(set(mapping) == set(order), "mapping complet des 16 natures")
    missing_assets = []
    needed_types = set()
    for starter_id in mapping.values():
        starter = starters.get(starter_id)
        if starter is None:
            missing_assets.append(f"starter absent: {starter_id}")
            continue
        asset_type = starter.get("EtoileType")
        needed_types.add(asset_type)
    check(not missing_assets, f"starters conclus et types d'étoile présents ({len(needed_types)} types)")

    missing_fluid = []
    for asset_type in sorted(t for t in needed_types if t):
        for path in (
            PARTICLE_DIR / f"Quiz_Etoile_Particule_{asset_type}.dir",
            OBJECT_DIR / f"Quiz_Etoile_Halo_{asset_type}.dir",
            OBJECT_DIR / f"Quiz_Etoile_Ondes_{asset_type}.dir",
            OBJECT_DIR / f"Quiz_Etoile_Forme_{asset_type}.dir",
        ):
            if not path.exists():
                missing_fluid.append(str(path))
    check(not missing_fluid, "particules, halo, ondes et étoile présents pour chaque type conclu")

    legacy_backgrounds = sorted((GAME / "Content/BG").glob("Quiz_Etoile*.dir"))
    check(not legacy_backgrounds, "aucun ancien fond plein écran du quiz conservé")

    fluid_specs = []
    for asset_type in sorted(t for t in needed_types if t):
        fluid_specs.extend([
            (PARTICLE_DIR / f"Quiz_Etoile_Particule_{asset_type}.dir", (144, 96), (24, 24, 0, 24), True),
            (OBJECT_DIR / f"Quiz_Etoile_Halo_{asset_type}.dir", (1728, 1728), (192, 192, 0, 81), True),
            (OBJECT_DIR / f"Quiz_Etoile_Ondes_{asset_type}.dir", (1344, 1344), (224, 224, 0, 36), True),
            (OBJECT_DIR / f"Quiz_Etoile_Forme_{asset_type}.dir", (1536, 2160), (192, 216, 0, 73), True),
        ])
    bad_fluid = []
    bad_premultiply = []
    fluid_atlases = {}
    for path, atlas_size, trailer_expected, needs_premultiply in fluid_specs:
        try:
            im, trailer = read_dirsheet(path)
            fluid_atlases[path.name] = im
            if im.size != atlas_size or trailer != trailer_expected:
                bad_fluid.append(path.name)
            if needs_premultiply and not premultiplied_ok(im):
                bad_premultiply.append(path.name)
        except Exception:
            bad_fluid.append(path.name)
    check(not bad_fluid, "formats DirSheet fluides : 24 poses particule, 81 halo, 36 ondes, 73 étoile" +
          (f" — KO: {bad_fluid}" if bad_fluid else ""))
    check(not bad_premultiply, "alpha prémultiplié des sprites fluides" +
          (f" — KO: {bad_premultiply}" if bad_premultiply else ""))

    growth_ok = True
    for asset_type in sorted(t for t in needed_types if t):
        try:
            halo = fluid_atlases[f"Quiz_Etoile_Halo_{asset_type}.dir"]
            star = fluid_atlases[f"Quiz_Etoile_Forme_{asset_type}.dir"]
            halo_values = [frame_alpha_sum(halo, f, 192, 192) for f in (0, 20, 40, 60, 80)]
            star_values = [frame_alpha_sum(star, f, 192, 216) for f in (0, 14, 28, 42, 56, 72)]
            if not (star_values[0] == 0 and
                    all(b > a for a, b in zip(halo_values, halo_values[1:])) and
                    all(b > a for a, b in zip(star_values, star_values[1:]))):
                growth_ok = False
        except Exception:
            growth_ok = False
    check(growth_ok, "halo et matérialisation de l'étoile progressent sans pose vide intermédiaire")

    init = INIT.read_text(encoding="utf-8")
    init_visible = visible_lua_without_comments(INIT)
    data_lua = DATA_LUA.read_text(encoding="utf-8")
    check("INPUT_RIGHT_MOUSE = 30" in init, "clic droit natif RightMouse (id 30)")
    check("GAME:IsInputDown" in init, "lecture du maintien frame par frame")
    check("MetaInputManager.MouseLoc" in init and "GraphicsManager.WindowZoom" in init,
          "point d'ancrage lu à la souris et converti en 320×240")
    check("RogueEssence.Menu.ScriptableMenu" in init and "UI:SetCustomMenu(hote)" in init,
          "menu scriptable mis à jour à chaque frame")
    check("Quiz_Etoile_Particule_" in init and "Quiz_Etoile_Halo_" in init and
          "Quiz_Etoile_Ondes_" in init and "Quiz_Etoile_Forme_" in init,
          "particules, halo, ondes et étoile dessinés séparément au point du clic")
    check("FLUIDE_CONVERGENCE = 0.70" in init and "etat.progression > FLUIDE_CONVERGENCE" in init,
          "l'étoile ne se matérialise qu'après la convergence des particules")
    check("StartFrame = pose_etoile" in init and "EndFrame = pose_etoile" in init,
          "parcours fluide des poses de matérialisation et de scintillement")
    check("clic_droit and not etat.clic_droit_precedent" in init,
          "ancrage immédiat au point où le clic droit commence")
    check("UI:WaitShowBG" not in init and "UI:WaitHideBG" not in init,
          "le fond de base du quiz n'est jamais remplacé")
    check("UI:TextPopUp" not in init,
          "aucune consigne ni symbole de souris en surimpression en bas")
    check("clic droit[color] sans le relâcher" in init,
          "la consigne du clic droit est donnée dans la boîte de dialogue")
    check("Quelqu’un comme toi serait " in init, "phrase finale demandée")
    check("UI:SetSpeaker('', false, starter.espece, starter.forme" in init,
          "portrait du starter avant sa création")
    check("nom_colore_type(starter)" in init, "nom coloré selon le/les type(s)")
    check("UI:BeginChoiceMenu('('" not in init and 'UI:BeginChoiceMenu("("' not in init,
          "aucun préfixe compteur devant les questions")
    check(counter_re.search(init_visible) is None, "aucun compteur visible dans le Lua exécutable")
    check("calculer_nature(scores, historique)" in init, "départage par réponses récentes")
    check(data_lua.count("\n  { texte = ") == 20, "20 questions dans quiz_data.lua")

    combined = (init + data_lua + CONFIG.read_text(encoding="utf-8") +
                NATURES.read_text(encoding="utf-8"))
    check("Halcyon" not in combined and "Remixed" not in combined,
          "aucune mention interdite dans les fichiers du quiz")

    if failures:
        print(f"\nÉCHEC : {len(failures)} contrôle(s)")
        return 1
    print("\nQuiz Destiny : validation complète réussie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
