# Atelier Réverie — travaux après v0.5.7

Ce dossier contient des **travaux en cours**, des scripts, des comptes rendus et des images de travail. Il ne constitue pas une mise à jour installée du jeu : les fichiers ici ne remplacent aucun fichier dans `game/`. La dernière prérelease jouable publiée reste la v0.5.7. Aucun nouveau tag ni release n'est créé pour faire passer ces candidats pour une version complète.

## Falaise de la guilde

`cliff/` contient les vues animées jour, crépuscule et nuit, le rendu sur magenta et les six calques de la falaise, avec un rapport. Pour ouvrir l'aperçu, télécharger ce dossier et servir son contenu par HTTP, par exemple `python -m http.server 8801`, puis ouvrir la page `index.html` ; le rendu direct d'un fichier HTML sur GitHub ne lance pas la galerie. Les ambiances sont des compositions hors moteur, pas des Grounds PMDO, et leurs raccords doivent être vérifiés dans PMDO. Le QG n'est pas encore dessiné.

## Autres travaux

`dossiers/` rassemble les rapports, scripts et tests textuels récupérés dans les différents chantiers (raccords, bassin, chemins, Lost Wood, Cliff, intérieurs, PMU, café, etc.). Certains scripts dépendent de fichiers locaux, de données ou d'outils absents du dépôt et ne sont pas autonomes. Ils sont conservés comme traces de travail ; leur présence ne prouve pas que le résultat correspondant est intégré ni reconstituable sans retrouver ses dépendances.

`candidats-non-installes/` comprend les fichiers candidats Lost Wood et dojo qui étaient encore disponibles. Ce sont des copies de travail, non écrasées sur les données du jeu : leur installation est conditionnée aux vérifications nécessaires, notamment sur les sauvegardes et dans PMDO. D'autres candidats et entrées manquent de cet export ; il ne prétend pas inclure toute la prochaine mise à jour.

`RECAP-ETAT-ANTERIEUR.md` est un bilan historique établi avant ce push d'atelier. Ses mentions « non publié » désignent les changements non intégrés dans le jeu et son état antérieur ; elles ne signifient pas que ce dossier d'atelier est absent du dépôt.

## Limitations importantes

- Aucun changement dans les cartes, collisions, sauvegardes ou scènes n'est effectué par ce dépôt d'atelier.
- Les tests statiques et sur doublures mentionnés dans les rapports ne remplacent pas des tests en jeu, sous Windows ou avec une sauvegarde réelle.
- Les demandes ouvertes et les ressources non intégrées restent indiquées dans les rapports ; la mer nocturne précise de Sharpedo n'est pas identifiée avec certitude.
- Ne pas installer en bloc des fragments PMU comme s'il s'agissait d'objets complets. Vérifier les droits de redistribution de chaque ressource avant une diffusion jouable.
