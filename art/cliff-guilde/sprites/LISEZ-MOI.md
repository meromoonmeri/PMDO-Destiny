# Sprites indépendants de la Guilde HD (feuillage fixe, sans brasiers)

Ressources prêtes à placer sur les 4 cartes nues `guilde_cliff_{jour,aube,crepuscule,nuit}.rsground`, laissées vides volontairement.

## Objets PMDO générés (`game/Content/Object/`, `262×262`, 1 frame statique)
- **Guilde porte fermée :** `Guilde_HD_{Jour,Aube,Crepuscule,Nuit}.dir`
- **Guilde porte ouverte (vantaux vers l'extérieur) :** `Guilde_HD_Porte_Ouverte_{Jour,Aube,Crepuscule,Nuit}.dir`
- **Calque d'ombre au sol séparé :** `Guilde_HD_Ombre_{Jour,Aube,Crepuscule,Nuit}.dir`

## Caractéristiques & placement recommandé
- **Feuillage fixe :** aucune animation de vent sur les feuilles.
- **Indépendance :** les deux brasiers avant (`furnace`) sont exclus du sprite et du calque d'ombre ; détourage propre sur magenta (`#FF00FF`) sans contour blanc.
- **Position à l'extrémité nord de la falaise :** `MapLoc = (X: 109, Y: 24)` (`0` pixel d'ombre ou de racine hors falaise, `83 px` d'esplanade herbeuse devant le haut de l'escalier à `Y = 365`).
- **Ordre des calques :** poser d'abord `Guilde_HD_Ombre_<Ambiance>` puis `Guilde_HD_<Ambiance>` (ou `Guilde_HD_Porte_Ouverte_<Ambiance>`) aux mêmes coordonnées `(109, 24)`.
