# Réverie — état du diagnostic des captures 46–52 et des ressources PMU

Base vérifiée : branche `wip/reverie-integration-kingambit-cafe`, commit `ee39156a24f350b67e81740478be8505f4ff1a05` (version 0.5.7). Ce document décrit un **travail inachevé**, pas une version corrigée ni une publication.

## Sauvegarde et méthode

`sauvegarde-057-avant.zip` conserve les dix cartes compressées, les 27 banques utilisées pour leur rendu et six fichiers de référence utiles. Les 43 fichiers ont été comparés aux blobs Git de la base et le CRC du ZIP est vérifié. La carte publiée a été recomposée en phase initiale, couche par couche ; localisation par correspondance d’image et contrôle visuel. Les coordonnées suivantes sont les origines approximatives des captures sur le rendu de la carte, en pixels natifs ; chaque capture est au zoom ×2.

| Capture | Origine | Zone à traiter |
|---|---:|---|
| 46 | 276, 222 | Clôture et berge sous la cascade. |
| 47 | 1304, 2136 | Pied de la grande falaise, derrière l’arbre. |
| 48 | 180, 1080 | Rive et bord du chemin près des pierres. |
| 49 | 666, 778 | Haut de la falaise et berge au pied de l’escalier. |
| 50 | 1156, 782 | Raccord du pied droit de l’escalier, partiellement derrière l’arbre. |
| 51 | 1282, 528 | Pied de l’escalier et deux raccords du chemin. |
| 52 | 948, 326 | Longue rive verticale près des arbustes. |

Ces correspondances ont des scores de 0,9955 à 0,9981, indicatifs seulement. Voir `reperage-46-52.png` et les images `inspect-*.png` pour le contexte. Les régions d’eau 48 et 52 ont été recomposées à quatre phases : `actuel-phases-eau48.png` et `actuel-phases-rive52.png`. En particulier, les cellules de la rive 52 contiennent déjà des séquences de quatre trames à 10 frames ; des pixels d’eau sur la couche `Objects` recouvrent une partie de la couche `River`. Un simple remplacement visuel peut donc rogner les séquences ou recouvrir le rivage.

Un essai local de remplacement par une autre rive a produit des superpositions et des raccords incertains ; il a été **écarté**. En revanche, le raccord central entre l’escalier et le chemin de la capture 51 a été préparé localement : le petit intervalle d’herbe est raccordé avec des pixels prélevés sur le chemin existant, sans couvrir les pixels de falaise. Les 728 pixels de raccord sont placés sur la couche `Base`, sous les personnages, dans 14 cases. Les dix variantes ont été contrôlées : toutes les autres cases et les sections hors couche sont inchangées ; les quatre phases sont vérifiées et les dix résultats sont reconstructibles depuis leurs empreintes d’origine. Voir `proposition-51-sans-toucher-escalier.png`. Ce n’est qu’une partie de l’image 51 : les deux autres zones entourées restent à examiner, ainsi que les images 46–50 et 52. L’éditeur, les collisions en mouvement et le jeu réel n’ont pas été testés. Les anciennes captures 26–45 restent elles aussi partiellement ouvertes.

## Ressources PMU : ce qui est présent et ce qui manque

La demande concerne bien les ressources **PMUniverse**, et non toutes les ressources de Destiny. Vérification dans l’arbre 0.5.7 :

