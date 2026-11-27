# Travaux expérimentaux Destiny — sauvegarde de session

Ces fichiers sont publiés comme **prototypes, sources, audits et captures**, pas comme une intégration jouable dans le jeu. Les répertoires de travail sont placés sous `experiments/travaux-arena/` afin de ne pas modifier les fichiers actifs du projet.

- `Capacites-Z/` : inventaires, prototypes des capacités Z, sources et galerie vidéo. Les nouvelles fins V2 sont à valider.
- `Capacites-de-base/` : Lame en Peine V6 charge calibrée et Canon Blindé V2 corrigée validées visuellement, Spatio-Rift et essais précédents. La validation visuelle ne signifie pas intégration ni validation exhaustive des mécaniques.
- `Mega-Evolution-in-game/`, `Mise-a-jour-Guilde/` : travaux et bancs associés.
- Autres dossiers de projet : travaux de guilde, audit Méga-Tsareena et autres expérimentations conservés à titre d'archive.

Les exemples de banc modifient temporairement une **copie isolée** du jeu puis la restaurent. Certains prototypes Z suspendent temporairement des talents, solution dangereuse à ne pas intégrer en l'état ; catégories de dégâts, immunités, interruptions, restrictions et menus demandent encore un travail spécifique. Lire les fichiers `ETAT*.md` et les journaux avant utilisation.

Les scripts de banc et le catalogue de la galerie contiennent des chemins de la machine de test `/home/user` et des dépendances locales. Ils sont fournis comme sources de travail à adapter, pas comme un installateur portable. La galerie enregistrée nécessite un serveur et une reconstruction de son catalogue. Les vidéos de captures et anciennes versions sont conservées pour comparaison ; aucune donnée de sauvegarde de joueur, aucun jeton, lien système, dépôt `.git` ou cache de dépendance n'est inclus.
