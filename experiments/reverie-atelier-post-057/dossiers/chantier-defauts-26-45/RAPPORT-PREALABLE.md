# Rapport préalable — captures 26 à 45 et défauts similaires

Base distante relevée : branche `wip/reverie-integration-kingambit-cafe`, commit `97847f618dd16d99f9475e75b74242c247146631`, version publiée 0.5.5. Le guide fourni et les règles de travail ont été relus ; les anciens rapports de bordures, superpositions et berges restent des références, non des preuves que les nouvelles captures sont corrigées.

## Demande et méthode

Les vingt captures comportent des annotations : vert pour les contours, raccords pixelisés, éléments rognés et autres défauts visuels ; bleu pour l'eau ou les animations manquantes. Repérer chaque capture sur les cartes à son échelle réelle, recenser chaque marque, examiner les couches séparées et les phases d'eau, comparer aux textures natives Métano et aux ressources Réverie. Les captures peuvent provenir d'une version antérieure ; comparer avec le commit actuel avant toute correction.

Créer une sauvegarde vérifiée des dix cartes et des banques susceptibles d'être modifiées. Corriger les cas démontrés avec des motifs natifs complets et des transitions organiques, sans lisser, redimensionner ni altérer les pixels par interpolation. Préserver les dimensions, la géographie, les PNJ, les obstacles, les scripts et les animations existantes. Ne pas dessiner par-dessus des personnages, recouvrir arbitrairement des objets ou convertir des éléments fixes en animations sans vérifier les références et cadences.

## Risques

La même image peut montrer un objet opaque au-dessus d'un contour, un effet d'ombre mobile, une cascade ou une vague volontairement transparente. Les annotations ne précisent pas toujours quels pixels supprimer ni quelle animation originale manque : les marquer comme candidats si le diagnostic n'est pas assez certain. Les cartes de développement et de jeu utilisent le même visuel mais ne doivent pas être désynchronisées. Les tests de références et la comparaison image par image ne suffisent pas à garantir le rendu en jeu ou l'absence de tous les défauts similaires. Une nouvelle autorisation GitHub sera nécessaire pour une publication complète ; ne pas demander ni enregistrer de jeton dans la conversation.
