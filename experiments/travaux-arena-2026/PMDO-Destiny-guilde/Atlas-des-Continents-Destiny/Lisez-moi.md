# Atlas des continents — Pokémon Mystery Dungeon: Destiny

Une proposition de monde pour Destiny, dessinée sur le **fond nu déjà validé**. Les côtes, les reliefs et les pictogrammes ont été redessinés pour cet atlas. La carte ne reprend ni le tracé des terres d’*Explorateurs du Ciel* ni celui de *Pokémon Méga Donjon Mystère*.

## Fichiers

- **`Carte-des-Continents-Destiny-5560x3660.png`** — planche mondiale, sans noms ni marqueurs par-dessus les dessins. Le dessin pixel art mesure 1 112 × 732 px au format de travail ; le grand PNG est un agrandissement entier ×5, sans interpolation.
- **`Explorer-Atlas-Destiny.html`** — atlas autonome, même hors ligne. Cliquez sur une terre, son nom ou sa fiche pour vous en approcher. **Île de Réverie** cadre la région de départ ; **Monde** réinitialise le cadrage. Masquez les **Noms** et **Lieux** pour retrouver le dessin seul. Panoramique au glisser, zoom à la molette, au pincement ou avec **− / +**. Au clavier, focalisez la carte puis utilisez les flèches, **+ / −** et **0**.
- **`Ile-de-Reverie.png`** — planche de détail, 900 × 900 px. Elle isole l’île sur le même papier et montre les petits sentiers entre les six emblèmes.
- **`Calques/Carte-Destiny-1112x732.png`** — planche mondiale à l’échelle de travail.

## Terres et lieux

| Terre | Biome |
| --- | --- |
| Verdelande | Sylves et chutes d’eau |
| Givrevent | Fjords et crêtes de glace |
| Cendrebrèche | Caldeiras et terres de cendre |
| Palusonges | Marais et mangroves |
| Métano | Grands lacs et côtes |
| Ambresable | Dunes, mesas et oasis |
| Vesperre | Falaises et ruines anciennes |
| Florélys | Palmeraies et jardins fleuris |
| Île de Réverie (hors des huit continents) | Île de départ, autour du grand arbre |

Parmi les 30 emplacements dessinés, huit sont rattachés à des lieux du projet : **Réverie Town, falaise de la guilde, Fosse Cascade, Passage Aquatique, Bois Perdus, Source Irisée**, puis **Bourg Écume** et **Côtes de Métano**. La disposition mondiale, la forme des terres, les sentiers dessinés et les autres noms sont des propositions pour Destiny ; ce ne sont pas des coordonnées du jeu. Le donjon derrière la cascade est nommé *Fosse Cascade*, conformément aux notes du projet (`docs/REVERIE_073.md`). Il n’y a pas de repère en double sous son ancien nom « Grotte Verdoyante ».

## Calques et retouches

Composer les calques dans cet ordre, tous en **1 112 × 732 px**, avec l’origine en haut à gauche :

| Fichier dans `Calques/` | Usage |
| --- | --- |
| `00-Parchemin-1112x732.png` | Fond nu ×2, sans retouche |
| `01-Continents-et-eaux.png` | Silhouettes, couleurs des biomes, rivières, lacs |
| `02-Courants-et-voiles.png` | Petites gravures marines |
| `03-Reliefs-et-forets.png` | Montagnes, dunes, arbres et reliefs |
| `04-Lieux.png` | Ensemble des emblèmes de lieux |
| `05-Nuages.png` | Nuages décoratifs fixes |

Les sentiers de la planche de Réverie sont dans `06-Sentiers-Reverie.png` et se placent **entre les reliefs et les lieux**, uniquement si souhaité. Chaque lieu a aussi son PNG transparent dans `Calques/Miniatures/`. `Calques/Atlas.json` donne sa position, son rectangle de placement et sa miniature. Dans ce JSON, les marges droite et basse des rectangles sont exclusives. Multiplier toutes les coordonnées par 5 pour le grand PNG.

`Sources/Fond-nu-original.png` est la copie à l’identique du PNG `Fond-nu-EoS-556x366.png`, SHA‑256 `67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3`. C’est le parchemin approuvé, non présenté comme une extraction attestée de la ROM. Les nouvelles terres et les miniatures sont entièrement séparées de ce fond. Aucun fichier de jeu n’est modifié par le kit.

## Recompiler

Depuis le dossier du kit, avec Python et les dépendances de `Sources/requirements.txt` :

```sh
python Sources/Dessiner.py
python Sources/Autonome.py
python Sources/Verifier-images.py
```

La géographie est dans `Sources/Geographie.json`, les dessins des miniatures dans `Sources/Miniatures.py`. Pour retoucher la carte, modifier ces sources avant de relancer le rendu. Les scripts de rendu n’accèdent pas au réseau et n’utilisent pas de ROM. Les résultats des tests image et navigateur sont dans les JSON `Verification-*`.
