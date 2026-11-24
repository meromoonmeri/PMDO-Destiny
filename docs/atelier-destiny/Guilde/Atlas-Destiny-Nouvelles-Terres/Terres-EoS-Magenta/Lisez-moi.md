# Destiny — terres séparées, texture EoS

Cette planche contient **les terres seules**, sans parchemin, quadrillage, cadre, nuage ni texte. La clé est du **magenta RGB 255, 0, 255 (#FF00FF)**, sans dégradé ni couleur voisine autour des côtes. Le tracé est celui des *Nouvelles Terres* validé : quatre continents, Réverie, trois îles aux Haltes et dix-huit îlots satellites.

## Fichiers prêts à placer

- `Planche-Terres-EoS-Magenta-5560x3660.png` : planche entière, agrandie ×5 sans interpolation.
- `Terres-EoS-Magenta-1112x732.png` : planche à l’échelle de placement d’origine.
- `Terres-EoS-Transparent-1112x732.png` : la même planche en RGBA, prête à poser sur un fond séparé.
- `Terres-separees/` : chaque continent, Réverie, l’archipel des Haltes et les îlots, en deux fichiers équivalents **magenta / transparent**.
- `Replacer-les-terres.json` : ancres haut-gauche de chaque PNG, rectangles (droite et bas exclusifs) et coordonnées des lieux validés. Origine de la planche : haut-gauche, à l’échelle 1 112 × 732 px. Multiplier les ancres et dimensions par cinq pour la grande planche.

## Rendu

Les terres ont été générées séparément à partir des contours validés et de références *Explorateurs du Ciel*, puis recadrées sur les masques d’origine. La finition reprend la palette des terres ocre, les hachures visibles et la trame de petits reliefs à l’échelle DS. Elle combine l’art généré, cinq petits prélèvements de matière à l’intérieur des terres de la référence et des motifs placés sur les crêtes et bois de Destiny. **Aucune île ni aucun arrangement géographique d’EoS n’est repris.** Les Haltes utilisent trois détails peints de la génération, chacun remis dans son île d’origine. Les illustrations ne sont pas des captures de la carte du jeu.

- **Orival** : crêtes et terrasses dorées, bois verts, arbres cuivrés, vallées humides.
- **Séracine** : massif enneigé, cèdres aux piémonts, plateau chaud et rocheux à l’est.
- **Estrel** : grand bassin turquoise, forêt riveraine, prairies et salines claires.
- **Torselune** : grès roux et canyons, oasis boisées, dunes et terrains salés.

La version précédente et ses fichiers game/atlas restent inchangés. Le JSON `Verification.json` consigne les contrôles de la clé chroma et du recalage exact des silhouettes.
