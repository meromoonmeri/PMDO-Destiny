# Giga-Tonnerre — génération et capture V3

Vidéo : `Pikachu-Giga-Tonnerre-V3-60ips-son.mp4`. La colonne continue jusqu'au haut de l'écran, sans sommet visible, avec éclairs multicolores autour de la cible. La banque d'impact comporte 48 images plutôt que 24, utilisées à raison d'une image par frame moteur ; la variation cyclique des éclairs a été régularisée.

Diagnostic : la vidéo V2 annonçait 30 i/s mais contenait 155 images pour 33,63 secondes, environ 4,6 images enregistrées par seconde. C'était donc une cause certaine de saccades ; cela ne prouve pas que chaque animation dans le jeu soit parfaitement fluide. La capture V3 contient 2 010 images pour 33,5 s, soit 60 i/s de vidéo. Des images vidéo peuvent néanmoins se répéter selon l'animation et le rendu du jeu.

Banc en copie isolée : huit directions, huit cibles touchées, huit témoins intacts, PP consommé. Journal `journal-v3-8-directions.txt`. Originaux restaurés et comparés. La casquette du banc est approximative. Prototype de test seulement : pas d'intégration complète des règles Z, cristal, menu ou bonus de critique.

Générateur : `Capacites-Z/Sources/preparer-z-foudre-v3.py` ; fiche `ten_million_volt_thunderbolt-v3-test-only.json`.
