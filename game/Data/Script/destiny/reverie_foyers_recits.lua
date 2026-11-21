-- Les foyers de Réverie. Les ancres sont des coins de collider 16×16,
-- mesurés sur les intérieurs livrés. Pas de nouvelles portes ni de cartes.
local function personne(id, nom, espece, genre, repos, textes, alerte, crique)
  return {id='Foyer_'..id, nom=nom, espece=espece, genre=genre,
    repos=repos, alerte=alerte, crique=crique, textes=textes}
end

return {
  pierre = {
    carte='reverie_rock_home', sortie='Rock_Home_Entrance',
    habitants={
      personne('Maelle','Maëlle','graveler','Female',{128,136,'DownRight'},{
        repos='Basalte est mon compagnon. Il trie les cailloux, et moi je les remets dans le mauvais panier. Sinon, nous n’aurions plus rien à nous raconter le soir.',
        bois='J’ai demandé un souvenir des Bois Perdus. Miette m’a rapporté de la boue sur ses pattes. J’aurais dû être plus précise.',
        alerte='J’ai rapproché le banc de la porte. On peut attendre une nouvelle ensemble, pas chacun dans un coin.',
        nilo='Quelqu’un a laissé une petite pierre devant le seuil. Miette croit que c’est Nilo qui nous l’a rapportée.',
        crique='Le sel dessine un bord blanc sur les pierres. Cette fois, Basalte ne me demande pas de tout nettoyer.',
      },{128,168,'Down'},{120,144,'Right'}),
      personne('Basalte','Basalte','nosepass','Male',{216,144,'DownLeft'},{
        repos='Maëlle, ma compagne, dit qu’une maison sonne creux si personne ne s’y raconte sa journée. Chez nous, Miette veille au grain.',
        bois='J’ai posé une pierre sur le plan des Bois Perdus. Pas pour marquer un chemin : pour empêcher le papier de s’envoler.',
        alerte='J’ai mis les paniers contre le mur. Si quelqu’un frappe, il faut pouvoir ouvrir la porte tout de suite.',
        nilo='Miette veut que chaque pierre ait un nom. Elle a appelé la plus petite « Celle qui a retrouvé le chemin ».',
        crique='Une pierre de la crique ne ressemble plus à la même pierre quand elle sèche. J’en garde une moitié mouillée, juste pour voir.',
      }),
      personne('Miette','Miette','geodude','Female',{168,104,'Down'},{
        repos='Maman taille des pierres plates et Papa en fait des piles. Moi, j’invente les questions auxquelles leurs piles ne savent pas répondre.',
        bois='Il y a sûrement des énigmes qu’on ne trouve qu’en revenant des Bois. C’est dommage : je n’ai pas le droit d’y aller seule.',
        alerte='Ma voix porte jusque dans l’entrée si je reste là. Si quelqu’un vient avec des nouvelles, je pourrai aider à les répéter.',
        nilo='Quand Nilo voudra jouer, je ne lui demanderai pas comment il est tombé. J’ai de bien meilleures questions.',
        crique='Je voulais rapporter le bruit d’un caillou dans l’eau. On m’a dit que je n’avais apporté que le caillou. Ça se discute.',
      }),
    },
    devinette={
      mene='Foyer_Miette', indice_par='Foyer_Basalte', donne_par='Foyer_Maelle',
      texte='Plus tu enlèves de terre, plus je grandis. Tu peux me reboucher, mais tu ne peux pas me mettre dans ta poche. Qui suis-je ?',
      choix={'Un tas','Un trou','Une brouette','Un indice','Plus tard'}, bonne=2,
      indice='Pense à ce qui reste sur place quand la brouette s’en va, pas à ce qu’on a chargé dedans.',
      rate='Non, mais retiens le verbe « reboucher ». On ne rebouche pas ce qu’on emporte.',
      trouve='Un trou, oui ! Papa, tu vois ? Mon énigme tient debout même sans aucune pierre.',
      offert='Bien joué. Prends cette Baie Pêcha : je glisse toujours une baie dans le sac de ceux qui partent en exploration.',
      apres='Cette fois, la réponse est à toi. Garde-la pour le jour où tu voudras poser la devinette à quelqu’un.',
      objet='berry_pecha',
    },
  },
  plante = {
    carte='reverie_grass_home', sortie='Grass_Home_Entrance',
    habitants={
      personne('Flore','Flore','bayleef','Female',{112,128,'DownRight'},{
        repos='Chaque matin, Aulne, mon compagnon, dit qu’il n’a pas faim. Le panier vide au retour ne lui donne jamais raison.',
        bois='Brin a trié les pommes des plus belles aux plus cabossées. J’ai gardé les cabossées pour la maison. Elles sont aussi bonnes.',
        alerte='Je mets deux parts de côté, sans demander à quelle heure les autres rentreront. Elles les attendront.',
        nilo='Pour Nilo, j’ai lavé une pomme. Finalement, c’est Brin qui lui portera. Il voulait trouver une façon de dire bonjour sans poser de question.',
        crique='Après le chemin de la crique, tout sent le sel. Ici, on passe les baies à l’eau douce avant de goûter.',
      },{112,160,'Down'},{104,176,'Right'}),
      personne('Aulne','Aulne','grotle','Male',{216,128,'DownLeft'},{
        repos='Flore dit que je traverse la cuisine plus lentement qu’un panier ne se vide. Avec Brin dans les jambes, comment pourrait-il en être autrement ?',
        bois='J’ai offert de porter les paniers du marché. Brin en a pris un avant moi. Il n’était pas lourd, mais j’ai fait semblant d’être impressionné.',
        alerte='On prépare la table, pas une fête. On a le droit de manger même quand on s’inquiète.',
        nilo='Brin a laissé la meilleure pomme à Nilo. Il fait mine que c’était la plus petite. Je n’ai rien dit.',
        crique='J’ai essayé le même nœud que sur les sacs des équipes de la crique. Flore l’a défait d’un coup de feuille.',
      }),
      personne('Brin','Brin','chikorita','Male',{184,96,'Down'},{
        repos='Maman réserve le bon panier. Papa croit que je ne sais pas lequel. Il l’a pourtant marqué de deux grosses feuilles.',
        bois='Je voulais faire le guet au marché. On m’a donné des pommes à compter. Les pommes ne se plaignent pas quand je recommence à trois.',
        alerte='J’ai gardé une place libre à table. Pas parce que je sais qui va venir. Parce que ça fait du bien de la voir.',
        nilo='J’ai dit « je peux m’asseoir là ? » et Nilo a fait oui de la tête. Je ne savais pas que ça pouvait suffire.',
        crique='Je craignais que les pommes de la crique aient un goût de mer. C’est juste la peau qui avait du sel !',
      }),
    },
    panier={
      mene='Foyer_Flore',
      choix={'Une Pomme','Une Baie Oran','Plus tard'},
      options={
        {id='food_apple', dit='Une Pomme pour la route, alors. Prends celle du dessus, Brin l’a déjà rincée.', suivi='La prochaine pomme reste dans notre panier. Ma part préférée, c’est celle que je peux partager à table.'},
        {id='berry_oran', dit='Une Baie Oran. Elle prend moins de place que les soucis qu’on emporte, et elle sert davantage.', suivi='Maman m’a montré comment reconnaître une Baie Oran mûre. La vôtre, c’était celle que j’avais choisie.'},
      },
    },
  },
  berge = {
    carte='reverie_water_home', sortie='Water_Home_Entrance',
    habitants={
      personne('Nacre','Nacre','azumarill','Female',{136,128,'DownRight'},{
        repos='Malo, mon compagnon, sait où l’eau monte avant que je voie la rive disparaître. Il ne sait jamais où il a posé nos tasses.',
        bois='Perle voudrait mesurer le courant comme on mesure la longueur d’un chemin. Impossible de lui faire lâcher sa ficelle.',
        alerte='Perle voulait courir prévenir tout le monde. Je lui ai confié une chose utile à faire ici : garder l’entrée dégagée.',
        nilo='Malo a remis les trois tasses côte à côte. On n’annonce pas les bonnes nouvelles en criant dans cette maison. On invite les gens à s’asseoir.',
        crique='La crique a ses repères à elle. Aucun dessin de notre rive ne vous dira où poser les pieds là-bas.',
      },{144,136,'Down'},{128,128,'Right'}),
      personne('Malo','Malo','poliwhirl','Male',{208,136,'DownLeft'},{
        repos='Nacre est ma compagne. Je voulais lui préparer du thé. Bon, d’abord il faut retrouver les tasses.',
        bois='Perle a trouvé une feuille qui remonte le courant à cause du vent. Depuis, plus personne ici ne prend une feuille pour une boussole.',
        alerte='Je sais où regarder le courant. Pour les nouvelles de la Fosse, je laisse parler ceux qui en reviennent.',
        nilo='On était trois à attendre. On est encore trois, mais ce n’est plus le même silence.',
        crique='Je garde une Échaporbe de secours pour les équipes qui repartent. Mieux vaut en avoir une que promettre de tout prévoir.',
      }),
      personne('Perle','Perle','poliwag','Female',{176,104,'Down'},{
        repos='Papa prétend que l’eau raconte des histoires. Je lui ai demandé de raconter la fin. Il m’a donné une devinette à la place.',
        bois='Je voulais mettre la fin du chemin sur mon dessin des Bois. Et si la fin, c’était simplement chez nous ?',
        alerte='Je garde la place du seuil libre. Si vous attendez des nouvelles aussi, on peut rester là sans parler.',
        nilo='Je ne veux pas obliger Nilo à jouer. Mais s’il me demande une devinette, j’en ai une prête.',
        crique='Les équipes qui ont vu la crique savent peut-être où mon énigme finit. Moi, je n’en ai vu que le début.',
      }),
    },
    devinette={
      mene='Foyer_Perle', indice_par='Foyer_Nacre', donne_par='Foyer_Malo',
      texte='J’ai un lit où je ne dors pas et une bouche qui ne parle pas. On peut me suivre jusqu’à la mer. Qui suis-je ?',
      choix={'Une route','Une rivière','Un bateau','Un indice','Plus tard'}, bonne=2,
      indice='Le lit n’est pas fait de draps. C’est la place que l’eau a creusée pour passer.',
      rate='Essaie avec quelque chose qui coule même quand personne ne le pousse.',
      trouve='Une rivière ! Sa bouche, Papa dit qu’on appelle ça l’embouchure. Moi, je l’appelle le grand bonjour à la mer.',
      offert='Et voici mon Échaporbe de réserve. Si l’expédition tourne mal, rentrer est aussi une bonne décision.',
      apres='Je travaille sur une énigme pour la mer. Pour l’instant, je ne sais pas comment lui faire tenir dans la maison.',
      objet='orb_escape',
    },
  },
  hutte = {
    carte='reverie_hutte_aquatique', sortie='Water_Home_Entrance',
    habitants={
      personne('Yuna','Yuna','lanturn','Female',{152,176,'DownRight'},{
        repos='Marius, mon compagnon, est dehors à pêcher. Lino lui réserve la place du bord : il tient absolument à voir ce qu’il rapporte.',
        bois='Le pêcheur écoute parfois les récits de retour plus longtemps qu’il ne surveille sa ligne. C’est plutôt bon signe.',
        alerte='Lino voudrait que Marius entende quand on l’appelle depuis la hutte. Avec l’eau entre nous, même un cri se perd.',
        nilo='Ce soir, on garde un bol pour Marius jusqu’à son retour. Lino veut lui raconter ce qu’il a entendu de Nilo. Avec ses mots, pas les nôtres.',
        crique='Marius dit que la lumière sur l’eau change selon le vent. Lino l’a cru le jour où il n’a plus retrouvé son reflet.',
      },{152,192,'DownRight'}),
      personne('Lino','Lino','chinchou','Male',{200,168,'DownLeft'},{
        repos='Je sais quand Papa arrive : il pose ses affaires avant de parler. Quand il ne le fait pas, c’est qu’il a une histoire urgente à raconter.',
        bois='Papa écoute les équipes de retour. Moi, je guette le bruit des pas à notre porte. Ce n’est pas vraiment la même chose, mais j’apprends.',
        alerte='Maman dit qu’on peut dire « je reviens » même si on ne sait pas quand. Est-ce qu’on peut aussi le laisser écrit ?',
        nilo='J’ai préparé une histoire pour Papa. Elle commence au moment où Nilo est rentré, pas quand il a disparu.',
        crique='J’ai voulu dessiner une vague pour Papa. Je l’ai faite tellement grande qu’il n’y avait plus de place pour le bateau.',
      },nil,{192,152,'Down'}),
    },
    discussion={
      mene='Foyer_Lino', repond='Foyer_Yuna', cle='Message',
      question='Quand Papa part pêcher avant que je me réveille, où est-ce qu’on laisse un mot pour se retrouver ?',
      choix={'À la porte','Sur la table','Plus tard'},
      options={
        {id='porte', dit='À la porte, juste à hauteur de nageoire. Je tracerai un gros rond autour de mon prénom pour qu’il trouve le mot même quand il fait sombre.', reponse='Un signe qu’on voit avant de partir. Bonne idée. On lira le mot ensemble ce soir, quand il n’aura plus les pattes prises.', suivi='Papa a vu mon rond au pas de la porte. Au retour, il a dessiné le sien à côté.'},
        {id='table', dit='Sur la table, là où on pose les bols. On aurait un mot à lire tous les deux pendant le petit déjeuner.', reponse='Alors on fait ça au calme. Même quand on part tôt, on finit toujours par revenir à table.', suivi='Papa a lu mon mot au petit déjeuner. Il est resté un peu plus longtemps que d’habitude.'},
      },
    },
  },
  citrouille = {
    carte='reverie_fire_home', sortie='Fire_Home_Entrance',
    habitants={
      personne('Zelie','Zélie','vulpix','Female',{120,144,'DownRight'},{
        repos='Lyra m’a confié la maison pendant qu’elle et Léo sont dehors. J’aère un peu, mais je ne ferme jamais le volet du seuil.',
        bois='Pour un retour, Lyra laisse toujours une place près de la porte. Je trouvais ça curieux jusqu’au jour où j’ai eu besoin qu’on m’attende.',
        alerte='Je garde la maison ouverte pour Lyra. Si vous partez l’aider, je resterai ici jusqu’à ce qu’on entende vos pas.',
        nilo='Nilo est dehors avec Lyra et Léo, sous l’arbre près de la maison. Il aimerait leur montrer son dessin avant de rentrer.',
        crique='Je veille sur cette maison pour Lyra. Sur le rebord, il y a assez de place pour faire sécher un petit dessin.',
      }),
      personne('Lyra','Lyra','luxray','Female',{128,136,'DownRight'},{
        nilo='Ici, je n’ai plus besoin d’appeler Nilo pour savoir où il est. Je l’entends tourner les pages à côté de moi.',
        crique='Si du sable tombe de votre sac, ne vous en faites pas. J’ai cessé de croire qu’une maison devait rester parfaitement en ordre.',
      }),
      personne('Leo','Léo','luxio','Male',{208,136,'DownLeft'},{
        nilo='Depuis qu’on est rentrés, Nilo dessine surtout les choses qui n’ont pas bougé. Le seuil, l’arbre… et nous, quand on tient en place.',
        crique='Nilo m’a demandé de dessiner le bruit de la crique. J’ai fait trois traits. Il a reconnu les vagues du premier coup.',
      }),
      personne('Nilo','Nilo','shinx','Male',{160,192,'Up'},{
        nilo='Dehors, mon dessin avait l’air tout petit. Ici, quand je le pose au milieu de nous, c’est la maison entière qui tient sur la feuille.',
        crique='On m’a dit que le papier de la crique mettait longtemps à sécher. Le mien aussi. Quand on efface beaucoup, on appuie fort.',
      }),
    },
    discussion={
      mene='Foyer_Nilo', repond='Foyer_Lyra', cle='Dessin',
      question='Je ne sais pas quoi faire de mon dessin maintenant. Qu’est-ce que tu ferais, toi ?',
      choix={'Le montrer','Le garder pour moi','Plus tard'},
      options={
        {id='montrer', dit='Alors je le montrerai d’abord à quelqu’un qui connaît la maison. S’il reconnaît le seuil, le reste viendra.', reponse='Tu choisis à qui tu le montres. Et tu n’es pas obligé de raconter toute l’histoire avec le dessin.', suivi='J’ai montré le dessin à Léo. Il a repéré sa patte près du seuil avant même de reconnaître ma tête.'},
        {id='garder', dit='Je le plie et je le garde dans mon coin. Ce n’est pas pour le cacher. Je veux juste le revoir quand j’en aurai envie.', reponse='Alors il reste à toi. Le jour où tu voudras le déplier, je serai là, même si c’est seulement pour tenir un coin de la feuille.', suivi='J’ai déplié mon dessin ce matin, juste pour moi. Il n’a pas changé, mais j’ai trouvé un détail que j’avais oublié.'},
      },
    },
  },
}
