# Bassin de Réverie — corrections locales des captures 53–54

## Référence et sauvegarde

Base : Destiny v0.5.7, commit `ee39156a24f350b67e81740478be8505f4ff1a05`. Les deux fichiers `payload/reverie_etang.rsground.gz` et `payload/reverie_etang_Dev.rsground.gz` ont été récupérés depuis ce commit et vérifiés contre leurs Git blobs respectifs `63c361a1f45184710de5a88925fc172e1fd15102` et `9ff9afa57015590b5a1c07813eb7f9c791691434`. Ils sont conservés comme originaux. Une ancienne sauvegarde du chantier ne correspond pas à cette version et n’a pas été utilisée pour réécrire les cartes.

## Modifications effectuées sur des copies locales

- **Deux arbres tronqués** : les pieds vers les sommets de référence `(1312,1956)` et `(1040,2460)` ont été complétés avec douze cellules (six par arbre) d’un arbre entier de même famille. Les pixels de cellules communes ont été comparés avant copie. Les emplacements cibles étaient vides sur le calque `Objects`.
- **Ombres sur rebords de falaise** : quatre régions signalées ont été reprises. Un nouveau calque de pixels opaques provenant des falaises sous-jacentes est placé localement dans `Objects Over`, uniquement à l’intersection des couleurs identifiées comme ombres et de falaises opaques, sans recouvrir les éléments des couches supérieures. 676 pixels répartis en 19 cases. Les couleurs du feuillage et du tronc ne sont pas effacées intentionnellement. Les pixels de ces corrections sont conservés dans `Reverie_Correction_Ombres_5354.tile` ; il ne faut pas installer les cartes sans cette banque.
- **Trait isolé dans l’eau** vers `(1135,2083)` : les deux premières images de la cellule `(141,260)` comportaient chacune uniquement une ligne isolée de cinq pixels ; les cinq autres étaient vides. Cette cellule seule a été supprimée du calque `Objects Anim`, sans supprimer les cellules voisines de la pierre, de l’eau ou leurs animations.

Corrections appliquées aux copies de la carte jeu et Dev : 32 cases par carte (12 `Objects`, 19 `Objects Over`, 1 `Objects Anim`). Les originaux et le journal des valeurs avant/après sont conservés. Les calques ne sont pas fusionnés ; leur nombre et leur ordre sont inchangés.

## Contrôles réellement effectués

- Les tuiles de la nouvelle banque ont été relues et comparées aux pixels calculés. Contrôle de structure PMDO par lecture Python : **pas un chargement dans PMDO**.
- Un comparateur intégral des données décompressées vérifie que, pour chacune des deux cartes, seules les 32 cases journalisées changent ; tous les autres champs, dont collisions, entités, décorations, BGM, dimensions et tous les autres calques, sont identiques.
- Des rendus statiques avant/après des deux arbres et des quatre zones d’ombre ont été produits depuis les tuiles. Les sept images de la séquence isolée ont été inspectées. La cascade, les eaux et autres animations n’ont pas été supprimées, mais leur rendu en moteur n’a pas été testé.

## Limites et éléments encore à reprendre

Les raccords en haut du bassin (1G et 1D), le chemin sud (6), le chemin est (7) et la petite touffe près de l’arbre sud (5) ne sont pas considérés corrigés : leurs couches et phases demandent une reprise distincte. Certaines branches peuvent masquer naturellement une falaise ; seul le chevauchement de l’ombre identifié a été traité, pas tout ce qui se trouve sous un arbre. Aucune garantie d’audit exhaustif de tous les arbres et de toutes les phases.

**Pas de test PMDO 0.8.12, de collision en mouvement, de sauvegarde réelle, de CI ou de publication.** Les changements sont des candidats locaux. Le doyen et sa nage ne sont pas installés par ce correctif. Avant intégration : prévisualiser dans l’éditeur, tester les deux cartes, regénérer les index sur le checkout complet et vérifier les animations et une ancienne sauvegarde. Ne pas confondre l’aperçu statique avec un rendu de jeu.
