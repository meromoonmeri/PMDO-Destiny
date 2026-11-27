# Super Tourbillon Abyssal — étude IA et banc PMDO

Cinq poses générées séparément (`image-01.png` à `image-05.png`) à partir d'une pose de `Gust_Blue`, l'effet utilisé par la capacité Whirlpool native de PMDO. Les originaux IA sont conservés. Les fichiers transparents sont redimensionnés au plus proche voisin et leur fond magenta est supprimé. `Tourbillon_IA_Impact.Dir8.png` et `.dir` sont la banque d'impact testée ; effet radial, les huit lignes de directions ont les mêmes dessins. Le projectile bleu est un effet PMDO existant et non généré par IA.

Capture du banc : `../../Pyro-Tourbillon-IA-8-directions-son-PMDO.mp4` ; journal : `../../journal-pyro-tourbillon-IA-8-directions.txt`. La fiche test `hydro_vortex-test-only.json` joue les nouvelles poses au contact et utilise le son natif `DUN_Whirlpool`. La cible, la direction et la capacité sont définies par script. `ProcessUseSkill` gère l'action, le projectile, la collision, les dégâts et la consommation de PP. Les huit positions adjacentes ont toutes reçu des dégâts ; l'effet est visible à chacune, dans la capture. La vidéo a aussi la musique du donjon.

Limites : c'est un prototype dans une copie isolée, non intégré à une partie normale. Seules cinq poses IA d'impact ; animation encore rudimentaire. L'impact est en un seul calque et recouvre parfois le Pokémon, contrairement à l'ancien vortex V2 arrière/avant. Aucune validation des obstacles, distances multiples, autres Pokémon ou des règles Z ; puissance 100, catégorie spéciale et PP 1 provisoires.

Référence : https://github.com/PMDCollab/RawAsset/tree/0b88bbd7dec6f3373d5ec2b0f40bbdc3f44ce90c/Particle .

## Variante en ligne traversante

`hydro_vortex-ligne-test-only.json` est une seconde fiche expérimentale qui remplace le projectile court par le flux de Hydrocanon : portée 4, traverse les ennemis (`StopAtHit=false`), théoriquement bloqué par les murs (`StopAtWall=true`, non testé). `Tourbillon-ligne-8-directions.mp4` et `journal-ligne-8-directions.txt` documentent huit orientations, trois ennemis placés à 1, 2, 3 cases et un quatrième sur le côté : les 24 ennemis alignés ont été touchés, les huit témoins sont restés indemnes. Une boîte de dialogue masque parfois la troisième cible à l'écran ; le journal permet de vérifier ses PV. La configuration est une proposition, pas la règle Z définitive. La variante originale V2 est conservée.
