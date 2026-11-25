# Audit et travail en cours — captures 26 à 45

Base : version publiée **0.5.5**, commit `97847f618dd16d99f9475e75b74242c247146631` de `wip/reverie-integration-kingambit-cafe`. Repérage sur un rendu des 11 couches de la carte centrale, phase 0, 1 600 × 4 000 pixels. Les coordonnées ci-dessous sont l'origine approximative du cadrage, pas celles de chaque pixel entouré. Les correspondances ont aussi été examinées visuellement ; personnages, ombres de nuages et annotations ne figurent pas sur le rendu. Un score élevé est un indice de localisation, pas une validation artistique.

| Capture | Origine approximative | Zones indiquées et état |
|---|---:|---|
| 26 | 736, 814 ; ×3 | Raccords supérieur gauche et pied gauche repris localement à partir de modules Métano natifs ; quatre phases et dix cartes contrôlées. Vérification esthétique et en jeu encore nécessaire. |
| 27 | 608, 1694 ; ×2 | Raccords irréguliers et découpes des deux bords du chemin. À reprendre. |
| 28 | 8, 2530 ; ×2 | Bords de chemin, pelouse à la tente et ombre sous arbre ; séparer ombres et sol avant modification. À reprendre. |
| 29 | 236, 2456 ; ×2 | Raccord long et élargissement du chemin ; à harmoniser. |
| 30 | 496, 2402 ; ×2 | Bordure en bas à gauche reprise avec un module Réverie natif ; la jonction près de la maison reste à examiner. |
| 31 | 776, 2468 ; ×2 | Longue bordure du chemin et boîte aux lettres près de l’arbre ; vérifier la superposition avant retouche. À reprendre. |
| 32 | 960, 2102 ; ×2 | Extrémité très droite du chemin au pied de l’étang : raccord natif posé localement, quatre phases et dix cartes contrôlées ; validation en jeu à faire. |
| 33 | 920, 1942 ; ×2 | Raccords des deux rives du bassin. Il existe des animations d'eau ; distinguer les effets animés des contours rognés. À reprendre. |
| 34 | 962, 2438 ; ×2 | Ombre et pied d'arbre, bordure près du chemin et petite touffe ; à examiner. |
| 35 | 506, 2326 ; ×2 | Raccord du chemin près de la maison citrouille ; recoupe la capture 30. À reprendre. |
| 36 | 540, 1852 ; ×2 | Flanc droit et pied de l'escalier ; conserver l'ombre mobile et le volume de la falaise. À reprendre. |
| 37 | 550, 1676 ; ×2 | Raccord gauche du chemin, même secteur que la capture 27. À reprendre. |
| 38 | 916, 1472 ; ×2 | Bords de la place, herbes et jonction proche de la rivière ; distinguer l'ombre de nuage. À reprendre. |
| 39 | 1142, 1328 ; ×2 | Pieds et coins de falaises, autour de la charrette ; à reprendre sans la recouvrir. |
| 40 | 448, 862 ; ×2 | Rive oblique près des boutiques : 38 cellules auparavant statiques ont reçu les quatre phases natives Métano (10 frames par phase), sans supprimer les objets au-dessus ; contrôle des dix variantes. Vérification en jeu à faire. |
| 41 | 608, 224 ; ×2 | Les sept pierres ont retrouvé l’ondulation originale Métano en neuf phases de 10 frames, avec le panneau et le décor animé préservés par l’ordre des couches. Fragments bleus de berge supprimés ; 73 instants contrôlés sur un rendu de données. Validation en jeu à faire. |
| 42 | 642, 840 ; ×2 | Jonctions herbe/falaise/eau au pied de la guilde. La ligne de falaise sur l'eau à gauche a déjà reçu un raccord en 0.5.3 ; cela ne démontre pas que les deux zones entourées sont entièrement corrigées. À reprendre. |
| 43 | 952, 1068 ; ×2 | Seuil du pont et coupe de l’eau sur la pelouse : huit séquences natives de rive ont été ajoutées sous le pont et les fleurs, sans suppression des séquences préexistantes ; quatre phases contrôlées. Validation en jeu à faire. |
| 44 | 1064, 854 ; ×2 | Bord de chemin à droite du bâtiment rose et extrémité près des arbres. À reprendre. |
| 45 | 1274, 1028 ; ×2 | Deux longs bords du chemin horizontal ; harmonisation encore à faire. |

## Cadre et limites

Une sauvegarde préalable de 103 ressources de la 0.5.5 a été vérifiée par blob Git et CRC ZIP ; les fichiers volumineux peuvent être absents après un instantané et se récupèrent avec `preparer.py`. Les retouches sont locales : aucun push, nouvelle CI ou publication n’a été effectué. La version publiée reste la 0.5.5. Pas de validation dans l’éditeur ou le jeu réel, ni sur une sauvegarde réelle. Les captures précédentes 22 et 24 et la recherche exhaustive de défauts similaires restent ouvertes.

