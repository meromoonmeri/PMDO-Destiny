# Rapport préalable — café, caméra, réactions et capture 25

Base distante v0.5.4, commit 04ea6f0fd0f7d9303abd805c5ff43075c795c3d8. Le chantier non publié de l'arrivée des habitants est conservé séparément. Guide de cinématiques et API de caméra PMDO relus ; le café, le conteneur de zone, le suivi des intérieurs et la carte d'accueil ont été sauvegardés dans `sauvegarde-avant-cafe-camera-dialogues.zip`, contrôlée CRC.

## Constat
- Le café est la carte Ground n°2 ; son marqueur de départ est `NewObject_17` à (290,354). La porte appelle `GAME:EnterZone` après fondu noir. Le script d'entrée appelle le suivi puis le fondu entrant ; aucune partie réelle ne prouve à ce stade la cause de l'écran noir. Vérifier l'API et les conventions de transfert avant d'avancer un diagnostic.
- La capture 25 correspond très probablement au pied de l'escalier nord de la guilde, vers (698,818), agrandissement ×2 (corrélation environ 0,945 avec un rendu antérieur). Aucun cercle ni défaut précis n'est indiqué : la bordure et l'eau sont des zones à examiner sans effacer automatiquement des tuiles animées.
- Après la scène de Lyra, la plupart des habitants utilisent encore leurs variantes quotidiennes sans tenir compte de Nilo ; seul Léo possède actuellement une réaction explicite. Les systèmes de banque, commerce et dialogues doivent rester fonctionnels.
- La caméra de la visite saute entre plusieurs comptoirs ; le guide recommande des transitions lisibles et peu brusques, sans dérive involontaire sur l'axe secondaire. Faire attention aux limites et au retour de caméra sur le héros.

## Intervention envisagée et risques
Préserver le partenaire choisi : Bulbizarre ne peut être forcé si le joueur en a choisi un autre. Mettre sa réplique de surprise dans la bouche du partenaire réel et laisser Kirlia expliquer qui est Spinda ; le héros exprime sa réaction intérieure sans attribution erronée. Déclencher la présentation une seule fois, avec reprise normale, entrée et caméra sûres, sans créer un étage ou un service de café prétendument ouvert. Conserver les services déjà en place sauf lorsqu'ils contredisent explicitement la rénovation demandée ; traiter ce point avec prudence.

Ajouter des réactions liées à l'alerte et au départ accepté seulement si les états correspondants sont réellement établis ; ne jamais annoncer un sauvetage inexistant. Étudier les fragments de falaise et de berge sur les cartes réelles et leurs phases ; corriger seulement les raccords identifiés. Tester l'entrée initiale, retour depuis l'étage, chargement, acteurs absents, compatibilité des sauvegardes et les fonctions de service avec des doublures. Des contrôles statiques ou simulés ne remplacent pas une partie PMDO réelle, ni ne permettent de garantir que tous les défauts similaires ont été trouvés.
