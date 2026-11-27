# Comptoirs & falaise — Guilde Destiny 0.7.7

## Dans l’atelier

- **Comptoirs** : choisis une orientation et une salle. L’Accueil, le Réfectoire et la Cuisine proposent chacun huit placements d’exemple. Les exemples ne sont pas enregistrés comme meubles.
- **Essayer dans cette salle** : choisis un emplacement sur le plan, ou clique sur **Poser comme dans l’exemple**. Après la pose, **Orientation du comptoir** conserve son point d’appui si la nouvelle empreinte et son allée restent libres. Un emplacement qui bouche une arrivée ou un passage est refusé.
- **Accueil → Passages → Falaise** : franchis la sortie sud pour voir la vraie carte Cliff. La porte et **Entrer dans l’Accueil** permettent de revenir sans changer d’ambiance. **Nuit** allume les deux braseros ; **Avec braseros / Sans braseros** compare avec le plan d’origine. Les trois autres ambiances gardent les trépieds éteints. Le bouton **Animations** peut figer la vue.
- Le fichier `Guilde-Destiny-Comptoirs-et-Falaise.html` est autonome. Pour exporter depuis un aperçu qui interdit les téléchargements, ouvre le fichier HTML téléchargé dans un navigateur. Les projets sont séparés de ceux des ateliers précédents ; tu peux importer un plan JSON compatible.

## Contenu du kit

| Dossier ou fichier | Contenu |
|---|---|
| `PNG-1x/` | Huit sprites RGBA, transparents, à taille native : `Down`, `DownRight`, `Right`, `UpRight`, `Up`, `UpLeft`, `Left`, `DownLeft`. |
| `Atlas-Comptoirs-1x.png` et `Cases-Atlas.json` | Les huit sprites dans un atlas de 384 × 160 px avec rectangles et pivots. |
| `Index-Comptoirs.json`, `Implantations.json` | Dimensions, point d’appui, empreinte et allée ; 24 positions contrôlées sur les plans. |
| `Braseros/` | Trépieds ouest/est détourés, versions éteintes et quatre poses allumées par côté. Les deux fichiers `*-boucle-nuit.png` sont des PNG animés à 6 images/s. |
| `Falaise/` | Rendus 480 × 520, avec et sans ajout, et calques RGBA pour la mer nocturne, les braseros et leurs reflets. Le relevé précise leurs origines, en pixels. |
| `Planche-Comptoirs.png` | Vues du meuble à 2×, détail de l’extérieur et exemples sur les parquets. |
| `Releve-Cliff.json`, `Provenance-cliff.json` et `Verification-*.json` | Référence des braseros, ressources contrôlées et résultats des vérifications. |

**Ce kit est un aperçu, pas un installateur.** Il ne contient aucune carte `.rsground` modifiée et n’écrit ni dans le jeu ni dans ses sauvegardes. Les 15 salles, leurs intérieurs et la balade nocturne sont conservés. Les braseros et leurs reflets ne sont ajoutés qu’à Cliff.

## Sources

- [Halcyon](https://github.com/Palikadude/Halcyon) — sprite `comptoir-cloche` comme modèle de mobilier (mod de Palika, décors crédités à D4yz et Edan Momu). La forme et les matériaux ont d’abord été explorés avec une étude générée ; les huit images sont ensuite projetées et dessinées par faces à l’échelle 1×. Elles ne sont pas obtenues en tournant ou en retournant un PNG.
- [Grodoudou de nuit, G01P01C, extraction de Pokémon Donjon Mystère : Explorateurs du Ciel](https://projectpokemon.org/home/gallery/image/77577-g01p01cpng/) et [G01P01A de jour](https://projectpokemon.org/home/gallery/image/77344-g01p01apng/) — extraction MegaMinerd, galerie Project Pokémon publiée par evandixon. Les pixels des quatre poses de flamme sont inchangés ; quelques pixels de la patte est masqués par une pierre sont repris sur le trépied ouest. Le reflet sur l’herbe et les racines est propre à cette adaptation.
- [Cliff Destiny, version Windows 0.7.7](https://github.com/meromoonmeri/PMDO-Destiny/releases/download/v0.7.7/PMDO-Destiny-Windows-x64-0.7.7.zip) — terrain, bâtiment, ciel et mer. L’ajout laisse l’axe de la porte, le ciel et la mer intacts à phase égale.

Les auteurs et ayants droit des ressources d’origine restent inchangés ; ce kit ne leur attribue pas de nouvelle licence.
