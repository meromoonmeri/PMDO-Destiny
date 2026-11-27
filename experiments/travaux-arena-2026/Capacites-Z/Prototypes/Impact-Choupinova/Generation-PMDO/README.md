# Impact Choupinova — prototype en banc

`Nymphali-Impact-Choupinova-8-directions-son.mp4` montre la séquence enregistrée dans une copie isolée de PMDO/Destiny. Impact Choupinova est une capacité générique : Nymphali est le lanceur de ce test, pas un porteur exclusif.

## Chorégraphie

Nymphali effectue un tour complet sur lui-même : le script fait défiler les huit orientations du personnage, puis rétablit l'orientation de départ. Une couronne féerique rose et lilas apparaît pendant le tour. Ensuite, trois cœurs étoilés tombent successivement sur chaque cible touchée et produisent des explosions roses et des étincelles. Les cibles sont traitées successivement par le moteur ; ce n'est pas une pluie simultanée plein écran.

Les sources de couronne, cœur étoilé et explosion ont été générées par IA. Les 24 poses de l'aura et les 38 poses de chute/explosion sont recomposées par déplacement, redimensionnement, fondu et particules ; ce ne sont pas des dessins indépendants pour chaque pose. Le visuel aura/pluie est identique dans les huit directions ; la rotation utilise les huit vues natives du lanceur. Les trois chutes par cible sont visuelles : un seul calcul de dégâts par cible.

## Test

Banc en terrain aménagé, trois Tortank et un témoin à distance 3, placement et activation scriptés. Huit orientations : 24/24 cibles ont subi des dégâts, 8/8 témoins sont restés intacts, les PP passent de 1 à 0 et la direction initiale est restaurée à chaque tour. Les dégâts et la consommation de PP passent par le moteur. Voir `journal-8-directions.txt`.

La zone d'essai utilise `AreaAction` Full rayon 2, avec propagation PMDO ; les murs, alliés, autres lanceurs et cibles, effets de terrain et interruptions ne sont pas vérifiés. Puissance 85 physique provisoire : les règles Z, conversion depuis une capacité, cristal, menu et limite d'utilisation ne sont pas intégrés. Fiche et événement test-only ; fiche d'origine, scripts de banc et sauvegardes restaurés après l'enregistrement.

Sources : `Capacites-Z/Sources/preparer-impact-choupinova.py`, `impact-choupinova-rotation.lua` et `test-impact-choupinova.lua`.
