# Quest Destiny — récupération complète (passe du 30 octobre 2026, seconde partie)

Cette passe répond à la demande « récupère tous les manquements, toutes les maps
manquantes, la guilde, tout ». Elle a consisté à **élargir la recherche à toutes
les branches de tous les dépôts**, et non plus aux seules branches principales.

---

## 1. Ce que la première passe avait manqué

La Quest avait été construite depuis `main` de PMDO-Destiny, qui ne contient
qu'une carte. Or le dépôt possède une **seconde branche de travail,
`arena/c40fd96f-pmdo-destiny`, qui contient déjà 262 Grounds** : côtes de Métano,
156 seuils de donjons et arènes, 8 cartes de chapitres, plus un menu-titre animé
et son outillage de validation. Cette branche n'avait jamais été fusionnée dans
`main`.

Balayage effectué : **113 branches** réparties sur 6 dépôts
(`PMDO-Destiny` 3, `projet-creation-pmdo` 26, `guilde-treehouse-pmd` 81,
`PROJET-PMD` 1, `town02` 1, `new-era-project` 1). 1 631 noms de Grounds
distincts ont été relevés, dont **185 absents des branches principales**.

---

## 2. Résultat

| | Avant cette passe | Après |
|---|---:|---:|
| Grounds dans la Quest | 25 | **303** |
| Zones | 25 | **10** (regroupées à la manière de Halcyon) |
| TileSheets | 142 | **1 640** |
| Fonds et animations (`Content/BG`, `Content/Object`) | 7 | **91 + 34** |
| Scripts de Ground | 25 | **303** |
| Tilesets manquants | 1 | **0** |

Aucune carte n'a été fusionnée dans un autre fichier : les 303 restent des
`.rsground` individuels.

### Les dix zones

| Zone | Cartes | Contenu |
|---|---:|---|
| `cotes_metano` | 84 | falaises et côtes de Métano, jour et nuit |
| `ateliers_donjons` | 156 | seuils de donjons, arènes, fins de donjon |
| `reverie` | 13 | bourg de Reverie et abords de la guilde |
| `chapitres_destiny` | 8 | les huit lieux des chapitres I et II |
| `guilde` | 17 | **la guilde** : 13 intérieurs, parvis, extérieur, sentier |
| `entrees_donjons` | 12 | entrées livrées par l'atelier + plages |
| `bourg_metano` | 10 | Métano générique, cafés, place du trésor |
| `cinematiques` | 3 | quiz de personnalité, halo d'intro, réveil |
| `capitale` | 1 | WaterfallVillageCapital |
| `destiny_hub` | 1 | carte de départ |

---

## 3. Ce qui a été récupéré au-delà des cartes

### Le quiz de personnalité

Le dossier `quest_pmd_destiny/` de la branche
`arena/64113588-projet-creation-pmdo` contenait un prototype de Destiny avec le
quiz complet, qui n'existait nulle part ailleurs :

- `Data/Script/destiny/ground/personality_test/init.lua` (11 044 octets) —
  enchaînement complet : purge de l'équipe, 15 questions, calcul de la nature,
  badge étoile, choix du starter, sexe, talent, confirmation avec mention
  méga-évolution, choix du partenaire, saisie du nom ;
- `quiz_data.lua` (10 936 octets) — 15 questions, 16 natures, pool de starters ;
- `Data/quiz_personnalite_config.json` (15 359 octets) et
  `Data/quiz_personnalite_natures.json` (5 767 octets) ;
- `Content/UI/quiz_badges/` — **17 badges** de nature.

Ces fichiers sont copiés **tels quels** ; seul leur emplacement est aligné sur
le namespace `destiny` (`Script/destiny/ground/…`), ce que le moteur exige
(`LuaEngine.MAP_SCRIPT_PATTERN = "ground.{0}"` + namespace courant).

### Les cartes de cinématique

`intro_halo` (halo arc-en-ciel d'ouverture) et `reveil_nuit` (réveil nocturne,
13 783 octets de script) avec leurs fonds `Halo_*`, `Reveil_Nuit`, `Dream_*` et
`CLIFF_PICHU_NUIT_*` — 13 `.dir` récupérés.

