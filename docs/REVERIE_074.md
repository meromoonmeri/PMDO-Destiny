# Réverie — mise à jour 0.7.4

Base : branche `wip/reverie-integration-kingambit-cafe` (après `v0.7.3` / `30dc4447f2`).
Objet : **refonte complète de la cinématique de pré-combat et de post-combat de la Fosse Cascade Fond** (boss Kabutops), sur demande explicite :

> « je veux pas d'animation d'eau à son apparition », « le pacing soit soutenu », « un flash blanc => incompréhension des héros/partenaire », « double flash blanc il spawn le boss », « le boss doit pas être sur l'escalier quand il spawn », « le Lixy doit trembler on doit le voir », « quand il part il fuit vers le sud en course », « les sons doivent être coordonnés à la cinématique visuelle ».

Fichier central : `game/Data/Script/destiny/ground/fgv1_fin_grotte_vasques/init.lua` (`PreBattle`, `PostBattle`, `EmptyReturn`).

## 1. Le problème de mise en scène corrigé

La bande des **vasques en terrasses** (« l'escalier » d'eau) occupe `y = 136..208` sur la carte `480x360`. Kabutops était créé en **`(240, 192)`**, c'est-à-dire *au milieu des terrasses*, et il « jaillissait » d'un geyser (`Water_Column_Ranger`, `Water_Spout_Splash`, `Bubbles_Blue`, `Wave_Circle_Blue`, SE `EVT_CH05_Waterfall_Cave_Geyser` / `EVT_CH05_Hot_Spring_Splash`).

| Repère | Avant | Après |
| --- | --- | --- |
| Kabutops | `(240, 192)` — sur les vasques | **`(240, 232)` — sable plat sous les vasques** |
| Nilo endormi | `(264, 152)` | `(264, 176)` (même zone, plus lisible) |
| Nilo en terreur | `(264, 144)` — derrière les vasques | **`(288, 248)` — à l'écran, côté est** |
| Héros / partenaire | `(240, 248)` / `(216, 256)` | `(232, 264)` / `(256, 268)` |
| Caméra de face | `(240, 200)` | **`(240, 236)`** (pieds des acteurs ≤ 152 px écran) |

La position de combat du `.rsmap` (`end_grotte_verdoyante`, Kabutops en tuile `(10, 8)`) est **inchangée** : seule la mise en scène au sol change.

## 2. Pré-combat : nouvelles structures d'éclairs

1. **Un éclair blanc** (`SOUND:PlayBattleSE('EVT_Battle_Flash')` + `GAME:FadeOut(true, 3)` / `GAME:FadeIn(9)`) : les deux héros ne comprennent pas ce qu'ils viennent de voir — regards désynchronisés (`0f` / `5f`), émote `question`, **un seul** SE d'émote (`EVT_Emote_Confused`), réplique courte du partenaire, puis la voix hors-champ des abysses (une seule réplique, sans portrait).
2. **Double éclair blanc** (`2f`+`6f`, puis `2f`+`8f`) : `GROUND:Unhide('Kabutops_Boss')` se produit **pendant le premier blanc plein**, donc le boss est déjà là quand le second éclair s'efface — il « apparaît dans le flash », sans aucune animation d'eau.
3. **Aucune eau** : suppression de tous les VFX (`Water_Column_Ranger`, `Water_Spout_Splash`, `Wave_Circle_Blue`, `Bubbles_Blue`) et des deux SE d'eau du script. Le bouillonnement des vasques est remplacé par une secousse de sol (`EVT_Tower_Tremor_Weak` + `MoveScreen(2, 4, 18)`).

## 3. Nilo (Lixy) tremble — visiblement

`GROUND:CharSetDrawEffect(nilo, RogueEssence.Dungeon.DrawEffect.Shaking)` (repli numérique `= 2` si l'énumération n'est pas exposée à Lua). `Shaking` oscille de **-2 à +2 px** sur un cycle de 8 images, alors que `Trembling` ne fait que 1 px : c'est la seule variante réellement visible à l'écran. Le tremblement est appliqué quand Nilo recule dans son recoin, maintenu pendant tout le face-à-face, relâché par `GROUND:CharEndDrawEffect` juste avant `COMMON.BossTransition`, et réutilisé en post-combat jusqu'au départ du boss.

## 4. Post-combat : Kabutops fuit vers le sud **en courant**

