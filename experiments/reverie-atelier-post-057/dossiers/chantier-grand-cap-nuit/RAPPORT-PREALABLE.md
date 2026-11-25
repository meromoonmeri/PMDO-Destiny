# Grand Cap nocturne — rapport préalable

## Demande et référence

Utiliser le Grand Cap panoramique comme zone accessible au-delà du grand escalier ; adapter à sa géométrie le ciel et la mer de la référence V24P01A, avec une animation nocturne. La source fournie par l’utilisateur est https://projectpokemon.org/home/gallery/image/77603-v24p01apng/ : le bouton Download fournit une image APNG 312×240 de 12 images de 133,33 ms, et non seulement la vignette statique du site. La ressource provient de Pokémon Donjon Mystère ; ses droits de redistribution ne sont pas établis.

## Base et conservation

La forme du Grand Cap provient de `cliff_centre_01_grand_cap_panoramique_nuit.rsground` du pack historique 9bac5c1. Sa carte fait 1200×880 pixels, 150×110 cases PMDO 8 px, avec un plateau existant, obstacles et point `Entrance`. Son ciel, ses étoiles et sa mer forment actuellement un calque de tuiles : remplacer seulement ce fond, en conservant les calques de terrain, le layout et les collisions de la carte indépendante. Ne pas toucher aux cartes de l’utilisateur ni effacer ses scènes et accès existants.

## Risques d’accès

Le Carrefour a déjà une sortie `SortieFalaise` vers `cliffdaytest`, et cette destination est liée à la maison de l’équipe et à des scènes. Réverie comporte plusieurs escaliers et l’escalier nord mène à la guilde fermée. Le seul terme « grand escalier » ne permet pas de choisir de façon certaine un déclencheur et sa destination : ne pas écraser `cliffdaytest`, ni la liaison du Carrefour, ni l’accès à la guilde. Préparer une zone séparée ; le raccordement exact devra être confirmé visuellement avant installation. Un aller et un retour doivent être définis et testés avec le partenaire sans couper les routes existantes.

## Adaptation

Conserver les 12 images originales et leur cadence (8 ticks à 60 FPS), sans interpolation ni recoloration. La mise à l’échelle horizontale et verticale du cadre n’est pas nécessaire : répéter à 1×, étendre le ciel et la mer par répétition, caler l’horizon sur celui du Grand Cap. Le raccord de répétition est à contrôler visuellement et ne doit pas être annoncé parfait sans test. Identifier et sauvegarder les fichiers de base, conserver l’APNG original, et comparer structurellement les calques et obstacles. L’aperçu indépendant n’est pas une capture de jeu ; tests moteur et dépendances doivent être établis séparément.
