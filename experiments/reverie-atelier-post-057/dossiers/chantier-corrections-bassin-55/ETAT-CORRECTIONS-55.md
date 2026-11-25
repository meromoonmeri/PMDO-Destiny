# Bassin de Réverie — capture 55, candidat local

## Base et sauvegardes

Les cartes jeu et Dev partent du candidat local 53–54, lui-même basé sur Destiny v0.5.7, commit `ee39156a24f350b67e81740478be8505f4ff1a05`. Les deux originaux vérifiés, les deux cartes 53–54 et leur journal sont dans `sauvegardes/`. Les modifications n'ont pas été installées ni publiées.

## Changements 55

- Sous la souche : reprise locale d'un trait horizontal dans l'herbe et de son petit retour vertical. La souche, les poteaux et l'arbre sont conservés.
- Près des fleurs : atténuation ciblée d'un trait vertical dans l'herbe. Les fleurs, poteaux et falaise sont conservés.
- La correction utilise un motif de sol existant de Réverie et des masques opaques, ajoutés à l'intérieur des cellules du calque `Base`, dans la banque `Reverie_Correction_Herbe_55.tile`. 318 pixels retouchés au total avant recouvrement par les calques supérieurs ; 36 cellules par carte. La sélection suit les lignes identifiées et écarte les pixels qui ne sont pas du sol vert. Toutes les modifications exactes sont dans `journal-55.json`.
- Les corrections 53–54 restent incluses : deux arbres, quatre zones d'ombre sur falaise et une petite ligne isolée dans l'eau. Elles utilisent aussi `Reverie_Correction_Ombres_5354.tile`. Les deux banques sont nécessaires avec les cartes candidates. Les deux cartes 53–54 sont conservées séparément dans `sauvegardes/`.

## Correspondance avec les sept cercles

Trois cercles à gauche et le rebord à droite recoupent les reprises d'ombre 53–54 : voir `gauche-haut.png`, `gauche-2.png`, `gauche-3.png`, `droite-falaise.png`. Les comparaisons sont des rendus statiques ; le raccord du milieu à gauche mérite une vérification visuelle en contexte. Les cercles de la souche et des fleurs sont repris dans le présent candidat, voir `avant-apres-souche.png` et `avant-apres-fleurs.png`.

Le dernier cercle, en bas à gauche entre deux arbres, montre une limite d'ombre. Le défaut exact n'est pas établi : le bord observé existe aussi dans une copie identique du motif source. Il n'a pas été modifié arbitrairement ; ce cercle reste **à examiner**. Les autres raccords de rive, de chemins et la touffe précédemment signalés restent eux aussi ouverts.

## Contrôles et limites

Les deux cartes ont été décompressées et comparées intégralement avec leurs homologues 53–54 : après annulation des seules 36 cellules `Base` journalisées, les objets JSON sont identiques. Les collisions, événements, décors, autres calques et données d'animation sont donc inchangés par ce correctif 55. La banque ajoutée a été relue et comparée aux pixels générés. Les images sont des rendus statiques d'une phase, pas des captures du moteur.

Pas de test PMDO 0.8.12, de collision en mouvement, d'animation en jeu, d'ancienne sauvegarde, de CI ni de publication. Installation à effectuer seulement sur une copie compatible, avec les deux banques, suivie d'un contrôle dans l'éditeur et le jeu. Ne pas écraser un état plus récent sans comparaison et sauvegarde.
