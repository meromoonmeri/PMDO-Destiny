# Fureur des Plumes Spectrales — V2 PMD, à valider

Cette reprise remplace la V1 rejetée. Une petite plume IA pixelisée complète les flèches et la traînée Spectre **natives de Tisse Ombre**. Deux banques animées composent l'effet : 40 images de préparation et 44 images d'impact, avec trajectoires successives de flèches et dispersion de petites plumes et d'éclats. Ce n'est pas une image entière agrandie. Le sprite natif d'Archéduc reste visible.

Test en copie isolée : huit orientations, 8/8 cibles Lokhlass touchées (270 → 240–243 PV), huit témoins latéraux indemnes, une charge consommée par utilisation. Journal : `journal-v2-pmd-8-directions.txt`. Les originaux ont été restaurés et comparés après le banc. Vidéo sonore : `Archeduc-Fureur-Plumes-V2-PMD-60ips-son.mp4` (38 s, 60 i/s vidéo ; des images peuvent se répéter suivant le moteur).

## Limites

Le lanceur prend une pose d'envol mais ne vole pas jusqu'à la cible ; une seule flèche native se déplace puis l'impact montre une volée. Les dégâts sont appliqués une seule fois, pas individuellement par flèche. La capacité vise la première cible sur une ligne de portée quatre dans ce banc ; les murs, alliés, bords, immunité Normal et distances restent à tester. Le journal peut masquer une partie des effets vers le bas. Les règles d'Archézélite, la sélection et l'intégration réelle sont absentes. Qualité artistique à valider par l'utilisateur ; aucun push.

Sources : `Sources/preparer-fureur-plumes-v2-pmd.py`, `Sources/fureur-plumes-v2-charge.lua`, `Sources/banc-fureur-plumes-v2-pmd.py`, `Sources/test-fureur-plumes-spectrales.lua`.
