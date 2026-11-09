#!/usr/bin/env python3
"""Génère le quiz de personnalité Destiny et l'animation de l'étoile.

Source unique pour :
  * game/Data/quiz_personnalite_config.json (20 questions) ;
  * game/Data/quiz_personnalite_natures.json (descriptions FR) ;
  * game/Data/Script/destiny/ground/personality_test/quiz_data.lua ;
  * game/Content/Particle/Quiz_Etoile_Particule_<Type>.dir ;
  * game/Content/Object/Quiz_Etoile_Halo_<Type>.dir ;
  * game/Content/Object/Quiz_Etoile_Ondes_<Type>.dir ;
  * game/Content/Object/Quiz_Etoile_Forme_<Type>.dir
    (VFX transparents dessinés par-dessus le fond Dream de base du quiz,
    sans jamais remplacer ce fond).

Les questions sont des textes originaux, dans l'esprit des quiz de
personnalité PMD : situations concrètes, réponses de 2 à 5 choix, quelques
oui/non et aucune nature affichée au joueur. Le compteur de question est
volontairement absent des données comme du script.

L'étoile part de la silhouette du badge déjà présent dans la quest, puis
reçoit un vrai travail de facettes, de reflets et de dissolution pixel art
selon le type principal du starter obtenu. Tous les VFX sont transparents,
écrits en alpha prémultiplié, et leurs ondes reprennent le rythme zigzagant
des couches Dream_Back / Dream_Front déjà affichées par la carte du quiz.
Aucun symbole de souris n'est dessiné dans les images : la consigne du clic
droit appartient uniquement à la boîte de dialogue qui précède l'animation.
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
PARTICLE_DIR = GAME / "Content/Particle"
OBJECT_DIR = GAME / "Content/Object"
PREVIEW_DIR = ROOT / "docs/quiz_etoile_apercus"

SCREEN_W, SCREEN_H = 320, 240

# Animation fluide pilotée par ScriptableMenu dans le Lua. Quatre calques
# transparents restent au-dessus du fond Dream de la carte :
#   - les ondes tournent en boucle à leur propre rythme ;
#   - le halo possède 81 poses de charge ;
#   - les particules sont déplacées individuellement à chaque frame ;
#   - l'étoile se matérialise en 56 poses puis scintille en 16 poses.
PARTICLE_TILE = 24
PARTICLE_FRAMES = 24
GLOW_TILE = 192
GLOW_FRAMES = 81
WAVE_TILE = 224
WAVE_FRAMES = 36
STAR_TILE_W, STAR_TILE_H = 192, 216
STAR_FINAL_W = 132
STAR_MATERIALIZE_LAST = 56
STAR_FRAMES = 73

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
        "silhouette à la révélation finale ; ses VFX transparents sont colorés "
        "selon le type principal du starter conclu et restent dessinés "
        "par-dessus le fond de base du quiz."
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

def mix_rgb(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    amount = max(0.0, min(1.0, amount))
    return tuple(int(round(a[i] * (1 - amount) + b[i] * amount)) for i in range(3))


def scale_rgb(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, round(c * factor)))) for c in color)


def vfx_palette(color_hex: str) -> dict[str, tuple[int, int, int]]:
    """Palette commune aux quatre calques du VFX.

    Le fond du quiz fait défiler tout le spectre : chaque type garde donc sa
    couleur au centre, mais reçoit aussi un contour indigo presque noir, une
    tranche ivoire et une lumière blanche. Cette charpente commune reste
    lisible quelle que soit la teinte Dream affichée derrière l'étoile.
    """
    base = hex_rgb(color_hex)
    lum = (0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]) / 255.0
    # Ramène les types très clairs ou très sombres dans une plage commune,
    # sans changer leur famille de couleur.
    if lum > 0.72:
        base = scale_rgb(base, 0.78)
    elif lum < 0.22:
        base = mix_rgb(base, (255, 255, 255), 0.20)
    return {
        "contour": (20, 12, 34),
        "ombre": mix_rgb(scale_rgb(base, 0.38), (24, 16, 52), 0.42),
        "fonce": scale_rgb(base, 0.62),
        "base": base,
        "clair": mix_rgb(base, (255, 255, 255), 0.34),
        "pale": mix_rgb(base, (255, 255, 255), 0.66),
        "ivoire": (255, 244, 214),
        "blanc": (255, 255, 255),
    }


def recolor_badge(source: Image.Image, color_hex: str) -> Image.Image:
    """Version haute résolution utilisée avant la réduction pixel art."""
    palette = vfx_palette(color_hex)
    arr = np.asarray(source.convert("RGBA")).astype(np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3]
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    ramp = np.array([
        palette["ombre"], palette["fonce"], palette["base"],
        palette["clair"], palette["pale"], palette["ivoire"],
    ], dtype=np.float32)
    ramp_index = np.clip((lum * len(ramp)).astype(np.int32), 0, len(ramp) - 1)
    colored = ramp[ramp_index]
    highlight = np.clip((lum - 0.80) / 0.20, 0, 1)[..., None]
    colored = colored * (1 - highlight * 0.85) + 255.0 * (highlight * 0.85)
    colored[lum < 0.10] = np.array(palette["contour"], dtype=np.float32)
    out = np.dstack([np.clip(colored, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def make_faceted_badge(white: Image.Image, color_hex: str) -> Image.Image:
    """Badge final travaillé pixel par pixel à sa taille d'affichage.

    La silhouette et les deux contours viennent du badge de la quest. Les
    facettes, en revanche, sont reconstruites à la taille finale : cinq
    secteurs autour du cœur, lumière venue du haut-gauche, tranche claire sur
    le rebord, ombre basse et éclats d'ivoire. Le résultat reste net après
    les réductions au plus proche voisin des poses de matérialisation.
    """
    palette = vfx_palette(color_hex)
    final_h = round(STAR_FINAL_W * white.height / white.width)
    resized = white.resize((STAR_FINAL_W, final_h), Image.Resampling.NEAREST).convert("RGBA")
    arr = np.asarray(resized).astype(np.float32)
    alpha = arr[..., 3]
    lum = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]) / 255.0
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = (w - 1) / 2, h * 0.55
    dx = (xx - cx) / max(1.0, w / 2)
    dy = (yy - cy) / max(1.0, h / 2)
    dist = np.sqrt(dx * dx + dy * dy)
    angle = (np.arctan2(-dy, dx) + math.pi / 2) % math.tau
    sectors = np.floor(angle / (math.tau / 5)).astype(np.int32) % 5
    sector_light = np.array([0.10, 0.03, -0.08, -0.05, 0.07], dtype=np.float32)[sectors]
    upper_left = np.clip(0.62 - 0.42 * dx - 0.34 * dy, 0, 1)
    # Le badge source est presque blanc : sans compression de sa luminance,
    # toutes les facettes tomberaient dans l'ivoire et seul le rebord
    # porterait la couleur du type. On ramène donc la matière dans les
    # teintes fonce/base/clair, en réservant le pâle aux vraies lumières.
    facet_lum = np.clip(0.20 + lum * 0.48 + upper_left * 0.10 + sector_light, 0, 1)

    ramp = np.array([
        palette["ombre"], palette["fonce"], palette["fonce"], palette["base"],
        palette["base"], palette["clair"], palette["clair"], palette["pale"],
    ], dtype=np.float32)
    ramp_index = np.clip((facet_lum * len(ramp)).astype(np.int32), 0, len(ramp) - 1)
    colored = ramp[ramp_index].copy()

    solid = alpha > 24
    dark_line = solid & (lum < 0.16)
    # Les lignes noires du badge deviennent indigo très profond ; elles
    # séparent l'étoile du fond arc-en-ciel dans toutes ses phases.
    colored[dark_line] = np.array(palette["contour"], dtype=np.float32)

    # Reflets durs, volontairement pixelisés : une bande claire sur la branche
    # supérieure, une tranche sur la gauche, puis une ombre au bas des pointes.
    top_glint = solid & ~dark_line & (yy < h * 0.30) & (np.abs(dx + 0.08) < 0.16) & (lum > 0.62)
    left_glint = solid & ~dark_line & (dx < -0.28) & (dy > -0.52) & (dy < 0.08) & (lum > 0.70)
    colored[top_glint | left_glint] = np.array(palette["ivoire"], dtype=np.float32)
    tiny_white = solid & ~dark_line & (lum > 0.94) & (dist < 0.72)
    colored[tiny_white] = np.array(palette["blanc"], dtype=np.float32)
    bottom_shade = solid & ~dark_line & (yy > h * 0.78) & (lum < 0.72)
    colored[bottom_shade] = np.array(palette["fonce"], dtype=np.float32)
    loop_light = solid & ~dark_line & (yy < h * 0.14) & (lum > 0.48)
    colored[loop_light] = np.array(palette["pale"], dtype=np.float32)

    # Un léger tramage 2×2 sur les transitions donne une matière minérale
    # sans lisser les contours.
    dither = ((xx + yy) % 2 == 0) & solid & ~dark_line & (np.abs(facet_lum - 0.48) < 0.045)
    colored[dither] = np.array(palette["clair"], dtype=np.float32)

    out = np.dstack([np.clip(colored, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_badge(white: Image.Image, colored: Image.Image, amount: float) -> Image.Image:
    w = np.asarray(white.convert("RGBA")).astype(np.float32)
    c = np.asarray(colored.convert("RGBA")).astype(np.float32)
    out = w.copy()
    out[..., :3] = w[..., :3] * (1 - amount) + c[..., :3] * amount
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


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
    """24 poses 24×24 : trois cycles d'une étincelle qui se déploie.

    Chaque cycle passe d'un losange minuscule à une étoile à quatre pointes,
    puis replie ses bras en laissant quatre grains orbitaux. Le Lua choisit
    une phase différente pour chaque particule ; leurs scintillements ne se
    synchronisent donc jamais en un clignotement global.
    """
    palette = vfx_palette(color_hex)
    arms = [2, 3, 5, 8, 10, 8, 5, 3]
    alphas = [155, 190, 225, 250, 255, 230, 205, 175]
    frames = []
    c = PARTICLE_TILE // 2
    for idx in range(PARTICLE_FRAMES):
        cycle, phase = divmod(idx, 8)
        arm = arms[phase]
        alpha = alphas[phase]
        im = Image.new("RGBA", (PARTICLE_TILE, PARTICLE_TILE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, "RGBA")

        # Petit nuage de poussière colorée, décalé d'un cycle à l'autre.
        glow_r = 3 + (1 if phase in (3, 4, 5) else 0)
        for dy in range(-glow_r, glow_r + 1):
            for dx in range(-glow_r, glow_r + 1):
                if abs(dx) + abs(dy) <= glow_r and (dx + dy + cycle) % 2 == 0:
                    d.point((c + dx, c + dy), fill=(*palette["fonce"], 58))

        # Bras principaux en deux épaisseurs et deux teintes : la tranche
        # extérieure est pâle, l'axe reste saturé, le cœur devient blanc.
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for step in range(2, arm + 1):
                col = palette["clair"] if step < arm * 0.62 else palette["pale"]
                a = int(alpha * (1.0 - 0.18 * step / max(1, arm)))
                d.point((c + dx * step, c + dy * step), fill=(*col, a))
                if phase in (3, 4, 5) and 2 < step < arm - 1:
                    # Épaule latérale d'un pixel, seulement au plus fort du
                    # déploiement, pour éviter une simple croix uniforme.
                    d.point((c + dx * step + abs(dy), c + dy * step + abs(dx)),
                            fill=(*palette["base"], int(a * 0.72)))

        # Micro-diagonales tournantes : elles changent de quadrant à chaque
        # cycle, ce qui donne une impression de rotation sans pivoter l'image.
        if phase in (2, 3, 4, 5, 6):
            diag = 3 + (1 if phase in (3, 4) else 0)
            quadrants = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
            for qi in range(4):
                if (qi + cycle + phase) % 2:
                    qx, qy = quadrants[qi]
                    d.point((c + qx * diag, c + qy * diag), fill=(*palette["ivoire"], alpha))
                    if phase == 4:
                        d.point((c + qx * (diag + 2), c + qy * (diag + 2)),
                                fill=(*palette["pale"], int(alpha * 0.66)))

        # Grains détachés en fin de cycle : la particule ne disparaît jamais
        # d'un coup entre deux poses.
        if phase >= 6:
            for dx, dy in ((-6, -2), (5, -5), (6, 3), (-4, 6)):
                d.point((c + dx, c + dy), fill=(*palette["pale"], 120 if phase == 6 else 82))

        core_r = 2 if phase in (3, 4) else 1
        d.rectangle((c - core_r, c - core_r, c + core_r - 1, c + core_r - 1),
                    fill=(*palette["blanc"], 255))
        d.point((c, c), fill=(*palette["ivoire"], 255))
        frames.append(im)
    return frames


def make_glow_frames(color_hex: str) -> list[Image.Image]:
    """81 poses du halo de charge, accordées aux vagues Dream.

    Le halo n'est plus une simple tache radiale : un noyau doux porte deux
    anneaux brisés et une bande zigzagante horizontale. Ce motif fait écho
    aux couches Dream_Back / Dream_Front sans les remplacer ; le fond de la
    carte continue donc de vivre derrière le VFX.
    """
    palette = vfx_palette(color_hex)
    small = GLOW_TILE // 4  # 48×48, agrandi ×4 pour garder de gros pixels
    yy, xx = np.mgrid[0:small, 0:small]
    center = (small - 1) / 2
    dx = xx - center
    dy = yy - center
    dist = np.sqrt(dx * dx + dy * dy)
    angle = np.arctan2(dy, dx)
    frames = []

    for idx in range(GLOW_FRAMES):
        t = idx / (GLOW_FRAMES - 1)
        growth = 1 - (1 - t) ** 2
        radius = 2.0 + 20.5 * growth
        soft = np.clip(1 - dist / max(2.0, radius), 0, 1) ** 1.65
        peak = 16 + 138 * smoothstep(t)
        intensity = soft * peak

        # Anneaux dont le rayon ondule avec l'angle. Les interruptions
        # tournent lentement pendant la charge, mais leur intensité globale
        # augmente de façon monotone avec la progression.
        for ring_ratio, width, strength, waves, speed in (
            (0.72, 1.15, 74, 12, 1.4),
            (0.94, 0.90, 54, 18, -1.0),
        ):
            wobble = 0.72 * np.sin(angle * waves + t * speed * math.tau)
            ring_dist = np.abs(dist - (radius * ring_ratio + wobble))
            ring = np.clip(1 - ring_dist / width, 0, 1)
            dashes = 0.46 + 0.54 * (0.5 + 0.5 * np.sin(angle * 9 - t * 5.2))
            intensity += ring * dashes * strength * (0.18 + 0.82 * smoothstep(t))

        # Bande en zigzag, signature visuelle du fond de base : elle traverse
        # le halo sans couvrir tout l'écran et s'estompe vers les bords.
        zig = np.abs(((xx * 0.72 + t * 12.0) % 8.0) - 4.0) - 2.0
        wave_y = center + zig * 0.86 + 1.4 * np.sin(xx / small * math.tau + t * 2.0)
        wave = np.clip(1 - np.abs(yy - wave_y) / 2.4, 0, 1)
        wave *= np.clip(1 - dist / (radius * 1.04), 0, 1)
        intensity += wave * (18 + 52 * smoothstep(t))

        # Huit rayons courts, révélés seulement après la mi-charge.
        ray_phase = np.cos((angle - t * 1.8) * 8)
        rays = np.clip((ray_phase - 0.955) / 0.045, 0, 1)
        rays *= np.clip((dist - radius * 0.22) / 2.0, 0, 1)
        rays *= np.clip(1 - dist / (radius * 1.02), 0, 1)
        intensity += rays * 72 * smoothstep((t - 0.46) / 0.54)

        # Quantification franche + chute tramée : le bord retombe à zéro bien
        # avant le cadre 192×192, donc aucun carré ne peut apparaître.
        intensity = np.round(np.clip(intensity, 0, 224) / 14.0) * 14.0
        edge = np.clip((radius * 1.08 - dist) / 3.5, 0, 1)
        bayer = ((xx % 2) + (yy % 2) * 2) / 4.0
        intensity *= np.where(edge >= 1, 1.0, (edge > bayer * 0.62).astype(np.float32))

        heat = np.clip(intensity / 224.0, 0, 1)[..., None]
        base = np.array(palette["base"], dtype=np.float32)
        pale = np.array(palette["pale"], dtype=np.float32)
        white = np.array(palette["blanc"], dtype=np.float32)
        rgb = base * (1 - heat) + pale * heat
        hot = np.clip((heat - 0.62) / 0.38, 0, 1)
        rgb = rgb * (1 - hot * 0.72) + white * (hot * 0.72)
        alpha = intensity.copy()
        alpha[alpha < 10] = 0
        arr = np.dstack([rgb, alpha]).astype(np.uint8)
        glow = Image.fromarray(arr, "RGBA").resize((GLOW_TILE, GLOW_TILE), Image.Resampling.NEAREST)
        frames.append(glow)
    return frames


def make_wave_frames(color_hex: str) -> list[Image.Image]:
    """36 poses bouclées d'ondes concentriques en zigzag.

    Ce calque est lu en continu par le Lua, indépendamment de la jauge de
    charge : trois fronts naissent près du point choisi, s'élargissent en
    perdant leur éclat, puis la boucle reprend sans couture. Les fronts sont
    brisés en arcs et leur rayon ondule, comme les vagues du fond Dream.
    """
    palette = vfx_palette(color_hex)
    small = WAVE_TILE // 4  # 56×56 avant agrandissement ×4
    yy, xx = np.mgrid[0:small, 0:small]
    center = (small - 1) / 2
    dx = xx - center
    dy = yy - center
    dist = np.sqrt(dx * dx + dy * dy)
    angle = np.arctan2(dy, dx)
    frames = []

    for idx in range(WAVE_FRAMES):
        phase = idx / WAVE_FRAMES
        intensity = np.zeros_like(dist, dtype=np.float32)
        for front in range(3):
            life = (phase + front / 3) % 1.0
            radius = 4.0 + 22.0 * (1 - (1 - life) ** 2)
            wobble = (0.52 + 0.20 * front) * np.sin(angle * (11 + front * 3) + phase * math.tau * (1 + front * 0.35))
            ring = np.clip(1 - np.abs(dist - (radius + wobble)) / 1.18, 0, 1)
            dashes = 0.34 + 0.66 * (0.5 + 0.5 * np.sin(angle * (7 + front * 2) - phase * math.tau * 2))
            fade = math.sin(math.pi * min(1.0, life * 1.08)) ** 1.25
            intensity += ring * dashes * fade * (118 - front * 18)

        # Une courte houle horizontale traverse les anneaux, toujours avec
        # le même pas de zigzag que le fond de la carte.
        zig = np.abs(((xx * 0.70 - phase * 16.0) % 9.0) - 4.5) - 2.25
        wave_y = center + zig * 0.92
        houle = np.clip(1 - np.abs(yy - wave_y) / 1.75, 0, 1)
        houle *= np.clip(1 - dist / 27.0, 0, 1)
        intensity += houle * 44

        # La périphérie retombe en trame avant le bord de la tuile.
        edge = np.clip((28.0 - dist) / 3.0, 0, 1)
        bayer = ((xx % 2) + (yy % 2) * 2) / 4.0
        intensity *= np.where(edge >= 1, 1.0, (edge > bayer * 0.58).astype(np.float32))
        intensity = np.round(np.clip(intensity, 0, 210) / 15.0) * 15.0

        heat = np.clip(intensity / 210.0, 0, 1)[..., None]
        rgb = (np.array(palette["clair"], dtype=np.float32) * (1 - heat) +
               np.array(palette["blanc"], dtype=np.float32) * heat)
        alpha = intensity.copy()
        alpha[alpha < 12] = 0
        arr = np.dstack([rgb, alpha]).astype(np.uint8)
        wave = Image.fromarray(arr, "RGBA").resize((WAVE_TILE, WAVE_TILE), Image.Resampling.NEAREST)
        frames.append(wave)
    return frames


def make_star_frames(white: Image.Image, colored: Image.Image, color_hex: str) -> list[Image.Image]:
    """73 poses : 56 de matérialisation, puis 16 de scintillement final.

    La forme ne se contente plus de grandir. Elle naît en poussière blanche,
    se révèle du cœur vers les pointes avec une dissolution Bayer, reçoit
    ses facettes colorées, puis ses rayons. Une fois complète, un reflet
    traverse le badge et quatre éclats orbitent lentement autour de lui.
    Le Lua parcourt les poses 1 à 56 pendant la fin du maintien, dans un
    sens ou dans l'autre, puis boucle les poses 57 à 72.
    """
    palette = vfx_palette(color_hex)
    final_h = round(STAR_FINAL_W * white.height / white.width)
    white_final = white.resize((STAR_FINAL_W, final_h), Image.Resampling.NEAREST)
    faceted_final = make_faceted_badge(white, color_hex)
    # `colored` reste accepté pour compatibilité de l'appelant historique,
    # mais la version facettée à taille finale est plus nette.
    _ = colored

    bayer = np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5],
    ], dtype=np.float32) / 16.0

    frames = []
    center = (STAR_TILE_W // 2, STAR_TILE_H // 2)
    for idx in range(STAR_FRAMES):
        tile = Image.new("RGBA", (STAR_TILE_W, STAR_TILE_H), (0, 0, 0, 0))
        if idx == 0:
            frames.append(tile)
            continue

        final_pose = idx > STAR_MATERIALIZE_LAST
        if final_pose:
            t = 1.0
            shimmer = (idx - STAR_MATERIALIZE_LAST - 1) / 15.0
        else:
            t = idx / STAR_MATERIALIZE_LAST
            shimmer = 0.0

        scale = 0.05 + 0.95 * ease_out_back(t)
        if final_pose:
            scale = 1.0 + 0.012 * math.sin(shimmer * math.tau)
        tw = max(4, round(STAR_FINAL_W * scale))
        th = max(4, round(final_h * scale))
        sprite = blend_badge(white_final, faceted_final, smoothstep((t - 0.10) / 0.78))
        sprite = sprite.resize((tw, th), Image.Resampling.NEAREST)

        arr = np.asarray(sprite).astype(np.float32)
        yy, xx = np.mgrid[0:th, 0:tw]
        dx = (xx - (tw - 1) / 2) / max(1.0, tw / 2)
        dy = (yy - (th - 1) * 0.55) / max(1.0, th / 2)
        dist = np.sqrt(dx * dx + dy * dy)
        if not final_pose:
            # Front radial + seuil Bayer : la matière semble condensée par
            # les particules plutôt que simplement fondu enchaîné.
            local_bayer = np.tile(bayer, (math.ceil(th / 4), math.ceil(tw / 4)))[:th, :tw]
            reveal = np.clip((0.10 + 1.18 * t - dist) / 0.17, 0, 1)
            dissolve = np.clip((t * 1.16 - local_bayer * 0.22) / 0.20, 0, 1)
            arr[..., 3] *= reveal * dissolve * smoothstep(t * 1.55)
        else:
            # Reflet oblique qui traverse les facettes pendant le maintien
            # final. Il éclaircit sans modifier la silhouette.
            band = np.clip(1 - np.abs((dx * 0.72 + dy * 0.30) - (-0.85 + 1.70 * shimmer)) / 0.16, 0, 1)
            lit = arr[..., 3] > 20
            arr[..., :3] = np.clip(arr[..., :3] + band[..., None] * 58 * lit[..., None], 0, 255)
        sprite = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

        d = ImageDraw.Draw(tile, "RGBA")
        # Rayons cardinaux et diagonaux en deux couches décalées. Ils sont
        # dessinés sous le badge, avec des extrémités tronquées pour garder
        # un vocabulaire pixel art plutôt qu'un faisceau flou.
        ray_birth = smoothstep((t - 0.54) / 0.46)
        if ray_birth > 0:
            pulse = 1.0 + (0.08 * math.sin(shimmer * math.tau * 2) if final_pose else 0.0)
            for k in range(8):
                ang = k * math.pi / 4 + 0.10 * math.sin(t * 5.0 + shimmer * math.tau)
                is_cardinal = k % 2 == 0
                inner = tw * (0.30 if is_cardinal else 0.36)
                outer = tw * (0.58 if is_cardinal else 0.50) * ray_birth * pulse
                col = palette["clair"] if is_cardinal else palette["base"]
                a = int((164 if is_cardinal else 116) * ray_birth)
                x1 = center[0] + math.cos(ang) * inner
                y1 = center[1] + math.sin(ang) * inner * 0.92
                x2 = center[0] + math.cos(ang) * outer
                y2 = center[1] + math.sin(ang) * outer * 0.92
                d.line((x1, y1, x2, y2), fill=(*palette["ombre"], int(a * 0.55)), width=3)
                d.line((x1, y1, x2, y2), fill=(*col, a), width=2 if is_cardinal else 1)
                d.point((round(x2), round(y2)), fill=(*palette["ivoire"], a))

        # Éclats de contour pendant la naissance : quelques grains blancs
        # longent le front de matérialisation, comme si les dernières
        # particules venaient souder les pointes.
        if not final_pose and 0.08 < t < 0.98:
            for k in range(10):
                ang = (k / 10) * math.tau + 0.7 * math.sin(idx * 0.31 + k)
                r = (0.12 + 0.95 * t) * tw * 0.48
                px = int(round(center[0] + math.cos(ang) * r))
                py = int(round(center[1] + math.sin(ang) * r * 0.92))
                if 2 <= px < STAR_TILE_W - 2 and 2 <= py < STAR_TILE_H - 2:
                    a = 96 + ((idx + k * 3) % 5) * 28
                    d.line((px - 2, py, px + 2, py), fill=(*palette["pale"], a), width=1)
                    d.line((px, py - 2, px, py + 2), fill=(*palette["pale"], a), width=1)
                    d.point((px, py), fill=(*palette["blanc"], 235))

        tile.alpha_composite(sprite, (center[0] - tw // 2, center[1] - th // 2))

        # Quatre satellites au-dessus du badge dans les poses finales.
        if final_pose:
            d2 = ImageDraw.Draw(tile, "RGBA")
            for k in range(4):
                ang = -math.pi / 2 + k * math.pi / 2 + shimmer * math.tau
                r = tw * (0.56 + 0.035 * math.sin(shimmer * math.tau * 2 + k))
                px = int(round(center[0] + math.cos(ang) * r))
                py = int(round(center[1] + math.sin(ang) * r * 0.86))
                arm = 4 if (idx + k) % 4 in (0, 1) else 3
                d2.line((px - arm, py, px + arm, py), fill=(*palette["pale"], 220), width=1)
                d2.line((px, py - arm, px, py + arm), fill=(*palette["pale"], 220), width=1)
                d2.rectangle((px - 1, py - 1, px, py), fill=(*palette["blanc"], 255))

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
    PARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    OBJECT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    made = []
    # Planche de contrôle : cinq instants de l'étoile par type, sur un fond
    # sombre neutre. L'aperçu animé sur le vrai fond Dream est produit à part.
    fluid_sheet = Image.new("RGBA", (STAR_TILE_W * 5, STAR_TILE_H * len(needed)), (14, 12, 34, 255))
    for row, (slug, color) in enumerate(sorted(needed.items())):
        colored = recolor_badge(source, color)

        particle_name = f"Quiz_Etoile_Particule_{slug}.dir"
        write_dirsheet_grid(make_particle_frames(color), PARTICLE_DIR / particle_name,
                            PARTICLE_TILE, PARTICLE_TILE, 6, premultiply=True)
        made.append(f"game/Content/Particle/{particle_name}")

        glow_name = f"Quiz_Etoile_Halo_{slug}.dir"
        write_dirsheet_grid(make_glow_frames(color), OBJECT_DIR / glow_name,
                            GLOW_TILE, GLOW_TILE, 9, premultiply=True)
        made.append(f"game/Content/Object/{glow_name}")

        wave_name = f"Quiz_Etoile_Ondes_{slug}.dir"
        write_dirsheet_grid(make_wave_frames(color), OBJECT_DIR / wave_name,
                            WAVE_TILE, WAVE_TILE, 6, premultiply=True)
        made.append(f"game/Content/Object/{wave_name}")

        star_frames = make_star_frames(source, colored, color)
        star_name = f"Quiz_Etoile_Forme_{slug}.dir"
        write_dirsheet_grid(star_frames, OBJECT_DIR / star_name,
                            STAR_TILE_W, STAR_TILE_H, 8, premultiply=True)
        made.append(f"game/Content/Object/{star_name}")
        for col, frame_idx in enumerate((0, 14, 28, STAR_MATERIALIZE_LAST, STAR_FRAMES - 1)):
            fluid_sheet.alpha_composite(star_frames[frame_idx],
                                        (col * STAR_TILE_W, row * STAR_TILE_H))

    fluid_sheet.convert("RGB").save(PREVIEW_DIR / "planche_vfx_etoile.png", optimize=True)
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
        print(f"{len(made)} DirSheet VFX générés (Particle + Object)")


if __name__ == "__main__":
    main()
