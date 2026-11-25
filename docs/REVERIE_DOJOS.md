# Les dojos de Réverie — le sceau et les 18 troupes

Ce lot se greffe sur [Les chemins de Réverie](REVERIE_CHEMINS.md). Cette révision prolonge la version DTEF : mêmes salles, nouvelle trappe au sceau et nouvelles troupes. Le hall de Kingambit, ses portes coulissantes et les accès à l'arène annexe et aux reliques restent indépendants des dédales. **Ledian et Ossatueur ne sont ni retouchés, ni utilisés comme sources des cartes.** Le duel de Liane et les autres cartes de Réverie sont inchangés.

## Jouer

À l'accueil du dojo, parler à **Kaito**. Gauche et droite changent de page dans la liste des 18 types. **Pas maintenant** est la réponse par défaut : ni marche, ni trappe. Après confirmation, le héros et son partenaire rejoignent le **sceau orange du hall**. En solo, le chef se place au milieu sans créer de partenaire fictif. Le dessin est ancré au centre du sceau `(384,270)` en pixels monde ; les deux plans du dessin ne sont pas deux trappes. Kaito reste à son poste, hors de l'ouverture, sans animation ni collision avec elle. Un trajet obstrué annule le départ. Ni les portes nord ni leurs marqueurs ne déclenchent l'entraînement.

Viennent ensuite **deux étages procéduraux**, puis la **finale fixe**. Chacun des dix-huit maîtres est un Pokémon évolué, accompagné de deux Pokémon moins évolués de sa propre lignée. Il faut battre les **trois**. L'ouverture du combat reste native et met en place l'équipe du joueur comme dans la version DTEF.

| Type | Dédale | Biome natif | Maître | Sa troupe | Apparition |
|---|---|---|---|---|---|
| Normal | des Échos | `tiny_meadow` | Fouinar | 2 Fouinette | Piste des échos |
| Feu | des Braises | `mt_blaze` | Arcanin | 2 Caninos | Fournaises |
| Eau | des Remous | `brine_cave` | Mustéflott | 2 Mustébouée | Couronne de ressac |
| Plante | des Ronces | `apple_woods` | Chapignon | 2 Balignon | Fougères déroulées |
| Électrik | des Étincelles | `mt_thunder` | Raichu | Pikachu + Pichu | Éclairs fourchus |
| Glace | du Givre | `frosty_forest` | Polagriffe | 2 Polarhume | Éclats de glace |
| Combat | des Poings | `rock_maze` | Colossinge | 2 Férosinge | Bonds et onde de choc |
| Poison | des Spores | `murky_forest` | Arbok | 2 Abo | Brume à bulles |
| Sol | des Sables | `quicksand_cave` | Libégon | Vibraninf + Kraknoix | Fentes de sable |
| Vol | des Alizés | `sky_peak_7th_pass` | Hélédelle | 2 Nirondelle | Piqués des alizés |
| Psy | des Prismes | `crystal_cave_2` | Alakazam | Kadabra + Abra | Téléportation prismatique |
| Insecte | des Cocons | `forest_path` | Aéromite | 2 Mimitoss | Cocons fendus |
| Roche | des Éboulis | `rock_aegis_cave` | Tarinorme | 2 Tarinor | Mégalithes fendus |
| Spectre | des Lanternes | `darknight_relic` | Magirêve | 2 Feuforêve | Sortie des ombres |
| Dragon | des Écailles | `craggy_peak` | Dracolosse | Draco + Minidraco | Volutes draconiques |
| Ténèbres | des Ombres | `deep_dusk_forest_2` | Corboss | 2 Cornèbre | Croissants nocturnes |
| Acier | des Lames | `steel_aegis_cave` | Scalproie | 2 Scalpion | Berceau magnétique |
| Fée | des Lucioles | `mystifying_forest` | Florges | Floette + Flabébé | Pluie de pétales de cerisier |

