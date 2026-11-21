-- Le carnet des retours : l'actualité de Réverie, indépendante des jours de marché.
-- Les jalons principaux sont relus dans les champs du scénario déjà sauvegardés.
-- Seule la première sortie réussie de la crique et les saynètes vues ont un état neuf.
local recit = {}

function recit.SauvetageFini(d)
  return d ~= nil and (d.CelebrationNilo == 'termine' or d.AlerteShinx == 'termine'
    or (d.AlerteShinx ~= 'a_secourir' and (d.GrotteVerdoyanteBossVaincu == true
      or d.GrotteVerdoyantePhase == 4)))
end

function recit.Acte(d)
  if d == nil or d.VisiteVille == 'en_route' or d.CelebrationNilo == 'en_attente' then return nil end
  if d.AlerteShinx == 'a_secourir' then return 'alerte' end
  if recit.SauvetageFini(d) then return 'nilo' end
  if d.RetourAccompli or d.CombatDazzling == 'termine' or d.VisiteVille == 'terminee' then return 'bois' end
  return nil
end

function recit.Crique(d)
  return d ~= nil and d.PassageAquatiqueTermine == true and d.AlerteShinx ~= 'a_secourir'
    and d.VisiteVille ~= 'en_route' and d.CelebrationNilo ~= 'en_attente'
end

