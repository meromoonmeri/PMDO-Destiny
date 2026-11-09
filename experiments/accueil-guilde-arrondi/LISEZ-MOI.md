# Accueil de guilde arrondi — proposition

Nouvel accueil vide généré en s'inspirant de la disposition de l'accueil de Spinda : salle arrondie, escalier central au nord, passage sud continu, fenêtres et grille relevable devant l'escalier. Les images des maisons Normale, Roche et Plante de Métano ont servi de références d'ambiance et de matériaux ; le dessin est une réinterprétation générée, pas une copie fidèle de leurs textures natives. Aucun mobilier, personnage ou plante n'est posé.

- `accueil-guilde-passage-ouvert.png` : proposition générée retenue, grille relevée et passage visible.
- `accueil-guilde-grille-relevee.png` : premier essai, conservé avant correction des passages.
- `grille-levante-essai.png` : aperçu animé de la grille (590 × 456, 25 phases enregistrées dont pauses). La grille est détourée de l'image ; les barreaux supérieurs ont été prolongés et la cavité derrière elle est reconstituée artificiellement. L'animation est un test visuel, non un sprite natif ou une animation Grodoudou authentifiée.
- `grille-ouverte-essai.png` / `grille-fermee-essai.png` : états du test animé.
- `animer-grille.py` : reconstruction reproductible (Pillow, NumPy, OpenCV). Le détourage et le fond restent à améliorer pour une production finale.

L'image est aplatie et sa lumière est peinte dans le sol. Elle n'est pas encore un tileset multicalque, une carte Tiled ou un Ground PMDO ; les collisions, l'ouverture effective, les transitions et les autres salles arrondies restent à faire. Aucune carte de jeu ou sauvegarde n'a été modifiée.
