# Audit préalable — falaises, buissons et animations d'eau

Base : 0.5.0 `a2db214dc89e675347f670f26594df92158fc9d9`, sauvegarde `sauvegarde-avant-chemins-0.5.0.zip` vérifiée et correctif herbe/chemins reconstitué séparément. Aucun accès GitHub en écriture n'est disponible dans l'environnement ; aucun push n'est donc annoncé.

## Falaises et buissons

Le rendu officiel 1600 × 4000 présente des trous transparents ponctuels et des découpes au raccord de plusieurs falaises. Un balayage alpha a recensé 38 composantes courtes dont 36 près de falaise ; certaines touchent eau, limite de carte, végétation ou couches animées et ne peuvent être corrigées automatiquement sans contrôle des couches. Remplissage limité aux pixels réellement transparents, avec pixels de Réverie voisins et dans les cases statiques identiques sur les dix cartes. Aucun effacement d'ombre, d'objet ou de fleur. Un balayage de la touffe de sable identique a retrouvé trois candidats : un fragment déjà restauré, un buisson partiellement caché derrière un arbre (à garder), et une différence de fond non concluante.

## Cascade de Kecleon et écumes

La cascade derrière Kecleon, environ x584–647 et y816–847, est animée dans `River` par 4 images dont une répétée, cadence `FrameLength=10`. L'écume utilise des séquences de 6 images dont certaines vides ou répétées, généralement `FrameLength=60`, réparties sur plusieurs couches. Le moteur choisit la frame par division du temps total par `FrameTick.FrameToTick(FrameLength)` modulo le nombre de frames. Proposition : cascade Kecleon 10→6, écumes identifiées 60→20 ; ordre et nombre de frames inchangés, pas d'autres animations ciblées. Plus rapide ne signifie pas ajout d'images intermédiaires : l'animation n'a pas davantage de dessins. Les cadences seront contrôlées pour tous les fragments de chaque écume afin d'éviter des déphasages.

## Bassin sud — aperçu d'abord, selon le choix utilisateur

La cascade est vers x288–351 et y1888–2007 ; son écume vers x264–367 et y1984–2047 tombe sur l'herbe juste au-dessus de la maison-plante. Un bassin empiéterait sur un secteur occupé et potentiellement accessible. L'utilisateur a choisi expressément **un aperçu d'abord** : aucun bassin ni changement de collision ne sera intégré dans les fichiers jouables à cette étape. Préparer une visualisation et un contrôle statique d'accès ; ne pas déplacer ni supprimer la maison ou son entrée, arbres, buissons, personnages, chemin ou autres décors. Une insertion ultérieure exigera choix de géométrie et validation des collisions / accès en jeu.

Les audits d'images et de données ne prouvent pas que tous les défauts sont identifiés et ne remplacent ni l'éditeur ni une partie. Conserver les sauvegardes de parties avant essai et reconstruire l'index sur le dépôt complet.
