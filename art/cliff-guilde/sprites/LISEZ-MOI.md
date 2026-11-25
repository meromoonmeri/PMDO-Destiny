# Sprites indépendants de la Guilde HD (feuillage fixe, sans brasiers)

Ressources prêtes à placer sur les 4 cartes nues `guilde_cliff_{jour,aube,crepuscule,nuit}.rsground`, laissées vides volontairement.

## Objets PMDO générés (`game/Content/Object/`, `262×262`, 1 frame statique)
- **Guilde porte fermée :** `Guilde_HD_{Jour,Aube,Crepuscule,Nuit}.dir`
- **Guilde porte ouverte (vantaux vers l'extérieur) :** `Guilde_HD_Porte_Ouverte_{Jour,Aube,Crepuscule,Nuit}.dir`
- **Calque d'ombre au sol séparé :** `Guilde_HD_Ombre_{Jour,Aube,Crepuscule,Nuit}.dir`

## Banques de tuiles PMDO pour le Dev Editor (`game/Content/Tile/`, `TileSize = 8`)
Les quatre variantes d'ambiance sont également accessibles directement dans **Ground Editor → Textures → Tiles** (comme les banques `PMU_*`), régénérées par `tools/build_guilde_hd_tiles.py` :
- `Guilde_HD_Jour.tile`
- `Guilde_HD_Aube_FILTRE.tile`
- `Guilde_HD_Crep_FILTRE.tile`
- `Guilde_HD_Nuit_FILTRE.tile`

Chaque banque (`66 × 46` cases = `528 × 368 px`) contient :
- **Guilde porte fermée :** cases `(0..31, 0..31)` (`32 × 32` tuiles)
- **Guilde porte ouverte :** cases `(34..65, 0..31)` (`32 × 32` tuiles)
- **Ombre au sol séparée :** cases `(0..33, 34..45)` (`34 × 12` tuiles, centrée avec décalage `(+5, +3) px`) ; en posant la guilde à `(tx, ty)`, tamponner l'ombre sur un calque inférieur à `(tx - 1, ty + 21)` pour un alignement exact à `0,0 px`.

## Caractéristiques & placement recommandé
- **Feuillage fixe :** aucune animation de vent sur les feuilles.
- **Indépendance :** les deux brasiers avant (`furnace`) sont exclus du sprite et du calque d'ombre ; détourage propre sur magenta (`#FF00FF`) sans contour blanc.
- **Position à l'extrémité nord de la falaise :** `MapLoc = (X: 109, Y: 24)` (`0` pixel d'ombre ou de racine hors falaise, `83 px` d'esplanade herbeuse devant le haut de l'escalier à `Y = 365`).
- **Ordre des calques :** poser d'abord `Guilde_HD_Ombre_<Ambiance>` puis `Guilde_HD_<Ambiance>` (ou `Guilde_HD_Porte_Ouverte_<Ambiance>`) aux mêmes coordonnées `(109, 24)`.
