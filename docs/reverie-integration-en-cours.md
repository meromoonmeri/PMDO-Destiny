# Réverie — intégration en cours, branche de travail

Cette branche contient de vraies modifications aux fichiers du jeu, mais **elle ne constitue pas la mise à jour complète demandée** et ne doit pas être présentée comme une release jouable finale.

## Intégré sur la branche

- Salle carrefour du lot Ledian reconstruite comme carte `dojo_kingambit`, avec le Kingambit et ses dialogues existants ; passages nord, est et ouest non raccordés.
- Tapis et bande noire supprimés devant le grand dojo sur les cartes de jeu et d'édition, avec 48 variantes de tuiles ajoutées dans la banque existante. Les autres tuiles et l'extérieur sont conservés.
- Trois cartes café de la sauvegarde town02 et dix banques isolées, sans écraser les banques originales. Les scripts Destiny du café conservent leurs textes et utilisent des identifiants locaux compatibles Lua 5.4.
- Deux accès erronés Arcanine et maison d'équipe retirés ; seuils confirmés repositionnés et auberge nord associée à `reverie_inn`. Le café revient à sa façade ; les retours et collisions doivent encore être testés en jeu.
- Hutte aquatique sud ajoutée comme carte distincte, porte d’accès et retour prévus ; animation native quatre phases de la fontaine selon la référence fournie. Les collisions sont reconstituées et les interactions restent à tester en jeu. Source visuelle : image fournie, identifiée comme rip de Pokémon Mystery Dungeon Red Rescue Team ; droits de redistribution à confirmer.
- Les scripts de la carte jeu et de la carte développeur restent identiques. L'index est dérivé globalement par le processus de build, et non remplacé par un index limité aux nouvelles banques.

## Vérifications connues et limites

Les 18 400 références de tuiles des quatre intérieurs ont été retrouvées dans les banques. PMDO 0.8.12 a désérialisé les trois cartes café, le dojo et la ville sur une copie, sans rendu GPU ou contrôle de gameplay. Les scripts ont été compilés avec Lua 5.4. Une recompilation de la carte d'édition a donné une carte de jeu identique octet pour octet. Les tests ne valident ni les interactions ni les sauvegardes.

Le test statique des collisions montre deux composantes : le poste et l'auberge ne sont pas reliés par le sol au centre dans la carte actuelle. Les escaliers et le découpage doivent être raccordés, sans prétendre que c'est déjà fait.

## À terminer avant release complète

Les quatre zones séparées et leurs passages ; migration et essais des sauvegardes ; validation en jeu de la hutte aquatique animée ; tableaux quotidiens et gazette ; E2 et ses indications ; réseau souterrain et casino avec raccords confirmés ; suppression sûre des intérieurs de guilde ; vérification des retours, du scénario et des interactions en jeu. E1 et les sorties de carrefour non précisées ne doivent pas recevoir de destination inventée.

La version et les tags 0.4.11 et 0.4.12 précédents restent intacts. Sauvegarder les parties avant tout test.

La carte de hutte a été désérialisée par PMDO 0.8.12 et contrôlée statiquement, sans test visuel ni de franchissement ; sa première image est identique à la référence fournie.
