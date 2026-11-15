# Audit — Grotte Verdoyante (donjon 9 étages)

Audit du 2026-11-13 sur `wip/reverie-integration-kingambit-cafe` (HEAD `6d5a975`),
dans la continuité de la mise en ligne 0.7.0.

## Périmètre

| Élément | Fichier |
| --- | --- |
| Zone (segments 0/1, échecs, retours) | `game/Data/Script/destiny/zone/grotte_verdoyante/init.lua` |
| Entrée cascade / statue / Lyra | `game/Data/Script/destiny/ground/ewc3_entree_waterfall_cave/init.lua` |
| Vasques 9F (avant/après combat) | `game/Data/Script/destiny/ground/fgv1_fin_grotte_vasques/init.lua` |
| Données | `game/Data/Zone/grotte_verdoyante.json`, `game/Data/Ground/{ewc3_entree_waterfall_cave,fgv1_fin_grotte_vasques}.rsground`, `game/Data/Map/end_grotte_verdoyante.rsmap` |
| Dépendances | `destiny/{equipe_scene,cinematique,missions_reverie}.lua`, `destiny/services/statue_kangourex` |
| Moteur de référence | `engine/RogueEssence` et `engine/PMDC` (lecture seule) |

Méthode : lecture des scripts et des données, vérification de chaque appel Lua
contre les bindings C# (`Lua/*.cs`), contrôle des contrats moteur
(`GroundChar.Collide`, `GroundObject.Tags`, `GroundMap.GetEntryPoint`,
`GameProgress.EndGame`, `DungeonScene.ProcessInput`, `ScriptServices.Publish`),
BFS 16 px sur les grilles `obstacles`, comparaison des objets de carte avec
leurs replis Lua, puis exécution des suites `tools/tests/test_*.py`.

## Bugs confirmés et corrigés

### 1. Menus empilés sur les deux déclencheurs de contact d'`ewc3`

`SeuilDonjon` (`368,184,40,24`) et `SortieRetourReverie` (`320,568,144,8`) sont
des objets `Touch` **passables**. Côté moteur, `GroundObject.Tags` renvoie `3`
(passable) et `GroundChar.Collide()` rappelle `Interact()` **à chaque pas**
effectué dans le collider, sans déduplication — `TouchOnce` fait l'inverse et
ignore le premier contact, il n'est donc pas un remplacement acceptable.
Les deux gestionnaires n'affichaient le verrou `sortie_en_cours` qu'**après**
la confirmation du joueur : marcher dans les trois cases du seuil, ou maintenir
la direction après un « Non », ouvrait plusieurs menus d'affilée.

Correctif : verrou posé **avant** le menu, relâché après 18 frames si le joueur
refuse (le temps de quitter la zone de contact).

### 2. Lyra fantôme devant la cascade après le sauvetage

`GROUND:CreateCharacterFromCharData()` appelle `GroundMap.AddMapChar()` : les
personnages créés par script sont **persistants** et enregistrés dans la carte
de la sauvegarde. `ewc3.Init` ne créait `Luxray_Ewc3` que si
`AlerteShinx == 'a_secourir'`, mais ne la retirait jamais quand le drapeau
passait à `'termine'` : après la mission, Lyra restait plantée à `(400,260)`
et son action continuait d'annoncer « Le passage est grand ouvert. Entrons vite
chercher Nilo ! ».

Correctif : `Init` réutilise la Lyra existante pendant le sauvetage (plus de
repositionnement inutile à chaque visite) et la retire sinon.

### 3. `ExplorationReverie` non relâché après un échec

`SeuilDonjon_Touch` pose `SV.Destiny.ExplorationReverie = true` au départ de la
ville ; `lost_wood.ExitSegment` lit ce drapeau pour choisir sa branche « visite
libre » (retour direct en ville, sans scène d'histoire). La branche d'échec de
`grotte_verdoyante.ExitSegment` ne le nettoyait pas : après un K.-O. devant la
cascade, le drapeau restait posé alors que le joueur n'était plus en exploration.

Correctif : `ExplorationReverie = nil` dans la branche d'échec.
Les branches `Cleared` sont inchangées : la run continue vers les vasques.

### 4. Statue Kangourex muette (stockage inaccessible)

`ewc3.Statue_Kangourex_Action` commençait par `if SV.Destiny.StatueKangourexExpliquee
then return end`. Or ce drapeau est posé dès la cinématique d'arrivée : toute
interaction ultérieure sortait donc immédiatement, sans rien faire, en comptant
sur l'enveloppe du service `StatueKangourex` pour ouvrir le stockage. Si cette
enveloppe n'était pas installée (service non chargé, exception dans
`OnGroundMapInit`, carte rechargée sans passage par `GroundMapInit`), la statue
devenait totalement inerte : ni dépôt, ni retrait.

