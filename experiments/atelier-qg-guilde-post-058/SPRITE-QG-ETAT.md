# QG de guilde — préparation visuelle, hors moteur

- Original fourni par l'utilisateur : `qg-reference-utilisateur.png`, conservé.
- `qg-sans-drapeaux-ni-torches.png` : retouche générative à partir de l'image fournie, drapeaux et torches retirés ; ce n'est pas une extraction native.
- `qg-fond-porte-ouverte-transparent.png` : bâtiment 224×224, entrée noire, fond magenta retiré. `qg-porte-fermee-transparent.png` : bâtiment avec porte fermée. L'image générée a été ramenée à cette taille pour la maquette ; ce n'est pas un sprite PMD natif certifié ni une validation artistique ou moteur.
- Porte séparée : `porte-00.png` à `porte-06.png`, cellules transparentes de 48×48 ; `porte-ouverture-spritesheet.png` aligne les 7 poses ; position dans l'image du bâtiment : (88,151). À la dernière pose les vantaux disparaissent et la base noire apparaît. `porte-cycle-ouverture-fermeture.png` présente l'aller-retour ; les poses intermédiaires sont des compressions horizontales, pas des dessins natifs.
- `apercu-guilde-jour.png` et `apercu-guilde-porte-ouverte.png` sont des montages 480×520 hors moteur. Le bâtiment placé dans ces images sert de repère visuel et n'est pas installé sur une carte jouable.

Les images séparées ne constituent pas un objet animé PMDO : l'interaction, le déclenchement, les collisions et les étapes de scène restent à implémenter et à tester. La guilde doit rester fermée pendant la première visite. Le raccord avec Réverie et une mise à jour 0.5.9 jouable ne sont pas encore disponibles.
