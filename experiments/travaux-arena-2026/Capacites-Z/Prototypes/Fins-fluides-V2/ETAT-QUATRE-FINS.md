# Quatre fins animées — prototypes V2

L'utilisateur a validé Lame en Peine V6 charge calibrée et Canon Blindé V2 corrigée. Ces validations n'impliquent pas une intégration dans le dépôt du jeu.

## Modifications visuelles
Les images d'impact fixes redimensionnées des quatre V1 ont été retirées de la phase finale et remplacées par des banques de poses, avec dessins et particules PMD animées. La charge, le comportement et les autres étapes V1 restent inchangés.

- **Rayons Séléno-Explosifs** : rayons convergents conservés, croissant animé, éclat et anneaux lunaires. La brèche V1 précédant l'impact est conservée ; elle utilise toujours une texture superposée et n'est pas une véritable aspiration ou scène cosmique.
- **Apocalypsis Luminis** : lignes prismatiques montantes, pulsation et scintillements animés en remplacement de l'image fixe du pilier.
- **Hélio-Choc Dévastateur** : impact de type explosion native, onde et particules en mouvement. La brèche V1 précédente reste une texture superposée ; la ruée reste celle du prototype V1.
- **Colère du Gardien d'Alola** : lances conservées et explosion finale reconstruite avec particules, onde et éclats. Les lances elles-mêmes sont des sprites superposés existants.

La fluidité artistique doit être appréciée par l'utilisateur : la vidéo est encodée à 60 images/s, mais les séquences utilisent des sprites et peuvent répéter des poses si le moteur ralentit. Ce ne sont pas des simulations physiques ni de la 3D.

## Résultats des bancs isolés
Les quatre essais ont atteint FIN OK. Les originaux ont été restaurés, les ajouts retirés et les fichiers comparés ; aucun push ni intégration définitive.

- Rayons : huit directions, cibles 270 → 234–238 PV, témoins 270 → 270 et PP consommé. Immunité Normal confirmée 395 → 395 ; Garde Mystik contournée en banc (270 → 236) et drapeau restauré.
- Apocalypsis : huit directions, cibles 270 → 125–153 PV, témoins intacts et PP consommé. Immunité Ténèbres confirmée 235 → 235 ; Garde Mystik contournée (270 → 142), drapeau restauré. Catégories physique et spéciale alternées selon les statistiques artificielles du banc.
- Hélio : huit directions, cibles 270 → 230–234 PV, témoins intacts et PP consommé. Garde Mystik contournée (270 → 231), drapeau restauré.
- Colère : huit orientations et cas de résistance, Garde Mystik et cible à 1 PV réussis, témoins et allié intacts. Exemples : 270 → 68, 100 → 25, Garde Mystik 100 → 100, minimum 1 PV 1 → 0.

**Attention :** le contournement des talents des trois premières capacités utilise toujours la suspension expérimentale de tous les talents et demeure dangereux en cas d'interruption, d'action imbriquée, de K.O. ou de talent non contournable ; ne pas l'intégrer tel quel. Les limites V1 restent valables : calcul incomplet de la catégorie d'Apocalypsis, restrictions et menu Z absents, protections et cas particuliers non exhaustivement testés. Les tests valident ces scénarios, pas l'ensemble des règles du jeu.

## Captures
La compilation `Quatre-fins-V2-apercu-60ips-son.mp4` présente les quatre premiers essais, 7,5 secondes chacun. Les vidéos complètes avec son, huit directions et cas de contrôle sont dans les dossiers `Generation-PMDO/V2-impacts` de chaque capacité et dans la galerie : `menacing_moonraze_maelstrom_v2`, `light_that_burns_the_sky_v2`, `searing_sunraze_smash_v2`, `guardian_of_alola_v2`. Captures individuelles : respectivement 59, 46, 56 et 66 secondes, H.264 640 × 480 60 ips, AAC non silencieux. Le téléchargement depuis le cadre d'aperçu reste non confirmé et peut être bloqué.

Sources : `~/Capacites-Z/Sources/impacts-fluides-v2.py` et `banc-impacts-fluides-v2.py`. Les journaux de chaque banc sont placés dans les dossiers V2 correspondants.
