-- Données du quiz de personnalité PMD Destiny (20 questions, 16 natures,
-- pool starters gen 1-9 + extras, mapping, méga-évolution).
--
-- Le format des questions s'inspire des tests de personnalité de
-- Pokémon Mystery Dungeon : Rouge Rescue Team et Explorers of Sky —
-- 20 situations parlantes, 5 choix axés sur la personnalité (certains
-- choix tiennent en plusieurs phrases, certaines questions se répondent
-- par « Oui » ou « Non »). Aucun compteur n'est affiché dans le dialogue.
--
-- Chaque choix crédite deux natures : +4 pour la nature dominante du
-- choix, +2 pour la nature secondaire. À la fin, la nature au score
-- maximal désigne le starter proposé via quiz_data.mapping.
local quiz_data = {}

quiz_data.questions = {
  { texte = "Une nouvelle journée d'aventure commence ! Comment la commences-tu ?", choix = {
    { texte = "Je prépare déjà mon sac et ma carte ! Demain ne m'attendra pas.", points = { hardy = 4, bold = 2 } },
    { texte = "Je contemple le ciel un moment… et je vois où mes pieds me mènent.", points = { relaxed = 4, calm = 2 } },
    { texte = "Je fonce réveiller tout le monde avec des cris de joie !", points = { jolly = 4, hasty = 2 } },
    { texte = "J'observe les autres s'agiter, et je les rejoins sans bruit.", points = { quiet = 4, timid = 2 } },
    { texte = "Je mijote une surprise pour surprendre les copains au réveil.", points = { impish = 4, quirky = 2 } },
  } },
  { texte = "Un trésor scintille au fond d'une grotte sombre. Personne ne te voit.", choix = {
    { texte = "J'y vais sans hésiter !", points = { brave = 4, rash = 2 } },
    { texte = "J'observe d'abord les alentours, patiemment.", points = { quiet = 4, timid = 2 } },
    { texte = "J'appelle un ami : à deux, c'est mieux !", points = { docile = 4, jolly = 2 } },
    { texte = "Je garde la trouvaille pour moi… chacun a son jardin secret.", points = { lonely = 4, sassy = 2 } },
    { texte = "Je conçois une astuce pour l'attraper sans danger.", points = { hardy = 4, calm = 2 } },
  } },
  { texte = "Ton partenaire t'invite à explorer un canyon inconnu, ce soir même, sans préparation.", choix = {
    { texte = "Oui ! L'aventure ne peut pas attendre.", points = { brave = 4, rash = 2 } },
    { texte = "Non. On prépare nos sacs, et on part demain frais et dispos.", points = { calm = 4, hardy = 2 } },
  } },
  { texte = "Ton partenaire raconte une blague nulle pendant le repas.", choix = {
    { texte = "J'éclate de rire, c'est hilarant !", points = { jolly = 4, naive = 2 } },
    { texte = "Je lève un sourcil… puis je lâche un petit sourire.", points = { sassy = 4, quirky = 2 } },
    { texte = "Je note la blague pour la resservir plus tard, au meilleur moment.", points = { impish = 4, lonely = 2 } },
    { texte = "Je remercie mon partenaire : il a essayé pour nous faire rire.", points = { docile = 4, calm = 2 } },
    { texte = "Je propose une blague encore plus nulle !", points = { rash = 4, bold = 2 } },
  } },
  { texte = "Dans un donjon, le groupe hésite entre deux chemins.", choix = {
    { texte = "Je propose un plan et je lance le groupe.", points = { bold = 4, hardy = 2 } },
    { texte = "Je demande l'avis de chacun avant de trancher.", points = { docile = 4, calm = 2 } },
    { texte = "Je prends le chemin le plus dangereux, forcément.", points = { brave = 4, rash = 2 } },
    { texte = "Je laisse les autres choisir, je suivrai avec plaisir.", points = { relaxed = 4, naive = 2 } },
    { texte = "Je lance une pièce ! Le destin décidera pour nous.", points = { quirky = 4, hasty = 2 } },
  } },
  { texte = "Tu trouves un Poké Ball abandonné sur la plage.", choix = {
    { texte = "Je l'ouvre tout de suite, je suis trop curieux !", points = { naive = 4, hasty = 2 } },
    { texte = "Je le garde, il a peut-être une histoire.", points = { lonely = 4, quiet = 2 } },
    { texte = "Je le rapporte au bureau des explorateurs.", points = { docile = 4, hardy = 2 } },
    { texte = "Je le jette à l'eau pour voir s'il flotte !", points = { impish = 4, rash = 2 } },
    { texte = "J'attends patiemment que quelqu'un revienne le chercher.", points = { calm = 4, relaxed = 2 } },
  } },
  { texte = "Un Pokémon plus fort que toi te provoque en duel.", choix = {
    { texte = "Jamais je ne refuse un défi !", points = { brave = 4, bold = 2 } },
    { texte = "Je prépare une ruse pour gagner autrement.", points = { impish = 4, quirky = 2 } },
    { texte = "Je décline poliment : mon équipe m'attend ailleurs.", points = { calm = 4, docile = 2 } },
    { texte = "Je fuis… mais j'en rêve toute la nuit.", points = { timid = 4, lonely = 2 } },
    { texte = "J'accepte et je frappe le premier ! Ou le deuxième.", points = { rash = 4, hasty = 2 } },
  } },
  { texte = "La fête de la ville bat son plein ce soir.", choix = {
    { texte = "Je suis le premier sur la piste de danse, sans attendre !", points = { hasty = 4, jolly = 2 } },
    { texte = "Je préfère une petite veillée tranquille au bord de l'eau.", points = { relaxed = 4, lonely = 2 } },
    { texte = "J'organise les jeux et les concours de la soirée.", points = { bold = 4, docile = 2 } },
    { texte = "Je mijote une surprise spectaculaire pour la fin de la fête.", points = { impish = 4, quirky = 2 } },
    { texte = "Je regarde les étoiles en silence, loin du bruit.", points = { quiet = 4, calm = 2 } },
  } },
  { texte = "On te confie une mission secrète de la guilde.", choix = {
    { texte = "Je note tout et je suis le plan à la lettre.", points = { hardy = 4, docile = 2 } },
    { texte = "Je m'adapte au fur et à mesure, ça ira !", points = { quirky = 4, naive = 2 } },
    { texte = "Je vérifie chaque détail avant de partir.", points = { sassy = 4, calm = 2 } },
    { texte = "Je pars immédiatement, la mission ne peut pas attendre !", points = { hasty = 4, rash = 2 } },
    { texte = "Je demande un coéquipier : les missions se partagent.", points = { jolly = 4, brave = 2 } },
  } },
  { texte = "Un ami garde un lourd secret et te le confie.", choix = {
    { texte = "Je le garde religieusement.", points = { calm = 4, sassy = 2 } },
    { texte = "Je lui trouve une solution, tout de suite !", points = { hasty = 4, bold = 2 } },
    { texte = "Je l'écoute en silence, aussi longtemps qu'il faudra.", points = { quiet = 4, docile = 2 } },
    { texte = "Je lui confie un de mes secrets pour l'aider à s'alléger.", points = { lonely = 4, naive = 2 } },
    { texte = "Je le transforme en devinette pour le rendre moins lourd.", points = { quirky = 4, jolly = 2 } },
  } },
  { texte = "Tu découvres une fleur rare. Personne ne te voit.", choix = {
    { texte = "Je la cueille pour l'offrir à quelqu'un.", points = { docile = 4, jolly = 2 } },
    { texte = "Je la laisse, elle est plus belle ici.", points = { quiet = 4, calm = 2 } },
    { texte = "Je la dessine et je repars fier de ma découverte.", points = { hardy = 4, relaxed = 2 } },
    { texte = "Je la garde pour moi, mon petit secret botanique.", points = { lonely = 4, sassy = 2 } },
    { texte = "Je la sens, je la goûte… elle pique ! Aïe !", points = { naive = 4, rash = 2 } },
  } },
  { texte = "La pluie tombe enfin sur les cultures de la guilde.", choix = {
    { texte = "Parfait pour courir dehors, les pieds dans la boue !", points = { rash = 4, hasty = 2 } },
    { texte = "Parfait pour lire sous le porche, au chaud.", points = { quiet = 4, timid = 2 } },
    { texte = "Parfait pour danser sous la pluie avec les copains !", points = { jolly = 4, naive = 2 } },
    { texte = "Parfait pour vérifier que les récoltes tiennent le coup.", points = { hardy = 4, docile = 2 } },
    { texte = "Parfait pour contempler le ciel changer de couleur.", points = { relaxed = 4, calm = 2 } },
  } },
  { texte = "Un inconnu te demande ton aide pour porter son fardeau jusqu'au village.", choix = {
    { texte = "Oui, bien sûr ! En route.", points = { naive = 4, docile = 2 } },
    { texte = "Non, je regarde d'abord ce qu'il transporte.", points = { timid = 4, sassy = 2 } },
  } },
  { texte = "Ton équipe perdra la finale si tu ne trouves pas l'idée gagnante.", choix = {
    { texte = "Je lance une idée folle, on verra bien !", points = { quirky = 4, rash = 2 } },
    { texte = "Je me concentre et je respire, l'idée viendra.", points = { relaxed = 4, hardy = 2 } },
    { texte = "Je motive tout le monde à voix haute !", points = { bold = 4, jolly = 2 } },
    { texte = "Je laisse les meilleurs stratèges décider pour nous tous.", points = { calm = 4, docile = 2 } },
    { texte = "Je tente le tout pour le tout, à la dernière minute !", points = { brave = 4, hasty = 2 } },
  } },
  { texte = "On te propose de diriger une expédition lointaine.", choix = {
    { texte = "Je pars, l'inconnu m'appelle !", points = { lonely = 4, brave = 2 } },
    { texte = "Je préfère veiller sur ceux qui restent.", points = { calm = 4, bold = 2 } },
    { texte = "Je pars si on m'emmène avec mes trésors préférés.", points = { naive = 4, quirky = 2 } },
    { texte = "J'étudie la route et les dangers avant de répondre.", points = { sassy = 4, quiet = 2 } },
    { texte = "On y va en équipe, ou pas du tout !", points = { docile = 4, jolly = 2 } },
  } },
  { texte = "Pour toi, une belle aventure c'est surtout…", choix = {
    { texte = "…des amis avec qui la vivre !", points = { jolly = 4, docile = 2 } },
    { texte = "…la sensation d'être pleinement soi-même.", points = { lonely = 4, sassy = 2 } },
    { texte = "…un grand mystère à résoudre de bout en bout.", points = { quirky = 4, quiet = 2 } },
    { texte = "…un défi à relever, toujours plus haut.", points = { brave = 4, bold = 2 } },
    { texte = "…un voyage sans empêchement, au fil de l'eau.", points = { relaxed = 4, calm = 2 } },
  } },
  { texte = "Sous les étoiles, à quoi rêves-tu pour ton avenir ?", choix = {
    { texte = "Devenir le plus grand explorateur de tous les temps !", points = { brave = 4, bold = 2 } },
    { texte = "Des amis fidèles et des rires pour toujours.", points = { jolly = 4, docile = 2 } },
    { texte = "Une cabane tranquille au bord d'un lac.", points = { relaxed = 4, calm = 2 } },
    { texte = "Résoudre un mystère que personne n'a jamais percé.", points = { quirky = 4, quiet = 2 } },
    { texte = "Prouver à tous ceux qui me sous-estimaient.", points = { lonely = 4, rash = 2 } },
  } },
  { texte = "Tu découvres qu'un ami a menti sur un petit détail sans importance.", choix = {
    { texte = "Je lui en parle franchement, mais avec douceur.\nLes amis méritent la vérité, même pour les petites choses.", points = { hardy = 4, docile = 2 } },
    { texte = "Je fais semblant de ne rien avoir remarqué.\nS'il voulait me le dire, il l'aurait fait ; ce n'est pas grave.", points = { calm = 4, relaxed = 2 } },
    { texte = "Je lui prépare une histoire encore plus rocambolesque.\nIl verra bien : les mensonges, ça se retourne toujours !", points = { impish = 4, quirky = 2 } },
    { texte = "Je m'en fais du souci en silence.\nAi-je fait quelque chose pour qu'il ne me fasse pas confiance ?", points = { timid = 4, lonely = 2 } },
  } },
  { texte = "La guilde te propose de diriger l'expédition de demain. C'est ta première fois.", choix = {
    { texte = "Oui, je suis prêt à guider tout le monde !", points = { bold = 4, brave = 2 } },
    { texte = "Non, je préfère seconder quelqu'un d'expérimenté.", points = { timid = 4, docile = 2 } },
  } },
  { texte = "La veille de ta première grande aventure, tu…", choix = {
    { texte = "Je vérifie mon sac trois fois et je me couche tôt.\nDemain, rien ne doit pouvoir m'arrêter.", points = { hardy = 4, calm = 2 } },
    { texte = "Je reste debout tard à rêver de tout ce qui m'attend.\nLe sommeil, ce sera après l'aventure !", points = { naive = 4, hasty = 2 } },
    { texte = "Je rejoins mes amis pour un dernier goûter ensemble.\nLes grands départs ont besoin de douceur.", points = { jolly = 4, docile = 2 } },
    { texte = "Je marche seul dans la nuit pour me prouver que je suis prêt.\nLe silence et moi, on se comprend.", points = { lonely = 4, brave = 2 } },
    { texte = "Je glisse deux ou trois surprises dans mon sac.\nOn ne sait jamais : l'aventure adore les astuces !", points = { impish = 4, quirky = 2 } },
  } },
}

