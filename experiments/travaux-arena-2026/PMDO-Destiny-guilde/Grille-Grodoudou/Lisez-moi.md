# Grille levante de l’Accueil

La grille ferme **toute l’ouverture de l’escalier nord**. Dans **`../Guilde-Destiny-Bourgeons-PMD.html`**, choisis **Lever la grille** dans le premier panneau. Les barreaux remontent derrière l’arche, puis **Franchir l’escalier** devient disponible. Le même contrôle est accessible dans l’atelier, à côté des passages. Il faut attendre l’ouverture complète ; une grille baissée bloque le passage dans les deux sens, entre l’Accueil et la salle des missions. On peut ensuite l’abaisser. Si l’appareil demande des mouvements réduits, le changement de position est immédiat.

Les rambardes latérales de la proposition précédente ne sont plus affichées. Une ombre placée **derrière** la grille atténue les lignes du fond et prolonge visuellement l’escalier vers un passage en retrait. Le calque `Calques/Ombre-Interieure.png` ne modifie que l’intérieur de l’arche ; le bois, les marches du bas, le tilesheet de la grille et le seuil sud gardent leur dessin et leur position. Les quatre ambiances et le comparatif vidéo sont conservés. Le verrou est simulé dans l’aperçu : ni les fichiers du jeu, ni les collisions ou les destinations natives ne sont modifiés.

## Tilesheet

**`Tilesheet-Grille-Escalier.png`** : PNG transparent de **256 × 320 px**, seize cases de **64 × 80 px**, de gauche à droite puis de haut en bas. Positionner le coin supérieur gauche de chaque case à **(224, 64)** sur la carte 512 × 384 de l’Accueil. L’image d’indice 0 est fermée ; l’image 15 est transparente parce que la grille est entièrement escamotée. Lire à **15 i/s** pour une levée en une seconde, ou inverser la séquence pour la descente. `Index-Tilesheet.json` détaille les 66 px de course et les ancrages. `Calques/` contient les principales poses PNG ; `Maitres/Grille-metal.png` est le sprite généré puis détouré avant raccord à l’arche.

## Référence et montage

La [façade fermée G01P01A2](https://projectpokemon.org/home/gallery/image/77345-g01p01a2png/) montre les barreaux métalliques et leur traverse. La [façade ouverte G01P01A](https://projectpokemon.org/home/gallery/image/77344-g01p01apng/) montre le passage sans grille. La grille adaptée a été générée d’après cette référence, puis translatée derrière le contour de l’arche de Destiny. Les deux cartes source sont statiques ; l’animation de levée a été créée pour l’aperçu.

Pour réassembler l’aperçu, lancer `python Grille-Grodoudou/Sources/Assembler.py` depuis le dossier de la guilde, après l’assemblage du seuil sud. Pour la finition de l’arche et des rives, lancer ensuite `python Bourgeons-PMD/Sources/Assembler-raccords.py`. Les images originales et le sprite détouré suffisent ; il n’est pas nécessaire de relancer le générateur.
