-- Les points sont les coins des collisions 16×16, pas le centre des sprites.
-- Sur chaque chemin, l'autre côté reste libre pour doubler le promeneur.
return {
  {
    id='Itinerant_Mirabelle', nom='Mirabelle', espece='skitty', genre='Female',
    carte='reverie_centre', y=1408, x={552,648,784}, vitesse=1.0, repos=32,
    emotion='Happy', objet='berry_oran',
    texte='Tu entends les planches du pont, là-bas ? Quand j’étais petite, je comptais leurs grincements pour savoir combien de voyageurs arrivaient.',
    cadeau='Je garde toujours deux Baies Oran en chemin. L’une est pour moi ; je serais ravie que tu prennes l’autre.',
    suite='Si tu entends deux grincements rapprochés, ce ne sont pas deux voyageurs. C’est la troisième planche qui a le hoquet.',
  },
  {
    id='Itinerant_Sureau', nom='Sureau', espece='seedot', genre='Male',
    carte='reverie_residentiel', y=2224, x={208,368,496}, vitesse=0.8, repos=56,
    emotion='Normal',
    texte='Quelqu’un a repeint les flèches des panneaux. Huit flèches, huit directions, et pas une qui dise où s’asseoir cinq minutes.',
    suite='Ne marche pas au ras des fossés. Je ne voudrais pas qu’on dise que je ne t’ai pas prévenu. Voilà, c’est tout.',
    apres_nilo='J’ai trouvé Nilo sous l’arbre l’autre jour. Il m’a demandé si je savais dessiner un pont. Bah… j’ai dit que oui, évidemment. Maintenant, il faut que j’apprenne.',
  },
  {
    id='Itinerant_Tilleul', nom='Tilleul', espece='phanpy', genre='Male',
    carte='reverie_etang', y=2040, x={1216,1352,1496}, vitesse=1.2, repos=24,
    emotion='Joyous', objet='food_apple',
    texte='J’ai essayé de faire le tour du reflet d’un nuage. J’ai traversé deux ponts avant de comprendre que c’était lui qui me suivait !',
    cadeau='J’avais emporté une Pomme pour mon grand voyage. Comme je n’ai fait que le tour de l’étang, je te la donne !',
    suite='Je voudrais dessiner une carte des endroits où l’on peut voir le ciel sans lever les yeux. Tu penses que les flaques comptent ?',
  },
  {
    id='Itinerant_Liane', nom='Liane', espece='mienfoo', genre='Female',
    carte='reverie_residentiel', y=2576, x={832,920,1024}, vitesse=1.1, repos=30,
    emotion='Determined', duel=true,
    texte='Tu vois ces empreintes dans le sable ? Je suis en train d’apprendre à tourner sans perdre un pas. Sur le tapis du Dojo Kingambit, ça fait toute la différence.',
  },
}