-- Chaque ligne est écrite pour un habitant, pas tirée d'une rumeur commune.
-- Col. 1 : Bois Perdus / première visite ; 2 : recherche ; 3 : retrouvailles ;
-- 4 : crique (indépendante, sans spoiler sur Nilo si on y accède plus tôt).
local repliques = {
  Kecleon = {
    'Au retour des Bois Perdus, j’ai compris : une pomme au fond du sac, c’est une pomme introuvable.',
    'Pour Lyra, je prépare des baies qui se reconnaissent au toucher. Dans le noir, la couleur ne sert à rien.',
    'Nilo m’a demandé pourquoi je rangeais les pommes près du bord. Je lui ai laissé choisir la meilleure place.',
    'Du sel sur le sac ? Séchez-le avant d’y remettre les pommes. Sinon, même la plus sucrée aura le goût de la mer.',
  },
  Kecleon_Violet = {
    'Je mets les graines dans un coin à part. Avec les pommes, on finit par croquer dans la mauvaise poche.',
    'J’ai vu quelqu’un vouloir tout acheter d’un coup. J’ai dit non : la panique pèse plus lourd que mes graines.',
    'Zig a déplacé les pommes. Mes graines n’ont pas bougé d’un pouce. Nilo dit qu’il saura donc retrouver au moins un étal.',
    'Les graines craignent l’humidité. J’ai noué le sac violet d’une boucle facile à défaire, même avec des pattes mouillées.',
  },
  Kangourex = {
    'Les sacs qui reviennent des Bois Perdus sont lourds de petites choses qu’on n’ose pas jeter. Je leur fais de la place.',
    'Si Lyra a besoin de ses deux pattes libres, je peux garder ce qu’elle porte. Dites-lui que rien ne presse pour le reprendre.',
    'Nilo m’a confié un caillou. Ce n’est pas un trésor, dit-il. C’est la preuve qu’il a retrouvé le chemin.',
    'Dans un sac trempé, mettez d’abord le papier à sécher. Les coquilles peuvent attendre, elles savent nager.',
  },
  NewObject_3 = {
    'Les pièces sonnent différemment sur le comptoir selon qu’on les a trouvées ou gagnées. Enfin… je les écoute depuis longtemps.',
    'J’ai commencé à compter pour me calmer. Arrivé à cent, j’espérais encore entendre les pas de Lyra et de Nilo sur la place.',
    'Nilo est passé sans une pièce. Il m’a offert un merci. Je l’ai compté quand même.',
    'Les Poké roulent jusque dans les coutures d’un sac mouillé. Je vérifie les coins avant de faire les comptes.',
  },
  NewObject_4 = {
    'Les Bois Perdus laissent des souvenirs confus. Racontez d’abord ce que vous avez fait ensemble, pas le nombre de virages.',
    'Il ne faut pas remplir le silence à tout prix. Dans la Fosse, le moindre appel de Nilo comptera.',
    'On se souviendra de qui a ramené Nilo. N’oublions pas de lui demander ce qu’il souhaite garder de ce retour.',
    'Dans la crique, éloignez-vous de l’entrée, juste assez pour écouter. Les tunnels ne rendent pas tous les sons à la même vitesse.',
  },
  NewObject_24 = {
    'J’avais appelé ça un loquet « solide ». Puis une équipe est rentrée des Bois Perdus sans réussir à ouvrir son propre sac.',
    'Je garde le marteau levé une seconde de plus avant de frapper. Je tends l’oreille, au cas où quelqu’un crierait depuis la place.',
    'J’ai reconnu Léo au bruit de ses pas. Pas besoin de frapper fort pour qu’une nouvelle traverse tout un quartier.',
    'Le sable se loge dans les charnières. Surtout, ne poussez pas plus fort : ouvrez, nettoyez, puis seulement refermez.',
  },
  Bellossom_Boutique = {
    'Les gelées vertes ne sentent pas les Bois Perdus. C’est volontaire : ce goût-là, je préfère vous laisser le raconter.',
    'Je garde une gelée à l’ombre pour Nilo. Non, ce n’est pas une commande. C’est une place réservée.',
    'La gelée a attendu au frais. Nilo m’a demandé de la couper en deux pour Léo. Je n’avais pas prévu ça.',
    'Je vais essayer un parfum de bord de mer… avec des fleurs, pas du sel. Le sel, vous en avez rapporté assez sur les pattes !',
  },
  NewObject_6 = {
    'D’ici, je perdais votre trace dans les Bois Perdus. Je me suis mise à guetter le chemin du retour plutôt que les arbres.',
    'Une ombre sur le chemin de l’est n’est pas forcément quelqu’un. Je reste plus bas pour mieux voir qui revient.',
    'En redescendant, j’ai entendu des rires près de la place. Pour une fois, je n’ai pas eu besoin de monter pour y voir clair.',
    'Le vent ramène une odeur de sel par le carrefour. Si vous voulez la suivre, attendez que les nuages descendent vers la mer.',
  },
  NewObject_7 = {
    'Les éclaboussures, je les confondais avec des pas. Alors j’ai appris le bruit du pont. Ça m’a occupé en attendant votre retour.',
    'Je voulais aller voir jusqu’à la Fosse. Marcel m’a rappelé qu’il valait mieux laisser le chemin dégagé pour Lyra.',
    'J’avais répété un grand discours pour le retour de Nilo… et j’ai seulement réussi à dire « salut ». Il a souri quand même.',
    'J’ai goûté l’eau de mer une fois. Je ne recommencerai pas. Marcel prétend que c’était un test scientifique.',
  },
  NewObject_8 = {
    'J’ai compté les pas avec toi, Nino. Mais les derniers, c’était les leurs. Même sous la pluie, on les reconnaît.',
    'On peut faire quelque chose d’ici. Regarde, Rose a besoin qu’on lui tienne cet endroit libre juste devant la place.',
    'Un « salut », c’était très bien. Il avait déjà entendu assez de grandes voix dans la grotte.',
    'Un test de danse, nuance ! L’eau salée porte bien, mais sur les galets, on glisse au deuxième pas.',
  },
  NewObject_9 = {
    'Léo voulait voir les Bois Perdus de plus près. Je lui ai proposé de commencer par observer comment les équipes en sortent.',
    'J’essaie de me rappeler par où Nilo est passé. À la Fosse, certaines traces disparaissent dès que l’eau monte.',
    'Après l’accueil, je l’ai entendu bâiller. Je ne crois pas avoir jamais été si contente de l’entendre bâiller.',
    'Sur la plage, l’écume efface les traces. Pour retrouver l’entrée du passage, choisissez plutôt un rocher qu’un trait dans le sable.',
  },
  NewObject_10 = {
    'Vous êtes revenus des Bois Perdus en restant ensemble. C’est ça que j’aimerais savoir faire ; pas simplement courir vite.',
    'Je fais deux pas dehors, puis je rentre. Si Nilo revient avant moi, je ne veux pas qu’il trouve la maison vide.',
    'Maman m’a laissé dessiner le chemin jusqu’à la maison avec lui. Pour une fois, j’ai attendu qu’il trace le premier trait.',
    'Je voulais tracer toute la côte. Finalement, je marque juste un rocher qu’on reconnaîtra en revenant. C’est déjà mieux qu’une grande flèche.',
  },
  Nilo_Shinx = {
    nil, nil,
    'Si Kabutops voyait mon dessin, il dirait que la Fosse est plus grande. Mais c’est la maison que je voulais montrer.',
    'Sur mon dessin, la mer prend presque toute la feuille. Il reste juste assez de place pour nous deux sur la plage.',
  },
  NewObject_12 = {
    'Après les Bois, j’ai posé les caisses à l’ombre. Je confondais encore « accueillir » et « se précipiter avec quatre bras ».',
    'Si Lyra appelle, j’ai deux bras pour les provisions et deux pour déblayer. Tant qu’elle n’a pas appelé, je ne bouche pas la route.',
    'J’ai installé les caisses plus bas. Nilo peut maintenant s’asseoir comme tout le monde, sans qu’on ait à le soulever.',
    'Si le retour de la plage vous a fatigués, posez le sac. Pour les caisses, je sais faire. Pour expliquer le chemin, je vous écoute.',
  },
  NewObject_13 = {
    'Je comptais les équipes depuis la berge. Pendant votre absence, j’ai appris qu’on peut compter les retours sans en manquer un seul.',
    'Depuis l’allée de l’est, je vois qui passe. Je ne compte plus les départs ; j’attends un retour.',
    'Je suis revenue près de l’eau. Cette fois, j’ai compté les pattes sur le pont et j’ai entendu Léo rire avant d’avoir fini.',
    'Ondine m’a demandé combien de reflets peut contenir la mer. Je lui ai proposé de commencer par l’étang ; c’est déjà beaucoup !',
  },
  NewObject_14 = {
    'Certains reviennent des Bois Perdus en fanfaronnant. Vous, vous preniez le temps de vérifier que l’autre suivait. Je retiens ça.',
    'Je monte la garde sur la place. Si tout le monde se lance à la suite de Lyra, qui guidera le retour ?',
    'Je ne donne pas de médaille à Nilo pour avoir eu peur. Je lui laisse le droit d’en parler. C’est autre chose.',
    'Un tunnel court à l’aller peut sembler deux fois plus long au retour. Gardez une provision pour le second trajet.',
  },
  NewObject_16 = {
    'De haut, les Bois Perdus ressemblent à une seule masse sombre. Ça m’a rappelé pourquoi on ne commande pas une équipe depuis le ciel.',
    'J’ai failli partir devant. Tyranocif m’a arrêté : les ailes remuent la poussière dans un tunnel. Alors j’attends Nilo ici, avec lui.',
    'Quand Nilo a passé la place, j’ai replié les ailes. Il voulait nous voir, pas disparaître dans une ombre de plus.',
    'Au-dessus de Sablefin, j’ai cru voir deux entrées. D’ici, je ne dessinerai que celle que vous avez vraiment empruntée.',
  },
  Doyen = {
    'Les Bois ne changent pas leur chemin pour nous perdre. Ils le changent parce qu’ils sont vivants. À nous d’apprendre à regarder.',
    'Le vent nous porte parfois des échos. Je ne laisserai personne les prendre pour des nouvelles de Nilo.',
    'Tout à l’heure, on attendait une nouvelle. Maintenant, on peut laisser Nilo décider s’il veut parler. Le vent n’a rien à lui arracher.',
    'Le vent du large se lève avant le vent de la ville. Si vous descendez à Sablefin, écoutez-les tous les deux.',
  },
  Drifloon = {
    'J’ai dessiné le retour des Bois Perdus dans l’air. Nuage dit qu’il manque le passage où on s’arrête pour s’écouter.',
    'J’ai entendu un sifflement. Ce n’était que le vent contre la pierre. Je le redis à Nuage pour qu’il n’attende pas au mauvais endroit.',
    'J’ai voulu aller demander comment c’était là-bas. Finalement, j’ai demandé à Nilo s’il jouerait avec nous demain.',
    'J’ai suivi une rafale jusqu’au carrefour. Elle a continué sur la mer. Moi, je préfère avoir un endroit où revenir.',
  },
  [''] = { -- Nuage : identifiant publié vide, mais GroundEntity appelle bien _Action.
    'Un chemin n’est jamais aussi droit qu’on le dessine dans le vent. Moi, je mets une boucle pour le moment où vous vous êtes retrouvés.',
    'Je suis resté près d’Aurèle. Avant de transmettre un bruit, on attend de savoir si quelqu’un l’a vraiment entendu.',
    'Plume veut dessiner la Fosse. Je lui ai demandé de commencer par la porte de la maison. Nilo saura où finir le dessin.',
    'Je ne confie pas mon dessin de la crique à la brise. Une bourrasque suffit et quelqu’un nous chercherait du mauvais côté.',
  },
  NewObject_11 = {
    'Je garde sur ma carte une ligne vide à la sortie des Bois. C’est là qu’on écrit avec qui on est rentré.',
    'Partir sans connaître les galeries vous ferait chercher deux équipes. Avec Atlas, on prépare plutôt de quoi accueillir celle de Lyra.',
    'Kabutops a pu se tromper et vous avez pris le temps de l’écouter. Sur la carte, j’ajoute « écouter », pas « vaincre ».',
    'Une crique cachée, ça ne mérite pas forcément une flèche sur toutes les cartes. Je noterai le retour, sans dessiner un raccourci à travers la mer.',
  },
  NewObject_20 = {
    'Ma première carte donnait la route, pas le point de rendez-vous. Sillage ne laisse plus celui-là au hasard.',
    'J’ai ouvert le sac de réserve. À l’intérieur, de quoi tenir au chaud. Rien dans ce sac n’a besoin d’un combat pour être utile.',
    'J’avais écrit « attention au gardien ». Je corrige : « demander avant de traverser ». Ce n’est pas la même chose.',
    'Les cartes mouillées se déchirent au pli. Quand on ne peut plus les lire, un compagnon qui se souvient des entrées vaut mieux qu’un beau trait.',
  },
  NewObject_18 = {
    'Zzz… J’avais promis de rester éveillé jusqu’à votre retour… Tout le monde est rentré ? Alors je peux fermer l’autre œil.',
    'M’appeler si Lyra revient… Oui, même si je ronfle. Je dormirai mieux après.',
    'Quelqu’un a chanté sur la place. Je n’ai pas tout entendu, mais j’ai reconnu le rire du petit. Zzz… enfin.',
    'Zzz… Le bruit des vagues, j’en rêve très bien d’ici. Pour les visiter, essayez plutôt quand je suis réveillé.',
  },
  NewObject_21 = {
    'Je voulais cuisiner quelque chose qui sente la forêt. Capucine a dit que les équipes rentraient justement pour changer d’air.',
    'Pas de tarte de fête tant que Nilo n’est pas rentré. Par contre, une part à emporter pour Lyra, ça, je peux faire.',
    'Je lui ai gardé une part sans glaçage. Nilo l’a échangée contre une part avec DEUX rubans. J’aurais dû m’en douter.',
    'J’ai mis une pincée de sel dans la pâte. Une seule ! Ceux qui reviennent de Sablefin en ont eu leur compte pour la journée.',
  },
  NewObject_23 = {
    'Faisons plutôt une tarte qui sente le café. De loin, les équipes reconnaîtront la ville au bon moment.',
    'Je plie l’emballage, pas les rubans. Il faut que Lyra puisse l’ouvrir en tenant son sac de l’autre patte.',
    'Le ruban le plus tordu était pour Nilo. Il l’a pris exprès : « Le chemin, lui non plus, n’était pas droit. »',
    'J’ai essayé de faire une vague de crème. Elle s’est affaissée… Moka dit que ça s’appelle une marée basse.',
  },
  NewObject_15 = {
    'Le lait refroidissait en attendant les équipes des Bois Perdus. Maintenant, je tiens les bols près de moi plutôt que de les remplir d’avance.',
    'Je laisse un bol vide sur la caisse. Dès que Nilo arrive, je saurai à qui le remplir.',
    'Nilo est resté un bon moment à tenir le bol sans boire. Je n’ai pas demandé pourquoi. Je l’ai resservi quand il me l’a tendu.',
    'Un bol chaud après la plage, oui. D’abord, essuyez vos pattes sur le côté. La moitié de la ville ramène du sable !',
  },
  NewObject_17 = {
    'Je fais un détour pendant ma ronde. Les nouveaux qui reviennent des Bois Perdus cherchent rarement le bon pont du premier coup.',
    'Je tiens la petite allée libre. Les voisins tournent en rond ; mes pattes me démangent aussi. Mais Lyra n’a demandé qu’un chemin dégagé.',
    'Je repars en ronde au sud. Si Léo et Nilo me voient de loin, c’est normal. Ils n’ont plus besoin que j’attende devant chez eux.',
    'Un aller à Sablefin et un retour, ce n’est pas la même ronde. Je vérifierai le carrefour à l’heure où les équipes rentrent.',
  },
  NewObject_22 = {
    'Mes Baies Lum n’ont pas servi cette fois. Je les laisse à portée : connaître une forêt ne veut pas dire qu’elle nous reconnaît.',
    'Le bruit d’une cascade couvre même le mien. Si vous trouvez une zone calme, arrêtez-vous une seconde pour y appeler Nilo.',
    'Je ne savais pas que Kabutops avait si peur pour les siens. J’y repenserai avant de dire qu’un lieu est dangereux « à cause » de ceux qui y vivent.',
    'La mousse de la crique ne pousse pas au même endroit que celle des Bois. Un indice, oui. Une raison de risquer une glissade, non.',
  },
  Pijako_Livreur = {
    'J’avais écrit « ils devraient être rentrés ». Maintenant je peux barrer le « devraient ». Ce sont mes lettres préférées.',
    'Pas de lettre de la Fosse, pour l’instant. Je ne remplis pas le vide avec des rumeurs. Si un mot arrive, je le porte.',
    'Je prends la tournée de l’étang. Ondine veut que j’écrive « rentré » sur la bonne page, sans point d’exclamation.',
    'J’ai abandonné l’idée d’expédier une lettre par la mer. La première enveloppe à atteindre l’étang était déjà illisible.',
  },
  Cradopaud_Pecheur = {
    'J’ai vu passer une feuille des Bois. Elle avait pris tant de détours que je l’ai laissée poursuivre en paix.',
    'Je suis resté à la berge. Si l’eau bouge, je regarde le chemin avant de regarder ma ligne.',
    'J’ai remis la ligne à l’eau quand les voix se sont tues sur la place. Je n’avais rien pris. Ce n’était pas le jour pour compter les prises.',
    'La rivière descend à la mer, mais votre barque n’est pas obligée de faire pareil. L’étang, pour apprendre, vaut mieux qu’une marée.',
  },
  Roserade_Fleuriste = {
    'Une guirlande pour le retour, oui, mais basse. Les équipes qui sortent des Bois ont déjà passé assez de temps à regarder en l’air.',
    'J’ai défait les rubans du passage. Vous les retrouverez sur le côté : Lyra n’a pas à chercher son chemin entre mes fleurs.',
    'Je n’ai pas refait toute la guirlande. Juste un petit bout, à la hauteur de Nilo, pour qu’il puisse y mettre le dernier nœud.',
    'Le sel a blanchi vos pattes. On dirait le bord de certaines feuilles. Ces fleurs-là tiennent sur les dunes, pas dans mon vase.',
  },
  Magneton_Garde = {
    'Bzz… Les Bois Perdus n’indiquent pas la sortie. Ici, le pont le peut. Je m’écarte du panneau pour qu’on le lise.',
    'Bzz… Deux unités gardent le pont. La troisième écoute l’est. C’est toujours un seul poste ; nous ne bougeons pas.',
    'Bzz… Nilo compté au retour. Je n’ai pas changé de poste. J’ai changé le côté que je surveille quand il passe.',
    'Bzz… Le sel fait grésiller une de mes unités. Le rapport de marée se fera loin de l’eau, cette fois.',
  },
  Babimanta_Enfant = {
    'Azur compte les équipes. Moi, je compte les reflets de deux silhouettes qui marchent ensemble. Ça fait une équipe, pas deux !',
    'Je suis près de la hutte, pas sur la route. Si Nilo passe, j’attendrai qu’il me voie au lieu de foncer vers lui.',
    'J’ai choisi l’étang pour attendre Pip. On ne compte plus personne aujourd’hui. On écrit seulement ceux qui sont là.',
    'Je veux garder un reflet de la crique sur le papier de Pip. Il dit qu’il me faut un crayon, pas de l’eau. On va essayer.',
  },
  Goinfrex_Voyageur = {
    'J’ai proposé de vérifier si la tarte avait le goût des Bois Perdus. On m’a dit que c’était hors sujet. Du gâchis, à mon avis.',
    'Vous pouvez me laisser près de l’entrée du café. Si Lyra veut une part, elle en aura une entière. J’ai promis.',
    'J’ai promis de ne pas manger sa part. Je n’avais rien promis pour les miettes… mais j’ai demandé quand même.',
    'La crème a fait une vague. Et puis elle a fait une marée basse. Et après, j’ai nettoyé la plage.',
  },
}
local index = {bois=1, alerte=2, nilo=3, crique=4}
function recit.Replique(nom, acte)
  local r = repliques[nom]
  return r and r[index[acte]] or nil
