# Réverie : falaises, cascades et proposition de bassin

## Fichiers

- `correctif-falaises-et-cascades-Reverie-0.5.0-ESSAI.zip` : correctif sources cumulatif ; il remplace les correctifs locaux précédents d'herbe et de chemins. Il est basé sur le commit officiel `a2db214dc89e675347f670f26594df92158fc9d9`. SHA-256 `edbe07231d89fb72829adb79402b3a92a59f2d978e21295ce8dc9c319d82a6a1`.
- `avant-apres-falaises.png` : échantillon des trous transparents réparés. Le rose correspond aux zones transparentes sur fond de contrôle ; la grande bande rose à gauche de la première image est hors carte.
- `avant-apres-cascades-anime.gif` : rendu de données sur six secondes, sans personnages, avec temps PMDO simulé. La première ligne montre la cascade derrière Kecleon et son écume ; la seconde l'écume de la cascade sud.
- `apercu-bassin-sud-avant-apres.png` : proposition non installée, pas une map ni un sol final validé ; son contour est une maquette pixel-art.
- `sauvegarde-avant-chemins-0.5.0.zip` : sauvegarde des ressources officielles avant ces interventions.

## Falaises et buissons

Une recherche sur les transparences du rendu a repéré 38 composantes courtes. Les deux proches de l'eau et une proche de la limite de carte ont été laissées de côté. Les 35 restantes ont été reprises sur des cases sans animation aux emplacements concernés : 171 pixels transparents de falaises/raccords sont remplis avec les pixels Réverie opaques voisins, sans interpolation ni inventer de couleur. D'autres imperfections ou problèmes de texture peuvent subsister. La recherche sur une famille de petites touffes a confirmé un fragment déjà restauré et un autre simplement caché par un arbre ; l'arbre et son occultation n'ont pas été altérés. Ce test ne couvre pas toutes les espèces de buissons.

## Cadences et vérifications

- Cascade Kecleon : 32 séquences par carte, `FrameLength` 10 → 6.
- Quatre groupes d'écumes : 311 séquences par carte, `FrameLength` 60 → 20. Aucun autre type d'animation n'a été volontairement accéléré ; toutes les images, leur ordre, et les images vides/répétées sont conservés. La cadence est plus rapide, mais aucune image intermédiaire n'a été créée.
- Dix cartes contrôlées ; 94 cases avec retouches graphiques et 62 tuiles nouvelles au total ; 2 058 pixels graphiques changés par carte, y compris le travail précédent. Les éléments hors colonnes transformées sont conservés octet pour octet ; un contrôle des colonnes transformées confirme que les seules différences sont les ajouts graphiques ciblés et changements de durée ci-dessus. Les scripts, collisions, objets et cadres d'animation existants ne sont pas modifiés.
- CRC de l'archive et contenu des nouvelles tuiles vérifiés. Pas de validation dans PMDO, ni en partie, ni sur sauvegarde réelle, ni de CI.

## Bassin sud — non inclus dans le correctif

La cascade et son écume sont au-dessus de la maison-plante autour de x288–351 et y1888–2047. Conformément au choix « aperçu d'abord », seul un dessin de proposition a été produit ; il n'est pas intégré à la map et aucune collision n'a été modifiée. La maquette évite visuellement de masquer l'entrée et les décors, mais sa forme et ses contours devront être affinés en tuiles Réverie.

La proposition recouvre au moins un pixel de 45 cases de terrain ; dans `reverie_residentiel` et `WaterfallVillageCapital`, 38 de ces cases ont actuellement `Tags=0`, contre 7 non nulles. Dans `reverie_centre`, ces 45 cases ont un tag non nul. Un éventuel bassin bloquant changerait donc potentiellement la circulation dans les cartes résidentielles. Ce seul comptage ne teste ni les objets, ni les PNJ, ni le trajet de la porte, ni la physique du moteur ; ces points devront être vérifiés avant intégration.

## Publication

Aucun accès GitHub en écriture n'était disponible, donc **pas de push ni de CI**. `pousser-correctif-falaises-eau.py` est prêt pour une utilisation avec un jeton limité au dépôt transmis par un mécanisme sécurisé en variable `DESTINY_TOKEN` ; il vérifie l'empreinte de l'archive et refuse si la branche a avancé. Il ne publie pas le bassin de prévisualisation. Il faut confirmer le résultat et la CI après exécution. Avant installation, suivre le LISEZ-MOI du ZIP et régénérer l'index sur un checkout complet.
