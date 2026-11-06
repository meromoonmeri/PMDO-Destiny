# Réverie — intégration en cours, branche de travail

Cette branche contient de vraies modifications aux fichiers du jeu, mais **elle ne constitue pas la mise à jour complète demandée** et ne doit pas être présentée comme une release jouable finale.

## Intégré sur la branche

- Salle carrefour du lot Ledian reconstruite comme carte `dojo_kingambit`, avec le Kingambit et ses dialogues existants ; passages nord, est et ouest non raccordés.
- Tapis et bande noire supprimés devant le grand dojo sur les cartes de jeu et d'édition, avec 48 variantes de tuiles ajoutées dans la banque existante. Les autres tuiles et l'extérieur sont conservés.
- Trois cartes café de la sauvegarde town02 et dix banques isolées, sans écraser les banques originales. Les scripts Destiny du café conservent leurs textes et utilisent des identifiants locaux compatibles Lua 5.4.
- Deux accès erronés Arcanine et maison d'équipe retirés ; seuils confirmés repositionnés et auberge nord associée à `reverie_inn`. Le café revient à sa façade ; les retours et collisions doivent encore être testés en jeu.
- Hutte aquatique sud ajoutée comme carte distincte, porte d’accès et retour prévus ; animation native quatre phases de la fontaine selon la référence fournie. Les collisions sont reconstituées et les interactions restent à tester en jeu. Source visuelle : image fournie, identifiée comme rip de Pokémon Mystery Dungeon Red Rescue Team ; droits de redistribution à confirmer.
- Sortie E2 avec menu natif des donjons débloqués, indicateurs d’histoire et de missions lorsque ces données existent, et parcours libre des Bois Perdus séparé des branches de scénario ; tests de logique avec doublures, sans validation en jeu.
- Les deux intérieurs de guilde et leurs banques dédiées sont retirés. Des espaces techniques vides gardent leurs indices et marqueurs historiques et redirigent les anciennes parties vers Réverie ; le chargement des sauvegardes réelles reste à tester. La banque Guild_First_Floor, partagée avec une autre carte, est conservée.
- Les deux tableaux repérés donnent accès aux missions et à la gazette. Un système autonome propose chaque jour la traversée des Bois Perdus s’ils sont débloqués, conserve la mission acceptée, enregistre le succès et attribue une récompense unique à la banque. L’indicateur de mission apparaît à E2. Tests de logique avec doublures, sans validation en jeu.
- Les scripts de la carte jeu et de la carte développeur restent identiques. L'index est dérivé globalement par le processus de build, et non remplacé par un index limité aux nouvelles banques.

## Vérifications connues et limites

Les 18 400 références de tuiles des quatre intérieurs ont été retrouvées dans les banques. PMDO 0.8.12 a désérialisé les trois cartes café, le dojo et la ville sur une copie, sans rendu GPU ou contrôle de gameplay. Les scripts ont été compilés avec Lua 5.4. Une recompilation de la carte d'édition a donné une carte de jeu identique octet pour octet. Les tests ne valident ni les interactions ni les sauvegardes.

Le test statique des collisions montre deux composantes : le poste et l'auberge ne sont pas reliés par le sol au centre dans la carte actuelle. Les escaliers et le découpage doivent être raccordés, sans prétendre que c'est déjà fait.

## À terminer avant release complète

Les quatre zones séparées et leurs passages ; migration et essais des sauvegardes ; validation en jeu de la hutte aquatique animée ; validation en jeu des tableaux quotidiens et de la gazette ; validation du menu E2 et de ses indications en jeu ; réseau souterrain et casino avec raccords confirmés ; essai de la récupération des anciennes sauvegardes ; vérification des retours, du scénario et des interactions en jeu. E1 et les sorties de carrefour non précisées ne doivent pas recevoir de destination inventée.

La version et les tags 0.4.11 et 0.4.12 précédents restent intacts. Sauvegarder les parties avant tout test.

La carte de hutte a été désérialisée par PMDO 0.8.12 et contrôlée statiquement, sans test visuel ni de franchissement ; sa première image est identique à la référence fournie.


## Découpage technique des quatre quartiers

