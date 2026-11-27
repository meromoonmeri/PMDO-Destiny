# Électro-Surf Survolté — banc V2

Vidéo : `Raichu-Electro-Surf-V2-sphere-son.mp4`.

Raichu d'Alola se charge d'électricité puis une sphère opaque se forme progressivement et avance en ligne droite avec des filaments et éclairs animés. Des effets électriques apparaissent aussi sur les cibles touchées.

Banc en copie isolée : huit directions, dans une pièce dégagée ; 24/24 cibles centrale et latérales touchées et paralysées, 16/16 témoins derrière le lanceur intacts, PP consommé. Lainergie testé : dégâts mais pas de paralysie. Voir `journal-v2-8-directions.txt`.

La zone de dégâts est un balayage natif de trois cases de large et trois de portée, pas une collision au pixel près avec chaque éclair dessiné ; ses cases diagonales suivent la géométrie du moteur. Obstacles, alliés et placement en bord de zone n'ont pas été validés. Le lanceur ne suit pas la sphère : c'est elle qui se déplace.

Prototype seulement : pas d'intégration complète des cristaux, restrictions et menu Z. Les originaux de la copie de jeu ont été restaurés et comparés après essai. Générateur : `Capacites-Z/Sources/preparer-z-foudre-v2.py` ; script : `electro-surf-v2-charge.lua` ; fiche marquée `test-only`.
