# Patati-Patattrape — V3 abîme, prototype à valider

Vidéo sonore : `Mimiqui-Patati-V3-abysse-60ips-son.mp4`. Planche : `Patati-V3-abysse-120images.png` ; cases 128 × 128 pixels, 8 colonnes, fond transparent, lecture de gauche à droite puis de haut en bas à 60 images/s. Banque PMDO : `PatatiV3_Abysse.dir`. Les captures peuvent comporter des images répétées en cas de ralentissement du moteur.

Mimiqui bondit vers l'adversaire ; un abîme noir et mauve s'ouvre au contact. Les deux sprites sont masqués pendant l'absorption. La cible réapparaît d'abord, puis Mimiqui ; la sortie de la cible est visuelle et n'annule pas les dégâts normaux. Dans ce banc, cette sortie est montrée à chaque lancement, sans probabilité distincte d'échappée. L'animation de 120 images comprend une ouverture, des ténèbres mouvantes et des particules natives, puis une fermeture.

## Chance de K.O.

Après un coup ayant effectivement réduit les PV et si la cible est encore en vie, un tirage entier de 0 à 999 est réalisé : seul 0 déclenche le K.O., soit 0,1 % par coup éligible. Les dégâts ordinaires sont calculés avant le K.O. éventuel : le K.O. se produit donc lors de la même attaque, mais techniquement après une première réduction de PV. Aucun tirage K.O. après un coup sans réduction de PV. Ce comportement est une personnalisation demandée, pas une règle officielle de la capacité.

## Tests en copie isolée

- Huit orientations, cible à deux cases : huit cibles touchées (270 → 243–245 PV), huit témoins indemnes, une charge consommée. Les huit tirages observés n'ont pas déclenché le K.O. Journal : `journal-v3-8-directions.txt`.
- Dans un deuxième banc distinct, le tirage a été forcé à zéro : cible 270 → 0, état K.O. vérifié, témoin intact et masquage temporaire retiré. Journal : `journal-v3-ko-force.txt`. Le tirage forcé ne figure pas dans la version ordinaire du script.
- Après chaque banc, les fichiers originaux de la copie ont été restaurés et comparés. La vidéo montre le banc ordinaire, pas le K.O. forcé.

## Limites importantes

Pour cet essai uniquement, le statut neutre existant `none` a été modifié dans la copie isolée pour masquer les sprites, puis restauré. Avant une intégration réelle, il faut un statut visuel dédié, correctement enregistré et nettoyé même en cas d'interruption ; cette V3 n'est pas une solution prête pour le jeu. La cible est masquée puis réaffichée : il n'y a pas de déplacement physique dans l'abîme. Aucun essai des alliés, obstacles, bords, cibles adjacentes, immunités, protection, boss, Talents ou autres moyens d'empêcher un K.O. Le K.O. forcé appelle directement les dégâts létaux et ses interactions avec ces protections ne sont pas garanties. Le comportement en cas d'interruption et les restrictions Mimiqui/Câlinerie/Mimiquizélite ne sont pas couverts. Pas de cristal, menu Z ni push.

Sources : `~/Capacites-Z/Sources/preparer-patati-v3.py`, `patati-v3-effets.lua`, `banc-patati-v3.py`, `test-patati-patattrape.lua` ; variante de test forcé `patati-v3-ko-force.lua`, `banc-patati-v3-ko-force.py` et `test-patati-v3-ko-force.lua`.
