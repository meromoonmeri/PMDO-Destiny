# Destiny · Les objets PMU dans les huit sens

**346 objets de la banque PMU de Destiny 0.7.7 · 2 768 PNG**, auxquels s’ajoutent **4 modèles inédits** (32 PNG) et **10 créations déjà présentes dans Destiny** (80 PNG). Le coffret contient donc **360 modèles et 2 880 vues individuelles**.

## Voir ou récupérer un objet

1. Décompresse `Kit-Destiny-PMU-8-orientations.zip` en entier.
2. Ouvre **`Catalogue.html`** dans ton navigateur. Il est local, sans serveur ni Internet. Recherche par nom ou code — par exemple `Mob_017` ou `grainothèque` — et sélectionne l’orientation. **Tourner** fait défiler les huit vues au même pivot.
3. **Ouvrir ce PNG** affiche la vue sélectionnée dans un nouvel onglet (clic droit → enregistrer si besoin). **Ouvrir l’atlas 4 × 2** affiche les huit vues sur une même planche transparente. Tu peux aussi aller directement dans `PNG/<code>/` ou `Atlas-4x2/`.

| Rangée de l’atlas | Colonne 1 | Colonne 2 | Colonne 3 | Colonne 4 |
|---|---|---|---|---|
| 1 | `Down` ↓ | `DownRight` ↘ | `Right` → | `UpRight` ↗ |
| 2 | `Up` ↑ | `UpLeft` ↖ | `Left` ← | `DownLeft` ↙ |

**`Index-PMU-8.csv`** : une ligne par PNG, avec dimensions, pivot et position de la vue dans l’atlas. **`Index-PMU-8.json`** : même inventaire, gabarits et provenance, recadrage et empreintes SHA-256. La petite vidéo et la planche illustrent une sélection ; le coffret couvre toute la banque retenue.

## Échelle et placement

- PNG RGBA à l’échelle **1×**, avec un pixel pour un pixel. Dans Destiny, une tuile logique mesure **8 × 8 px**. Pour agrandir, utilise le **voisin le plus proche**.
- Le pivot `[x, y]` est lu depuis le coin haut gauche du PNG. Place ce point sur le sol, à la même coordonnée d’une direction à l’autre : pour poser à `[X, Y]`, utilise `[X − x, Y − y]` comme origine de l’image. Pour un tapis, c’est le centre. Pour un objet mural ou une forme en U, il peut tomber sur une partie transparente ou juste en dehors du recadrage.
- Dans chaque atlas, le pivot est commun aux huit cases. Rectangle et pivot exacts dans le JSON : `atlas.cellule`, `atlas.pivot_case` et `vues[].rectangle_atlas`. `ligne_de_sol` est un repère indicatif relatif au pivot, **pas une collision**.
- **Ce coffret n’installe rien dans le jeu.** Ce sont des PNG, pas des fichiers `.dir` prêts à insérer. Aucun accès de salle, thème, atelier précédent ou fichier de sauvegarde n’a été modifié.

## D’où viennent les vues ?

- **Banque PMU :** 128 meubles `Mob`, 41 objets `Cpt`, 80 décors `DecA`, 62 décors `DecB`, 33 sprites `Guilde_Imm_pmu_*` et 2 accessoires `PMU_*`. Tous sont issus de `Content/Object` de la publication Windows Destiny 0.7.7. Les tuiles qui ne sont pas des sprites d’objets indépendants et les ressources qui n’ont jamais été intégrées à Destiny ne sont pas dans ce coffret. Des variantes graphiques proches ont été conservées quand elles existent sous deux ressources distinctes.
- **Face de référence (`Down`) :** image du `.dir`, recadrée par transparence et convertie en RGBA lisible. Les objets dessinés de biais dans les sources restent de biais dans cette vue. Aucun changement graphique dans cette direction (en dehors de la conversion d’alpha).
- **Sept angles complémentaires :** dessin numérique par volumes à partir de la silhouette, de la palette et des détails visibles. Les profils et dos sont *reconstitués* : le jeu ne fournissait qu’une seule pose. Les 65 éléments plats restent sur le plan du sol ; plusieurs orientations peuvent paraître identiques pour un motif symétrique. Des fichiers d’origine contiennent plusieurs accessoires ; ils restent groupés dans le catalogue.
- **Nouveautés :** Pupitre aux cartes, Chariot à thé, Grainothèque et Horloge lunaire. Études générées, détourées puis ramenées à l’échelle du jeu. Leurs faces non visibles ont été reconstruites dans le même style. Les 10 anciens modèles générés sont séparés sous « Bonus existants ».

Crédits : banques historiques **PMUniverse / PMU-Client**, adaptées dans les ressources de **PMDO Destiny 0.7.7**. Les noms et SHA-256 des sources sont repris dans le JSON et `Inventaire-sources-PMU.csv`.
