# Crédits et provenance des ressources

Ce fichier trace l'origine de tout contenu importé dans **Pokémon Mystery
Dungeon: Destiny**, conformément au filtre de provenance du projet
(licence lue, origine vérifiée, aucun contenu extrait d'un jeu commercial
utilisé comme carte, crédit systématique).

Le détail fichier par fichier de l'import d'octobre 2026 est dans
[`docs/IMPORT_GUILDE_TREEHOUSE.md`](docs/IMPORT_GUILDE_TREEHOUSE.md).

## Moteur et jeu de base

- **PMDC / RogueEssence / PMDO** — moteur open source ; commits épinglés dans
  [`docs/SOURCE_LOCK.json`](docs/SOURCE_LOCK.json), notices dans `licenses/` et
  `base/Licenses/`. Voir [`docs/SOURCES.md`](docs/SOURCES.md).

## Cartes, layouts et assemblages

- **meromoonmeri** (auteur du projet) — les 228 cartes au sol et la carte de
  donjon importées en octobre 2026 sont ses propres créations pour PMDO,
  développées dans son atelier
  [`guilde-treehouse-pmd`](https://github.com/meromoonmeri/guilde-treehouse-pmd)
  (dépôt sans licence publique ; import effectué à la demande de l'auteur,
  droit de réutilisation interne au projet). Méthode décrite dans
  `MANUEL_METHODE_PMDO.md` et `AGENTS.md` de ce dépôt.

## Menu-titre animé (récupéré le 27 octobre 2026)

- **meromoonmeri** (auteur du projet) — fonds animés jour/nuit, blason
  « Œuf Ailé », séquence d'ouverture et service Lua `destiny_title_anim`,
  créés dans son atelier
  [`meromoonmeri/projet-creation-pmdo`](https://github.com/meromoonmeri/projet-creation-pmdo)
  (branche `arena/637b0828-projet-creation-pmdo`, commit
  `24c84f45c8bdd62969ef58de8b22ce2a874d415a` ; dépôt sans licence publique,
  import à la demande de l'auteur). Les images sources sont ses propres
  générations détourées par son pipeline
  (`source/pmd_destiny_fangame_v1/bruts/`) ; les sorties ont été reconstruites
  à l'octet près depuis ce pipeline (voir
  [`docs/MENU_TITRE.md`](docs/MENU_TITRE.md)).

## Cartes récupérées de `projet-creation-pmdo` (27 octobre 2026)

- **meromoonmeri** (auteur du projet) — cartes et assemblages produits dans
  son atelier
  [`meromoonmeri/projet-creation-pmdo`](https://github.com/meromoonmeri/projet-creation-pmdo)
  (dépôt sans licence publique ; import effectué à la demande de l'auteur).
  Lot 1 (7 cartes construites) : paquets des branches
  `arena/f9b9e04a-projet-creation-pmdo` (commit
  `f243f3e8107390940390f1af7c39230374ab60ee`),
  `arena/52e6a9de-projet-creation-pmdo` (commit
  `c2d77959d87bf334e9603b47df012bc4f1e3dd7a`) et
  `arena/e39626d2-projet-creation-pmdo` (commit
  `ef492fec6612924c7b2185e7c9555a562f3882db` ; seuls les grounds, tuiles et
  fonds des falaises ont été repris, les scripts de la cinématique Pichu sont
  restés dans l'atelier). Lot 2 (21 cartes) : sorties régénérées depuis les
  `build.py` committés de la branche `arena/637b0828-projet-creation-pmdo`
  (commit `24c84f45c8bdd62969ef58de8b22ce2a874d415a`), avec des `zip_bytes`
  et des comptes de tuiles identiques aux `metadata.json` d'origine.
  Plusieurs feuilles générées par ces pipelines réemploient de la matière
  pixellique dite « canonique » de *Pokémon Donjon Mystère : Équipe de
  Secours Rouge* / *Explorers of Sky* : même réserve de redistribution que
  pour les cellules DTEF ci-dessous. Aucun fichier source extrait
  (`.bpl`/`.bpc`/`.bma`) ni décodeur n'a été importé dans Destiny. Le rapport
  détaillé sera consolidé dans `docs/IMPORT_CREATION_PMDO.md` à la clôture de
  la tâche D.

## Banques de tuiles réemployées par ces cartes

- **Métano Town / Vast Steppe** (`Metano_Town_*`, `Vast_Steppe_*`, variantes
  nocturnes au filtre Abyss) — matière des falaises « Métano » et de
  Reverie Town. Selon l'auteur du projet, ce sont les tuiles de
  **« Reverie Town (waterfallvillagecapital) »**. La chaîne documentée dans
  l'atelier (`provenance.json`, sha256 à l'appui) les fait transiter par le mod
  **Halcyon** de Palikadude (dépôt `Palikadude/Halcyon`, branche
  `working-copy`, commit `1522c7a8b7a34d70078e11ed605b21d563b0dc51`).
  Halcyon ne publie **pas** de fichier LICENSE et son readme ne contient pas de
  clause de réutilisation : crédit affiché ici, et **accord de Palika à
  confirmer avant toute redistribution publique** du fangame.
  Crédits Halcyon (readme) : Palika (auteur) ; pixel art notamment Edan Momu,
  D4yz, Jaifain, Sunkern (Apricorn Grove).
- **Filtre nocturne Abyss** — `tools/tile_night.py` du projet New Era / Abyss
  de l'auteur (`new-era-abyss-to-ascension-V4`, commit
  `55860b9a5eb48697a3cea3a8bdfce5f0529d6141`), appliqué une fois aux terrains.
- **Fonds ciel/nuages Guilde / Sharpedo** — repris tels quels des travaux de
  l'atelier (commit `c16efe12` du dépôt source), sans redessin.
- **DumpAsset** (audinowho) — planches issues des ressources de base PMDO
  récupérées par DumpAsset (ex. `VastIceMountain.tile`), source autorisée par
  les règles du projet.
- **Cellules DTEF** — certaines cartes (série `canon1_*`, `ful1_*`, plages
  `D01P11A_*`) sont assemblées par l'auteur à partir de cellules de tuiles
  DTEF (format d'échange issu des dumps de Pokémon Donjon Mystère : Explorers
  of Sky). Les **layouts** sont originaux ; les **pixels** de ces feuilles
  proviennent du jeu commercial, au même titre que les tuiles livrées avec le
  jeu de base PMDO. À réévaluer si le projet durcit sa règle sur les pixels.
- **Objets Ice Peak** (`Ice_Peak_*.dir`, carte `frozen_crucible`) — conversions
  depuis le **PMD Sprite Repository / SpriteCollab** ; créditer les artistes
  des `AnimData.xml` d'origine avant redistribution.
- **Fonds glacier** (`GLACIER_*.dir`) — convertis par l'atelier depuis des PNG
  « canoniques » de son espace de travail (`*pmdsky*.png`) ; origine première
  non établie, à confirmer par l'auteur.

## Contenu explicitement écarté (non importé)

- Cartes de référence tierces stockées dans l'atelier (dossiers `references/`) :
  ExplorersOfSkyOrigins (`Brine Cave`, `Drenched Bluff`, `Beach`…), lieux des
  jeux commerciaux (`treasure_town`, `guild_outside`, `spinda_cafe`,
  `luminous_spring`…), ainsi que les copies de référence embarquées dans
  certains packs (`altere_pond`, `vast_steppe_entrance` — identifiées par
  sha256).
- Extractions Spriters Resource / dumps DTEF bruts présents à la racine de
  l'atelier (documents d'étude uniquement).
- Anciennes versions des lieux importés : la liste et le motif de chaque
  exclusion sont consignés dans
  [`docs/IMPORT_GUILDE_TREEHOUSE.md`](docs/IMPORT_GUILDE_TREEHOUSE.md).
