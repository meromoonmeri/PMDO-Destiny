# Destiny — Foulards et rubans des starters

Ce kit ajoute deux accessoires cosmétiques pour les **86 formes de départ** : un ruban et un foulard, disponibles en neuf teintes. Chaque membre du duo choisit sa pièce et sa couleur indépendamment. L’objet tenu et les statistiques ne sont pas modifiés.

## Essayer sans installer

Ouvrir **`Vestiaire-Foulards-et-Rubans.html`**. Choisir le héros ou le partenaire, sa forme, sa pièce et sa couleur. Les huit directions, la marche et le mode nuit permettent de voir les accessoires sur les sprites natifs. L’aperçu est autonome, sans connexion et sans sauvegarde de jeu.

**`Foulards-et-Rubans-en-jeu.png`** réunit des captures du jeu de test : Pikachu porte le foulard Garance, Goupix d’Alola le ruban Lagon. Les détails sont des agrandissements sans lissage de ces captures.

## Utiliser dans le jeu recompilé

1. Au sol, ouvrir **Équipe → Pokémon → Ruban** ou **Foulard**.
2. Haut/Bas sélectionne une teinte ; Gauche/Droite tourne l’aperçu. Rien n’est appliqué avant validation.
3. Valider la teinte ou choisir **Sans accessoire** pour retirer la pièce. Annuler laisse la tenue inchangée.
4. Sauvegarder normalement. L’accessoire est purement visuel ; l’ancien coloris de ruban reste un ruban si le champ de style est absent.

Un seul accessoire est porté à la fois par Pokémon : choisir un foulard remplace son ruban, et inversement. Les deux membres du duo sont indépendants. Le changement se fait au sol ; le rendu est aussi branché sur les animations en donjon. Les fondateurs gardent l’accès après évolution, de même qu’un starter recruté déjà ajusté.

## Intégrer aux sources

Le patch vise la révision **`8f80c6e2c47e681acd334be661d601a59fed2367`** de Destiny. Sur une copie de travail propre de cette révision, et après sauvegarde de vos données :

```sh
git apply --check /chemin/vers/Foulards-et-Rubans.patch
git apply /chemin/vers/Foulards-et-Rubans.patch
```

Recompiler ensuite le moteur et le jeu selon la procédure du projet. Le patch comprend C# et Lua : **il ne s’installe pas sur le seul exécutable existant** et remplace le précédent patch de rubans, il ne s’ajoute pas par-dessus. Le moteur a été compilé et essayé sous Linux/.NET 8/FNA ; aucun exécutable Windows n’est fourni. Aucun fichier de votre installation ou de votre sauvegarde n’a été modifié.

## Coupes et limites

Le placement utilise la silhouette, les repères natifs de tête et de centre, la direction, le miroir et la pose d’animation. Quatorze profils et des coutures propres à certaines espèces/formes adaptent la coupe. Le ruban est noué côté avant ; le foulard comporte un pan arrière, occulté par le corps lorsque la perspective le demande. Les attaches latérales sont prévues pour certaines morphologies.

Les essais géométriques et les planches de contrôle ne sont pas une reconnaissance sémantique des visages : **ils ne garantissent pas un ajustement visuel parfait pour chaque image ou chaque forme évoluée**. Certains petits sprites ou poses particulières peuvent nécessiter une retouche manuelle de couture. Après reprise, si plusieurs personnages de l’équipe sont impossibles à distinguer avec les données disponibles, l’acteur détaché n’est pas modifié au hasard : un changement de carte peut être nécessaire pour rafraîchir son apparence.

## Vérifications et contenu

- **`Starters-eligibles.tsv`** : formes, profils et décalages de couture par angle.
- **`Verification-rendu.json`** : 56 336 poses repos/marche et 1 600 rendus FNA, dont 480 rendus d’actions de donjon. Cela ne constitue pas un parcours complet de donjon.
- **`Verification-integration.json`** : menu réel, annulation, choix indépendants, sauvegarde et reprise sur banc isolé, retrait et objet tenu vérifié.
- **`Verification-vestiaire.json`** : huit groupes de tests, dont 2 752 comparaisons pixel à pixel et le fonctionnement hors ligne.
- **`Sources/` et `Tests/`** : construction et recette. `Tests/Banc-jeu.lua` est une fixture réservée au banc : ne pas l’installer dans une partie normale.

Les sprites restent ceux de Destiny et de leurs auteurs, notamment SpriteCollab : voir les [crédits du projet](https://github.com/meromoonmeri/PMDO-Destiny/blob/8f80c6e2c47e681acd334be661d601a59fed2367/CREDITS.md). Les coupes et palettes de ce kit sont propres à l’atelier ; aucun sprite de ruban Halcyon n’a été utilisé.
