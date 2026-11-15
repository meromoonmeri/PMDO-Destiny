# Cinématiques — cadre de dialogue et découpe des répliques

Audit du 15 novembre 2026, sur `wip/reverie-integration-kingambit-cafe`.

## La règle, mesurée dans le moteur

PMDO dessine en 320 × 240. `DialogueBox` fixe `MAX_LINES = 2`,
`TEXT_HEIGHT = 16`, `VERT_PAD = 2` et `SIDE_BUFFER = 8`. Le haut de la boîte
tombe donc à `240 − (16 + 16 × 2 + 2 × 2) = 188`. `SpeakerPortrait.DefaultLoc`
pose le portrait 56 px plus haut, soit Y = 132, ce que `cinematique.lua`
reprend avec ses deux ancres (8, 132) et (256, 132).

Deux conséquences, que `reveil_nuit` appliquait déjà et que les autres scènes
ne suivaient pas toujours :

- **Cadrage** : les pieds des acteurs doivent rester au-dessus de 188.
  Le repère du projet est Y écran ≤ 160, soit 28 px de marge.
- **Longueur** : la boîte tient deux lignes d'environ 48 caractères, soit
  **96 caractères par page**. Au-delà, le texte défile tout seul alors que
  les personnages ont fini de bouger : la scène paraît figée, et le joueur
  lit une page et demie pendant qu'un sprite attend.

Une réplique peut enchaîner plusieurs pages : dans les chaînes Lua, `\n`
marque une page. La contrainte porte donc sur **le plus long morceau**, pas
sur la réplique entière.

## Ce qui a été changé

Neuf pages dépassaient 96 caractères. Aucun mot n'a été réécrit : la coupe
tombe sur une ponctuation, et chaque page garde ses balises `[color=…]`
équilibrées.

| Scène | Réplique | Avant | Après |
| --- | --- | --- | --- |
| `dojo_kingambit` | accueil du dojo | 115 | 30 + 89 |
| `dojo_kingambit` | description des salles | 110 | 45 + 63 |
| `dojo_kingambit_arene` | inscription de l'octogone | 105 | 38 + 68 |
| `dojo_kingambit_reliques` | les trois préceptes | 125 | 38 + 85 |
| `dojo_kingambit_reliques` | rouleau d'archives | 124 | 40 + 81 |
| `dojo_kingambit_reliques` | stèle des contres | 101 | 56 + 45 |
| `dojo_kingambit_reliques` | gravures de partenariat | 101 | 57 + 44 |
| `reveil_nuit` | réveil dans les Bois Perdus | 107 | 83 + 24 |
| `reveil_nuit` | promesse du partenaire | 104 | 39 + 60 |

## Outil

`tools/audit_cinematiques.py` relit les 131 scripts de `game/Data/Script` et
signale :

- une page de plus de 96 caractères (défilement subi) ;
- une balise `[color=…]` non refermée dans la même réplique ;
- un placement de portrait hors des deux ancres connues.

Il sort en erreur s'il reste un problème, ce qui permet de le brancher sur la
suite de tests.

## Ce qui reste à faire en jeu

Le cadrage ne se vérifie complètement qu'à l'écran : l'outil contrôle la
longueur et les ancres, pas la position réelle des acteurs, qui dépend de la
caméra de chaque scène. `reveil_nuit` documente le calcul (pieds à 160 pour
une boîte à 188) ; les scènes de village posent leur caméra en dur et
mériteraient le même repère explicite.
