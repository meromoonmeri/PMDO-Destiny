# Quest Destiny — ressources manquantes et non intégrées

Aucun remplacement n'a été fabriqué. Chaque manque est documenté avec sa
référence exacte, le fichier qui la porte et les fichiers voisins retrouvés.

---

## 1. Les 12 salles « Guilde Treehouse » — aucun Ground n'existe

C'est le manque principal du périmètre demandé.

| Salle | Ressources retrouvées | Ground |
|---|---|---|
| `01_accueil` | 11 calques jour + 11 nuit, PNG salle jour/nuit, `tiled/01_jour.tmj`, `tiled/01_nuit.tmj`, 7 vues de fenêtres | **absent** |
| `02_hall_missions` | idem | **absent** |
| `03_salle_commune` | idem | **absent** |
| `04_cantine` | idem | **absent** |
| `05_chambre_equipe` | idem | **absent** |
| `06_chambre_veilleur` | idem | **absent** |
| `07_chambre_residents` | idem | **absent** |
| `08_dortoir_trio` | idem | **absent** |
| `09_dortoir_quatre` | idem | **absent** |
| `10_dortoir_trio` | idem | **absent** |
| `11_chambre_eclaireurs` | idem | **absent** |
| `12_salle_chef` | idem | **absent** |

Emplacements des ressources (dépôts `projet-creation-pmdo` et
`guilde-treehouse-pmd`, contenu identique) :

- `salles/<NN_nom>/jour/*.png` et `salles/<NN_nom>/nuit/*.png`
- `calques/<NN_nom>/{jour,nuit}/00_exterieur.png` … `10_bordure_avant.png` (264 fichiers)
- `fenetres_exterieur/<NN_nom>/*.png` (84 fichiers)
- `tiled/<NN>_{jour,nuit}.tmj` (24 fichiers)

Tilesets liés, présents uniquement dans `PROJET-PMD` :

- `Content/Tile/GT2A_01_citadelle_qg_guilde_Jour.tile`
- `Content/Tile/GT2A_01_citadelle_qg_guilde_Nuit.tile`
- `Content/Tile/salle_jour.tile`

**Pourquoi elles ne sont pas dans la Quest** : aucun `.rsground` n'existe dans
aucun dépôt, et la conversion Tiled → Ground n'a jamais été faite. Produire ces
12 Grounds serait un développement de cartes, explicitement hors du mandat
(« tu ne dois pas recommencer le développement des cartes à partir de zéro »).
Les ressources sont intactes et inventoriées ci-dessus, prêtes pour une passe de
conversion.

En attendant, la guilde est représentée dans la Quest par les 13 Grounds
d'intérieur de Halcyon et par `guilde_parvis` — les seules cartes de guilde
complètes et chargeables qui existent.

---

## 2. `treasure_cafe` — TileSheet référencé introuvable

- Fichier : `projet-creation-pmdo:source/cafe_multietage_v1/references/treasure_cafe.rsground`
- Référence manquante : `Tiles[].Layers[].Frames[].Sheet == "Treasure_Town_Cafe"`
- Recherche effectuée : index global de 2 907 TileSheets, aucun `Treasure_Town_Cafe.tile`
- Fichiers voisins réellement présents dans le même dossier :
  `Treasure_Town_Cafe_Base.tile`, `Treasure_Town_Cafe_Objects.tile`,
  `Treasure_Town_Cafe_Objects_Fringe.tile`, `Treasure_Town_Cafe_Objects_Over.tile`,
  `Treasure_Town_Cafe_Objects_Under.tile` (+ PNG correspondants)

Le nom référencé n'est le nom d'aucune de ces planches : la référence est
cassée à la source. La carte n'a pas été intégrée et n'a **pas** été corrigée
d'office (un renommage de `Sheet` changerait la donnée).

## 3. `guildcliff` — TileSheet introuvable et AssetName vide

- Fichier : `PROJET-PMD:Data/Ground/guildcliff.rsground` (280 Ko, `Version 0.8.12.0`)
- Référence manquante : `Sheet == "télécharger (6)"` (nom de fichier de
  téléchargement, jamais renommé)
- `Object.AssetName` est vide, `TexSize` vaut 3
- Aucun `.tile` de ce nom dans les neuf dépôts

## 4. Coquilles de Ground sans contenu

Ces fichiers existent mais ne contiennent qu'une tuile de remplissage
(`Sheet == "debug_placeholder_Base"`, `TexSize 1`) : ce ne sont pas des cartes.

| Fichier | Emplacement |
|---|---|
| `guild_hut.rsground` | `PROJET-PMD:Data/Ground/` |
| `guild_path.rsground` | `PROJET-PMD:Data/Ground/` |
| `guildmaster_summit.rsground` | `PROJET-PMD:Data/Ground/` |

## 5. Cartes d'essai à la racine de l'atelier

| Fichier | Références manquantes |
|---|---|
| `cliffdaytest.rsground` | `01_long_cap_jour_02`, `13_avancee_basse_gauche_terrain`, `Treasure_Town_Animated`, `Treasure_Town_Trimmed`, `v2_promontoire_jour_03` |
| `cliffnordouesttest1.rsground` | `Treasure_Altere_Transition_Base`, `terrain`, `terrain (2)`, `terrain (3)`, `terrain (4)`, `v2_promontoire_jour_03` |

Ce sont des brouillons (`Comment` vide, `Released: false`), jamais livrés.

---

## 6. Faux manquants — vérifiés et finalement fournis par la base PMDO

| Référence | Résolution |
|---|---|
| `InsideHut` (TileSheet de `destiny_hub`) | `base/Content/Tile/InsideHut.tile` |
| `Banana_Yellow` (animation de `guild_dining_room`) | `base/Content/Item/Banana_Yellow.dir` |

Ces deux ressources ne sont donc pas dupliquées dans la Quest : c'est le
comportement attendu d'un mod PMDO, qui hérite du `base/`.

---

## 7. Hors périmètre de cette passe (documenté, non traité)

| Élément | Emplacement | Volume |
|---|---|---|
| Cinématiques PMD Rouge | `PROJET-PMD:dev/CAMPAIGNS/PMD_RED_RESCUE_TEAM/` (`Cinematics/*.cif.json`, `DIALOGUES_INDEX.json`, `EVENT_SCRIPTS_INDEX.json`) | 1 234 fichiers |
| Cinématiques PMD Ciel | `PROJET-PMD:dev/CAMPAIGNS/PMD_SKY_EXPLORERS/` | 1 236 fichiers |
| Grounds de guilde PMD Ciel | `PROJET-PMD:Data/Ground/sky_wigglytuff_guild_entrance.rsground`, `…_main.rsground` (TileSheets `G01p03a_Base`, `G01p04a_Base` présents) | 2 Grounds |
| Port PMD Ciel | `PMD-SKY-PMDO-PORT` | 460 Grounds |
| Mod « New Era » | `new-era-project` | 276 Grounds |
| Adaptations KLOA / No Name Village | `PROJET-PMD:dev/` | 1 810 + 1 138 fichiers |

Ces ensembles appartiennent à d'autres projets et ne sont pas mélangés à la
Quest `destiny`. Les cinématiques seront traitées dans une passe dédiée.
