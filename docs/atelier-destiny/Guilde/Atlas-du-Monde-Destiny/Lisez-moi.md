# Le monde de Destiny — sans texte

- **`Monde-Destiny-Sans-Texte-6144x4608.png`** : le monde entier sur parchemin, en pixel art. Grille de dessin de 1 536 × 1 152 px, agrandie 4× au voisin le plus proche. Les continents, îles, forêts, reliefs et petits lieux restent dessinés ; aucun nom n’est incrusté.
- **`Reverie-Et-Ses-Donjons.png`** : gros plan de la zone de départ. Au centre, Réverie Town (maisons et pont). Plus haut à droite, Fosse Cascade (chute d’eau). Au sud-ouest, Passage Aquatique (arche dans la crique). Bois Perdus est à l’ouest et la guilde au nord. Les trois donjons sont sur la même côte à moins de 53 pixels du pivot de Réverie, à l’échelle de dessin.
- **`Monde-Destiny-Devoilement.mp4`** : 27 secondes, sans texte ni son. Le film dévoile d’abord la région de Réverie, puis recule pour révéler le monde. Les nuages gravés, les éclats et les huit poses d’eau gardent le même style de carte. Aucun aperçu interactif n’est requis.
- **`Reperes-separes.json`** : index facultatif des lieux, ancres et sentiers. Les noms sont séparés des images. Les ancres Destiny sont une proposition de maquette, pas des coordonnées canoniques ni un nouveau raccord de jeu.

## Recomposer

Compositing à 1× : `Parchemin-relief` → `Reliefs-et-forets` → `Sentiers-et-ruisseau` → `Lieux-Destiny`. Les cinq emblèmes ont leur PNG transparent ; les trois symboles croqués avec le générateur ont été détourés et adaptés à la palette du parchemin. `Carte-non-devoilee` et `Nuages-graves` contiennent la couverture et sa gravure indépendantes. `Eau-*-8-poses.png` : quatre colonnes, deux rangées, ordre de lecture, un huitième de seconde par pose. `Sources/Animer.py` lit ces calques et l’index pour reproduire le film avec Pillow, NumPy et ffmpeg.

Inspirations : [Eddy’s Lab — World Map](https://eddyk28.github.io/PMD%20Map/) pour les repères, [plan PSMD extrait et assemblé sur Project Pokémon](https://projectpokemon.org/home/gallery/image/74067-world-map/) pour le relevé des côtes, et les planches *Explorateurs du Ciel* fournies pour le vocabulaire pixel art et le dévoilement. Ce projet de fans n’installe rien dans Destiny.
