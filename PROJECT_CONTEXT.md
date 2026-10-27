# Pokémon Mystery Dungeon: Destiny — contexte du projet

Fangame PMDO autonome (moteur 0.8.12 épinglé, voir `docs/SOURCES.md`),
Namespace `destiny`, UUID `746CBBCD-426F-5419-A735-D50248440935`
(**ne jamais les modifier** — voir `docs/LESSONS.md`).

## État actuel (27 octobre 2026)

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

## Chantiers suivants (par priorité)

1. **Tâche D (`projet-creation-pmdo`) — terminée le 27/10/2026** : 33 cartes
   importées en 3 lots, rapport `docs/IMPORT_CREATION_PMDO.md` (exclusions
   prouvées incluses : intérieurs `metano_gen_*`, SpindaV4, tour temporelle),
   galerie complète régénérée. Reste l'arbitrage « pixels canoniques »
   du lot 2 (réserve dans `CREDITS.md`).
2. **Tests en jeu** PMDO Dev 0.8.12 (checklist dans
   `docs/IMPORT_GUILDE_TREEHOUSE.md` §8) — surtout les 98 cartes en
   sérialisation 0.7.x/0.8.9 et les plages.
3. **Collisions et entrées/sorties** des bases côtières (`Tags = 0` dans
   l'atelier), puis raccordements entre cartes voisines et vers `destiny_hub`.
4. **Dépendances manquantes** : MapStatus `steam` et 4 musiques à récupérer
   depuis New Era / l'installation de l'auteur
   (`docs/IMPORT_GUILDE_TREEHOUSE.md` §6).
5. **Pièces de la guilde** : les 12 salles n'existent qu'en PNG dans l'atelier ;
   à construire en `GroundMap`.
6. **Cinématiques (Partie 2)** : cadrage, foreshadowing
   (`docs/foreshadowing.md`), puis scènes en français avec portraits vérifiés,
   caméra dynamique, boss motivés (règles dans `docs/LESSONS.md`).
7. **Renommage « univers Destiny »** des cartes au fil des raccordements (les
   `AssetName` actuels sont ceux de l'atelier).

## Règles qui ne changent pas

- Filtre de provenance (étape 0) avant tout nouvel import ; exclusions fermes :
  extractions/remakes de jeux commerciaux, Spriters Resource.
- Toujours valider (`tools/validate.py`) avant de commiter ; commits séparés
  par domaine ; jamais de token d'accès dans les fichiers.
