# Référence Guildhouse PMD — essai Orival

## Ce qui a été vérifié dans le dépôt

- [`continents_9_iles_10_magenta.png`, commit `2438e89`](https://github.com/meromoonmeri/guilde-treehouse-pmd/blob/2438e89/source/world_map_9_continents_magenta_v2/raws/continents_9_iles_10_magenta.png) : génération brute sur magenta, bosquets en masses, très peu de couleurs par motif et des intervalles lisibles entre les volumes.
- [`world_map_7_continents_generated.png`, commit `d4db33d`](https://github.com/meromoonmeri/guilde-treehouse-pmd/blob/d4db33d/source/world_map_7_continents_v2/raws/world_map_7_continents_generated.png) : génération guidée par des références EoS ; texture ocre tramée, petites crêtes et motifs lisibles. Le README du lot distingue explicitement le rendu de pixels natifs du jeu.
- [`WorldMap_8_Continents_ReverieTown_UserBackground.png`, commit `2438e89`](https://github.com/meromoonmeri/guilde-treehouse-pmd/blob/2438e89/renders/world_map_8_continents_reverie_v1/WorldMap_8_Continents_ReverieTown_UserBackground.png) : montage de références sur le fond utilisateur, avec arbre de Réverie ajouté séparément. Ce n’est pas le même procédé que la génération brute sur magenta.

## Ce qui a changé sur Orival

Le générateur a reçu d’abord un **gabarit de géographie seulement** (côte et eaux d’Orival, grandes zones indicatives sans dessin préalable), puis deux petits détails tirés des rendus du dépôt pour la finition. Forêt dense, crête ambre, décrochements calcaires, bois d’automne et terrasses plus ouvertes sont conçus comme des masses qui se répondent. Aucune silhouette de ces références n’est reprise dans l’atlas.

La génération brute est `Sources/Orival-genere.png`. Le rendu de contour est contrôlé à l’échelle de l’atlas. Après cadrage, le masque généré recouvre le masque d’origine avec une IoU de 99,77 %. La version finale est écrêtée sur le masque approuvé pour préserver **exactement** la côte. Pas de filtre de grain, de peinture procédurale ajoutée au relief, ni de recoloration globale. Les lignes intérieures sont les traits du générateur d’après le gabarit, pas des tracés de navigation.

## Sorties

- `Orival-Guildhouse-Magenta.png` : Orival seul, agrandi à deux fois l’échelle de l’atlas avec un bord libre, clé `#FF00FF`.
- `Orival-Guildhouse-Transparent-2x.png` : même dessin détouré et sans bord libre, 758 × 680 px ; origine dans le plan natif `(72, 78)`, soit `(144, 156)` sur l’atlas entier ×2.
- `Verification-Orival.json` : mesures d’alignement et de clé. Cette étude ne remplace pas encore les autres continents et ne modifie ni le dépôt ni le jeu.
