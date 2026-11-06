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
