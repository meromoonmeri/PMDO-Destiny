# Réadaptation du Grand Cap : escalier et nuages — avant modification

## Demande

Le départ du Cap doit être la suite logique du grand escalier nord de Réverie : marches alignées au raccord, comme l'approche de la guilde de Grodoudou sur la référence T00P04A. Des nuages doivent se déplacer sur cette carte de guilde. Garder également le ciel et les 12 phases de mer nocturnes V24P01A précédemment demandés. La référence T00P04A reçue est un GIF 480 × 408 à quatre images de 100 ms : ses différences observées concernent le décor au sol ; le ciel/les nuages de cette image ne bougent pas. La dérive des nuages est donc une adaptation supplémentaire, pas une propriété attestée du GIF.

## Base et protection

Partir du candidat Grand Cap nocturne antérieur, sans modifier les projets ou sauvegardes utilisateur, les scènes, le Carrefour ni cliffdaytest. Créer une nouvelle copie et sauvegarder les fichiers originaux du candidat. La carte fusionnée `reverie_centre` se termine en haut au milieu du grand escalier : le parcours doit reprendre au bas du Cap, non arriver directement au milieu d'un plateau nu. Respecter les collisions et prévoir une entrée/retour du duo. L'identité de la future guilde de Destiny et son intérieur ne sont pas définis : ne pas coller arbitrairement la guilde de Grodoudou comme bâtiment définitif, ni prétendre que son accès futur est terminé.

## Méthode et risques

Étudier les marches et murs provenant du rendu géographique de Réverie, les disposer de façon centrée au bas du Cap avec une sortie vers le plateau, en respectant l'échelle des pixels et en vérifiant le franchissement par deux acteurs. La source de ville rendue est diurne, le candidat est nocturne ; la continuité des couleurs et le branchement jour/nuit devront être réglés avant intégration. Ne pas prétendre que des pixels recolorés sont natifs.

Ajouter, en couches de fond indépendantes, des nuages nocturnes du projet avec défilement lent par `MapBG.BGMovement`, modèle déjà présent sur cliffdaytest_nuit ; laisser inchangée la mer V24P01A et ses 12 phases. Le GIF T00P04A sert de référence de composition, non de copie du bâtiment ni d'indication de mouvement. Les raccords à la bordure et l'apparition des nuages exigent un contrôle caméra réelle, pas seulement une maquette. Les collages depuis un rendu aplati et les positions de collision sont à vérifier avec précaution ; préserver originaux et ne pas écraser le travail précédent.

## Validation prévue

Comparer les données inchangées, tester tuiles et collisions, vérifier l'enregistrement et la cadence des couches, fournir un aperçu complet clairement marqué hors moteur et une capture moteur uniquement si obtenue. L'essai précédent Réverie → Cap et retour complet n'a pas été validé ; un processus a été tué sous pression mémoire. Ne pas présenter ce raccord comme prêt à publier tant que le duo, les sauvegardes, l'accès futur à la guilde, les scènes, les variantes jour/nuit et le gameplay réel ne sont pas testés.
