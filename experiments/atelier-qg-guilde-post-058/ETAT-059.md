# État — demande v0.5.9 jouable

**Aucune v0.5.9 publiée ni jeu modifié.** Les ressources inspectées proviennent de la branche `wip/reverie-integration-kingambit-cafe` au commit `58567e2909f50b360eabfcc2886ede34b95035b5`. La v0.5.8 reste la dernière version annoncée.

## Audit réalisé

- Source de la zone `town02_waterfallvillage`, index, script commun ville et cartes Réverie centre/nord exacts récupérés en copie et conservés dans `references/`. Les cartes centre/nord délèguent leur script à `WaterfallVillageCapital` ; les 23 cartes de la zone sont inchangées.
- Audit statique des collisions à partir des données compressées : les deux cases de retour 16 × 16 à (760,32) et (784,32) sont libres. Depuis (760,32), la position (800,1160) est atteignable par les obstacles statiques ; 12 227 positions de 16 × 16 sont atteignables au pas de 8 px, pour chaque carte analysée. C'est un parcours calculé, **pas** un essai en jeu ni une validation des entités dynamiques ou du partenaire.
- Attention : un personnage de 16 × 16 placé à (800,8) empiète sur des obstacles. Positionner les entrées/retours avec prudence et les vérifier dans le moteur.
- Le script historique d'essai nocturne n'est pas une intégration validée : il pointe toujours vers une carte ancienne nocturne, pas vers les quatre maquettes actuelles. Les indices source et installé ne doivent pas être remplacés l'un par l'autre sans fusion.

## Bloquants avant publication

1. Transformer les maquettes Cliff en véritable Ground PMDO à l'échelle voulue, avec collisions, ciel/mer/nuages et choix des ambiances, sans dégrader les accès ni les cinématiques existantes.
2. Retrouver ou redéfinir le QG : l'image autrefois sélectionnée a disparu de la sandbox ; les propositions suivantes n'ont pas été sélectionnées. Créer la porte séparée animée ouverte/fermée avec entrée noire.
3. Faire le raccord bidirectionnel depuis le grand escalier nord, conserver le héros et le partenaire, et tester en jeu l'aller, le retour, les sauvegardes et les scènes. Les essais historiques ont été interrompus par la pression mémoire lors du chargement de Réverie ; ils ne démontrent pas le trajet complet.
4. Vérifier le build Windows et sa CI, puis seulement pousser les changements effectivement intégrés et publier la version si les tests permettent de la présenter honnêtement comme jouable.

Les résultats d'audit sont dans `rapports/audit-statique-escalier.json` ; `auditer-escalier.py` les recalcule (Python `ijson` requis). Les sauvegardes et projets existants n'ont pas été modifiés.
