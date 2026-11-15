# Audit des étages de donjon — Passage Aquatique et Grotte Verdoyante

Audit du 15 novembre 2026, sur `wip/reverie-integration-kingambit-cafe`.

## Ce qui était demandé

Chaque étage doit mener à l'escalier et rester franchissable par **n'importe
quel Pokémon**, y compris un non-nageur, et les tables de rencontre doivent
réellement peupler les deux donjons.

## Méthode

Les données de zone ne décrivent pas des cartes : elles décrivent une
**chaîne de génération**. L'audit a donc lu les étapes de chaque étage et les
classes du moteur qui les exécutent, puis comparé ces réglages à ceux des
donjons livrés avec PMDO (`base/Data/Zone`).

Les trois propriétés vérifiées, et le code qui les porte :

| Propriété | Code de référence |
| --- | --- |
| L'eau bloque un Pokémon qui ne nage pas | `BaseMap.TerrainBlocked` : `(BlockType & mobility) == Passable`, avec `BlockType = Water (1)` et `mobility = Passable (0)` |
| Un escalier isolé doit faire échouer l'étage | `DetectIsolatedStairsStep`, qui inonde depuis l'entrée avec la mobilité `Passable` |
| L'absence de `TeamSizes` vide la rencontre | `PoolTeamSpawner.ChooseSpawns` : `if (!TeamSizes.CanPick) return chosenSpawns;` |

`base/Data/Terrain/water.json` porte bien `BlockType: 1`, et `BlockType`
`Water` vaut `1` dans `TerrainData.Mobility`. La chaîne est donc cohérente :
l'eau est infranchissable à pied sec, et le garde-fou teste exactement ça.

## Défauts trouvés

### 1. L'eau n'était posée que sur les goulots

`NoChokepointTerrainStencil.Test` se termine par :

```csharp
return this.Negate == Detection.DetectDisconnect(checkArea, IsMapValid, testLoc, Loc.One, IsBlobValid, true);
```

`DetectDisconnect` renvoie **vrai quand retirer la case coupe la zone**, donc
quand la case *est* un goulot. Avec `Negate: false`, la comparaison rend
`true` pour les cases qui ne sont **pas** des goulots : c'est le
comportement annoncé par le nom de la classe.

Les deux donjons portaient `"Negate": true`, ce qui inverse le test : le
stencil ne laissait plus passer que les goulots, et l'eau se posait donc
exactement sur les cases d'un tile de large dont le remplissage isole une
salle. C'est la cause directe du « des points d'eau qui permettent pas ».

Occurrences corrigées : 20 dans Passage Aquatique (10 `PerlinWaterStep` +
10 `BlobWaterStep`), 8 dans Grotte Verdoyante (les `BlobWaterStep`).

Les deux `PerlinWaterStep` d'herbes hautes (`lost_wood`, Grotte Verdoyante)
gardent `Negate: true` : l'herbe ne bloque pas le passage, seul son
placement est concerné.

### 2. Les flaques du Passage Aquatique ne se posaient jamais

`BlobWaterStep.Apply` calcule `startScale = GenerateScale.Max - 1` puis boucle
tant que `area >= GenerateScale.Min * GenerateScale.Min`. Avec
`GenerateScale 100..100`, l'aire de départ vaut `99² = 9801` et le seuil
`100² = 10000` : la boucle n'entrait jamais. Les dix étages demandaient
2 à 8 flaques et n'en posaient aucune.

Le même bloc visait `AreaScale 12..28`, soit des flaques de 144 à 784 tiles.
Le plus gros blob de tout PMDO vanilla est `2..9`, soit 81 tiles.

Correction : `GenerateScale 7..12` et `AreaScale 2..8`, exactement les valeurs
de `sleeping_caldera`, un donjon aquatique livré avec le jeu.

### 3. `TeamSizes` absent : aucun Pokémon

`TeamSpawnZoneStep` définit les tailles d'équipe rencontrées. La clé était
absente du JSON des deux donjons. Absente et non nulle : le constructeur
garde donc une liste vide, `ChooseSpawns` sort immédiatement, et aucun
Pokémon n'apparaît, quel que soit le contenu de `Spawns`.

