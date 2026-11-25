# Destiny — Atlas des 150 lieux

**Aperçu interactif dans Arena :** choisir **Atlas Destiny · 150 lieux** parmi les aperçus actifs (port 4190). La vue **Monde entier** s’ouvre sur le parchemin, avec les 150 décors. **Départ Réverie** rapproche la carte des premiers chemins. **Dévoiler** joue l’ouverture des nuages à partir du village ; le même bouton met l’animation en pause ou la reprend.

- Glisser la carte, zoomer à la molette, avec `+` et `−` ou en pinçant sur mobile. Au clavier, les flèches déplacent la carte, `+` et `−` zooment et `0` revient au monde entier.
- Cliquer un décor ou le chercher dans l’index. Le filtre **Repères** ajoute uniquement des points pour les résultats courants ; les noms ne sont jamais inscrits dans le dessin. Quand un lieu est choisi, son fragment dans l’URL permet de revenir à la fiche.
- Sur mobile, l’index se trouve sous la carte. Après le choix d’un lieu, le bouton en bas de la carte ramène à sa fiche.

## Fichiers

| Fichier | Utilisation |
|---|---|
| `Apercu/` | Site statique complet. Il ne charge pas de bibliothèque ni de police à distance. |
| `Atlas-Destiny-150-Hors-Ligne.html` | Le même atlas dans un fichier autonome ; ouvrir directement dans un navigateur, sans serveur. |
| `Monde-Destiny-150-Lieux-6144x4608.png` | Carte seule sans texte, agrandie en pixels nets. |
| `Apercu/assets/Lieux.json` | Noms, miniatures, positions, régions et sources ; séparé du dessin. |
| `Verification-carte.json`, `Verification-navigateur.json` | Vérifications des calques, du total, des positions et de l’interface. |

## Les 150 lieux

| Région | Lieux |
|---|---:|
| Côte de Réverie | 5 |
| Continent de l’Eau | 24 |
| Continent de l’Air | 30 |
| Continent de l’Herbe | 32 |
| Continent de la Brume | 28 |
| Continent du Sable | 14 |
| Mer des Merveilles | 14 |
| Continent Mystère | 3 |
| **Total** | **150** |

Les cinq décors validés (Réverie Town, Fosse Cascade, Passage Aquatique, Bois Perdus et falaise de la guilde) gardent leurs silhouettes, positions et chemins. Les 145 autres décors combinent des miniatures de référence, quatre silhouettes détourées issues du générateur d’images (bourg, glace, ruines, volcan) et de nouveaux détails en pixel art. Les lieux ont des sprites distincts ; les reliefs de fond ne sont pas comptés. 32 lieux comportent des variations animées en huit poses.

La géographie suit la carte de [Eddy’s Lab](https://eddyk28.github.io/PMD%20Map/) et le [fond PSMD](https://projectpokemon.org/home/gallery/image/74067-world-map/) extrait par evandixon et assemblé par Levin. Quelques repères sont légèrement décalés pour garder les miniatures lisibles. Ce sont des placements d’atlas, non des coordonnées canoniques de Destiny. Maquette autonome : aucun fichier de jeu n’a été modifié.

## Reprendre le serveur ou reconstruire

Avec Python, lancer depuis ce dossier : `python -m http.server 4190 --bind 0.0.0.0 --directory Apercu`. Le dossier `Apercu/` suffit pour servir le site. `Sources/Construire150.py` reconstruit le graphisme à partir de `Sources/Traits/` et du dossier voisin `Atlas-du-Monde-Destiny` (Pillow, NumPy et SciPy). `Sources/Autonome.py` regroupe les calques et le code dans le fichier autonome. `Sources/VerifierAtlas.py` et `Sources/Tester.cjs` contrôlent la carte et le navigateur ; pour le second script, renseigner si nécessaire `PLAYWRIGHT` et `ATLAS_ORIGIN`.
