# Destiny — audit de la caméra et de l’échelle des cartes

**Périmètre :** paquet Windows 0.3.1, commit `8142cadba6e8c7499fc01d9b3e1b21ff54f3c788`. Audit du 31 octobre 2026. Aucune carte ni aucun script livrés n’ont été modifiés. Les essais en moteur ont utilisé une copie de banc temporaire, restaurée ensuite.

## Ce que mesure l’audit

La question est bien : « en parcourant les endroits où le joueur peut aller, quelles parties de la carte la caméra finit-elle par montrer ? » Ce n’est pas la même chose que voir toute la carte **d’un seul coup**.

- La vue logique par défaut mesure **320 × 240 pixels**, soit 76 800 pixels. Le zoom de jeu observé par défaut est ×1 ; agrandir la fenêtre agrandit l’image, mais ne montre pas davantage de terrain.
- Dans les Grounds, la caméra suit normalement le centre du personnage. Sa boîte de collision mesure **16 × 16 pixels**. Les murs sont découpés en cellules de **8 × 8 pixels**.
- Si la caméra suit bien le personnage, chaque position effectivement parcourue est, par définition, visible lorsqu’on y passe. Les vrais points à vérifier sont les zones séparées, les décors loin des chemins, les obstacles, les déclencheurs et les scripts qui figent ou décalent la caméra.
- Les surfaces ci-dessous sont calculées sur le **rectangle géométrique** de la carte, pas uniquement sur les pixels de décor utiles. Le ciel, les marges et des zones laissées libres dans la grille de collisions peuvent ne pas être destinés au joueur.

## Synthèse

Sur les **376 cartes Ground de la Quest**, toutes présentes dans le ZIP :

| Mesure | Résultat et interprétation |
|---|---|
| Simulations géométriques calculées | **375 / 376** ; la carte restante a une grille de collisions incohérente. |
| 100 % du rectangle vu selon le modèle | **179 / 375**, avec les hypothèses de départ et de collision indiquées dans le tableau ; ce n’est pas une validation de 179 parcours réels. |
| Moins de 90 % du rectangle vu | **139 / 375** ; cela peut correspondre à des décors volontairement inaccessibles, pas nécessairement à des défauts. |
| Sans mur bloquant ni objet fixe bloquant sérialisé | **170 / 376**, dont certaines scènes ou cartes de travail ; impossible d’en déduire un chemin jouable fidèle au décor. |
| Sans marqueur | **28 / 376** ; le départ du calcul est alors hypothétique. |
| Zones sans obstacle statique isolées et hors champ | **26 / 375** présentent plus de 1 % de positions échantillonnées dans ce cas ; leur rôle décoratif ou jouable reste à vérifier. |

Les références d’entrées ont été recherchées dans le point de départ et les appels littéraux des scripts du paquet. Une référence trouvée ne prouve pas à elle seule qu’un parcours complet l’atteint ; les entrées variables, numériques ou issues d’autres mécanismes peuvent échapper à la recherche. Pour la plupart des cartes, le premier marqueur est donc **une hypothèse**, pas une entrée certifiée.

Le fichier `audit_grounds.csv` contient les **393 Grounds du paquet** : 376 pour Destiny et 17 de base, distingués par colonne. Le rapport interactif permet de filtrer et d’ouvrir un schéma pour chaque carte. Les noms de zones désignent des conteneurs internes à la Quest ; ce ne sont pas des Quests supplémentaires.

## Constatations prioritaires

### 1. Caméra figée après le retour sur `cliffdaytest_nuit` — confirmé sur banc

Dans `Data/Script/destiny/ground/cliffdaytest_nuit/init.lua`, la scène de retour place la caméra en coordonnées absolues `(666, 516)` (ligne 60). Elle quitte ensuite le mode cinématique sans la rendre relative au joueur (ligne 78). `CutsceneMode(false)` ne recentre pas la caméra.

Essai moteur Linux : l’état de retour et l’équipe ont été préparés directement sur une **copie de banc**, mais la séquence et ses commandes caméra sont restées inchangées. À la fin, `IsCameraOnChar=false`, caméra `(666, 516)`, joueur `(648, 516)`. Après un déplacement à droite, le joueur est à `(688, 516)` et la caméra toujours à `(666, 516)`.