quiz_data.natures = {
  { slug = "hardy", fr = "Hardi", en = "Hardy", couleur = "Or", hex = "#E8A020" },
  { slug = "docile", fr = "Docile", en = "Docile", couleur = "Sable", hex = "#D8C050" },
  { slug = "brave", fr = "Brave", en = "Brave", couleur = "Écarlate", hex = "#E03028" },
  { slug = "jolly", fr = "Joyeux", en = "Jolly", couleur = "Citron", hex = "#E8D828" },
  { slug = "impish", fr = "Malicieux", en = "Impish", couleur = "Améthyste", hex = "#9040D0" },
  { slug = "naive", fr = "Naïf", en = "Naive", couleur = "Rose", hex = "#F070B0" },
  { slug = "timid", fr = "Timide", en = "Timid", couleur = "Bleu brume", hex = "#6098D8" },
  { slug = "hasty", fr = "Pressé", en = "Hasty", couleur = "Mandarine", hex = "#F06820" },
  { slug = "sassy", fr = "Malin", en = "Sassy", couleur = "Indigo", hex = "#5848C8" },
  { slug = "calm", fr = "Calme", en = "Calm", couleur = "Menthe", hex = "#40C898" },
  { slug = "relaxed", fr = "Relax", en = "Relaxed", couleur = "Lagune", hex = "#28A0B8" },
  { slug = "lonely", fr = "Solo", en = "Lonely", couleur = "Bleu nuit", hex = "#28406E" },
  { slug = "quirky", fr = "Bizarre", en = "Quirky", couleur = "Cyan", hex = "#28C8C8" },
  { slug = "quiet", fr = "Discret", en = "Quiet", couleur = "Émeraude", hex = "#28B058" },
  { slug = "rash", fr = "Précipité", en = "Rash", couleur = "Magenta", hex = "#D02890" },
  { slug = "bold", fr = "Assuré", en = "Bold", couleur = "Saphir", hex = "#2858D0" },
}

