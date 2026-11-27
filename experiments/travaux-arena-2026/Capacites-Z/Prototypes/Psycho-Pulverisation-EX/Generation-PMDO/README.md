# Psycho-Pulvérisation EX — prototype de banc

`Gardevoir-Psycho-Pulverisation-EX-8-directions-son.mp4` montre l'animation expérimentale dans une copie isolée de PMDO/Destiny. Gardevoir est le lanceur du test ; la capacité Z est générique.

## Animation

Une aura de concentration apparaît derrière le lanceur. Des fragments psychiques roses et violets glissent sur l'ensemble de l'écran. Sur chaque cible, un cercle d'énergie grandit puis se contracte, avant d'éclater en rayons et en fragments. Le moteur traite les cibles successivement ; le voile global est uniquement visuel et n'inflige pas de dégâts hors zone.

L'anneau et l'éclat ont été générés par IA puis recomposés en 22 poses de concentration et 36 poses d'impact. L'animation officielle d'Ultra-Soleil et Ultra-Lune consultée sur Poképédia a inspiré les couleurs, la concentration et l'explosion ; cette adaptation PMDO ne reproduit ni le déplacement tridimensionnel, ni le changement de décor de la cinématique. Sons du moteur : `DUN_Confusion`, `DUN_Psybeam` et `DUN_Psycho_Boost`.

## Test et limites

Huit orientations en donjon, trois Tortank dans la zone et un témoin à distance 3 : 24/24 cibles ont subi des dégâts, 8/8 témoins sont restés intacts, PP 1 → 0. Placement et lancement sont scriptés, mais dégâts et PP passent par le moteur. Voir `journal-8-directions.txt`.

Banc seulement : zone Full rayon 2, avec propagation PMDO, puissance spéciale 85 et PP provisoires. Alliés, immunités, murs, interruptions, autres lanceurs et terrains ne sont pas vérifiés. La Psychézélite, la conversion depuis la capacité de base, le menu et les règles Z ne sont pas intégrés. Après capture, fiche originale, événement, script de banc, introduction et sauvegardes de la copie ont été restaurés ; banques temporaires retirées de la copie.

Sources : `Capacites-Z/Sources/preparer-psycho-pulverisation.py`, `psycho-ex-concentration.lua`, `test-psycho-pulverisation.lua` et `intro-halo-banc-gardevoir.lua`.
