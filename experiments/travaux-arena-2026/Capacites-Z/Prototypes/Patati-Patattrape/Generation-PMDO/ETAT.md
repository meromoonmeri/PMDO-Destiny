> **V1 REJETÉE : retirée de l’aperçu à la demande de l’utilisateur. À refaire image par image dans le style PMD.**

# Patati-Patattrape — V1 expérimentale

Vidéo sonore : `Mimiqui-Patati-Patattrape-V1-IA-60ips-son.mp4` ; journal : `journal-v1-8-directions.txt`.

Mimiqui prépare l'attaque avec l'effet Fée natif de Charme, puis bondit vers la première cible. Au contact, une pose native de Mimiqui agrandie et agitée évoque son déguisement recouvrant la cible, accompagnée de poussière et d'étoiles natives de Câlinerie ainsi que d'un nuage féerique généré puis animé. La fiche de banc est Fée, physique, puissance 190, avec contact ; elle n'ajoute pas la baisse d'Attaque de Câlinerie. Les secousses sont visuelles : les dégâts ne sont calculés qu'une fois.

## Banc en copie isolée

Huit orientations : 8/8 cibles Lokhlass touchées (270 → 242–245 PV), 8/8 témoins latéraux intacts, une charge consommée par lancement. Cible placée à deux cases ; Mimiqui niveau 30 et Lokhlass niveau 100. Les fichiers originaux de la copie isolée ont été restaurés et comparés et les ajouts temporaires retirés.

La vidéo dure 33 s, comprend 1 980 images à 60 i/s et du son (moyenne −23,3 dB). Certaines images peuvent se répéter selon le rendu du moteur. Le journal de combat peut masquer le bas de l'effet.

## Limites

Le recouvrement est une **superposition visuelle d'une pose agrandie**, pas un vrai tissu animé qui enveloppe et transporte la cible : la pose agrandie est orientée de face dans les huit directions et le sprite normal peut parfois rester visible à côté. Le bond, les coups et le déguisement ne reproduisent donc pas littéralement la cinématique originale. Le rayon de deux cases est une adaptation de banc ; les cibles adjacentes, obstacles, alliés, bords et immunités restent à tester. Les restrictions Mimiqui / Câlinerie / Mimiquizélite, le cristal et le menu Z ne sont pas intégrés. Prototype scripté de banc, pas une publication en jeu ni un push.

Sources reproductibles : `~/Capacites-Z/Sources/preparer-patati-patattrape.py`, `patati-charge.lua`, `test-patati-patattrape.lua`, `intro-halo-banc-mimiqui.lua`, `banc-patati.py`.

Références : https://www.pokepedia.fr/Patati-Patattrape/G%C3%A9n%C3%A9ration_7 ; https://bulbapedia.bulbagarden.net/wiki/Let%27s_Snuggle_Forever_(move).
