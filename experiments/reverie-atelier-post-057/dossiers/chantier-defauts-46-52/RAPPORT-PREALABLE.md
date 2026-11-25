# Rapport préalable — captures 46–52 et accès aux ressources

Base de travail : version publiée 0.5.7, commit `ee39156a24f350b67e81740478be8505f4ff1a05`, branche `wip/reverie-integration-kingambit-cafe`. Les images montrent des raccords de falaise ou de berge, de chemins et de végétation ; leur position exacte et leurs calques doivent être établis sur les cartes publiées, sans confondre les annotations, la grille de l’éditeur, des animations et les défauts réels. Les cartes sont des variantes du même paysage ; les changements ciblés doivent rester identiques entre leurs dix versions, sans modifier événements, collisions ou géographie.

Une sauvegarde des cartes et des banques réellement consultées sera créée et vérifiée avant toute modification. Les effets animés seront conservés ; les comparaisons de phase et les vérifications de coordonnées ne remplacent pas un contrôle dans l’éditeur ni dans le jeu. Les zones ambiguës ne doivent pas être repeintes arbitrairement.

## Ressources dans l’éditeur

L’inventaire initial de l’arbre Git de 0.5.7 contient 2 213 fichiers sous `game/Content/Tile`, 82 sous `game/Content/Object`, 74 sous `game/Content/Objects`, et 138 sous `game/Content/Chara` (ces totaux peuvent inclure des index ou fichiers auxiliaires). Les données de base disposent de leurs propres répertoires. La présence d’un fichier ne prouve ni qu’il est indexé, ni qu’il est lisible dans le bon sélecteur de l’éditeur. Les graphismes historiques PMU ne sont pas présumés tous convertis ou libres d’erreurs ; les séquences ne doivent pas être aplaties. Étudier l’API d’import/indexation native et auditer précisément les ressources disponibles avant d’ajouter ou de régénérer quoi que ce soit.

Risques : un index erroné peut cacher des ressources ou écraser des noms ; une fusion de catégories différentes peut altérer animations et références ; le sélecteur `Char Display` ne doit pas être alimenté avec des éléments de décor incompatibles. Ne pas modifier d’autres projets ni promettre la disponibilité exhaustive sans contrôle réel.
