# Audit de la cinématique de Réverie

## Périmètre

Visite du centre depuis l'arrivée jusqu'à la fin de l'alerte de Lyra, version 0.5.3 (`64106fc`). Les scènes des Bois Perdus et des autres lieux n'ont pas été réécrites. Audit du script et de ses API, pas visionnage en jeu : le rythme et le rendu des sprites restent à valider manuellement.

## Observations et reprise

| Moment | Constat | Reprise préparée |
|---|---|---|
| Accueil | Dracaufeu s'adresse au partenaire sans que le duo regarde explicitement le locuteur. | Le héros et le partenaire se tournent vers Dracaufeu en décalé. |
| Place et guilde | Lombre et Ludicolo regardent arbitrairement vers le bas ; leurs interlocuteurs ne suivent pas systématiquement. | Regards adressés entre les personnages ; l'hôte indique brièvement le nord puis reprend l'échange. |
| Présentation des boutiques | Partenaire hors champ et marchands dans leur propre plan. | Conservée : pas de geste forcé du duo hors champ ni de déplacement des marchands. |
| Cri et arrivée de Lyra | Réactions collectives déjà désynchronisées, mais les proches ne se tournent pas explicitement vers Lyra à son arrivée. | Réactions collectives conservées ; regards des proches vers Lyra, puis Lyra vers le partenaire qui la questionne. |
| Guilde absente et proposition | Les échanges changent de locuteur alors que plusieurs personnages conservent leur orientation précédente. | Regards des proches vers Lombre, puis vers le partenaire volontaire et Tyranocif ; le héros conserve son geste d'accord. |
| Arrivée d'Alakazam | Le cadrage précédent plaçait son point d'arrêt sur la bordure gauche du plan de 320 px ; Lyra n'était pas dans le groupe tourné vers lui. | Caméra recentrée ; Lyra rejoint les auditeurs. L'emplacement exact des sprites à l'écran doit être vérifié dans le moteur. |
| Réponse et remerciement | Les interlocuteurs restent tournés vers Alakazam quand le partenaire puis Lyra parlent. | Alakazam et les proches regardent le partenaire ; Lyra baisse brièvement les yeux avant de remercier l'équipe, puis les regards reviennent vers elle et Alakazam. |
| Retour libre | Risque de casser le choix de préparation, les positions ou la musique. | Aucun changement aux dialogues, déplacements, musiques ou états de progression. |

## Contrôles et limites

- Deux scripts ville et ville `_Dev` identiques. Comparaison des 50 appels de dialogue, des sons, des 13 appels de placement/déplacement et des trois affectations d'état : identiques à la base.
- Tests sur doublures : plusieurs espèces de partenaire, carte historique et centrale, absence d'Alakazam ou de Tyranocif, partenaire absent et trajet obstrué ; conservation des choix Lyra/Nilo. Cibles de regard et décalages vérifiés. Le module de regards réel a aussi été exercé avec un ordonnanceur simplifié.
- Les doublures ne reproduisent ni les durées exactes des coroutines, ni les animations/sprites, ni le comportement de la caméra et des collisions en jeu. L'expressivité et le tempo doivent être jugés dans une partie réelle avant de les considérer validés.
- Le guide relu recommande de laisser respirer les actions importantes, de désynchroniser les réactions de groupe et d'éviter la suranimation. Sa copie locale a été utilisée ; son lien Google Docs renvoyait 404 lors de la vérification précédente.

Sauvegarde préalable : `sauvegarde-avant-gestes.zip`, contrôle CRC réussi. Aucune sauvegarde de partie n'a été modifiée.
