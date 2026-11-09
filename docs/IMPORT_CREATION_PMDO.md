# Import des cartes de l'atelier `projet-creation-pmdo` — rapport final

**Date : 27 octobre 2026.** Objectif (tâche D) : récupérer dans Destiny les
cartes créées par l'auteur dans son atelier
[`meromoonmeri/projet-creation-pmdo`](https://github.com/meromoonmeri/projet-creation-pmdo)
qui n'y étaient pas encore, **avec leurs animations et dépendances
complètes**, rangées par thème. Périmètre arbitré par l'auteur :
« nouveautés + cartes des Chapitres I/II de Destiny », falaise `cliffdaytest`
en carte seule (cinématique reportée en Partie 2), rangement par thème.
Comme pour la tâche A ([`IMPORT_GUILDE_TREEHOUSE.md`](IMPORT_GUILDE_TREEHOUSE.md)),
les cartes arrivent avec des scripts squelettes, sans raccordement au hub.

## 1. Méthode (preuve avant hypothèse)

1. **Filtre de provenance (étape 0)** : dépôt de l'auteur, sans licence
   publique ; import à sa demande de ses propres créations (voir
   [`CREDITS.md`](../CREDITS.md)). Contenu mixte dans l'atelier : les
   références tierces, anciennes versions déjà élaguées par la tâche A et les
   cartes recouvrant Destiny à l'octet près restent exclues (§6).
2. **Inventaire exhaustif** sans clone complet : clone *blobless*,
   20 branches listées ; `INDEX_METHODES.md` de la branche principale
   (208 chantiers, extraction du dépôt-usine `projet-pmdo` @ `6cca4a0`) ;
   audit automatisé (`import_work/audit_creation/audit.py`) : **249 cartes
   construites localisées**, dont **167 déjà présentes dans Destiny**
   (recouvrement vérifié par sha256 sur échantillon, 6/6 identiques) et
   82 absentes (~56 exclusions de doctrine + ~26 nouveautés).
3. **Collecte** des construits réels (ZIPs des branches `f9b9e04a`,
   `52e6a9de`, `e39626d2`, packages `renders/*` de `637b0828`, `exports/`) :
   30 `.rsground` collectés, puis **audit de résolution** unitaire (JSON
   parsé, version, `TexSize`, `AssetName`, toutes les références `Sheet` /
   `AnimIndex` / musique résolues contre `game/` + `base/` + cache source).
4. Trois voies d'import selon l'état réel des fichiers : **copie octet pour
   octet** (lot 1), **reconstruction par les pipelines committés** (lot 2),
   **conversion de format** (lot 3). Chaque lot : simulation, assemblage,
   reconstruction de `game/Content/Tile/index.idx`, déclarations de zone en
   fin de tableau (append-only), scripts squelettes, `tools/validate.py`,
   commits par domaine, push vérifié (`ls-remote` == HEAD local).

## 2. Résultat chiffré (tâche D, 3 lots)

| Élément | Lot 1 | Lot 2 | Lot 3 | Total tâche D |
|---|---:|---:|---:|---:|
| Cartes au sol importées | 7 | 21 | 5 | **33** |
| Banques de tuiles nouvelles | 58 | 208 | 33 | **299** |
| Fonds `.dir` nouveaux | 8 | 0 | 0 | 8 |
| Volume grounds | — | 234,5 Mio | 29,9 Mio | — |
| Conflits nom↔octets / références manquantes | 0 / 0* | 0 / 0 | 0 / 0 | 0 |

\* hors cartes exclues à l'audit (§6).

**État du dépôt après la tâche D** : **262 cartes au sol** (+ 1 `.rsmap`),
**1 322 banques de tuiles**, 113 `.dir`, 262 scripts squelettes, 5 zones —
`destiny_hub` (1), `chapitres_destiny` (8, nouvelle, `SortOrder` 50),
`cotes_metano` (84), `reverie` (13), `ateliers_donjons` (156).
`tools/validate.py` : **VALIDATION OK** (16 006 fichiers, 4 868,4 Mio, plus
gros fichier `cliffdaytest.rsground` 51,98 Mio < 100 Mio).
Galerie d'aperçus régénérée en clôture (`tools/preview_maps.py`,
`import_work/apercus_site/`, hors Git).

