# Lame en Peine / Bitter Blade — V1 à valider

## Visuel
Malvalame s'entoure de feux follets sombres avant de frapper : trois entailles violettes et noires se succèdent, accompagnées de flammes spectrales. La profondeur est **suggérée par des sprites 2D en perspective et des superpositions**, pas par une géométrie 3D réelle. Les séquences de charge et d'impact comptent chacune 48 images ; des textures et sons natifs PMDO de Feu Follet et d'attaques spectrales les complètent.

La vidéo `Malvalame-Lame-en-Peine-V1-60ips-son.mp4` est une capture sonore du banc en donjon. Le fichier est encodé à 60 ips ; le nombre d'images de jeu distinctes par seconde n'a pas été mesuré. L'effet reste une proposition à valider visuellement.

## Règles expérimentales
La fiche PMDO d'origine est non publiée : elle contient une attaque Feu physique de puissance 90 mais aucun soin ni effet graphique défini. Le prototype conserve cette puissance, sa précision et sa portée, et ajoute les marqueurs de contact et de soin, ainsi que l'événement natif d'absorption avec un diviseur de 2. Cette modification de comportement est expérimentale, pas une intégration finale. Selon la description officielle, l'attaque restaure au lanceur la moitié des dégâts subis par la cible : [2](https://scarletviolet.pokemon.com/fr-be/pokemon/ceruledge/).

## Résultats du banc
Huit orientations : 8/8 cibles Leuphorie touchées, 8/8 témoins latéraux intacts, PP 10 → 9. Le second banc a laissé Malvalame à 1 PV pour éviter le plafonnement du soin. Exemple : cible 202 → 33 (169 dégâts) ; lanceur 1 → 85 (84 PV récupérés, soit la moitié arrondie à l'inférieur). Les huit soins non plafonnés correspondent à la formule du moteur ; voir `journal-v1-soin-non-plafonne.txt`. Le premier banc vérifiait aussi le plafonnement au maximum de PV.

Les fichiers et sauvegardes de la copie isolée ont été restaurés et comparés après chaque banc. La capacité reste non publiée et n'a pas été ajoutée à l'apprentissage de Malvalame dans le jeu distribué.

## À vérifier avant intégration
Talent Torche, immunités et résistances, Suintement, protection, K.O., dégâts faibles, saturation de vie, soin bloqué, alliés, murs, bords et interruptions. Les feux follets sont visuels : aucune brûlure n'a été ajoutée. Le push reste en attente d'un accès Git en écriture.
