# Réverie — mise à jour 0.7.3

Base : branche `wip/reverie-integration-kingambit-cafe` (refonte de la **Fosse Cascade** / **Fosse Cascade Fond**, remplacement du boss par **Kabutops**, correction de l'arène `.rsmap` et de l'écran noir au duel, et nouvelle cinématique d'apparition inspirée d'*Halcyon*).

## Renommage affiché : Fosse Cascade & Fosse Cascade Fond

* **Fosse Cascade (`grotte_verdoyante`).** Le donjon derrière la cascade est désormais nommé **« Fosse Cascade »** (`Fosse Cascade\n{0}F` sur les étages `1F` à `8F`, **« Fosse Cascade — Entrée »** sur `ewc3_entree_waterfall_cave`) dans les zones, cartes, menus de destination, tableau des missions, gazette et dialogues de Réverie Town, du Café Spinda et de la falaise de la Guilde.
* **Fosse Cascade Fond (`fgv1_fin_grotte_vasques` & `end_grotte_verdoyante`).** La salle finale et son arène de duel portent désormais le titre **« Fosse Cascade Fond »**, tout en conservant intacts l'ensemble des identifiants techniques de scripts, zones et ressources.

## Arène `end_grotte_verdoyante.rsmap` et correction de l'écran noir

* **Concordance visuelle exacte (`0 / 172 800` px d'écart).** Reconstruction de `end_grotte_verdoyante.rsmap` (`20×15` tuiles de `24 px` = `480×360`) sur la planche animée 12 phases `FGV1_VASQUES_BASE_24.tile` (`DrawLayer.Bottom` + `DrawLayer.Top`), `DiscoveryArray = Traversed (2)` sur les 300 tuiles, `TileSight = 0`, `CharSight = 0`, `EdgeView = Clamp`, `BoxStorage = []` et 42 cases de sol praticables épousant la clairière sableuse de `fgv1_fin_grotte_vasques`.
* **Transition de duel y compris depuis l'éditeur (`-dev`).** Lorsque la scène est lancée directement depuis le *Ground Editor* (`_ZONE.InDevZone == true`), `GAME:ContinueDungeon` (`forceNewZone = false`) renvoyait à l'éditeur au lieu de charger le Segment 1 : `fgv1_fin_grotte_vasques` bascule désormais automatiquement sur `GAME:EnterDungeon('grotte_verdoyante', 1, 0, 0, ...)` en session `-dev` et conserve `GAME:ContinueDungeon` en traversée normale.

## Nouveau boss : Kabutops & cinématique d'apparition (*Searing Crucible*)

* **Kabutops (`kabutops`, Niv. 14).** Remplace Carchacrok comme seigneur de la **Fosse Cascade Fond** (`Roche`/`Eau`, talent `Armurbaston`, `PV 162/162`, `Aqua-Jet`, `Tranche`, `Tir de Boue`, `Groz'Yeux`, posté en `(10, 8)` face à l'équipe entrant en `(10, 11)`). Le PNJ citadin Sillage à Réverie Town demeure inchangé.
* **Mise en scène inspirée de *Searing Crucible* (*Halcyon*) et du *PMD Cutscene Guide*.** Boss pré-instancié masqué (`GROUND:Hide`), coupure nette de la musique sur la première secousse souterraine (`SOUND:StopBGM`), bouillonnement des vasques (`Bubbles_Blue`, `Wave_Circle_Blue`) et recul synchronisé du groupe en gardant le regard vers le haut (`AnimateInDirection`), voix invisible hors-champ sans portrait (`\uE040`), montée de tension sur `Rising Fear.ogg`, éruption d'un geyser (`EVT_CH05_Waterfall_Cave_Geyser`, `Water_Column_Ranger`, `Water_Spout_Splash`) révélant Kabutops (`GROUND:Unhide`, saut `Hop` et coup de faux `Swing` / `Slash_Ranger`), puis fondu musical propre de `30` frames vers `Boss Battle 2.ogg`.

## Vérifications

Validation complète via `tools/validate.py`, vérification de désérialisation et de génération des 9 étages (`Segment 0` `1F..8F` et `Segment 1` `LoadGen`) dans le moteur C# `.NET 8` (`RogueEssence` / `PMDC`), et passage de l'intégralité des `43/43` suites `tools/tests/test_*.py` (Python + runtime Lua `lupa`). Sauvegarder ses parties avant de mettre à jour.