quiz_data.starters = {
  ["bulbasaur"] = { espece = "bulbasaur", forme = 0, nom = "Bulbizarre", gen = 1, talents = { "Engrais", "Chlorophylle" }, mega = "Méga-Bulbizarre" },
  ["charmander"] = { espece = "charmander", forme = 0, nom = "Reptincel", gen = 1, talents = { "Brasier" }, mega = "Méga-Reptincel" },
  ["squirtle"] = { espece = "squirtle", forme = 0, nom = "Carapuce", gen = 1, talents = { "Torrent", "Cuvette" }, mega = "Méga-Carapuce" },
  ["pikachu"] = { espece = "pikachu", forme = 0, nom = "Pikachu", gen = 1, talents = { "Statik", "Paratonnerre" }, mega = nil },
  ["eevee"] = { espece = "eevee", forme = 0, nom = "Évoli", gen = 1, talents = { "Adaptabilité", "Anticipation", "Cœur Noble" }, mega = nil },
  ["meowth"] = { espece = "meowth", forme = 0, nom = "Miaouss", gen = 1, talents = { "Ramassage", "Technicien", "Tension" }, mega = nil },
  ["goupix"] = { espece = "vulpix", forme = 0, nom = "Goupix", gen = 1, talents = { "Torche", "Sécheresse" }, mega = nil },
  ["goupix_alola"] = { espece = "vulpix", forme = 1, nom = "Goupix d'Alola", gen = 7, talents = { "Voile Neige" }, mega = nil },
  ["chikorita"] = { espece = "chikorita", forme = 0, nom = "Germignon", gen = 2, talents = { "Engrais", "Feuille Magique" }, mega = nil },
  ["cyndaquil"] = { espece = "cyndaquil", forme = 0, nom = "Héricendre", gen = 2, talents = { "Brasier", "Turbo" }, mega = nil },
  ["totodile"] = { espece = "totodile", forme = 0, nom = "Kaiminus", gen = 2, talents = { "Torrent", "Agitation" }, mega = nil },
  ["treecko"] = { espece = "treecko", forme = 0, nom = "Arcko", gen = 3, talents = { "Engrais", "Glissade" }, mega = "Méga-Arcko" },
  ["torchic"] = { espece = "torchic", forme = 0, nom = "Poussifeu", gen = 3, talents = { "Brasier", "Turbo" }, mega = "Méga-Poussifeu" },
  ["mudkip"] = { espece = "mudkip", forme = 0, nom = "Gobou", gen = 3, talents = { "Torrent", "Glissade" }, mega = "Méga-Gobou" },
  ["skitty"] = { espece = "skitty", forme = 0, nom = "Skitty", gen = 3, talents = { "Jolie Grâce", "Normalise", "Peau Miracle" }, mega = nil },
  ["turtwig"] = { espece = "turtwig", forme = 0, nom = "Tortipouss", gen = 4, talents = { "Engrais", "Coque Armure" }, mega = nil },
  ["chimchar"] = { espece = "chimchar", forme = 0, nom = "Ouisticram", gen = 4, talents = { "Brasier", "Poing de Fer" }, mega = nil },
  ["piplup"] = { espece = "piplup", forme = 0, nom = "Tiplouf", gen = 4, talents = { "Torrent", "Acharné" }, mega = nil },
  ["snivy"] = { espece = "snivy", forme = 0, nom = "Vipélierre", gen = 5, talents = { "Engrais", "Contestation" }, mega = nil },
  ["tepig"] = { espece = "tepig", forme = 0, nom = "Gruikui", gen = 5, talents = { "Brasier", "Isograisse" }, mega = nil },
  ["oshawott"] = { espece = "oshawott", forme = 0, nom = "Moustillon", gen = 5, talents = { "Torrent", "Coque Armure" }, mega = nil },
  ["zorua"] = { espece = "zorua", forme = 0, nom = "Zorua", gen = 5, talents = { "Illusion" }, mega = nil },
  ["chespin"] = { espece = "chespin", forme = 0, nom = "Marisson", gen = 6, talents = { "Engrais", "Poing de Fer" }, mega = nil },
  ["fennekin"] = { espece = "fennekin", forme = 0, nom = "Feunnec", gen = 6, talents = { "Brasier", "Magicien" }, mega = nil },
  ["froakie"] = { espece = "froakie", forme = 0, nom = "Grenousse", gen = 6, talents = { "Torrent", "Protéen" }, mega = nil },
  ["rowlet"] = { espece = "rowlet", forme = 0, nom = "Brindibou", gen = 7, talents = { "Engrais", "Impassible" }, mega = nil },
  ["litten"] = { espece = "litten", forme = 0, nom = "Flamiaou", gen = 7, talents = { "Brasier", "Tension" }, mega = nil },
  ["popplio"] = { espece = "popplio", forme = 0, nom = "Otaquin", gen = 7, talents = { "Torrent", "Hydratation" }, mega = nil },
  ["zorua_hisui"] = { espece = "zorua", forme = 1, nom = "Zorua de Hisui", gen = 8, talents = { "Ruse" }, mega = nil },
  ["grookey"] = { espece = "grookey", forme = 0, nom = "Ouistempo", gen = 8, talents = { "Engrais", "Agitation" }, mega = nil },
  ["scorbunny"] = { espece = "scorbunny", forme = 0, nom = "Flambino", gen = 8, talents = { "Brasier", "Turbo" }, mega = nil },
  ["sobble"] = { espece = "sobble", forme = 0, nom = "Larméléon", gen = 8, talents = { "Torrent", "Sniper" }, mega = nil },
  ["sprigatito"] = { espece = "sprigatito", forme = 0, nom = "Poussacha", gen = 9, talents = { "Engrais", "Progné" }, mega = nil },
  ["fuecoco"] = { espece = "fuecoco", forme = 0, nom = "Chochodile", gen = 9, talents = { "Brasier", "Inconscient" }, mega = nil },
  ["quaxly"] = { espece = "quaxly", forme = 0, nom = "Coiffeton", gen = 9, talents = { "Torrent", "Tension" }, mega = nil },
  ["charcadet"] = { espece = "charcadet", forme = 0, nom = "Charbamm", gen = 9, talents = { "Armure de Feu", "Flash Fire" }, mega = nil },
}