Le plongeon dans les vasques (`Water_Spout_Splash` + `Wave_Circle_Blue` + `Hop` + `RemoveCharacter`) est remplacé par :

* réplique de défaite (courte) puis `arrêter le tremblement de Nilo` ;
* `GROUND:CharAnimateTurnTo(kabutops, Direction.Down, 3)` ;
* `SOUND:PlayBattleSE('DUN_Tile_Step')` sur la même image que le départ ;
* **`GROUND:MoveToPosition(kabutops, 240, 352, true, 3)`** — course de `232` à `352` px dans le couloir sud à **3 px/image**, caméra qui accompagne (`(240,236)` → `(240,240)`, limite de `Clamp`), puis sortie de carte ;
* Nilo se relève et rejoint le duo (`(256, 248)`), Lyra arrive ensuite du sud comme avant.

## 5. Pacing soutenu & sons coordonnés

* Fondu d'entrée `16f`, carte de titre `16f`/`18f`, attentes de réaction réduites de `25–30f` à `6–12f`.
* Transitions musicales raccourcies : `FadeOutBGM(15)` + `15f` avant `Rising Fear.ogg` et avant `Boss Battle 2.ogg` (au lieu de `30f`).
* **Jamais de coupe BGM → BGM** : `SOUND:StopBGM()` sec au moment du choc (coupure vers le silence), puis relance **après** le retour de l'image.
* **Un seul SE par événement**, déclenché sur l'image de son événement visuel : `EVT_Battle_Flash` (chaque éclair), `EVT_Tower_Tremor_Weak` (secousse), `EVT_Roar` + `MoveScreen` (réception), `DUN_Slash` (coup de faux d'intimidation), `DUN_Tile_Step` (départ de la fuite). Le rugissement final est devenu une secousse (`EVT_Tower_Tremor_Strong`) pour éviter deux rugissements identiques.
* `Camera` : un seul axe de panoramique, `1,5 px/image` pour la montée du duo, pas de panoramique secondaire pendant les répliques, pieds de tous les acteurs sous le repère `160 px` écran (la boîte commence à `188`).

## 6. Vérifications

* `tools/tests/test_grotte_verdoyante.lua` — **PASS**, avec de nouveaux contrôles :
  * Kabutops créé hors de la bande des terrasses (`y >= 216`) ;
  * **exactement 3** `EVT_Battle_Flash` (un éclair + un double) ;
  * **zéro** VFX / SE d'eau en pré- et post-combat ;
  * `DrawEffect` appliqué **puis** relâché sur `Nilo_Grotte` ;
  * fuite de Kabutops enregistrée vers `y >= 344` à la vitesse `3`.
* `tools/audit_cinematiques.py` — OK (131 scripts, aucune réplique > 96 caractères, balises `[color]` équilibrées).
* `tools/audit_cadrage_acteurs.py` — OK (aucun personnage masqué par la boîte de dialogue).
* Compilation Lua du script vérifiée (`load`), et `diff` de contrôle : le fichier distant avant patch était bien identique à la sauvegarde `backup_avant_cinematique_boss_fgv1.tar.gz`.

## 7. À valider en jeu

1. `RogueEssence.Dungeon.DrawEffect` n'est pas garanti exposé à Lua : repli numérique `2` (`Shaking`) prévu ; si le tremblement ne s'affiche pas, le repli prend le relais sans erreur.
2. `DUN_Tile_Step` sert de bruit de course (un seul pas au départ). Alternative possible : `SOUND:LoopBattleSE('DUN_Tile_Step')` pendant la fuite puis `StopBattleSE`.
3. Les éclairs utilisent `GAME:FadeOut(true, …)` / `GAME:FadeIn(…)` : ce sont des fondus au **blanc** plein écran (le moteur ne possède pas de flash instantané unique), ce qui donne bien l'effet « flash ».

## 8. Hors périmètre (non appliqué)

Le lot **« côté vert foncé rectangulaire » + intérieurs de chemin vs Metano Town** (unification des tuiles `01_Sol_herbe(39,218)` et sables dorés des 14 segments `C-01..C-14`) reste **proposé et simulé uniquement** : aucune carte `.rsground` / `.rsground.gz` n'est modifiée par cette mise à jour. Les 15 points épinglés (`tools/corriger_15_pins_reverie.py`) et l'unification du calque `Cliffs` restent en l'état de `v0.7.3`.
