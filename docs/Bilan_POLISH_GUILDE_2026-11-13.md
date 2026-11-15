# Guilde Destiny — fenêtres 4 ambiances & polish du re-shade

**Branche** : `wip/reverie-integration-kingambit-cafe` · **Commits** : `0e07c46` (fenêtres),
`0f1827d` (taches / parasites / filtre), `120c6c7` (façade + bordure rocheuse + ombres).

Les planches avant/après sont dans `art/guilde_destiny_reseau/polish/`.

---

## 1. Fenêtres & ambiances — 4 variantes par fenêtre

### Le défaut

Dans l'accueil, les 4 ambiances des fenêtres sortaient **quasi identiques** : seuls
**7,6 %** des pixels changeaient entre le jour et la nuit, contre 36 % pour la salle
des missions.

**Cause** — l'ancien générateur classait les pixels « bois » avec une règle de
couleur *et* une comparaison au décor brut de la pièce (`diff < 22`). Or dans
l'accueil le ciel de jour est **crème** et le mur alentour aussi : toute la baie
était classée « bois ». Comme seuls les pixels de verre reçoivent la compensation et
les variantes, l'accueil n'avait **aucune** fenêtre qui changeait — et c'était le cas
des 13 fenêtres, pas seulement l'accueil.

### Le générateur retenu

`tools/refaire_fenetres_ambiances.py` — 56 `.dir` régénérés.

| Avant | Après |
|---|---|
| Bois/verre par heuristique de couleur sur le décor | **Séparation structurelle** : est verre toute composante non-orange (`r − g < 25`) qui **ne touche pas le bord** de l'image. Le cadre et les meneaux touchent toujours le bord → exclus mécaniquement. |
| Ciel conservé avec son dithering d'origine | **Dégradé vertical 4 tons** par ambiance : jour crème, aube rosée, crépuscule braise, nuit étoilée |
| Compensation écrasée quand la teinte de monde était mal détectée | Calcul en **couleur effective** (ce que voit le joueur) puis division par `WorldAmbianceTint` → la vitre ressort sur le mur |
| Cadre modifié dans certains cas | **Cadre DS strictement intact**, alpha intact, rien touché hors du verre |

### Résultat mesuré (luminance effective de la vitre, après filtre moteur)

| Fenêtre | Jour | Aube | Crépuscule | Nuit |
|---|---|---|---|---|
| accueil / Gauche | 163,3 | 137,3 | 102,2 | **52,0** |
| accueil / Droite | 162,1 | 136,5 | 101,7 | **51,9** |
| missions / Gauche | 159,6 | 134,6 | 100,1 | **51,2** |
| dortoir_nord / Centre | 170,6 | 144,0 | 109,1 | **54,4** |
| bureau_maître / Centre | 176,5 | 147,4 | 112,7 | **56,3** |

Décroissance régulière sur les **14 fenêtres** ; les 14 ressortent la nuit (contraste
vitre/salle ≥ 2,3 en moyenne). La pire baie était à **0,93** avant, c'est-à-dire *moins
lumineuse que le mur*.

### Audit

`tools/audit_guilde_fenetres_ambiances.py` → `art/guilde_destiny_reseau/polish/audit_fenetres.json`

| Contrôle | Résultat |
|---|---|
| Salles couvertes | **15 / 15** appellent `AppliquerAmbianceEtFenetres` avec leur identifiant |
| Fenêtres déclarées | **14** (9 salles) — les 6 autres n'ont aucune fenêtre dessinée dans l'art DS |
| Modes d'appel | `Init` + `Enter` + `GameLoad` → l'ambiance est réévaluée au rechargement |
| `.dir` d'ambiance | **56 / 56** |
| Complétude / dimensions / variantes distinctes | **14 / 14** sur les trois |
| Vitre plus lumineuse que le mur la nuit | **14 / 14** |
| Anomalies / avertissements | **0 / 0** |

---

## 2. Taches lumineuses circulaires (plafond de l'accueil)

**Cause** : régression du re-shade, pas du décor DS. Le relief était appliqué aussi aux
bois sombres : le grain rond du plafond (couleur DS `(64,31,17)`, 4200 px plats)
recevait un bombement et s'éclaircissait par plaques.

**Correctif** (`tools/pmdo_shade.py`) : garde `relief_min = 30` / `relief_span = 60`
(aucun relief sous une luminance de 30), et les régions de moins de 3 px d'épaisseur
restent **plates** — une strie de grain ne doit pas devenir une crête claire continue
(sinon des traînées horizontales apparaissent sur les planches).

---

## 3. « Sorte de filtre » — ombrage

**Cause 1** : la rampe d'ombrage **interpolait** entre deux tons. Chaque couleur de base
produisait des dizaines de teintes intermédiaires → dégradé flou au lieu d'un ombrage
pixel art. **Correctif** : application du **ton le plus proche**, en escalier.

| | DS 673e05b | avant | après |
|---|---|---|---|
| couleurs (15 salles) | 1 054 | 4 163 | **1 875** |
| ratio vs DS | 1,0 | ×3,95 | **×1,78** |

**Cause 2** : le gradient vertical global traversait les paliers de rampe sur les grandes
surfaces plates et laissait une **bande horizontale** visible. Amplitude ramenée de
0,55 à 0,16 ; le volume vient du relief local et de l'occlusion. Écart moyen avec le DS
après correction : **1,30 / 255**.

---

## 4. Pixels parasites

`tools/speckle.py` — un amas de 1 à 3 px dont la couleur tranche avec **tous** ses
voisins est remplacé par la couleur voisine dominante ; l'alpha n'est jamais modifié
(silhouette DS intacte).

