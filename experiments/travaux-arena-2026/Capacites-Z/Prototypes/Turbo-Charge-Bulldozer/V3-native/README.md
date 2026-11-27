# Turbo-Charge Bulldozer — V3, banc natif

## Ce qui a été créé

- Deux séquences distinctes, charge et impact : 18 poses chacune, 8 directions, en deux calques. Chaque pose est dessinée par le script `Sources/turbo-frame-par-frame.py` à partir de paramètres temporels et directionnels. Ce n'est **pas** une génération IA indépendante pour chaque image ; c'est du pixel art produit par algorithme image par image. Les effets au sol gardent la perspective horizontale.
- Fiche expérimentale `breakneck_blitz-test-only.json` produite à partir de la fiche d'origine et de mécanismes natifs PMDO : `DashAction`, arrêt à l'ennemi et au mur, effets de charge/impact et bruitages, portée provisoire de deux cases. La puissance fixe 100 sert au test ; elle ne reproduit pas la puissance Z variable des jeux officiels.
- Test dans une copie PMDO/Destiny isolée : le script affecte la capacité puis appelle `ProcessUseSkill` ; le moteur exécute le déplacement, la détection de l'ennemi, l'application des dégâts et la dépense d'un PP. Le banc place la cible en attente et la replace/régénère entre les huit essais. Le journal montre les huit résultats `TurnTaken`, des PV réduits de 155 à 104–107 et un PP consommé à chaque fois.
- `Turbo-v3-8-directions-capacite-native.mp4` : capture réelle en donjon avec son du moteur ; `journal-test-natif.txt` contient les résultats.

## Limites

Ce n'est pas encore un système Z complet : aucune vérification du cristal, espèce, capacité d'origine, catégorie ou puissance variable, aucune limite Z persistante. La capacité a été attribuée et déclenchée par script de test et non sélectionnée dans le menu. Les obstacles et plusieurs tailles de Pokémon n'ont pas été testés ; les huit positions sont forcées par script. La copie de test modifiée n'est pas l'installation de l'utilisateur. `breakneck_blitz-original.json` est sauvegardé séparément ; après le test, la fiche originale a été remise dans la copie pour éviter toute confusion avec la release.

Cette V3 remplace visuellement le prototype antérieur pour le banc, sans certifier la fidélité aux jeux officiels ni la qualité finale. L'animation doit encore être examinée et affinée en conditions de jeu réelles.
