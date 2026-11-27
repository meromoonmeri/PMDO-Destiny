> **V1 REJETÉE : retirée de l’aperçu à la demande de l’utilisateur. À refaire image par image dans le style PMD.**

# Fureur des Plumes Spectrales — V1 expérimentale

Vidéo sonore : `Archeduc-Fureur-Plumes-Spectrales-V1-IA-60ips-son.mp4` ; journal : `journal-v1-8-directions.txt`.

Archéduc se prépare avec une animation d'envol et une couronne de flèches natives. Le tir reprend le projectile et la traînée Spectre de Tisse Ombre ; à l'arrivée, une volée de flèches PMDO converge sur une image spectrale générée et animée. L'impact réutilise également des particules Spectre natives. La fiche de banc est physique, de type Spectre, de puissance 180 ; elle ne reprend pas l'entrave de Tisse Ombre. C'est un projectile sur la première cible, pas huit coups de dégâts indépendants.

## Test en copie isolée

Huit orientations : 8/8 cibles Lokhlass touchées, 8/8 témoins latéraux indemnes, une charge consommée à chaque utilisation. Archéduc était de niveau 30 et les Lokhlass de niveau 100 pour éviter que la cible soit mise K.-O. et disparaisse du banc entre deux essais. Les fichiers originaux de la copie de jeu ont été restaurés puis comparés ; les banques et scripts temporaires ont été retirés.

La vidéo dure 37 s et contient 2 220 images à 60 i/s, avec son ; certaines images peuvent se répéter selon le rendu du moteur. L'effet d'impact est grand et peut être en partie masqué par le journal de combat, notamment vers le bas.

## Limites

Le vol vers la cible de la cinématique d'origine n'est pas reproduit : l'envol est une animation préparatoire et c'est la flèche qui se déplace. La volée est visuelle, les dégâts sont appliqués une seule fois. Les murs, alliés, bords de carte, immunité de type Normal, distances et effets en conditions réelles restent à tester. Restrictions Archéduc / Tisse Ombre / Archézélite, système de cristal et menu Z ne sont pas intégrés. Prototype de banc, pas publication en jeu ni push.

Sources : `~/Capacites-Z/Sources/preparer-fureur-plumes-spectrales.py`, `fureur-plumes-charge.lua`, `test-fureur-plumes-spectrales.lua`, `banc-fureur-plumes.py`. Référence de l'animation et des conditions : https://www.pokepedia.fr/Fureur_des_Plumes_Spectrales/G%C3%A9n%C3%A9ration_7.
