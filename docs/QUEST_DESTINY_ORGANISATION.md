# Quest Destiny — organisation des fichiers

## 1. Ce que l'étude de Halcyon a réellement montré

`Palikadude/Halcyon` (branche `main`, commit `da6c213`) est une Quest PMDO
complète. Son arborescence a été relevée fichier par fichier, pas supposée :

```text
Halcyon/
├── Mod.xml                       Namespace halcyon · ModType Quest · version 0.4.0
├── Data/
│   ├── Ground/     37 .rsground            (aucun index : le dossier fait foi)
│   ├── Zone/       14 .json + index.idx    (index.idx obligatoire)
│   ├── Tile/        6 .json                (données de tuiles, pas des planches)
│   ├── Map/        13 .json                (segments de donjon)
│   ├── AutoTile/    9 .json
│   └── Script/    677 fichiers             ground/<map>/init.lua + chapitres
├── Content/
│   ├── Tile/      181 .tile                ← LES TILESETS SONT ICI
│   ├── Object/     17 .dir
│   ├── BG/  Chara/ Portrait/ Music/ Item/ Sound/ UI/ Particle/
│   └── ContentParams.xml
└── Strings/
```

Deux conventions sont à retenir, parce qu'elles ne sont pas intuitives :

1. **Un tileset est un seul fichier** `Content/Tile/<Nom>.tile`, **autonome** :
   les PNG sont embarqués dans le binaire (chunks `IHDR`/`IDAT`/`IEND`
   concaténés). Il n'existe **aucun PNG voisin** : `Content/Tile/` de Halcyon
   contient 181 `.tile` et un `index.idx`, rien d'autre. Un Ground n'a donc
   jamais besoin d'une « planche » séparée.
2. **`Data/Tile/*.json` n'est pas un tileset.** C'est une donnée de tuile
   (escaliers, coffres, panneaux). Ne pas confondre avec `Content/Tile/*.tile`.

Les références d'un Ground sont portées par son JSON :

| Champ du `.rsground` | Cible |
|---|---|
| `Tiles[].Layers[].Frames[].Sheet` | `Content/Tile/<Sheet>.tile` |
| `AutoTileset`, `BlankBG.AutoTileset` | `Data/AutoTile/<nom>.json` |
| `AnimIndex` (décorations, entités) | `Content/Object/<nom>.dir` (ou `Content/Item/`) |
| `Music` | `Content/Music/<nom>.ogg` |
| `MapChars` | `Content/Chara/<id>.chara` |
| `Background.BGAnim.AnimIndex` | `Content/BG/<nom>.dir` |

Le nom du fichier **est** l'identifiant du Ground, et `Object.AssetName` doit lui
correspondre. C'est ce contrôle qui a été appliqué à chaque import.

Enfin, Halcyon groupe plusieurs Grounds par zone (`apricorn_grove` →
`GroundMaps: ["apricorn_grove_entrance", "apricorn_glade"]`) et possède une zone
de débogage `master_zone` qui liste tous ses Grounds.

## 2. Structure retenue pour Destiny

```text
game/
├── Mod.xml
├── Data/
│   ├── Ground/    25 .rsground   (24 importés + destiny_hub)
│   ├── Zone/      25 .json + index.idx (25 entrées)
│   ├── Script/destiny/
│   │   ├── scriptvars.lua
│   │   └── ground/<map>/init.lua   (25 scripts minimaux)
│   └── StartParams.xml             (inchangé : départ sur destiny_hub)
├── Content/
│   ├── Tile/      142 .tile        (tilesets récupérés, dédoublonnés)
│   ├── Object/      7 .dir
│   └── UI/Title.png
├── Strings/
ressources/
└── WaterfallVillageCapital.rsground.gz
tools/
└── restaurer_waterfall.py
```

### Choix d'organisation

- **Une seule Quest**, `destiny`. Aucune seconde Quest n'a été créée.
- **Chaque carte reste un `.rsground` individuel.** Aucune fusion de cartes,
  aucune carte composite : les 25 fichiers sont indépendants et portent leur nom
  d'origine.
- **Dossiers Map / Ground** : `Data/Ground/` reçoit les Grounds, `Content/Tile/`
  les tilesets. `Data/Map/` n'est pas créé : aucune carte de donjon (segment
  procédural) n'entre dans ce périmètre ; les 24 cartes sont des Grounds fixes.
- **Un tileset n'est copié qu'une fois.** Les 142 fichiers sont dédoublonnés par
  nom et par contenu ; aucun conflit de contenu n'a été rencontré (le script
  d'assemblage s'arrête si deux dépôts proposent des octets différents pour un
  même nom).
- **Zones** : une zone par Ground, `Released: true`, `Rogue: 0`, `Segments: []`,
  `GroundMaps: [<ground>]`, exactement la forme utilisée par `destiny_hub` et par
  les zones de bourg de Halcyon. `index.idx` est régénéré avec ces 25 entrées.
- **Scripts** : un `init.lua` minimal par Ground (rappels `Init`, `Enter`,
  `GameLoad`, `Update`). **Aucun script de Halcyon n'a été recopié** : ceux de
  Halcyon font `require 'ground.<map>.<map>_ch_N'` et dépendent de
  `SV.ChapterProgression`, `PartnerEssentials`, `SV.metano_town`… Les importer
  aurait créé une dépendance cachée à un autre mod, ce que le projet interdit.
  Les cartes sont donc intégrées **avec leurs données**, pas avec leur scénario.
