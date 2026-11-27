# Canon Blindé V2 corrigée — prototype à valider

Le rectangle provenait de la texture du corps du rayon : le moteur étire cette ligne sur toute sa longueur. Cette partie est désormais entièrement transparente. La tête et la queue de flammes restent visibles et les flammes natives sur la trajectoire remplissent le tir ; charge et explosion sont inchangées. La largeur graphique de la banque reste de 112 pixels, mais sa partie centrale est désormais transparente : les limites visibles viennent des sprites de flammes, pas d'un rectangle.

Capture en jeu avec son, 60 images par seconde : `Carmadura-Canon-Blinde-V2-corrige-60ips-son.mp4`. Le banc a réussi dans les huit directions : trois cibles blessées et brûlées, deux témoins intacts, PP 5 → 4, Défense et Défense Spéciale du lanceur à −1. Une case d'impact correcte par direction. Un test de mur frontal à deux cases a confirmé l'impact sur le mur, le mur intact et le témoin derrière indemne. Journal : `journal-v2-corrige.txt`.

La zone de touche expérimentale reste une bande de trois cases, sur une portée de trois cases. Brûlure garantie : adaptation expérimentale non canonique. L'explosion est visuelle, sans dégâts de zone supplémentaires ni destruction de mur. Immunités, protections, murs diagonaux et interruptions restent à vérifier. La copie isolée a été restaurée et comparée ; aucune intégration ni aucun push.
