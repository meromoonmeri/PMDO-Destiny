# Patati-Patattrape — V5, prototype à valider

Vidéo sonore : `Mimiqui-Patati-V5-sac-ferme-60ips-son.mp4`. Planches transparentes : `PatatiV5_Yeux-planche.png` (60 images) et `PatatiV5_Sac-planche.png` (120 images), cases 128 × 128 pixels, huit colonnes, lecture de gauche à droite puis de haut en bas à 60 images/s. Banques de banc : `PatatiV5_Yeux.dir` et `PatatiV5_Sac.dir`.

Avant le bond, des yeux en spirale et des étoiles s'affichent autour de Mimiqui. Ensuite un grand sac de Mimiqui opaque et fermé, aux oreilles séparées et pointes noires, descend sur la cible et s'agite. La cible et le petit sprite de Mimiqui sont masqués durant la séquence ; une lueur sombre et mauve reste sous le sac. Les deux sprites réapparaissent à la fin. L'enveloppement est un effet visuel inspiré de la référence fournie, non une animation physique de la cible sous le tissu. La sortie de la cible ne supprime pas les dégâts.

## Résultats des bancs isolés

- Huit directions, cible à deux cases : huit cibles touchées (270 → 243–245 PV), témoins latéraux indemnes et charges consommées ; journaux de début et de fin confirmant le masquage et la réapparition.
- Tirage de K.O. fixé à 0,1 % après dégâts effectifs, si la cible survit au coup normal. Un banc séparé force le tirage gagnant : cible 270 → 0, témoin intact et masquage retiré. Le script normal ne force pas le résultat. Journaux : `journal-v5-8-directions.txt`, `journal-v5-ko-force.txt`.
- Après chaque banc, les fichiers originaux de la copie ont été restaurés et comparés. Vidéo encodée en 60 i/s avec son ; certaines images peuvent être répétées si le moteur ralentit.

## Limites

La cible est masquée et réaffichée, sans déplacement physique sous le sac ; les sprites reviennent avant le calcul des dégâts, même en cas de K.O. Le sac apparaît de face dans les huit directions et son aspect reste à valider. Pour les essais seulement, le statut neutre `none` a été temporairement modifié dans la copie : un statut dédié et un nettoyage en cas d'interruption sont nécessaires avant intégration. Alliés, obstacles, bords, cibles adjacentes, immunités, boss et protections contre les K.O. n'ont pas été testés. Les dégâts létaux directs peuvent contourner certaines protections ; interactions non garanties. Cristal, restrictions et menu Z non intégrés ; aucun push.

Sources de banc : `~/Capacites-Z/Sources/preparer-patati-v5.py`, `patati-v5-effets.lua`, `banc-patati-v5.py`, `test-patati-patattrape.lua` ; variantes de test forcé `patati-v5-ko-force.lua`, `banc-patati-v5-ko-force.py`, `test-patati-v5-ko-force.lua`.
