# Modifier les calques et utiliser les tilesets de Réverie

## Choisir une carte dans PMDO 0.8.12

Dans le Ground Editor, ouvrir `File > Open` puis choisir dans `Data/Ground` :

| Fichier | Vue | Calques |
| --- | --- | --- |
| `WaterfallVillageCapital_Dev.rsground` | Ville complète pour l'édition | 37 séparés |
| `reverie_centre_Dev.rsground` | Centre, copie d'édition | 37 séparés |
| `reverie_nord_Dev.rsground` | Nord, copie d'édition | 37 séparés |
| `reverie_residentiel_Dev.rsground` | Résidentiel, copie d'édition | 37 séparés |
| `reverie_etang_Dev.rsground` | Étang, copie d'édition | 37 séparés |

Dans l'onglet `Textures`, la liste `Layers` contient les calques de la carte ouverte. Le navigateur `Tiles` contient les banques de tuiles : les 14 banques de ville ont un nom commençant par `Reverie_WV_`. C'est une liste différente des calques. Les intérieurs utilisent leurs propres cartes et banques.

Les cartes de jeu, sans suffixe `_Dev`, conservent 11 couches composites. Les copies `_Dev` reprennent séparément les 37 couches de la ville d'édition et masquent les zones éloignées, en conservant la même marge graphique que le quartier correspondant. Leurs données de terrain, entités et décorations proviennent du quartier de jeu. Elles servent à l'édition ; elles ne sont pas déclarées comme destinations jouables.

**Enregistrer une carte `_Dev` ne met pas automatiquement à jour sa carte jouable.** La compilation ou le transfert des modifications vers les 11 couches de jeu est une étape distincte, à sauvegarder et à valider avant diffusion. Ne pas utiliser `Save and Test` comme preuve que ces copies sont jouables. Les tests automatisés vérifient la structure et les tuiles ; les quatre cartes ont aussi été chargées par PMDO 0.8.12 et initialisées avec `OnEditorInit` sans interface graphique. L'ouverture interactive de l'éditeur et une partie restent à vérifier.

## À propos des PNG

Les PNG de couches et de tilesets sont des exports à part : leur présence dans une archive ne les ajoute pas automatiquement à l'éditeur. Les PNG montrent la première frame, pas les animations. Les cartes `.rsground` et les banques `.tile` natives conservent les données animées ; privilégier les ressources natives pour poursuivre l'édition.

L'éditeur propose `Tiles > Load from .png into Tileset`, puis `Tiles > Load Tileset into Layer`. Attention : l'import produit une banque portant le nom du PNG et peut écraser une banque homonyme. Toujours travailler sur une copie, utiliser un nom distinct et vérifier la taille des tuiles avant un import. Ce processus n'a pas été validé comme méthode de reconstruction automatique des calques ou des animations.