## 3. Lot 1 — cartes construites saines (copie octet pour octet)

Sources : ZIPs committés des branches `f9b9e04a` (ECE1/EGV1/FGV1),
`52e6a9de` (traversée cristalline) et `e39626d2`
(`MOD_CUTSCENE_PICHU_DAZZLING_PMDO.zip`). Audit : version `0.8.12.0`,
`TexSize` 1, `AssetName` == fichier, 0 conflit ; 58 `.tile` nouvelles et
8 `.dir` BG `CLIFF_PICHU_*` résolus dans les paquets d'origine.

| Carte | Titre (inchangé) | Zone |
|---|---|---|
| `ece1_entree_crevasse_enneigee` | Entree Crevasse enneigee - sud vers nord (4:3) | ateliers_donjons |
| `egv1_entree_grotte_vasques` | Entree Grotte aux vasques - sud vers nord (4:3) | ateliers_donjons |
| `fgv1_fin_grotte_vasques` | Fin Grotte aux vasques - salle des sources (4:3) | ateliers_donjons |
| `etx1_entree_traversee_cristalline` | Entree Traversee Cristalline - sud vers nord (4:3) | ateliers_donjons |
| `ftx1_fin_traversee_cristalline` | Fin Traversee Cristalline - Sanctuaire des Trois Cristaux (4:3) | ateliers_donjons |
| `cliffdaytest` | CliffReverietownnordest | reverie |
| `cliffdaytest_nuit` | Cliff Reverie Town — Nuit | reverie |

`cliffdaytest_nuit` est une **nouveauté** (variante nocturne absente de
Destiny). Sur les deux falaises, la cinématique « Pichu & la Team Dazzling »
est **volontairement inactive** : seuls grounds/tuiles/fonds ont été repris,
les scripts de l'atelier ne sont pas importés et les squelettes le signalent.

## 4. Lot 2 — 21 cartes reconstruites par leurs pipelines

**Découverte d'audit** : dans `renders/<projet>_v1/package/` (branche
`637b0828`), les `.rsground` et la plupart des `.tile` des 13 seuils
monts/mine/faille/forêt/tour sont des **liens symboliques pendants**
(mode git `120000` → `../../../../../.cache/tiles/<projet>/…`) ; le `.cache/`
n'existe sur **aucune des 20 branches**. Réels et committés : `layers/*.png`,
`metadata.json`, `package/Content/Tile/index.idx`, `init.lua`. Même situation
pour les 8 cartes `destiny_*` (sources présentes, sorties absentes).

**Reconstruction** (même voie que le menu-titre) : sparse-checkout de
`source/*.py`, des 21 projets et de leurs dossiers donneurs
(`dungeon_biomes_v1` — dont `red.py`, lecteur de formats BPC/BPL/BMA de
83 lignes —, `assets_gba_pmd_red`, `pmdo_cote`, `eau_metano`,
`fosse_argent_sanctuaire_v1`, `amp_plains_fleurie_v1`, `great_canyon_*`,
`magma_visqueux`, `mer_houleuse_entree_v1`, `reshiram_montagne_entree_v1`,
`silent_chasm_entree_v1`, `sinister_woods_entree_v1`, `zekrom_*`,
`zone_zero_v2`, `pmd_destiny_fangame_v1`), gabarit racine
`cliffdaytest.rsground`, puis exécution des 21 `build.py`
(moteur commun `tour_celeste_moteur_nuages.build_rsground_package`).

**Preuve de fidélité** : pour les 21 projets, le `zip_bytes` régénéré est
**identique au `metadata.json` committé** (clairière vérifiée champ par
champ : dimensions, `walkable_tiles`, `total_unique_tiles`,
`unique_tiles_per_sheet` — tous identiques). Audit de résolution sur les
sorties : 21/21 en `0.8.12.0`, `TexSize` 1, 208 feuilles nouvelles,
0 `.dir`, **0 conflit, 0 manquant**.

Nouvelle zone **`chapitres_destiny`** (calquée sur `reverie`, `SortOrder`
50), ordre narratif :

