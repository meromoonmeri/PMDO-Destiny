# Sauvegarde partielle — atelier Cliff, hors jeu

Archive des fichiers de travail Cliff qui subsistaient dans la sandbox au moment de la sauvegarde. Elle ne constitue pas une mise à jour jouable et ne couvre pas l'ensemble des autres travaux locaux. Les animations APNG générées auparavant et la proposition de QG sélectionnée n'étaient plus présentes dans la sandbox au moment de cette sauvegarde ; l'animation de porte n'est pas encore créée. Voir `inventaire.json`.

Pour reconstituer l'archive :

```sh
cat cliff.zip.part-* > cliff.zip
sha256sum cliff.zip
unzip -t cliff.zip
```

SHA-256 attendu : `278d2f75c6ac3ddf8f5cb1b93b79d7144d4ae973e4fa9105ca7d8f426d41f066`.

Les PNG séparés sont les derniers raccords herbe–falaise disponibles. Il s'agit d'une adaptation de colonnes de pixels sans interpolation, non validée en jeu. Préserver les sauvegardes et les autres chantiers.
