# Kingambit — éclairages des finales et ouverture du sceau

Retouche de Destiny v0.7.7. Elle modifie des scripts et des effets **en jeu**, sans nouvel exécutable, carte ou format de sauvegarde.

## Mise en scène

- **Hall.** Kaito reste à sa place. Le trajet vers le sceau `(384,270)` est toujours validé par `dojo_kingambit_sceau` avant le mouvement. Sur le sceau : arrêt, recadrage, deux clacs de pênes, coulissement, ouverture puis chute. Les banques `Kingambit_Mecanisme_<type>_{Sol,Rebord}` ont 24 poses à quatre ticks et gardent le pivot et le découpage historique : un plan sous les acteurs, la lèvre au premier plan. Les feuilles et la denture reprennent les couleurs de la trappe du biome. Le deuxième acteur chute quatre ticks après le premier ; après le fondu, les sprites, les ombres et la caméra Ground sont remis en état avant `EnterDungeon`. Sans les nouvelles banques, les anciennes trappes restent utilisables.
- **Finales.** `BattlePositionEvent`, le masquage `-11`, le raccord `-9` et `BeginBattleEvent` à `-5` restent aux mêmes priorités. Extinction et musique en fondu, puis une voix `???` sans portrait sur fond noir. Le noir dure autant que la lecture ; aucune boucle d’éclairage n’est synchronisée avec la vitesse de lecture. Après la boîte : trois signaux propres au type, avec accents sonores et mouvement de caméra Dungeon, recouvrent l’amorce de l’entrée existante. Maître et cadets arrivent selon leur chorégraphie d’origine. Pose et portrait du maître, woosh PMD et combat natif. La musique, la direction du joueur et la caméra d’arrivée sont rétablies. Si une banque de lumière est absente, reprise directe de l’entrée et du précombat.
- **Règles.** Ni les cases, ni les formes, ni les clefs de victoire, ni les étages à parcourir ne changent. Le sprint QA saute les deux étages précédant la finale, jamais son événement de combat. Le test de la trappe utilise le hall et le véritable événement d’action de Kaito.

Le *PMD Cutscene Guide* a servi pour organiser les pauses de lecture, le cadrage avec la boîte de texte, l’immobilité des acteurs au sol, la séparation des plans lors de la chute et le calage du son sur l’image. Le traitement de lumière est un voile PMDO en pixels monde, indépendant de la boîte et sur la couche `Top`. Il ne requiert ni shader ajouté ni API de cinématique Ground dans le donjon.

## Sources et vérifications

Le script Python utilise Pillow et NumPy et réemploie `art/dojo_dedales_trappes` ; aucune source de personnage ou de carte n’est régénérée. Depuis le dépôt :

```sh
python tools/cinematiques_kingambit/generer.py --base . --out .
python tools/cinematiques_kingambit/verifier.py --base . --lot . --pmdo /chemin/vers/PMDO
LUA_PATH='game/Data/Script/?.lua;game/Data/Script/?/init.lua;;' \
  lua tools/tests/test_dojo_kingambit_cinematiques.lua
LUA_PATH='game/Data/Script/?.lua;game/Data/Script/?/init.lua;;' \
  lua tools/tests/test_dojo_kingambit_dedales.lua
```

`Plans.json` contient l’écriture des 18 scènes. `Banques.json` enregistre les dimensions, le nombre de poses et le SHA-256 des 54 atlas. Les nouvelles ressources `.dir` n’emploient pas l’index des `.tile`. La validation moteur et la vidéo sont des preuves distinctes du colis Windows publié : la préversion v0.7.7 reste inchangée sur GitHub.
