# Rapport préalable — raccords Réverie et ressources PMU

## Base et sauvegarde

Base de travail : copies locales des cartes `reverie_etang` jeu et Dev issues des déplacements d'arbres, elles-mêmes issues de la branche Destiny `wip/reverie-integration-kingambit-cafe` à `ee39156a24f350b67e81740478be8505f4ff1a05` (v0.5.7). La branche a été vérifiée avant cette intervention ; ne pas modifier le dépôt, une sauvegarde utilisateur ni un autre projet. Préserver ces deux cartes et leurs banques dans une sauvegarde avant toute modification.

## Risques et méthode

Les falaises comportent des retours de roche mauve naturels : une couleur mauve n'est pas en soi un défaut. Comparer les zones aux modules natifs Métano, aux calques et aux phases ; ne pas repeindre globalement, déformer ou effacer les décors. Les chemins doivent se raccorder à l'escalier et aux bords d'herbe, sans masquer cascades et animations. Reprendre d'abord les corrections locales 27 et 51 précédemment auditées lorsque la correspondance exacte des cellules est confirmée ; comparer aussi le rivage 52 sans écraser des données animées. Préserver les arbres récemment déplacés et les corrections 53–55.

Pour PMU, les 40 banques issues de l'instantané client 2014 sont déjà présentes dans Destiny v0.5.7. Elles ne constituent pas tous les objets complets ou leurs animations. Conserver les sources, l'échelle 32 px → grille PMDO 8 px, les trames et durées, et ne pas intégrer de personnages PMU. Ne pas prétendre avoir converti tous les objets à partir de paires de cases non assemblées. Préparer une intégration locale et vérifiable des ressources identifiées, sans la présenter comme exhaustive si elle ne l'est pas.

Tester intégrité des variantes, cellules modifiées, calques, collisions, séquences, références et archive ; prévoir rendu avant/après. Aucun test statique ne remplace PMDO 0.8.12, l'éditeur Windows ou une ancienne sauvegarde. Aucune publication sans accès et vérification de la branche.