quiz_data.mapping = {
  ["hardy"] = "pikachu",
  ["docile"] = "eevee",
  ["brave"] = "charcadet",
  ["jolly"] = "goupix",
  ["impish"] = "zorua",
  ["naive"] = "skitty",
  ["timid"] = "goupix_alola",
  ["hasty"] = "charmander",
  ["sassy"] = "zorua_hisui",
  ["calm"] = "bulbasaur",
  ["relaxed"] = "squirtle",
  ["lonely"] = "mudkip",
  ["quirky"] = "meowth",
  ["quiet"] = "rowlet",
  ["rash"] = "chespin",
  ["bold"] = "piplup",
}

-- Noms français et couleurs des types (Element1) pour la révélation
-- finale : « Quelqu'un comme toi serait [Nom en couleur du type] ! ».
-- Les hex sont partagés avec tools/generer_etoile_quiz.py (étoiles BG).
quiz_data.couleurs_types = {
  ["normal"] = { hex = "#A8A878", fr = "Normal" },
  ["fire"] = { hex = "#F08030", fr = "Feu" },
  ["water"] = { hex = "#6890F0", fr = "Eau" },
  ["grass"] = { hex = "#78C850", fr = "Plante" },
  ["electric"] = { hex = "#F8D030", fr = "Électrik" },
  ["ice"] = { hex = "#98D8D8", fr = "Glace" },
  ["fighting"] = { hex = "#C03028", fr = "Combat" },
  ["poison"] = { hex = "#A040A0", fr = "Poison" },
  ["ground"] = { hex = "#E0C068", fr = "Sol" },
  ["flying"] = { hex = "#A890F0", fr = "Vol" },
  ["psychic"] = { hex = "#F85888", fr = "Psy" },
  ["bug"] = { hex = "#A8B820", fr = "Insecte" },
  ["rock"] = { hex = "#B8A038", fr = "Roche" },
  ["ghost"] = { hex = "#705898", fr = "Spectre" },
  ["dragon"] = { hex = "#7038F8", fr = "Dragon" },
  ["dark"] = { hex = "#705848", fr = "Ténèbres" },
  ["steel"] = { hex = "#B8B8D0", fr = "Acier" },
  ["fairy"] = { hex = "#EE99AC", fr = "Fée" },
  ["none"] = { hex = "#9098A0", fr = "Incolore" },
}

-- Texte affiché quand le Pokémon possède une Méga-Évolution.
quiz_data.mega_texte = "MÉGA-ÉVOLUTION"

return quiz_data
