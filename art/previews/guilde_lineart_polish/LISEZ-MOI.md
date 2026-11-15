# Salles de la Guilde — réponse au retour « trait épais, couleurs plates »

> « The lineart is a bit thick and the colors are a bit flat. Since the colors are
> so light, if you want to polish it up, you can reuse stuff from the rest of the
> palette, I think. Though, if not, I think it's fine! It already looks quite good »

Le retour est juste, et mesurable. Voici ce que j'ai trouvé et ce que j'ai fait.

## Ce que disaient les pixels

Mesures sur les 11 bases 1x des salles (`01_accueil` … `11_chambre_heros`) :

| Mesure | Valeur |
|---|---|
| Épaisseur réelle du trait (pixels de trait ÷ longueur de la ligne médiane) | **1,61 px** |
| Part du dessin occupée par le trait sombre | 4,9 % à 10,8 % selon la salle |
| Couleurs distinctes | 192 |
| Pixels au-dessus de 190 de luminance | **1,9 %** |
| Pixels entre 150 et 170 de luminance | 24,1 % |

Deux constats :

1. **Le trait est trop épais.** Il fait 1,6 px en moyenne alors que le pixel art de
   cette résolution travaille en 1 px. Sur une forme qui tourne, ça se voit
   immédiatement : les courbes épaississent et le dessin « colle ».
2. **Les couleurs sont plates parce que la palette est mal répartie**, pas parce
   qu'elle manque de teintes. Il y a 192 couleurs, mais un tiers d'entre elles sont
   collées dans une seule tranche de luminance (150–170) : le bois du mur, le sol et
   les racines ont le même poids visuel. Et seulement 1,9 % du dessin dépasse 190,
   donc presque aucun point lumineux pour accrocher l'œil.

## Ce que fait le correctif

`tools/polish_guilde_trait.py`, sur les 11 bases 1x :

1. **Amincissement du trait** par ligne médiane (`skeletonize`), limité aux
   structures de 4 px et moins — les masses sombres volontaires (intérieur des
   arches, creux des racines) ne sont pas touchées.
2. **Le pixel libéré reprend l'aplat qui le borde** (le plus proche dans un rayon
   de 2). Ce point a demandé deux essais : ma première version y mettait
   systématiquement un cran d'ombre, ce qui glissait un liseré sombre dans les
   vitraux et les rendait plus foncés qu'avant — l'inverse du but.
3. **Aucune couleur inventée.** Le cran d'ombre et le cran de lumière sont choisis
   parmi les couleurs déjà présentes dans la salle : la sortie ne contient que des
   teintes de la palette d'entrée. Vérifié automatiquement (compteur `nouvelles`,
   à 0 sur les 11 salles).

J'ai aussi essayé un biseau d'un pixel sur les aplats pour le relief : je l'ai
**désactivé**. Le gain de contraste local était nul (94,38 contre 94,14 sur
l'écart-type du laplacien) et il cassait les détails fins, notamment les anneaux
de corde des piliers. Le paramètre reste disponible via `--bevel`.

## Résultat

| | Avant | Après |
|---|---|---|
| Épaisseur du trait | 1,61 px | **1,04 px** (−35 %) |
| Couleurs | 192 | 166–178 |
| Couleurs inventées | — | **0** |
| Pixels de trait (Accueil) | 10 184 | 6 398 |

Le dessin, les formes, les couleurs et les positions ne bougent pas : seule
l'épaisseur du contour change, et les quelques pixels récupérés prennent la teinte
du bois adjacent.

## Fichiers

- `1_planche_11_salles_avant_apres.png` — les 11 salles, avant / après
- `2_zoom_echelle_jeu_x3.png` — zoom à l'échelle réelle du jeu (la banque de
  l'Accueil est en 3× : 1536×1152 px pour une base de 512×384)
- `3_zoom_accueil_salon_refectoire.png` — Accueil, Grand Salon, Réfectoire en 2×
- `*_1x_base.png` — les 11 bases corrigées, prêtes à être recompilées
- `polish_guilde_trait.py` — le script, reproductible (`--check` pour mesurer)

## Pour appliquer en jeu

Le pipeline existant lit ces bases et régénère les banques `.tile` :

```bash
cp guilde_lineart_polish/*_1x_base.png \
   guilde_destiny_reseau/cartes_base_sans_decors/
python3 tools/build_guilde_destiny_reseau.py
```

Je n'ai pas encore touché au dépôt : les fichiers sont livrés ici pour que tu
valides le rendu d'abord. Dis-moi si tu veux que je pousse, ou si tu préfères
un trait encore plus fin sur certaines salles.
