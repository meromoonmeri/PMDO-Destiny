# Cliff — mise à jour 0.6.1

* Quatre vues Cliff nues ajoutées au dépôt : jour, aube, crépuscule et nuit (`art/cliff-nu/ambiances/`), 480×520 chacune.
* Deux variantes de falaise seule ajoutées comme sources de découpe : fond transparent et fond magenta (`art/cliff-nu/falaise-seule/`), 480×416.
* Empreintes SHA-256 et dimensions notées dans `art/cliff-nu/MANIFESTE.json` ; mode d’emploi dans `art/cliff-nu/LISEZ-MOI.md`.
* Aucun élément de décor n’est ajouté à ces vues : ni guilde, ni arbres, ni pont, ni bassin. L’artiste placera lui-même ces éléments et renverra les cartes terminées.
* Aucun fichier de `game/` n’est modifié par ce lot : les scènes de jeu, les collisions, les transitions et les sauvegardes restent celles de la 0.5.8.

## Limites à ne pas confondre avec du contenu jouable

* Les quatre images sont des **rendus aplatis fixes**, pas des cartes PMDO : il n’existe ni `Data/Ground/*.rsground`, ni `Content/Tile/*.tile`, ni `Zone`, ni objet, ni événement pour Cliff dans ce lot.
* La mer n’est pas animée dans ces images et les raccords nord-est déjà repérés ne sont pas corrigés.
* Rien n’a été testé dans le moteur, dans l’éditeur, en Windows réel ni dans une partie sauvegardée. Les contrôles de ce lot se limitent à la CI du dépôt et à la vérification des empreintes.
* La publication 0.6.1 sert à mettre ces ressources à disposition pour la suite des retouches ; elle ne signifie pas que Cliff est jouable ou raccordé à Réverie.