Correctif : l'action ouvre désormais elle-même le stockage de l'équipe
(`destiny.statue_kangourex.OuvrirStockage()` → `COMMON.ShowTeamStorageMenu`,
soit Entreposer / Prendre / Tout entreposer / Argent) après l'explication
éventuelle ; le service ne fait plus qu'ajouter le même comportement aux statues
sans script. Un drapeau partagé (`deja_ouvert`) empêche la double ouverture quand
les deux chemins se superposent.

### 5. Vasques muettes après le chargement d'une sauvegarde

`fgv1_fin_grotte_vasques` a `Music = ''` (contrairement à `ewc3`, qui déclare
`Lower Spring Cave.ogg`). Le moteur ne lance donc aucune piste à l'entrée, et
`fgv1.GameLoad` ne faisait que `GAME:FadeIn(20)` : une sauvegarde chargée pendant
une scène des vasques restait silencieuse jusqu'à la fin du donjon.

Correctif : `GameLoad` relance `Lower Spring Cave.ogg`, l'ambiance déclarée par
la carte d'entrée du même donjon.

### 6. Lyra « encore sonnée » après un retour en ville

`SV.Destiny.GrotteVerdoyanteDernierKO` n'était effacé qu'en reprenant le donjon
(`SeuilDonjon_Touch`). Après un K.-O., un aller-retour à Réverie Town laissait le
drapeau posé : de retour devant la cascade, Lyra récitait encore « Ne forcez pas
si vous êtes encore sonnés ».

Correctif : `SortieRetourReverie_Touch` efface le drapeau (le duo rentre se
reposer) ; la réplique de réveil ne vaut plus que sur place.

## Points audités et **écartés** (ne pas « corriger »)

Ces suspicions ont été levées avec preuve moteur ; les traiter comme des bugs
casserait des comportements corrects.

- **`GAME:EnterZone()` sans `EndDungeonDay` après le segment 0 (et après une
  victoire au 9F)** : c'est le motif canonique de PMDO pour un palier hors
  donjon (`origin/zone/ambush_forest`, `secret_garden`,
  `treacherous_mountain`). La session reste ouverte, `COMMON.BossTransition`
  puis `GAME:ContinueDungeon('grotte_verdoyante', 1, 0, 0)` reprennent le run ;
  `EndGame` n'est appelé qu'à la fin (PostBattle / EmptyReturn).
- **`GrotteVerdoyantePhase = 1` en fin de `PreBattle` *et* sur échec segment 1** :
  la machine d'état est cohérente. `1` = combat de boss engagé (donc revanche
  abrégée au retour), `3` = victoire en attente de scène, `4` (+ `BossVaincu`) =
  visite libre. Un échec au 9F garde `1`, une victoire force `3` : aucun
  scénario ne produit de « revanche fantôme ».
- **`missions_reverie.Completer('grotte_verdoyante', false)` sur échec** :
  `Completer` exige `reussi` (`if ... and reussi then`), l'appel est un no-op.
  Aucune mission n'est validée par un échec, même en visite libre.
- **`GROUND:MoveToPosition(hero, 432, 250, ...)` devant la statue** :
  `_MoveToPosition` n'a **aucun pathfinding** (`AnimateToPositionGroundAction`,
  interpolation linéaire), et `(432,250)` est hors du collider de la statue
  (`428,236,24,12`) : le héros ne se superpose pas au décor. Un BFS « case
  bloquée » n'y prouve rien (seule la rangée `y ≥ 264` est solide).
- **`CharSetAnim('Hop'/'Wake')` sans `CharEndAnim`** : tous les cas du donjon
  sont clos (`Nilo` dans `PostBattle`, `Wake` dans `PreBattle`, `Wake` du duo
  dans `cinematique_retour_echec`). `Carchacrok_Boss` est retiré avant la fin de
  son animation, ce qui est sans effet.
- **Émotions et emotes** : les 11 émotions de portrait utilisées appartiennent
  aux 20 de `base/Base/GFXParams.xml` ; les emotes de sol (`exclaim`, `notice`,
  `question`, `sweatdrop`, `sweating`, `shock`, `happy`, `glowing`) existent
  toutes dans `base/Data/Emote/`.
