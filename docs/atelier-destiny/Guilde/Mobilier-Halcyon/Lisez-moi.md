# Destiny · Mobilier de Halcyon

**490 variantes pixel art, à leur taille native.** Le kit rassemble 49 silhouettes distinctes en dix palettes. Les découpes viennent des cartes de Halcyon, pas d’une banque PMU ni d’une génération d’image.

| Provenance | Modèles | Variantes |
|---|---:|---:|
| Guilde de Halcyon | 42 | 420 |
| Auberge de Metano, dans le même mod | 7 | 70 |
| **Total** | **49** | **490** |

Pièces principales : table de banquet et son tapis séparé, comptoir à cloche, bureau aux parchemins, trois coffres et un coffret, piles de caisses, tonneau, couchage en paille, bannières et tapis tissés, tableau des missions, plantes et accessoires. Le rayon Metano comprend entre autres le banc fleuri, la table sur souche et la grande paillasse. Chaque silhouette se décline dans **Lierre, Minuit, Miel, Ronce, Brume, Mousse, Braise, Lin, Rivière et Bruyère**.

## Dans l’atelier

1. Ouvre **`Guilde-Destiny-Mobilier-Halcyon.html`** (fichier autonome, fourni séparément du kit). Il démarre sur **Mobilier Halcyon**. Choisis une palette, un rayon, un type d’objet ou une recherche.
2. Ouvre une fiche pour comparer les dix teintes, retrouver les couleurs originales ou télécharger le PNG sélectionné. L’exemple dans le Réfectoire est une démonstration : rien n’est encore placé dans ton plan.
3. Choisis une salle et clique sur **Choisir pour la pose**. Clique ensuite sur le plan ou utilise **Poser au centre**. Une pièce déjà placée peut changer de teinte depuis son panneau, sans changer de coordonnées. Annuler/Rétablir inclut ces changements.
4. **Exporter → Plan de l’atelier** garde les placements en JSON. **Image de la salle** rend le PNG avec l’ambiance choisie. Pour reprendre un projet de l’aperçu Bourgeons, exporte son JSON puis utilise **Ouvrir un plan** dans ce nouvel atelier. Les projets sauvegardés localement restent distincts entre les deux aperçus.
5. Avec **Visiter de nuit**, les passages gardent l’ambiance Nuit et la lueur de la verdure. Les 15 plans, 29 passages, 7 cadres sud et la grille verrouillée jusqu’à sa levée sont conservés.

**Aperçu et kit graphique seulement.** Aucun objet n’est préposé dans ton projet ni installé dans le jeu. Le bouton de copie native `.rsground` est désactivé dans une salle dès qu’elle contient une variante d’atelier. Dans l’aperçu intégré, si le navigateur bloque un téléchargement, ouvre directement le fichier HTML dans ton navigateur, ou prends le PNG correspondant dans le ZIP.

## Dans le kit ZIP

- **`PNG-1x/<palette>/<modèle>.png`** : les 490 variantes individuelles RGBA, rognées à la taille du sprite, sans fond ni agrandissement.
- **`Atlas-1x/`** : une planche RGBA par palette, 1 344 × 784 px, 7 × 7 cases de 192 × 112 px. `rect_atlas` donne le rectangle exact du sprite, en pixels depuis le coin haut gauche (x, y, largeur, hauteur). La planche de comparaison, en revanche, est une image de présentation sur parquet et non un atlas de jeu.
- **`Index.json` et `Index.csv`** : dimensions, palette, provenance et coordonnées dans les cartes Halcyon. Le CSV est en UTF‑8 (BOM) et séparé par des points-virgules. Le JSON donne aussi les empreintes SHA‑256 et les règles de découpe.
- **`Originaux-1x/`** : 49 références des découpes originales en couleurs Halcyon, en dehors du décompte des variantes.
- **`Sources/Palettes.json`** : nuances de bois, de textile, de métal et de feuillage, du sombre au clair. `Sources/Modeles.json` et `Sources/Provenance-brute.json` fixent les sources. Les ombres semi-transparentes et l’alpha d’origine des découpes sont conservés. Le bois, les étoffes, les métaux et les plantes ne sont pas recolorés d’un seul filtre.
- **`Planche-10-Palettes.png`** : dix modèles présentés dans chacune des dix palettes sur un extrait du parquet du Réfectoire.

## Crédits et provenance

- **[Halcyon](https://github.com/Palikadude/Halcyon)** est un mod de Palika pour PMDO. Le [README du projet](https://github.com/Palikadude/Halcyon#spriting-credits) crédite D4yz pour les tuiles et ornements intérieurs originaux, et Edan Momu pour l’extérieur et une partie des intérieurs de la guilde.
- Révision source : [`da6c2130d641507447e6386a5e47a296e8cb4c71`](https://github.com/Palikadude/Halcyon/tree/da6c2130d641507447e6386a5e47a296e8cb4c71). Les meubles de guilde viennent des calques d’objets `guild_*`; les sept pièces de Metano viennent de `metano_inn`. Ni les cartes complètes ni les `.tile` bruts ne sont inclus dans le kit. Les droits sur les sprites d’origine restent à leurs auteurs ; vérifie leurs conditions d’utilisation avant redistribution.

## Régénérer et vérifier

Avec Python, Pillow, NumPy et SciPy, `Sources/Prelever.py --telecharger` retrouve les sources du commit épinglé et vérifie leurs empreintes. Les PNG d’origine étant déjà présents, `Sources/Fabriquer.py` suffit pour refaire les variantes et les atlas. Dans le dossier de travail, `Sources/Assembler.py` intègre le kit dans une copie de **Bourgeons PMD**, puis `Sources/Planches.py` refait la planche de comparaison. L’assembleur refuse de réécrire le fichier de référence. `Sources/Verifier.cjs` contrôle le catalogue et la pose avec Playwright. Les deux rapports de vérification résument les contrôles graphiques et navigateur.
