# Réverie Town — nouvelles planches autonomes

Ces planches ont été fabriquées à partir des éléments réellement utilisés dans les cartes de Réverie 0.4.16. Ce ne sont pas de simples fichiers Metano renommés : les 39 091 tuiles effectivement référencées ont été extraites, classées et réassemblées en 14 nouveaux fichiers `.tile` et 14 PNG ; les coordonnées ont changé et les dix cartes de ville ont été raccordées à ces nouvelles banques. Les tuiles ont conservé les pixels des ressources existantes : ce n'est pas une redéfinition des droits ou de la provenance des dessins.

## Dans l'éditeur PMDO

Ouvrir une carte Réverie avec le Ground Editor et sélectionner l'onglet `Textures`. Le navigateur `Tiles` contient les 14 nouvelles banques dont les noms commencent par `Reverie_Geo_`. Elles regroupent notamment sol, chemins, rivières, rives, falaises, franges, bâtiments, cascades et décors. Les PNG correspondants sont dans `Sources_Reverie/Planches_PNG` dans la distribution Windows et `art/reverie/tilesheets` dans les sources.

Les cartes jouables conservent 11 calques composites et les copies `_Dev` 37 calques d'édition. Les noms et l'organisation des calques restent pour l'instant ceux des cartes d'origine : la création de nouvelles planches ne transforme pas automatiquement leurs 37 couches en couches sémantiques indépendantes. Les copies d'édition restent distinctes des cartes jouables.

## Précautions

Le classement des cases de terrain utilise une règle automatique et certains éléments précomposés ne peuvent pas être séparés parfaitement en sol, eau et chemin sans restauration manuelle : des cases ambiguës sont regroupées dans `Terrains_mixtes` ou `Paysages_composites`. Les planches ne sont donc pas garanties comme une bibliothèque de sprites parfaitement détourés. Les PNG montrent des images statiques ; les séquences d'animation et cadences sont conservées dans les cartes natives, avec des références vers les nouvelles banques.

Toutes les références des dix cartes ont été remappées et leur conversion inverse reconstitue exactement les fichiers de 0.4.16. Chaque tuile a été comparée aux octets d'origine, et PMDO 0.8.12 a chargé les dix cartes et vérifié l'index des 39 091 positions dans une copie sans les anciennes banques de ville. Ces vérifications ne remplacent ni l'ouverture visuelle de l'éditeur, ni une partie complète, ni le test d'anciennes sauvegardes.

Les anciennes banques `Reverie_WV_*` restent pour le moment dans la distribution par précaution, afin de ne pas casser d'éventuels usages ou anciennes sauvegardes. Les dix cartes converties n'y font plus référence et ne référencent pas `Metano_Town`. Ne supprimez pas les anciennes banques d'une installation personnelle sans sauvegarde et contrôle. L'édition de PNG n'est pas répercutée automatiquement dans les `.tile` ou les cartes.
