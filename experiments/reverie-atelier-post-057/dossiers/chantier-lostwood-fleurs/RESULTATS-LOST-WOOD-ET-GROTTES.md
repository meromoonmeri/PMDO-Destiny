# Lost Wood fleuri et recherche de grottes

## Recherche dans les dépôts et sur le Drive

Les noms **Marvelous Cave**, **Lush Cave** et **Lush Hollow** n’ont pas été trouvés comme noms de fichiers dans les arbres des branches principales consultées : `projet-creation-pmdo`, `projet-pmdo` (ses 12 sous-arbres), `town02`, `PMDO-Destiny`, `BIBLIOTHEQUE`, `zone-pmd`, `zone-pmdo`, `all-zone-PMDO-project`, `guilde-treehouse-pmd`, `new-era-project`, `new-era-abyss-to-ascension-V4`, `PMD-NewEra`, `PMD-RED-PMDO-PORT`, `PMD-SKY-PMDO-PORT`, `mypmdproject` et `WitchLittlewood-TO-Pmdo`. L’arbre de la branche Destiny utilisée pour la v0.5.7 a également été vérifié. Le nom seul peut ne pas refléter un contenu binaire ou une archive ; la recherche n’a pas couvert toutes les branches ni toutes les archives.

Sur Google Drive, les recherches par nom et les recherches textuelles exactes des trois expressions n’ont rien retourné. Cela ne garantit pas que le contenu de toutes les archives, tous les fichiers binaires ou toutes les images ait été indexé.

### Correspondances proches, mais différentes

