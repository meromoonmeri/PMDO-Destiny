# Gare au Ronflex — V1 expérimentale, banc isolé

Ronflex utilise un mouvement inspiré du saut natif de Rebond, porté ici à trois cases et arrêté à la première cible ou au mur. L'effet visuel combine les textures natives **Giga_Impact_Back** et **Giga_Impact_Front** de Giga Impact (type Normal), avec une onde d'impact générée par IA et animée en 24 images. Les deux précédentes images IA de poussière sont conservées comme essais mais ne sont pas utilisées. Les sons proviennent de Giga Impact et de Plaquage.

La fiche de test conserve type Normal, catégorie physique, puissance 210 et ajoute le contact. Dans une pièce dégagée, sur huit orientations : 8 cibles Leuphorie touchées, 8 témoins latéraux indemnes et une charge consommée à chaque essai. Le premier banc avait dû être interrompu : Ronflex avait mis la cible K.-O. dès le premier tir. Le second banc utilise un Ronflex niveau 30 et des Leuphorie niveau 100, pour permettre de mesurer les huit directions. Les originaux de la copie de test ont été restaurés et vérifiés.

Vidéo sonore : `Ronflex-Gare-au-Ronflex-V1-test-son.mp4`. C'est une capture à 60 images/s, ce qui ne garantit pas 60 changements d'image du jeu par seconde. Voir `journal-v1-8-directions.txt`.

**Limites :** la trajectoire et l'écrasement sont une adaptation PMDO et pas une reproduction littérale de la cinématique officielle. Le banc est scripté ; alliés, obstacles, bords, cibles immunisées et enchaînements n'ont pas été validés. Les conditions Ronflex / Giga Impact / Ronflézélite, le menu et le système Z ne sont pas intégrés. La puissance reste à équilibrer en conditions réelles. Aucun push n'a été effectué.

Sources : `~/Capacites-Z/Sources/preparer-gare-au-ronflex.py`, `animer-gare-au-ronflex.py`, `test-gare-au-ronflex.lua` et `intro-halo-banc-ronflex.lua`. La fiche produite est strictement test-only.
