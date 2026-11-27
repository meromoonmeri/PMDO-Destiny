# Créer une capacité Z dans PMDO — méthode de travail

## 1. Travailler sur une copie / un mod

La copie examinée est Destiny 0.7.8 avec données de moteur PMDO 0.8.12. Toujours sauvegarder les fichiers et travailler dans un mod ou un banc isolé, pas directement sur une sauvegarde de joueur. Les 35 fiches Z existent déjà : commencer par la fiche correspondante, ne pas créer un second identifiant concurrent. Elles ne sont pas activées (`Released: false`) dans la copie examinée.

## 2. Créer les visuels

1. Définir pour chaque capacité sa chorégraphie : préparation, mouvement de l'utilisateur, trajectoire, effet sur cible, fin et son. Vérifier la source de référence ; les signatures ont parfois besoin de sprites propres au Pokémon, les génériques doivent fonctionner avec plusieurs espèces.
2. Séparer les couches : charge autour du lanceur, projection directionnelle, impact sur la cible et éventuels éléments de décor. Distinguer les animations du Pokémon des effets VFX. Pour un statut Z, concevoir l'activation commune et conserver la capacité de base ; ne pas inventer automatiquement 239 effets exclusifs.
3. Dessiner les poses dans les huit directions utiles : bas, bas-droite, droite, haut-droite, haut, haut-gauche, gauche, bas-gauche. Une animation réellement radiale peut être mutualisée ; si l'effet indique une direction, ajuster sa perspective et vérifier toutes les orientations. Une rotation automatique ne garantit pas une belle vue pixel art.
4. Exporter des PNG transparents ; conserver les sources, les dimensions par image, l'ancrage, l'ordre de lecture, les durées, les crédits et les tests. L'éditeur PMDO attend pour les VFX un nom tel que `Nom.Dir8.png` : huit directions empilées verticalement, cellules carrées et images sur la largeur. Autres formats documentés : `Dir5`, `Dir2`, `Dir1`, `Flip`, `None`, ou dossier avec `DirData.xml`. Vérifier l'ordre exact à l'import avec des flèches repères avant de produire le lot.
5. Importer dans l'éditeur de sprites/particules du mod, inspecter l'animation puis vérifier le `.dir` obtenu. Ne pas supposer qu'un PNG ou un `.dir` isolé rende déjà la capacité jouable.

## 3. Configurer la fiche de capacité

Dans le mode développeur, ouvrir la liste des capacités et la fiche existante. Suivre le tutoriel officiel « Creating Moves » :

- `Name`, description et `Released` seulement lorsque l'implémentation est prête ; charges et autres paramètres selon le design retenu.
- `HitboxAction` : portée et forme de l'action (`AttackAction`, projectile, déplacement, etc.), animation du personnage (`CharAnim`), cibles et obstacles. Les 35 fiches examinées sont des points de départ, pas des mouvements Z déjà validés.
- `ActionFX` : effet de lancement, son et éventuel tremblement. `Explosion` : zone d'effet si nécessaire. Dans `Data`, régler type, catégorie, précision, états et événements ; `HitFX` pour l'impact et son son.
- Pour les dégâts, le tutoriel utilise `BasePowerState` et `DamageFormulaEvent` en priorité -1. Les attaques de statut et les signatures ont d'autres effets ; ne pas leur attribuer automatiquement une formule de dégâts.
- Tester d'abord avec le bouton de test de l'éditeur, puis en situation réelle : un test d'émetteur seul ne valide pas une capacité complète.

## 4. Ajouter la mécanique Z

La fiche visuelle seule ne suffit pas. Il faut concevoir puis tester la détection de l'objet, la compatibilité de la capacité et de l'espèce/forme, l'éventuelle conversion de puissance et catégorie, l'interface, les effets de statut et la limitation d'usage. Les règles de la série principale servent de référence mais ne précisent pas directement leur adaptation aux tours et aux étages d'un donjon PMDO. Vérifier toutes les interactions et la persistance, notamment changements d'étage et sauvegardes. Aucun de ces mécanismes n'est déclaré implémenté ici.

## 5. Validation avant livraison

Pour chaque capacité : huit captures ou vidéo en jeu selon les orientations ; mouvement vers la cible ; collisions et limites de carte ; superposition devant/derrière lanceur et cible ; durées, son, impact, cible et dégâts/effets ; conditions d'accès et limite d'utilisation ; absence de régression sur plusieurs Pokémon et tailles. Suivre les prototypes et leurs limites dans le CSV : les tests scriptés ne valident pas une capacité jouable.

## Documentation

- https://wiki.pmdo.pmdcollab.org/Creating_Moves
- https://wiki.pmdo.pmdcollab.org/Modding_Objects_and_VFX
- https://wiki.pmdo.pmdcollab.org/PMD_Sprite_Format
- https://wiki.pmdo.pmdcollab.org/Scripting_Cheat_Sheet
