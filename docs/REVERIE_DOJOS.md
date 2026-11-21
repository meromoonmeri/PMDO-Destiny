# Les dojos de Réverie — arènes DTEF

Ce lot se greffe sur [Les chemins de Réverie](REVERIE_CHEMINS.md). Il remplace le prototype des finales au sol brun et à l'anneau commun. Le hall de Kingambit, ses portes coulissantes et les accès à l'arène annexe et aux reliques restent indépendants des dédales. **Ledian et Ossatueur ne sont ni retouchés, ni utilisés comme sources des cartes.** Le duel de Liane et les autres cartes de Réverie sont inchangés.

## Jouer

À l'accueil de Kingambit, parler à **Kaito**. Gauche et droite changent de page dans la liste des 18 types. **Pas maintenant** est la réponse par défaut. En acceptant, le sol se fissure sous l'équipe : le bord du trou annonce le biome choisi. Il est dessiné là où se trouve le héros, en deux plans pour que les sprites s'enfoncent derrière le rebord. Puis viennent **deux étages explorables** et **une arène fixe** avec un maître.

| Type | Dédale | Biome natif | Maître |
|---|---|---|---|
| Normal | des Échos | `tiny_meadow` | Fouinar |
| Feu | des Braises | `mt_blaze` | Caninos |
| Eau | des Remous | `brine_cave` | Mustébouée |
| Plante | des Ronces | `apple_woods` | Balignon |
| Électrik | des Étincelles | `mt_thunder` | Pikachu |
| Glace | du Givre | `frosty_forest` | Polarhume |
| Combat | des Poings | `rock_maze` | Férosinge |
| Poison | des Spores | `murky_forest` | Abo |
| Sol | des Sables | `quicksand_cave` | Kraknoix |
| Vol | des Alizés | `sky_peak_7th_pass` | Nirondelle |
| Psy | des Prismes | `crystal_cave_2` | Spoink |
| Insecte | des Cocons | `forest_path` | Mimitoss |
| Roche | des Éboulis | `rock_aegis_cave` | Tarinor |
| Spectre | des Lanternes | `darknight_relic` | Feuforêve |
| Dragon | des Écailles | `craggy_peak` | Griknot |
| Ténèbres | des Ombres | `deep_dusk_forest_2` | Cornèbre |
| Acier | des Lames | `steel_aegis_cave` | Scalpion |
| Fée | des Lucioles | `mystifying_forest` | Snubbull |

Élèves de niveau 7–8 puis 9–10 ; maître de niveau 12. Pas de ticket, d'objet au sol, de recrutement ni de secours. EXP à 175 % conservée, même en cas de K.O. ou d'abandon (`DungeonStakes.Progress`). Les objets consommés le restent. Le **+** signale une victoire enregistrée et n'interdit pas de rejouer. Retour au hall (17/3), victoire ou non.

## Les deux méthodes graphiques sont séparées

### Arènes du labyrinthe : DTEF du biome

