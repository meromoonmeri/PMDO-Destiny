# Impact Choupinova — V2, vent féerique

La vidéo `Nymphali-Impact-Choupinova-V2-vent-feerique-son.mp4` montre le prototype enregistré en jeu dans une copie isolée de PMDO/Destiny ; la V1 rejetée est conservée séparément.

## Effets

- Le lanceur fait un tour complet sur ses huit vues, avec une aura féerique dessinée derrière lui, puis retrouve son orientation.
- Un voile transparent d'étincelles, étoiles et traînées pastel traverse globalement l'écran. Il utilise le même type d'overlay mobile plein écran que Vent Argenté ; il ne remplace pas le terrain par un décor fixe.
- La deuxième image de cœur étoilé générée est détourée puis redimensionnée pour créer les projectiles qui tombent sur les cibles. Trois arrivées et explosions roses sont animées par cible, avec un seul calcul de dégâts. Les cibles sont traitées successivement par le moteur, pas simultanément.
- Effets recentrés par cible, avec des sprites plus petits que dans la V1. Les visuels ont été vérifiés dans la capture en jeu, pas dans tous les contextes ou résolutions.

Le mouvement de Vent Argenté et la référence d'Impact Choupinova USUL ont servi de repères ; il s'agit d'une adaptation PMDO, pas d'une reproduction fidèle de la scène officielle : le vol autour de la cible et sa projection dans les airs ne sont pas réalisés.

## Banc et limites

Huit orientations : 24/24 cibles ont perdu des PV, 8/8 témoins hors zone sont restés intacts ; PP 1 → 0 et direction initiale rétablie à chaque fois. Le journal est `journal-v2-8-directions.txt`. Les effets ont été observés sur un seul terrain et avec une mise en scène scriptée ; alliés, interruptions, autres lanceurs et terrains ne sont pas validés.

La zone, la puissance et les PP sont ceux du banc, provisoires. Le cristal, la conversion depuis la capacité de base, le menu et les règles Z complètes ne sont pas intégrés. Après capture, fiche de capacité, événements, script de banc, introduction et sauvegardes de la copie ont été restaurés ; les banques V2 ont été retirées de la copie. Les sources du prototype restent dans `Capacites-Z/Sources/preparer-impact-choupinova-v2.py`, `impact-choupinova-v2-rotation.lua` et `test-impact-choupinova-v2.lua`.
