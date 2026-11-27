> **V1 REJETÉE : retirée de l’aperçu à la demande de l’utilisateur. À refaire image par image dans le style PMD.**

# Symphonie des Ondines — V1 expérimentale

Vidéo sonore : `Oratoria-Symphonie-des-Ondines-V1-IA-60ips-son.mp4` ; journal : `journal-v1-8-directions.txt`.

Oratoria prépare une sphère d'eau grandissante, puis la projette en ligne droite sur la première cible. La sphère et l'éclatement sont issus d'images générées puis animées ; les bulles bleues et les cercles d'impact proviennent d'Aria de l'Écume, la capacité Eau native. Le projectile reprend le fonctionnement de Vibraqua. La fiche de test est Eau, spéciale, de puissance 195, et ne reprend ni la guérison des brûlures d'Aria ni le statut Son : ces effets ne sont pas ceux de la capacité Z d'origine.

## Banc en copie isolée

Huit orientations : 8/8 Lokhlass touchés (270 → 254–256 PV), 8/8 témoins latéraux indemnes, une charge consommée par utilisation. Oratoria niveau 30 et Lokhlass niveau 100 ; ces derniers résistent au type Eau. Le journal donne les valeurs. Les fichiers originaux de la copie ont été restaurés et comparés, les ajouts temporaires retirés.

La vidéo dure 35,5 s, contient 2 130 images à 60 i/s et du son (niveau moyen −22,3 dB). Certaines images peuvent être répétées selon le rendu du moteur. Le journal de combat peut masquer une partie de l'effet vers le bas.

## Limites

La préparation évoque le chant avec des bulles et des sons du jeu, mais ne reproduit pas une voix chantée ni toute la chorégraphie d'origine. La sphère grossit par redimensionnement d'une image générée : son écoulement interne n'est pas simulé ; sa transition entre charge et projectile reste une approximation. Le banc teste uniquement une cible à deux cases ; alliés, murs, bords de carte, distances et immunités n'ont pas été vérifiés. Les restrictions Oratoria / Aria de l'Écume / Oratozélite, le cristal et le menu Z ne sont pas intégrés. Prototype scripté de banc, pas une publication en jeu ni un push.

Sources reproductibles : `~/Capacites-Z/Sources/preparer-symphonie-ondines.py`, `symphonie-ondines-charge.lua`, `test-symphonie-ondines.lua`, `intro-halo-banc-oratoria.lua`, `banc-symphonie-ondines.py`.

Références : https://www.pokepedia.fr/Symphonie_des_Ondines/G%C3%A9n%C3%A9ration_7 ; https://bulbapedia.bulbagarden.net/wiki/Oceanic_Operetta_(move) ; https://www.pokebip.com/pokedex/soleil-lune/attaques/symphonie-des-ondines.
