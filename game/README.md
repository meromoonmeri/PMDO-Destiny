# Quest Destiny

Ce dossier est copié dans `MODS/Destiny/` pendant la construction, puis la
commande native `-build` de PMDO le fusionne avec la base pour produire le jeu
standalone.

- `Mod.xml` : identité, UUID et namespace `destiny`.
- `Data/Ground/` : **303 Grounds** individuels, jamais fusionnés.
- `Data/Zone/` : **10 zones** (modèle Halcyon : plusieurs cartes par zone) + `index.idx`.
- `Data/Script/destiny/` : scripts de la quest, un `init.lua` par Ground, plus le
  quiz de personnalité (`ground/personality_test/`) et ses données.
- `Content/Tile/` : **1 640 tilesets** (`.tile` autonomes, PNG embarqués) et leur
  `index.idx` (1 640 entrées, tenu par `tools/ajouter_tilesheets_index.py`).
- `Content/BG/` (91) et `Content/Object/` (34) : fonds et animations.
- `Content/UI/` : écran-titre et `quiz_badges/` (17 badges de nature).
- `Data/quiz_personnalite_config.json`, `Data/quiz_personnalite_natures.json`.

## Les 10 zones

| Zone | Cartes | Contenu |
|---|---:|---|
| `cotes_metano` | 84 | falaises et côtes de Métano, jour et nuit |
| `ateliers_donjons` | 156 | seuils de donjons, arènes, fins de donjon |
| `reverie` | 13 | bourg de Reverie et abords de la guilde |
| `chapitres_destiny` | 8 | les huit lieux des chapitres I et II |
| `guilde` | 17 | intérieurs, parvis, extérieur et sentier de la guilde |
| `entrees_donjons` | 12 | entrées livrées par l'atelier, plages |
| `bourg_metano` | 10 | Métano générique, cafés, place du trésor |
| `cinematiques` | 3 | quiz, halo d'intro, réveil |
| `capitale` | 1 | WaterfallVillageCapital |
| `destiny_hub` | 1 | carte de départ |

## Avant de lancer le jeu

`WaterfallVillageCapital.rsground` pèse 315 Mio, au-delà de la limite GitHub de
100 Mio par fichier, et le dépôt n'utilise pas Git LFS. Il est versionné
compressé sans perte dans `ressources/` (1,9 Mio). C'est la version du Drive de
l'auteur, **étendue au sud** (voir `docs/AMELIORATION_WVC_SUD.md`).
Restauration unique :

```bash
python tools/restaurer_waterfall.py
```

Le script vérifie la taille (233 727 831 octets) et l'empreinte SHA-256 publiée
dans `town02`.

## Documentation

- `docs/QUEST_DESTINY_RECUPERATION.md` — récupération complète, ce qui manquait, ce qui reste impossible.
- `docs/QUEST_DESTINY_AUDIT.md` — inventaire des sources et périmètre.
- `docs/QUEST_DESTINY_ORGANISATION.md` — conventions PMDO déduites de Halcyon.
- `docs/QUEST_DESTINY_MANQUANTS.md` — références cassées et hors-périmètre.
