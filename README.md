# Pokémon Mystery Dungeon: Destiny

Base autonome du fangame **Pokémon Mystery Dungeon: Destiny**, construite avec le moteur open source PMDO 0.8.12.

Ce dépôt est volontairement **sans Git LFS, sans sous-module et sans lien symbolique**. Le moteur, les ressources de base et le mod Destiny sont de vrais fichiers présents dans le dépôt.

## Jouer sous Windows

1. Télécharger `PMDO-Destiny-Windows-x64.zip` dans la section Releases.
2. Extraire tout le ZIP dans un dossier accessible en écriture.
3. Double-cliquer sur **`JOUER_A_DESTINY.bat`**.

PMDO fusionne la quest pendant la construction : le lanceur démarre simplement `Destiny.exe`. Il n'est pas nécessaire d'installer PMDO séparément, de choisir une quest ou de conserver un dossier `MODS`.

Si le son grésille, essayer `JOUER_A_DESTINY_WASAPI.bat`.

## Contenu actuel

- écran-titre Destiny avec nuages et mer ;
- moteur PMDO compilable et inclu dans `engine/` ;
- données et ressources PMDO dans `base/` ;
- quest autonome `destiny` dans `game/`, fusionnée au moteur dans le ZIP ;
- sélection du héros proposée par PMDO ;
- première map technique `destiny_hub`, avec son script et sa zone indexée.

Il s'agit d'un socle de développement jouable, pas encore d'une histoire complète.

## Organisation

| Dossier | Rôle |
|---|---|
| `engine/` | PMDC, RogueEssence et leurs dépendances source matérialisées |
| `base/` | Données et ressources runtime PMDO nécessaires au moteur |
| `game/Content/` | Images et ressources propres à Destiny |
| `game/Data/Ground/` | Maps fixes ouvrables dans l'éditeur |
| `game/Data/Map/` | Futures maps de donjons |
| `game/Data/Zone/` | Zones, donjons et index |
| `game/Data/Script/destiny/` | Scripts Destiny séparés par namespace |
| `game/Strings/` | Traductions et titre du jeu |
| `art/` | Illustrations sources, dont l'écran-titre |
| `tools/` | Validation et construction du ZIP Windows |
| `docs/` | Architecture, provenance et crédits |

## Compiler le ZIP Windows

Prérequis : **.NET SDK 8**, **Python 3** et **Pillow**.

```bash
python -m pip install Pillow
python tools/validate.py
python tools/build_windows.py
```

Sous Windows, il est aussi possible de double-cliquer sur `build_windows.bat`.

Résultats :

- `build/windows/` : dossier du jeu autonome ;
- `dist/PMDO-Destiny-Windows-x64.zip` : archive prête à distribuer.

Les sorties compilées ne sont pas suivies par Git. Une action GitHub manuelle permet aussi de produire le ZIP.

## Vérifier le dépôt

```bash
python tools/validate.py
```

Les résultats du contrôle structurel, de la construction Windows et du parcours runtime jusqu'à la sauvegarde sont consignés dans [`docs/VALIDATION.md`](docs/VALIDATION.md).

Le contrôle vérifie notamment :

- absence de pointeurs Git LFS et de règles `filter=lfs` ;
- absence de sous-modules et de liens symboliques ;
- absence de fichiers dépassant la limite GitHub de 100 Mio ;
- cohérence de la map, de la zone, de l'index et des paramètres de départ ;
- dimensions de l'écran-titre interne PMDO.

## Maps de PROJET-PMD

Les maps de l'ancien dépôt peuvent être importées sélectivement dans `game/Data/Ground/`. Elles ne sont pas copiées massivement : certaines ressources de PROJET-PMD dépassent 100 Mio et devront être optimisées ou reconstruites pour conserver ce nouveau dépôt sans LFS.

## Moteur et statut

- Moteur : PMDO / PMDC / RogueEssence.
- Notices du moteur : `licenses/` et `base/Licenses/`.

Destiny est un fangame non officiel et non commercial. Pokémon et Pokémon Mystery Dungeon appartiennent à leurs ayants droit respectifs.