La carte historique conserve son indice et la copie d’édition 37 calques reste inchangée. Quatre cartes de jeu sont ajoutées en fin de liste : centre, nord, résidentiel et étang. Elles gardent l’ensemble des onze calques graphiques, les coordonnées d’origine, les décors et leurs animations ; leurs obstacles limitent la marche au quartier, sans retirer aucun obstacle existant. Les cinq escaliers sont équipés de déclencheurs bidirectionnels ; chaque arrivée dispose d’une position distincte pour le héros et son partenaire. Le script de ville reste partagé et les retours d’intérieurs, d’exploration et de sauvegardes historiques sont réacheminés sans changer la narration. Une sauvegarde ancienne positionnée sur une frontière reste sur la carte historique pour éviter un déplacement forcé.

Les empreintes, les obstacles, les dix directions d’escalier et les arrivées sont vérifiés automatiquement ; les interactions Lua ont été exercées avec des doublures. PMDO 0.8.12 a également désérialisé séparément les quatre cartes et chargé leurs callbacks. Conformément à la décision de conserver le décor, aucun pont ni passage artificiel n’a été ajouté dans l’eau : la zone du poste et de l’auberge reste séparée de la place par la rivière dans le graphe de collisions d’origine. Ce découpage doit encore être confirmé en partie graphique et avec de vraies anciennes sauvegardes avant d’être considéré comme une intégration finale jouable.


## Correction : personnages et calques propres à chaque quartier

Le joueur a signalé que les personnages des quatre secteurs se retrouvaient dans des endroits improbables ou empilés. La cause identifiée était la duplication des 26 personnages sérialisés sur toutes les cartes, combinée à six personnages recréés par script dans chaque secteur. Ils sont maintenant répartis par emplacement d’origine, sans suppression : 17 PNJ sérialisés au centre, quatre au nord, cinq au résidentiel et aucun à l’étang ; les six personnages ajoutés par script n’apparaissent que dans leur secteur (21, cinq, six et zéro au total). Un nettoyage ciblé retire, à l’initialisation, les PNJ étrangers présents dans un état ancien et remet une première fois les habitants locaux à leur emplacement prévu. Le héros et son partenaire ne sont pas concernés. Deux positions de marcheurs sont décalées de quatre pixels et celle de Magnéton de douze pixels pour sortir des collisions.

Chaque quartier possède des données de calques indépendantes. Les éléments graphiques distants sont retirés, mais une marge de 1 408 pixels autour du secteur conserve les éléments vus de part et d’autre des frontières, y compris au zoom le plus éloigné du moteur PMDO 0.8.12 avec la résolution 320 × 240 du projet. Les onze calques et les animations dans cette zone de visibilité restent identiques à l’original ; les cinq escaliers, coordonnées et obstacles ne changent pas. La carte complète historique et sa carte d’édition à 37 calques restent disponibles.

La visite existante conserve l’arrivée, la place, les boutiques, le marché et les échanges narratifs de fin ; les trois déplacements de caméra vers le résidentiel, le nord et le grand bâtiment ont été retirés. Les tests vérifient tous les PNJ, les 11 calques, la continuité dans la marge, les cinq escaliers et des chargements simulés d’états anciens. Ces vérifications ne remplacent pas une partie graphique ou un essai avec d’anciennes sauvegardes réelles.


## Correction préparée : entrées au contact

Les huit seuils confirmés et l’entrée/sortie du café utilisent des capteurs au contact, directement devant les bâtiments, sans question ni modification des collisions. Chaque entrée garde son intérieur et un retour joueur/partenaire vérifié sur la grille. Les deux tentes conservent leur interaction historique, leurs destinations n’étant pas confirmées. Les intérieurs de guilde, Arcanine et la fausse maison d’équipe restent exclus. Le poste et l’auberge restent isolés de la place par les collisions de la rivière ; aucun pont ni passage n’a été créé. Les événements ont été raccordés sur des objets PMDO 0.8.12 natifs et testés avec services simulés ; les transitions graphiques et anciennes sauvegardes réelles restent à vérifier.

## Réponses des commerçants pendant la visite

Forgelina, Alakazam et Mordudor répondent brièvement depuis leurs comptoirs pendant la visite déjà existante. Les échanges précédents et les dialogues de conclusion sont conservés ; la scène est testée avec doublures et non dans une partie graphique. Les exports PNG des ressources sont des documents d’édition séparés, et ne remplacent pas les formats natifs du jeu.
