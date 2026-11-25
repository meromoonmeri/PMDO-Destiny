# Polish — taches, pixels parasites, artefacts de filtre

Correction des défauts signalés sur les captures (`image-7`, `image-8`, `image-9`,
toutes des recadrages de `guilde_destiny_accueil`) : taches lumineuses rondes,
pixels parasites et « sorte de filtre » avec de petits défauts visibles.

## 1. Taches lumineuses circulaires (plafond de l'accueil)

**Cause** : régression de mon re-shade, pas du décor DS. Le relief était appliqué
aussi aux bois sombres : le grain rond du plafond (couleur DS `(64,31,17)`,
4200 px plats) recevait un bombement et s'éclaircissait par plaques.

**Correctif** (module `tools/pmdo_shade.py`)
- garde `relief_min = 30` / `relief_span = 60` : **aucun** relief sous une
  luminance de 30, relief graduel jusqu'à 90 ;
- les régions fines (≤ 2 px d'épaisseur) sont laissées **plates** : une strie de
  grain ne doit pas devenir une crête claire continue (des traînées
  horizontales claires apparaissaient sur les planches du plafond).

## 2. « Sorte de filtre » — ombrage

**Cause** : la rampe d'ombrage **interpolait** entre deux tons
(`ton = ton_i + (ton_i+1 − ton_i) × fraction`). Chaque couleur de base produisait
des dizaines de teintes intermédiaires : à l'écran, un dégradé flou au lieu d'un
ombrage pixel-art.

**Correctif** : le ton **le plus proche** de la rampe est appliqué, sans
interpolation. Résultat mesuré sur les 15 salles :

| | DS 673e05b | avant | après |
|---|---|---|---|
| couleurs (total 15 salles) | 1 054 | 4 163 | **1 875** |
| ratio moyen vs DS | 1,0 | ×3,95 | **×1,78** |

**Second correctif** : le gradient vertical global a été réduit (`amp` 0,55 → 0,16
sur les murs). Sur une grande surface plate, un gradient même faible finit par
franchir un palier de rampe et laisse une **bande horizontale visible** — c'est
exactement le défaut de la zone 2 (mur derrière le comptoir de l'accueil).
Le volume vient désormais du relief local et de l'occlusion, pas d'un dégradé
d'ensemble. Écart moyen avec le DS après correction : **1,30 / 255**.

## 3. Pixels parasites

- nettoyage par amas (`tools/speckle.py`) : un amas de 1 à 3 px dont la couleur
  tranche avec **tous** ses voisins est remplacé par la couleur voisine
  dominante ; l'alpha n'est jamais modifié (silhouette DS intacte) ;
- mesure (amas ≤ 2 px, écart L1 > 90 avec tous les voisins) :

| | DS 673e05b | après |
|---|---|---|
| total 15 salles | 3 105 | **759** |
| accueil | 707 | 40 |
| cuisine | 315 | 80 |

## 4. Fenêtres — halo et flou

**Halo d'étoiles** : `etoiles()` appliquait un flou gaussien qui débordait du verre
et bavait sur le cadre. Remplacé par une diffusion limitée aux 4 voisins qui sont
eux aussi du verre, et les étoiles sont désormais des **amas de 3 à 6 px**
(jamais d'étoile isolée de 1 px, qui se lisait comme un pixel parasite blanc).

**Flou de cadre** : les PNG sources des fenêtres sont *peints* avec des dégradés
lisses — **1 885 couleurs** pour un sprite de 48 × 88. Posé à côté des murs DS
(une dizaine de tons francs), cela faisait un cadre sale, avec liserés clairs et
sombres sur les arêtes. Correctif : palette de bois de **14 tons** extraite par
coupe médiane (commune aux 4 ambiances, donc aucun scintillement d'une ambiance à
l'autre) et chaque pixel de cadre y est ramené.

**Ciel** : les 4 tons des rampes étaient interpolés en ~90 teintes voisines.
Le ciel est maintenant en **bandes plates** (4 tons francs par ambiance).

## Contrôles

- `audit_guilde_fenetres_ambiances.py` : 15 salles, 14 fenêtres, **56/56** `.dir`,
  4 ambiances complètes, tailles OK, vitres distinctes la nuit,
  **0 anomalie / 0 avertissement** ;
- `build_tile_index.py` : 2 282 planches ; `test_batiments_interieurs.py` : OK ;
- grille 8 px : **15/15** salles valides (dimensions, calques, obstacles, entités,
  décorations, fenêtres, porte).

## Planches

- `zones_signalees_avant_apres.png` — les 3 zones des captures, DS vs corrigé (×4) ;
- `planche_finale_polish.png` — 4 salles : DS / corrigé jour / corrigé nuit ;
- `fenetres_4_ambiances_polish.png` — cadres re-quantifiés, ciel en bandes.
