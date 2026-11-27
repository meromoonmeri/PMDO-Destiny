# Déluge Causti-Toxique — prototype de banc

`Nidoking-Deluge-Causti-Toxique-8-directions-son.mp4` montre la capacité expérimentale dans une copie isolée de PMDO/Destiny. Nidoking est choisi pour l'essai ; cette capacité Z est générique et non réservée à ce Pokémon.

## Animation

Une pluie toxique violette traverse l'écran ; des gouttes concentrées tombent sur chaque cible, puis des éclaboussures et une nappe violette bouillonnante apparaissent autour d'elle. Les impacts sont recentrés sur les cibles ; ils sont exécutés successivement par le moteur. La pluie globale est purement visuelle et ne transforme pas le terrain, n'empoisonne pas et ne touche pas toutes les créatures affichées. Les trois gouttes par cible sont visuelles : il n'y a qu'un calcul de dégâts.

Les images de goutte et d'éclaboussure ont été générées par IA puis recomposées en 40 poses. La pluie est un overlay transparent animé. L'animation USUL consultée sur Poképédia a servi de repère pour la pluie et la nappe violettes ; ce n'est pas une reproduction exacte de sa cinématique. Sons moteur `DUN_Gastro_Acid` et `DUN_Sludge`.

## Test et limites

Huit orientations en donjon, trois Tortank dans la zone et un témoin hors zone, placés par script : 24/24 cibles ont subi des dégâts, 8/8 témoins sont restés intacts, PP 1 → 0. Les dégâts et PP passent par le moteur. Voir `journal-8-directions.txt`.

Banc seulement : rayon 2 avec propagation de l'AreaAction PMDO, puissance spéciale 85 et PP provisoires. Le placement et l'activation sont scriptés ; alliés, autres terrains, murs, immunités, interruptions et autres lanceurs ne sont pas validés. La Toxizélite, la conversion de puissance et de catégorie depuis la capacité d'origine, le menu et les règles Z ne sont pas intégrés. Fiche originale, script de banc, introduction et sauvegardes de la copie restaurés après la capture ; banques temporaires retirées de la copie.

Sources : `Capacites-Z/Sources/preparer-deluge-causti-toxique.py`, `test-deluge-causti-toxique.lua` et `intro-halo-banc-nidoking.lua`.
