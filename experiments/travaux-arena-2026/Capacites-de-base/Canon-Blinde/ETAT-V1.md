# Canon Blindé — prototype V1 à valider

Carmadura tire un large rayon ardent, accompagné de flammes natives PMDO, suivi d'une grande explosion au point final calculé par le moteur. Le rayon utilise une banque de 12 images et l'impact une séquence de 42 images. La vidéo est une capture du banc, avec son et encodage à 60 images par seconde.

## Fonctionnement expérimental

La fiche d'origine est non publiée et incomplète. Dans cette copie de test uniquement, la capacité conserve les 5 PP, la puissance spéciale Feu 120 et la précision 100 ; elle reçoit la baisse d'un niveau de Défense et de Défense Spéciale du lanceur, conformément à la description officielle ([source](https://scarletviolet.pokemon.com/fr-be/pokemon/armarouge/)). Le rayon perce, couvre trois cases de largeur et porte à trois cases pour ce prototype. Il s'arrête aux murs selon les paramètres natifs. La brûlure de tous les ennemis touchés est une adaptation expérimentale demandée, pas un effet canonique de Canon Blindé ; les immunités restent à tester.

L'explosion est **purement visuelle**, pas un second dégât de zone ni une destruction des murs. Le script utilise `StrikeLandTiles`, la case finale calculée par `WaveMotionAction`, afin de ne pas déclencher un impact à chaque case traversée. Le banc vérifie qu'une seule case de destination est fournie dans chaque direction, mais ne prouve pas encore la bonne collision avec des murs placés intentionnellement ou l'absence de problème aux limites de carte. Une première étude à sept cases laissait souvent l'impact hors écran ; ce cadrage à trois cases permet de le voir.

## Vérifications et limites

Le banc à trois cases a réussi dans les huit directions : trois cibles centrales et latérales blessées et brûlées par direction, deux témoins derrière le lanceur intacts, PP 5 → 4. Un seul point d'impact a été relevé par attaque. Les messages en jeu indiquent les deux baisses défensives, sans banc chiffré séparé. Journal : `journal-v1-cadre.txt`. Le précédent banc à sept cases est conservé dans `journal-v1.txt`.

La copie isolée a été restaurée et ses originaux comparés. Reste à tester les murs proches et diagonaux, les ennemis derrière les murs, les immunités et protections, les limites de carte et les interruptions, puis à décider de la portée et de la probabilité de brûlure. Les dégâts éventuels d'une explosion de zone et la destruction des murs ne sont pas implémentés. Aucun changement définitif n'a été intégré au jeu ni poussé.
