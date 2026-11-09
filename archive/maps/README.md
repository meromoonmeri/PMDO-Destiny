# Maps archivées

Archivage local du 2026-11-04, à partir du commit `46d38a6a143f1966177facddb87459043ec0d20b`.

Les maps de ce dossier ne sont plus chargées par le jeu actif. Le jeu conserve
le scénario actuel, les Chapitres/Source, les donjons actifs, le hub technique
et la carte de menu.

## Contenu

- `game/Data/Ground/` : 341 fichiers `.rsground` non utilisés dans le périmètre actuel.
- `game/Data/Script/destiny/ground/` : scripts associés à ces grounds.
- `game/Data/Zone/` : définitions des zones entièrement archivées et copie de
  l'index des zones avant archivage.
- `game/Data/Map/` : maps `.rsmap` sans zone active.
- `MANIFESTE.json` : zone et index d'origine de chaque ground.

Les tilesets restent dans `game/Content/Tile`. La conversion géographique
validée a été appliquée à toutes les planches concernées avant l'archivage ;
les grounds archivés utilisent donc déjà les nouvelles coordonnées lorsqu'ils
font partie des 198 grounds convertis.

## Réimporter une map

1. Déplacer son fichier `.rsground` vers `game/Data/Ground/`.
2. Déplacer son dossier de script vers `game/Data/Script/destiny/ground/`.
3. L'ajouter à une zone active, ou restaurer une zone archivée complète, puis
   mettre à jour à la fois le fichier de zone et `game/Data/Zone/index.idx`
   avec exactement la même liste `GroundMaps`/`Grounds` et le même ordre.
4. Relancer les validations du projet avant de tester dans le Dev Mode.

Ne pas restaurer `index_complet_avant_archivage.idx` tel quel sauf si toutes
les zones et tous les grounds correspondants sont également restaurés.
