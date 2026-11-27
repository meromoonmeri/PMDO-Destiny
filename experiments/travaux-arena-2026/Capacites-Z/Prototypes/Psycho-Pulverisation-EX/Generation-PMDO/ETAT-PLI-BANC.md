# Psycho-Pulvérisation EX — pli spatial, banc expérimental

## Ce qui a été testé
`Gardevoir-Psycho-Pli-Spatial-banc-60ips-son.mp4` est une capture sonore du jeu lancé dans une copie isolée du moteur. Il s'agit d'un banc, **pas d'une intégration dans la version distribuée du jeu**. Le conteneur est à 60 images par seconde ; cela ne garantit pas 60 images distinctes produites par le moteur.

Le rendu de la scène est échantillonné à des coordonnées déplacées dans une zone locale autour de chaque cible. Ainsi, le Pokémon et le décor sont réellement déformés ensemble, sans texture de paysage pré-dessinée ni quadrillage. Le banc conserve aussi les particules roses et l'impact de la V1, qui sont des effets distincts du pli transparent.

## Résultats
- 8 orientations ; 3 cibles atteintes à chaque orientation, 1 témoin hors zone intact à chaque fois : 24 cibles et 8 témoins. PP du banc : 1 vers 0.
- 24 déclenchements de pli relevés dans le journal. Les cibles sont traitées successivement, pas simultanément.
- Le rendu a été filmé en forêt seulement. Les pixels sont pris dans la scène courante, ce qui ne dépend pas d'une texture de biome ; les autres biomes restent à tester.
- Originaux du jeu isolé restaurés et comparés ; fichiers temporaires ajoutés retirés après le banc. Le moteur modifié reste dans un répertoire de test séparé.

## Limites importantes
Ce n'est pas un shader : l'essai redessine de nombreux petits rectangles depuis la texture de rendu. Sa performance et sa fluidité ne sont pas garanties selon les machines, résolutions et zooms. Un relevé indicatif sur quatre secondes de capture a trouvé environ 173 images visuellement distinctes sur 240 images capturées ; cette mesure ne constitue pas un benchmark du moteur. L'interface est déjà dessinée dans la texture source et pourrait être déformée si elle chevauche une cible. Le suivi utilise la case courante du personnage, pas ses déplacements sous-case. Cibles simultanées et zones de pli qui se recouvrent, changement de scène, pause, morts, interruptions, caméra, différents zooms, bords et autres biomes ne sont pas validés. La durée est comptée en images de rendu plutôt qu'en temps de jeu. L'effet visuel de la V1 demeure provisoire. Cristal, menu, conversion et restrictions Z ne sont pas intégrés.

## Sources
- `Capacites-Z/Sources/PliSpatial/Effet/Pli.cs` : rendu expérimental.
- `Capacites-Z/Sources/PliSpatial/Patch/Program.cs` : branchement sur une copie de RogueEssence au moyen de Mono.Cecil.
- `Capacites-Z/Sources/psycho-pli-banc.lua` et `banc-psycho-pli.py` : déclenchement et installation/restauration de la copie isolée.
- `journal-pli-banc.txt` : résultats du banc. Le tout premier essai d'import Lua ayant échoué a été corrigé avant cette capture.

Avant toute intégration réelle : utiliser une solution de rendu plus efficace, exclure l'interface, gérer explicitement les durées et le nettoyage, puis tester les cas non couverts.
