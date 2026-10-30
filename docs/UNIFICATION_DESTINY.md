# Unification Destiny — Quest unique `destiny` (PMDO 0.8.12)

Branche `destiny-unifiee` de `meromoonmeri/PMDO-Destiny`. Ce document est l'état des lieux
et le journal exact de l'unification : ce qui existait, ce qui a été récupéré, d'où, avec quelles
vérifications, ce qui a été modifié (et pourquoi), et ce qui reste introuvable.

Outil de reconstruction : `tools/assemble.py` (dans l'espace de travail `destiny_work`, copié ici
dans `docs/audit/assemble.py`) ; données brutes d'audit dans `docs/audit/*.json`.

## 1. Périmètre et décisions

* Une seule Quest : `game/` — `Mod.xml` inchangé (nom « Pokémon Mystery Dungeon: Destiny »,
  namespace `destiny`, UUID `746CBBCD-426F-5419-A735-D50248440935`, ModType Quest).
* Socle retenu (décision utilisateur) : la Quest de `PMDO-Destiny` (branche
  `arena/c40fd96f-pmdo-destiny`, 262 cartes, 1 322 planches, 5 zones). Rien n'y a été supprimé.
* Anciennes versions remplacées → zone `archives` (fichiers individuels, intacts ; seul le champ
  `AssetName` est réécrit quand un renommage est indispensable pour coexister — voir §6).
* Cartes de référence tierces (Halcyon / EoS / « references ») exclues ; seules les planches
  requises par des cartes de l'utilisateur sont embarquées (aucune dépendance à un autre mod :
  tout ce qui n'est pas dans le PMDO de base est copié dans `game/Content`).
* `WaterfallVillageCapital` : intégrée telle quelle (233 727 831 o) — livrée compressée dans `payload/`
  (Git LFS impossible : budget LFS du compte GitHub épuisé, voir §8).

## 2. État des lieux avant modification

| Source | Contenu pertinent |
|---|---|
| `PMDO-Destiny` `arena/c40fd96f` (socle) | `game/` : 262 `.rsground`, 1 322 `.tile` + `index.idx`, 86 BG + 27 Object, zones `destiny_hub`(1) `cotes_metano`(84) `reverie`(13) `ateliers_donjons`(156) `chapitres_destiny`(8), 262 scripts squelettes `Data/Script/destiny/ground/<carte>/init.lua`, `tools/validate.py`. Importait déjà projet-pmdo (167 cartes), guilde-treehouse-pmd, 21 cartes reconstruites par pipeline, `cliffdaytest`/`cliffdaytest_nuit` (version cinématique, sans les scripts). |
| `projet-creation-pmdo` `arena/64113588` | Quest `quest_pmd_destiny/` : scénario complet (intro_halo → personality_test → cliffdaytest_nuit → donjon lost_wood → reveil_nuit), 87 fichiers (3 cartes, 4 zones, scripts, autotiles Lost Wood, musique, badges UI). |
| `projet-creation-pmdo` `arena/2a041d50` | Inventaire 262 (`DESTINY_262_RECOVERY`), zip Treasure Expeditions, composant titre. 95 entrées de cet inventaire étaient absentes du socle (22 zips, 29 branches, 44 générées). |
| `projet-creation-pmdo` `arena/e39626d2` | `MOD_CUTSCENE_PICHU_DAZZLING_PMDO.zip` (cinématique Pichu × Team Dazzling), `livrables_cliff_nord_centre_pmdo` (pack 10 falaises jour/nuit), `livrables_cliff_nord_nuit_pmdo` (conversions nocturnes), paquets `renders/*/package`, ~470 lots `source/*/build.py`. |
| `projet-creation-pmdo` racine `main` | `cliffnordouesttest1.rsground` canonique (blob 51e9dd3b), cartes café Spinda, `town02/` (copie), `town02_tiles_pack_*`. |
| `projet-pmdo` `main` | `cliffdaytest.rsground` original sans entités (cd276dab), `cotes_v2_0812_pmdo.zip`, `cote_metano_v2_pmdo.zip`. |
| `guilde-treehouse-pmd` (82 branches) | `renders/*/*_projet_pmdo_0812.zip` (13 paquets), `exports/*` (reverie_town_v1, forest_cave_*, cliffnordouesttest1_*), `base/` = copie des cartes PMDO, `source/*/references` = cartes tierces. Aucune cinématique propre. |
| `town02` (`main`) | Quest « New Era » (namespace halcyon, 621 cartes) : `WaterfallVillageCapital.rsground` et `waterfall_cave_1.rsground` (Git LFS), 1 271 planches, musiques EoS (LFS). |
| `Palikadude/Halcyon` | Modèle d'organisation : `Data/Ground/*.rsground` à plat, `Data/Zone/*.json + index.idx`, `Data/Script/ground/<carte>/init.lua`, `Data/Script/zone/<zone>/init.lua`, `Content/Tile/*.tile + index.idx`, `Content/BG|Object/*.dir`, `Data/StartParams.xml`. En 0.8.12 les scripts sont sous `Data/Script/<namespace>/…`. |

