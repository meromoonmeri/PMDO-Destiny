# Réverie — raccords Métano et ressources PMU

## Base et protection

Le candidat reprend les deux cartes locales après le déplacement des quatre arbres. Leur état d'entrée et leurs banques sont sauvegardés dans `sauvegarde/avant-raccords-cartes-et-banques.zip` (CRC vérifié). Les deux Ground originaux v0.5.7 ont été récupérés et leur Git blob contrôlé. La branche `wip/reverie-integration-kingambit-cafe` pointait encore sur `ee39156a24f350b67e81740478be8505f4ff1a05` lors de l'intervention. Aucun projet existant, sauvegarde utilisateur, dépôt ni release n'a été modifié.

## Chemins et falaises

- Capture 51, escalier nord-est : le chemin rejoint les deux côtés du pied de l'escalier et les bords sont repris avec des modules Métano, dans la reprise antérieure existante. 134 cellules de `Base`.
- Capture 27 : une saillie coupée du bord gauche est reprise par un module Métano natif. 13 cellules de `Base`. Les autres raccords de cette capture ne sont pas considérés comme corrigés.
- Les 147 retouches ajoutées aux deux cartes sont identiques, pixel par pixel, aux tuiles du candidat déjà audité `Reverie_Raccords_Arrondis_27_51_52_058.tile`. Avant ajout, les 11 couches des cellules concernées ont été comparées aux originaux de la v0.5.7. Les vérifications intégrales après retrait des seules 147 modifications confirment l'identité de toutes les autres données avec les cartes d'entrée : collisions, entités, animations et autres calques. Rendu indépendant contrôlé sur quatre phases pour les deux zones.
- Les arbres déplacés, leurs collisions ajustées, les retouches 53–55 et leurs deux banques sont conservés. Les 147 retouches sont une surcouche dans `Base`, pas une fusion des 11 calques.
- La rive de la capture 52 n'a pas été ajoutée ici : elle réclame une comparaison des quatre phases sur la carte candidate complète avant de l'intégrer. Les falaises et leurs courbes mauves ne sont **pas toutes corrigées** : l'examen de la vue globale n'établit pas une anomalie précise dans chaque couleur mauve. Une recherche de petits trous transparents entourés de roche sur la phase statique n'a rien signalé ; elle ne détecte pas les mauvaises courbes opaques et ne prouve pas que les raccords sont seamless. Les autres chemins, rives, bordures et ombres restent à inspecter.

Le PNG global est un rendu statique de la carte `reverie_etang` 1600 × 4000, première image des séquences ; ce n'est pas le jeu. La partie sud à retirer dans la maquette en deux sections est encore présente et le doyen Draco n'est pas installé.

## Ressources PMU — progrès et limites

`candidat-banques-et-15-objets-pmu.zip` : 40 banques .tile PMDO de la branche v0.5.7 retéléchargées et vérifiées SHA-256, les 5 objets statiques et 10 fleurs animées précédemment préparés, leurs PNG source et la carte de démonstration séparée des fleurs. Les 15 .dir avaient été comparés intégralement à leurs PNG après prémultiplication alpha. Les 40 banques étaient déjà dans le dépôt ; les 15 objets et la carte fleurs ne sont pas publiés. 32 pixels PMU correspondent à 4 × 4 tuiles PMDO de 8 pixels, sans preuve d'échelle visuelle adaptée pour tous les objets. Un index PMDO approprié et des tests sont nécessaires avant installation sur une copie.

`fragments-animes-pmu-4058-non-assembles.zip` : pour les 4 058 paires historiques aux références valides, fichiers `.dir` de deux trames 32 × 32 créés et relus pixel par pixel ; les 22 paires avec référence invalide sont documentées, pas inventées. La cadence de 250 ms vient du client historique et reste indicative au placement. Ces fichiers sont **des fragments de cases**, pas 4 058 objets, cascades ou écumes complets ; ils sont volontairement hors `game/Content/Object` et ne doivent pas être installés en bloc comme une bibliothèque d'objets finis. L'intégration exhaustive des objets multicases et de leurs animations reste à réaliser. Aucun personnage PMU n'est intégré ici.

Les deux archives ont été vérifiées CRC. Aucune des cartes, banques supplémentaires ou animations n'a été installée, publiée ou validée dans PMDO 0.8.12, l'éditeur Windows, une sauvegarde réelle ou une CI. Ne pas présenter ce travail comme une intégration exhaustive ou comme un raccord global garanti sans couture.
