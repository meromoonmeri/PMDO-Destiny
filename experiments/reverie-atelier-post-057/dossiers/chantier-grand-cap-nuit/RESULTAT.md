# Grand Cap panoramique nocturne — candidat et test moteur

## Ce qui est préparé

- Carte distincte `grand_cap_panoramique_nuit`, basée sur la version historique du Grand Cap panoramique du 21 octobre (`9bac5c1`). Le terrain, les collisions, les cinq calques restants, les entités et le marqueur d’entrée de la source sont conservés. Le premier calque historique, qui mélangeait le fond et une partie du bord de falaise, a été remplacé par un fond et deux calques de raccord extraits des calques nocturnes originaux à la même échelle, sans recoloration.
- Fond issu de [V24P01A](https://projectpokemon.org/home/gallery/image/77603-v24p01apng/) : l’original téléchargé est un APNG **312 × 240, 12 phases de 133,33 ms**. Les 12 images sont présentes intactes à 1× ; ciel prolongé par bandes d’étoiles et mer prolongée et répétée pour le format de la carte ; horizon aligné à y=296. Cadence PMDO proposée : **8 ticks par phase**. La répétition horizontale peut produire des raccords ou motifs visibles : à peaufiner et contrôler selon la caméra.
- La zone est encore une falaise nue, conformément au Grand Cap de la galerie : aucun chemin, bâtiment ou personnage d’histoire n’a été ajouté ou supprimé ailleurs.

## Test en jeu

La carte et le fond ont été chargés dans une **copie isolée** de Destiny avec le moteur Linux PMDO 0.8.12. Un accès technique temporaire a court-circuité le quiz ; le personnage de test est donc Missingno. Déplacement depuis le marqueur `Entrance` vers le bord nord : constaté. Le ciel et la mer sont visibles ; 24 captures successives ont été assemblées en `apercu/grand-cap-vrai-jeu-anime.gif`, avec 14 images distinctes relevées dans la zone de mer. La capture est un rendu du moteur, pas la maquette.

`apercu/grand-cap-nuit-anime.png` et `apercu/grand-cap-nuit-phase-01.png` montrent quant à eux la carte entière recomposée **hors moteur**, utile pour voir le layout complet. Ce ne sont pas des captures en jeu.

## Raccordement préparé après confirmation

Le grand escalier est celui du **nord de Réverie vers la guilde**, pas l’escalier du Carrefour. Sur la carte fusionnée actuelle, ses marches atteignent le bord supérieur à x≈736–808 et y=0. Un capteur Touch candidat à cet endroit envoie vers `grand_cap_panoramique_nuit`, dans la zone `town02_waterfallvillage` ; un capteur au bord sud du Cap prépare le retour vers `reverie_centre`. Les positions de retour (760,32) et (784,32) et d’entrée du Cap (592,800 et 616,800) sont libres au contrôle statique des obstacles. Les anciens numéros et l’ordre des 23 cartes dans la zone et son index sont préservés : la nouvelle carte est ajoutée en 24e position. La carte et le trajet `cliffdaytest` n’ont pas été modifiés. Pas de porte de guilde ou de bâtiment inventé : l’organisation du futur accès à la guilde reste à concevoir et valider.

Un premier démarrage isolé sur Réverie a chargé la carte et enregistré l’événement Touch `SortieGrandCap` dans le journal moteur, mais le test s’est retrouvé sous forte pression mémoire et a été interrompu avant de valider le trajet aller. Dans un second essai, l’accès direct technique au Cap a enregistré `RetourEscalierNord` ; après une commande vers le sud, le journal confirme la sortie du Cap et le début du chargement de `reverie_centre`. Le processus a ensuite été tué lors de l’initialisation de Réverie ; la position finale et l’arrivée à l’écran ne sont donc pas démontrées. Les fenêtres de chargement capturées ne valent pas preuve visuelle du trajet. Journal : `test-raccord-journal-extrait.txt`. Les deux essais utilisent le personnage technique Missingno seul, pas le héros et son partenaire.

Le script candidat prévoit la recréation du partenaire à côté du héros et sa conservation au chargement s’il est déjà présent, avec vérification des obstacles ; cette dernière révision **n’a pas encore été testée dans le moteur**. L’aller complet, le retour complet, le suivi du partenaire, les sauvegardes, les scènes, la musique et Windows restent à valider. Le seul visuel nocturne préparé est actuellement la destination du capteur quel que soit le moment de la journée ; ne pas intégrer tel quel si le jeu doit choisir une version jour/nuit. La cohérence avec la guilde future et les raccords visuels restent à valider.

## Installation et sécurité

Les fichiers `candidat/` ne sont **pas installés dans le projet utilisateur et ne sont pas une version validée**. Les scripts et l’index/zone nécessitent une fusion avec les autres travaux avant publication, pas un remplacement aveugle. `sauvegarde-raccord-057.zip` contient les fichiers originaux de zone et de script ville ; CRC vérifié. L’index de tuiles original pèse 191 Mo et n’est pas stocké dans ce dossier : `construire-index-tuiles.py` crée une copie candidate uniquement à partir de l’index exact v0.5.7, vérifié par SHA-256, sans écraser la source. Les tests ont été effectués uniquement dans une installation jetable sans sauvegarde utilisateur. Aucun push ni publication.

La source Project Pokémon est issue de Pokémon Donjon Mystère ; les droits de redistribution ne sont pas établis.
