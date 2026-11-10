# Falinks #0870 (Hexadron) — escouade 6 unités + 16 portraits

Sources récupérées depuis `meromoonmeri/guilde-treehouse-pmd` (branche `arena/01a07b43-guilde-treehouse-pmd`, dossiers `personnages/falinks/` et `portraits/falinks/`).

## Intégration dans PMDO-Destiny

- **Forme 0 (`870.chara`, `870.portrait`)** : escouade complète à 6 unités (1 Brass + 5 Troopers, 12 animations donjon, `ShadowSize = 2`) et 16 émotions de portrait + 16 miroirs dérivées pixel-par-pixel du portrait `Normal` d'Emmuffin.
- **Formes existantes préservées** : `base/Content/Chara/870.chara` (Formes 1 Brass et 2 Trooper + shinies) et `base/Content/Portrait/870.portrait` (`(0, 1)` shiny forme 0, Formes 1 et 2 + shinies) sont conservées intactes dans les conteneurs fusionnés.
- **Données espèce (`game/Data/Monster/falinks.json` & `index.idx`)** : `Released = true` sur l'espèce et la forme 0.
- **Reconstruction** : `python tools/integrer_falinks.py`

## Crédits & licences

- Unité Brass `0870/0002` : ◥θ┴θ◤ (`<@!215638650434617345>`), licence `PMDCollab_1`.
- Unité Trooper `0870/0003` : baronessfaron (`<@!544245909639397378>`), licence `CC BY-NC 4.0`.
- Portrait `Normal` de base : Emmuffin (`<@!356635814668664832>`), licence `PMDCollab_2`.
- Composition escouade 6 unités & déclinaison 16 émotions : Guilde Treehouse (`CC BY-NC 4.0` / `PMDCollab_2` — hors usage commercial).