- **Aucune dépendance externe** : la Quest ne référence que `origin.common`
  (fourni par la base PMDO) et ses propres fichiers.

### Renommage normalisé (2 cas)

Deux Grounds du lot `cote_v5_expeditions` portaient un `AssetName` interne sans
le préfixe de provenance :

| Fichier source | `AssetName` interne | Nom retenu |
|---|---|---|
| `ExplorersOfSkyOrigins__Brine_Cave_Entrance.rsground` | `Brine_Cave_Entrance` | `Brine_Cave_Entrance.rsground` |
| `ExplorersOfSkyOrigins__drenched_bluff_entrance.rsground` | `drenched_bluff_entrance` | `drenched_bluff_entrance.rsground` |

Le nom de fichier a été aligné sur le nom interne, conformément à la règle
PMDO — et non l'inverse, qui aurait modifié la donnée.

## 3. Inventaire des 24 Grounds importés

| Groupe | Ground | Source | Taille | TileSheets |
|---|---|---|---:|---:|
| guilde | `guild_first_floor` | Halcyon | 297 Ko | 1 |
| guilde | `guild_second_floor` | Halcyon | 3 856 Ko | 8 |
| guilde | `guild_third_floor_lobby` | Halcyon | 4 626 Ko | 7 |
| guilde | `guild_bedroom_hallway` | Halcyon | 1 131 Ko | 4 |
| guilde | `guild_heros_room` | Halcyon | 1 412 Ko | 6 |
| guilde | `guild_dining_room` | Halcyon | 1 540 Ko | 7 |
| guilde | `guild_guildmasters_room` | Halcyon | 1 612 Ko | 6 |
| guilde | `guild_storage_hallway` | Halcyon | 1 173 Ko | 4 |
| guilde | `guild_storage_room` | Halcyon | 1 733 Ko | 8 |
| guilde | `guild_top_left_bedroom` | Halcyon | 1 218 Ko | 5 |
| guilde | `guild_top_right_bedroom` | Halcyon | 1 280 Ko | 5 |
| guilde | `guild_bottom_left_bedroom` | Halcyon | 1 435 Ko | 6 |
| guilde | `guild_bottom_right_bedroom` | Halcyon | 1 438 Ko | 5 |
| guilde | `guilde_parvis` | PROJET-PMD | 2 054 Ko | 1 |
| entrees | `crooked_cavern_entrance` | Halcyon | 496 Ko | 3 |
| entrees | `Brine_Cave_Entrance` | pcp | 997 Ko | 1 |
| entrees | `drenched_bluff_entrance` | pcp | 1 308 Ko | 2 |
| entrees | `vast_steppe_entrance` | pcp | 2 493 Ko | 6 |
| entrees | `altere_pond` | pcp (v0.8.9) | 9 949 Ko | 9 |
| donjons | `ledian_dojo` | pcp | 1 301 Ko | 7 |
| donjons | `luminous_spring` | pcp | 585 Ko | 2 |
| bourg | `spinda_cafe` | pcp | 1 633 Ko | 2 |
| bourg | `metano_cafe` | Halcyon | 1 348 Ko | 6 |
| capitale | `WaterfallVillageCapital` | town02 | 228 Mio | 36 |

## 4. WaterfallVillageCapital

Le Ground fait **233 727 831 octets** (2 800 002 couches de tuiles, 37
références `Sheet`, `Version 0.8.12.0`, `TexSize 1`). Il est stocké en Git LFS
dans `town02` ; il a été téléchargé par l'API LFS et **n'a subi aucune
transformation** : structure, dimensions, couches, tuiles et références
conservées.

Ses 36 TileSheets (hors chaîne vide) ont toutes été retrouvées, y compris les
noms non conventionnels `CLIFF MIROR-Photoroom`, `patwhay`, `tiles8_0058` ou
encore `kzKLPRyU8on31…` (un data-URI collé comme nom de tileset). Elles sont
copiées depuis `town02`, le dépôt d'origine de la carte.

GitHub refuse tout fichier de plus de 100 Mio et le dépôt a fait le choix
documenté de ne pas utiliser Git LFS (`docs/ARCHITECTURE.md`,
`tools/validate.py`). Le Ground est donc versionné **compressé sans perte** :

```bash
python tools/restaurer_waterfall.py
# restauré : game/Data/Ground/WaterfallVillageCapital.rsground
#            (233727831 octets, sha256 vérifié)
```

L'archive pèse 1,4 Mio (facteur 152) et la restauration reproduit le fichier
d'origine à l'octet près, empreinte `afc5081f7348b2af…` comparée à celle publiée
dans `town02`.

## 5. État de la Quest

- 25 Grounds, 25 zones, 25 scripts, 142 tilesets, 7 animations d'objets.
- `destiny_hub` reste la zone de départ (`Data/StartParams.xml` inchangé) ; les
  24 nouvelles zones sont accessibles depuis le menu de débogage de PMDO.
- Aucun fichier de la Quest d'origine n'a été supprimé ni réécrit.
- Le seul fichier modifié est `game/Mod.xml` (version et description).
