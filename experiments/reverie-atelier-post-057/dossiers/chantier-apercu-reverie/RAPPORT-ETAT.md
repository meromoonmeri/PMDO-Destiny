# Réverie — aperçu deux sections et travail local

## Aperçu demandé avant modification de la carte

`apercu-reverie-deux-sections.png` présente à gauche la géographie publiée v0.5.7 et, à droite, une proposition de conservation de la ville en deux sections : nord/centre, puis un seul secteur sud réunissant les habitations, l'autel, l'étang et les ponts. La maison isolée au sud du cours d'eau est conservée ; la grande forêt plus au sud serait retirée, avec une limite indicative autour de y = 3000. Le trait bleu de transition est seulement un repère général, pas une découpe finale ; la séparation réelle devra respecter cascades, ponts, chemins et continuité visuelle. De même, la limite sud devra être ajustée pour ne pas couper d'arbres ou autres sprites. Aucun Ground, collision, évènement, sauvegarde ou géométrie n'a été modifié pour cette proposition.

La carte actuelle utilise plusieurs Grounds de quartiers, avec un découpage scripté : centre/nord fusionnés, résidentiel et étang encore séparés. Réunir étang et résidentiel implique de refaire les zones d'appartenance des PNJ, les capteurs de changement de quartier et les destinations des portes, puis de vérifier les anciennes sauvegardes : l'aperçu n'est pas une carte fonctionnelle et ne réalise pas encore cette fusion.

## Scène ACT

La scène locale est maintenant placée **après** la marche visible et le fondu de départ de Lyra, du héros et du partenaire. Les positions, orientations et états IA des trois membres de l'équipe ACT sont restaurés. Les variantes ville et Dev ont le même script. Tests sur doublures : ordre marche → fondu → dialogue ACT, interlocuteurs absents/cachés, retours, menu et sauvegarde des positions : PASS. Placement des sprites, rythme et rendu caméra n'ont pas été visionnés dans PMDO ; la surveillance et le rapport sont seulement évoqués, pas implémentés dans le donjon.

## Intérieurs, retours et musique — prototype local

Dans `travail/` :

- L'existant `suivi_interieurs.lua` est conservé : il crée le partenaire réel à proximité si nécessaire, réutilise un partenaire déjà présent et active son suivi. Il est utilisé par les intérieurs Réverie, le dojo Kingambit et les trois salles du café ; sur une carte entièrement bloquée ou si le partenaire manque dans l'équipe, il ne peut pas le créer.
- Les huit portes de maison/dojo installées côté ville et le café mémorisent les positions du héros et du partenaire quand elles sont proches, libres et hors du capteur de porte. Sinon, les points prévus devant le bâtiment servent de repli, afin d'éviter un retour directement dans le déclencheur. Le retour exact n'est donc **pas garanti** quand il serait dangereux ou quand les positions sont indisponibles.
- Les appels d'entrée/sortie des intérieurs Réverie, du dojo et des trois salles du café utilisent l'API `EnterGroundMap(..., true)` pour préserver la musique. Le code moteur v0.5.7 vérifié montre que `EnterZone` ne possède pas cet argument tandis que `EnterGroundMap` le transmet à `MoveToZone`/`MoveToGround`. Le retour final dans la ville ne relance pas la musique quand le drapeau de passage bâtiment est actif. Cette stratégie suppose que ces transitions sont exécutées dans la zone `town02_waterfallvillage` ; sa liste Ground vérifiée contient bien les lieux et les indices 0, 2, 3, 4 utilisés.
- Le correctif local précédent du café (incluant le chargeur moteur) est conservé dans le répertoire de travail, mais la piste du chargement des chemins accentués et l'écran noir restent non confirmés sous Windows. Pas de compilation C# effectuée.

`lancer-tests.py` exécute les tests de visite, huit entrées/retours, annulation, positions exactes et repli anti-porte, trois salles du café, réutilisation et absence du partenaire, cartes bloquées et maintien du drapeau musical sur des doublures, sur les scripts ville et Dev : PASS. Les doublures ne testent ni lecture audio, déplacement/collision dynamiques, entrées accessibles dans le vrai jeu, écran noir Windows, ni anciennes sauvegardes réelles. En particulier, la maison d'équipe sur la falaise est dans une autre zone et n'est pas validée par cette série.

## Sauvegardes et état

Les scripts et sources d'origine consultés sont conservés dans `originaux/` et sauvegardés dans `sauvegarde-avant-interieurs.zip` (le dojo et les deux fichiers ajoutés après cette archive restent dans `originaux/`). Les scripts de travail ont des empreintes dans `empreintes-travail.json`. Aucun push, CI, tag ou release : la version publique reste v0.5.7. Les contours des chemins, le café et le catalogue PMU demeurent des chantiers ouverts.
