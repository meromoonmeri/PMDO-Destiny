# État de l'harmonisation des chemins — Réverie 0.5.0

## Corrections locales de cette version d'essai

Cette archive remplace le précédent correctif C05/C06, qu'elle inclut ; ne pas installer les deux par-dessus l'un de l'autre. Base : commit `a2db214dc89e675347f670f26594df92158fc9d9`.

| Zone | Intervention |
|---|---|
| C05 et C06, x80–120 et 680–720, y2936–2951 | Adoucir les deux extrémités coupées à l'aide de la bordure Réverie, sans prolongement du chemin. |
| C01, x176–215, y1584–1591 | Atténuer une découpe rectangulaire de la nuance en bas d'un raccord, en réutilisant les nuances d'un bord de Réverie. |
| C03, x1064–1071, y2584–2595 | Retirer une tache de sable rognée et deux pixels d'herbe isolés, en prenant le sable voisin. |
| x992–999, y1576–1583 | Remplacer un carré d'herbe isolé au milieu d'une zone de sable par le sable voisin. |
| x544–551, y2216–2247 | Retirer une ligne verticale de nuance coupée au milieu du sable avec le sable adjacent. |
| x72–79, y568–575 | Restaurer la moitié manquante d'une touffe sur un chemin en copiant la touffe identique et intacte de Réverie. |

La carte garde ses dimensions, son réseau, ses collisions, ses scripts et les séquences d'animation originales. Les interventions ajoutent des pixels en transparence dans des séquences statiques locales du calque `Objects Over`, sans changer les graphismes de Metano ni les autres banques. 33 cases, 23 nouvelles tuiles, 1 615 pixels modifiés dans chaque rendu contrôlé. Les dix variantes de carte produisent les mêmes pixels avant/après aux emplacements retouchés ; l'absence d'animation et de surimpression aux emplacements modifiés a été vérifiée statiquement. L'archive ZIP et les tuiles extraites sont vérifiées.

## Ce qui reste à faire

Les 302 segments suspects relevés sur la carte ont été regroupés en 187 zones de contrôle, et des candidats supplémentaires de taches ont été visualisés. Beaucoup sont des bordures normales, pierres, effets de terrain ou calques proches d'objets : ils ne sont pas tous des erreurs. D'autres raccords ou dégradés imparfaits peuvent subsister, notamment les transitions ambiguës C02/C07/C08 ; il n'est pas possible d'affirmer que tous les défauts de toute la carte ont été éliminés. Une inspection complète à plusieurs phases et dans l'éditeur/jeu est nécessaire avant une correction plus large.

Pas de test en jeu, CI ou publication. Avant installation : sauvegarder le checkout et les parties, puis suivre `LISEZ-MOI.txt` dans l'archive. Si un état de carte ancien est déjà chargé en sauvegarde, il peut garder les graphismes antérieurs jusqu'au rechargement de carte ; ce cas n'a pas été testé avec une vraie sauvegarde.
