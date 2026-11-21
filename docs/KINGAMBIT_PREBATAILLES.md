# Kingambit — les dix-huit wooshes de prébataille

Extension du lot **Cyclones–Météo**. Le maître et ses deux cadets arrivent comme avant. Une transition courte signe le type de l'épreuve une fois la troupe en place, puis l'événement natif `BeginBattleEvent` lance le combat. Aucun changement dans les cartes, les espèces, les niveaux, les règles Méga, le menu des dojos, la musique ou les conditions de victoire.

## Dix-huit signatures

| Type | Maître | Woosh |
|---|---|---|
| Normal | Lockpin | Double écho : rubans ivoire et deux anneaux d'écho. |
| Feu | Braségali | Braises en éventail : bandes qui ondulent et flammèches ascendantes. |
| Eau | Tortank | Roulis des marées : crêtes en contre-courant et arcs d'écume. |
| Plante | Jungko | Entrelacs de feuilles : vrilles et petites feuilles détachées. |
| Électrik | Élecsprint | Circuit foudroyant : filaments brisés qui claquent sur les côtés. |
| Glace | Oniglali | Fracture polaire : éclats radiaux et flocon taillé dans la glace. |
| Combat | Lucario | Frappes croisées : chevrons latéraux brefs et sceau en forme de poing. |
| Poison | Ectoplasma | Miasme à bulles : voiles roulés et bulles montantes. |
| Sol | Laggron | Lignes de faille : plusieurs strates et une cassure basse. |
| Vol | Dracaufeu | Plumes d'alizé : grandes courbes et plumes en piqué. |
| Psy | Alakazam | Réfraction mentale : trois losanges en miroir autour de l'œil. |
| Insecte | Dardargnan | Ruée de l'essaim : sillages découpés et alvéoles. |
| Roche | Tyranocif | Éclats de carrière : blocs cassants avec des fragments taillés. |
| Spectre | Branette | Feux-follets : ombres en contre-courant et quatre petites veilleuses. |
| Dragon | Altaria | Sillage des écailles : grandes courbes en S et écailles qui s'écartent. |
| Ténèbres | Démolosse | Croissants nocturnes : bordures d'ombre et demi-lunes. |
| Acier | Métalosse | Verrou magnétique : rails rivetés et mâchoires métalliques qui se ferment puis repartent. |
| Fée | Gardevoir | Étoiles de soie : bandes or et rose, étoiles en tête et en gerbe. |

## Référence et différence

La transition `Pre_Battle_Dazzling_Etoiles` de [`cliffdaytest`](../game/Data/Script/destiny/ground/cliffdaytest/init.lua) est la référence : bandes traversantes alternées, motifs qui les mènent, particules, calque plein écran. Dazzling change de scène sur un blanc plein. Ici on reste dans la même arène, donc le masque se résorbe sans blanc plein, fondu de carte ou coupure de musique. Dessins et sons originaux par type, aucune reprise des pixels ou des samples du woosh Dazzling. La scène de Dazzling n'est pas éditée.

## Intégration et cadence

1. Les événements existants `-15 / -11 / -9` placent puis révèlent les équipes comme avant.
2. Le raccord ajouté à `destiny/event.lua` enveloppe uniquement `DestinyDojoTroupeJouer`. Le nouveau module vérifie zone, finale 3F, type et troupe de trois. Il attend 4 ticks quand le maître et les cadets sont en place.
3. `Kingambit_Prebataille_<type>` : une banque BG et un Ogg dans `Sound/Battle`. `FiniteOverlayEmitter` non répété, centré sur `DungeonScene.ViewRect`, calque `Top`. 320 × 240 px, 28 poses × 3 ticks, 84 ticks (1,40 s à 60 i/s). Première/dernière cellules transparentes. Une seule lecture de son. Le module restitue `CutsceneMode` même si un asset ou un son manque.
4. Après deux ticks de marge, `BeginBattleEvent` à `-5` reprend avec `map_clear_check`. Le lot n'ajoute ni tour, ni effet météo, ni statut, ni code de transformation.

```sh
python tools/dessiner_prebatailles_kingambit.py --out /copie/prebatailles --reviews
LUA_PATH='./game/Data/Script/?.lua;;' lua tools/tests/test_dojo_kingambit_prebatailles.lua
```

Pillow, NumPy, SciPy et FFmpeg/libvorbis sont nécessaires à la reconstruction. Les banques précompilées sont dans `game/Content`. Grille atlas 7 × 4, RGBA prémultiplié dans les `.dir` et alpha droit pour les planches de revue. Hors dépôt, le banc PMDO Linux 0.8.12 entre directement dans chaque finale, enregistre les images et le son du moteur, et contrôle l'ordre apparition → woosh → combat. Il ne teste pas la traversée complète depuis le hall ni un build Windows Destiny.
