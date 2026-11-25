# Draco et le bassin de Réverie — rapport préalable

Base : Destiny 0.5.7, commit ee39156a24f350b67e81740478be8505f4ff1a05, travail local restauré depuis `sauvegarde-integrations-locales-pmu.zip` (les sept intérieurs sont encore en chantier). La sauvegarde `avant-init.lua` est une copie du script local avant toute intervention Draco ; conserver aussi l'archive complète déjà existante.

Bassin candidat : carte `reverie_etang`, sous la cascade au sud-est, autour de (1070, 2080), avec grand autel et trois pierres. Ce n'est pas le grand plan d'eau du nord ni la proposition non intégrée près de la maison-plante. L'identification est fondée sur l'agencement demandé (étang/autel), pas sur une confirmation explicite du nom par le joueur.

Position prototype : Draco (1120, 2080), dans une case actuellement bloquée par l'eau, adjacent à la plate-forme ; case du joueur testée libre (1104, 2080). Un parcours statique est possible entre (1072, 2200) et cette case via les pierres, mais aucun test d'interaction moteur ni d'événement ou d'acteur dynamique n'a été réalisé. Les collisions de la carte ne seront pas modifiées. Grodrive `Doyen` et les autres habitants ne doivent pas être remplacés.

SpriteCollab : Dragonair #0148, commit 709f2e32ae4b21d11628883fd2356bb2d5f75244 ; crédits CHUNSOFT, mention de licence « Unspecified » dans le fichier d'origine. Ne pas déclarer les graphismes libres ni les redistribuer sous une licence inventée. Le dépôt Destiny possède déjà `base/Content/Chara/148.chara` (SHA-256 4d4b49aa3540df78f2d4b6f56f6e7a5083fc454576925cc558d88bd84e479cf1) et l'espèce `dragonair`, index 148 ; correspondance exacte des frames native/SpriteCollab non vérifiée.

Le SpriteCollab `Idle` est un alias de `Walk`, pas une animation de nage distincte. Halcyon étudié ne prouve pas d'effet de nage automatique. `HideShadow` existe dans le moteur Destiny mais ne crée aucune ondulation ; l'aperçu est une composition statique, non une capture moteur. La suppression de l'ombre doit être réappliquée au chargement car elle n'est pas sérialisée. Un véritable effet aquatique et les migrations liées à la future fusion des sections restent à faire et tester.
