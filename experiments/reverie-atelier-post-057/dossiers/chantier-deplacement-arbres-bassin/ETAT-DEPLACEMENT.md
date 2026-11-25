# Bassin de Réverie — déplacement des arbres près des falaises

## Base et méthode

Candidat local, basé sur les cartes jeu et Dev des corrections 53–55. L'archive complète de cet état, avec ses cartes originales, journaux et banques, est conservée dans `sauvegardes/`. Aucun fichier de jeu n'a été installé ou publié.

Les quatre arbres correspondant aux zones de falaise des captures 53–55 sont déplacés comme éléments complets, avec leur feuillage, leur tronc et leur ombre native. Les coordonnées ci-dessous désignent l'origine du rectangle de motif en cases de 8 px :

| Arbre | Avant | Après | Déplacement |
|---|---|---|---|
| Ouest haut | (97,253) | (95,252) | 16 px à gauche, 8 px vers le haut |
| Ouest milieu | (97,262) | (95,261) | 16 px à gauche, 8 px vers le haut |
| Ouest bas | (98,272) | (95,271) | 24 px à gauche, 8 px vers le haut |
| Est | (158,263) | (158,260) | 24 px vers le haut |

À l'ouest, un simple déplacement vertical ne suffisait pas à dégager le rebord vertical : les arbres sont aussi légèrement décalés horizontalement. Les fragments de chaque arbre sont issus du même motif natif ; quatre fragments manquants au pied de l'arbre ouest supérieur ont été reconstitués depuis le motif complet. Les autres fragments présents dans une cellule partagée sont conservés. Une touffe de fleurs animée voisine, qui se retrouvait sur le feuillage, a été décalée de 8 px à gauche, en conservant ses trois phases et leur durée. Certains feuillages se chevauchent naturellement ; leur rendu mérite une vérification en jeu.

Les 19 anciennes surimpressions de falaise utilisées pour masquer les ombres sont retirées : ce n'est plus le moyen employé pour résoudre ces quatre cas. Dans le calcul statique, aucun pixel des couleurs de l'ombre du bas de chacun des quatre motifs déplacés ne recouvre une tuile opaque du calque `Cliffs`. Ce test ciblé n'est pas un audit de toutes les ombres de la carte.

Le déplacement de l'arbre est a découvert des coutures rectilignes anciennes dans le sol. Elles sont reprises dans `Base` avec un masque de pixels de la tuile d'herbe native existante, sur 18 cellules. L'archive contient la banque `Reverie_Correction_Deplacement_Bassin.tile` ; la correction des traits précédents nécessite également `Reverie_Correction_Herbe_55.tile`. La banque d'ombres précédente est conservée dans l'archive de sauvegarde, mais ne reste pas référencée par ces cartes.

## Collisions et contrôles

À l'est, 46 cellules de collision ont été ajustées pour suivre le déplacement, en conservant les obstacles là où subsiste une falaise ou un autre élément. Les cases ouest étaient déjà dans une zone globalement bloquée : leurs collisions préexistantes ont été conservées, ce qui peut laisser des obstacles invisibles et doit être vérifié en jeu. Aucune garantie de circulation réelle sans test moteur.

Pour chacune des deux variantes, une comparaison intégrale avec le candidat 55 confirme qu'après annulation des 450 cellules de calque et 46 collisions journalisées, toutes les données sont identiques : notamment événements, entités, scripts et autres calques. La touffe animée déplacée conserve ses données de phases et de cadence ; les autres animations sont inchangées. Les masques de sol sont relus et comparés à leurs pixels source. Sur une approximation statique à grille 16×16, les six points testés autour du chemin est gardent leur état d'accessibilité depuis le point de départ ; 696 positions accessibles avant contre 686 après. Ce test ne valide pas tous les trajets ni les mouvements PMDO.

Les corrections de sol près de la souche et des fleurs ainsi que les arbres et l'animation déjà corrigés en 53–54 sont conservés. Le cercle entre les arbres sud-ouest, les rives et chemins précédemment signalés restent à examiner. Aperçus statiques uniquement ; pas de test PMDO 0.8.12, d'animation, de sauvegarde réelle, de CI ni de publication. Vérifier les collisions et raccords en éditeur et en jeu avant intégration.