| Carte | Titre |
|---|---|
| `destiny_bourg_ecume_port` | PMD : Destiny — Bourg-Écume · Village Portuaire des Explorateurs |
| `destiny_passe_rocheuse_ecumes` | PMD : Destiny — Passe Rocheuse des Écumes · Route Côtière |
| `destiny_grotte_maree_entree` | PMD : Destiny — Grotte des Marées Prismatiques · Entrée du 1er Donjon |
| `destiny_grotte_maree_boss` | PMD : Destiny — Cœur Rocheux de l'Écho Marin · Arène Boss du 1er Donjon |
| `destiny_gorge_basaltique_magma_entree` | PMD : Destiny — Gorge Basaltique des Sources Brûlantes · 2e Donjon Entrée |
| `destiny_caldeira_coeur_solaire_boss` | PMD : Destiny — Caldeira du Cœur Solaire · 2e Donjon Boss |
| `destiny_sous_bois_mycelien` | PMD : Destiny — Sentier du Sous-Bois Mycelien · Chapitre II |
| `destiny_clairiere_source_lumineuse` | PMD : Destiny — Clairière de la Source Lumineuse · Chapitre II |

Treize seuils/arènes ajoutés en fin d'`ateliers_donjons` :
`mont_brasier_entree/sommet`, `mont_foudre_entree/sommet`,
`mont_lointain_entree/sommet`, `mine_magma_entree/arene`,
`faille_spatiale_entree/sanctuaire`, `foret_givree_entree/sanctuaire`,
`tour_celeste_entree`.

⚠️ **Réserve de provenance** : ces pipelines réemploient de la matière
pixellique dite « canonique » de *Pokémon Donjon Mystère : Équipe de Secours
Rouge* / *Explorers of Sky* (décodée dans l'atelier depuis ses fichiers
`assets_gba_pmd_red`). Les **layouts et assemblages sont de l'auteur** ;
aucun fichier extrait (`.bpl`/`.bpc`/`.bma`) ni le décodeur n'ont été
importés dans Destiny. Même réserve de redistribution que les cellules DTEF
(voir `CREDITS.md`) — **à arbitrer par l'auteur** s'il durcit la règle pixels.

## 5. Lot 3 — 5 exports « sud-nord » convertis au format natif

Les dossiers `exports/` de la branche `52e6a9de` contenaient des grounds au
**schéma maison incompatible PMDO** : champ `AssetLayers` inconnu du moteur
0.8.12, `Layers[].Tiles` vides, et des `.tile` dans un format propre à
l'atelier. Le code source de l'encodeur (`write_pmdo_tile` dans les
`build.py` des 5 projets, branche `52e6a9de`) établit le format exact :

```
.tile maison = <5i : 8, 96, 72, nb_séquences, durée_frame>
             + séquences × 72 × 96 paires <ii> (coordonnées d'atlas,
               ligne par ligne, (-1,-1) = transparent)
             + <i=1> <i longueur> + PNG atlas des patchs 8×8 dédupliqués
               (grille de 32 colonnes).
```

**Conversion** (`import_work/audit_creation/convert_exports.py`) : décodage
des frames 768×576, prémultiplication alpha (`RGB×A//255`, comme
`pmdo_cote.TileBank`), ré-encodage natif PMDO (`TileIndexNode` + records
`BaseSheet`, tuile vide sentinelle en `(0,0)`, déduplication sur 32
colonnes), cellules `Layers[].Tiles[x][y]` natives (frames via
`Frames`/`FrameLength` en ticks, cellule vide si toutes les frames sont
transparentes, frame unique si la cellule est statique). Dans les grounds :
`obstacles` d'origine conservés après vérification `[x][y]`, marqueurs
normalisés au schéma natif, clés exotiques retirées (`Width`, `Height`,
`Walls`, `Markers`, `AssetLayers`), titre ajouté en `LocalTexts.fr`.

**Vérifications** : chaque feuille native relue patch par patch
(`SheetReader`) — octets identiques aux patchs décodés ; audit indépendant à
l'assemblage (références == rapport == fichiers) ; pose 0 rendue par
`tools/preview_maps.py` : **0 feuille/tuile manquante et 0 pixel différent**
vs composite décodée, pour les 5 cartes.

