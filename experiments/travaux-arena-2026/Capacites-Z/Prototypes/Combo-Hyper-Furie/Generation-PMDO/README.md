# Combo Hyper-Furie — V2 sans mains humaines

Capture en donjon : `Mackogneur-Combo-Hyper-Furie-V2-8-directions-son.mp4`.

La première idée, un poing réaliste, a été rejetée : elle n'est pas retenue dans la galerie. La V2 reprend le vocabulaire des effets PMDO Combat étudiés dans `References-PMDO-Combat` : rythme alterné et impacts rouge/blanc de `Close_Combat`, succession de frappes de `Bullet_Punch`, impacts éclatés de `Arm_Thrust`. Les nouvelles formes sont abstraites : traces directionnelles et éclats, sans mains ni bras. Mackogneur utilise sa propre animation native de combat.

Les deux images d'effet sont générées avec IA d'après des références PMDO. Les 26 poses sont recomposées à partir de ces deux images (déplacement, taille, opacité), puis tournées pour constituer huit lignes : ce ne sont pas 26 dessins indépendants par orientation. Les coups successifs sont visuels ; le moteur applique un seul calcul de dégâts pour l'attaque. Son `DUN_Close_Combat` natif.

Essai en copie isolée : AttackAction sur la case adjacente face au lanceur, une cible Tortank et un témoin latéral placés par script, déclenchement scripté. Huit orientations, huit cibles touchées (PV 114 → 63–67), huit témoins intacts à 114 PV, PP consommés. Voir `journal-v2-8-directions.txt`. Puissance 75 et catégorie physique provisoires ; murs, alliés, autres Pokémon, menu, cristal, conversion depuis la capacité de base et limite Z restent à tester ou implémenter. La fiche initiale, l'intro et les sauvegardes de banc ont été restaurées après capture.
