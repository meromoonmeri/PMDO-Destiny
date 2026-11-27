# Trou Noir des Ombres — V2 centrée, zone 5 × 5 et murs

## Capture et comportement observé

`Absol-Trou-Noir-V2-5x5-murs-son.mp4` est une capture sonore PMDO dans une copie isolée. Un seul vortex apparaît au niveau d'Absol, s'étend autour de lui, tourne puis disparaît. Le voile plein écran est propre à la capacité. La banque contient 32 poses recomposées à partir de deux sources générées par IA, par redimensionnement, rotation et fondu ; ce ne sont pas 32 dessins indépendants. Le vortex radial a les mêmes images pour les huit directions.

Action expérimentale : `AreaAction` Full, rayon 2, donc zone maximale de 5 × 5 cases centrée sur le lanceur. Les tests placent trois ennemis dans la zone et un témoin à distance 3, dans chacune des huit orientations : 24/24 ennemis touchés, 8/8 témoins intacts et PP consommés. Les ennemis et le déclenchement ont été préparés par script, puis l'action et les dégâts sont exécutés par le moteur. Toutes les cases et toutes les configurations d'obstacles n'ont pas été testées.

La fiche appelle elle-même l'événement Lua `BATTLE_SCRIPT.TrouNoirV2_BriserMurs` : pendant l'apparition, il transforme les cases de terrain `GenWall` sans effet en `GenFloor` dans le carré 5 × 5. Les effets spéciaux, murs indestructibles et bordures ne sont pas supprimés. Sur le montage de test, deux murs intérieurs sont devenus du sol ; un mur extérieur et un mur indestructible sont restés intacts. La case intérieure devenue sol n'était plus bloquée et un ennemi derrière ce mur a été touché. La modification demeure sur l'étage pendant le test ; la persistance après sauvegarde/rechargement n'a pas été vérifiée. Voir `journal-v2-5x5-murs.txt`.

## Limites et intégration

Le code de destruction est intégré à la fiche expérimentale via un `BattleScriptEvent`, pas aux consignes du script de test ; mais il n'est installé que dans le banc et reste à intégrer proprement au projet. L'aire de PMDO utilise un flood-fill : des murs indestructibles peuvent bloquer sa propagation vers des cases isolées. La destruction ne concerne pas les murs spéciaux non identifiés par `GenWall`, l'eau, la lave, les objets ou les effets de case. Les alliés, autres tailles de carte, bords, sauvegarde/rechargement et interruptions pendant la coroutine restent à tester. La puissance, la catégorie, les règles de cristal et le menu Z ne sont pas finalisés.

Ressources de banc : `black_hole_eclipse-v2-test-only.json`, `Trou_Noir_5x5_V2.dir`, `Trou_Noir_Vide.dir`, ainsi que `Capacites-Z/Sources/trou-noir-v2-effet-terrain.lua`, `preparer-trou-noir-v2.py` et `test-trou-noir-v2.lua`. La fiche originale, les scripts et les sauvegardes de la copie isolée ont été restaurés après essai. La V1 et sa vidéo sont conservées.
