# Réverie — mise à jour 0.7.1

Base : branche `wip/reverie-integration-kingambit-cafe` (intégration du commit `7.1` / `136fcc4b` et de l'audit Phase 1 des cinématiques).

## Façade extérieure `guilde_cliff` (`Guilde_HD_*`)

* **Tronc marron (`wood_bark`) sur les 4 ambiances.** Les huit variantes de la façade extérieure de la Guilde Destiny (`Jour`, `Aube`, `Crépuscule`, `Nuit` × porte fermée et porte ouverte) reprennent le tronc boisé marron sans éclats violets ni bordure mauve rapportée au pied de l'escalier.
* **Ombre verte canonique (`Guilde_HD_Ombre_*`).** Les quatre ombres au sol (`Jour`, `Aube`, `Crépuscule`, `Nuit`) adoptent la teinte verte canonique translucide, encodée en RGBA prémultiplié conforme au chargeur XNA/FNA (`DirSheet` et banques `.tile` synchronisées à `0.0 px`).
* **Accueil de la Guilde (`Scale3x`).** Conserve la recompilation nette de `guilde_destiny_accueil`, le trait affiné des 11 bases intérieures et la correction des étages de donjons.

## Cinématiques et joignabilité (`destiny`)

* **Audit complet selon le *PMD Cutscene Guide*.** Correction des animations d'attente en cinématique (`CharEndAnim` au lieu de `'Idle'` sur les personnages non volants dans `cliffdaytest`), des retournements surpris animés face à Carchacrok (`fgv1_fin_grotte_vasques`), des pas de désynchronisation des rotations à vitesse `4` (`6` frames au lieu de multiples de `4` ou `0` sur la Guilde, le Café Spinda, la Grotte Verdoyante et Réverie Town), ainsi que des paliers d'écran noir d'au moins `30` frames lors des fondus de transition (`intro_halo`, `WaterfallVillageCapital`).
* **Accès direct en mode Dev.** Correction de l'écran noir lors d'une entrée directe via `Enter Ground` sur `personality_test` avec une sauvegarde ayant déjà franchi le prologue (`GAME:FadeIn(20)` sur le retour anticipé), en complément du garde `AccesDirectDevSansScenario()` sur les cartes à quatre ambiances.

## Vérifications et limites

Validation complète via `tools/validate.py`, `tools/audit_cinematiques.py`, `tools/audit_cadrage_acteurs.py` et l'intégralité de la suite `tools/tests/test_*.py` (Python + runtime Lua `lupa`). Sauvegarder ses parties avant de mettre à jour.
