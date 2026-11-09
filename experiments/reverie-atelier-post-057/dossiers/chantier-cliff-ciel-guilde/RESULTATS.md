# Ciel de la guilde et crépuscule EoS

## Jour

Le ciel de l'aperçu est reconstruit d'après les pixels et les alternances de la capture T00P04A de la guilde : la guilde et les montagnes masquent une partie de l'original, qui n'est donc pas disponible comme couche de ciel indépendante dans cette image. Les zones cachées ont été complétées à partir des couleurs dominantes par ligne et par parité ; la comparaison retrouve 59 864 pixels sur 60 057 pixels échantillonnés comme ciel dans la source. Le bleu, le dégradé tramé et le petit nuage blanc viennent de cette référence. Les cinq copies d'un nuage entier sont animées par translation cyclique dans la maquette ; ce mouvement n'est pas l'animation originale de T00P04A. Lorsqu'un nuage franchit un bord de l'écran, une partie est naturellement hors cadre et réapparaît de l'autre côté ; son sprite source est entier.

## Crépuscule

Recherche effectuée dans les 338 fonds de l'album des décors EoS (125 fonds V et T examinés sous forme de planches). Un authentique ciel de crépuscule EoS a été identifié : [V02P01A](https://projectpokemon.org/home/gallery/image/77462-v02p01apng/), dont les couleurs sont conservées et dont deux nuages entiers ont été extraits pour le wrap. La mer provient d'un autre vrai fond EoS, [V22P01A](https://projectpokemon.org/home/gallery/image/77513-v22p01apng/), prolongé sans répéter les écumes. L'eau crépusculaire est fixe dans cette maquette. L'ensemble est une adaptation de deux fonds canoniques, pas une preuve du ciel exact de la guilde au crépuscule. L'image de guilde [V01P08B](https://projectpokemon.org/home/gallery/image/77461-v01p08bpng/) montre également une ambiance crépusculaire en gros plan, mais ne fournit pas un ciel panoramique libre de structure. La teinte du terrain au crépuscule est provisoire.

## Nuit et tests

La nuit conserve le ciel, la lune et les étoiles de la zone Réveil de Destiny, ainsi que les nuages EoS mobiles et la mer calmée de l'aperçu précédent. Les trois APNG sont en 480 × 520 px, 120 phases à 133,33 ms ; pour chaque mode, l'image complète de la phase théorique 120 est identique à celle de la phase 0 avant encodage. Les sprites des nuages utilisés sont entourés de transparence. Le terrain de jour est identique au précédent après vérification binaire.

Ce sont des compositions hors moteur, non des Grounds ou captures PMDO ; ni carte, ni script, ni sauvegarde n'ont été modifiés. Le raccord Métano et les collisions ne sont pas validés en jeu. L'identification de la mer nocturne exacte de Sharpedo reste à confirmer. Les droits de redistribution des ressources PMD restent à vérifier. Sources, algorithme et preuves : `RAPPORT-PREALABLE.md`, `verifications-jour-crepuscule.json`, `verifications-nuit.json`, scripts du chantier.