- **API Lua** : 12 `GROUND:`, 13 `GAME:`, 9 `UI:`, plus `COMMON.*`,
  `cinematique.*`, `equipe_scene.*`, `missions_reverie.*` — toutes définies.
  Signatures vérifiées : `MoveCamera(x,y,duration,toPlayer)`,
  `MoveToPosition(chara,x,y,run,speed)`,
  `CreateCharacterFromCharData(nom,data,x,y,dir)`,
  `EnterDungeon(zone,seg,map,entry,stakes,recorded,noRestrict)`,
  `SetSpeaker(nom,keysound,specie,form,skin,gender)`.
- **Marqueurs de carte** : `Entities[0].Markers` sont des `GroundMarker`
  (types `Marker`), jamais insérés dans la grille de collision ; l'index 0 vaut
  `entrance` sur les deux cartes (`ewc3` 392,544 ; `fgv1` 240,344), donc
  `EndDungeonDay(..., -1, 0, 0)` et `EnterZone(..., -1, 1, 0)` placent bien le
  joueur à l'entrée (`GroundMap.GetEntryPoint` renverrait `(0,0)` sinon).
- **Objets `ewc3`** : les trois objets du `.rsground` (`SeuilDonjon`,
  `SortieRetourReverie`, `Statue_Kangourex` avec `DrawOffset 4,16`) sont
  identiques à leurs replis Lua — les anciennes sauvegardes retrouvent donc une
  statue alignée ; `RogueEssence.Content.ObjAnimData('Statue_Kangourex', 1)`
  correspond au constructeur `ObjAnimData(string,int)`.
- **Service `StatueKangourex`** : `ScriptServices.Publish` passe les arguments
  dans une table **indexée à 0** (cf. `origin/services/menu_tools` :
  `args[0]`), donc `args[1]` est bien la carte et non son nom.
- **`NoRescue` du 9F** : une défaite sur la carte de boss renvoie `Failed`
  (et non `Downed`), un abandon renvoie `GaveUp` ; `cause_echec_grotte` les
  classe correctement en `'ko'` et `'repli'`.
- **`GAME:SetRescueAllowed(false)`** : convention de tous les donjons Destiny
  (`lost_wood`, `passage_aquatique`, `dazzling_fight`), pas une régression.
- **`end_grotte_verdoyante`** : `20×15`, `EntryPoints (10,12)`, `NoRescue`,
  `BattlePositionEvent` → `(10,12),(9,12),(11,12),(10,13)` toutes sur du sol
  (aucun `InvalidOperationException`).

## Choix assumés (pas des bugs)

- `EmptyReturn` incrémente `JourneeVille` : chaque traversée complète des huit
  étages fait avancer la journée, comme le prévoit le cycle des missions.
- `GrotteVerdoyanteNbKO` est écrit mais jamais lu : compteur d'information pour
  les sauvegardes, volontairement conservé.
- `TouchOnce` ne remplacerait pas le verrou du seuil : le moteur ignore le
  **premier** contact de ce type (`GroundChar.Collide`), ce qui laisserait passer
  le joueur.

## Validation

```
tools/tests/test_grotte_verdoyante.py            PASS
tools/tests/test_statue_kangourex.lua            PASS
tools/tests/test_entrees_reverie.py              PASS
tools/tests/test_e2_reverie.py                   PASS
tools/tests/test_carrefour_reverie.py            PASS
tools/tests/test_lostwood_tutoriel.py            PASS
tools/tests/test_lostwood_lecons_statue.lua      PASS
tools/validate.py                                VALIDATION OK
les 44 scripts tools/tests/test_*.py             PASS
```

Les deux alertes vues pendant l'audit (`art/sprites/...` et les `*.csproj`)
venaient du checkout partiel, pas du dépôt : sur un clone complet, le test des
Bois Perdus et `tools/validate.py` passent sans modification.

Trois assertions de non-régression ont été ajoutées à
`tools/tests/test_grotte_verdoyante.lua` ; chacune **échoue** sur le code
d'avant correctif (vérifié par réinstallation temporaire de l'ancienne version)
et passe après.

`python3 tools/validate.py` signale uniquement les trois fichiers absents du
checkout partiel (`engine/**/*.csproj`, `art/destiny_title_background.png`) :
attendu en sparse-checkout, sans rapport avec ces changements.