| | DS 673e05b | après |
|---|---|---|
| amas ≤ 2 px isolés (15 salles) | 3 105 | **759** |
| accueil | 707 | 40 |
| cuisine | 315 | 80 |

Bruit isolé mesuré sur Floor/Walls/Supports : **4,51 %** (contre **5,80 %** pour le DS).

---

## 5. Pixels bleu foncé sur les fenêtres

Deux causes cumulées :
1. le nettoyage post-quantification pouvait prendre un pixel de **verre** comme couleur
   de référence et le recopier dans le cadre ;
2. la palette du cadre était extraite de PNG d'ambiance qui contenaient du ciel bleu nuit.

**Correctif** : donneurs restreints au cadre (`donor=sel`) et palette filtrée aux tons
bois. Résultat : **0 pixel froid sur les cadres**, sur les 56 fichiers.

Le halo des étoiles qui bavait sur le cadre est supprimé : diffusion limitée aux 4 voisins
qui sont eux aussi du verre, et étoiles en **amas de 3 à 6 px** (plus de point isolé d'1 px).

Les cadres sont aussi re-quantifiés sur une **palette de 14 tons** commune aux 4 ambiances
(les PNG sources en comptaient **1 885** pour un sprite de 48 × 88 : dégradés lisses qui se
lisaient comme un filtre sale), et le ciel est passé de ~90 teintes interpolées à **4 bandes
franches**.

---

## 6. Aperçu HTML — flou de compression

`art/guilde_destiny_reseau/apercu_reseau_interieur_guilde.html` embarquait ses images en
**JPEG qualité 84**. Sur du pixel art, c'est une perte sèche : contours baveux et teintes
délavées. Remplacé par du **PNG quantifié 256 couleurs** (5209 Ko au lieu de 4124) et
`image-rendering: pixelated` sur toutes les images.

---

## 7. Façade `Guilde_HD` — pixels parasites

Les captures du joueur ne correspondaient à aucune image du dépôt : ce sont des
agrandissements rééchantillonnés de `Guilde_HD_Jour`. Les salissures sont de petits
**éclats bleu-violet perdus dans le bois** (poutres, linteaux, pourtour de la porte).

**Signature retenue** : sur cette façade, **tout vrai caillou est surmonté d'un éclat
orangé clair** — sans ce reflet à côté, la tache bleu-violette est une salissure.
Un premier nettoyage générique avait été rejeté : il transformait des reflets dorés voulus
en contours sombres et rabotait les vrais cailloux.

`tools/nettoyer_pixels_facade.py` — détection sur la version **Jour** (seule ambiance où
la teinte pierre se distingue du bois), masque appliqué aux 4 ambiances (même dessin
recoloré). Résultat : **132 px** corrigés, cailloux / mousse / liserés intacts.

---

## 8. Bordure rocheuse courbée sur le flanc gauche de l'escalier

`tools/bordure_rocheuse_escalier.py` — un **arc de Bézier** adossé au flanc gauche de
l'escalier : il s'écarte du talus au milieu puis revient sous la dernière marche, effilé
aux deux extrémités. Pierre appareillée (joints plus sombres), arête claire côté escalier,
contour sombre côté talus, deux touches de mousse.

Palette **relevée sur la façade**, aucune couleur nouvelle : `(48,36,42)`, `(82,63,70)`,
`(118,94,102)` sont les tons exacts de ses cailloux, contour `(36,17,12)`, mousse `(44,90,33)`.

Appliquée aux **8 variantes** (4 ambiances × porte fermée / ouverte). Elle ne dessine que
sur des pixels transparents : l'escalier, la porte et le rocher sont intacts.

---

## 9. Jeu d'ombre de la façade

Régression de la refonte : les `Guilde_HD_Ombre_*` étaient devenus un **gris uniforme
alpha 112**. La sauvegarde brute portait un dégradé de **4 teintes vertes jusqu'à alpha 224**.
Restaurées à l'identique depuis `assets/backup_c2766e5/objects`.

À noter : sur la carte extérieure réelle, l'ombre reste en grande partie masquée par le
gazon du promontoire — c'est pourquoi elle se voit peu, mais elle est de nouveau correcte.

---

## Contrôles de sortie

- audit fenêtres : **0 anomalie / 0 avertissement** ;
- grille 8 px : **15 / 15** salles valides (dimensions, calques, obstacles, entités,
  décorations, fenêtres, porte) ;
- `build_tile_index.py` : 2 282 planches ; `test_batiments_interieurs.py` : OK.

## Planches

| Fichier | Contenu |
|---|---|
| `planche_positions.png` | les 14 fenêtres en place, une par salle |
| `planche_ambiances.png` | les 4 ambiances de chaque fenêtre, ×8 |
| `avant_apres_fenetres.png` | avant / après sur les 13 fenêtres |
| `apres_ambiances_4_salles.png` | 4 salles complètes, 4 ambiances |
| `zones_signalees_avant_apres.png` | les 3 zones des captures, DS vs corrigé |
| `planche_finale_polish.png` | 4 salles : DS / corrigé jour / corrigé nuit |
| `fenetres_4_ambiances_polish.png` | cadres re-quantifiés, ciel en bandes |
| `facade_bordure_finale.png` | façade + bordure rocheuse en situation |
| `bordure_4_ambiances.png` | la bordure dans les 4 ambiances |
| `exterieur_4_ambiances.png` | l'extérieur complet, 4 ambiances |
| `ombres_brut_vs_pmdo.png` | ombres : sauvegarde brute vs gris PMDO |
