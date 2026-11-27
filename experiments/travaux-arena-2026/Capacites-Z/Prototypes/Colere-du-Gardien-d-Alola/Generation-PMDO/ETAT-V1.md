# Colère du Gardien d'Alola — V1 à valider

## Animation

Tokorico est entouré par des lances de lumière tombant successivement, puis une grande explosion blanche, dorée et rose. Le rendu emploie les particules natives de Clair de Lune, les sons natifs et deux banques de 60 poses (effets à l'arrière et à l'avant). Les poses sont lues trois images moteur chacune. La vidéo sonore `Tokorico-Colere-V1-lances-explosion-60ips-son.mp4` montre le banc en donjon, enregistrée à 60 images par seconde ; le moteur peut répéter des images s'il ralentit.

## Mécanique de banc et essais

La fiche Fée spéciale à une charge utilise l'événement natif `CutHPDamageEvent` avec `HPFraction=4`. Contrairement à une simple division des dégâts par quatre, son calcul natif retire les trois quarts des PV actuels, arrondis à l'inférieur, avec minimum 1. En copie isolée, onze actions ont été vérifiées :

- Huit directions : 270→68, 269→68, 101→26, 7→2, 4→1, 3→1, 2→1 et 100→25. Témoin et allié à 270 PV inchangés, une charge consommée chaque fois.
- Cible résistante Acier/Fée : 100→25, sans multiplier les dégâts fixes par la résistance.
- Garde Mystik sur la même cible : 100→100.
- Cible à 1 PV : 1→0, K.O. ; témoin et allié intacts.

Journal : `journal-v1-8-directions-pv-garde-mystik.txt`. La copie a été restaurée et les originaux comparés.

## Limites

Le banc vise un adversaire adjacent dans la direction du lanceur : c'est une adaptation expérimentale à PMDO. La grande explosion et les lances sont visuelles et ne signifient pas que les Pokémon autour sont des cibles. La Protection spéciale des capacités Z (dégâts réduits au quart), les autres protections, immunités provenant d'autres talents ou effets, Endure, substitution, boss, murs, bords et interruptions n'ont pas été testés. Le modèle d'événement natif n'établit pas à lui seul la bonne interaction avec toutes ces règles. Ni les restrictions aux quatre gardiens, ni Ire de la Nature, ni la Tokozélite, ni les menus Z ne sont intégrés. Pas de push effectué.

Sources du banc : `~/Capacites-Z/Sources/{preparer-colere-v1.py,colere-v1-effets.lua,test-colere-v1.lua,banc-colere-v1.py,intro-halo-banc-tokorico.lua}`. La maquette précédente reste disponible séparément et ne constitue pas une capture en jeu.
