# Éruption Géo-Sismique — V2 expérimentale

`Carchacrok-Eruption-Geo-Sismique-V2-eau-8-directions-son.mp4` est une capture sonore de la capacité déclenchée dans la copie isolée de Destiny/PMDO. Carchacrok sert au banc : la capacité est générique.

## Corrections réalisées

- Fissures radiales sous le lanceur, puis fissure locale au pied de chaque pointe lors de l'impact. Les pointes montent depuis le sol, restent brièvement, puis disparaissent avec des débris. Les impacts se succèdent. Les deux formes sources de la V1 sont issues du générateur d'images ; 24 poses de fissure et 22 poses de pointe sont recomposées (découpe, déplacement, fondu et débris), et non dessinées indépendamment. Les huit lignes sont identiques, car les effets sont radiaux/verticaux.
- La palette est choisie automatiquement à partir de l'autotile du lanceur : 476 autotiles existants dans la copie ont été échantillonnés sur leur première tuile, puis classés dans neuf palettes. Voir `correspondance-palettes-auto.csv`. Si l'autotile est absent ou inconnu, la palette terre sert de repli. Cela fournit une adaptation approximative, pas la preuve d'un rendu approprié dans tous les biomes : un seul donjon a été filmé/testé, et les différences locales ou les textures ajoutées ultérieurement ne sont pas analysées en temps réel. L'ensemble de l'attaque emploie la palette de la case du lanceur, même sur des sols mélangés.
- Le lanceur sur `water` ou `water_poison` ne peut pas utiliser l'attaque : l'événement l'annule avant consommation de PP. Sur le banc, les deux cas ont donné échec, PP 1→1 et PV de la cible inchangés. L'interdiction concerne le terrain du lanceur ; le cas d'une cible sur l'eau n'a pas été testé.

## Résultats et limites

Huit orientations sur terrain aménagé : 24/24 cibles touchées, 8/8 témoins à distance 3 intacts et PP 1→0 ; après cela, deux refus sur eau. Journal `journal-v2-8-directions-et-eau.txt`. Aucun obstacle, allié ou changement de biome en cours de combat n'a été vérifié. Le flood-fill natif ne garantit pas une attaque à travers les murs.

Les règles Z, le menu, le cristal et l'intégration à Destiny ne sont pas implémentés : fiche et événement test-only, installation dans la copie de banc. Les fichiers d'origine, les sauvegardes et le service de test ont été restaurés après la capture. Le générateur `Capacites-Z/Sources/preparer-eruption-geo-sismique-v2.py`, le script Lua et le banc conservent le travail reproductible ; leurs chemins attendent les ressources d'une copie PMDO/Destiny compatible. La V1 reste conservée.