Élèves de niveau 7–8 puis 9–10 ; maître de niveau 12, troupe de niveaux 8 et 7. Pas de ticket, d'objet au sol, de recrutement ni de secours. EXP à 175 % conservée, même en cas de K.O. ou d'abandon (`DungeonStakes.Progress`). Les objets consommés le restent. Le **+** signale une victoire enregistrée et n'interdit pas de rejouer. Retour au hall (17/3), victoire ou non.

## Les deux méthodes graphiques sont séparées

### Arènes du labyrinthe : DTEF du biome

`tools/dojo_dtef.py` décrit 18 plans de **15 × 11** cases : sol, paroi et terrain secondaire. Il suit les 47 cas d'adjacence de l'atelier [`dungeon_autotiles_v1`](https://github.com/meromoonmeri/projet-creation-pmdo/tree/8d2a5b8d9dadef254a0773bb36d633888148adcd/source/dungeon_autotiles_v1) : 6 × 8 cases par matière, tuiles de **24 px** et coins calculés avec leurs voisins. Chaque finale référence directement les cases du même biome que les étages 1F et 2F. Variantes, animations et durées restent celles des fichiers `AutoTile` du jeu de base. Le sol complet est sous les deux calques de relief ; les parois et l'eau, le magma ou les autres terrains secondaires d'ornement ne sont pas praticables. Test de connexité de l'arrivée au maître pour chaque plan.

**Natif** désigne ici les pixels inchangés des tuiles PMDO, pas un dessin généré. Le dépôt n'embarque pas une copie des banques de donjon. La provenance et leurs SHA-256 sont dans [`art/dojo_dedales_trappes/biomes.json`](../art/dojo_dedales_trappes/biomes.json). Les banques Apple Woods, Murky Forest et Quicksand Cave ont été comparées octet par octet avec les copies DumpAsset du dépôt de l'atelier. Les dix-huit plans sont nouveaux ; aucun fond de carte complet n'est repris.

### Trappe : génération guidée, détourage et animation à 1×

Références fournies au générateur : cellules ou planches de biome extraites des banques `.tile` de PMDO, également utilisées pour caler les palettes. Les **huit** dessins source sont des ouvertures originales, pas des tuiles canoniques. Selon la [méthode de l'atelier](https://github.com/meromoonmeri/projet-creation-pmdo/blob/8d2a5b8d9dadef254a0773bb36d633888148adcd/METHODE_MAGENTA_ET_GENERATEUR.md), le magenta balise à la fois le vide extérieur et le puits. `preparer_trappes_magenta.py` supprime la frange, différencie le puits de la lèvre, réduit avec un facteur identique sur les deux axes par vote de matière, utilise la palette du biome sans tramage et nettoie les pixels orphelins. On obtient 18 variantes en **96 × 80 px**, alpha 0/255, avec deux plans `Sol`/`Rebord`. Les images intermédiaires sont préparées sur la même grille ; les poses d'ouverture déplacent des bandes entières de pixels, sans filtrage.

`dessiner_trappe_kingambit.py` produit les **36** DirSheets utilisées en jeu, 10 poses de 5 ticks par plan. Avec `--export`, il sort également les planches PNG et la banque `Kingambit_Trous_24.tile` pour l'éditeur : une ligne par type, une colonne par pose, repères dans `Trous_index.json`. Cette banque d'édition n'est pas nécessaire au jeu : la trappe se joue par les DirSheets au seul point d’ancrage du sceau.

### Arrivée des troupes : plans sol/air et whooshes générés

`dojo_kingambit_troupes.py` donne le casting, les positions et la pose de révélation. Le forgeron vérifie dans les données PMDO les liens `PromoteFrom` et `Promotions`, la forme disponible et la compatibilité des capacités ; les 54 membres et toutes les positions de scène passent par ces contrôles. Les deux événements Lua encadrent le fondu natif, après `BattlePositionEvent` et avant `BeginBattleEvent`. Ils ne dépensent aucun tour et ne modifient ni l'IA ni les stats. Les ennemis mis en scène sont les vrais combattants, pas des acteurs de décor. Le masque visuel disparaît avant le premier tour.

Les 18 motifs animés ont leurs propres formes et leurs propres mouvements. Psy se montre à l'arrière, disparaît puis réapparaît sur trois autres cases. Spectre avance depuis des nappes d'ombre. Les pétales de cerisier tourbillonnent **avant** l'arrivée du groupe Fée. Pour ces trois effets, de vrais dessins générés sur références officielles ont été détourés et réduits en alpha binaire avec `preparer_motifs_troupes.py` ; le reste des motifs, trajectoires et plans est dessiné en pixels sur une seule grille native. `dessiner_entrees_kingambit.py` fabrique 37 DirSheets de 112 × 112 px : 18 paires de 16 poses et 6 poses pour le départ Psy.

`synthetiser_whooshes_kingambit.py` synthétise 18 partitions sans échantillon externe. Les whooshes, déclenchés une fois par intro, sont des `.ogg` stéréo 44,1 kHz (env. 1–1,6 s), de la nappe grave du Spectre au souffle cristallin de Fée. La mise en scène et le déclenchement du son ont lieu avant le premier tour ; la condition `map_clear_check` contrôle ensuite l'ensemble du groupe.

### Hors labyrinthe : références de fonds fixes

L'[album Map Backgrounds de Project Pokémon](https://projectpokemon.org/home/gallery/album/878-map-backgrounds/) (338 fonds statiques d'Explorateurs du Ciel, extractions de MegaMinerd, album d'evandixon) est réservé aux **nouvelles cartes d'exploration et aux salles de boss hors labyrinthe**. Il sert de référence de composition, matière et perspective pour le pipeline à calques, pas de source des arènes DTEF. Aucun fond de l'album n'est installé ou ajouté au jeu par ce lot.

## Reconstruction

Utiliser une installation complète de PMDO avec `Data/AutoTile` et `Content/Tile`, et des destinations vides. Le premier outil lit également les gabarits natifs `.rsmap` et Zone depuis ce dépôt ; les statistiques de la troupe proviennent des formes choisies dans les données et des niveaux décrits ci-dessus.

```sh
python tools/build_dedales_kingambit.py --donnees /jeu/PMDO-Destiny/Data --out /copie/dedales
python tools/dessiner_trappe_kingambit.py /copie/trappes --export /copie/edition
python tools/dessiner_entrees_kingambit.py /copie/troupes --export /copie/feuilles-vfx
python tools/synthetiser_whooshes_kingambit.py /copie/sons
python tools/dojo_dtef.py --donnees /jeu/PMDO-Destiny/Data --biome apple_woods --out /copie/dtef
```

La dernière commande est facultative : elle reproduit les planches DTEF à partir des dépendances locales et compare chaque cellule et pose à sa source. Pour refaire le détourage à partir des PNG bruts (archive de travail), installer NumPy, Pillow et SciPy puis exécuter `python tools/preparer_trappes_magenta.py --bruts /sources --donnees /jeu/PMDO-Destiny/Data --out /copie/trappes`. Pour reprendre les trois nouveaux dessins bruts, utiliser `python tools/preparer_motifs_troupes.py /sources/troupes /copie/motifs`, puis passer `--art /copie/motifs` au dessinateur de finales. Le décodage et l'assemblage seuls requièrent Pillow ; l'export des sons requiert aussi FFmpeg avec `libvorbis`.

`python tools/build_tile_index.py` régénère l'index lors de l'intégration de la mise à jour dans un dépôt complet. `tools/tests/test_dojo_kingambit_dedales.py` contrôle plans, références, routes Lua, transparence et phases. Avec `DESTINY_DTEF_DATA=/jeu/PMDO-Destiny/Data`, il résout et compare aussi toutes les références et palettes du jeu de base. `tools/tests/test_dojo_kingambit_complexe.py` vérifie les accès du hall ; `tools/tests/test_dojo_kingambit_troupes.py` relit les 582 poses, les sons et les événements de scène.
