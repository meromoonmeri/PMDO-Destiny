# Psycho-Pulvérisation EX — étude de pli spatial

## Intention
Un pli transparent sans quadrillage ni décor peint : l'effet doit déformer les pixels effectivement présents autour de la cible, quel que soit le biome, puis disparaître progressivement. Le décor et le personnage participent à la même déformation.

## Ce qui a été réalisé
`Psycho-pli-spatial-etude-hors-jeu-60ips-son.mp4` est une **étude visuelle hors jeu**, calculée à partir d'une image fixe d'une capture PMDO en forêt. Le calcul rééchantillonne les pixels de cette image : aucun quadrillage ni calque de paysage n'est ajouté. La bande sonore provient d'une capture existante ; elle n'est pas synchronisée avec une action jouée ici. Le script reproductible est `Capacites-Z/Sources/etude-pli-spatial.py`.

La formule ne contient aucune texture de biome, mais l'étude n'a été vérifiée visuellement que sur cette capture de forêt. Elle ne démontre ni un comportement en jeu, ni un suivi des cibles, ni la compatibilité avec d'autres biomes, résolutions, zooms ou plusieurs cibles.

## Intégration à faire
Rendre le décor et les personnages dans une texture, puis rééchantillonner cette texture à proximité des coordonnées écran de chaque cible, idéalement via un shader et une cible intermédiaire. Prévoir la durée, la synchronisation avec l'attaque, les bords et zooms, les effets multiples et le nettoyage en cas d'interruption. Mesurer les performances et vérifier plusieurs biomes en jeu. La V2 à quadrillage reste rejetée ; cette étude ne la remplace pas comme capacité jouable.
