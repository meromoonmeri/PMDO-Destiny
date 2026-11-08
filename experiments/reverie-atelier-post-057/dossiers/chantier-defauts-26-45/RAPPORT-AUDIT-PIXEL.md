# Réverie — audit pixel, animations et raccords

**État : audit technique approfondi et corrections locales, travail artistique et publication encore incomplets.** Base publiée : 0.5.5, commit `97847f618dd16d99f9475e75b74242c247146631`. Les corrections examinées sont locales et ne sont pas publiées.

## Périmètre et méthode

- Carte `reverie_centre` : rendu de **1 600 × 4 000 pixels**, soit **6 400 000 positions**, en phase initiale, sans personnage ni effets propres au moteur.
- Dix variantes de cartes : comparaison des 11 matrices de tuiles ; elles ont le même contenu graphique, couche par couche. **203 425 références d’images** ont été contrôlées par carte, avec leurs coordonnées et durées. Aucune référence invalide ou banque manquante dans cet échantillon de 27 banques utilisées.
- Toutes les images référencées ont été décodées et les images vides représentées comme transparentes : **13 019 200 pixels de trame**, avec répétitions. Ceci recense les images utilisées, pas toutes les combinaisons de calques dans une partie.
- La transparence a été contrôlée sur les cycles locaux exacts de chaque cellule en tenant compte des durées et des calques. La comparaison de la phase initiale avec le rendu a réussi. Ce contrôle concerne l’alpha nul des ressources graphiques ; il ne teste pas les personnages, les événements ou les effets moteur.
- Les terrains visibles (`Base`, `Cliffs`, `River`) ont été comparés, pixel par pixel en phase initiale, à la palette de huit banques Métano authentifiées depuis `Palikadude/Halcyon@1522c7a8b7a34d70078e11ed605b21d563b0dc51`. Une égalité de couleur ne démontre pas que le pixel est au bon endroit.

## Transparences détectées et correction

L’audit initial a repéré **104 pixels complètement transparents** dans le rendu initial ; l’analyse des cycles locaux n’en a pas découvert d’autres intermittents. Parmi eux, **12 pixels intérieurs**, regroupés près de deux rives et d’une falaise, étaient transparents à toutes les phases.

Ces 12 pixels ont reçu un fond transparent ailleurs, placé dans `Base` sous les animations, en prélevant les couleurs de pixels voisins du même terrain. Les images existantes ne sont ni supprimées ni recouvertes : chaque image de chaque couche aux quatre cases touchées a été vérifiée dans les dix variantes. Après correction, le même audit trouve **92 pixels transparents**, tous sur la limite gauche de la carte, entre y=792 et y=916. Ils restent à examiner comme limites de carte : leur remplissage automatique pourrait créer une fausse continuation du décor ou modifier le cadrage.

Le rendu initial comportait aussi **142 pixels partiellement transparents** en 14 composantes ; certains se trouvent sur des transitions ou sous des objets. Ils ne sont pas automatiquement des trous : leur alpha, leur contexte et les couches ont été conservés pour examen.

## Comparaison de la palette et des motifs

Sur **4 459 805 pixels de terrain visibles et non recouverts** à la phase initiale, **4 311 646** ont exactement une couleur présente dans la palette Métano de référence. Une comparaison par distance de couleur signale seulement **17 pixels** à 16 niveaux ou plus du plus proche RGB de cette palette ; l’inspection les situe dans des feuillages ou des mélanges sur des falaises. Ce ne sont pas, à eux seuls, des défauts prouvés. Les autres écarts incluent des mélanges alpha et des matériaux ou effets propres à Réverie ; aucune recoloration globale n’a été appliquée.

Exemple de contrôle spatial : sur une portion de la bordure gauche du chemin de la capture 27 (24 × 40 pixels), **932 pixels sur 960** sont exactement identiques à un module Métano de même orientation. Quatre motifs Réverie analogues sont identiques ou quasi identiques. Cela confirme l’origine du motif, mais ne prouve pas que l’ensemble du chemin ou de ses raccords répond au souhait esthétique de l’utilisateur ; la zone reste à juger et à peaufiner.

## Autres corrections locales déjà cumulées

- Ondulations des sept pierres : séquence Métano de neuf images, panneau et objet animé préservés ; 73 instants inspectés sur le rendu de données.
- Rive oblique près des boutiques : 38 cellules statiques ont retrouvé leurs quatre phases natives ; 36 autres cellules d’eau non ambiguës ont été restaurées ailleurs.
- Huit segments de rive sous le pont ont été raccordés en utilisant des séquences natives ; les animations préexistantes n’ont pas été supprimées.
- Raccords locaux à l’étang, à l’escalier de guilde et sur une bordure près de la maison, avec contrôles des variantes et des phases concernées.

## Régression et sauvegarde du travail

Les dix cartes ont été comparées intégralement à la 0.5.5 en retirant virtuellement les changements ciblés : **PASS**. Par carte, les changements sont limités à 4 cellules `Base`, 88 `River`, 35 `Objects` et 35 `Objects Over`. Les objets, obstacles, événements et autres données hors des couches ont aussi été comparés à la base lors de la reconstitution précédente.

Le travail local peut être reconstitué par `kit-reprise-visuel/reconstituer.py` à partir des dix fichiers du commit exact : 162 cellules modifiées par carte, contrôle de l’empreinte de chaque fichier d’origine et du résultat. Reconstitution et empreintes des dix cartes : **PASS**. Le delta compressé a le SHA-256 `4a483ad1440dcfb2b623fa817295534517bed9b7b16567d9632cc6c844aeccf0`. Ce kit est une sauvegarde de travail, pas une version complète à installer ou une release.

## Ce qui reste ouvert

- Terminer la correction ou l’examen motivé des zones indiquées dans les captures 27–29, 31, 33–39, 42, 44 et 45, ainsi que la seconde zone de la capture 30. D’autres défauts similaires peuvent subsister.
- Examiner les 92 pixels en limite de carte et les 14 groupes d’alpha partiel dans le contexte de jeu ; revoir les résultats selon les objets et les mouvements réels.
- La comparaison de couleurs et l’inventaire de trames ne certifient **ni la continuité artistique de chaque raccord, ni l’absence d’objets rognés, ni la fidélité de tous les pixels dans tous les états de jeu**. Un examen visuel complet, un test dans l’éditeur et en jeu, y compris sur une ancienne sauvegarde, restent nécessaires.
- Aucune nouvelle CI, publication ou version complète n’a été faite pour ce travail. La version publiée reste 0.5.5. Ne pas présenter cet audit ou le kit comme une correction exhaustive terminée.

## Pièces de contrôle

- `audit-pixel-integral/inventaire-pixel-et-references.json` : rendu phase initiale, palette et références.
- `audit-pixel-integral/inventaire-pixels-images-animees.json` : inventaire pondéré de toutes les trames référencées.
- `audit-pixel-integral/alpha-toutes-phases.json` et `alpha-apres-toutes-phases.json` : transparences avant/après par cycle local.
- `audit-pixel-integral/references-10-cartes.json` : références et empreintes des couches des dix cartes.
- `audit-pixel-integral/comparaison-couleurs-metano.json`, `atypiques-16-detail.png` : distances de couleur et contextes des pixels atypiques.
- `audit-pixel-integral/verification-cartes-apres.json` : comparaison des cellules modifiées avec la base.
- `AUDIT-CAPTURES-26-45.md` : suivi individuel des captures.
