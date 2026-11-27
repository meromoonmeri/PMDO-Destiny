# Piqué Supersonique — prototype en donjon

La capture sonore `Roucarnage-Pique-Supersonique-8-directions-son.mp4` montre une adaptation de la capacité Z générique dans une copie isolée de PMDO/Destiny. Roucarnage est le lanceur de ce banc, pas un porteur exclusif.

Le lanceur décolle avec l'animation native `CharAnimFly`, puis redescend vers l'adversaire grâce à une `DashAction` native de type `DropDown`. Un sillage de vent bleu-blanc accompagne la descente et une onde de choc aérienne apparaît à l'impact. Les images de sillage et de choc ont été générées par IA puis animées en 12 et 28 poses. Sons moteur `DUN_Fly` et `DUN_Sky_Attack`. La cinématique officielle USUL a servi de repère pour le décollage, la descente et les couleurs ; le voyage dans le ciel et l'impact à grande échelle ne sont pas reproduits.

## Test et limites

Huit orientations : une cible à deux cases touchée dans chaque essai, témoin latéral intact dans les huit cas, PP 1 → 0 ; voir `journal-8-directions.txt`. Le lanceur est repositionné par le banc entre les essais ; les dégâts et les PP passent par le moteur. Portée 3, collision, puissance physique 90 et PP provisoires. Obstacles, alliés, bordures, autres distances et lanceurs, interruptions et cas d'échec ne sont pas validés. Aérozélite, conversion de puissance et catégorie, menu et règles Z non intégrés.

Fiche originale, événement, scripts de banc, introduction et sauvegardes de la copie restaurés après capture ; banques temporaires retirées. Sources dans `Capacites-Z/Sources/preparer-pique-supersonique.py`, `pique-supersonique-decollage.lua`, `test-pique-supersonique.lua`, `intro-halo-banc-roucarnage.lua`.