**Conséquence :** dans cette situation, le joueur peut se déplacer sans que le cadrage le suive. C’est un vrai problème de caméra, non un simple pourcentage de décor hors champ.

**Autre anomalie observée pendant ce même essai :** la carte ne contient pas le générateur `TEAMMATE_1` requis par `COMMON.RespawnAllies()` ; le moteur signale son absence, puis un partenaire invalide lors de sa téléportation. La scène a été déclenchée en accès direct, sans rejouer les sept étages ; le trajet narratif complet reste donc à vérifier. Le noir observé au lancement direct du banc ne prouve pas, à lui seul, que le trajet normal reste noir.

**Recommandation :** restituer explicitement le suivi du joueur à la fin de la scène, et examiner séparément l’apparition du partenaire et le fondu. Préserver les cinématiques et les cartes existantes ; tester le retour réel complet avant livraison.

### 2. `glacier_cliff_aurora_v1` — dimensions incohérentes, erreur reproduite sous condition

- Le moteur lit une carte de **1 728 × 1 296 px** : couche de `72 × 54` tuiles, `TexSize=3`, donc cellules graphiques de 24 px.
- Il attend en conséquence **216 × 162 cellules** de collision de 8 px. Le fichier n’en contient que **72 × 54**, couvrant **576 × 432 px**.
- La couverture globale est donc **non calculable de façon fiable**. Ne pas réduire la carte, agrandir l’image, ou reconstruire ses collisions automatiquement sans vérifier l’intention et l’alignement du décor.

Sur une copie identique de la carte en moteur Linux, l’entrée s’est chargée. Après une **téléportation volontaire de test** en `(800, 500)`, à l’intérieur du rectangle de carte mais hors de la grille de collision existante, `GroundMap.findWalls` a émis des `IndexOutOfRangeException` répétées. Les murs de l’entrée semblent arrêter le déplacement ordinaire avant cette limite dans le modèle : **le test ne prouve pas qu’un joueur y parvient à pied**. L’erreur de structure et le risque lors d’une téléportation ou d’un futur accès sont néanmoins réels.

### 3. Source irisée — cadrage à décider et à harmoniser

La Source fait **600 × 600 px**. Depuis l’entrée sud, avec suivi simple et sans interaction, le modèle voit au fil du déplacement environ **59,34 % du rectangle**. Les zones libres isolées comptées par le modèle comprennent du décor et du bassin : elles ne doivent pas être déclarées jouables sans examen visuel.

Le fichier sérialise un offset vertical de `−64`, mais le moteur le remet à zéro à l’entrée. Le script applique de nouveau `−64` **après** l’interaction avec la Source. Un essai moteur à personnage immobile `(292, 320)` montre :

- avant décalage : centre caméra `(300, 328)` ; seule la partie basse de la colonne apparaît au bord supérieur ;
- après application de `(0, −64)` : centre `(300, 264)` ; davantage de colonne apparaît, mais pas nécessairement sa totalité.

Les deux captures sont dans le rapport interactif. Le banc a reproduit directement la commande de décalage, sans rejouer le menu ; le personnage de test affiché n’est pas un starter normal. **C’est une différence de cadrage confirmée, pas la preuve que le cadrage d’origine est forcément involontaire.** À valider selon l’effet souhaité pour l’escalier et la colonne pulsante.

### 4. `WaterfallVillageCapital` — grande carte, parcours pas encore certifiable

La carte mesure **1 600 × 4 000 px**. Une vue complète de 320 × 240 couvre au maximum **1,2 %** de son rectangle à la fois. Les **100 000 cellules de collision sont à zéro**, aucun objet fixe bloquant ni marqueur n’y est sérialisé. Le modèle optimiste obtient 100 % en supposant qu’on peut circuler partout ; ce chiffre **ne prouve pas** que les bâtiments, l’eau et les chemins sont réellement jouables ni que la carte est accessible dans le scénario.

