# Audit préalable — raccords d'herbe claire/foncée

Base conservée : version publiée 0.5.0 commit `a2db214dc89e675347f670f26594df92158fc9d9`, reconstruite et vérifiée. La sauvegarde `sauvegarde-avant-chemins-0.5.0.zip` contient les fichiers de départ avant toutes ces corrections ; le correctif de chemins et sable est reconstitué séparément.

## Recherche

Comparer le sol de Réverie au sol de la carte Metano fournie comme référence visuelle, notamment les raccords entre plages d'herbe claires et foncées et les limites artificiellement rectilignes ou carrées. Les changements naturels de palette, les ombres et les objets, dont arbres et fleurs, ne sont pas des erreurs à éliminer. Utiliser une recherche sur toute l'image puis une vérification visuelle des candidats ; une détection automatique à elle seule ne prouve pas un défaut.

## Précautions

Conserver les teintes, textures et la géographie propres à Réverie, sans importer de graphismes Metano. Corriger seulement sur copie, sur les coordonnées vérifiées, en pixels et tuiles natives ; préserver toutes les couches et séquences existantes, les animations, les ombres, les objets, collisions et scripts. Reconstruire les 10 variantes de carte affectées seulement si les compositions de référence sont identiques aux emplacements corrigés. Vérifier les phases et priorités des couches en ces points, les fichiers, les contenus hors modifications et les aperçus avant/après.

Risques : certaines variations rectilignes peuvent être intentionnelles ou correspondre à un décor caché à une autre phase. Ne pas annoncer un état sans défaut sur l'ensemble de la carte ni une validation en jeu après une inspection statique. La copie demande un index régénéré dans un checkout complet et une sauvegarde de partie. La publication exige un accès GitHub en écriture et une CI ; aucun jeton n'est disponible dans l'environnement actuel.
