# Destiny — Terres dans la DA de la carte du monde DS

Cette version repart du **layout Nouvelles Terres validé**. Le terrain est une nouvelle génération d’image dédiée à Destiny, avec pour référence principale le rendu de la carte du monde d’*Explorateurs du Ciel* (`S01P01A`), plus le détail fourni par le joueur. Les côtes et les emplacements ne viennent pas de cette référence. Le dossier `Etude-Style-Guildhouse` reste un essai séparé ; ses illustrations aux arbres et falaises plus grands n’ont pas été reprises ici.

L’image d’ensemble a été générée en utilisant la géographie de Destiny comme gabarit. Les motifs ont été ramenés à l’échelle de travail 556 × 366 : collines ocre en groupes de petits losanges, bosquets d’arbres pointus, pierre jaune, petites touches de neige et d’eau. L’arbre de Réverie vient d’une seconde génération de détail, puis a été détouré et placé dans le virage de la rivière, sur la terre, à l’ancre `(150, 551)`. Le tracé de cette seconde génération n’a pas été conservé.

## Choisir le fichier

- `Destiny-Style-DS-Magenta-1112x732.png` : planche de placement, sans parchemin, texte ou pictogrammes d’interface. Chroma **`#FF00FF`** exact à l’extérieur des terres.
- `Destiny-Style-DS-Magenta-5560x3660.png` : agrandissement ×5 sans interpolation pour lecture des détails.
- `Destiny-Style-DS-Transparent-1112x732.png` : même premier plan en PNG RGBA, sans besoin d’incrustation chroma.
- `Reverie-Style-DS-Apercu.png` : zoom de l’île de départ sur fond magenta.
- `Terres-separees/` : Orival, Séracine, Estrel, Torselune, Réverie, Les Haltes et les 18 satellites (groupe), chacun sur magenta et transparent. Deux sous-dossiers donnent aussi les **trois Haltes et les 18 satellites en fichiers individuels**.
- `Replacer-les-terres.json` : origine `(x, y)` et taille de chaque découpe dans le plan 1112 × 732. Les limites hautes du rectangle sont exclusives. Assembler les sept groupes **ou** décomposer les Haltes et les satellites, sans doubler les deux ensembles.
- `Calques/` : masque des eaux et index des terres de placement. Dans l’index : 0 = extérieur ; 1 à 6 = régions ; 101 à 118 = satellites. Les eaux intérieures restent dans le premier plan, sur les terres.

Les 34 emplacements restent dans le fichier de placement. Les huit noms connus sont distingués par `existe_dans_le_projet` ; leurs positions cartographiques restent des propositions. Ils ne sont pas des libellés peints sur le rendu.

## Contrôles

`Verification.json` décrit le contrôle des 26 silhouettes, du chroma et de la recomposition pixel à pixel des sept groupes. Les côtes et les empreintes des eaux proviennent des masques du layout approuvé, pas de l’interprétation du générateur. Ces contrôles vérifient la géographie et les formats ; ils ne prétendent pas que l’art est un asset officiel ou une extraction du jeu.
