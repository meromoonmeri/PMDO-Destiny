# Guilde Destiny — plans et charpente

Les **15 cartes de `guilde_destiny_interieur`** ont de nouveaux contours, parois, raccords et collisions. Elles restent à l'échelle native de Destiny (tuiles de 8 px). Aucun meuble, tapis, panneau indépendant, pot, fontaine, nid ou élément de verdure n'est posé. Les baies, montants, escaliers et la porte du bureau appartiennent au bâti. Les anciens atlas de réserve restent disponibles pour l'éditeur, mais aucun de leurs éléments de mobilier ou de verdure n'est référencé par ces cartes.

## Références et adaptation

- [Pokémon Mystery Dungeon: Explorers of Time / Darkness — 3rd Floor of Guild](https://www.spriters-resource.com/ds_dsi/pokemonmysterydungeonexplorersoftimedarkness/asset/5964/) (planche de redblueyellow) : angles du pourtour, échelle en fond, baie du maître décalée, montants et assises de structure. La charpente est redessinée en bois ambré, sans le vert ni les objets de la planche.
- [ExplorersOfSkyOrigins, `0507c4a55b5841b1afe880c09f5c53afb77ca3f6`](https://github.com/Minemaker0430/ExplorersOfSkyOrigins/tree/0507c4a55b5841b1afe880c09f5c53afb77ca3f6) : lecture et rendu des six cartes `guild_basement`, `guild_bedroom`, `guild_dining_hall`, `guild_entrance`, `guild_guildmaster_chambers` et `guild_second_floor`. Nef large et ailes latérales au salon, salle des missions en éventail, volume resserré du bureau, rangée de baies au réfectoire, chambre du héros en cul-de-sac côté est. Les cartes et sprites de référence ne sont pas ajoutés au jeu.

## Accès

- **Falaise ↔ accueil ↔ missions ↔ Grand Salon.** Au Grand Salon, l'échelle du fond donne sur les missions et la porte à sa droite sur le bureau du maître. Les emplacements physiques de ces deux capteurs et de leurs marqueurs de retour ont été déplacés. `SeuilSud` et `ArriveeSudMarker` conservent leur nom pour rester compatibles avec les scripts existants.
- **À gauche du salon**, le carrefour dessert le réfectoire, la cuisine et la réserve. **À droite**, les deux couloirs successifs desservent les quatre dortoirs et la chambre du héros. Le nom historique *couloir ouest* désigne le premier de ces deux couloirs.
- Aucun changement de destination, d'index de zone, de nom de marqueur, ni de script de progression. La porte du bureau conserve son son, ses états ouvert/fermé et le fondu de transition. Les fenêtres sont traversables et se déclinent en quatre ambiances. Les seuils sont des capteurs invisibles, pas des meubles.

## Reconstruire et vérifier

```sh
python tools/build_guilde_charpente.py --apercus /chemin/vers/apercus
python tools/build_tile_index.py
python tools/tests/test_guilde_charpente.py
```

`guilde_plans.py` décrit les contours et les saillies ; `lib_guilde_charpente.py` dessine les matériaux à la résolution des tuiles. Le générateur recalcule le parquet, les parois, les ombres, le premier plan, la grille de collision et les baies. Les quatre calques réservés à l'ancien décor restent vides. L'index de tuiles reconstruit est **généré, pas versionné**. Les anciens générateurs d'intérieur dans `tools/` sont historiques : ne pas les relancer pour éditer ces plans, car ils remettent les anciens contours et la frange végétale.

Le test de `Build Windows` compare les **29 seuils** (28 accès intérieurs et le retour falaise) au réseau attendu, vérifie la marche 16×16, la place du partenaire aux arrivées, l'absence de mobilier et de verdure, le câblage Lua et la porte. Le test Lua utilise `lua5.4` ou `lupa`. La lecture des données ne remplace pas un parcours dans le moteur ni une CI Windows.