Méthode : clones « blobless » de tous les dépôts, index de tous les blobs `.rsground/.tile/.dir`
sur l'ensemble des commits (`docs/audit/rsground_index_all.json`, `tile_dir_index_all.json`),
scanner JSON des cartes (`rsground_scan.py` : version, dimensions, calques, planches utilisées
avec nombre de cases, fonds, entités, musiques). Chaque carte candidate a été scannée et ses
dépendances cherchées dans tous les dépôts **avant** intégration (`candidates_deps.json`).

## 3. Structure finale

```
game/
  Mod.xml
  Content/Tile/*.tile (1 740) + index.idx      Content/BG (117) Content/Object (27)
  Content/Music (4 .ogg)  Content/UI/quiz_badges (17 PNG)
  Data/Ground/*.rsground (342, fichiers individuels)
  Data/Zone/<zone>.json (11) + index.idx       Data/AutoTile (3 Lost Wood) + index.idx
  Data/Script/destiny/{main,scriptvars}.lua, services/, ground/<carte>/init.lua (342), zone/lost_wood/init.lua
  Data/StartParams.xml  Data/quiz_personnalite_*.json
```

| Zone | Cartes | Rôle |
|---|---:|---|
| `destiny_hub` | 1 | clairière technique du socle (inchangée) |
| `personality_test` | 3 | scénario : `personality_test`(0) `intro_halo`(1) `reveil_nuit`(2) — départ de partie = `intro_halo` |
| `destiny_cliff_tests` | 5 | `cliffdaytest`(0, cinématique Dazzling) `cliffdaytest_source`(1) `cliffnordouesttest1`(2) `cliffnordouesttest1_nuit`(3) `cliffdaytest_nuit`(4, scénario) |
| `lost_wood` | donjon 7 étages | scénario (segment généré, autotiles `lost_wood_*`) |
| `town02_waterfallvillage` | 2 | `WaterfallVillageCapital`, `waterfall_cave_1` |
| `cotes_metano` | 84 | socle (inchangée) |
| `falaises_nord_centre` | 20 | pack « 10 Falaises Nord Centrées » jour/nuit |
| `reverie` | 11 | socle moins `cliffdaytest`/`cliffdaytest_nuit` (déplacées vers `destiny_cliff_tests`, comme dans le scénario) |
| `ateliers_donjons` | 168 | socle (156) + 12 cartes récupérées (paquets renders + tour céleste) |
| `chapitres_destiny` | 8 | socle (inchangée) |
| `archives` | 40 | anciennes versions / variantes conservées |

