# Audit avant correction des chemins de Réverie

Base : branche Destiny 0.5.0, commit `a2db214dc89e675347f670f26594df92158fc9d9`. Dix cartes compressées et banques associées ont été récupérées depuis GitHub avec vérification des SHA Git, sauvegarde ZIP CRC vérifiée (`sauvegarde-avant-chemins-0.5.0.zip`, SHA-256 `6d65730d153836b459fc9304e0447d79f9407f58a9cd78fe6a6fb593f0f9f776`). La référence Metano/Halcyon est utilisée uniquement en comparaison, pas comme source graphique pour Réverie.

## Zones prioritaires

- C01 x168–213 y1563–1600 et C02 x145–178 y1265–1323 : raccords de sable rectangulaires ; retrouver la ou les séquences de tuiles en cause avant traitement.
- C03 x1058–1078 y2574–2602 : petite tache rectangulaire ; éviter la pierre décorative et examiner l'origine.
- C05 et C06 x78–120 / x678–720 y2927–2958 : extrémités de chemins coupées net au sud des ponts. Garder les extrémités à leur place, sans créer de liaison.
- C07 x1425–1494 y580–620 et C08 x1202–1240 y2020–2080 : raccords abrupts près d'escalier et étang ; ne pas modifier l'eau, l'escalier ou les collisions et ne pas inventer d'accès.
- C04, C09 et C10 sont de simples soupçons et ne doivent pas être modifiés sans preuve ; la détection automatique inclut des faux positifs.

## Méthode et risques

Comparer avec les bordures organiques de Metano en respectant la géographie et la palette existantes de Réverie. Construire les raccords depuis les textures de Réverie, en respectant leurs pixels et leur échelle native. Créer des tuiles dédiées, sans modifier une banque partagée ni affecter d'autres positions. Sur les 10 cartes utilisant la même géographie, modifier exclusivement les séquences de tuiles visées, sans modifier collisions, objets, dimensions, animations, scripts ni ordre des autres séquences ; pour les tuiles composites, ne pas écraser un objet ou une animation en surimpression. Refaire un rendu avant/après, tester les coordonnées et toutes les phases concernées, vérifier l'intégrité et les références, et garder un ensemble de restauration.

Cette correction est risquée pour les anciennes sauvegardes qui sérialisent une carte chargée ; les objets déjà en mémoire peuvent garder l'ancien graphisme jusqu'au rechargement. Une sauvegarde de partie à l'extérieur de la ville est recommandée avant essai. La comparaison Python et les tests de données ne remplacent pas l'éditeur PMDO ni une partie graphique. Aucune CI ni publication n'est possible sans accès en écriture confirmé.
