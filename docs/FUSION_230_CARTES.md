# Fusion des 230 cartes manquantes — 31/10/2026

## Ce qui a été fait

La quête `destiny` livrée ne contenait que **25 cartes** (24 `.rsground` + WaterfallVillageCapital).
L'archive Drive `PMD_Destiny_Map_Quest_247_0812.zip` en contient **247 entrées / 213 noms distincts**,
dont **230 absentes** de la livraison. Elles ont toutes été intégrées, avec leurs dépendances.

| | Avant | Après |
|---|---|---|
| `.rsground` dans `game/Data/Ground` | 24 | **254** |
| planches `.tile` dans `game/Content/Tile` | 142 | **1 164** |
| fonds parallaxe `Content/BG/*.dir` | 0 | **36** |
| zones déclarées (`Data/Zone/index.idx`) | 25 | **26** (+ `exploration_cartes`) |
| documentation d'origine | — | **11** fichiers dans `docs/archive_247/` |

Aucune carte existante n'a été écrasée : les fichiers présents ont priorité.
`WaterfallVillageCapital` vient désormais de l'archive Drive (223 Mo bruts) ;
la variante retravaillée (eau animée, chemins) reste disponible dans
`ressources/WaterfallVillageCapital.rsground.gz`.

## Source et intégrité

- Archive : `PMD_Destiny_Map_Quest_247_0812.zip`, 243 355 578 o,
  SHA-256 `45bbdce3e6b246a69308b8b0f826103d1cbecc6ddce48e10e1c59becf80216be`
  (conforme au `README_reconstitution_PMDO_Destiny_247.txt` du Drive).
- Chaque carte restaurée est vérifiée en SHA-256 par `tools/restaurer_cartes.py`.

## Découpage Git / Drive (décidé par la mesure)

| Contenu | Brut | Compressé | Où |
|---|---|---|---|
| 230 `.rsground` | 3 634 Mo | **47 Mo** (÷77) | **Git** — `ressources/CARTES_230/*.rsground.gz` |
| 1 164 planches `.tile` | 925 Mo | ~600 Mo (÷1,5) | **Drive** — non versionnées, manifeste de vérification |
| 36 fonds `.dir` | 2,6 Mo | — | Git |
| docs, zones, scripts | < 1 Mo | — | Git |

Raison : Git refuse un fichier de plus de 100 Mo (`WaterfallVillageCapital.rsground` en fait 223).
Les planches, presque incompressibles, ne peuvent pas non plus être versionnées sans rendre le
dépôt ingérable ; elles restent donc dans l'archive Drive et sont contrôlées par
`ressources/PLANCHES/manifest.json` (nom, taille, SHA-256 des 1 164 planches).

## Restauration

```bash
python3 tools/restaurer_cartes.py .            # décompresse les 230 cartes + vérifie
python3 tools/restaurer_cartes.py . --verifier-seulement
```

## Réserves à connaître

1. **`Content/Tile/index.idx`** (44 Mo, binaire) a été copié depuis l'archive : il indexe
   1 090 planches et **pas** les 74 planches propres à la livraison d'origine. PMDO régénère
   cet index au démarrage (l'index était d'ailleurs absent de la livraison précédente) ;
   à défaut, le supprimer pour forcer la reconstruction.
2. **Deux planches réellement absentes** : `InsideHut` (utilisée par `destiny_hub`) et
   `Treasure_Town_Cafe`. Elles ne sont ni dans l'archive 247, ni dans la livraison, ni dans
   les branches inspectées. Elles ne sont **pas** remplacées : le rendu de `destiny_hub` reste
   vide et le sera en jeu.
3. **229 cartes sur 254 n'ont pas d'entrée de zone** : c'est le fonctionnement de l'archive
   d'origine, où elles sont rattachées à la zone de développement `exploration_cartes`
   (« Zone de prévisualisation … aucune transition, ne fait pas partie de la progression »).
   Aucune entrée de zone n'a donc été inventée.
4. Les cartes `d262_*` sont des **doublons d'inventaire** : 247 entrées pour 213 noms distincts
   (`crooked_cavern_entrance` ×4, `guild_second_floor` ×3, `luminous_spring` ×3, `treasure_cafe` ×3).
   Elles ont été conservées telles quelles, car leurs identifiants sont cités par des zones et
   des scripts.
5. Aucun fichier de script ou de cinématique n'a été réécrit.

## Aperçus

`work/apercus_quete247/PLANCHE_01_sur_09.png` … `_09_sur_09.png` : les 247 cartes rendues tuile
par tuile avec `work/tools/rendre_carte.py`.
