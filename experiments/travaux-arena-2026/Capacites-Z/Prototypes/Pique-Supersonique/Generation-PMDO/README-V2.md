# Piqué Supersonique — V2 : plumes et rémanence

`Roucarnage-Pique-Supersonique-V2-plumes-remanence-son.mp4` montre le banc en jeu. La V1 reste archivée séparément.

Au décollage, le Pokémon s'élève avec l'animation native `CharAnimFly`. Des plumes issues de la banque native PMDO sont dispersées et des copies translucides du sprite du lanceur sont laissées derrière lui. La descente utilise `DashAction` en mode `DropDown` et l'émetteur natif `AfterImageEmitter` du moteur, puis un choc aérien. Le sillage et le choc sont recomposés à partir d'images IA. Les copies visibles au décollage sont de vraies images du sprite du porteur, mais emploient la pose 0 de son animation ; la rémanence de descente utilise l'émetteur natif.

Huit orientations : 8/8 cibles à deux cases touchées, 8/8 témoins latéraux intacts, PP 1 → 0. Voir `journal-v2-8-directions.txt`. Le placement et l'activation sont scriptés. Portée 3, puissance physique 90 et PP provisoires ; murs, alliés, autres distances et porteurs, interruptions et échecs non validés. Aérozélite, conversion de capacité, menu et règles Z non intégrés.

Fiche originale, événement, scripts temporaires, introduction et sauvegardes de la copie ont été restaurés ; banques V2 retirées de la copie. Sources : `Capacites-Z/Sources/preparer-pique-supersonique-v2.py`, `pique-supersonique-v2-decollage.lua`, `test-pique-supersonique-v2.lua` et `intro-halo-banc-roucarnage.lua`.
