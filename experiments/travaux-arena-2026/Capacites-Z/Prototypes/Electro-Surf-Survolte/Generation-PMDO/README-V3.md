# Électro-Surf Survolté — génération et capture V3

Vidéo : `Raichu-Electro-Surf-V3-60ips-son.mp4`. Charge autour de Raichu, formation progressive d'une sphère opaque, départ rectiligne et arcs électriques mobiles. La sphère utilise 48 images plutôt que 24 et sa formation 96 étapes au lieu de 48, avec 18 images de maintien pour couvrir le délai du moteur avant l'apparition du projectile. Cette jonction évite la disparition constatée lors du premier essai V3 ; il peut y avoir une brève superposition des deux sphères au départ.

Diagnostic : la vidéo V2 annonçait 30 i/s mais contenait 270 images pour 59,47 secondes, soit environ 4,5 images enregistrées par seconde. La vidéo V3 contient 3 600 images pour 60 s, soit 60 i/s de vidéo. Cela ne garantit pas 60 images distinctes par seconde : le rendu du jeu et les images d'animation peuvent être répétés.

Banc en copie isolée : huit directions, 24/24 cibles centrale et latérales touchées et paralysées, 16/16 témoins arrière intacts, PP consommé. Lainergie perd des PV mais ne subit pas de paralysie. Journal `journal-v3-8-directions.txt`. La zone réelle est un balayage moteur de trois cases de large, pas la forme exacte des éclairs ; murs et alliés non validés. Raichu reste en place, seule la sphère avance. Originaux restaurés et comparés.

Prototype de test seulement : pas de système Z complet avec cristal, restrictions et menu. Générateur : `Capacites-Z/Sources/preparer-z-foudre-v3.py` ; charge : `electro-surf-v3-charge.lua` ; fiche `stoked_sparksurfer-v3-test-only.json`.
