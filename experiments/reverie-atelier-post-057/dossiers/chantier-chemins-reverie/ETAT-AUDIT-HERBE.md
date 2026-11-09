# Réverie — audit et corrections des raccords verts

## Base et conservation

La copie est construite sur la 0.5.0, commit `a2db214dc89e675347f670f26594df92158fc9d9`, et inclut les corrections de chemins et de sable du précédent essai. La carte et les banques de Metano ont été consultées comme référence de raccords ; les pixels ajoutés sont issus de Réverie. La sauvegarde de départ est `sauvegarde-avant-chemins-0.5.0.zip`.

## Correctifs d'herbe ajoutés

- x160–167, y496–511 : retirer deux fragments de terrain orange isolés, avec l'herbe réellement située sous ces fragments.
- x400–415, y2552–2559 : retirer une bordure rose tronquée au milieu du pré ; restauration de la première tuile d'herbe sous-jacente.
- x371, y301–351 : atténuer un long trait vertical ; la fleur animée dans la case plus au sud reste hors retouche. Le bout voisin peut rester visible.
- x1189–1206, y2256 : atténuer un trait horizontal dans l'herbe sous un arbre ; ombre et tronc sont conservés.
- x1008–1023, y2303 et x1008–1015, y2304–2311 : retirer une ligne foncée et de petites traces roses isolées, avec des tuiles d'herbe Réverie.

La planche `avant-apres-herbe-et-chemins.png` montre ces endroits et deux exemples des précédents correctifs. Le correctif unique remplace les archives précédentes : ne pas les empiler.

## Contrôles et limites

- 50 cases locales et 34 tuiles nouvelles pour l'ensemble des corrections (herbe + chemins + sable) ; 1 887 pixels modifiés en rendu statique, par carte. Aucun script, objet, collision ou séquence d'animation existante n'est modifié.
- Pour chacune des dix cartes, composition identique à la référence dans les cases modifiées, aucun multi-frame dans ces cases, pas de pixels recouverts par une couche supérieure à la retouche ; vérification des tuiles natives et CRC ZIP. Ceci n'est ni une partie, ni l'éditeur, ni un test de sauvegarde réelle.
- Balayage automatique de 5 134 candidats verts, regroupés en 861 zones, et détection complémentaire de 76 composantes aux couleurs chaudes et 9 traits verts. Beaucoup correspondent à la trame répétée de l'herbe, des motifs de sol ou des objets. Des planches ont été inspectées ; ce recensement ne permet pas d'affirmer que chaque défaut sur l'ensemble de la carte a été trouvé. Ne pas effacer aveuglément les candidats restants.
- Les transitions C02/C07/C08 et des extrémités proches de décors ou d'animations nécessitent toujours une vérification complémentaire. Des différences entre herbe claire et foncée peuvent être volontaires.

Aucun test en jeu, CI ou push n'a été effectué à ce stade. La publication requiert une autorisation GitHub en écriture. Avant installation suivre le LISEZ-MOI de l'archive et régénérer l'index dans le checkout complet, pas dans le sous-ensemble de l'audit.