| Carte | Feuilles | Entrées natives | Animations (frames × ticks) | Marqueurs |
|---|---:|---:|---|---|
| `entree_falaise_trempee_sud_nord_v1` | 6 | 12 801 | fleurs_mousse 4×16, embruns 8×8 (boucle 64) | entrance, donjon_seuil |
| `fin_falaise_trempee_source_v1` | 6 | 20 543 | source 5×12, fleurs_mousse 4×15 (boucle 60) | entrance, boss, objectif |
| `entree_promontoire_nuages_sud_nord_v1` | 7 | 15 574 | nuages 24×5, fleurs 4×30 (boucle 120) | entrance, donjon_seuil |
| `fin_promontoire_nuages_clairiere_v1` | 8 | 14 169 | nuages 24×5, fleurs 4×30, cristal 8×15 (boucle 120) | entrance, boss, objectif |
| `entree_tourbiere_piliers_sud_nord_v1` | 6 | 26 814 | bassins 8×8, bulles 8×8 (boucle 64) | entrance, donjon_seuil |

Les 5 cartes rejoignent `ateliers_donjons` (append-only).

## 6. Exclusions (prouvées, non importées)

| Contenu | Motif |
|---|---|
| `metano_gen_accueil/cafe/casino/salon_bas/salon_haut` (`reseau_metano_normal_v1`) | Intérieurs construits dans un environnement mod « évier » : 65–139 Sheets référencées par carte, ~99 % introuvables (138/139, 117/118, 89/90, 64/65, 99/101 manquantes), dont des provenances fermement exclues (`EoN_*`, `Altere_Pond_*`, `telechargement_6_tileset (1)`, `image (4)`, `10-PMD SKY`…). Titre commun « Metano Normal Home ». Non importables proprement sans décision de l'auteur. |
| `SpindaV4_pack.zip` | PNG/calques seuls : aucun ground, aucune tuile. |
| Exports tour temporelle | Fichiers `.ora` seuls (pas de ground construit). |
| ZIPs `*_calques_png_8px` | Calques PNG sans ground. |
| 167 cartes des ZIPs `projet-pmdo` | Déjà dans Destiny (tâche A), octet-identiques — non réimportées. |
| ~56 anciens basenames / références tierces | Doctrine tâche A (dernière version par lieu ; pas de cartes de référence). |
| ~470 autres projets `source/` | Pipelines intermédiaires hors périmètre (déjà livrés via les ZIPs `projet-pmdo` ou non aboutis) ; seuls les 21 du lot 2 ont été reconstruits. |

## 7. Commits (branche `arena/c40fd96f-pmdo-destiny`)

- Lot 1 : `0558c32` (tuiles/fonds), `7cd3138` (7 cartes), `ebc2ed5` (zones/scripts).
- Lot 2 : `91b1acc` (208 tuiles), `143f0fb` (21 cartes), `a61b85d` (zone
  chapitres + scripts), `1deb01f` (documentation).
- Lot 3 : `2bb4fef` (33 tuiles natives), `1f284dd` (5 cartes), `73e72b1`
  (zone + scripts), `0aa8051` (documentation).

Outils et rapports d'atelier (hors Git, régénérables) :
`import_work/audit_creation/` — `audit.py`, `resolve.py`, `assemble1.py`,
`run_builds.py`, `resolve2.py`, `assemble2.py`, `convert_exports.py`,
`assemble3.py` et leurs rapports JSON.

## 8. Limites et tests en jeu à faire (PMDO Dev 0.8.12)

Aucun test en moteur n'est possible depuis le sandbox. À vérifier en jeu,
par ordre :

1. **Ouverture des 33 cartes** dans le Dev Mode (zones `chapitres_destiny`,
   `ateliers_donjons`, `reverie`) — en particulier les 5 converties du lot 3
   (leurs manifestes d'atelier indiquent `runtime_tested: false`).
2. **Animations natives** : cycles d'eau/nuages/embruns (frames et
   `FrameLength` des lots 2 et 3), fonds animés des falaises.
3. **Collisions et chemins** : `obstacles` des lots 2/3 (entrée sud →
   seuil/boss au nord), marqueurs `entrance`/`donjon_seuil`/`boss`/`objectif`.
4. **Falaises Reverie jour/nuit** : PNJ présents mais immobiles (cinématique
   Pichu volontairement inactive — Partie 2).
5. Raccordements, renommages « univers Destiny » (titres du lot 1 sans
   accents, `cliffdaytest` = « CliffReverietownnordest ») et cinématiques :
   chantier suivant (voir `PROJECT_CONTEXT.md`).
