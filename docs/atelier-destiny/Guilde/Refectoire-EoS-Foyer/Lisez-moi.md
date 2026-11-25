# Réfectoire G01P06 · La cheminée de pierre et de bois

Le plan de **Pokémon Donjon Mystère : Explorateurs du Ciel** reste en **504 × 360 px**. Cette version l’habille de bois Destiny. La grande table demeure au centre, la fontaine à droite, et le passage est garde sa place et sa largeur. Un seul foyer se trouve entre les deux fenêtres rondes. Le conduit en dalles de calcaire rejoint la traverse du mur, le manteau est en chêne, et la dalle au sol porte l’âtre.

## Voir le rendu

- **`Refectoire-EoS-Cheminee.mp4`**, livré séparément : salle de jour, comparaison avec la référence G01P06, détail de l’âtre éteint et allumé, ambiance de nuit.
- **`Plans/Refectoire-EoS-Jour.png`** et **`Plans/Refectoire-EoS-Nuit.png`** : vues fixes en PNG RGBA 1×, sans fond autour du plan.
- **`Plans/*-Anime.png`** : APNG complets à quatre poses, 100 ms par pose, avec les flammes, les reflets et l’eau qui bouge. Pour le foyer éteint, utiliser `Plans/*-Foyer-Eteint.png`.

## Recomposition à 1×

Dans `Calques/Jour` et `Calques/Nuit`, la salle bois, l’ameublement, l’eau, le foyer et son raccord de conduit sont séparés. `Foyer-en-place-eteint.png` et `Foyer-en-place-allume.png` sont des **calques 504 × 360 déjà alignés**, pour une pose rapide. Leur ombre de contact est incluse, mais pas la lumière, fournie à part dans `Reflets-pose-1…4.png` (mode **Écran** ; 53 % de jour, 92 % de nuit). Ne pas cumuler le calque déjà aligné avec les petits sprites du foyer.

Pour animer à partir des éléments découpés :

1. Poser `01-Salle-bois.png`, puis `Ombres-mobilier.png` et `Ombre-de-contact.png` en mode Normal. En état allumé, poser le reflet choisi en mode Écran, avant l’ameublement.
2. Poser `02-Table-et-corbeilles.png` et une des 4 cases horizontales de `03-Source-4poses.png` (une case = 504 × 360).
3. Poser `Raccord-sous-traverse.png` à **[228, 76]** et le foyer à **[228, 83]**. `Foyer-eteint.png` = 46 × 94 px ; `Foyer-allume-4poses.png` contient quatre cases de 46 × 94 px. `Braises-et-feu-4poses.png` isole la partie animée de l’âtre à la même taille de case.

`Releve-G01P06.json` détaille les fenêtres, le seuil, la position du foyer et la provenance. Le plan est une **adaptation graphique**, pas une carte installable : la carte Destiny 0.7.7, les deux anciens foyers et les sauvegardes sont intacts. Ne pas remplacer le décor natif du jeu en 576 × 432 avec ces calques G01P06 en 504 × 360.

Références visuelles : [G01P06A](https://projectpokemon.org/home/gallery/image/77579-g01p06apng/) et [G01P06B](https://projectpokemon.org/home/gallery/image/77580-g01p06bpng/) pour le plan, la table et la fontaine ; [G01P05C](https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/) pour les quatre poses de flamme. Étude originale de la cheminée générée pour cette version, puis détourée, reprise en pixel art et ajustée à la travée centrale.