Index régénérés : `Content/Tile/index.idx` (même construction que `ImportHelper.BuildTileIndex` :
nom + 8 octets d'en-tête + n×16 octets par planche, vérifié par `tools/validate.py`),
`Data/Zone/index.idx` (résumés recalculés depuis les JSON de zone), `Data/AutoTile/index.idx`.

## 4. Cartes ajoutées (83) — provenance et vérification

#### Zone `personality_test` (3 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `personality_test` |  | projet-creation-pmdo arena/64113588 quest_pmd_destiny | 180 870 | `52a37435d167` |  |
| `intro_halo` |  | projet-creation-pmdo arena/64113588 quest_pmd_destiny | 286 123 | `ab689cb6c719` |  |
| `reveil_nuit` |  | projet-creation-pmdo arena/64113588 quest_pmd_destiny | 32 498 805 | `d4fcc4d37135` |  |

#### Zone `destiny_cliff_tests` (3 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `cliffdaytest_source` | `cliffdaytest` | projet-pmdo main cliffdaytest.rsground (blob cd276dab) = source canonique de la cinématique (nom attendu par la zone du scénario) | 10 042 774 | `fb216699246c` | TILE MANQUANTE: v2_promontoire_jour_03; TILE MANQUANTE: 13_avancee_basse_gauche_terrain; sheet "" (texture par défaut); TILE MANQUANTE: Metano_Town_Animated; TILE MANQUANTE: 01_long_cap_jour_02; TILE MANQUANTE: Altere_Pond_Objects_Under |
| `cliffnordouesttest1` |  | projet-creation-pmdo main cliffnordouesttest1.rsground (blob 51e9dd3b) | 7 812 806 | `2cb10918d6bf` | INCOMPLETE: planches v2_promontoire_jour_03  terrain  terrain (2)  terrain (3)  terrain (4) introuvables dans tous les dépôts; TILE MANQUANTE: v2_promontoire_jour_03; TILE MANQUANTE: terrain; TILE MANQUANTE: terrain (4); TILE MANQUANTE: terrain (3); TILE MANQUANTE: terrain (2) |
| `cliffnordouesttest1_nuit` |  | projet-creation-pmdo commit e6c22020 (2026-10-21 21:44) livrables_cliff_nord_nuit_pmdo — version « compatible town02 » | 5 473 377 | `2f7b49835873` |  |

#### Zone `town02_waterfallvillage` (2 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `WaterfallVillageCapital` |  | meromoonmeri/town02 main Data/Ground/WaterfallVillageCapital.rsground (Git LFS  233 727 831 o) | 233 727 831 | `afc5081f7348` |  |
| `waterfall_cave_1` |  | meromoonmeri/town02 main Data/Ground/waterfall_cave_1.rsground (Git LFS) | 1 817 738 | `37bc99352869` |  |

#### Zone `falaises_nord_centre` (20 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `cliff_centre_01_grand_cap_panoramique_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 456 629 | `4d50853b4446` |  |
| `cliff_centre_01_grand_cap_panoramique_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 456 914 | `ef85e270fddc` |  |
| `cliff_centre_02_eperon_nord_effile_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 349 773 | `6294a3197fd8` |  |
| `cliff_centre_02_eperon_nord_effile_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 350 058 | `bb0554eabf08` |  |
| `cliff_centre_03_double_terrasse_centrale_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 415 091 | `269fbefa4e84` |  |
| `cliff_centre_03_double_terrasse_centrale_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 415 376 | `80febda2a421` |  |
| `cliff_centre_04_grande_esplanade_royale_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 478 750 | `484c467cadfd` |  |
| `cliff_centre_04_grande_esplanade_royale_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 479 035 | `7ae3f62f6960` |  |
| `cliff_centre_05_cap_anse_jumelle_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 445 219 | `d4efa3c3efb2` |  |
| `cliff_centre_05_cap_anse_jumelle_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 445 504 | `68c86b55cf53` |  |
| `cliff_centre_06_presquile_isthme_etroit_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 468 933 | `6cdc22e3adc7` |  |
| `cliff_centre_06_presquile_isthme_etroit_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 469 218 | `8c320c349197` |  |
| `cliff_centre_07_cap_asymetrique_ouest_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 511 020 | `268f77e48bc3` |  |
| `cliff_centre_07_cap_asymetrique_ouest_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 511 305 | `f8f171738f57` |  |
| `cliff_centre_08_cap_asymetrique_est_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 443 506 | `7fb0e03d0a93` |  |
| `cliff_centre_08_cap_asymetrique_est_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 443 791 | `235bb89645fe` |  |
| `cliff_centre_09_trois_paliers_sacres_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 470 604 | `65c3cd419bd7` |  |
| `cliff_centre_09_trois_paliers_sacres_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 470 889 | `694b8443a53d` |  |
| `cliff_centre_10_bastion_circulaire_jour` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 293 455 | `e31dee3200c3` |  |
| `cliff_centre_10_bastion_circulaire_nuit` |  | projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip | 5 293 740 | `7baac760164e` |  |

#### Zone `ateliers_donjons` (15 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `agm1_arene_groudon_magma` |  | guilde-treehouse-pmd renders/*/arene_groudon_magma (agm1_arene_groudon_magma.rsground) | 12 808 059 | `ca53e58418b2` |  |
| `agm2_arene_groudon_magma` |  | guilde-treehouse-pmd renders/*/arene_groudon_magma (agm2_arene_groudon_magma.rsground) | 16 860 369 | `f8a25c76c2aa` |  |
| `esn1_entree_vapeur_jour` |  | guilde-treehouse-pmd renders/*/entree_vapeur_sud_nord (esn1_entree_vapeur_jour.rsground) | 4 389 114 | `fc5a62dd47d8` |  |
| `ewc1_entree_waterfall_cave` |  | guilde-treehouse-pmd renders/*/entree_waterfall_cave_sud_nord (ewc1_entree_waterfall_cave.rsground) | 9 195 325 | `e10cb07696d0` |  |
| `ewc2_entree_waterfall_cave` |  | guilde-treehouse-pmd renders/*/entree_waterfall_cave_v2 (ewc2_entree_waterfall_cave.rsground) | 11 869 210 | `5dc492358bf7` |  |
| `eaz1_entree_zone_zero` |  | guilde-treehouse-pmd renders/*/entree_zone_zero (eaz1_entree_zone_zero.rsground) | 6 894 524 | `bff2d7619f2c` |  |
| `fgg1_fin_givre_grotte` |  | guilde-treehouse-pmd renders/*/fin_givre_grotte (fgg1_fin_givre_grotte.rsground) | 8 258 735 | `59d303452524` |  |
| `fmf1_clairiere_mystifying` |  | guilde-treehouse-pmd renders/*/fin_mystifying_forest (fmf1_clairiere_mystifying.rsground) | 2 876 038 | `fe5f3b96aaaf` |  |
| `fmf2_enceinte_mystifying` |  | guilde-treehouse-pmd renders/*/fin_mystifying_forest (fmf2_enceinte_mystifying.rsground) | 2 680 925 | `4755bdbe92a4` |  |
| `ful1_rive_underground_lake` |  | guilde-treehouse-pmd renders/*/fin_underground_lake (ful1_rive_underground_lake.rsground) | 4 004 682 | `ddfe555f1ce3` |  |
| `raz1_levre_cratere` |  | guilde-treehouse-pmd renders/*/route_zone_zero_1 (raz1_levre_cratere.rsground) | 6 947 633 | `6c40fa7414e3` |  |
| `raz2_terrasses_cascades` |  | guilde-treehouse-pmd renders/*/route_zone_zero_2 (raz2_terrasses_cascades.rsground) | 7 986 344 | `fd4cde39afd0` |  |
| `raz3_fond_cristallin` |  | guilde-treehouse-pmd renders/*/route_zone_zero_3 (raz3_fond_cristallin.rsground) | 6 567 190 | `26befb327067` |  |
| `stc1_tour_celeste` |  | projet-creation-pmdo commit 106b6e49 renders/tour_celeste_sommet_v1/package (sha = inventaire 262) | 7 322 870 | `62387a4e0ae3` |  |
| `rtc1_tour_celeste` |  | projet-creation-pmdo commit a35f9a3d renders/tour_celeste_relais_v1/package | 35 826 292 | `d727b973dab7` |  |

#### Zone `archives` (40 cartes ajoutées)

| Carte (AssetName) | Nom d'origine | Source | Octets | SHA-256 (12) | Remarques |
|---|---|---|---:|---|---|
| `cote_v2_promontoire` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 11 365 746 | `14221be57911` |  |
| `cote_v2_terrasse` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 12 083 649 | `2c1242803878` |  |
| `v30812_01_cap_large_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 992 966 | `5d3d2dcb5bcf` |  |
| `v30812_01_cap_large_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 993 852 | `9593a315e73f` |  |
| `v30812_02_terrasse_croissant_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 075 998 | `293695419d56` |  |
| `v30812_02_terrasse_croissant_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 076 742 | `edec0f53dfd0` |  |
| `v30812_03_double_belvedere_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 637 226 | `48b21129ccc9` |  |
| `v30812_03_double_belvedere_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 635 899 | `3d8723a05c36` |  |
| `v30812_04_pointe_sinueuse_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 047 316 | `7649a8272fa5` |  |
| `v30812_04_pointe_sinueuse_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 048 006 | `45b4d9ab284d` |  |
| `v30812_05_grande_mesa_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 134 679 | `37e3a935655e` |  |
| `v30812_05_grande_mesa_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 135 465 | `3efb61f029e0` |  |
| `v30812_06_crique_profonde_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 791 706 | `e0a559f8eda2` |  |
| `v30812_06_crique_profonde_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 792 197 | `51870795684b` |  |
| `v30812_07_balcon_haut_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 709 036 | `5b60707e5563` |  |
| `v30812_07_balcon_haut_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 709 673 | `404cca254840` |  |
| `v30812_08_terrasses_decalees_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 598 534 | `1de527779498` |  |
| `v30812_08_terrasses_decalees_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 599 298 | `8c4f544146ef` |  |
| `v30812_09_cap_eventail_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 629 957 | `89394c29c6c9` |  |
| `v30812_09_cap_eventail_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 16 630 441 | `71ddfacd9ca6` |  |
| `v30812_10_esplanade_arrondie_jour` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 183 073 | `99ebc4e40171` |  |
| `v30812_10_esplanade_arrondie_nuit` |  | projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262) | 17 183 701 | `cb43394dd6f0` |  |
| `caféspindaaccueil` |  | projet-creation-pmdo racine caféspindaaccueil.rsground | 2 259 906 | `f1e2e67ff9b6` | MUSIC MANQUANTE: Spinda's Cafe.ogg |
| `spindacaféétage1` |  | projet-creation-pmdo racine spindacaféétage1.rsground | 1 604 932 | `cff338a216f8` | MUSIC MANQUANTE: Spinda's Cafe.ogg |
| `spindacaféétage1salle2` |  | projet-creation-pmdo racine spindacaféétage1salle2.rsground | 2 269 156 | `4b0a0476ea83` | MUSIC MANQUANTE: Spinda's Cafe.ogg |
| `spindacafetest` |  | projet-creation-pmdo racine spindacafetest.rsground | 962 590 | `d0f3fbd9e5b3` |  |
| `rvt_ne_jour` |  | guilde-treehouse-pmd exports reverie_town_v1 | 5 411 560 | `9ea948cf29f4` |  |
| `rvt_ne_nuit` |  | guilde-treehouse-pmd exports reverie_town_v1 | 5 465 279 | `59dbfc7cf8d7` |  |
| `rvt_no_jour` |  | guilde-treehouse-pmd exports reverie_town_v1 | 5 361 920 | `1b22b806e68b` |  |
| `rvt_no_nuit` |  | guilde-treehouse-pmd exports reverie_town_v1 | 5 423 203 | `97a8b0708644` |  |
| `v50812_beach_cave_entrance_v2` |  | guilde-treehouse-pmd renders beach_cave_entrance_v2 | 782 070 | `d0f59752a54e` | MUSIC MANQUANTE: BGM_DUN_BeachCave |
| `forest_render_v1` |  | guilde-treehouse-pmd exports/forest_cave_render_v1_pmdo (version antérieure  commit 3d24de1d) | 2 665 640 | `302c7f2c3a10` |  |
| `forest_magenta_v1` |  | guilde-treehouse-pmd exports/forest_cave_magenta_v1_pmdo | 2 687 988 | `817b5a86ce6b` |  |
| `etc1_tour_celeste` |  | projet-creation-pmdo commit a35f9a3d renders/tour_celeste_entree_v1/package — version antérieure de tour_celeste_entree | 35 645 154 | `c1ea66623c92` |  |
| `cliffdaytest_nuit_v1_nord_nuit` | `cliffdaytest_nuit` | projet-creation-pmdo commit c96645d4 PACK_CLIFF_NORD_NUIT (conversion nuit v1) | 9 139 580 | `6afba323d34e` |  |
| `cliffdaytest_nuit_v2_animee` | `cliffdaytest_nuit` | projet-creation-pmdo commit 9d95a275 (nuages animés + mer 8 phases) | 9 301 047 | `5cc53e4e0fba` |  |
| `cliffdaytest_nuit_v3_compat_town02` | `cliffdaytest_nuit` | projet-creation-pmdo commit e6c22020 (compat town02) | 4 939 378 | `2c874e58733e` | TILE MANQUANTE: WoN_overwyh_spring; TILE MANQUANTE: GouffreMuetBord_Base; TILE MANQUANTE: D04p12a_Base; TILE MANQUANTE: D41p41a_Base; TILE MANQUANTE: Metano_Town_Animated_Night; TILE MANQUANTE: P05p03a_Base; TILE MANQUANTE: Ledian_Dojo_Ceiling; TILE MANQUANTE: GrotteEchos_Base; TILE MANQUANTE: Metano_Town_Objects_Over_Night; TILE MANQUANTE: b05p02c_Base; TILE MANQUANTE: D31p11a_Base; TILE MANQUANTE: Metano_Town_Water_Home_Base_Animated; TILE MANQUANTE: D54p11a_Base; TILE MANQUANTE: b05p02a_Base; TILE MANQUANTE: RecifGenereux_Base; TILE MANQUANTE: zone_corrigee_magenta; TILE MANQUANTE: AntreDragon_Base; TILE MANQUANTE: MarecageCacahuete_Base; TILE MANQUANTE: Metano_Town_River_Animation_3_Night; TILE MANQUANTE: WoN_overwyh_summer; TILE MANQUANTE: d21p01_DirectBase; TILE MANQUANTE: V12p01a_Base |
| `cliffnordouesttest1_nuit_v1_nord_nuit` | `cliffnordouesttest1_nuit` | projet-creation-pmdo commit c96645d4 (conversion nuit v1) | 7 373 912 | `87ed247c0214` |  |
| `cliffnordouesttest1_nuit_v2_animee` | `cliffnordouesttest1_nuit` | projet-creation-pmdo commit 9d95a275 (nuages animés) | 7 385 725 | `f97658ecdfa3` |  |
| `cliffnordouesttest1_compat_town02` | `cliffnordouesttest1` | projet-creation-pmdo commit e6c22020 (compat town02  blob b40eaa93) | 5 463 330 | `0551be4379da` |  |

Toutes les cartes conservent leur contenu binaire d'origine (SHA-256 identique au blob source),
sauf les 10 renommées (§6) dont seul le champ `AssetName` diffère. Les 22 côtes `v30812_*`/`cote_v2_*`
et `stc1_tour_celeste` ont le SHA attendu par l'inventaire 262 ; `agm2_arene_groudon_magma`
provient du paquet publié (`AGM2_projet_pmdo_0812.zip`), différent de la sortie `.cache` listée
dans l'inventaire (sortie jamais committée).

### 4.1 Planches et fonds ajoutés
388 planches `.tile` et 25 fonds `.dir` ajoutés (`docs/audit/assemble_report.json`). Règle : un
fichier déjà présent dans `game/Content` n'est jamais écrasé ; chaque homonyme a été comparé
octet à octet (ex. `Metano_Town_Base/Cliffs/Objects/Animation_Tileset` de town02 = socle,
`PICHU_CLIFF_*`, `CLIFF_PICHU_NUIT_*` du zip cinématique = socle). Aucun conflit de contenu.
Les planches de town02 nécessaires aux versions « compatibles town02 » (§6) représentent
~140 Mo ; elles n'ont pas de dépendance au mod New Era (copiées dans la Quest).

## 5. Cinématiques et scripts

### 5.1 Scénario (`arena/64113588`) — fichiers repris tels quels avec les correctifs minimaux ci-dessous
| Script | Correctif | Raison |
|---|---|---|
| `ground/intro_halo`, `personality_test`, `reveil_nuit`, `cliffdaytest_nuit`, `zone/lost_wood` | `require 'common'` → `require 'origin.common'` | en 0.8.12 le `common.lua` de base est sous le namespace `origin` (`base/Data/Script/origin/common.lua`) |
| `ground/intro_halo` l.67 | `GROUND:EnterGroundMap(...)` → `GAME:EnterGroundMap('personality_test', 'Main_Entrance_Marker')` | `EnterGroundMap` est une méthode de `GAME` (ScriptGameAdventure), pas de `GROUND` |
| `ground/personality_test` l.298 | `GROUND:EnterGroundMap('cliffdaytest_nuit', …)` → `GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Crossroads')` | idem + changement de zone obligatoire (la carte n'est pas dans `personality_test`) |
| `ground/personality_test` l.21 | `require 'ground.personality_test.quiz_data'` → `require 'destiny.ground.personality_test.quiz_data'` | chemin namespacé (`quiz_data.lua` copié à côté d'`init.lua`) |
| `ground/cliffdaytest_nuit` l.89 | `GROUND:Hide(hero)` → `GROUND:Hide('PLAYER')` | `GROUND:Hide` attend le nom d'entité |
| `zone/lost_wood` | `GAME:EnterZone('destiny_cliff_tests', -1, 8, 0)` → index `4` | la zone du scénario listait 9 cartes dont 5 inexistantes (`cliffdaytest_2/_3/_4`, `cliffnordouesttest1_2/_3`, introuvables dans tous les dépôts) ; `cliffdaytest_nuit` est désormais à l'index 4 |
| `scriptvars.lua` | ajout de `SV.Destiny = SV.Destiny or {...}` | pré-création de la table de drapeaux du scénario (les scripts testent déjà `~= nil`) |
| `Data/StartParams.xml` | `DefaultZone`/`StartMap` : `destiny_hub`/0 → `personality_test`/1 | départ sur `intro_halo` comme dans le scénario ; `DefaultRank` reste `none` (`unranked` du scénario n'existe pas dans PMDO) ; liste `StartChars` du socle conservée |

Non repris : les « shims » `Data/Script/ground/<carte>/init.lua` (`return require 'destiny.ground.<carte>'`)
du scénario, inutiles avec le chargement namespacé de 0.8.12 ; `Mod.xml` du scénario (UUID différent).

### 5.2 Cinématique « Pichu × Team Dazzling » (`arena/e39626d2`, zip `MOD_CUTSCENE_PICHU_DAZZLING_PMDO.zip`)
* Les cartes du zip (`cliffdaytest`, `cliffdaytest_nuit`) sont **octet pour octet** celles du socle
  (entités `Pichu`, `Adagio`, `Sonata`, `Aria`, marqueurs `Pichu_Home_Door`, `Pichu_Crossroads`, …).
* Script jour repris intégralement : `Data/Script/destiny/ground/cliffdaytest/init.lua`
  (seul correctif : `require 'origin.common'`). Déclenchement à l'entrée tant que `SV.PichuDazzling.Seen` est faux.
* La carte `cliffdaytest_nuit` est pilotée par le script du **scénario** (plus récent : scène du
  partenaire / retour de Lost Wood). La variante nocturne de la cinématique Dazzling (identique au
  jour à `SV.PichuDazzlingNuit` près) est conservée intacte dans
  `ground/cliffdaytest_nuit/cinematique_dazzling_nuit.lua` (non chargée automatiquement).
* Fonds/planches/sprites : fonds `CLIFF_PICHU_*` et planches `PICHU_CLIFF_*` déjà dans le socle ;
  sprites Pokémon = ceux de l'installation PMDO (comme prévu par le README du zip).

### 5.3 Autres scripts
* Pack falaises nord centre : scripts d'origine du pack (`COMMON.RespawnAllies()` dans `Init`), préfixés de `require 'origin.common'`.
* Paquets renders / tour céleste / archives / town02 : squelette Destiny (fondu d'entrée), identique à celui du socle — les scripts des paquets étaient des coquilles vides.

## 6. Comparaison des versions et renommages (zone `archives`)

| Carte finale | Versions trouvées (blob, taille, source) | Choix |
|---|---|---|
| `cliffdaytest` | cd276dab 10 042 767 o (projet-pmdo main, sans entités) ; e0138fdb… 54 507 370 o (zip cinématique = socle, avec entités) | socle conservé ; l'original devient `cliffdaytest_source` (nom attendu par la zone du scénario) |
| `cliffdaytest_nuit` | zip cinématique 48 563 170 o (socle, 28/10) ; conversions nuit c96645d4 (v1), 9d95a275 (animée), e6c22020 (compat town02) du 21/10 | socle conservé ; les 3 conversions → `cliffdaytest_nuit_v1_nord_nuit`, `_v2_animee`, `_v3_compat_town02` |
| `cliffnordouesttest1` | 51e9dd3b (racine `main`, canonique) ; 4633c9ab (quest_pmdo_0812, même contenu sans fonds) ; 84c80b74 (2a041d50, planches renommées `Treasure_*`) ; 1737733c / 65c48168 (gtp exports animation, fonds nuit ajoutés) ; b40eaa93 (compat town02, 91 planches, entités PLAYER/TEAMMATE) | canonique 51e9dd3b en zone `destiny_cliff_tests` (incomplète, §7) ; b40eaa93 → `cliffnordouesttest1_compat_town02` (seule version dont toutes les planches existent) ; les autres sont des variantes de la même grille avec les mêmes planches manquantes : non dupliquées |
| `cliffnordouesttest1_nuit` | fd40bd98 (v1), 377b14d8 (animée), a67c011d (compat town02, dernière, 21/10 21:44) | dernière version en zone `destiny_cliff_tests` ; v1 → `cliffnordouesttest1_nuit_v1_nord_nuit`, animée → `_v2_animee` |
| `tour_celeste_entree` | socle TCE1 28 014 532 o (reconstruite) ; `etc1_tour_celeste` 35 645 154 o (paquet renders a35f9a3d) | socle conservé ; ancienne → archives |
| `stc1_tour_celeste` | 6 blobs (7,3 à 19,8 Mo) ; 425d6726 = SHA de l'inventaire 262, commit 106b6e49 avec ses 10 planches | 425d6726 |
| `rvt2_*` (socle) / `rvt_*` v1 | exports reverie_town_v1 (2 blobs quasi identiques par carte) | v1 → archives (dernier blob de chaque paire) |
| `forest_cave_render_v1` (socle) | `forest_render_v1` 5dba77d7 (version antérieure, planches FRV1), `forest_magenta_v1` | les deux → archives avec leurs planches |
| `v50812_beach_cave_entrance_v3` (socle) | v2 e4df4aa7 | v2 → archives |
| café Spinda | `caféspindaaccueil`, `spindacaféétage1`, `spindacaféétage1salle2`, `spindacafetest` (racine projet, planches dans le scénario 64113588) | archives (hors scénario), noms accentués d'origine conservés |
| côtes `v30812_01..10` jour/nuit, `cote_v2_*` | zips projet-pmdo (SHA = inventaire) | archives (remplacées par `cotes_metano` dans le socle) |

Renommages (champ `AssetName` réécrit, reste du fichier identique) : `cliffdaytest_source`,
`cliffdaytest_nuit_v1_nord_nuit`, `cliffdaytest_nuit_v2_animee`, `cliffdaytest_nuit_v3_compat_town02`,
`cliffnordouesttest1_nuit_v1_nord_nuit`, `cliffnordouesttest1_nuit_v2_animee`, `cliffnordouesttest1_compat_town02`.

## 7. Introuvable / non intégré — liste précise

### 7.1 Dépendances manquantes de cartes intégrées (aucun remplacement fabriqué)
| Carte | Ressource manquante | Détail |
|---|---|---|
| `cliffnordouesttest1` | planches `v2_promontoire_jour_03` (6 209 cases), `terrain` (992), `terrain (4)` (451), `terrain (3)` (130), `terrain (2)` (94) | absentes de tous les commits de tous les dépôts (seuls des PNG non convertibles à l'identique existent : `guilde-treehouse-pmd sprites/cote_dix_zones/v2_promontoire/jour_00.png`). Les cases concernées s'affichent avec la texture d'erreur du moteur. Les planches `00_ciel`, `Altere_Pond_Cliffs`, `INVERSEPATHWAY`, `Metano_Altere_Transition_Base`, `Metano_Town_Animation_Tileset` sont fournies. |
| `cliffdaytest_source` | `v2_promontoire_jour_03`, `13_avancee_basse_gauche_terrain`, `01_long_cap_jour_02` + 12 cases de planche vide `""` | idem (version d'avant la cinématique ; la version socle est complète) |
| `WaterfallVillageCapital` | 282 cases référencent la planche vide `""` | état natif du fichier town02 (même rendu dans New Era : texture par défaut) |
| `v50812_beach_cave_*` (4 cartes) | musique `BGM_DUN_BeachCave` | introuvable partout (nom interne EoS) |
| socle : `plage_cv2_anse/crique`, `pmd_petal_clearing`, café Spinda | `Brine Cave.ogg`, `Sky Peak Prairie.ogg`, `Spinda's Cafe.ogg` | **récupérées** dans town02 (LFS) → `Content/Music` |
| socle | `Boss Battle!.ogg`, statut de carte `steam` | toujours introuvables (déjà signalés par le socle) |
| `destiny_hub`, `glacier_cliff_aurora_v1`, `guild_path` | `InsideHut`, `VastIceMountain`, `GuildPath`, objets `Flowerpot_*`, `Flowers_Tropical_*`, `Berry_Basket_*`, `Pot`, `House_Normal`, `Guildmaster.ogg`, `Title.ogg` | fournis par le PMDO de base (`base/Content`), pas par un mod |

### 7.2 Cartes non intégrées
* **33 cartes « générées » sans sortie committée** (inventaire 262, catégorie `generated_build`, sorties dans `.cache/` jamais poussées ; seuls `source/<lot>/build.py` + bruts existent sur `arena/e39626d2`) : `ekr1_entree_caverne_cristal`, `eoc1_entree_old_castle`, `faille_spatiale_sanctuaire_avant_portail`, `fct1_fin_clairiere_tropicale`, `fkr1_fin_caverne_cristal`, `fosse_argent_entree`, `fosse_argent_sanctuaire_lugia`, `fse1_fin_jardin_secret`, `fth1_fin_mt_thunder`, `fvc1_fin_couloir_violet`, `great_canyon_entree`, `great_canyon_fin`, `grotte_ouest_entree`, `grotte_ouest_sanctuaire_mewtwo`, `kyurem_cratere_entree`, `kyurem_sanctuaire_glace`, `pmd_destiny_menu_jour` (ses 10 planches `DSTJ_00..09` sont présentes), `reshiram_montagne_entree`, `reshiram_sommet_flamme`, `ruines_enfouies_entree`, `ruines_enfouies_sanctuaire_mew`, `silent_chasm_entree`, `silent_chasm_fin`, `sinister_woods_entree`, `sinister_woods_entree_nuit`, `sinister_woods_fin`, `sinister_woods_fin_nuit`, `tiny_woods_entree`, `tiny_woods_fin`, `zekrom_montagne_entree`, `zekrom_sommet_tornade` ; `flu1_fin_underground_lake` et `fmy1_fin_mystifying_forest` correspondent aux versions publiées `ful1_rive_underground_lake` et `fmf1/fmf2_*` (intégrées). SHA attendus : `docs/audit/inventory_sha.json`. Reconstruction possible par les `build.py` (non exécutée : sorties non vérifiables sans les `.cache`).
* **Grotte Météore** (`grotte_meteore_entree` 80c3cd80/9cb20154/ed349f6a, `grotte_meteore_arene` 09b24b06/5130a233/e25bb61d, `gme1_/gma1_tour_celeste`) : `.rsground` réels dans `renders/grotte_meteore_*/package`, mais leurs 10 planches `GME1_*`/`GMA1_*` sont des liens symboliques vers `.cache` (absents de git) → non intégrées.
* **Placeholders** (blobs de 79–789 o = liens vers `.cache`) : `mer_houleuse_entree/sanctuaire`, `tour_celeste_relais`, `tour_du_temps_entree/pinacle`, `plage_pmd_sky_large`. (`rtc1_tour_celeste` = relais, intégrée.)
* **Intérieurs générés « Metano Normal Home »** `metano_gen_{accueil,cafe,casino,salon_bas,salon_haut}` (4 blobs chacun : 3 versions 0×0 invalides, 1 version 100×75 de 65–139 planches tierces), `metano_reseau_*` (0×0), `treasure_gen_*` (planches `Treasure_*` absentes) : non intégrés (déjà exclus par le socle) ; blobs listés dans `docs/audit/candidates_manifest.json`.
* **Cartes tierces** (références, exclusion décidée) : `guild_path_halcyon(_layers,_palika)`, `luminous_spring(_pmdo)`, `beach`, `altere_pond`, `crooked_cavern_entrance`, `guild_second_floor`, `ledian_dojo`, `treasure_cafe`, `vast_steppe_entrance`, `spinda_cafe`, `treasure_normal_home`.
* **Versions intermédiaires du pack falaises nord centre** : 10 mods individuels (`MOD_01..10_*.zip`, planches `Cliff0N_Canon_*`, cartes plus petites) et 4 blobs git de `cliff_centre_01_*` (0f6d8019, 0f83a791, 02b6d687, 9ea06bef) : remplacés par le PACK consolidé (`CliffCentre10_Canon_*`).
* **Variantes de `cliffnordouesttest1`** 4633c9ab, 84c80b74, 1737733c, 65c48168 (même grille, mêmes planches manquantes ; fonds `CLIFFNW_*` des exports gtp non récupérés car les cartes ne sont pas intégrées).
* `cliffdaytest_2/_3/_4`, `cliffnordouesttest1_2/_3` : noms présents dans la zone du scénario, aucun fichier nulle part.

## 8. WaterfallVillageCapital (town02)
* Fichier natif LFS `Data/Ground/WaterfallVillageCapital.rsground` (233 727 831 o, version 0.8.12.0,
  200×500 cases, 29 calques, sans entités ni musique), copié sans modification.
* **Git LFS refusé par GitHub** : le push LFS a échoué avec
  `This repository exceeded its LFS budget. The account responsible for the budget should increase it to restore access.`
  (le quota LFS du compte est consommé par `town02`). La carte dépassant la limite de 100 Mio des
  fichiers ordinaires, elle est livrée sous forme compressée : `payload/WaterfallVillageCapital.rsground.gz`
  (1 549 395 o, gzip du fichier natif octet pour octet, SHA-256 attendu
  `afc5081f7348b2afed306953bf5e66a358e442cb00f93fa139ec239cf94c98ee`).
  `python3 tools/unpack_payload.py` la reconstitue dans `game/Data/Ground/` et vérifie le SHA-256 ;
  `tools/validate.py` et `tools/build_windows.py` l'appellent automatiquement. Le fichier reconstitué
  est dans `.gitignore`. Si le budget LFS est augmenté, il suffira de retirer la ligne du `.gitignore`,
  de rétablir `git lfs track "game/Data/Ground/WaterfallVillageCapital.rsground"` et de committer le fichier.
  L'objet LFS d'origine reste disponible dans `meromoonmeri/town02` (même SHA-256).
* 37 planches référencées : 36 trouvées dans `town02/Content/Tile` et copiées (4 déjà dans le socle, identiques),
  la 37ᵉ est le nom vide `""` (282 cases, comportement natif). `waterfall_cave_1` : planche `D06p11a_Base` copiée.
* Zone `town02_waterfallvillage` = celle du scénario. Aucune collision de nom avec les cartes existantes.

## 9. Validation et limites
* `python3 tools/validate.py` : toutes les vérifications de contenu passent (chaque carte déclarée
  dans exactement une zone, `AssetName` = nom de fichier, script présent, `Content/Tile/index.idx`
  conforme octet pour octet aux en-têtes des planches, JSON valides). Les seuls messages restants
  concernent les fichiers hors du checkout partiel (`engine/`, `base/`, `art/` exclus de l'espace de travail).
* Contrôle de dépendances final (`docs/audit/final_dependency_problems.json`) : 342 cartes scannées ;
  seules les manques du §7.1 subsistent.
* Noms accentués (`caféspindaaccueil`, `spindacaféétage1`, planches `télécharger (…)`) conservés tels
  quels (noms d'origine de l'utilisateur / de town02) ; sous Windows, PMDO charge les scripts par
  `require 'destiny.ground.<AssetName>'` — à vérifier en jeu pour ces trois cartes d'archives.
* Le moteur PMDO n'a pas pu être lancé dans l'environnement de travail : rendu et scripts restent à
  confirmer en jeu (`-dev -quest`, Dev Warp). Les scripts du scénario proviennent d'une Quest non testée
  par son auteur (voir README du scénario) ; ils n'ont reçu que les correctifs du §5.1.
