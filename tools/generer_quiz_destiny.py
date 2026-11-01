#!/usr/bin/env python3
"""Génère le quiz de personnalité Destiny et l'animation de l'étoile.

Source unique pour :
  * game/Data/quiz_personnalite_config.json (20 questions) ;
  * game/Data/quiz_personnalite_natures.json (descriptions FR) ;
  * game/Data/Script/destiny/ground/personality_test/quiz_data.lua ;
  * game/Content/BG/Quiz_Etoile_<Type>_<étape>.dir
    (ancien secours 320×240, 4 poses, étapes 0 à 4) ;
  * game/Content/BG/Quiz_Etoile_Fond.dir (ciel 320×240) ;
  * game/Content/Particle/Quiz_Etoile_Particule_<Type>.dir ;
  * game/Content/Object/Quiz_Etoile_Halo_<Type>.dir ;
  * game/Content/Object/Quiz_Etoile_Forme_<Type>.dir
    (matérialisation fluide en 61 poses, pilotée frame par frame dans le Lua).

Les questions sont des textes originaux, dans l'esprit des quiz de
personnalité PMD : situations concrètes, réponses de 2 à 5 choix, quelques
oui/non et aucune nature affichée au joueur. Le compteur de question est
volontairement absent des données comme du script.

L'étoile utilise le badge blanc déjà présent dans la quest, réduit au plus
proche voisin et reteint selon le type principal du starter obtenu. Les fonds
sont entièrement opaques : aucun problème d'alpha prémultiplié dans les .dir.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import struct
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
CONFIG_PATH = GAME / "Data/quiz_personnalite_config.json"
NATURES_PATH = GAME / "Data/quiz_personnalite_natures.json"
LUA_PATH = GAME / "Data/Script/destiny/ground/personality_test/quiz_data.lua"
BADGE_PATH = GAME / "Content/UI/quiz_badges/badge_etoile_blanc.png"
BG_DIR = GAME / "Content/BG"
PARTICLE_DIR = GAME / "Content/Particle"
OBJECT_DIR = GAME / "Content/Object"
PREVIEW_DIR = ROOT / "docs/quiz_etoile_apercus"

SCREEN_W, SCREEN_H = 320, 240
STAGES = 5
FRAMES_PER_STAGE = 4

# Animation fluide pilotée par ScriptableMenu dans le Lua : les particules
# sont des éléments séparés déplacés à chaque frame, tandis que halo et
# étoile possèdent assez de poses pour être parcourues sans palier visible.
PARTICLE_TILE = 16
PARTICLE_FRAMES = 16
GLOW_TILE = 160
GLOW_FRAMES = 41
STAR_TILE_W, STAR_TILE_H = 160, 184
STAR_FINAL_W = 126
STAR_FRAMES = 61

# ---------------------------------------------------------------------------
# Questions — nature principale +3 (+2 pour les deux oui/non), nuance +1.
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "texte": "Le soleil se lève sur une journée libre. Tu commences par…",
        "choix": [
            ("Préparer mon sac et tracer mon plan.", {"hardy": 3, "docile": 1}),
            ("Sortir avant même d’avoir fini de manger.", {"hasty": 3, "bold": 1}),
            ("Regarder le ciel un moment, sans me presser.", {"relaxed": 3, "quiet": 1}),
            ("Suivre la première idée qui me traverse l’esprit.", {"rash": 3, "impish": 1}),
        ],
    },
    {
        "texte": "On te dit souvent que tu parles trop vite ?",
        "choix": [
            ("Oui… mes idées déboulent avant mes mots.", {"hasty": 2, "rash": 1}),
            ("Non, je prends le temps de choisir mes mots.", {"quiet": 2, "hardy": 1}),
        ],
    },
    {
        "texte": "Ton ami trébuche de façon spectaculaire devant tout le monde.",
        "choix": [
            ("Je l’aide à se relever tout de suite.", {"brave": 3, "docile": 1}),
            ("j'éclate de rire, puis je lui tends la main.", {"impish": 3, "naive": 1}),
            ("Je vérifie d’abord s’il s’est fait mal.", {"timid": 3, "docile": 1}),
            ("Je lance une blague pour détendre l’ambiance.", {"naive": 3, "bold": 1}),
            ("Je fais semblant de trébucher aussi.", {"rash": 3, "impish": 1}),
        ],
    },
    {
        "texte": "Demain, un examen très important t’attend.",
        "choix": [
            ("Je révise sérieusement, étape par étape.", {"hardy": 3, "brave": 1}),
            ("Je bachote au dernier moment.", {"hasty": 3, "rash": 1}),
            ("Je me couche tôt : tête reposée, esprit clair.", {"calm": 3, "relaxed": 1}),
            ("Je compte sur mon intuition.", {"naive": 3, "quirky": 1}),
            ("Je prépare une excuse très convaincante…", {"sassy": 3, "impish": 1}),
        ],
    },
    {
        "texte": "Un coffre cabossé dépasse du sable.",
        "choix": [
            ("Je l’ouvre, évidemment !", {"brave": 3, "rash": 1}),
            ("J’inspecte les alentours et je cherche un piège.", {"quiet": 3, "timid": 1}),
            ("Je le secoue pour écouter ce qu’il contient.", {"naive": 3, "hasty": 1}),
            ("J’appelle mes amis pour l’ouvrir ensemble.", {"jolly": 3, "bold": 1}),
            ("Je le laisse : il appartient peut-être à quelqu’un.", {"docile": 3, "calm": 1}),
        ],
    },
    {
        "texte": "As-tu déjà rêvé qu’un trésor dormait juste sous tes pieds ?",
        "choix": [
            ("Oui, et j’ai même eu envie de creuser !", {"naive": 2, "quirky": 1}),
            ("Non, je préfère les choses que je peux voir.", {"relaxed": 2, "hardy": 1}),
        ],
    },
    {
        "texte": "Dans un donjon, ton équipe arrive à une bifurcation.",
        "choix": [
            ("Je propose un cap et je passe devant.", {"bold": 3, "brave": 1}),
            ("Je demande l’avis de chacun.", {"docile": 3, "jolly": 1}),
            ("Je choisis le passage le plus étroit et mystérieux.", {"impish": 3, "brave": 1}),
            ("J’écoute, j’observe, puis je décide.", {"quiet": 3, "timid": 1}),
            ("Pile ou face. Le destin choisira !", {"quirky": 3, "rash": 1}),
        ],
    },
    {
        "texte": "Alors que tu rêvassais, un ami t’asperge d’eau par surprise.",
        "choix": [
            ("Bataille d’eau générale !", {"jolly": 3, "impish": 1}),
            ("Je prépare ma revanche en secret.", {"sassy": 3, "impish": 1}),
            ("J’éclate de rire. Bien joué !", {"naive": 3, "jolly": 1}),
            ("Je vais me sécher, tranquillement.", {"relaxed": 3, "calm": 1}),
        ],
    },
    {
        "texte": "Un Pokémon plus grand embête un plus petit dans la rue.",
        "choix": [
            ("Je m’interpose immédiatement.", {"brave": 3, "bold": 1}),
            ("Je vais chercher quelqu’un de plus fort.", {"timid": 3, "docile": 1}),
            ("Je détourne son attention avec une ruse.", {"impish": 3, "sassy": 1}),
            ("J’essaie de calmer la situation par la parole.", {"calm": 3, "brave": 1}),
        ],
    },
    {
        "texte": "On te remet un énorme sac-cadeau.",
        "choix": [
            ("Je l’ouvre sur-le-champ !", {"rash": 3, "naive": 1}),
            ("Je le secoue doucement pour deviner.", {"hasty": 3, "quirky": 1}),
            ("J’attends d’être chez moi pour l’ouvrir.", {"calm": 3, "hardy": 1}),
            ("Je me demande pourquoi le mien semble différent.", {"lonely": 3, "quiet": 1}),
        ],
    },
    {
        "texte": "Quand tu es seul un moment, le silence te pèse ?",
        "choix": [
            ("Oui, je cherche vite de la compagnie.", {"lonely": 3, "timid": 1}),
            ("Non, j’aime vraiment ce calme.", {"quiet": 3, "relaxed": 1}),
            ("Seulement quand je m’ennuie.", {"hasty": 3, "jolly": 1}),
        ],
    },
    {
        "texte": "Une après-midi entière s’offre à toi. Tu choisis…",
        "choix": [
            ("Une grande sortie avec tous mes amis.", {"jolly": 3, "bold": 1}),
            ("Terminer un projet qui me tient à cœur.", {"hardy": 3, "quiet": 1}),
            ("Ne rien faire, et le faire lentement.", {"relaxed": 3, "calm": 1}),
            ("Explorer un endroit inconnu, seul.", {"lonely": 3, "brave": 1}),
            ("Inventer une activité complètement improbable.", {"quirky": 3, "impish": 1}),
        ],
    },
    {
        "texte": "Ton ami a beaucoup de retard au rendez-vous.",
        "choix": [
            ("j'attends en profitant du paysage.", {"relaxed": 3, "docile": 1}),
            ("Je regarde l’heure toutes les minutes.", {"hasty": 3, "timid": 1}),
            ("Je pars. Mon temps compte aussi.", {"bold": 3, "brave": 1}),
            ("Je m’inquiète et je vais à sa rencontre.", {"timid": 3, "docile": 1}),
            ("Je lui prépare une arrivée triomphale.", {"impish": 3, "sassy": 1}),
        ],
    },
    {
        "texte": "On te dit : « Tu es bizarre, mais vraiment drôle. »",
        "choix": [
            ("Parfait, c’est exactement moi !", {"quirky": 3, "naive": 1}),
            ("Évidemment. Je le savais déjà.", {"sassy": 3, "bold": 1}),
            ("Je ne sais pas trop comment le prendre…", {"timid": 3, "quiet": 1}),
            ("Je ris, puis je passe à autre chose.", {"jolly": 3, "relaxed": 1}),
        ],
    },
    {
        "texte": "On a une bonne et une mauvaise nouvelle pour toi.",
        "choix": [
            ("La mauvaise d’abord. Allons droit au but.", {"bold": 3, "brave": 1}),
            ("La bonne d’abord, pour garder le moral.", {"naive": 3, "relaxed": 1}),
            ("Une par une, calmement.", {"calm": 3, "quiet": 1}),
            ("Surprends-moi : choisis pour moi !", {"rash": 3, "sassy": 1}),
        ],
    },
    {
        "texte": "Une fois que tu as décidé quelque chose, tu vas jusqu’au bout ?",
        "choix": [
            ("Oui. Quand je m’engage, je tiens bon.", {"hardy": 3, "brave": 1}),
            ("Non, si une meilleure idée surgit, je change.", {"quirky": 3, "hasty": 1}),
            ("Cela dépend de ce que ressent mon équipe.", {"docile": 3, "brave": 1}),
        ],
    },
    {
        "texte": "La fête du village bat son plein.",
        "choix": [
            ("Je suis au centre de la piste !", {"jolly": 3, "hasty": 1}),
            ("Je discute avec un petit groupe.", {"docile": 3, "timid": 1}),
            ("J’observe la fête depuis un coin tranquille.", {"lonely": 3, "quiet": 1}),
            ("Je lance une farce pour briser la glace.", {"impish": 3, "bold": 1}),
            ("Je propose un toast devant tout le monde.", {"bold": 3, "sassy": 1}),
        ],
    },
    {
        "texte": "Tu découvres une fleur rare au bord du chemin.",
        "choix": [
            ("Je la cueille pour l’offrir à quelqu’un.", {"docile": 3, "jolly": 1}),
            ("Je la laisse grandir là où elle est.", {"calm": 3, "hardy": 1}),
            ("Je reviens la voir en secret, juste pour moi.", {"lonely": 3, "quiet": 1}),
            ("J’appelle tout le monde : regardez ça !", {"bold": 3, "naive": 1}),
            ("Je dessine sa forme pour ne pas l’oublier.", {"quirky": 3, "lonely": 1}),
        ],
    },
    {
        "texte": "Tu fais une énorme erreur devant toute ton équipe.",
        "choix": [
            ("Je l’assume et je répare ce que je peux.", {"hardy": 3, "brave": 1}),
            ("Je trouve une excuse… très créative.", {"sassy": 3, "impish": 1}),
            ("J’ai besoin d’un moment loin des regards.", {"timid": 3, "docile": 1}),
            ("Je rebondis immédiatement, encore plus fort.", {"rash": 3, "bold": 1}),
            ("Je respire et j’analyse ce qui s’est passé.", {"calm": 3, "hardy": 1}),
        ],
    },
    {
        "texte": "Pour toi, une belle aventure, c’est surtout…",
        "choix": [
            ("Des amis avec qui rire jusqu’au bout.", {"jolly": 3, "docile": 1}),
            ("Rester pleinement moi-même, sans me cacher.", {"sassy": 3, "lonely": 1}),
            ("Avancer même quand le cœur tremble.", {"brave": 3, "hardy": 1}),
            ("Aller à mon rythme, libre comme le vent.", {"relaxed": 3, "quirky": 1}),
            ("Trouver les lieux que personne ne remarque.", {"lonely": 3, "impish": 1}),
        ],
    },
]

DESCRIPTIONS = {
    "hardy": "Tu avances avec constance et tu termines ce que tu commences.",
    "docile": "Tu écoutes les autres et tu sais créer un climat de confiance.",
    "brave": "Quand quelque chose compte, tu trouves le courage d’agir.",
    "jolly": "Ton énergie et ton rire donnent envie aux autres de te suivre.",
    "impish": "Tu aimes les détours, les ruses et les petites étincelles de malice.",
    "naive": "Tu regardes le monde avec spontanéité et un émerveillement sincère.",
    "timid": "Tu observes avant d’agir, avec une sensibilité plus forte qu’on ne l’imagine.",
    "hasty": "Ton esprit va vite, parfois même un peu avant le reste du monde.",
    "sassy": "Tu sais qui tu es, et tu n’as pas peur de le montrer.",
    "calm": "Même sous pression, tu cherches d’abord l’équilibre.",
    "relaxed": "Tu avances sans te laisser happer par l’agitation.",
    "lonely": "Tu chéris les moments à part, là où tes pensées deviennent claires.",
    "quirky": "Tu suis une logique bien à toi, souvent là où personne n’aurait regardé.",
    "quiet": "Tu remarques les détails que les autres traversent sans les voir.",
    "rash": "Quand l’élan est là, tu fonces et tu réfléchis en chemin.",
    "bold": "Tu prends ta place naturellement et tu oses décider.",
}

# Couleurs lisibles dans la boîte de dialogue et dans l'étoile.
TYPE_INFO = {
    "Normal": ("Normal", "#DDD6C8"),
    "Plante": ("Plante", "#58C96B"),
    "Feu": ("Feu", "#FF7A45"),
    "Eau": ("Eau", "#4AA8FF"),
    "Électrik": ("Electrik", "#FFD83D"),
    "Glace": ("Glace", "#79E6F2"),
    "Combat": ("Combat", "#FF5C5C"),
    "Poison": ("Poison", "#C77DFF"),
    "Sol": ("Sol", "#D8B36A"),
    "Vol": ("Vol", "#A9C7FF"),
    "Psy": ("Psy", "#FF7EB6"),
    "Insecte": ("Insecte", "#B6D94C"),
    "Roche": ("Roche", "#C2B280"),
    "Spectre": ("Spectre", "#9A86E8"),
    "Dragon": ("Dragon", "#7C8CFF"),
    "Ténèbres": ("Tenebres", "#A99AC2"),
    "Acier": ("Acier", "#B8C7D9"),
    "Fée": ("Fee", "#FFB3D9"),
}


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def winner(scores: dict[str, int], history: list[dict[str, int]], order: list[str]) -> str:
    """Même départage que le Lua : score, puis réponses les plus récentes."""
    best = max(scores[s] for s in order)
    candidates = [s for s in order if scores[s] == best]
    for points in reversed(history):
        if len(candidates) <= 1:
            break
        local_best = max(points.get(s, 0) for s in candidates)
        candidates = [s for s in candidates if points.get(s, 0) == local_best]
    return candidates[0]


def audit(order: list[str], random_runs: int = 20000) -> dict:
    assert len(QUESTIONS) == 20, len(QUESTIONS)
    max_scores = {slug: 0 for slug in order}
    appearances = Counter()
    choice_counts = Counter()
    for q in QUESTIONS:
        assert 2 <= len(q["choix"]) <= 5, q
        choice_counts[len(q["choix"])] += 1
        for slug in order:
            max_scores[slug] += max(points.get(slug, 0) for _, points in q["choix"])
        for _, points in q["choix"]:
            assert points and all(slug in order for slug in points), points
            assert sum(points.values()) == (3 if len(q["choix"]) == 2 else 4), points
            appearances.update(points.keys())

    greedy_winners = {}
    for target in order:
        scores = {slug: 0 for slug in order}
        history = []
        for q in QUESTIONS:
            def rank(item):
                points = item[1]
                others = max((pts for slug, pts in points.items() if slug != target), default=0)
                return points.get(target, 0) * 10 - others
            _, points = max(q["choix"], key=rank)
            history.append(points)
            for slug, pts in points.items():
                scores[slug] += pts
        greedy_winners[target] = winner(scores, history, order)

    rng = random.Random(20261101)
    random_winners = Counter()
    for _ in range(random_runs):
        scores = {slug: 0 for slug in order}
        history = []
        for q in QUESTIONS:
            _, points = rng.choice(q["choix"])
            history.append(points)
            for slug, pts in points.items():
                scores[slug] += pts
        random_winners[winner(scores, history, order)] += 1

    return {
        "questions": len(QUESTIONS),
        "repartition_choix": dict(sorted(choice_counts.items())),
        "apparitions": {slug: appearances[slug] for slug in order},
        "score_max_theorique": max_scores,
        "test_cible": greedy_winners,
        "test_cible_reussi": {slug: greedy_winners[slug] == slug for slug in order},
        "simulation_aleatoire": {slug: random_winners[slug] for slug in order},
        "simulation_runs": random_runs,
    }


def lua_string(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def lua_points(points: dict[str, int]) -> str:
    return "{ " + ", ".join(f"{slug} = {pts}" for slug, pts in points.items()) + " }"


def type_fields(starter: dict) -> tuple[str, str, list[str]]:
    types = starter.get("Types") or ["Normal"]
    asset, color = TYPE_INFO[types[0]]
    colors = [TYPE_INFO[t][1] for t in types]
    return asset, color, colors


def build_data() -> tuple[dict, dict, dict]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    natures_doc = json.loads(NATURES_PATH.read_text(encoding="utf-8-sig"))
    obj = config["Object"]
    natures_obj = natures_doc["Object"]

    order = []
    for entry in natures_obj["Natures"]:
        if entry["Index"] == -1:
            continue
        slug = entry["NomEN"].lower()
        order.append(slug)
        entry["DescriptionFR"] = DESCRIPTIONS[slug]
    assert len(order) == 16

    report = audit(order)

    obj["Comment"] = (
        "Quiz de personnalité PMD Destiny — 20 questions originales dans l'esprit "
        "des quiz PMD, réponses de 2 à 5 choix sans compteur visible, 16 natures, "
        "pool starters gen 1-9 + extras, mapping nature → starter, talents et "
        "méga-évolution. La révélation finale forme une étoile pixel art colorée "
        "selon le type principal du starter pendant le maintien du clic droit."
    )
    obj["Questions"] = [
        {
            "Texte": q["texte"],
            "Choix": [
                {"Texte": text, "Points": points}
                for text, points in q["choix"]
            ],
        }
        for q in QUESTIONS
    ]

    for starter in obj["Starters"]:
        asset, color, colors = type_fields(starter)
        starter["EtoileType"] = asset
        starter["CouleurType"] = color
        starter["CouleursTypes"] = colors

    natures_obj["Comment"] = (
        "Quiz de personnalité — 16 natures. Le badge étoile de l'opening sert de "
        "base à la révélation finale ; les fonds Quiz_Etoile_<Type>_<étape>.dir "
        "sont colorés selon le type principal du starter conclu."
    )
    return config, natures_doc, report


def write_lua(config: dict, natures_doc: dict) -> None:
    obj = config["Object"]
    lines = [
        "-- Généré par tools/generer_quiz_destiny.py — NE PAS ÉDITER À LA MAIN.",
        "-- Données du quiz de personnalité PMD Destiny (20 questions, 16 natures,",
        "-- pool starters gen 1-9 + extras, mapping, couleurs de types, méga-évolution).",
        "local quiz_data = {}",
        "",
        "quiz_data.questions = {",
    ]
    for q in QUESTIONS:
        choices = []
        for text, points in q["choix"]:
            choices.append(
                "{ texte = " + lua_string(text) + ", points = " + lua_points(points) + " }"
            )
        lines.append(
            "  { texte = " + lua_string(q["texte"]) + ", choix = { " + ", ".join(choices) + " } },"
        )
    lines += ["}", "", "quiz_data.natures = {"]
    for entry in natures_doc["Object"]["Natures"]:
        if entry["Index"] == -1:
            continue
        slug = entry["NomEN"].lower()
        color = entry["Couleur"]
        lines.append(
            "  { slug = " + lua_string(slug)
            + ", fr = " + lua_string(entry["NomFR"])
            + ", en = " + lua_string(entry["NomEN"])
            + ", couleur = " + lua_string(color["Nom"])
            + ", hex = " + lua_string(color["Hex"])
            + ", description = " + lua_string(DESCRIPTIONS[slug]) + " },"
        )
    lines += ["}", "", "quiz_data.starters = {"]
    for st in obj["Starters"]:
        talents = "{ " + ", ".join(lua_string(t) for t in st.get("Talents", [])) + " }"
        types = "{ " + ", ".join(lua_string(t) for t in st.get("Types", [])) + " }"
        colors = "{ " + ", ".join(lua_string(c) for c in st["CouleursTypes"]) + " }"
        mega = lua_string(st["MegaNom"]) if st.get("Mega") else "nil"
        lines.append(
            "  [" + lua_string(st["Id"]) + "] = { espece = " + lua_string(st["Espece"])
            + ", forme = " + str(st.get("Forme", 0))
            + ", nom = " + lua_string(st["NomFR"])
            + ", gen = " + str(st["Gen"])
            + ", types = " + types
            + ", couleur_type = " + lua_string(st["CouleurType"])
            + ", couleurs_types = " + colors
            + ", etoile_type = " + lua_string(st["EtoileType"])
            + ", talents = " + talents
            + ", mega = " + mega + " },"
        )
    lines += ["}", "", "quiz_data.mapping = {"]
    for item in obj["Mapping"]:
        lines.append("  [" + lua_string(item["Nature"]) + "] = " + lua_string(item["Starter"]) + ",")
    lines += [
        "}",
        "",
        "quiz_data.mega_texte = " + lua_string(obj.get("MegaTexteFR", "MÉGA-ÉVOLUTION")),
        "return quiz_data",
        "",
    ]
    LUA_PATH.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Animation de l'étoile
# ---------------------------------------------------------------------------

def recolor_badge(source: Image.Image, color_hex: str) -> Image.Image:
    arr = np.asarray(source.convert("RGBA")).astype(np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3]
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    base = np.array(hex_rgb(color_hex), dtype=np.float32)
    colored = base * (0.30 + 0.88 * lum[..., None])
    highlight = np.clip((lum - 0.68) / 0.32, 0, 1)[..., None] * 0.78
    colored = colored * (1 - highlight) + 255.0 * highlight
    outline = lum < 0.10
    colored[outline] = np.array((18, 10, 28), dtype=np.float32)
    out = np.dstack([np.clip(colored, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_badge(white: Image.Image, colored: Image.Image, amount: float) -> Image.Image:
    w = np.asarray(white.convert("RGBA")).astype(np.float32)
    c = np.asarray(colored.convert("RGBA")).astype(np.float32)
    out = w.copy()
    out[..., :3] = w[..., :3] * (1 - amount) + c[..., :3] * amount
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def make_background(frame: int) -> Image.Image:
    yy = np.linspace(0, 1, SCREEN_H, dtype=np.float32)[:, None]
    top = np.array((5, 7, 24), dtype=np.float32)
    bottom = np.array((25, 15, 48), dtype=np.float32)
    arr = (top * (1 - yy) + bottom * yy)[:, None, :].repeat(SCREEN_W, axis=1)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(12345)
    for i in range(95):
        x, y = rng.randrange(SCREEN_W), rng.randrange(SCREEN_H)
        bright = 90 + rng.randrange(120)
        if (i + frame) % 7 == 0:
            bright = 235
            d.line((x - 2, y, x + 2, y), fill=(bright, bright, 255, 180), width=1)
            d.line((x, y - 2, x, y + 2), fill=(bright, bright, 255, 180), width=1)
        else:
            d.point((x, y), fill=(bright, bright, 255, 170))
    return im


def add_glow(im: Image.Image, center: tuple[int, int], color_hex: str, strength: float, radius: int) -> None:
    if strength <= 0:
        return
    small_w, small_h = SCREEN_W // 4, SCREEN_H // 4
    yy, xx = np.mgrid[0:small_h, 0:small_w]
    cx, cy = center[0] / 4, center[1] / 4
    dist = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.2) ** 2)
    alpha = np.clip(1 - dist / (radius / 4), 0, 1) ** 1.7
    alpha = np.round(alpha * 5) / 5 * strength * 150
    r, g, b = hex_rgb(color_hex)
    overlay = np.zeros((small_h, small_w, 4), dtype=np.uint8)
    overlay[..., 0], overlay[..., 1], overlay[..., 2], overlay[..., 3] = r, g, b, alpha.astype(np.uint8)
    glow = Image.fromarray(overlay, "RGBA").resize((SCREEN_W, SCREEN_H), Image.Resampling.NEAREST)
    im.alpha_composite(glow)


def draw_mouse_icon(im: Image.Image, color_hex: str, frame: int) -> None:
    d = ImageDraw.Draw(im, "RGBA")
    x, y, w, h = 289, 202, 20, 29
    tip = hex_rgb(color_hex) if frame % 2 == 0 else (255, 255, 255)
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=(10, 10, 18, 220), outline=(245, 245, 255, 255), width=2)
    d.line((x + w // 2, y + 2, x + w // 2, y + 11), fill=(245, 245, 255, 255), width=2)
    d.line((x + 2, y + 11, x + w - 2, y + 11), fill=(245, 245, 255, 255), width=1)
    d.rectangle((x + w // 2 + 2, y + 3, x + w - 3, y + 10), fill=(*tip, 255))


def make_stage_frames(color_hex: str, slug: str, white: Image.Image, colored: Image.Image, stage: int) -> list[Image.Image]:
    # La forme naît des étincelles : d'abord un simple germe de lumière,
    # puis une silhouette blanche à peine devinée, puis l'étoile colorée.
    widths = [46, 64, 84, 106, 126]
    opacities = [0.14, 0.30, 0.52, 0.78, 1.0]
    blends = [0.0, 0.15, 0.38, 0.70, 1.0]
    center = (160, 103)
    badge = blend_badge(white, colored, blends[stage])
    tw = widths[stage]
    th = round(tw * badge.height / badge.width)
    badge_small = badge.resize((tw, th), Image.Resampling.NEAREST)
    if opacities[stage] < 1:
        a = badge_small.getchannel("A").point(lambda v: int(v * opacities[stage]))
        badge_small.putalpha(a)

    rng = random.Random(hash((slug, "particles")) & 0xFFFFFFFF)
    particles = []
    for _ in range(92):
        particles.append((
            rng.uniform(0, math.tau),
            rng.uniform(88, 150),
            rng.uniform(-0.10, 0.10),
            rng.randrange(4),
            rng.random(),
        ))

    frames = []
    for frame in range(FRAMES_PER_STAGE):
        im = make_background(frame)
        add_glow(im, center, color_hex, [0.06, 0.16, 0.38, 0.68, 1.0][stage], [46, 62, 82, 104, 124][stage])
        d = ImageDraw.Draw(im, "RGBA")
        progress = stage / (STAGES - 1)

        if stage == STAGES - 1:
            cr, cg, cb = hex_rgb(color_hex)
            for k in range(8):
                ang = k * math.pi / 4 + (0.04 if frame % 2 else -0.04)
                length = 66 + (10 if (k + frame) % 2 else 0)
                x1 = center[0] + math.cos(ang) * 34
                y1 = center[1] + math.sin(ang) * 28
                x2 = center[0] + math.cos(ang) * length
                y2 = center[1] + math.sin(ang) * length * 0.78
                d.line((x1, y1, x2, y2), fill=(cr, cg, cb, 150), width=2)

        for angle, start_radius, drift, phase, tint_mix in particles:
            if stage == STAGES - 1:
                radius = 70 + (start_radius - 88) * 0.38 + ((frame + phase) % 4) * 2
            else:
                radius = start_radius * (1 - progress * 0.78)
            a = angle + drift * frame + progress * 0.65
            x = int(center[0] + math.cos(a) * radius)
            y = int(center[1] + math.sin(a) * radius * 0.72)
            if not (2 <= x < SCREEN_W - 2 and 2 <= y < SCREEN_H - 2):
                continue
            cr, cg, cb = hex_rgb(color_hex)
            col = (
                int(255 * (1 - tint_mix * max(0.25, progress)) + cr * tint_mix * max(0.25, progress)),
                int(255 * (1 - tint_mix * max(0.25, progress)) + cg * tint_mix * max(0.25, progress)),
                int(255 * (1 - tint_mix * max(0.25, progress)) + cb * tint_mix * max(0.25, progress)),
                235,
            )
            if (phase + frame) % 4 == 0:
                d.line((x - 3, y, x + 3, y), fill=col, width=1)
                d.line((x, y - 3, x, y + 3), fill=col, width=1)
            else:
                s = 2 if tint_mix > 0.45 else 1
                d.rectangle((x, y, x + s, y + s), fill=col)

        im.alpha_composite(badge_small, (center[0] - tw // 2, center[1] - th // 2))
        if stage < 3:
            # Germe de lumière au centre : il reste lisible avant que la
            # silhouette de l'étoile ne devienne identifiable.
            seed = [9, 7, 5][stage] + (1 if frame % 2 else 0)
            d_seed = ImageDraw.Draw(im, "RGBA")
            d_seed.line((center[0] - seed, center[1], center[0] + seed, center[1]),
                   fill=(255, 255, 255, 230), width=2)
            d_seed.line((center[0], center[1] - seed, center[0], center[1] + seed),
                   fill=(255, 255, 255, 230), width=2)
            d_seed.rectangle((center[0] - 2, center[1] - 2, center[0] + 2, center[1] + 2),
                        fill=(255, 255, 255, 255))
        if stage < STAGES - 1:
            draw_mouse_icon(im, color_hex, frame)
        frames.append(im.convert("RGB"))
    return frames


def write_dirsheet(frames: list[Image.Image], path: Path) -> None:
    assert len(frames) == FRAMES_PER_STAGE
    atlas = Image.new("RGB", (SCREEN_W * 2, SCREEN_H * 2))
    for i, frame in enumerate(frames):
        atlas.paste(frame, ((i % 2) * SCREEN_W, (i // 2) * SCREEN_H))
    buf = io.BytesIO()
    atlas.save(buf, "PNG", optimize=True)
    png = buf.getvalue()
    path.write_bytes(struct.pack("<q", len(png)) + png + struct.pack("<iiii", SCREEN_W, SCREEN_H, 0, len(frames)))


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def ease_out_back(value: float) -> float:
    c1 = 1.2
    c3 = c1 + 1
    value = max(0.0, min(1.0, value))
    return 1 + c3 * (value - 1) ** 3 + c1 * (value - 1) ** 2


def premultiply_rgba(im: Image.Image) -> Image.Image:
    """Écrit les sprites comme les DirSheet PMDO : RGB déjà multiplié par A."""
    arr = np.asarray(im.convert("RGBA")).astype(np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] *= alpha
    arr[arr[..., 3] == 0] = 0
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def write_dirsheet_grid(frames: list[Image.Image], path: Path, tile_w: int, tile_h: int,
                        cols: int, premultiply: bool = False) -> None:
    rows = math.ceil(len(frames) / cols)
    atlas = Image.new("RGBA", (tile_w * cols, tile_h * rows), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        if frame.size != (tile_w, tile_h):
            raise ValueError(f"Frame {i} de {path.name} : {frame.size} au lieu de {(tile_w, tile_h)}")
        atlas.paste(frame.convert("RGBA"), ((i % cols) * tile_w, (i // cols) * tile_h))
    if premultiply:
        atlas = premultiply_rgba(atlas)
    buf = io.BytesIO()
    atlas.save(buf, "PNG", optimize=True)
    png = buf.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<q", len(png)) + png +
                     struct.pack("<iiii", tile_w, tile_h, 0, len(frames)))


def make_particle_frames(color_hex: str) -> list[Image.Image]:
    """16 poses 16×16 : une séquence de scintillement répétée deux fois.

    Le Lua choisit un décalage de phase par particule (StartFrame), donc les
    étincelles ne clignotent pas toutes en même temps.
    """
    base = hex_rgb(color_hex)
    arms = [2, 3, 5, 7, 5, 4, 6, 3]
    alphas = [150, 190, 235, 255, 220, 185, 245, 175]
    frames = []
    for idx in range(PARTICLE_FRAMES):
        phase = idx % 8
        arm = arms[phase]
        alpha = alphas[phase]
        im = Image.new("RGBA", (PARTICLE_TILE, PARTICLE_TILE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, "RGBA")
        c = PARTICLE_TILE // 2
        # Halo minuscule puis croix principale.
        d.rectangle((c - 2, c - 2, c + 1, c + 1), fill=(*base, max(70, alpha - 90)))
        d.line((c - arm, c, c + arm, c), fill=(*base, alpha), width=2 if phase in (3, 6) else 1)
        d.line((c, c - arm, c, c + arm), fill=(*base, alpha), width=2 if phase in (3, 6) else 1)
        if phase in (2, 3, 6):
            for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
                d.point((c + dx, c + dy), fill=(255, 255, 255, alpha))
        core = 2 if phase in (3, 6) else 1
        d.rectangle((c - core, c - core, c + core - 1, c + core - 1),
                    fill=(255, 255, 255, 255))
        frames.append(im)
    return frames


def make_glow_frames(color_hex: str) -> list[Image.Image]:
    """Halo radial pixelisé, de la graine de lumière au halo final."""
    small = GLOW_TILE // 4
    yy, xx = np.mgrid[0:small, 0:small]
    center = (small - 1) / 2
    dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2)
    base = np.array(hex_rgb(color_hex), dtype=np.float32)
    frames = []
    for idx in range(GLOW_FRAMES):
        t = idx / (GLOW_FRAMES - 1)
        # Le petit atlas fait 40×40 avant agrandissement ×4 : le rayon doit
        # rester sous 20 unités pour retomber à zéro avant les bords du
        # sprite 160×160, sans quoi le halo afficherait un carré visible.
        radius = 1.5 + 18.0 * (1 - (1 - t) ** 2)
        falloff = np.clip(1 - dist / radius, 0, 1) ** 1.75
        peak = 18 + 145 * smoothstep(t)
        alpha = np.round(falloff * 14) / 14 * peak
        core = np.clip(1 - dist / max(2.5, radius * 0.36), 0, 1)[..., None]
        rgb = base * (1 - core * 0.58) + 255.0 * (core * 0.58)
        arr = np.dstack([rgb, alpha]).astype(np.uint8)
        glow = Image.fromarray(arr, "RGBA").resize((GLOW_TILE, GLOW_TILE), Image.Resampling.NEAREST)
        frames.append(glow)
    return frames


def make_star_frames(white: Image.Image, colored: Image.Image, color_hex: str) -> list[Image.Image]:
    """61 poses de matérialisation : révélation radiale + croissance douce.

    Le Lua ne change pas brutalement d'étape : il parcourt ces poses dans
    l'ordre à chaque frame pendant la fin du maintien. En relâchant, il les
    parcourt dans l'autre sens.
    """
    final_h = round(STAR_FINAL_W * white.height / white.width)
    white_final = white.resize((STAR_FINAL_W, final_h), Image.Resampling.NEAREST)
    colored_final = colored.resize((STAR_FINAL_W, final_h), Image.Resampling.NEAREST)
    base = hex_rgb(color_hex)
    frames = []
    for idx in range(STAR_FRAMES):
        t = idx / (STAR_FRAMES - 1)
        tile = Image.new("RGBA", (STAR_TILE_W, STAR_TILE_H), (0, 0, 0, 0))
        if idx == 0:
            frames.append(tile)
            continue

        scale = 0.06 + 0.94 * ease_out_back(t)
        tw = max(4, round(STAR_FINAL_W * scale))
        th = max(4, round(final_h * scale))
        sprite = blend_badge(white_final, colored_final, smoothstep(t))
        sprite = sprite.resize((tw, th), Image.Resampling.NEAREST)

        # Révélation du centre vers les pointes : les particules ont déjà
        # convergé avant que le Lua commence à parcourir ces poses.
        arr = np.asarray(sprite).astype(np.float32)
        yy, xx = np.mgrid[0:th, 0:tw]
        dx = (xx - (tw - 1) / 2) / max(1.0, tw / 2)
        dy = (yy - (th - 1) / 2) / max(1.0, th / 2)
        dist = np.sqrt(dx * dx + dy * dy)
        reveal = np.clip((0.16 + 1.08 * t - dist) / 0.20, 0, 1)
        opacity = smoothstep(t * 1.65)
        arr[..., 3] *= reveal * opacity
        sprite = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

        center = (STAR_TILE_W // 2, STAR_TILE_H // 2)
        if t > 0.78:
            d = ImageDraw.Draw(tile, "RGBA")
            ray_alpha = int(150 * smoothstep((t - 0.78) / 0.22))
            for k in range(8):
                ang = k * math.pi / 4 + 0.12 * math.sin(t * 6)
                inner = tw * 0.34
                outer = tw * (0.52 + 0.05 * math.sin(idx * 0.7 + k))
                d.line((center[0] + math.cos(ang) * inner,
                        center[1] + math.sin(ang) * inner * 0.9,
                        center[0] + math.cos(ang) * outer,
                        center[1] + math.sin(ang) * outer * 0.9),
                       fill=(*base, ray_alpha), width=2)
        tile.alpha_composite(sprite, (center[0] - tw // 2, center[1] - th // 2))
        frames.append(tile)
    return frames


def generate_assets(config: dict) -> list[str]:
    starters = {s["Id"]: s for s in config["Object"]["Starters"]}
    needed = {}
    for item in config["Object"]["Mapping"]:
        starter = starters[item["Starter"]]
        needed[starter["EtoileType"]] = starter["CouleurType"]

    source = Image.open(BADGE_PATH).convert("RGBA")
    bbox = source.getbbox()
    source = source.crop(bbox)
    BG_DIR.mkdir(parents=True, exist_ok=True)
    PARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    OBJECT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    made = []

    # Ciel seul pour l'animation fluide : particules, halo et étoile sont
    # ensuite dessinés librement autour du point de la souris.
    fond_frames = [make_background(i).convert("RGB") for i in range(FRAMES_PER_STAGE)]
    write_dirsheet(fond_frames, BG_DIR / "Quiz_Etoile_Fond.dir")
    made.append("game/Content/BG/Quiz_Etoile_Fond.dir")

    global_sheet = Image.new("RGB", (SCREEN_W * STAGES, SCREEN_H * len(needed)), (8, 8, 16))
    fluid_sheet = Image.new("RGBA", (STAR_TILE_W * 5, STAR_TILE_H * len(needed)), (7, 8, 26, 255))
    for row, (slug, color) in enumerate(sorted(needed.items())):
        colored = recolor_badge(source, color)

        # Ancien rendu plein écran : conservé uniquement comme secours si le
        # menu scriptable ne peut pas être créé sur une configuration donnée.
        for stage in range(STAGES):
            frames = make_stage_frames(color, slug, source, colored, stage)
            name = f"Quiz_Etoile_{slug}_{stage}.dir"
            write_dirsheet(frames, BG_DIR / name)
            made.append(f"game/Content/BG/{name}")
            global_sheet.paste(frames[0], (stage * SCREEN_W, row * SCREEN_H))

        particle_name = f"Quiz_Etoile_Particule_{slug}.dir"
        write_dirsheet_grid(make_particle_frames(color), PARTICLE_DIR / particle_name,
                            PARTICLE_TILE, PARTICLE_TILE, 4, premultiply=True)
        made.append(f"game/Content/Particle/{particle_name}")

        glow_name = f"Quiz_Etoile_Halo_{slug}.dir"
        write_dirsheet_grid(make_glow_frames(color), OBJECT_DIR / glow_name,
                            GLOW_TILE, GLOW_TILE, 7, premultiply=True)
        made.append(f"game/Content/Object/{glow_name}")

        star_frames = make_star_frames(source, colored, color)
        star_name = f"Quiz_Etoile_Forme_{slug}.dir"
        write_dirsheet_grid(star_frames, OBJECT_DIR / star_name,
                            STAR_TILE_W, STAR_TILE_H, 8, premultiply=True)
        made.append(f"game/Content/Object/{star_name}")
        for col, frame_idx in enumerate((0, 15, 30, 45, STAR_FRAMES - 1)):
            fluid_sheet.alpha_composite(star_frames[frame_idx],
                                        (col * STAR_TILE_W, row * STAR_TILE_H))

    global_sheet.save(PREVIEW_DIR / "planche_etoiles_types.png", optimize=True)
    fluid_sheet.convert("RGB").save(PREVIEW_DIR / "planche_etoile_fluide.png", optimize=True)
    return made


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-only", action="store_true", help="ne réécrit ni les données ni les .dir")
    parser.add_argument("--no-assets", action="store_true", help="réécrit les données sans régénérer les .dir")
    args = parser.parse_args()

    config, natures_doc, report = build_data()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(report["test_cible_reussi"].values()):
        raise SystemExit("Audit quiz : au moins une nature ciblée ne gagne pas son test.")
    if args.audit_only:
        return

    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    NATURES_PATH.write_text(json.dumps(natures_doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_lua(config, natures_doc)
    if not args.no_assets:
        made = generate_assets(config)
        print(f"{len(made)} DirSheet générés (BG + Particle + Object)")


if __name__ == "__main__":
    main()
