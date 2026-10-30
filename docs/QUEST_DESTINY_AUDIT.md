# Quest Destiny — audit des sources

Relevé effectué le 30 octobre 2026 sur l'ensemble des dépôts accessibles de
`meromoonmeri`, à partir de clones partiels (`--filter=blob:none`), sans
modification d'aucun dépôt source.

Version cible : **PMDO 0.8.12** (`RogueEssence`, format de données `0.8.12.0`).

---

## 1. Le dépôt cible

`meromoonmeri/PMDO-Destiny` (privé, branche `main`, commit `5710537`) n'est pas
un simple mod : il contient le moteur (`engine/`), les données PMDO de base
(`base/`) et la Quest (`game/`).

| Élément | Contenu avant cette passe |
|---|---|
| `game/Mod.xml` | Quest `destiny`, UUID `746CBBCD-426F-5419-A735-D50248440935`, version 0.1.0 |
| `game/Data/Ground/` | 1 fichier — `destiny_hub.rsground` |
| `game/Data/Zone/` | `destiny_hub.json` + `index.idx` (1 entrée) |
| `game/Data/Script/destiny/` | `scriptvars.lua` + `ground/destiny_hub/init.lua` |
| `game/Content/` | `UI/Title.png` uniquement |
| `docs/VALIDATION.md` | campagne de validation du 24 octobre 2026 |

La Quest existait donc comme **socle technique** : une zone, un Ground vide de
toute issue, aucun tileset propre. Aucune carte n'y avait encore été intégrée.

---

## 2. Cartographie des sources explorées

| Dépôt | Nature | Fichiers | `.rsground` | Tilesets | Remarque |
|---|---|---:|---:|---:|---|
| `projet-creation-pmdo` (branche `arena/2a041d50`) | atelier de méthode : 208 sous-projets, générateurs Python, rendus, calques | 3 751 | 13 | 110 `.tile` | copie allégée de `projet-pmdo` (169 Mo au lieu de 6 Go) |
| `guilde-treehouse-pmd` | miroir « Guilde Treehouse » : 12 salles, calques, planches | 13 684 | 10 | 33 hors références | rendus 4,4 Go inclus |
| `projet-pcp` → `PROJET-PMD` (privé) | fork complet de Halcyon enrichi : campagnes, adaptations KLOA / No Name Village, 779 Grounds | 41 027 | 1 840 | 1 675 | `.rsground` en **Git LFS** |
| `town02` | même lignée Halcyon, jeu complet | 32 916 | 1 620 | 1 774 | `.rsground` en **Git LFS**, contient `WaterfallVillageCapital` |
| `projet-pmdo` | dépôt source d'origine (6 Go de rendus) | 41 868 | 13 | — | même contenu méthode que `projet-creation-pmdo` |
| `new-era-project` | mod français distinct, 276 Grounds | 3 551 | 276 | — | projet séparé |
| `PMD-SKY-PMDO-PORT` | port de PMD Ciel | 1 532 | 460 | — | projet séparé |
| `Palikadude/Halcyon` | **modèle d'organisation** | 1 299 | 37 | 181 | 14 zones, 677 scripts |

### Ce que l'atelier `projet-creation-pmdo` contient réellement

Les 208 sous-projets de `source/` sont des **chantiers** : générateur, tests,
documentation, rendus. La colonne « Ground / tileset » de `INDEX_METHODES.md`
n'est vraie que pour **huit** d'entre eux, et les Grounds livrés se trouvent dans
leur dossier `references/` :

| Sous-projet | Grounds livrés | TileSheets associés |
|---|---|---|
| `cote_v5_expeditions` | `Brine_Cave_Entrance`, `drenched_bluff_entrance`, `crooked_cavern_entrance` | 6 |
| `cafe_multietage_v1` | `spinda_cafe`, `metano_cafe`, `treasure_cafe` | 8 |
| `cafe_multietage_v3` | `guild_second_floor` | 8 |
| `antre_harmonie_v3` | `altere_pond` | 9 |
| `amp_plains_fleurie_v1` | `vast_steppe_entrance` | 7 |
| `ledian_dojo_v1` | `ledian_dojo` | 7 |
| `soleil_spring_v1` | `luminous_spring` | 2 |
| `viewport_pmdo_v1` | `crooked` | 3 |

Ces huit lots ont été produits à partir du 8 px natif, avec calques et PNG de
provenance — c'est le travail directement récupérable.

### Les 12 salles « Guilde Treehouse »

`salles/01_accueil` … `salles/12_salle_chef` existent sous forme de :
PNG jour/nuit, 11 calques séparés par salle (264 fichiers), vues de fenêtres
(84 fichiers), sources Tiled `tiled/01_jour.tmj` … `tiled/12_nuit.tmj`.

**Aucun `.rsground` n'existe pour ces 12 salles**, dans aucun dépôt. Les seuls
tilesets liés sont `GT2A_01_citadelle_qg_guilde_Jour.tile`,
`GT2A_01_citadelle_qg_guilde_Nuit.tile` et `salle_jour.tile` (dans `PROJET-PMD`).
La conversion Tiled → Ground n'a jamais été faite.

---

## 3. Méthode d'analyse

1. Clonage partiel sans blobs des neuf dépôts pertinents.
2. Index global des ressources par nom de base : **2 907 TileSheets**, plus les
   `Data/AutoTile/*.json`, `Content/Object/*.dir`, `Content/Chara`, `Content/BG`,
   `Content/Music`.
3. Extraction, pour chaque `.rsground`, de toutes les références réelles :
   `Tiles[].Layers[].Frames[].Sheet`, `AutoTileset`, `AnimIndex`, `Music`,
   `MapChars` (analyse JSON ; pour `WaterfallVillageCapital`, 228 Mo, extraction
   en flux par expression régulière pour rester sous 2 Go de RAM).
4. Résolution de chaque référence dans l'index, avec préférence pour le dépôt
   d'origine du Ground.
5. Récupération des blobs manquants et des objets **Git LFS** (`town02`,
   `PROJET-PMD`) via l'API LFS.
6. Comparaison par empreinte des Grounds présents dans plusieurs dépôts.

### Doublons constatés

| Ground | Dépôts | Verdict |
|---|---|---|
| `crooked_cavern_entrance` | Halcyon, `pcp` | identiques (`md5 bcbc1d50`) |
| `guild_second_floor` | Halcyon, `pcp` | identiques (`md5 8c1d9111`) |
| `ledian_dojo` | Halcyon, `pcp` | identiques (`md5 3d5f27ee`) |
| `luminous_spring` | Halcyon, `pcp` | identiques (`md5 97c41ba9`) |
| `altere_pond` | Halcyon (`0.7.4`, 9 940 Ko) et `pcp` (`0.8.9`, 9 949 Ko) | **versions différentes** : la version `0.8.9` livrée par les agents a été retenue |

Aucun Ground n'a été écrasé silencieusement : la provenance et l'empreinte
SHA-256 de chacun figurent dans `rapports/manifeste_quest.json`.

---

## 4. Périmètre retenu

Décision du porteur du projet : **cœur Destiny** — la guilde, les lots livrés par
les agents, et `WaterfallVillageCapital`. Les campagnes PMD Rouge / PMD Ciel, les
276 Grounds de `new-era-project` et les 460 Grounds du port Sky restent hors
périmètre et ne sont pas mélangés à la Quest.

24 Grounds ont été intégrés (voir `QUEST_DESTINY_ORGANISATION.md`), soit
**142 TileSheets** et **7 animations d'objets** récupérés, plus la base PMDO qui
fournit `InsideHut` et `Banana_Yellow`.