`tools/dojo_dtef.py` décrit 18 plans de **15 × 11** cases : sol, paroi et terrain secondaire. Il suit les 47 cas d'adjacence de l'atelier [`dungeon_autotiles_v1`](https://github.com/meromoonmeri/projet-creation-pmdo/tree/8d2a5b8d9dadef254a0773bb36d633888148adcd/source/dungeon_autotiles_v1) : 6 × 8 cases par matière, tuiles de **24 px** et coins calculés avec leurs voisins. Chaque finale référence directement les cases du même biome que les étages 1F et 2F. Variantes, animations et durées restent celles des fichiers `AutoTile` du jeu de base. Le sol complet est sous les deux calques de relief ; les parois et l'eau, le magma ou les autres terrains secondaires d'ornement ne sont pas praticables. Test de connexité de l'arrivée au maître pour chaque plan.

**Natif** désigne ici les pixels inchangés des tuiles PMDO, pas un dessin généré. Le dépôt n'embarque pas une copie des banques de donjon. La provenance et leurs SHA-256 sont dans [`art/dojo_dedales_trappes/biomes.json`](../art/dojo_dedales_trappes/biomes.json). Les banques Apple Woods, Murky Forest et Quicksand Cave ont été comparées octet par octet avec les copies DumpAsset du dépôt de l'atelier. Les dix-huit plans sont nouveaux ; aucun fond de carte complet n'est repris.

### Trappe : génération guidée, détourage et animation à 1×

Références fournies au générateur : cellules ou planches de biome extraites des banques `.tile` de PMDO, également utilisées pour caler les palettes. Les **huit** dessins source sont des ouvertures originales, pas des tuiles canoniques. Selon la [méthode de l'atelier](https://github.com/meromoonmeri/projet-creation-pmdo/blob/8d2a5b8d9dadef254a0773bb36d633888148adcd/METHODE_MAGENTA_ET_GENERATEUR.md), le magenta balise à la fois le vide extérieur et le puits. `preparer_trappes_magenta.py` supprime la frange, différencie le puits de la lèvre, réduit avec un facteur identique sur les deux axes par vote de matière, utilise la palette du biome sans tramage et nettoie les pixels orphelins. On obtient 18 variantes en **96 × 80 px**, alpha 0/255, avec deux plans `Sol`/`Rebord`. Les images intermédiaires sont préparées sur la même grille ; les poses d'ouverture déplacent des bandes entières de pixels, sans filtrage.

`dessiner_trappe_kingambit.py` produit les **36** DirSheets utilisées en jeu, 10 poses de 5 ticks par plan. Avec `--export`, il sort également les planches PNG et la banque `Kingambit_Trous_24.tile` pour l'éditeur : une ligne par type, une colonne par pose, repères dans `Trous_index.json`. Cette banque d'édition n'est pas nécessaire au jeu : la trappe s'ouvre à une position dynamique et est jouée par les DirSheets.

### Hors labyrinthe : références de fonds fixes

L'[album Map Backgrounds de Project Pokémon](https://projectpokemon.org/home/gallery/album/878-map-backgrounds/) (338 fonds statiques d'Explorateurs du Ciel, extractions de MegaMinerd, album d'evandixon) est réservé aux **nouvelles cartes d'exploration et aux salles de boss hors labyrinthe**. Il sert de référence de composition, matière et perspective pour le pipeline à calques, pas de source des arènes DTEF. Aucun fond de l'album n'est installé ou ajouté au jeu par ce lot.

## Reconstruction

Utiliser une installation complète de PMDO avec `Data/AutoTile` et `Content/Tile`, et des destinations vides. Le premier outil lit également les gabarits natifs `.rsmap` et Zone depuis ce dépôt ; les statistiques de l'équipe et des maîtres ne sont pas modifiées par la reprise graphique.

```sh
python tools/build_dedales_kingambit.py --donnees /jeu/PMDO-Destiny/Data --out /copie/dedales
python tools/dessiner_trappe_kingambit.py /copie/particules --export /copie/edition
python tools/dojo_dtef.py --donnees /jeu/PMDO-Destiny/Data --biome apple_woods --out /copie/dtef
```

La dernière commande est facultative : elle reproduit les planches DTEF à partir des dépendances locales et compare chaque cellule et pose à sa source. Pour refaire le détourage à partir des PNG bruts (archive de travail), installer NumPy, Pillow et SciPy puis exécuter `python tools/preparer_trappes_magenta.py --bruts /sources --donnees /jeu/PMDO-Destiny/Data --out /copie/trappes`. Le décodage et l'assemblage seuls requièrent Pillow.

`python tools/build_tile_index.py` régénère l'index lors de l'intégration de la mise à jour dans un dépôt complet. `tools/tests/test_dojo_kingambit_dedales.py` contrôle plans, références, routes Lua, transparence et phases. Avec `DESTINY_DTEF_DATA=/jeu/PMDO-Destiny/Data`, il résout et compare aussi toutes les références et palettes du jeu de base. `tools/tests/test_dojo_kingambit_complexe.py` vérifie les accès du hall.