end

-- Positions ancrées (haut-gauche du collider 16x16). Seuls Pip et Ondine
-- changent de carte ; ils sont déjà créés par script, jamais clonés d'une carte.
-- Les commerçants et les sentinelles fixes n'ont pas d'entrée dans ce tableau.
local placements = {
  bois = {
    {'Pijako_Livreur', 'reverie_centre', 648, 1064, 'Down'},
    {'NewObject_6', 'reverie_centre', 704, 680, 'Down'},
    {'Babimanta_Enfant', 'reverie_centre', 680, 1732, 'Left'},
    {'', 'reverie_centre', 1080, 344, 'Up'},
    {'NewObject_17', 'reverie_residentiel', 216, 2600, 'Up'},
  },
  alerte = {
    {'Pijako_Livreur', 'reverie_centre', 736, 1056, 'Down'},
    {'NewObject_6', 'reverie_centre', 680, 712, 'Down'},
    {'NewObject_13', 'reverie_centre', 1392, 1560, 'DownRight'},
    {'Babimanta_Enfant', 'reverie_centre', 656, 1776, 'Up'},
    {'', 'reverie_centre', 1096, 344, 'UpLeft'},
    {'NewObject_17', 'reverie_residentiel', 248, 2592, 'Down'},
  },
  nilo = {
    {'Pijako_Livreur', 'reverie_etang', 1092, 2200, 'Right'},
    {'Babimanta_Enfant', 'reverie_etang', 1124, 2200, 'Left'},
    {'NewObject_6', 'reverie_centre', 704, 736, 'Down'},
    {'NewObject_13', 'reverie_centre', 692, 1752, 'Up'},
    {'', 'reverie_centre', 1080, 352, 'Up'},
    {'NewObject_17', 'reverie_residentiel', 280, 2592, 'Up'},
    {'Nilo_Shinx', 'reverie_residentiel', 720, 2420, 'Up'},
  },
  crique = {
    {'Pijako_Livreur', 'reverie_etang', 1088, 2304, 'DownRight'},
    {'Babimanta_Enfant', 'reverie_etang', 1120, 2312, 'UpLeft'},
  },
}
function recit.Placements(d)
  local choix, ordre = {}, {}
  local function ajouter(liste)
    for _, p in ipairs(liste or {}) do
      if choix[p[1]] == nil then ordre[#ordre+1] = p[1] end
      choix[p[1]] = p
    end
  end
  ajouter(placements[recit.Acte(d)])
  if recit.Crique(d) then ajouter(placements.crique) end
  local resultat = {}
  for _, nom in ipairs(ordre) do resultat[#resultat+1] = choix[nom] end
  return resultat
end

local scenes = {bois={}, alerte={}, nilo={}, crique={}}
local function groupe(acte, id, acteurs, ouverture, chute, emote, pas)
  local fiche = {id=id, acteurs=acteurs, ouverture=ouverture, chute=chute, emote=emote, pas=pas}
  for _, nom in ipairs(acteurs) do
    assert(scenes[acte][nom] == nil, 'Deux saynètes pour '..nom..' : '..acte)
    scenes[acte][nom] = fiche
  end
end
-- Une scène par groupe et par jalon. La première réplique à chaque place
-- met en jeu une décision locale ; les lignes du carnet y répondent, avec
-- les réactions des voisins. Les services suivent, sans consommer d'objet.
local function groupe3(id, acteurs, bois, alerte, nilo)
  groupe('bois', id, acteurs, bois[1], bois[2], bois[3])
  groupe('alerte', id, acteurs, alerte[1], alerte[2], alerte[3])
  groupe('nilo', id, acteurs, nilo[1], nilo[2], nilo[3])
end

groupe3('etals', {'Kecleon','Kecleon_Violet'},
  {'Zag, qu’est-ce qu’on trouverait dans ton sac si je te réveillais en pleine nuit ?', 'Bon. Nouvelle règle : on ferme les yeux pour vérifier son sac.', 'question'},
  {'Zag, j’ai une demande : si quelqu’un prend trois provisions par peur, on lui demande où il veut les ranger.', 'Vérifiez d’abord ce que vous avez. Les deux étals restent ouverts, sans vous presser.', 'sweatdrop'},
  {'Zag, regarde l’ardoise. Nilo a dessiné les pommes de mon côté et laissé une place pour les graines du tien.', 'Eh bien, qu’elle reste comme ça. Pour une fois, cette ardoise sert à autre chose qu’aux prix.', 'happy'})
groupe3('reserve', {'Kangourex'},
  {'Attendez… Si je pose le sac ici, vous pouvez l’ouvrir sans le tenir en l’air.', nil, 'happy'},
  {'La ville devient bruyante quand elle s’inquiète. Ici, on peut encore entendre une patte qui frappe au comptoir.', nil, 'question'},
  {'Chut… Vous voyez le petit coin au fond ? Je garde une place pour quelqu’un qui revient de loin.', nil, 'happy'})
groupe3('banque', {'NewObject_3'},
  {'Écoutez. Une pièce suffit pour faire du bruit : ce n’est pas le bruit qui dit ce qu’il vous reste.', nil, 'question'},
  {'Un, deux, trois… Non. Ce n’était pas quelqu’un à la porte. Juste moi qui ai fait tomber une pièce.', nil, 'sweatdrop'},
  {'J’ai une ligne que je ne sais pas où mettre dans mes comptes. Elle est entre les dépôts et les retraits…', nil, 'happy'})
groupe3('memoire', {'NewObject_4'},
  {'Fermez les yeux. Quand vous pensez au retour, quel est le premier bruit qui vous revient ?', nil, 'question'},
  {'Je n’ai pas de technique à vous enseigner pour ça. Juste une chose : si l’un appelle, l’autre tend l’oreille.', nil, 'question'},
  {'La place parle encore de la Fosse. Tout le monde se souvient d’autre chose. Laissez à chacun sa version.', nil, 'happy'})
groupe3('forge', {'NewObject_24'},
  {'Regardez ce verrou. Du bon métal, du beau travail… mais l’anse était trop petite pour des pattes tremblantes.', nil, 'sweatdrop'},
  {'Un instant. Je vais attendre avant de reprendre la forge…', nil, 'question'},
  {'C’est moi qui fais le plus de bruit ici. Quand j’ai entendu Léo, j’ai posé mon marteau sans même m’en apercevoir.', nil, 'happy'})
groupe3('tente', {'Bellossom_Boutique'},
  {'Approchez sans acheter. Je n’arrive pas à trouver un nom pour ce parfum. « Retour à Réverie », peut-être ?', nil, 'question'},
  {'Je retire celle-ci de l’étal. Voyons… l’endroit le plus frais, c’est derrière les fleurs.', nil, 'question'},
  {'J’avais choisi la plus jolie gelée, pas la plus facile à partager… Vous voulez savoir ce que Nilo en a fait ?', nil, 'happy'})
groupe3('guirlande', {'Roserade_Fleuriste','NewObject_7','NewObject_8'},
  {'Nino, tiens le ruban de ce côté. Marcel, ne le lève pas trop : c’est pour les gens qui marchent, pas pour ceux qui volent.', 'Comme ça, le premier pas en ville est à eux. Nous, on reste sur le côté.', 'happy'},
  {'Retenez les fleurs pendant que je tire sur le nœud. Il faut un passage sans rien au milieu.', 'Voilà. Si vous voulez attendre aussi, mettez-vous avec nous, ici. Le chemin reste à Lyra.', 'question'},
  {'Vous cherchiez la grande guirlande ? J’en ai laissé un morceau sur le bord. C’est Nilo qui l’a noué.', 'Alors on laisse le nœud tordu. Ça lui ressemble, et c’est bien mieux comme ça.', 'happy'})
groupe3('bols', {'NewObject_12','NewObject_15'},
  {'Margot, le bol tremble. C’est le bois de la caisse ou c’est moi ?', 'D’accord. Je lâche la caisse. Je peux vous saluer avec deux bras seulement.', 'sweatdrop'},
  {'Margot, dis-moi ce que je peux porter. Si je reste là sans rien faire, je vais repartir avec mon propre banc.', 'Je le tiens, ton bol. Je le poserai quand j’entendrai les pas sur la place.', 'question'},
  {'Le petit banc ne bouge plus. J’ai vérifié. Je ne sais pas trop si c’était pour lui ou pour moi.', 'Je m’assieds à côté la prochaine fois. Pas en face à poser des questions.', 'happy'})
groupe3('sentinelles', {'NewObject_16','NewObject_14'},
  {'Tyranocif, tu les as vus juste avant la place ? De haut, je croyais les avoir perdus de nouveau.', 'Je resterai ici quand la prochaine équipe reviendra. Tu me diras ce qu’on voit depuis le sol.', 'question'},
  {'Si j’allais juste jusqu’au carrefour ? Je peux me poser avant la sortie est.', 'Tu as raison. Je surveille le chemin avec toi, pas par-dessus tout le monde.', 'sweatdrop'},
  {'J’avais préparé de grands battements d’ailes pour fêter son retour. Au dernier moment, je n’en ai pas eu envie.', 'Je crois que je comprends. Le voir rentrer, c’était déjà une fête.', 'happy'})
groupe3('vent', {'Doyen','Drifloon',''},
  {'Plume, Nuage, ne dessinez pas une carte avant de savoir où les marcheurs ont fait halte.', 'Gardez votre boucle sur le dessin. Un chemin peut changer quand on retrouve quelqu’un.', 'question'},
  {'Vous entendez, là-haut ? Avant de croire que c’est un appel, écoutons si ça recommence.', 'Prêtons l’oreille, oui. Laissons la rumeur au vent ; il saura l’emporter.', 'question'},
  {'On m’a montré deux dessins. Un de la grotte, un de la maison. À votre avis, lequel Nilo voulait finir en premier ?', 'Alors dessinez la maison, et gardez une place pour demain.', 'happy'})
groupe3('boutique_ciel', {'NewObject_6'},
  {'Tenez, essayez de voir la route entre les deux toits. Ce n’est pas de là-haut qu’on voit le mieux quand quelqu’un hésite.', nil, 'question'},
  {'Ce n’est que la cime de cet arbre. La première fois, j’ai cru voir deux voyageurs. Je ne veux pas me tromper de nouveau.', nil, 'sweatdrop'},
  {'Je pensais encore scruter les hauteurs. Et puis, depuis cette allée, un éclat de rire a dépassé le bruit de la cascade.', nil, 'happy'})
groupe3('berges', {'Cradopaud_Pecheur'},
  {'Chut. Regardez le remous, pas le flotteur. Ça vous évitera de tirer trop tôt.', nil, 'question'},
  {'Eh ? J’ai cru entendre des pas. Non, pas encore. L’eau reparle aussitôt qu’on attend un autre bruit.', nil, 'question'},
  {'La ligne est à nouveau tendue. Pourtant, si vous voulez me dire comment ça s’est passé, je peux lâcher la canne.', nil, 'happy'})
groupe3('sieste', {'NewObject_18'},
  {'… Hm ? C’est bien vous, là ? Pas un rêve de plus ?', nil, 'question'},
  {'Zzz… Si vous allez vers l’est… dites-lui qu’on attend…', nil, nil},
  {'Je l’ai entendu. Je n’ai pas bougé d’une feuille, mais je l’ai entendu.', nil, 'happy'})
groupe3('cafe', {'NewObject_21','NewObject_23','Goinfrex_Voyageur'},
  {'Moka, yeux fermés. Qu’est-ce qui te donnerait envie de finir les derniers pas sur le chemin ?', 'Parfait : un parfum pour le retour. Et une part seulement pour le test !', 'question'},
  {'Capucine, regarde l’emballage. Comment le fermer sans faire un nœud qui résiste ?', 'Prêt. On met ça près de la porte, pour les voyageurs qui n’ont pas le temps de s’asseoir.', 'sweatdrop'},
  {'Je compte trois parts découpées, trois rubans… et aucune miette sur l’assiette. Moka ?', 'D’accord. Tu auras la prochaine part entière. Mais celle qui a le ruban tordu est réservée.', 'happy'})
groupe3('cartes', {'NewObject_11','NewObject_20'},
  {'Regarde, Atlas. Ici j’ai dessiné le dernier croisement. Qu’est-ce qui manque ?', 'Je garde la place. La prochaine équipe pourra y poser son propre point de rendez-vous.', 'question'},
  {'Atlas, tourne le sac vers la maison. Je veux pouvoir l’attraper même si j’arrive dans l’autre sens.', 'On reste ici tant qu’on ne nous appelle pas. Un sac disponible vaut mieux qu’un autre disparu.', 'sweatdrop'},
  {'Je ressortais le crayon rouge pour la Fosse. Attends… Tu n’as pas une autre couleur ?', 'Prends le bleu. On ne fait pas de tous les avertissements des interdictions.', 'happy'})
groupe3('ronde', {'NewObject_17'},
  {'On me demande toujours où mène ce pont. Essayez la question inverse : quel endroit voulez-vous retrouver ?', nil, 'question'},
  {'Deux tours de plus, et j’aurai vérifié chaque coin. Mais je garde cet angle : depuis ici, je vois les voisins avant qu’ils se précipitent.', nil, 'sweatdrop'},
  {'Les rues sont tranquilles. J’avais oublié à quel point ça peut être agréable de n’avoir rien à signaler.', nil, 'happy'})
groupe3('poste_sud', {'Magneton_Garde'},
  {'Bzz… Panneau obstrué. Cause identifiée : moi. Je pivote sur place, pas besoin d’envoyer un rapport.', nil, 'sweatdrop'},
  {'Bzz… Écoute à droite. Contrôle à gauche. Unité du milieu, arrête de compter les minutes.', nil, 'question'},
  {'Bzz… Ancien message : « attendre ». Nouveau message : « passage libre ». Ça tient dans le même espace.', nil, 'happy'})
groupe3('mousse', {'NewObject_22'},
  {'Prenez cette odeur de mousse pour un souvenir, pas pour une boussole. Même moi, j’ai dû le réapprendre.', nil, 'question'},
  {'Le bruit mange les cris. Le silence peut vous rendre une voix. Cherchez-le quand la roche vous le permet.', nil, 'question'},
  {'Quelqu’un m’a demandé s’il fallait se méfier de Kabutops. Je lui ai répondu que « se méfier » n’est pas une façon d’écouter.', nil, 'happy'})

groupe('bois', 'lettre', {'Pijako_Livreur'}, 'Attendez, j’ai un mot pour la ville. Ce n’est pas votre adresse. C’est votre arrivée que je note.', nil, 'happy')
groupe('alerte', 'lettre', {'Pijako_Livreur'}, 'Aucun mot dans la sacoche. Je l’ouvre encore une fois… Non. On ne va rien inventer.', nil, 'question')
groupe('bois', 'reflets', {'NewObject_13','Babimanta_Enfant'}, 'Ondine, l’équipe rentre à deux. Dis-moi ce que ça fait dans tes comptes.', 'D’accord, mais le premier reflet est pour moi !', 'question')
groupe('alerte', 'reperes_est', {'NewObject_13'}, 'Je me suis mise de côté. S’il y a des pas derrière le bruit de l’eau, d’ici je pourrai les reconnaître.', nil, 'question')
groupe('alerte', 'reperes_hutte', {'Babimanta_Enfant'}, 'Chut. Je voulais guetter au bord du chemin. On voit aussi bien depuis ici, si on ne saute pas à chaque mouvement.', nil, 'sweatdrop')
groupe('nilo', 'reflets', {'NewObject_13'}, 'J’en avais fait un jeu, au début. Et puis j’ai commencé à reconnaître les gens avant de les compter.', nil, 'happy')
groupe('nilo', 'carnet_etang', {'Pijako_Livreur','Babimanta_Enfant'}, 'J’ai cherché le bon papier. Pas le plus joli. Celui qu’on peut relire même mouillé.', 'Alors voilà : j’écris tout doucement « rentré ». Le reste, on le laisse à ceux qui y étaient.', 'happy', {'Pijako_Livreur', 8, 0})
groupe('bois', 'famille', {'NewObject_9','NewObject_10'}, 'Léo, les équipes ne rentrent pas toujours par le chemin où elles sont parties. Demande-leur lequel elles ont pris.', 'Très bien. Aujourd’hui, on marche côte à côte jusqu’au pont, sans chronomètre.', 'happy')
groupe('alerte', 'fenetre', {'NewObject_10'}, '… Attendez. J’ai cru que quelqu’un frappait à la porte. C’était juste moi qui l’avais laissée mal fermée.', nil, 'question')
groupe('nilo', 'famille', {'NewObject_9','NewObject_10','Nilo_Shinx'}, 'Vous tombez bien. Léo et Nilo ont quelque chose à me montrer. Faites un peu de place, que je voie aussi.', 'On l’accroche près de la porte ? Comme ça, même le jour où tu n’as pas envie de parler, ton dessin pourra rester là.', 'happy')
-- Lyra à la place / à la sortie E2 conserve sa scène et son vrai menu de départ.
-- La crique a son propre ensemble de saynètes. Aucun texte n'exige que
-- l'alerte de Nilo ait déjà eu lieu ; l'ordre de découverte est libre.
groupe('crique', 'carnet_etang', {'Pijako_Livreur','Babimanta_Enfant'}, 'Ondine, prends le papier par le bord. Il sèche encore. Oui, je sais que tu n’as presque pas de doigts.', 'Eh bien, dessinons la crique sans la remplir d’eau. On pourra prêter le carnet à Azur ainsi.', 'question', {'Pijako_Livreur', 8, 0})
groupe('crique', 'tarte_sale', {'NewObject_21','NewObject_23','Goinfrex_Voyageur'}, 'Capucine, on refait la vague avec moins de crème ? Il ne reste déjà plus rien de la précédente.', 'Ça suffit pour la pâtisserie marine : la prochaine vague, on ira la voir à la plage.', 'happy')
groupe('crique', 'carte_cote', {'NewObject_11','NewObject_20'}, 'Atlas, viens voir : la ligne bleue s’arrête ici. Ce n’est pas un chemin, c’est le bord de l’eau.', 'Ça restera une carte pour rentrer. La prochaine crique, on la découvrira sur place.', 'question')
groupe('crique', 'etals', {'Kecleon','Kecleon_Violet'}, 'Zag, secoue donc ce sac. Tu entends quelque chose ? Ce n’est pas le bruit habituel des graines.', 'Bien. Au retour de la plage, on ouvre les sacs dehors. Pas au-dessus des étals.', 'sweatdrop')
groupe('crique', 'reserve', {'Kangourex'}, 'Par ici, sur le bord. Si on pose votre sac au milieu, tout le monde va croire que le sol a pris l’eau.', nil, 'sweatdrop')
groupe('crique', 'banque', {'NewObject_3'}, 'Celle-là fait « toc », pas « ting ». Posez-la là… Ah, c’était un galet. Bon, je comprends mieux.', nil, 'question')
groupe('crique', 'memoire', {'NewObject_4'}, 'Sans fermer les yeux, dites-moi : qu’avez-vous remarqué de la crique AVANT d’avoir aperçu la mer ?', nil, 'question')
groupe('crique', 'forge', {'NewObject_24'}, 'On dirait que ce loquet résiste. Écoutez juste sous le pouce : ce grincement, c’est du sable, pas du métal.', nil, 'exclaim')
groupe('crique', 'tente', {'Bellossom_Boutique'}, 'Sentez un peu, sans goûter. Les fleurs donnent déjà l’impression de marcher sur les dunes.', nil, 'question')
groupe('crique', 'guirlande', {'Roserade_Fleuriste','NewObject_7','NewObject_8'}, 'Doucement avec cette tige. Ce n’est pas un roseau, elle vient de plus près de la mer.', 'Pour la guirlande, je vais garder ce qui pousse ici. Pour le bord de mer, mieux vaut aller le voir.', 'sweatdrop')
groupe('crique', 'bols', {'NewObject_12','NewObject_15'}, 'Margot, cette caisse pèse le double depuis qu’elle est revenue du sud. Je peux la poser à sécher de ton côté ?', 'D’accord, dehors. Et je préviens la prochaine équipe avant qu’elle repasse avec du sable partout.', 'question')
groupe('crique', 'sentinelles', {'NewObject_16','NewObject_14'}, 'Tyranocif, depuis le ciel je vois la plage. De là à connaître le tunnel… c’est un autre trajet.', 'Alors je poserai mes ailes avant de donner des indications. C’est entendu.', 'question')
groupe('crique', 'vent', {'Doyen','Drifloon',''}, 'Plume me dit que le vent va vers le large. Nuage, regarde ici : les feuilles ne vont pas toutes dans le même sens.', 'Gardez au moins un repère qui ne flotte pas. Sinon, on rentre avec le vent au lieu de rentrer chez soi.', 'question')
groupe('crique', 'boutique_ciel', {'NewObject_6'}, 'Distinguez-vous cette lumière par-delà les toits ? À cette heure, c’est la mer qui renvoie le soleil.', nil, 'happy')
groupe('crique', 'berges', {'Cradopaud_Pecheur'}, 'La ligne va vers la chute. Si je la laisse faire, elle ne s’arrêtera pas d’elle-même avant la mer.', nil, 'question')
groupe('crique', 'sieste', {'NewObject_18'}, '… Une grande vague… puis une autre… Non, ne parlez pas, je les compte pour m’endormir.', nil, nil)
groupe('crique', 'reperes', {'NewObject_13'}, 'J’en étais à cinq… Ondine est passée. Depuis, on n’arrive plus à savoir si on compte les choses ou leurs reflets.', nil, 'sweatdrop')
groupe('crique', 'ronde', {'NewObject_17'}, 'Non, je ne suis pas perdu ! J’essaie de suivre la ronde dans l’autre sens pour voir quand les sacs vont revenir.', nil, 'sweatdrop')
groupe('crique', 'poste_sud', {'Magneton_Garde'}, 'Bzz… Rapport, unité une. Unité une ? Ce n’est pas le vent qui fait ce grésillement…', nil, 'question')
groupe('crique', 'mousse', {'NewObject_22'}, 'Touchez cette pierre, puis dites-moi si vous feriez le même pas sur celle qui luit à côté.', nil, 'question')
groupe('crique', 'maree_famille', {'NewObject_9','NewObject_10'}, 'Léo, tu voudrais d’abord dessiner la mer. Mais à quel endroit on rentre, sur ton papier ?', 'On garde le rocher. Et une feuille à part, pour ce qui ne sert pas à s’orienter.', 'question')
groupe('crique', 'maree_nilo', {'Nilo_Shinx'}, 'Léo dit que mon dessin déborde. Évidemment qu’il déborde, c’est la mer !', nil, 'happy')

function recit.Scene(nom, acte)
  return scenes[acte] and scenes[acte][nom] or nil
end

return recit