Les 77 autres segments de zone du jeu (vanilla et Destiny) définissent tous
ce champ. Valeurs ajoutées, dans l'idiome des donjons voisins :

| Donjon | Étages | `TeamSizes` |
| --- | --- | --- |
| Passage Aquatique | 10 | `1 × r12 0..10` + `2 × r4 4..10` |
| Grotte Verdoyante | 8 | `1 × r12 0..8` + `2 × r3 5..8` |

Une équipe seule reste majoritaire (12 contre 4, puis 12 contre 3), et les
binômes n'apparaissent qu'en profondeur.

## Ce qui était déjà correct

Les tables de rencontre elles-mêmes sont saines et n'ont pas été touchées :

- **Passage Aquatique** : 26 espèces, 241 de poids total, niveaux 10 à 16
  montant avec la profondeur, faune cohérente (Krabby, Staryu, Tentacool,
  Chinchou, Carvanha, Frillish, Clauncher…).
- **Grotte Verdoyante** : 18 espèces, 173 de poids, niveaux 8 à 12,
  faune de caverne humide (Lotad, Zubat, Wooper, Morelull, Croagunk…),
  avec `MobSpawnWeak` et `MobSpawnMovesOff StartAt 2` comme le veut une
  première caverne.

Vérifié aussi : aucune espèce inconnue (1011 disponibles), aucune capacité ni
talent inconnu (883 capacités, 299 talents), et les `Range` tiennent dans le
nombre d'étages — `Max` est **exclusif** (`SpawnRangeList.GetSpawnList` teste
`Min <= level && level < Max`), donc `0..10` couvre bien les étages 0 à 9.

## Outils

- `tools/audit_donjons.py` vérifie les huit invariants ci-dessus sur les
  14 zones du jeu. Il signale 40 défauts sur l'état d'avant et zéro après.
- `tools/tests/test_correctifs_runtime_zones_et_debugger.py` valide les 2634
  expressions `$type` de l'ensemble des `Zone/*.json`, donjons inclus.

## Reste ouvert

`Zone.GetMap` réessaie cinq fois une génération qui échoue, puis **retombe sur
une carte vide de 10×10**. Une carte vide n'a ni entrée ni escalier. Ce
filet de sécurité est dans le moteur et n'a pas été modifié ; il reste la
seule façon dont un étage peut encore ne pas mener à son escalier.

## Addendum — le filet de sécurité du moteur ne peut plus être atteint

`Zone.GetMap` réessaie cinq fois une génération qui échoue, puis retombe sur
une carte vide de 10×10. Une carte vide n'a ni entrée ni escalier : c'était le
dernier moyen de rester coincé sur un étage.

Le seul générateur capable de lever l'exception dans ces deux donjons est
`DetectIsolatedStairsStep`, qui échoue quand un escalier n'est plus joignable à
pied sec. Trois propriétés du moteur rendent cette situation impossible
désormais :

1. `WaterStep.DrawBlob` teste `TerrainStencil` **case par case** avant de poser
   l'eau, flaques comprises. Le garde-fou n'est donc pas contourné par
   `BlobWaterStep`.
2. `NoChokepointTerrainStencil` refuse toute case dont le remplissage coupe la
   zone. Avec `Negate: false` — rétabli ici — l'eau ne peut plus occuper un
   goulot d'un tile de large.
3. `DetectIsolatedStairsStep` tourne après toutes les étapes de terrain sur les
   dix-huit étages des deux donjons, ce que vérifie la règle 2 de
   `tools/audit_donjons.py`.

L'audit couvre maintenant aussi le cas d'une eau posée sur le sol **sans**
garde-fou du tout (règle 4b) : une eau qui ne porte pas de
`NoChokepointTerrainStencil` peut couper la carte, alors qu'une eau posée sur
des murs est inoffensive, ces cases n'étant pas marchables. La règle se
déclenche sur vingt étages si l'on retire les gardes, et reste muette sur
l'état livré.

Le repli sur carte vide n'est donc plus un risque connu sur ces donjons. Il
reste, tel quel, dans `engine/`, que ce dépôt matérialise à un commit épinglé
dans `SOURCE_LOCK.json` : le modifier ferait diverger la copie du moteur, ce
que la structure du projet interdit.
