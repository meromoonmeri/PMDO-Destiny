# Pokémon Mystery Dungeon: Destiny — contexte du projet

Fangame PMDO autonome (moteur 0.8.12 épinglé, voir `docs/SOURCES.md`),
Namespace `destiny`, UUID `746CBBCD-426F-5419-A735-D50248440935`
(**ne jamais les modifier** — voir `docs/LESSONS.md`).

## État actuel (26 octobre 2026)

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
- **Validation** : `tools/validate.py` (Python + Pillow) couvre désormais
  aussi les cartes/zones/index importés et le menu-titre — `VALIDATION OK`
  le 27/10/2026.

## Chantiers suivants (par priorité)

1. **Tests en jeu** PMDO Dev 0.8.12 (checklist dans
   `docs/IMPORT_GUILDE_TREEHOUSE.md` §8) — surtout les 98 cartes en
   sérialisation 0.7.x/0.8.9 et les plages.
2. **Collisions et entrées/sorties** des bases côtières (`Tags = 0` dans
   l'atelier), puis raccordements entre cartes voisines et vers `destiny_hub`.
3. **Dépendances manquantes** : MapStatus `steam` et 4 musiques à récupérer
   depuis New Era / l'installation de l'auteur
   (`docs/IMPORT_GUILDE_TREEHOUSE.md` §6).
4. **Pièces de la guilde** : les 12 salles n'existent qu'en PNG dans l'atelier ;
   à construire en `GroundMap`.
5. **Cinématiques (Partie 2)** : cadrage, foreshadowing
   (`docs/foreshadowing.md`), puis scènes en français avec portraits vérifiés,
   caméra dynamique, boss motivés (règles dans `docs/LESSONS.md`).
6. **Renommage « univers Destiny »** des cartes au fil des raccordements (les
   `AssetName` actuels sont ceux de l'atelier).

## Règles qui ne changent pas

- Filtre de provenance (étape 0) avant tout nouvel import ; exclusions fermes :
  extractions/remakes de jeux commerciaux, Spriters Resource.
- Toujours valider (`tools/validate.py`) avant de commiter ; commits séparés
  par domaine ; jamais de token d'accès dans les fichiers.
