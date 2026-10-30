# Waterfall Village — amélioration de la partie sud

Point de départ : le fichier **du Drive de l'auteur**
(`WaterfallVillageCapital.rsground`, 330 233 300 octets, sha256
`2268e269…4a446a`, 37 calques, 200 × 500 cases de 8 px). C'est la base de
travail retenue ; la version `town02` et les essais intermédiaires sont écartés.

Consigne appliquée : **ne pas remplacer le sud par une copie du village du
nord**. La plaine d'herbe et ses arbres sont conservés tels quels ; on n'ajoute
que des **chemins**, et on corrige les raccords.

---

## 1. Ce qui n'allait pas

1. **Les chemins s'arrêtaient net.** Les deux ponts de bois qui franchissent la
   rivière (lignes 351-355) débouchaient sur le gazon : les chemins descendaient
   à la ligne 368 puis s'interrompaient, laissant 130 lignes de plaine sans
   aucune voie.
2. **Les deux rives ne communiquaient pas.** Rien ne reliait le chemin du pont
   ouest (tx 11-14) à celui du pont est (tx 86-89) : il fallait traverser
   72 cases d'herbe.
3. **Des amorces orphelines.** Les tronçons déjà posés au sud de la rivière
   s'arrêtaient sur un embout, sans destination.

Le défaut n'était donc pas l'absence de contenu au sud — la plaine et ses
arbres sont voulus — mais l'**absence de circulation**.

---

## 2. Le problème technique à résoudre

Les chemins du nord sont dessinés avec trois planches (`INVERSEPATHWAY`,
`CanyonCamp`, `Metano_Town_Base`) réparties sur les calques **1, 3, 24, 26,
27, 32 et 33** — la répartition n'est pas régulière, et le calque 33 ne contient
que des **fragments** (509 cases isolées), ce qui exclut d'en déduire une règle
d'auto-jointure à partir des quatre voisins : la table testée
(`tools/chemins.py`) s'est révélée non déterministe, l'hypothèse a été
abandonnée.

Autre contrainte : tout le sud est couvert par un **remplissage de gazon**
(calque 27, `Altere_Pond_Cliffs` @ 106,5) posé *au-dessus* des calques 1 à 26.
Écrire un chemin dans ces calques ne produirait rien de visible : le gazon le
recouvrirait.

Solution retenue : **recopier des tronçons natifs complets** (chaussée + berges,
toutes couches confondues) dans le **calque 33**, celui que l'auteur utilise
déjà pour les amorces sous les ponts et qui passe au-dessus du remplissage.
Aucune tuile inventée, aucune planche ajoutée, aucune retouche du gazon.

---

## 3. Ce qui a été fait

Script : `tools/dessiner_chemins.py` (reproductible, voir § 6).

| Tronçon ajouté | Empreinte d'origine | Calque source | Cellules |
|---|---|---|---|
| Route du pont ouest, de ty 356 au bord sud | tx 9-16 × ty 336-349 (7 × 13) | 26 | ~ 1 100 |
| Route du pont est, de ty 356 au bord sud | tx 84-91 × ty 336-349 (7 × 13) | 3 | ~ 1 100 |
| Route est-ouest, sur toute la largeur, ty 427-431 | lignes 196-200, tx 40-90 (50 × 5), sans aucun trou | 1 (`WaterfallVillage-base`) | ~ 210 |

Les empreintes sont prises **juste au nord des ponts**, là où les chemins font
3 à 4 cases de large : c'est exactement la largeur des amorces déjà présentes au
sud, donc le prolongement ne crée pas de rupture d'échelle. Les répétitions se
chevauchent de 6 cases pour que les embouts arrondis ne laissent pas de coupure.

Enfin, les **buissons qui empiétaient sur les nouveaux chemins ont été retirés
en entier** (composante connexe complète, jamais un demi-buisson) : 1 514 cases
sur les calques d'objets.

Bilan des calques modifiés — et de ceux qui ne le sont pas :

```
calque 33 : 2 119 → 4 545 cases   (+2 426)
calque 34 : 7 568 → 6 054 cases   (-1 514)
tous les autres calques : inchangés à l'octet
```

Aucune zone existante n'a été réécrite, aucun arbre de la plaine n'a été
déplacé hors des emprises de chemin, aucune case de gazon n'a été remplacée.

---

## 4. Contrôles passés

- **Réécriture à vide identique à l'octet** :
  `python tools/editer_ground.py <fichier> --verifier` → `IDENTIQUE`
  (sha256 `867a90e7…c56777`).
- **Taille** : 330 315 007 octets (+ 81 707).
- **Relecture de l'archive** : `gzip.decompress()` du `.gz` livré redonne
  exactement le fichier ci-dessus.
- **Aperçu** : rendu hors-moteur complet (`docs/apercus/avant_apres_chemins.png`).

---

## 5. Limites assumées

- **Aucun aperçu ne vaut validation en jeu.** Il reste à charger la carte dans
  PMDO 0.8.12 et à marcher les trois chemins pour vérifier le passage.
- **Collisions** : la grille `obstacles` du fichier est uniforme (200 × 500
  entrées `{"Bounds": …, "Tags": 0}`) — elle ne porte aucune information de
  blocage par objet. Aucune n'a donc été modifiée : les buissons retirés
  n'étaient pas, dans ce fichier, des obstacles déclarés.
- **Motif répété** : la route est-ouest reprend le même tronçon de 50 cases ; à
  fort grossissement, les petites décorations (cailloux, touffes) se répètent.
  C'est le prix d'une texture 100 % native — aucune retouche peinte n'a été
  introduite.
- **Rien n'a été ajouté au sud en dehors des chemins** : pas de bâti, pas de
  nouvel objet, pas de nouvel ennemi. La plaine reste la plaine, comme demandé.

---

## 6. Reproduire

```bash
python tools/restaurer_waterfall.py          # remet le .rsground depuis le .gz livré
# ou, depuis le fichier du Drive intact :
python tools/dessiner_chemins.py <drive.rsground> <sortie.rsground>
python tools/editer_ground.py <sortie.rsground> --verifier
```

`tools/dessiner_chemins.py` ne dépend que de `tools/editer_ground.py` (numpy
inutile) et n'écrit que dans le calque 33.
