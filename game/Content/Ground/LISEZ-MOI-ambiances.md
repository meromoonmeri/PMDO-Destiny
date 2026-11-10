# Cliff — quatre ambiances jouables

Trois cartes et leurs ressources. `cliffdaytest` (jour) n'est pas modifié : il
n'apparaît pas dans ce commit.

## Cartes

| Carte | Falaise | Ciel | Mer |
|---|---|---|---|
| `cliffdaytest` (inchangée) | jour | T00P04A | jour EoS |
| `cliffdaytest_aube` | jour, filtre aube | dérivé du ciel de jour | jour, filtre aube |
| `cliffdaytest_crepuscule` | jour, filtre crépuscule | dérivé du ciel de jour | jour, filtre crépuscule |
| `cliffdaytest_nuit` (remplacée) | **jour, filtre nuit** | Réveil, lune, étoiles | jour, filtre nuit |

La nuit utilise donc exactement le relief du jour, assombri par le filtre de
l'ancien agent (×0,38 / 0,46 / 0,62), au lieu d'un terrain de nuit distinct.

## Ressources ajoutées

- `Tile/PICHU_CLIFF_DAY_{TERRAIN,SEA,CANOPY}_{NUIT,AUBE,CREP}_FILTRE.tile`
- `Tile/{Reverie_Town_Cliffs,13_avancee_basse_gauche_terrain,Reverie_Town_Animation_Tileset}_{NUIT,AUBE,CREP}_FILTRE.tile`
  (quelques cases du terrain emploient ces petites feuilles ; sans teinte,
  elles restaient lumineuses au milieu du terrain assombri)
- `BG/CLIFF_{AUBE,CREPUSCULE}_{CIEL,NUAGES_HIGH,NUAGES_MID,NUAGES_HORIZON}.dir`

## Ce qui reste à faire dans le moteur

- Ces cartes ne sont **pas encore déclarées** dans `destiny_cliff_tests` (zone)
  ni atteignables par une sortie : aucune entrée n'a été ajoutée sans ton accord.
- Aucun essai dans PMDO n'a été fait. Les contrôles ici sont des rendus hors
  moteur : géométrie, obstacles et entités recopiés à l'identique de la carte
  source, vérifiés par comparaison.
- L'aube et le crépuscule restent des adaptations colorimétriques : aucune
  source canonique de ciel d'aube ou de crépuscule Cliff n'existe dans le dépôt.