## Poursuite locale — après la restauration des sources Métano

Source de référence : `Palikadude/Halcyon` au commit `1522c7a8b7a34d70078e11ed605b21d563b0dc51`, carte `metano_town` et banques natives, vérifiées par empreintes Git. La séquence des pierres a été retrouvée dans `Metano_Town_Animation_Tileset` : seules les 27 positions de pixels propres à l’ondulation sont ajoutées au dessin existant, ordre 0–7–7, durée 10. Les traits bleus parasites proviennent d’une berge de la carte originale restée collée à la pierre lors d’une composition.

En complément, 36 autres cellules d’eau statiques, dont la correspondance avec une séquence native était non ambiguë, ont été restaurées dans différents secteurs. Cela ne prouve pas que toutes les animations similaires sont réparées. La recherche globale a recensé de nombreux candidats ambigus, notamment des tuiles d’eau uniforme identiques à plusieurs emplacements natifs ; ils ne sont pas remplacés automatiquement.

Vérifications réalisées : pour chacune des dix cartes, comparaison de toutes les cellules des onze couches à la 0.5.5, en retirant virtuellement les ajouts ciblés : **PASS** ; 88 cellules `River`, 35 `Objects` et 35 `Objects Over` diffèrent par carte. Les objets, obstacles et autres données situées hors couches sont identiques octet pour octet à la base. Contrôles de composition par phases et des neuf images de pierres, ainsi que CRC de la sauvegarde et de la reprise interne : **PASS**. Cela ne remplace pas un test moteur, éditeur, jeu réel, ancienne sauvegarde ou une CI.

L'état cumulé est dans `corrections-chemin30-en-cours/` ; la reprise interne CRC vérifiée est `reprise-visuelle-cumulee-interne.zip` (SHA-256 `d64173f05f86b4f1ae4074e05a51dcd93c39f5971ae28d2f6b0397f03462c0bd`). La sauvegarde d’origine et la référence native sont conservées en ZIP. Pour relancer les diagnostics : extraire `sauvegarde-v055-cartes-banques.zip` dans `base/` et `reference-metano-interne.zip` dans `reference-metano/`. Les scripts successifs s’appuient sur leurs répertoires d’étape ; ne pas les relancer en bloc sur des données déjà transformées.

**Le travail n’est pas complet :** la plupart des contours des captures 27–29, 31, 33–39, 42, 44 et 45 et la seconde zone de la capture 30 nécessitent encore une réparation ou une conclusion motivée ; les autres défauts similaires ne sont pas épuisés. Une analyse complète de toutes les superpositions et un test en jeu restent nécessaires. Pas de push, CI ni release ; ne pas diffuser cette reprise interne comme version complète.


## Audit supplémentaire — 7 novembre 2026

Les 11 couches graphiques sont identiques dans les dix variantes : contrôle de 27 banques, des coordonnées et durées des trames, sans référence invalide. Les 203 425 images référencées correspondent à 13 019 200 pixels de trame avec répétitions, tous décodés et recensés. La recherche exacte de transparences sur les cycles locaux a trouvé 104 pixels alpha nul à toutes les phases, dont 12 intérieurs ; ces 12 ont été remplis localement dans quatre cellules de fond avec des pixels de terrain voisins sans masquer aucune image existante. Après correction : 92 pixels alpha nul, tous à la limite gauche, délibérément non modifiés dans l’attente d’un examen de cadrage. Le rendu initial compte aussi 142 pixels alpha partiels, à ne pas confondre automatiquement avec des trous.

Sur 4 459 805 pixels de terrain visibles phase initiale, 4 311 646 ont une couleur exactement présente dans la palette Métano de référence. Les 17 pixels à distance maximum-canal ≥16 sont dans des feuillages ou des mélanges de falaise. Ce résultat ne garantit ni l’emplacement de chaque pixel, ni les raccords, ni les autres phases en jeu. Sur une portion de 24 × 40 pixels du chemin de la capture 27, 932 pixels sont identiques à un motif natif de Métano ; ce secteur reste à examiner en contexte plutôt qu’être déclaré réparé.

Après ajout du fond, le contrôle des dix variantes passe pour les 162 cellules modifiées : 4 `Base`, 88 `River`, 35 `Objects`, 35 `Objects Over`. La reconstruction à partir de la base vérifie les empreintes d’origine et des dix résultats. Sauvegarde légère mise à jour : `kit-reprise-visuel/`, delta SHA-256 `4a483ad1440dcfb2b623fa817295534517bed9b7b16567d9632cc6c844aeccf0`, huit banques et huit PNG. Lire `RAPPORT-AUDIT-PIXEL.md` pour les méthodes, limites et tâches restantes. Rien n’a été publié.
