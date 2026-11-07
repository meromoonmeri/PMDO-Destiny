# Réverie — arrivée, café et actualité des habitants

## Modifications locales en cours

- À l'arrivée du duo, Lombre et Ludicolo approchent par deux trajets vérifiés, puis regagnent leur position ; Dracaufeu et Tyranocif restent fixes. Si le passage est occupé, l'approche concernée est sautée. La discussion sur la guilde précède l'appel de Lyra. Sa demande progresse du cri jusqu'à la chute de Nilo et à l'échec de sa tentative ; aucune réplique de la référence n'est copiée.
- Les grands panoramiques de la visite ont des durées augmentées selon la distance. La caméra de l'accueil du café est rendue au héros avant le fondu, puis cadrée sur la présentation ; aucune validation visuelle en moteur n'a été faite.
- À la première entrée à l'accueil, Spinda s'avance si le passage est libre ; le partenaire choisi prend la réplique initiale, Kirlia/Alizé explique qui il est, puis le héros réagit. La séquence est mémorisée après sa conclusion. S'il manque un acteur, elle est différée. L'accueil reste ouvert pendant les travaux, tandis que l'escalier et les raccourcis vers les salles sont fermés tant que `CafeRenovationTerminee` n'est pas vrai ; les salles et les chemins de retour restent conservés. La sieste reste proposée.
- Le fondu entrant est fait avant l'initialisation facultative du suivi, qui est protégée : si celle-ci échoue, son erreur est journalisée et le fondu a déjà eu lieu. La cause précise de l'écran noir rapporté n'est pas connue, et son élimination n'est pas démontrée par cette modification.
- Après l'alerte de Nilo, les habitants de Réverie concernés et les employés Spinda/Kirlia réagissent à la situation. Les marchands et services restent accessibles ; les paroles quotidiennes reviennent si l'alerte n'est pas active. Aucun sauvetage n'est déclaré. Les événements futurs non implémentés ne possèdent pas encore de dialogues contextuels.

## Capture 25

Correspondance forte (~0,945 ; ×2) autour de (698,818), pied de l'escalier de la guilde. Le raccord à gauche à y=904, visible coupé dans la capture, a déjà été retouché en v0.5.3 : la carte actuelle utilise les neuf cellules de la banque `Reverie_Berges_053`, chacune en quatre phases. Voir `capture25-avant-apres053.png` : reconstruction statique avant/après, pas un rendu du moteur. La capture ne désigne pas une autre anomalie précise ; pas de suppression spéculative. Les captures 22 et 24 et l'audit de tous les défauts similaires restent partiellement ouverts.

## Vérifications

Sauvegardes préalables contrôlées : `sauvegarde-avant-arrivee.zip` et `sauvegarde-avant-cafe-camera-dialogues.zip`. Syntaxe Lua contrôlée ; tests sur doublures : visite, cinq partenaires, acteurs absents, chemin obstrué, choix de Lyra, dialogues et banque, introduction unique du café, chemin bloqué, suivi en erreur, retour de l'étage, escalier fermé et réouverture future ; contrôles statiques de trajectoires sur deux cartes de ville et sur la carte du café. Les tests ne remplacent pas une partie ni des sauvegardes réelles. Les déplacements de personnages pendant les trajectoires et le rendu des grands sprites ne sont pas simulés.

## État de publication

Travail local non publié ; la branche distante reste à vérifier avant tout push. La dernière version confirmée publiée est v0.5.4. Publication d'une version complète et CI Windows en attente d'une nouvelle autorisation GitHub. Ne pas transmettre de jeton dans la conversation ; révoquer celui qui a déjà été exposé.
