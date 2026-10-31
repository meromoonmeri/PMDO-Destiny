# Source irisée : intégration et limites

## Origine et préservation

La Source retrouvée est celle de l'atelier de **meromoonmeri** : décor avec escalier et relief, bassin turquoise et colonne arc-en-ciel à couleurs fixes dont l'opacité pulse. Il s'agit de `spring_pulsation_v2`, et non des quatre premières variantes sans cet escalier. La composition de référence est le blob Git `0dcd026a1946f9c3aa72a00ab16c64e2db814ccf` ; le descriptif associé est `b9e61f01d0a771ba908a1cab118fb3cbac3b63a1`. Le travail part de ressources PMDO et de l'étude du projet de **Palika** ; la coloration et la pulsation d'atelier ne sont pas attribuées à Palika et ne sont pas prétendues natives. Les crédits et restrictions sont rappelés dans [CREDITS.md](../CREDITS.md).

La nouvelle carte `game/Data/Ground/destiny_source_irisee.rsground` est **individuelle**, dans l'unique Quest `destiny`. Elle ne remplace ni la clairière Destiny préexistante, ni la carte native de la base. Elle reprend la géométrie, les collisions, marqueurs et entités du socle PMDO `luminous_spring`, avec ses calques de terrain masqués ; le panneau et le coffre natifs sont désactivés sur cette adaptation pour ne pas recouvrir le décor de l'atelier. L'escalier et le bassin sont les images retrouvées, pas un redessin. Les 14 chaînes localisées de l'évolution native sont conservées pour ce nouveau Ground.

## Animation et reconstruction

Les trois PNG d'origine et les cycles d'eau à 3 et 13 phases se trouvent dans `art/source_irisee/`. `python tools/construire_source_irisee.py` (Python et Pillow) les convertit en cinq fonds natifs `.dir`. La colonne comporte **78 phases, 6,5 secondes à 60 Hz**, avec couleurs fixes et alpha pulsé ; l'eau conserve ses deux cycles indépendants. Les couleurs des atlas sont prémultipliées par l'alpha, comme lors de l'import PMDO, pour éviter la surexposition du faisceau. Avant conversion, la recomposition de la phase 39 est identique à la référence : SHA-256 des octets RGBA `d7279147d176f60a22399d3a8e3258a6f3982b1010d74807f01c081cbe9bf324`.

À l'approche de la Source, la caméra présente la colonne. L'option « Évoluer » délègue au rituel et aux conditions natifs ; le menu Méga et QI est partagé avec l'ancienne clairière. Une sortie au sud ramène à cette clairière ; son menu propose de rejoindre la Source irisée. Ces passages ont été testés dans les deux sens.

**Limite de parcours :** la liaison entre ces deux cartes est un accès technique provisoire, pas une nouvelle scène de l'histoire. Aucun accès à la clairière depuis le scénario principal n'a été confirmé ; l'ensemble n'est donc pas présenté comme accessible depuis une nouvelle partie sans intervention. Aucun raccord narratif arbitraire n'a été inventé.

## Évolutions et vérifications

Les fiches Quest et leur index activent Canarbello, Mygavolt et Carmadura. La branche Coiffeton → Canarbello au niveau 16 et Canarbello → Palmaval au niveau 36, ainsi que Statitik → Mygavolt au niveau 36, sont attestées par la ROM privée 2.3.28 fournie. Les deux branches de Charbambin, auparavant sans objet, utilisent les objets correspondant aux identifiants relevés dans cette ROM : Protecteur → Carmadura et Tissu Fauche → Malvalame. Ces objets et conditions ne sont pas présentés comme les mécanismes des jeux principaux.

Le sprite natif `913.chara` provient du sprite 1013 de la ROM fournie, converti par le moteur : 18 animations nommées et des noms neutres pour les animations non identifiées. Le portrait de base `913.portrait` a été conservé après comparaison : ses images normales correspondent aux deux portraits disponibles dans la ROM, chacun avec une seule expression ; les autres formes et skins de la base ne sont pas supprimés. Le Pokédex public indique `◥θ┴θ◤/N-A` pour Canarbello ; l'attribution exacte de cette paire reste à confirmer.

Essais réels sous PMDO 0.8.12, sur banc isolé construit avec la release Windows et lancé sous Linux : marche sur l'escalier, pulsation, menus, évolution de Coiffeton en Canarbello et sprite obtenu, Méga-Raichu X puis retour à la forme précédente, et passages aller-retour entre les deux cartes. Des assertions du moteur ont aussi vérifié les trois niveaux et les deux évolutions de Charbambin, avec refus sans objet. L'introduction, les 15 questions et l'accès à la liste libre de 11 pages ont été revérifiés après renommage. Captures et journaux : `audit/source_2_3_28/tests/source_irisee/`. Ces essais ne valident ni tous les starters, ni toutes les animations et sauvegardes, ni le scénario complet.
