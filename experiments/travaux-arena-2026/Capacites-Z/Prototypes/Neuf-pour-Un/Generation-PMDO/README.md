# Neuf pour Un — prototype de banc

**Vidéo :** `Evoli-Neuf-pour-Un-huit-evolitions-60ips-son.mp4` (capture sonore à 60 images vidéo/s).

## Réalisation

Les huit évolutions apparaissent en cercle autour d'Évoli et transmettent leur énergie par des rayons colorés. Leurs images sont extraites des sprites de la copie PMDO : ce sont des effets visuels, pas des Pokémon alliés invoqués. La séquence est un effet en 72 images (deux frames moteur par image), avec des mouvements et des apparitions progressives ; l'animation 3D originale est adaptée librement à la vue de donjon.

La fiche expérimentale utilise une action sur soi et applique +2 aux statuts `mod_attack`, `mod_defense`, `mod_special_attack`, `mod_special_defense` et `mod_speed`, sans augmenter précision ou esquive. La vitesse est celle du moteur PMDO, pas une reproduction exacte des combats principaux : son statut comporte un compteur de 20 tours.

## Résultat du banc

Dans une copie isolée de PMDO-Destiny, Évoli a lancé la capacité dans les huit orientations ; chacun des cinq statuts a été vérifié à +2 et le PP à 0. Le Ronflex témoin est resté indemne et sans ces boosts. Voir `journal-8-directions.txt`. La fiche, les scripts et la sauvegarde de la copie de test ont été restaurés et comparés aux originaux ; l'effet temporaire a été retiré.

## Limites

Aucun système complet de capacité Z : Évolizélite, vérification de Dernier Recours, restriction à Évoli, menu, limites d'utilisation et interactions avec d'autres statuts restent à concevoir et tester. Les alliés, plafonds de statistiques, durée en partie réelle et interruptions ne sont pas testés. Aucune installation permanente effectuée.

Sources de conception : [Poképédia — Neuf pour Un](https://www.pokepedia.fr/Neuf_pour_Un) et [Pokémon Soleil et Lune — capacités exclusives](https://www.pokemon-sunmoon.com/fr-fr/exclusive-z-moves/). Générateur : `Capacites-Z/Sources/preparer-neuf-pour-un.py` ; script : `neuf-pour-un-visuel.lua` ; fiche `extreme_evoboost-test-only.json`.
