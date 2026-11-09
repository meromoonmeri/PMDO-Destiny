# Réverie — mise à jour 0.5.1

* Poursuite de la visite avec l’alerte de Lyra et les choix de préparation ; Grotte Verdoyante non jouable, aucun faux accès au donjon.
* Habitants nommés ; Alakazam, Tyranocif, Dracaufeu et Spinda sont désignés par leur espèce. Rondoudou s’appelle Asa. Le héros et son partenaire gardent leur nom.
* Liaisons et retours des trois salles du café ; suivi du partenaire dans les intérieurs, menus système sans portrait, déplacement de Bekipan et dialogue de falaise corrigés. L’auberge de la maison citrouille est distincte et son îlot n’est pas raccordé à la place.
* Dojo de Réverie : Kingambit. Ancien raccord de la tente vers Ledian désactivé, capteur résiduel retiré. Les données historiques Ledian sont conservées pour les sauvegardes.
* Retouches locales de chemins, herbe et falaises sans déplacement de la géographie ; cadence de la cascade Kecleon et des écumes accélérée avec les mêmes frames ; pas de bassin.
* Deux ressources statiques `Content/Object/PMU_Table_bois_01.dir` et `PMU_Lampe_sur_pied_01.dir` issues de Tiles5 peuvent servir à des décorations `ObjAnimData`. PNG sources d’import : `art/reverie/objets_pmu/`. Elles ne sont pas placées sur les cartes.

## Limites

La conversion de l’ensemble des objets et animations PMU n’est pas achevée ; aucune animation PMU d’objet n’est validée dans ce lot. Il reste à identifier les objets complets, cadres, cadences, collisions et droits de redistribution. Les quêtes façon Halcyon et la décomposition sémantique des calques ne sont pas complètes. Le jeu, les sauvegardes réelles et l’éditeur n’ont pas été vérifiés manuellement ; les contrôles sont des simulations et tests statiques, en plus de la CI si elle réussit. Sauvegarder ses parties avant mise à jour.
