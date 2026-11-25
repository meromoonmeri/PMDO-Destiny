# Import des cartes de l'atelier `guilde-treehouse-pmd` — rapport d'audit

**Date : 26 octobre 2026.** Objectif : rendre présentes dans Destiny toutes les
cartes PMDO **créées par l'auteur** dans son dépôt atelier
[`meromoonmeri/guilde-treehouse-pmd`](https://github.com/meromoonmeri/guilde-treehouse-pmd)
(**toutes branches** confondues), avec leurs dépendances, en ne conservant que
**la dernière version de chaque lieu**. Les cinématiques sont volontairement
reportées (décision de l'auteur) : les cartes arrivent avec des scripts
squelettes, sans transitions ni raccordements.

## 1. Méthode (preuve avant hypothèse)

1. **Filtre de provenance (étape 0)** sur le dépôt source : pas de `LICENSE`,
   contenu mixte (créations de l'auteur + cartes de référence tierces rangées
   dans des dossiers `references/` + extractions de jeux commerciaux en
   documents d'étude). Arbitrage de l'auteur : *« toutes mes création map et
   ses dépendances »* → import des seules créations + dépendances, exclusion
   documentée du reste (voir §5).
2. **Inventaire exhaustif** sans télécharger les ~12,8 Go du dépôt : clone
   *blobless* (métadonnées, 4,9 Mo), listage des 83 branches, des 402 chemins
   `.zip` et de toutes les occurrences `.rsground`/`.rsmap`.
3. **Audit unitaire** des 315 contenus de cartes distincts (sha256) : JSON
   parsé, `AssetName`, version de sérialisation, `TexSize`, titre, dimensions,
   références `Sheet` / `AnimIndex` / `Music` / `Status` / espèces / callbacks.
4. **Sélection par lieu** (doctrine §3), **extraction octet pour octet**,
   résolution des dépendances (même ZIP > même dossier > arbre global),
   reconstruction de `game/Content/Tile/index.idx` depuis les en-têtes `.tile`
   — vérifié **octet pour octet** contre l'index source du pack Expéditions
   (même construction que `ImportHelper.BuildTileIndex` du moteur).
5. **Validation** : `tools/validate.py` étendu (déclarations de zones, index,
   scripts présents, nœuds de tuiles) — `VALIDATION OK`.

## 2. Résultat chiffré

| Élément | Valeur |
|---|---:|
| Contenus de cartes audités (toutes branches) | 315 |
| Cartes au sol importées (`game/Data/Ground/`) | **228** (+ `destiny_hub` déjà présent) |
| Carte de donjon importée (`game/Data/Map/frozen_crucible.rsmap`) | 1 |
| Banques de tuiles (`game/Content/Tile/*.tile`) | **1 023** (719 Mio) + `index.idx` fusionné |
| Fonds/objets `.dir` (`game/Content/BG|Object/`) | 102 (23,7 Mio) |
| Scripts squelettes `destiny/ground/<carte>/init.lua` | 228 |
| Nouvelles zones | 3 (`cotes_metano` 84, `ateliers_donjons` 133, `reverie` 11) |
| Conflits de noms de feuilles | **0** |
| Dépendances introuvables | 5 (voir §6) |
| Volume cartes importées | 2 507 Mio de JSON (fortement compressibles par Git) |

Les cartes importées gardent leur `AssetName` d'atelier (copies octet pour
octet, chaîne de provenance intacte). Un renommage « univers Destiny » pourra
être fait plus tard, carte par carte, lors des raccordements ; leurs titres
affichés sont déjà en français.

## 3. Doctrine de sélection (« dernière version de chaque lieu »)

1. **Chaînes de versions explicites** (même code, numéro croissant) → dernière
   seule : `AGM1→3`, `TMA1→3`, `EMB8→9`, `FMB8→9`, `FGG1→2`, `ESP1→2`, `ESN1→2`,
   `EWC1→3`, `ECN1→2` (cascade), `ZRV1→2`, `IA2→IA3`, `beach_cave_entrance v2→v3`.
2. **Générations renommées prouvées** (documentation de l'atelier, titres et
   dimensions identiques) → dernière seule : côtes `v30812_*` remplacées par
   `v40812_*` (correction V4) ; côtes V2 d'origine remplacées par
   `cote10_v2_*` ; Reverie Town v1 → v2 ; duos viewport `vp1_*` et rendus
   `vp1_fd1_*` remplacés par `dn1_*` ; Zone Zéro v1 (`raz*`, `eaz1`) remplacée
   par la refonte fleurie (`raf*`, `eaf1`) ; entrée Amp série 1 remplacée par
   `s2ap1` (série 2) ; sentier de la guilde : seule la version finale
   chargeable (« texture swap ») est retenue.
3. **Codes distincts = lieux/scènes distincts** → importés même si le thème est
   proche (ex. trois prises « Dark Crater » `ecf1`/`edp1`/`ecm1`, `ecc1` +
   `ecc2`, `ejs1` + `ejs2`, `eff1` + `eff2`, lots SN v3/v4 *et* série E).
4. **Paires jour/nuit** importées ensemble ; **prototypes** rattachés à un lieu
   livré exclus (`cliffdaytest`, `cliffnordouesttest1` → Reverie Town).
5. **Doute non tranchable** → importer et signaler (consigne dominante :
   « toute mes création map »).

86 contenus ont été exclus pour ces motifs (anciennes versions), plus les
exclusions de provenance du §5. Tous restent récupérables dans le dépôt
atelier ; le présent rapport et `import_work/selection.json` (atelier local)
gardent la trace de chaque décision.

## 4. Zones créées

La zone `destiny_hub` et son index 0 sont intacts (point de départ inchangé).

| Zone | GroundMaps | Contenu |
|---|---:|---|
| `cotes_metano` — « Côtes de Métano » | 84 | Lots `cote10_*` (24, dont les deux côtes V2 refondues), `cote20_*` (20), `v40812_*` (20), `v50812_*` (20, dont 3 entrées avec marqueur `donjon_seuil`) |
| `ateliers_donjons` — « Seuils, arènes et fonds de donjons » | 133 | Entrées sud→nord série E, fins série F, duos `dn1_*` (44), zones amies `vp1_fa1_*`, grotte brumeuse, arènes (Groudon, Terapagos, glace boréale, Thunder Meadow…), lots SN v3/v4, plages, Canonia, Zone Zéro, série 2 |
| `reverie` — « Reverie Town, la guilde et la clairière » | 11 | `rvt2_*` (4), `guild_path`, `clairiere`, `pmd_petal_clearing`, zone de réveil `zrv2_*` (4) |

`frozen_crucible.rsmap` est déposé dans `game/Data/Map/` **sans segment de
donjon qui l'utilise** : fichier inerte tant qu'aucune zone ne le référence.

## 5. Provenance : écarté au filtre (étape 0)

- **Cartes de référence tierces** (dossiers `references/` de l'atelier) :
  ExplorersOfSkyOrigins et lieux des jeux commerciaux — jamais importées,
  conformément à l'exclusion ferme du projet.
- **Références embarquées dans certains packs** : `altere_pond.rsground` et
  `vast_steppe_entrance.rsground`, identifiées par sha256 comme les copies de
  référence projet de Palikadude → exclues.
- **Fichiers non chargeables** : `guild_path_<référence>_layers` et
  `guild_path_<référence>_palika` (JSON sans enveloppe `{Version, Object}`,
  `TexSize=24` brut) ; `plage_pmd_sky_large.rsground` (descripteur JSON de
  789 o, pas un `GroundMap`).
- Crédits détaillés (projet de Palikadude/Palika et mention « Reverie Town
  (waterfallvillagecapital) » de l'auteur, filtre Abyss, DumpAsset, cellules
  DTEF, SpriteCollab) : voir [`CREDITS.md`](../CREDITS.md).

**Point d'attention tuiles** : la matière « Métano » provient des planches
`Metano_Town_*` / `Vast_Steppe_*` transitant par projet de Palikadude (aucune licence
publique trouvée) — accord de Palika à confirmer avant redistribution.

## 6. Dépendances non résolues (5)

Rien ne bloque le chargement des cartes, mais ces références resteront muettes
ou inactives tant qu'elles ne sont pas fournies (elles existent vraisemblablement
dans l'installation/le projet New Era de l'auteur) :

| Référence | Type | Cartes concernées |
|---|---|---|
| `steam` | MapStatus (`game/Data/MapStatus/steam.json`) | `frozen_crucible` |
| `Boss Battle!.ogg` | Musique | `frozen_crucible` (+ callbacks Lua `LuaBeginBattleEvent`, `LavaFlowHandler` hérités du projet d'origine) |
| `BGM_DUN_BeachCave` | Musique | 3 plages `v50812_beach_*` |
| `Brine Cave.ogg` | Musique | `plage_cv2_anse`, `plage_cv2_crique` |
| `Sky Peak Prairie.ogg` | Musique | `pmd_petal_clearing` |

Aucun autre manque : 1 023/1 023 feuilles et 102/102 `.dir` résolus, aucune
espèce inconnue de la base, aucun callback script dans les cartes au sol.

## 7. Avertissements techniques

- **Sérialisations anciennes** : 131 cartes en `0.8.12.0`, mais **98** en
  formats antérieurs (52 en `0.7.15.1` — `dn1_*`, `vp1_*`… ; 44 en `0.7.4.0` —
  `cote10_*`/`cote20_*` ; 2 en `0.8.9.0`). RogueEssence migre en principe ces
  formats au chargement, mais **chacune doit être ouverte dans PMDO 0.8.12**
  pour confirmation (et ré-enregistrée si le moteur le propose).
- **Collisions libres** sur la plupart des bases côtières (`Tags = 0` dans
  l'atelier) : à dessiner avant tout usage jouable. Les entrées `v50812_*` ont
  des collisions de base générées, à vérifier en mouvement.
- **`Released = false`** sur beaucoup de cartes d'atelier : ce sont des bases
  d'édition, pas des niveaux finalisés.
- **Plages `v50812_beach_*`** : le champ `Name` y est une chaîne simple (et non
  un objet `LocalizedText`) ; toléré à la lecture normalement, à confirmer.
- **Pièces de la guilde (les 12 salles)** : elles n'existent dans l'atelier
  qu'en calques PNG, pas en `GroundMap` — rien à importer en l'état ; leur
  construction en cartes reste à faire (chantier séparé).
- **Aucune transition** n'a été créée : les cartes ne sont pas encore
  atteignables en jeu depuis `destiny_hub` (accès par l'éditeur Ground ou la
  console dev). Les seuils `donjon_seuil` des trois entrées `v50812_08/09/10`
  sont documentés dans `RACCORDEMENT_DONJONS.json` du pack source, sans
  destination configurée.

## 8. Tests à faire en jeu (impossibles depuis le sandbox)

1. Ouvrir dans PMDO Dev 0.8.12 un échantillon par famille : `v40812_01_cap_large_jour`,
   `cote10_01_long_cap_jour` (ancienne sérialisation), `cote20_11_anses_jumelles_jour`,
   `v50812_08_antre_crochu_jour`, `dn1_volcan_entree`, `rvt2_ne_jour`,
   `guild_path`, `clairiere`, `pmd_petal_clearing`, `emb9_entree_mt_blaze`,
   `canon1_TC1_entree_jour`, `v50812_beach_cave_entrance_v3`, `zrv2_zone_reveil_jour`.
2. Pour chaque : rendu des calques (rien de magenta/vide), jour **et** nuit,
   animations (mer 8 phases, nuages, eau), marqueur d'entrée atteignable,
   pas de personnage traversant paroi/mer.
3. Vérifier spécialement les anciennes sérialisations (0.7.x) et les plages
   (champ `Name` en chaîne).
4. Construire le ZIP Windows (`tools/build_windows.py`) et lancer une partie :
   l'écran-titre puis `destiny_hub` doivent rester inchangés.

## 9. Commits de l'import

Import effectué sur la branche `arena/c40fd96f-pmdo-destiny`, par domaines :
banques de tuiles/fonds → cartes → zones/scripts → documentation/validation.
Provenance machine (occurrences, sha256, choix de sources) : générée pendant
l'atelier d'import (non versionnée : `import_work/`, régénérable par les
scripts `audit_pipeline.py`, `select.py`, `extract.py`, `assemble.py`).
