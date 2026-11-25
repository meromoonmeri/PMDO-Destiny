# Réverie — audit des entrées, du dojo et des intérieurs de guilde

## Demandes confirmées

- L’intérieur nouvellement généré avec les textures Ledian doit être relié au **grand dojo au nord-est**, anciennement raccordé au dojo Kingambit.
- Les banques Ledian déjà présentes peuvent être utilisées. L’utilisateur déclare en être le créateur et confirme son autorisation. Leur égalité avec les fichiers présents dans Halcyon ne démontre pas que Halcyon en est l’auteur.
- Retirer les accès attribués à Arcanine et à la supposée maison de l’équipe, sans effacer leurs extérieurs. La maison citrouille nord est l’auberge.
- Utiliser les ouvertures encadrées dans les images 5 à 7 pour situer les entrées ; ne pas attribuer arbitrairement un intérieur à une structure non identifiée.
- Retirer du projet actif les intérieurs de guilde appartenant à Halcyon ; conserver les sauvegardes historiques et la 0.4.11 intactes.

## Ce qui est fait localement

Une sauvegarde ciblée des ressources d’origine, contrôlée par CRC et SHA-256, est disponible dans `sauvegarde-avant-corrections-portes-guilde.zip`. Les copies supplémentaires du modèle `reverie_inn` et les sources moteur consultées n’y sont pas incluses car elles sont uniquement lues et non modifiées.

Les trois images annotées ont été recalées sur le rendu 11 couches d’origine : 1 875, 1 253 et 828 points concordants respectivement. Résultat détaillé dans `travail-corrections-reverie/calage-images.json`. Les coordonnées sont indicatives, sujettes à l’arrondi et à vérification en jeu.

Une proposition de dojo se trouve dans `Dojo-Reverie-proposition.png` et dans `Reverie-entrees-et-dojo-proposition.html`. La carte expérimentale `dojo_reverie.rsground` et son script se trouvent dans `travail-corrections-reverie/proposition/`. Ils ne sont ni intégrés à la zone, ni publiés. Le générateur assemble directement les banques autorisées et ne lit pas la carte Halcyon `ledian_dojo`. La forme des planches préassemblées reste toutefois reconnaissable : elle n’est pas présentée comme une création graphique entièrement originale. Les tapis et torches sont disposés différemment ; le personnage et les dialogues du dojo Kingambit actuel sont conservés dans la proposition. Le rendu PNG ne montre pas les personnages ni l’animation.

Tests statiques : 2 432 références de frames présentes dans les banques, 42 cases animées, syntaxe Lua vérifiée, dimensions et objets dans les limites, cheminement approximatif 16 × 16 entre départ, partenaire, personnage et sortie. Ces vérifications ne remplacent pas l’ouverture, le rendu, l’interaction et les tests de sauvegarde dans PMDO 0.8.12.

## Seuils et collision

En coordonnées de la carte originale (pixels), les rectangles suivants sont des estimations des cadres fournis :

| Structure | Rectangle approximatif x min–max ; y min–max | Intérieur |
|---|---|---|
| Poste Bekipan | 53–87 ; 462–504 | `reverie_post_office`, liaison existante |
| Auberge nord | 393–450 ; 546–586 | `reverie_inn`, destination confirmée par l’utilisateur |
| Hutte nord-est | 1043–1087 ; 591–637 | `reverie_water_home`, liaison existante à valider |
| Grand dojo | 1438–1490 ; 346–391 | `dojo_reverie`, proposition non intégrée |
| Hutte du sud du centre | 603–645 ; 1668–1718 | `reverie_electric_home`, liaison existante à valider |
| Maison de pierre | 440–478 ; 2295–2328 | `reverie_rock_home`, liaison existante à valider |
| Maison plante sud | 563–600 ; 2478–2518 | `reverie_grass_home`, liaison existante à valider |
| Citrouille sud | 755–805 ; 2502–2537 | `reverie_fire_home`, liaison existante à valider |
| Café Spinda | 1053–1092 ; 1323–1370 | `caféspindaaccueil`, correspondance de zone vérifiée |

Un contrôle des cases de collision de la carte 0.4.11 montre que de nombreuses ouvertures sont sur des cases bloquantes. Le moteur interroge les objets à **un pixel devant le rectangle du personnage** (`GSceneMap.ProcessObjectInteract`, `GroundAction.HITBOX_WIDTH/HEIGHT = 16`). Un simple rectangle réduit au noir peut donc être inatteignable. Pour la hutte du sud du centre, les cases situées juste sous l’ouverture restent notamment bloquées sur une longue distance. Il faut choisir et tester une solution qui garde le repère sur l’ouverture tout en permettant l’interaction depuis un emplacement accessible, sans supprimer les collisions utiles, et vérifier le retour du partenaire. Aucune correction de collision ni de marqueur n’a été appliquée.

Les autres portes annotées sans correspondance confirmée ne reçoivent pas de destination inventée. Les associations existantes des tentes, en particulier l’ancienne liaison vers `reverie_inn` et celle vers le dojo Ledian, demandent une décision explicite avant toute réaffectation.

## Retrait des intérieurs Halcyon : précautions

`guild_storage_room.rsground` est identique à la carte de Halcyon ; `guild_heros_room.rsground` utilise des banques `Guild_Heros_Room_*` identiques à celles de Halcyon. Les deux sont présents dans la liste `GroundMaps` de `town02_waterfallvillage` aux indices 13 et 14 ; les scripts qui y correspondent et l’accès attribué à la maison de l’équipe sont également à traiter.

La suppression brutale de ces deux entrées déplacerait les indices suivants et pourrait affecter des sauvegardes ou les destinations enregistrées. Prévoir une migration ou un mécanisme de récupération testé, en particulier pour les joueurs sauvegardés dans une carte retirée ; ne pas prétendre qu’une simple suppression dans le tableau est compatible. La 0.4.11 historique et les sauvegardes d’audit doivent rester inchangées.

Les 48 cartes `game/Data/Ground` du relevé Git ont été recherchées en flux pour les banques de guilde, avec vérification de leurs SHA Git : les banques dédiées `Guild_Heros_Room_*` et `Guild_Storage_Room_*` apparaissent dans leurs intérieurs respectifs. **La banque `Guild_First_Floor.tile` est aussi utilisée par `cliffnordouesttest1_nuit.rsground`**, déclarée dans `destiny_cliff_tests` : son retrait aveugle casserait cette carte. Les textures sont déclarées appartenir à l’utilisateur, contrairement aux intérieurs de guilde. Il ne faut pas détruire une ressource partagée au seul motif de son nom. D’autres catégories de références et l’index global des tuiles doivent encore être vérifiés avant retrait effectif.

## État de publication

Aucune carte ou script du jeu actif n’a été modifié ; aucun intérieur n’a encore été retiré du dépôt. Aucun commit, tag, release ou CI n’a été produit pour ces corrections. Le jeton GitHub précédemment utilisé n’est pas disponible dans cette session. Les tests réels PMDO n’ont pas été réalisés. L’aperçu et la carte générée sont des propositions de travail, pas une mise à jour jouable validée.
