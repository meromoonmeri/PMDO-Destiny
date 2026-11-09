# Lost Wood — forêt aux lucioles et ruines

Les sept étages conservent leurs leçons françaises, leurs rencontres, leurs événements particuliers et `Tiny Woods.ogg`. La génération utilise deux rives et une rivière : les passages de sol traversent l'eau, tandis que des galets décoratifs apparaissent sur l'eau près des berges. L'eau reste bloquée pour les déplacements ordinaires. Les sentiers sont sur une couche sous les personnages et ne changent pas les collisions.

Les six types de vestiges sont disposés avec un stencil natif évitant les étranglements. Leurs feuilles, inspirées de références et issues d'images originales générées pour cette version, ne sont pas des dessins officiels ; les six fragments PMDO et leurs collisions rectangulaires ont été créés pour ces dessins. Les sprites éditables sont dans `art/lost_wood_ruines`. Aucune carte ou feuille de ruines du projet étudié n'est livrée.

Le DTEF `art/dtef/LostWoodLucioles` vient de l'atelier Treehouse de l'utilisateur : 47 raccords, variantes et deux couches de douze phases. Les PNG sont conservés pour permettre l'édition ; les matériaux générés sur géométrie native ne sont pas présentés comme des sprites canoniques. Les ressources de tiers et la franchise restent soumises aux droits de leurs titulaires.

## Contrôles

- `python tools/tests/test_lost_wood_dtef.py` : DTEF, variantes et 1 080 cellules d'eau animée, y compris la prémultiplication alpha.
- `python tools/tests/test_lost_wood_raccords.py` : couverture des 47 configurations et mesure des bords. Pour cette matière, l'écart RGB moyen observé est de 9,38/255 ; les raccords ne sont pas tous pixel-identiques.
- `python tools/tests/test_lost_wood_refonte.py` : sept étages, six fragments, feuilles éditables, raccords des sentiers et index.
- Moteur PMDO 0.8.12 sous Linux/Xvfb : trois générations pour chacun des sept étages, puis une carte supplémentaire jouée. Les 22 sorties, les sols des sentiers et les berges de galets ont été contrôlés ; eau, lucioles et ruines ont été observées sans exception sur ces tirages.

Ces tests ne couvrent pas tous les tirages ni un parcours humain continu des sept étages et des dialogues. La vidéo a été enregistrée sans son ; la sélection de Tiny Woods est vérifiée dans les données, pas son écoute réelle. Windows n'a pas été exécuté pendant ces essais ; le banc utilise une installation aplatie et le chargement en couches Quest séparées reste à confirmer.
