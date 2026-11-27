# Patati-Patattrape — V2, prototype à valider

Vidéo : `Mimiqui-Patati-Patattrape-V2-PMD-60ips-son.mp4`. Journal : `journal-v2-8-directions.txt`. Planche : `Patati-V2-tissu-impact-112images.png`, 8 colonnes, cases 128 × 128 pixels, fond transparent, lecture ligne par ligne à 60 images/s.

Mimiqui charge avec le cœur natif de Charme puis bondit. Deux pans de tissu se déploient autour de la cible, se referment et se déforment pendant des secousses ; l'effet s'achève sur un cœur, des étoiles et de la poussière, avec les textures natives Fée de Câlinerie. L'impact comprend 112 images ; les secousses sont uniquement visuelles et les dégâts sont calculés une fois. Le fichier `.dir` et la fiche JSON sont ceux du banc isolé.

## Résultats du banc

Huit orientations : huit Lokhlass à deux cases touchés (270 → 242–245 PV), huit témoins latéraux indemnes, charge consommée à chaque lancement. Mimiqui niveau 30, cibles niveau 100. Fiche Fée physique de puissance 190 avec contact, sans baisse d'Attaque ajoutée. Les originaux de la copie de test ont été restaurés et comparés.

La vidéo est encodée à 60 i/s avec son ; le moteur peut répéter des images si son rendu ralentit.

## Limites

L'étoffe est un effet animé superposé à la cible : elle ne change pas réellement les sprites ou positions de Mimiqui et de l'adversaire. Le haut de certaines cibles et Mimiqui peuvent rester visibles à côté ou au-dessus du tissu ; le rendu doit donc être validé par le joueur. Ce n'est pas une simulation physique du costume. Les cibles adjacentes, obstacles, alliés, bords et immunités ne sont pas testés ; la portée de deux cases est une adaptation du banc. Le cristal, les restrictions Mimiqui/Câlinerie/Mimiquizélite et le menu Z ne sont pas intégrés, et aucun push n'a été effectué.

Sources de banc : `~/Capacites-Z/Sources/preparer-patati-v2.py`, `banc-patati-v2.py`, `patati-charge.lua`, `test-patati-patattrape.lua`, `intro-halo-banc-mimiqui.lua`.