### Le bourg de Métano

Six intérieurs `metano_gen_*` (accueil, café, casino, deux salons, maison) qui
exigeaient **185 tilesets** jusqu'ici absents de la Quest, dont beaucoup portaient
des noms de fichiers de téléchargement (`téléchargement (6)`, `télécharger (2)`).

---

## 4. Le problème technique qu'il a fallu résoudre

`Content/Tile/index.idx` n'est pas un cache facultatif : c'est un **`TileGuide`
binaire** qui associe chaque nom de TileSheet à la position en octets de chacune
de ses tuiles dans le `.tile` (`RogueEssence/Content/Indices/TileIndex.cs`).
`TileGuide.GetPosition` renvoie **0** pour une planche absente de l'index — la
tuile n'est tout simplement pas dessinée.

Ajouter 185 `.tile` sans toucher à cet index aurait donc donné 185 planches
invisibles. Le format a été décodé depuis le moteur et un outil écrit
(`tools/ajouter_tilesheets_index.py`) : il relit l'en-tête `TileIndexNode` de
chaque nouveau `.tile` et l'ajoute au `TileGuide` sans réécrire les planches.

Vérification : **1 640 entrées d'index pour 1 640 fichiers `.tile`**, aucun écart
dans les deux sens. L'outil a d'ailleurs révélé qu'un tileset de la branche
d'origine (1 323 fichiers pour 1 322 entrées) n'était pas indexé.

---

## 5. Ce qui reste réellement impossible à récupérer

### Les 12 salles de la guilde

Toujours aucun `.rsground`, dans aucune des 113 branches. Elles n'existent
qu'en calques PNG, sources Tiled et deux tilesets `GT2A_*`. La guilde est donc
représentée par 17 cartes réelles : les 13 intérieurs, `guilde_parvis`,
`guild_outside`, `guild_path_halcyon` et `guild_path`.

### Trois `TileSheets` — finalement fournis par la base

`GuildPath`, `InsideHut` et `TownBase` sont introuvables dans les dépôts mais
présents dans `base/Content/Tile/` : le mod en hérite, rien à copier.

### Trois cartes intégrées avec des décors incomplets

| Carte | Décor manquant | Conséquence |
|---|---|---|
| `treasure_town` | `AppleBounce`, `Totem_2`, `Totem_3`, `Totem_4` | la carte se charge, les 4 objets sont invisibles |
| `beach_cave_pit` | `RelicFragment` | la carte se charge, l'objet est invisible |
| `spindacafetest` | — | complet après récupération du tileset |

Ces animations n'existent dans aucun dépôt ni aucune branche. Elles ont été
cherchées nommément, pas supposées. Les cartes ont été conservées parce qu'elles
restent jouables ; le manque est cosmétique et traçable.

### Deux cartes volontairement écartées

- `treasure_cafe` : référence un TileSheet `Treasure_Town_Cafe` qui n'existe pas
  (seules les variantes `_Base`, `_Objects`, `_Objects_Fringe`, `_Objects_Over`,
  `_Objects_Under` existent). Corriger demanderait de modifier la donnée.
- `cliffnordouesttest1` : 6 tilesets introuvables, brouillon jamais livré.

### Hors périmètre, intact ailleurs

Port PMD Ciel (460 Grounds), mod New Era (276 Grounds), campagnes PMD Rouge et
PMD Ciel (`dev/CAMPAIGNS/`, 2 470 fichiers de cinématiques), adaptations KLOA et
No Name Village : ces ensembles appartiennent à d'autres projets et ne sont pas
mélangés à la Quest.

---

## 6. Contrôles passés

- 303 Grounds relus intégralement (3,15 Go) : **0 TileSheet manquant**, 0 planche
  hors index.
- 10 zones ↔ 10 fichiers ↔ 10 entrées d'index : aucun écart ; tous les Grounds
  cités par une zone existent (sauf `WaterfallVillageCapital`, restauré à part).
- 303 scripts de Ground présents, un par carte.
- `WaterfallVillageCapital` : 233 727 831 octets, empreinte SHA-256 vérifiée
  après restauration depuis `ressources/`.
