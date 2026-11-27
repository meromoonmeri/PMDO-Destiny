# Destiny — Vestiaire d’accessoires · version d’essai

Cette version ajoute au ruban et au foulard six accessoires : **chapeau cow-boy, casquette, haut-de-forme, béret, bonnet et lunettes de soleil**. Elle donne à Kaiminus une coupe de col spécifique et plus compacte.

## Essayage sans installation

Ouvrir **`Vestiaire-Foulards-et-Rubans.html`**. Choisir le héros ou le partenaire, son espèce, un accessoire et une teinte. Les huit directions, le repos, la marche et le mode nuit sont disponibles. Il n’y a **qu’un accessoire par Pokémon** : en choisir un autre remplace le précédent. Les deux membres peuvent avoir des choix différents.

La planche **`Apercu-accessoires.png`** montre plusieurs styles sur les sprites de Kaiminus et de Pikachu. Le HTML est autonome et ne modifie aucune sauvegarde.

## État et limites importantes

C’est une **version d’essai**, pas une garantie d’ajustement parfait sur toutes les espèces. Les chapeaux sont ancrés automatiquement à la silhouette et les lunettes à une estimation de la position des yeux, avec une correction pour Kaiminus. Sur certaines morphologies atypiques ou animations, les lunettes peuvent être décalées ou les coiffes se poser sur une mèche, une oreille ou une pointe : essayer les vues et prévoir des retouches par espèce avant une intégration définitive. Les contrôles automatiques vérifient l’ancrage et le rendu, pas la reconnaissance des yeux.

Le menu, la sauvegarde, la reprise et le remplacement ont été essayés sur une copie isolée ; les captures et détails sont dans `Verification-integration.json`. Aucun parcours complet en donjon ni compilation Windows n’a été effectué. Aucune installation ou sauvegarde du joueur n’a été modifiée.

## Essai dans le jeu recompilé

Au sol : **Équipe → Pokémon → Chapeaux et lunettes**, puis choisir le style et la couleur ; les menus Ruban et Foulard restent disponibles. Tourner l’aperçu avec Gauche/Droite, valider ou annuler. « Sans accessoire » retire la pièce. L’objet tenu et les statistiques ne sont pas modifiés. Pour les lunettes, la teinte concerne la monture ; les verres restent sombres.

## Intégration aux sources

Le patch `Foulards-et-Rubans.patch` est un patch complet qui **remplace**, et non complète, le précédent patch de rubans/foulards. Il vise la révision `8f80c6e2c47e681acd334be661d601a59fed2367` :

```sh
git apply --check /chemin/vers/Foulards-et-Rubans.patch
git apply /chemin/vers/Foulards-et-Rubans.patch
```

L’appliquer seulement à une copie propre et après sauvegarde, puis recompiler le jeu et le moteur selon la procédure Destiny. Il ne s’installe pas sur le seul exécutable existant. Aucun exécutable Windows n’est fourni.

## Contrôles

- `Verification-rendu.json` : 86 formes, 15 profils, 56 336 poses ruban/foulard, 169 008 poses d’accessoires de tête, 4 480 rendus FNA dont 1 440 actions de donjon. Ces nombres ne prouvent pas le bon placement anatomique de tous les modèles.
- `Verification-vestiaire.json` : neuf groupes de contrôles, dont 11 008 comparaisons pixel à pixel du HTML avec les calques exportés et les essais hors ligne.
- `Tests/Recette-native.md` décrit le banc. `Tests/Banc-jeu.lua` est une fixture réservée aux tests isolés et ne doit pas être installée dans une partie normale.

Les sprites sont ceux de Destiny et de leurs auteurs, notamment SpriteCollab ; voir les [crédits du projet](https://github.com/meromoonmeri/PMDO-Destiny/blob/8f80c6e2c47e681acd334be661d601a59fed2367/CREDITS.md). Les accessoires sont dessinés en pixels par le moteur pour épouser ces sprites.