**Recommandation :** garder la carte et ses dépendances intactes ; établir les vraies entrées et les collisions de parcours, puis reprendre la mesure sur les chemins effectivement prévus. Ne pas fusionner les cartes ni redessiner ce terrain pour résoudre un problème de caméra.

### 5. Autres points à vérifier

- `cliffdaytest/init.lua` emploie `MoveCamera(..., true)` avec de grandes coordonnées comme `(608, 476)` et `(716, 650)`. Le dernier argument `true` désigne un **décalage relatif au joueur**, et non une position absolue ; le dernier décalage n’est pas annulé avant la sortie de scène. Risque élevé de cadrage déporté, détecté dans le code mais non rejoué dans cet audit. Le fichier de cinématique nocturne contient des appels similaires ; son déclenchement effectif reste à établir.
- `destiny_clairiere_source_lumineuse` : le marqueur `entrance` visé par le retour de la Source chevauche des cellules bloquantes selon la position exacte de sa hitbox. Le modèle n’arrive pas à prendre cette entrée comme départ et présente seulement une simulation de la plus grande composante. Un précédent essai avait validé le passage retour ; ce signal n’établit donc pas à lui seul un blocage en jeu.
- Plusieurs cartes ont un bord apparemment franchissable dans les données statiques. Les déclencheurs, scripts ou usages en cinématique peuvent empêcher ou rendre sans objet cette sortie ; ce sont des **vérifications**, pas autant de défauts confirmés.

## Donjons fixes et étages générés

Le paquet comprend **123 cartes de donjon fixes**. Leur tableau séparé donne dimensions, terrain normal, entrée et couverture géométrique indicative : **121 simulées**, deux cartes en `Wrap` non simulées. **23** ont une vision de tuiles ou de personnages différente de « claire » ; la géométrie seule ne prédit donc pas leur visibilité réelle.

La carte fixe de la Quest `frozen_crucible` mesure **504 × 504 px**. À partir de son entrée 0 et sur le terrain normal statique, le modèle trouve **100 % des positions normales dans la même composante** et **89,66 % du rectangle** couverts géométriquement. Les bords restants peuvent être du décor/mur ; effets, créatures, scripts et usage scénaristique ne sont pas certifiés.

Les étages procéduraux, notamment les sept étages de `lost_wood`, ne peuvent pas être certifiés par une simple lecture des cartes fixes. Il faut générer plusieurs graines et parcourir les étages en jeu, avec leur brouillard et leurs effets.

## Méthode et limites

Pour chaque Ground au format cohérent, les murs `Tags=1/2` et objets activés, fixes et non passables sont pris en compte ; les personnages, les modifications de collision par script et les effets dynamiques ne le sont pas. Le centre de hitbox est échantillonné tous les 8 px, puis les positions sont regroupées par cheminement orthogonal. Pour l’entrée choisie, on réunit tous les rectangles de caméra 320 × 240 accessibles dans sa composante, en appliquant les règles de bord `Blank` ou `Clamp` du moteur. Les éventuelles autres composantes ne sont pas supposées atteignables d’une seule traite. Le tableau fournit aussi une union optimiste de toutes les composantes, à ne pas confondre avec un parcours unique.

La grille échantillonnée peut manquer des passages ou des positions au pixel près ; un déclencheur peut interrompre le chemin, une cinématique peut déplacer la caméra et des calques, masques, avant-plans, parallaxes ou brouillards peuvent occulter le décor. Les valeurs sont donc **des estimations géométriques**, pas un test exhaustif du rendu, de l’histoire ou de la qualité d’agrandissement des textures. Le moteur Linux a été utilisé pour les trois cas décrits ; le binaire Windows n’a pas été exécuté ici.

### Fichiers

- `AUDIT_CAMERA_DESTINY.html` : synthèse interactive, captures Source, schémas et filtre par carte ; utilisable hors ligne.
- `audit_grounds.csv` : tableau complet des Grounds du paquet.
- `audit_donjons_fixes.csv` : tableau des 123 cartes de donjon fixes.
- `preuves/` : journaux et captures de banc ; scripts d’audit et tests synthétiques conservés dans le dossier de travail.
