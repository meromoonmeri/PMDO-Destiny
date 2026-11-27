# Patati-Patattrape — V4 grand costume, prototype à valider

Vidéo sonore : `Mimiqui-Patati-V4-grand-costume-60ips-son.mp4`. Planche : `Patati-V4-grand-costume-120images.png`, 8 colonnes de cases 128 × 128 pixels, fond transparent et lecture ligne par ligne à 60 images/s. Banque de banc : `PatatiV4_Costume.dir`.

Mimiqui bondit vers la cible. À l'impact, les sprites ordinaires de Mimiqui et de la cible sont masqués ; un grand costume animé descend et les recouvre, avec des ténèbres noires et mauves sous le tissu. Le costume bouge, se contracte et disparaît ; la cible et Mimiqui réapparaissent ensuite. La cible reste masquée durant la séquence du costume. Il s'agit d'une adaptation inspirée de l'animation d'origine, non d'une reproduction exacte : l'absorption est rendue par un masquage et une superposition, pas par le déplacement physique de la cible à l'intérieur du costume. La sortie de la cible est uniquement visuelle ; les dégâts normaux restent appliqués.

## Chance de K.O.

Après une réduction effective des PV, si la cible est encore en vie, un tirage sur 1 000 donne 0,1 % de chance de K.O. Le coup normal est calculé d'abord et les dégâts létaux éventuels ensuite, au cours de la même attaque. C'est une personnalisation demandée, non une règle officielle de la capacité.

## Essais

- Huit orientations en copie isolée, cible à deux cases : huit cibles touchées (270 → 242–245 PV), huit témoins intacts, une charge consommée. Les journaux confirment que les deux sprites sont masqués au début et en fin de séquence, puis réaffichés.
- Un banc séparé a forcé le tirage gagnant : cible 270 → 0, état K.O., témoin intact et masquage retiré. Le tirage forcé n'est pas présent dans le script ordinaire. Voir `journal-v4-ko-force.txt`.
- Les fichiers originaux de la copie de test ont été restaurés et comparés après chaque banc. Vidéo à 60 i/s avec son ; le moteur peut répéter des images si son rendu ralentit.

## Limites

Le masquage est réalisé par le statut neutre `none` provisoirement modifié dans la copie de test. Il faut un statut dédié et un nettoyage fiable en cas d'interruption avant toute intégration réelle. Le costume est un effet animé superposé et apparaît de face dans les huit directions. La cible redevient visible avant le calcul des dégâts, y compris dans le cas d'un K.O. Les cibles adjacentes, alliés, obstacles, bords, immunités, protection, boss et autres protections contre le K.O. ne sont pas testés. Les dégâts létaux directs peuvent contourner des protections ; leurs interactions ne sont pas garanties. Cristal, restrictions et menu Z non intégrés ; aucun push.

Sources : `~/Capacites-Z/Sources/preparer-patati-v4.py`, `patati-v4-effets.lua`, `banc-patati-v4.py`, `test-patati-patattrape.lua`, et variantes `patati-v4-ko-force.lua`, `banc-patati-v4-ko-force.py`, `test-patati-v4-ko-force.lua`.