- **[Lush Prairie / Prairie Luxuriante](https://drive.google.com/file/d/1LX72cQzE-0DAZmGOYKUncpxbTK1UpjfC/view)** : zone `lush_prairie_post.json`. Elle s’appelle Lush Prairie dans les données ; ce n’est pas une preuve qu’il s’agit de Lush Cave ou Lush Hollow. Son nom de niveau contient encore une référence « Dusk Forest » dans le texte lu : il faudrait auditer sa finition avant toute réutilisation. Aussi présente dans [`town02/Data/Zone/lush_prairie_post.json`](https://github.com/meromoonmeri/town02/blob/1efd098f92a0abcc892f40410db8249ecc9c9bb1/Data/Zone/lush_prairie_post.json).
- **[Marvelous Sea / Mer Merveilleuse](https://drive.google.com/file/d/1n9iWsezY-SdoJUyuREkcv8heMUZgP8xv/view)** : zone `marvelous_sea.json`, distincte de Marvelous Cave. Cette définition indique `Released: false`. Le [rapport de génération](https://drive.google.com/file/d/1O4H7pXZ7cDwZxLwhjchQeXJ3-EUTgcip/view) décrit 20 étages ; une autre version `new_era_zone_54.json` décrit une adaptation à 99 étages, à ne pas confondre. Aussi présente dans [`town02/Data/Zone/marvelous_sea.json`](https://github.com/meromoonmeri/town02/blob/1efd098f92a0abcc892f40410db8249ecc9c9bb1/Data/Zone/marvelous_sea.json).
- **[Mystery Cave / Grotte du Mystère](https://drive.google.com/file/d/1EjEEub2i7yPjVZF8d9u0GZSyjOjmSDi3/view)** : donjon New Era nommé `grotte_mystere.json`, également présent dans [`town02/Data/Zone/grotte_mystere.json`](https://github.com/meromoonmeri/town02/blob/1efd098f92a0abcc892f40410db8249ecc9c9bb1/Data/Zone/grotte_mystere.json). C’est une grotte différente ; sa disponibilité dans la sauvegarde n’établit pas qu’elle soit jouable dans Destiny.
- **[Fertile Valley / Vallée Fertile](https://drive.google.com/file/d/16xzB7TEQgh_yobUtoR1hcoi_efAzG9ME/view)** : autre zone verte de New Era, qui ne doit pas non plus être présentée comme Lush Cave.

Aucun de ces candidats n’est installé dans Destiny par cette recherche.

## Lost Wood : base conservée, fleurs à la place des ruines

La version de référence est Destiny v0.5.7, commit `ee39156a24f350b67e81740478be8505f4ff1a05`. Les essais de remplacement DTEF par Relict/Amapola ne sont **pas utilisés**.

Dans la copie candidate :

- Suppression des étapes de placement des six types de ruines sur les **14 générateurs** des deux segments de sept étages. Les fichiers de ruines ne sont pas effacés : ils restent archivés et disponibles pour d’éventuelles autres références.
- Ajout de cinq fleurs et buissons fleuris natifs de Destiny (`Flowers_Town_1` à `_5`), en décors sans collision. L’aperçu `choix-fleurs-natives.png` montre ces cinq graphismes ; **il ne montre pas un étage généré en jeu**.
- Fleurs réservées aux sols libres, éloignées des murs, des escaliers/effets déjà présents et des couloirs identifiés. Leur répartition calculée ne consomme pas de nouveaux tirages aléatoires dans le script. Le retrait du placement des ruines modifie cependant la consommation aléatoire précédente : les étages générés ne seront donc pas identiques à ceux d’avant, même avec une même graine.
- Autotiles, rivière, chemins, galets, lucioles, musiques, événements et sorties restent inchangés dans les données et le script de base, hors suppression des étapes de ruines et ajout du bloc floral. Pas de recoloration ni de changement du DTEF.
- Le test existant qui exigeait des ruines a été adapté pour vérifier au contraire leur absence sur les deux segments, tout en conservant les contrôles des ressources d’origine.

### Contrôles et limites

- Comparaison structurelle complète de la zone : seules les 14 étapes de placement des ruines ont été retirées. Le script est identique à l’original après retrait du seul bloc floral ajouté.
- Exécution Lua sur une carte doublure : terrain, couches de sentiers/galets, lucioles et état aléatoire identiques au script original sur cette même carte ; 50 fleurs non bloquantes placées sur cette simulation, sans présence sur les couloirs ou les effets testés.
- Test adapté des 14 étages et test du DTEF Treehouse d’origine : réussis dans un environnement local isolé. L’index de tuiles réduit utilisé pour ce test n’est pas un index de jeu et n’est pas livré.
- **Pas de génération réelle dans PMDO, de contrôle graphique Windows, de CI ou de sauvegarde de joueur testée.** Des apparitions ultérieures pourraient visuellement se superposer à une fleur ; une sauvegarde déjà dans un étage généré peut en garder la disposition. Les collisions et positions en jeu restent à vérifier.

La sauvegarde originale vérifiée est `../chantier-lostwood-amapola/sauvegarde-lostwood-057.zip`. La copie de travail se trouve dans `candidat/`. Les changements ne sont ni installés dans le jeu ni publiés ; une session GitHub autorisée sera nécessaire pour la prochaine mise à jour.


## Essai moteur ultérieur : aperçu de l’étage

Une copie isolée de la v0.5.7 a été lancée avec le moteur Linux PMDO 0.8.12 et les deux fichiers candidats. Un raccourci temporaire dans la copie a amené une nouvelle partie directement en 1F, sans utiliser de sauvegarde de joueur ; l’animation du titre a été désactivée dans cette copie pour réduire la consommation mémoire. Le moteur a effectivement généré et affiché `lost_wood`. Capture réelle recadrée : `LostWood-capture-reelle-1F.png`. Le personnage de test est Missingno (1 PV), car le quiz a été contourné.

Sur la graine de test 4236241353887920669, l’instrumentation temporaire a compté seulement trois décors floraux (Flowers_Town_5 aux cases 6,5 et 7,20 ; Flowers_Town_4 à 21,31). Ils ne sont pas clairement visibles sur la capture initiale : cette image ne valide donc pas l’aspect fleuri. Ce seul étage Linux ne valide ni les 14 étages, ni les sauvegardes, ni Windows ; la densité et le rendu doivent être vérifiés avant publication. Aucun de ces changements de diagnostic n’a été appliqué au candidat livré.
