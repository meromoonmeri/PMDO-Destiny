# Électro-Surf Survolté — V4 avec image générée

La source `source-ia-v4-sphere.png` a été générée puis détourée et animée en 48 étapes. Elle sert à la formation progressive et au projectile opaque ; les arcs de charge et d'impact V3 sont conservés. La sphère avance en ligne droite après la charge autour de Raichu.

Banc isolé : huit orientations, 24/24 cibles centrale et latérales touchées et paralysées, 16/16 témoins arrière intacts, une charge consommée par utilisation. Lainergie subit des dégâts (110→47) sans paralysie. Voir `journal-v4-ia-8-directions.txt`. La copie a été restaurée et ses originaux comparés après l'essai.

Vidéo sonore `Raichu-Electro-Surf-V4-IA-60ips-son.mp4` : 60 s et 3 600 images vidéo à 60 i/s ; cela ne garantit pas 60 images distinctes du moteur par seconde. La version V3 est conservée.

Limites : la zone de dégâts native balaie trois lignes de cases ; les éclairs dessinés ne sont pas des projectiles infligeant des dégâts individuellement. Raichu reste en place. Une brève superposition des sphères de charge et de projectile reste possible au départ. Alliés, obstacles et bords non validés ; conditions d'espèce/cristal et menu Z non intégrés. Génération : `~/Capacites-Z/Sources/preparer-z-foudre-v4-ia.py` ; banc : `banc-foudre-v4-ia.py` ; fiche test-only `stoked_sparksurfer-v4-test-only.json`.
