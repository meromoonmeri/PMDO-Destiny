# Chaînes de l’escalier nord — Destiny

**`Tilesheet-Chaines-Escalier.png`** est une planche PNG transparente à l’échelle 1× : **192 × 112 px**, 8 pièces en 4 colonnes × 2 rangées. Chaque case fait 48 × 56 px (6 × 7 tuiles de 8 px). Les pièces sont détourées et centrées ; les marges sont transparentes. Garder l’échantillonnage « plus proche voisin » pour afficher la planche agrandie.

| Rangée | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Haut | Potelet de pied | Anneau mural | Chaîne droite de palier | Ombre de pied |
| Bas | Chaîne en montée gauche | Chaîne en montée droite | Barrière gauche montée | Barrière droite montée |

`Index-tilesheet.json` indique la case, le rectangle exact et les repères de chaque pièce. `Calques/` contient les 8 PNG individuels. Les barrières assemblées font 21 × 49 px ; placer les origines gauche et droite aux coordonnées **(210, 98)** et **(281, 98)** sur le plan natif de l’Accueil (512 × 384 px).

Dans **`../Guilde-Destiny-Bourgeons-PMD.html`**, la section **Deux chaînes pour la montée** montre le gros plan et le tilesheet. **Voir dans l’Accueil** ouvre le plan complet ; **Chaînes : avec / sans** permet de vérifier le calage. Les chaînes montent des deux potelets du palier jusqu’aux anneaux fixés dans les montants de l’arche. Le passage `EscalierNord` reste libre sur ses 48 px. Le tapis et le halo du seuil sud ne bougent pas. Les chaînes sont fixes, non lumineuses et suivent les quatre ambiances.

**Référence :** [G01P01A2 — guilde de Grodoudou, façade fermée](https://projectpokemon.org/home/gallery/image/77345-g01p01a2png/). Les chevalets d’origine ont du bois doré et des attaches sombres ; les garde-corps à maillons inclinés sont une adaptation à Destiny, pas une extraction canonique. Potelet et maillons ont été générés comme sprites séparés, puis détourés, recalés et assemblés avec des ancrages précis.

Graphismes et aperçu seulement. Aucun changement des plans natifs, des collisions ou des fichiers de jeu. Pour reconstruire depuis les deux PNG dans `Maitres/`, lancer `python Chaines-Grodoudou/Sources/Assembler.py` depuis la racine de la guilde, après l’assemblage du seuil sud.