- **Texture Tileset** : 40 banques `PMU_00_partie_01` à `PMU_10_partie_01` sont présentes sous `game/Content/Tile`, dérivées des onze planches historiques du client PMU de 2014. Le test du dépôt contrôle 467 399 positions de tuiles, signatures et offsets. Le build reconstruit l’index depuis les banques. Leur affichage effectif dans l’éditeur n’a pas été testé ici. Elles sont mixtes : mobilier, murs, sols et décor ne sont pas tous séparés en objets nommés.
- **Object / Decoration** : deux objets PMU natifs statiques seulement sont repérés dans la version publiée, sous `game/Content/Object` : `PMU_Table_bois_01` et `PMU_Lampe_sur_pied_01`. Cinq objets complets supplémentaires ont été sélectionnés manuellement et préparés **localement** en `.dir` : cheminée avec tableau, canapé rose, bibliothèque verte, piano et épée décorative. Leurs pixels, leurs en-têtes et l’absence de collision de noms ont été vérifiés (`verifier-objets-pmu-selection.py`) ; ils ne sont pas installés dans Destiny et leur affichage dans l’éditeur n’a pas été testé. Les autres objets des planches ne sont pas encore convertis individuellement. Une décoration Ground utilise une animation placée ; un fichier `.tile` ne devient pas automatiquement un objet `.dir`.
- **Char Display** : aucune ressource `PMU_` n’a été trouvée dans `game/Content/Chara`. La présence de Pokémon PMDO de base ne signifie pas que les personnages graphiques PMU ont été convertis.
- L’instantané historique de cartes PMU a 2 395 références graphiques indisponibles sur 177 cartes ; il ne prouve pas couvrir les versions PMU actuelles. Les contours exacts de chaque objet et les séquences d’animations de tuiles ne peuvent pas être déduits fiablement en découpant toutes les cases.

## Nouvelle recherche sur les sprites PMU

Le client public PMU au commit `c25c01f9879369647cd5a19731b2e4e5acd33e67` contient **751 fichiers `.sprite`**. Les 751 ont été récupérés et vérifiés contre leurs blobs Git ; leur archive locale `pmu_reference/sprites-pmu-2014-original.zip` a un CRC valide. Le lecteur a suivi `GraphicsManager.cs` et `SpriteSheet.cs` du client : il a analysé 751 fichiers, 751 formes et 12 676 bandes PNG d’animations directionnelles, sans échec. Les fichiers comptent 565 binaires distincts ; 181 fichiers sont identiques à un même binaire. Ce n’est pas une preuve que tous correspondent à des personnages distincts.

`inventaire-sprites-pmu-2014.json` liste les formes, actions, directions, dimensions, nombres de trames et empreintes des bandes. `exporter-sprite-pmu.py` peut extraire un sprite choisi sans modifier ses images ; un test sur le numéro 25 a vérifié 17 bandes. Ces bandes **ne sont pas des CharSheets PMDO**, ne sont pas installées dans Destiny et ne sont pas encore accessibles dans Char Display. Il faut encore déterminer et valider correspondances d’identifiants, points d’ancrage, directions, actions et cadence, gérer les ressources déjà présentes et tester l’import natif sans écrasement.

La licence MIT du code source ne démontre pas les droits de réutilisation de tous les dessins tiers. Les droits réels des ressources doivent être vérifiés avant leur redistribution.

## Publication

Aucun changement de carte ni d’asset n’a été poussé, aucune nouvelle CI n’a été lancée et aucune nouvelle release n’a été créée. La dernière release disponible est toujours la 0.5.7. Les cinq objets préparés localement sont conservés avec leurs sources dans `sauvegarde-objets-pmu-local.zip` ; le raccord est conservé dans `sauvegarde-raccord51-local.zip`. Les CRC des deux sauvegardes ont été vérifiés ; elles ne constituent pas une version installable complète. Le rapport préalable, la sauvegarde et les outils de diagnostic sont conservés dans ce dossier.

## Reprise locale après retour utilisateur : captures 51 et 52

Le premier raccord trop étroit a été remplacé à partir des dix cartes v0.5.7 d'origine, et non empilé. Le nouveau raccord part des deux extrémités de l'escalier : 62 cases de Base, 2 941 pixels, donneur local élargi sans interpolation ; pixels de falaise exclus. La rive 52 est ondulée par déplacement de 0 à 4 pixels de la rive existante et reprise des quatre phases à 10 frames sur `Objects Over` (niveau de dessin 0), 46 cases ; l'eau d'origine reste dessous mais l'animation superposée remplace visuellement une partie de ses pixels. Résultats locaux et limites dans `reprise-51-52/CONTROLE-LOCAL.md`, images avant/après et contrôles dans le même dossier. Rendu indépendant quatre phases PASS pour `reverie_centre` et empreintes des dix variantes PASS. Sauvegarde `sauvegarde-reprise-51-52-local.zip` CRC valide. Il faut encore vérifier les jonctions et le rythme dans le jeu ; les autres zones restent ouvertes. Aucun changement n'a été poussé.
