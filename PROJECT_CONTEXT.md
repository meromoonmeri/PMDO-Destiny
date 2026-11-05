# Pokémon Mystery Dungeon: Destiny — contexte du projet

Fangame PMDO autonome (moteur 0.8.12 épinglé, voir `docs/SOURCES.md`),
Namespace `destiny`, UUID `746CBBCD-426F-5419-A735-D50248440935`
(**ne jamais les modifier** — voir `docs/LESSONS.md`).

## Mise à jour du 5 novembre 2026 (état réel de l'arbre)

Les sections historiques plus bas décrivent la **phase d'import** (octobre
2026) et ne correspondent plus au contenu livré. L'arbre consolidé de la
branche `destiny-unifiee` (release 0.4.7 → tranche en cours) contient :

- **47 cartes au sol** versionnées (+ `WaterfallVillageCapital` livrée
  compressée dans `payload/` et restaurée à la construction) réparties en
  **9 zones** : `destiny_hub`, `personality_test`, `destiny_cliff_tests`,
  `lost_wood` (donjon), `dazzling_fight`, `town02_waterfallvillage`,
  `reverie`, `chapitres_destiny`, `vitrines_menu` ;
- **2 133 planches** `.tile` (index régénéré par la construction), 136 fonds,
  80 jeux d'objets, 7 musiques propres ;
- **69 scripts Lua** sous `game/Data/Script/destiny/` ;
- parcours jouable continu : `intro_halo` → quiz de personnalité → réveil à
  Réverie → falaise de nuit → donjon des Bois Perdus (aller/retour, échecs
  KO et abandon) → falaise de jour et combat Dazzling → Réverie Town
  (`WaterfallVillageCapital`) et son quartier vivant ;
- **Réverie Town** : 25 habitants avec dialogues Destiny, marchands natifs
  (Kecleon ×2, Kangourex, Gimmighoul, Alakazam, Tinkaton), 12 intérieurs
  raccordés, café Spinda sur trois salles, Bekipan facteur, thème d'interface
  réglable dans les options ;
- **café Spinda** : bar à jus (`JuiceShopMenu` natif, 87 ingrédients) et
  atelier de recyclage d'Okéoké/Qulbutoké (`InventorySelectMenu`, cotes de
  reprise, trouvailles du jour) — voir
  `docs/Bilan_CAFE_SERVICES_2026-11-05.md`.

Les cartes importées mais non raccordées (`chapitres_destiny`, l'essentiel de
`reverie`) restent des décors ouvrables dans l'éditeur : elles attendent leur
scénarisation, pas leur construction.

## État actuel (27 octobre 2026) — journal de la phase d'import

- **`destiny_hub`** : carte de départ d'origine, inchangée ; la partie démarre
  toujours dessus (`game/Data/StartParams.xml`).
- **Import des cartes de l'atelier** `guilde-treehouse-pmd` : **228 cartes au
  sol + 1 carte de donjon** importées avec leurs dépendances (1 023 banques de
  tuiles, 102 fonds/objets), rangées dans trois zones dédiées
  (`cotes_metano`, `ateliers_donjons`, `reverie`) avec scripts squelettes.
  Rapport complet : `docs/IMPORT_GUILDE_TREEHOUSE.md` ; crédits :
  `CREDITS.md`. **Aucun raccordement au hub pour l'instant** (choix de
  l'auteur : import d'abord, cinématiques ensuite).
- **Menu-titre animé** (27/10/2026) : récupéré depuis l'atelier
  `projet-creation-pmdo` et reconstruit à l'octet près depuis son pipeline —
  fonds mer/ciel JOUR et NUIT animés (24 poses, selon l'heure), apparition du
  blason Œuf Ailé une fois par session, service Lua `destiny_title_anim`
  enregistré par `game/Data/Script/destiny/main.lua`. Voir
  `docs/MENU_TITRE.md`.
- **Import `projet-creation-pmdo` (tâche D, en cours)** : lot 1, 7 cartes
  construites saines (crevasse enneigée, grotte aux vasques, traversée
  cristalline, falaises Reverie jour/nuit) ; lot 2, 21 cartes reconstruites
  depuis leurs pipelines d'atelier avec des `zip_bytes` identiques aux
  métadonnées commitées ; lot 3, 5 seuils sud-nord convertis depuis le
  schéma maison `AssetLayers` vers le format natif PMDO (animations par
  `Frames`/`FrameLength`, collisions et marqueurs d'origine conservés ;
  poses 0 relues par le renderer du projet sans tuile manquante ni écart de
  pixel). Les 8 lieux des Chapitres I/II forment la nouvelle zone
  `chapitres_destiny` ; les autres seuils/arènes rejoignent
  `ateliers_donjons` (156 cartes). État après ces trois lots : **262 cartes
  au sol** (dont `destiny_hub`), 1 carte de donjon, **1 322 banques de
  tuiles**, 113 `.dir`, 5 zones et 262 scripts squelettes. Aucune de ces
  nouvelles cartes
  n'est encore raccordée au hub ni scénarisée ; sur les falaises, la
  cinématique Pichu d'origine est volontairement inactive.
- **Aperçus des maps** : `tools/preview_maps.py` rend hors-moteur les cartes
  au sol (fonds + calques, pose 0) dans `import_work/apercus_site/` (galerie
  HTML, hors Git, régénérable). Galerie complète régénérée à la clôture de
  la tâche D : 264 entrées (262 cartes + 2 écrans-titre), 0 erreur,
  0 tuile irrésolue.
- **Validation** : `tools/validate.py` (Python + Pillow) couvre désormais
  aussi les cartes/zones/index importés et le menu-titre — `VALIDATION OK`
  le 27/10/2026.

## Chantiers suivants (par priorité, 5 novembre 2026)

1. **Services du café Spinda — fait** (5/11) : bar à jus et atelier de
   recyclage branchés sur les menus natifs, voir
   `docs/Bilan_CAFE_SERVICES_2026-11-05.md`. Reste le passage en jeu
   (Windows) des deux menus.
2. **Tests en jeu** PMDO Dev 0.8.12 : checklist des intérieurs
   (`docs/Bilan_MAJ_BATIMENTS_INTERIEURS_2026-11-02.md`), menus natifs de la
   ville, séquences Bois Perdus avec KO et abandon, services du café.
3. **Suite du scénario (Chapitre II)** : enchaîner après l'arrivée à Réverie
   Town, raccorder les lieux de `chapitres_destiny` et écrire les scènes en
   français (cadrage, foreshadowing `docs/foreshadowing.md`, boss motivés).
4. **Intérieurs dédiés** : forge de Tinkaton, réserve commune
   (Kecleon/banque/Kangourex), dojo Kingambit — aujourd'hui partagés ou
   provisoires.
5. **Dépendances manquantes** : MapStatus `steam` et 4 musiques à récupérer
   depuis New Era / l'installation de l'auteur
   (`docs/IMPORT_GUILDE_TREEHOUSE.md` §6).
6. **Renommage « univers Destiny »** des cartes au fil des raccordements (les
   `AssetName` actuels sont ceux de l'atelier).

## Règles qui ne changent pas

- Filtre de provenance (étape 0) avant tout nouvel import ; exclusions fermes :
  extractions/remakes de jeux commerciaux, Spriters Resource.
- Toujours valider (`tools/validate.py`) avant de commiter ; commits séparés
  par domaine ; jamais de token d'accès dans les fichiers.
