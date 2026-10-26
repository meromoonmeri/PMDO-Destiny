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
