# Falaise de guilde — parois prolongées et raccord Métano

## Correction

- `cliff-corrige-magenta.png` : falaise nue sur fond #ff00ff, 480 × 416 pixels. Les parois continuent au bas de l'image de part et d'autre de l'escalier. La forme générale du plateau et l'escalier n'ont pas été déplacés.
- `cliff-corrige-transparent.png` : même recomposition sur transparence. Les quatre calques PNG séparés ont chacun les mêmes dimensions ; la grille est de 8 px.
- Le filet artificiel de la version précédente est remplacé par des morceaux du rebord herbe/roche du rendu nord de Réverie, en taille d'origine ; les portions de 8 × 11 px sont positionnées sur le tracé du plateau. C'est une adaptation à cette forme, et non une bordure native préexistante à l'identique. Le raccord conserve des ressauts de jonction et doit encore être peaufiné visuellement, notamment aux changements de pente.
- Les colonnes de roche sont prolongées depuis les extraits de la paroi d'escalier du rendu nord de Réverie. 84 pixels de deux coutures d'herbe accidentelles ont été remplacés par leurs voisins rocheux : retouche locale documentée, sans changement de couleur des pixels réemployés. Les colonnes restent répétitives.
- La version antérieure est conservée dans le sous-dossier `sauvegarde/`. Les dimensions divisibles par 8, la présence des parois en bas et la conservation du plateau et de l'escalier sont vérifiées dans `verifications.json`.

## Ambiances

Jour et crépuscule sont des images fixes composites ; elles utilisent des nuages PMU et ne sont pas des captures moteur. Le crépuscule utilise une teinte d'aperçu. La nuit est une simulation animée 120 phases : mer V24P01A, 10 étoiles, nuages PMD complets répétés par wrap. Le pixel de la phase théorique 120 égale celui de la phase 0 avant encodage ; la période APNG est 16 secondes. La bande de mer basse est répétée. L'identité exacte entre V24P01A et la mer de Sharpedo n'est pas établie.

## Limites

Ces PNG sont des compositions de travail, pas une carte Ground finalisée ni des tilesets validés. L'échelle d'import ciblée reste 8 px. Aucun test en jeu, aucun contrôle de collision et aucun test de la jonction entre les deux cartes n'a été effectué. Aucune modification des cartes ou sauvegardes, aucun push. La qualité artistique des raccords doit encore être vérifiée au zoom natif et dans l'éditeur PMDO.
