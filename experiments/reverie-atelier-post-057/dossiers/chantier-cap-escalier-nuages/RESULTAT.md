# Grand Cap nocturne : escalier et nuages — travail en cours

## Ce qui a été modifié dans la copie candidate

- L'entrée sud n'est plus directement sur une surface vide : elle est placée sur la suite du grand escalier nord de Réverie. Le dessin provient de l'escalier de la carte de Réverie, sans changement d'échelle ; il a été **assombri/recoloré** pour l'essai nocturne. Les murs sont matérialisés par des obstacles et la voie centrale reste ouverte. Le raccord de position entre les deux cartes est centré sur le même axe ; la sortie sud du Cap est resserrée sur la largeur de l'escalier.
- Le ciel et les 12 phases de mer de V24P01A restent en arrière-plan. Deux couches de nuages nocturnes **défilent indépendamment**, à 9 et 5 pixels par seconde ; elles proviennent des ressources déjà présentes pour `cliffdaytest_nuit`, copiées sans modification. Les nuages fixes qui font partie de V24P01A restent eux aussi présents : tous les nuages ne bougent donc pas.
- La référence T00P04A a guidé la disposition générale : accès par l'escalier au sud, plateau et horizon au nord. Son GIF est 480 × 408, 4 images de 100 ms ; l'analyse des pixels montre que son ciel est fixe, donc l'animation des nuages est une adaptation demandée ici et non une animation reprise de ce GIF.

## Aperçus et tests

- `nuages-vrai-jeu.gif` : **32 captures successives du moteur** PMDO 0.8.12 Linux, assemblées en GIF ; un nuage clair traverse réellement le ciel tandis que la mer s'anime. Le symbole `?` est Missingno, acteur technique du raccourci de test.
- `capture-moteur-escalier.png` : capture moteur à l'entrée du Cap, sur les nouvelles marches. Le test technique a ensuite pu monter jusqu'au bord nord du plateau.
- `apercu-nuages-et-mer-hors-moteur.gif` et `apercu-complet-hors-moteur.png` : recompositions de toute la carte, **pas des captures du jeu**. Le montage animé recalcule le mouvement des couches et des 12 phases d'eau.
- Les cinq calques conservés et les deux calques de bordure préexistants n'ont pas été altérés ; 295 cases d'obstacle ont été ajoutées pour les murs. Les positions d'entrée et une voie centrale de 16 × 16 ont été vérifiées statiquement. Contrôles détaillés dans `preuves.json` et `journal-test-extrait.txt`.

## Limites importantes

La carte est encore un **plateau largement vide** : la composition complète de l'extérieur de la guilde, son bâtiment, ses abords et son accès fermé ne sont pas achevés. La référence est utilisée pour l'approche, pas pour prétendre que la carte de Grodoudou a été reproduite. L'entrée depuis Réverie et le retour complets n'ont pas été retestés sur cette version ; le partenaire, les cinématiques, les sauvegardes et Windows ne sont pas validés. L'apparence du joint avec une version nocturne de Réverie et le choix automatique jour/nuit restent à régler. Certains motifs de ciel/mer sont répétés, et les nuages superposés peuvent nécessiter une retouche visuelle.

La sauvegarde `sauvegarde-candidat-precedent.zip` préserve la version précédant ces modifications, CRC vérifié. Les fichiers de `candidat/` ont été chargés uniquement dans une copie jetable ; **rien n'a été installé dans le projet utilisateur, poussé ou publié**. Le script `construire-index-tuiles.py` prépare un index séparé uniquement depuis l'index v0.5.7 exact ; il n'effectue pas de fusion avec les autres travaux. Les ressources de référence issues de Pokémon Donjon Mystère ne disposent pas ici d'une licence de redistribution établie.
