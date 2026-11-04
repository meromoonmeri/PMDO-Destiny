-- Réverie Town : arrivée après les Bois Perdus et présentation des lieux existants.
-- La version town02 étendue contient ses habitants, objets et marqueurs ;
-- Kecleon et Kangourex sérialisés sont réutilisés, avec création en repli
-- uniquement si une ancienne sauvegarde/carte ne les fournit pas.
require 'origin.common'
require 'origin.menu.skill.SkillSelectMenu'
require 'origin.menu.team.AssemblySelectMenu'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'

local ville = {}
local ENTREE_X, ENTREE_Y = 800, 1320
local PLACE_X, PLACE_Y = 800, 1160

-- Habitants sérialisés dans la carte town02 étendue.  Leurs positions
-- initiales sont relevées à l'Init afin que chacun déambule autour de son
-- propre quartier sans traverser toute la ville.
local habitants_vivants = {
  'Kecleon', 'Kecleon_Violet', 'NewObject_3', 'NewObject_4', 'Kangourex',
  'NewObject_6', 'NewObject_7', 'NewObject_8', 'NewObject_9', 'NewObject_10',
  'NewObject_12', 'NewObject_13', 'NewObject_14', 'Doyen', 'Drifloon',
  'NewObject_16', 'NewObject_11', 'NewObject_18', 'NewObject_20',
  'NewObject_21', 'NewObject_15', 'NewObject_17', 'NewObject_22',
  'NewObject_23', 'NewObject_24',
  'Pijako_Livreur', 'Cradopaud_Pecheur', 'Roserade_Fleuriste',
  'Magneton_Garde', 'Babimanta_Enfant', 'Goinfrex_Voyageur',
}
local positions_habitants = {}
local vie_ville_activee = false

-- Services extérieurs : ils restent à leur comptoir ou devant leur bâtiment,
-- sans IA de déambulation, donc dans leur idle par défaut.
local marchands_fixes = {
  Kecleon = true,          -- boutique verte
  Kecleon_Violet = true,   -- boutique violette
  Kangourex = true,        -- réserve d'objets
  NewObject_3 = true,      -- Mordudor, banque
  NewObject_4 = true,      -- Alakazam, souvenirs de capacités
  NewObject_24 = true,     -- Forgelina, ouverture des boîtes
}

-- Discussions réelles : dialogues partagés (Lombre/Ludicolo, Luxio/Luxray)
-- ou duo déjà placé côte à côte (Doyen/Baudrive). Les anciennes paires
-- d'ambiance séparées par plusieurs centaines de pixels ne font plus
-- semblant de discuter à travers la ville.
local paires_discussion = {
  {'NewObject_7', 'NewObject_8'},  -- Lombre et Ludicolo
  {'NewObject_10', 'NewObject_9'}, -- Luxio et Luxray
  {'Doyen', 'Drifloon'},           -- le Doyen et Baudrive
}
local partenaires_discussion = {}
for _, paire in ipairs(paires_discussion) do
  partenaires_discussion[paire[1]] = paire[2]
  partenaires_discussion[paire[2]] = paire[1]
end

local function est_fixe(nom)
  return marchands_fixes[nom] == true or partenaires_discussion[nom] ~= nil
end

local function tourner_vers(acteur, cible)
  if acteur == nil or cible == nil or acteur == cible then return end
  pcall(function() GROUND:CharTurnToChar(acteur, cible) end)
end

local function orienter_discussion(nom)
  local autre_nom = partenaires_discussion[nom]
  if autre_nom == nil then return end
  local acteur, autre = CH(nom), CH(autre_nom)
  tourner_vers(acteur, autre)
  tourner_vers(autre, acteur)
end

local function restaurer_orientation(nom, acteur)
  acteur = acteur or CH(nom)
  if nom == nil or acteur == nil then return end
  if partenaires_discussion[nom] ~= nil then
    orienter_discussion(nom)
    return
  end
  if marchands_fixes[nom] then
    local depart = positions_habitants[nom]
    if depart ~= nil and depart.dir ~= nil then
      pcall(function() GROUND:EntTurn(acteur, depart.dir) end)
    end
  end
end

local function figer_habitant(nom, acteur)
  acteur = acteur or CH(nom)
  if nom == nil or acteur == nil then return end
  pcall(function()
    AI:DisableCharacterAI(acteur)
    GROUND:CharEndAnim(acteur) -- idle par défaut, sans déplacement
  end)
  restaurer_orientation(nom, acteur)
end

-- Tout habitant abordé se tourne vers le joueur avant la première boîte.
-- Les marchands et les duos en discussion reprennent ensuite leur
-- orientation normale ; les promeneurs sont rendus à leur IA.
local function commencer_dialogue(personnage, activator)
  local joueur = CH('PLAYER') or activator
  tourner_vers(personnage, joueur)
end

local function terminer_dialogue(personnage, nom)
  restaurer_orientation(nom, personnage)
end

-- Jour de ville courant : la sieste au café Spinda fait passer au jour
-- suivant (même compteur que la rotation des étals Kecleon).
local function jour_actuel()
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.JourneeVille ~= nil then
    return SV.Destiny.JourneeVille
  end
  return 0
end

-- Choisit la variante de dialogue du jour parmi une liste de variantes.
local function repliques_du_jour(variantes)
  if variantes == nil or #variantes == 0 then return {} end
  return variantes[(jour_actuel() % #variantes) + 1]
end

-- La carte sérialise la plupart des habitants sous des noms d'entité
-- génériques (NewObject_*) : on leur donne leur vrai nom affiché en
-- dialogue, sans toucher à la carte.
local noms_habitants = {
  Kecleon = 'Kecleon', Kecleon_Violet = 'Kecleon violet',
  NewObject_3 = 'Mordudor', NewObject_4 = 'Alakazam', Kangourex = 'Kangourex',
  NewObject_6 = 'Altaria', NewObject_7 = 'Lombre', NewObject_8 = 'Ludicolo',
  NewObject_9 = 'Luxray', NewObject_10 = 'Luxio', NewObject_12 = 'Mackogneur',
  NewObject_13 = 'Marill', NewObject_14 = 'Tyranocif', Doyen = 'Doyen Grodrive',
  Drifloon = 'Baudrive', NewObject_16 = 'Dracaufeu', NewObject_11 = 'Carchacrok',
  NewObject_18 = 'Ronflex', NewObject_20 = 'Drattak', NewObject_21 = 'Cupcanaille',
  NewObject_15 = 'Écrémeuh', NewObject_17 = 'Arcanin', NewObject_22 = 'Arbok',
  NewObject_23 = 'Charmilly', NewObject_24 = 'Forgelina',
  Pijako_Livreur = 'Pijako', Cradopaud_Pecheur = 'Cradopaud',
  Roserade_Fleuriste = 'Roserade', Magneton_Garde = 'Magnéton',
  Babimanta_Enfant = 'Babimanta', Goinfrex_Voyageur = 'Goinfrex',
}

local function habitant(nom, espece, genre, x, y)
  local acteur = CH(nom)
  if acteur == nil then
    local donnees = RogueEssence.Dungeon.CharData()
    donnees.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
    donnees.Nickname = nom
    donnees.Level = 5
    acteur = GROUND:CreateCharacterFromCharData(nom, RogueEssence.Dungeon.Character(donnees), x, y, Direction.Down)
  end
  AI:DisableCharacterAI(acteur)
  acteur:ReloadEvents()
  return acteur
end

local function partenaire_pour(hero)
  local partenaire = CH('Teammate1')
  if partenaire == nil and hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
  end
  return partenaire
end

-- Portes des bâtiments : la carte town02 ne sérialise aucune sortie, on
-- installe donc un objet invisible sur chaque seuil (coordonnées relevées
-- sur le rendu de la carte, à confirmer au runtime). Chaque porte mène à
-- l'intérieur correspondant et mémorise le point de retour devant la façade.
local portes_batiments = {
  {nom = 'PortePosteBekipan', titre = 'Poste Bekipan', x = 60, y = 468, retour_x = 92, retour_y = 516, interieur = 'post_office', marqueur = 'entrance_south'},
  {nom = 'PorteCitrouilleNordOuest', titre = 'Maison citrouille', x = 400, y = 436, retour_x = 412, retour_y = 468, interieur = 'metano_fire_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteHutteNordEst', titre = 'Hutte du nord-est', x = 1028, y = 472, retour_x = 1076, retour_y = 500, interieur = 'metano_water_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteMaisonEquipe', titre = 'Maison de l\'équipe', x = 660, y = 524, retour_x = 676, retour_y = 548, interieur = 'guild_heros_room', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteDojoKingambit', titre = 'Dojo Kingambit', x = 1440, y = 384, retour_x = 1468, retour_y = 428, interieur = 'dojo_kingambit', marqueur = 'MarowakDojoExitMarker'},
  {nom = 'PorteHutteSud', titre = 'Hutte du sud', x = 588, y = 1740, retour_x = 652, retour_y = 1756, interieur = 'metano_electric_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteTenteCentre', titre = 'Campement des explorateurs', x = 788, y = 1688, retour_x = 812, retour_y = 1740, interieur = 'metano_inn', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteTenteEst', titre = 'Dojo de l\'est (Ledian)', x = 1172, y = 1808, retour_x = 1180, retour_y = 1884, interieur = 'ledian_dojo', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteMaisonArcanine', titre = 'Maison d\'Arcanine', x = 140, y = 2552, retour_x = 172, retour_y = 2596, interieur = 'metano_fire_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteMaisonPierre', titre = 'Maison de Pierre', x = 378, y = 2376, retour_x = 444, retour_y = 2396, interieur = 'metano_rock_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteMaisonPlanteSud', titre = 'Maison plante', x = 580, y = 2492, retour_x = 612, retour_y = 2540, interieur = 'metano_grass_home', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteCitrouilleSud', titre = 'Maison citrouille du sud', x = 748, y = 2552, retour_x = 780, retour_y = 2596, interieur = 'metano_fire_home', marqueur = 'Main_Entrance_Marker'},
}

local function installer_une_porte(map, nom, x, y)
  if map == nil or map:FindObject(nom) then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = nom
  porte.Collider = RogueElements.Rect(x, y, 56, 20)
  porte:OnMapInit()
  map:AddObject(porte)
end

local function installer_portes(map)
  -- Café Spinda : tapis rouge de l'annexe (centre x≈1188, y≈1605).
  installer_une_porte(map, 'PorteCafeSpinda', 1020, 1344)
  for _, porte in ipairs(portes_batiments) do
    installer_une_porte(map, porte.nom, porte.x, porte.y)
  end
end

-- Comptoirs des boutiques, façon Metano Town : chaque marchand se tient
-- dans sa boutique, derrière son comptoir, et le joueur lui parle en
-- interagissant devant le comptoir. Le comptoir est un objet invisible
-- infranchissable posé sur la devanture (déjà bloquée par les collisions
-- town02, sauf la terrasse de la forge) ; le poste est l’alcôve fermée de
-- la boutique relevée dans ces mêmes collisions. Les deux Kecleon sont
-- déjà sérialisés derrière leur comptoir : aucun poste à corriger pour
-- eux. Les seuils d’Alakazam, de Kangourex et de la forge deviennent des
-- comptoirs : leurs anciennes portes d’intérieur sont donc retirées.
local comptoirs = {
  {nom = 'ComptoirKecleon', marchand = 'Kecleon', x = 584, y = 936, w = 32, h = 16},
  {nom = 'ComptoirKecleonViolet', marchand = 'Kecleon_Violet', x = 616, y = 936, w = 32, h = 16},
  {nom = 'ComptoirBanqueMordudor', marchand = 'NewObject_3', x = 480, y = 1072, w = 64, h = 16, poste_x = 504, poste_y = 1040},
  {nom = 'ComptoirAlakazam', marchand = 'NewObject_4', x = 352, y = 1120, w = 32, h = 16, poste_x = 360, poste_y = 1100},
  {nom = 'ComptoirKangourex', marchand = 'Kangourex', x = 928, y = 952, w = 40, h = 16, poste_x = 940, poste_y = 930},
  {nom = 'ComptoirForgeTinkaton', marchand = 'NewObject_24', x = 1080, y = 1008, w = 64, h = 16, poste_x = 1104, poste_y = 972},
}

local function installer_comptoirs(map)
  if map == nil then return end
  for _, comptoir_def in ipairs(comptoirs) do
    if not map:FindObject(comptoir_def.nom) then
      local comptoir = RogueEssence.Ground.GroundObject()
      comptoir.EntName = comptoir_def.nom
      comptoir.Collider = RogueElements.Rect(comptoir_def.x, comptoir_def.y, comptoir_def.w, comptoir_def.h)
      pcall(function()
        comptoir.Passable = false
        comptoir:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Action)
      end)
      comptoir:OnMapInit()
      map:AddObject(comptoir)
    end
  end
end

-- Chaque marchand prend son poste derrière son comptoir, face à la rue
-- (sud). Le poste devient sa position de repos mémorisée : après un
-- dialogue, il reprend cette orientation sans jamais quitter la boutique.
local function placer_marchands_aux_comptoirs()
  for _, comptoir_def in ipairs(comptoirs) do
    if comptoir_def.poste_x ~= nil then
      local marchand = CH(comptoir_def.marchand)
      if marchand ~= nil then
        GROUND:TeleportTo(marchand, comptoir_def.poste_x, comptoir_def.poste_y, Direction.Down)
        positions_habitants[comptoir_def.marchand] = {
          x = comptoir_def.poste_x, y = comptoir_def.poste_y, dir = Direction.Down,
        }
      end
    end
  end
end

function ville.Init(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  installer_portes(map)
  installer_comptoirs(map)
  habitant('Kecleon', 'kecleon', Gender.Male, 599, 922)
  habitant('Kangourex', 'kangaskhan', Gender.Female, 940, 930)
  -- Habitants ajoutés (ville vivante) : créés s'ils ne sont pas sérialisés
  -- dans la carte (positions relevées sur le rendu, à confirmer au runtime).
  habitant('Pijako_Livreur', 'chatot', Gender.Male, 116, 508)
  habitant('Cradopaud_Pecheur', 'croagunk', Gender.Male, 186, 1496)
  habitant('Roserade_Fleuriste', 'roserade', Gender.Female, 748, 1112)
  habitant('Magneton_Garde', 'magneton', Gender.Genderless, 772, 2052)
  habitant('Babimanta_Enfant', 'mantyke', Gender.Female, 1112, 1668)
  habitant('Goinfrex_Voyageur', 'munchlax', Gender.Male, 1012, 1404)
  -- Luxio et Luxray partagent un vrai dialogue, mais la carte les place à
  -- 136 px l'un de l'autre, de part et d'autre de la maison citrouille sud.
  -- Luxray est donc posé juste à l'est de Luxio, sur l'herbe libre au nord
  -- de la maison ; ils peuvent enfin se faire face sans se déplacer.
  local luxio, luxray = CH('NewObject_10'), CH('NewObject_9')
  if luxio ~= nil and luxray ~= nil then
    GROUND:TeleportTo(luxray, luxio.Position.X + 24, luxio.Position.Y,
      Direction.Left)
    GROUND:EntTurn(luxio, Direction.Right)
  end
  placer_marchands_aux_comptoirs()
  positions_habitants = {}
  for _, nom in ipairs(habitants_vivants) do
    local acteur = CH(nom)
    if acteur ~= nil then
      positions_habitants[nom] = {
        x = acteur.Position.X, y = acteur.Position.Y, dir = acteur.Direction,
      }
      local nom_affiche = noms_habitants[nom]
      if nom_affiche ~= nil and acteur.Data ~= nil then acteur.Data.Nickname = nom_affiche end
      if est_fixe(nom) then figer_habitant(nom, acteur) end
    end
  end
  vie_ville_activee = false
  partenaire_pour(CH('PLAYER'))
  -- Ombres de nuages sur toute la ville : même statut natif que la ville de base PMDO.
  GROUND:AddMapStatus('clouds_overhead')
end

local function parler(personnage, emotion, texte, placement)
  if personnage == nil then return end
  cinematique.Dire(personnage, emotion, texte, placement or 'standard')
end

-- Le héros ne parle pas pendant la visite : le partenaire lit ses gestes.
-- Les rotations restent à la vitesse 4 des cinématiques Destiny, et un
-- geste adressé au partenaire se termine en le regardant.
local function geste_heros(hero, geste, partenaire)
  if hero == nil then return end
  UI:ResetSpeaker()
  local function vers_partenaire()
    if partenaire ~= nil then
      GROUND:CharTurnToCharAnimated(hero, partenaire, 4)
    else
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    end
  end
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    vers_partenaire()
    GAME:WaitFrames(28)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(10)
    vers_partenaire()
    GAME:WaitFrames(12)
  else -- oui : regard vers le partenaire, deux inclinaisons, puis retour.
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
    GAME:WaitFrames(16)
  end
end

local function se_faire_face_ville(a, b)
  cinematique.RegarderGroupe({
    {a, b, 0, 4},
    {b, a, 5, 4},
  })
  cinematique.Respirer(10)
end

local function regarder_lieu_ville(hero, partenaire, direction)
  cinematique.TournerGroupe({
    {partenaire, direction, 0, 4},
    {hero, direction, 5, 4},
  })
end

local function activer_vie_ville()
  if vie_ville_activee then return end
  vie_ville_activee = true
  for _, nom in ipairs(habitants_vivants) do
    local acteur, depart = CH(nom), positions_habitants[nom]
    if acteur ~= nil and depart ~= nil then
      if est_fixe(nom) then
        -- Marchands à leur comptoir et duos en discussion : aucune zone de
        -- marche, IA coupée, idle par défaut et orientation de repos.
        figer_habitant(nom, acteur)
      else
        local rayon = 56
        local cx, cy = depart.x, depart.y
        -- Chaque jour, quelques flâneurs changent de quartier de déambulation.
        local vagabonds = {
          Pijako_Livreur = {{0, 0}, {72, 0}, {-72, 0}},
          Cradopaud_Pecheur = {{0, 0}, {0, 72}, {0, -72}},
          Goinfrex_Voyageur = {{0, 0}, {72, 0}, {-72, 0}},
        }
        local decalages = vagabonds[nom]
        if decalages ~= nil then
          local d = decalages[(jour_actuel() % #decalages) + 1]
          cx, cy = cx + d[1], cy + d[2]
        end
        COMMON.CreateWalkArea(nom,
          math.max(0, cx - rayon), math.max(0, cy - rayon),
          rayon * 2, rayon * 2)
        AI:EnableCharacterAI(acteur)
      end
    end
  end
end

local function retour_au_joueur(hero, partenaire)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:MoveCamera(0, 0, 45, true)
  activer_vie_ville()
  if hero ~= nil and partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
end

function ville.Visite()
  local hero = CH('PLAYER')
  local partenaire = partenaire_pour(hero)
  if hero == nil or partenaire == nil then
    -- Ne pas marquer la visite comme terminée si l'équipe est incomplète.
    GAME:FadeIn(20)
    print('[Destiny] Visite de la ville suspendue : partenaire absent de l’équipe.')
    return
  end
  local kecleon, kangourex = CH('Kecleon'), CH('Kangourex')
  local function parler_guide(emotion, texte)
    cinematique.Dire(partenaire, emotion, texte, 'droite')
  end
  GAME:CutsceneMode(true)
  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  GROUND:TeleportTo(hero, ENTREE_X - 8, ENTREE_Y, Direction.Up)
  GROUND:TeleportTo(partenaire, ENTREE_X + 12, ENTREE_Y - 20, Direction.Up)
  GAME:MoveCamera(ENTREE_X, ENTREE_Y - 30, 1, false)
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(45)

  se_faire_face_ville(partenaire, hero)
  parler_guide('Happy', 'Nous y voilà ! Bienvenue à [color=#F5D27A]Réverie Town[color].')
  parler_guide('Normal', 'Le jour se lève. Reste avec moi : je vais te montrer les endroits importants.')
  geste_heros(hero, 'oui', partenaire)
  parler_guide('Happy', 'Après cette nuit, tu n’arrives pas ici tout seul. On avance ensemble.')

  -- Le partenaire guide le héros vers la place, tous deux à pied ; la caméra
  -- les accompagne plutôt que de téléporter les personnages au milieu du plan.
  local avance_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, PLACE_X + 12, PLACE_Y - 8, false, 1.5)
  end)
  local avance_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(12)
    GROUND:MoveToPosition(hero, PLACE_X - 8, PLACE_Y + 12, false, 1.5)
  end)
  local suivi = TASK:BranchCoroutine(function() GAME:MoveCamera(PLACE_X, PLACE_Y + 20, 100, false) end)
  TASK:JoinCoroutines({avance_partenaire, avance_hero, suivi})
  regarder_lieu_ville(hero, partenaire, Direction.Up)
  parler_guide('Happy', 'Voici la place. Les chemins, les ponts et les boutiques se rejoignent ici.')

  regarder_lieu_ville(hero, partenaire, Direction.UpLeft)
  GAME:MoveCamera(616, 925, 90, false)
  parler_guide('Normal', 'Là-bas, c’est la boutique de ' .. cinematique.NomEspece('kecleon', 'Kecleon') .. '. On peut y acheter des provisions pour les expéditions.')
  if kecleon ~= nil then
    GROUND:CharAnimateTurnTo(kecleon, Direction.Down, 4)
    parler(kecleon, 'Happy', 'Bienvenue ! Une pomme ou une baie peut toujours être utile en chemin.')
  end
  geste_heros(hero, 'oui', partenaire)
  parler_guide('Happy', 'C’est ça : on vérifiera notre sac avant chaque départ.')

  regarder_lieu_ville(hero, partenaire, Direction.UpRight)
  GAME:MoveCamera(936, 940, 100, false)
  parler_guide('Normal', 'Et voici ' .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. '. Elle garde les objets que nous préférons laisser en sécurité.')
  if kangourex ~= nil then
    GROUND:CharAnimateTurnTo(kangourex, Direction.Down, 4)
    parler(kangourex, 'Happy', 'Confiez-moi vos affaires et revenez les chercher quand vous voudrez.')
  end
  geste_heros(hero, 'question', partenaire)
  parler_guide('Normal', 'Exactement : ce que nous laissons à tatie ' .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. ' n’a pas à traverser le donjon avec nous.')

  regarder_lieu_ville(hero, partenaire, Direction.UpRight)
  GAME:MoveCamera(1100, 950, 75, false)
  parler_guide('Happy', 'Juste à côté, il y a aussi cet étal aux couleurs vives. Le quartier du marché est plein de surprises !')
  regarder_lieu_ville(hero, partenaire, Direction.UpLeft)
  GAME:MoveCamera(500, 1010, 110, false)
  parler_guide('Normal', 'Et de l’autre côté de la place, d’autres comptoirs nous attendent. Nous aurons le temps de les découvrir ensemble.')
  regarder_lieu_ville(hero, partenaire, Direction.DownLeft)
  GAME:MoveCamera(530, 2350, 200, false)
  parler_guide('Happy', 'Plus au sud, les chemins passent devant les maisons. C’est un coin tranquille, entouré d’arbres.')
  regarder_lieu_ville(hero, partenaire, Direction.Up)
  GAME:MoveCamera(800, 530, 240, false)
  parler_guide('Normal', 'Regarde les ponts et les cascades : ils relient les différents quartiers de la ville.')
  regarder_lieu_ville(hero, partenaire, Direction.UpRight)
  GAME:MoveCamera(1425, 320, 135, false)
  parler_guide('Happy', 'Et ce grand bâtiment, là-haut… un jour, nous irons voir ce qui nous attend de ce côté !')
  GAME:MoveCamera(PLACE_X, PLACE_Y, 135, false)
  geste_heros(hero, 'autour', partenaire)
  se_faire_face_ville(partenaire, hero)
  parler_guide('Normal', 'Tu ne te souviens toujours pas de ton passé, mais tu commences à trouver tes repères. Ça se voit.')
  parler_guide('Happy', 'Tu n’as pas besoin de tout retenir d’un coup. On explorera la ville et les alentours à notre rythme.')
  parler_guide('Normal', 'Pour l’instant, reposons-nous. Notre prochaine aventure commencera quand nous serons prêts.')

  SV.Destiny.VisiteVille = 'terminee'
  UI:ResetSpeaker()
  retour_au_joueur(hero, partenaire)
end

local function entrer()
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.VisiteVille == 'en_route' then
    ville.Visite()
    return
  end
  local hero = CH('PLAYER')
  if hero ~= nil and hero.Position.X == 0 and hero.Position.Y == 0 then
    -- Le ground natif ne contient pas de marqueur d'entrée.
    GROUND:TeleportTo(hero, PLACE_X, PLACE_Y, Direction.Up)
  end
  local partenaire = partenaire_pour(hero)
  if SV.Destiny.ArriveeVille == 'cafe' or SV.Destiny.ArriveeVille == 'batiment' then
    -- Retour d'un intérieur : réapparaître devant la façade utilisée.
    local arrivee_x, arrivee_y = 1188, 1652
    if SV.Destiny.ArriveeVille == 'batiment' then
      arrivee_x = SV.Destiny.RetourBatimentX or PLACE_X
      arrivee_y = SV.Destiny.RetourBatimentY or PLACE_Y
    end
    SV.Destiny.ArriveeVille = nil
    if hero ~= nil then GROUND:TeleportTo(hero, arrivee_x, arrivee_y, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, arrivee_x - 28, arrivee_y, Direction.Down) end
  end
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(20)
  retour_au_joueur(hero, partenaire)
end

function ville.Enter(map) entrer() end
function ville.GameLoad(map) installer_portes(map) installer_comptoirs(map) placer_marchands_aux_comptoirs() entrer() end
function ville.Exit(map) end
function ville.Update(map, time) tic_ambiance() end


-- Ambiance vivante (non bloquante) : les marchands s'animent comme dans la
-- ville de base PMDO (émotes périodiques) et des paires d'habitants
-- discutent entre eux par émotes, en se tournant l'un vers l'autre.
-- Les paires et les gestes tournent avec le temps… et avec le jour courant.
local horloge_ambiance = 0
local function geste_ambiance(nom, emote)
  local acteur = CH(nom)
  if acteur == nil then return end
  pcall(function()
    if acteur.IsInteracting then return end
    GROUND:CharSetEmote(acteur, emote, 1)
  end)
end
local function discussion_ambiance(cycle)
  local paire = paires_discussion[((cycle + jour_actuel()) % #paires_discussion) + 1]
  local a1, a2 = CH(paire[1]), CH(paire[2])
  if a1 == nil or a2 == nil then return end
  -- Ne jamais détourner du joueur un PNJ déjà en interaction.
  if a1.IsInteracting or a2.IsInteracting then return end
  orienter_discussion(paire[1])
  if cycle % 2 == 0 then
    geste_ambiance(paire[1], 'question')
    geste_ambiance(paire[2], 'happy')
  else
    geste_ambiance(paire[1], 'happy')
    geste_ambiance(paire[2], 'glowing')
  end
end
local function tic_ambiance()
  if not vie_ville_activee then return end
  horloge_ambiance = horloge_ambiance + 1
  if horloge_ambiance % 540 == 0 then
    local cycle = math.floor(horloge_ambiance / 540) % 6
    if cycle == 0 then
      geste_ambiance('Kecleon', 'happy')
      geste_ambiance('Kecleon_Violet', 'glowing')
    elseif cycle == 1 then geste_ambiance('Kangourex', 'happy')
    elseif cycle == 2 then geste_ambiance('NewObject_24', 'exclaim')
    elseif cycle == 3 then geste_ambiance('NewObject_4', 'glowing')
    elseif cycle == 4 then geste_ambiance('NewObject_3', 'glowing')
    else geste_ambiance('Kecleon_Violet', 'exclaim') end
  end
  if horloge_ambiance % 900 == 0 then
    discussion_ambiance(math.floor(horloge_ambiance / 900))
  end
end

function ville.PorteCafeSpinda_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue('[color=#FF9E5E]Café Spinda[color]\nUne douce odeur de baies s’échappe de la porte.')
  UI:ChoiceMenuYesNo('Entrer au café Spinda ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    GAME:FadeOut(false, 20)
    GAME:EnterZone('town02_waterfallvillage', -1, 2, 0)
  end
end

for _, porte_def in ipairs(portes_batiments) do
  local porte = porte_def
  ville[porte.nom .. '_Action'] = function(obj, activator)
    UI:ResetSpeaker()
    UI:ChoiceMenuYesNo('Entrer : ' .. porte.titre .. ' ?', true)
    UI:WaitForChoice()
    if UI:ChoiceResult() then
      SV.Destiny = SV.Destiny or {}
      SV.Destiny.RetourBatimentX = porte.retour_x
      SV.Destiny.RetourBatimentY = porte.retour_y
      GAME:FadeOut(false, 20)
      GAME:EnterGroundMap('town02_waterfallvillage', porte.interieur, porte.marqueur)
    end
  end
end

-- Interagir devant un comptoir revient à s’adresser au marchand posté
-- derrière : même dialogue et même service que l’Action du personnage.
for _, comptoir_def in ipairs(comptoirs) do
  local comptoir = comptoir_def
  ville[comptoir.nom .. '_Action'] = function(obj, activator)
    local marchand = CH(comptoir.marchand)
    local action = ville[comptoir.marchand .. '_Action']
    if marchand ~= nil and action ~= nil then action(marchand, activator) end
  end
end

-- Les habitants sont visibles pendant la visite et restent utilisables après.
-- Kangourex ne garde que les objets : dépôt et retrait, jamais l'argent.
-- La banque est assurée par Gimmighoul (NewObject_3), plus bas.
function ville.Kangourex_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Bienvenue, mes petits. Je garde vos objets bien au sec, loin des donjons.')
  while true do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion('Normal')
    UI:BeginChoiceMenu('Souhaitez-vous déposer ou retirer des objets ?', {
      'Déposer des objets', 'Retirer des objets', 'Quitter',
    }, 1, 3)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 1 then
      UI:ResetSpeaker()
      UI:StorageMenu()
      UI:WaitForChoice()
    elseif choix == 2 then
      UI:ResetSpeaker()
      UI:WithdrawMenu()
      UI:WaitForChoice()
    else
      break
    end
  end
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Vos affaires vous attendront ici. Revenez quand vous voulez.')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'Kangourex')
end

-- Petits assortiments de départ : menus, argent et sac sont ceux de PMDO.
-- Les deux frères Kecleon ne proposent pas les mêmes marchandises.
local assortiments_kecleon_vert = {
  {{id = 'food_apple', prix = 50}, {id = 'berry_oran', prix = 80}, {id = 'berry_leppa', prix = 80}},
  {{id = 'food_apple_big', prix = 100}, {id = 'berry_pecha', prix = 80}, {id = 'berry_chesto', prix = 80}},
  {{id = 'food_banana', prix = 100}, {id = 'berry_lum', prix = 150}, {id = 'berry_persim', prix = 80}},
}
local assortiments_kecleon_violet = {
  {{id = 'berry_sitrus', prix = 150}, {id = 'medicine_elixir', prix = 300}, {id = 'seed_reviver', prix = 800}},
  {{id = 'medicine_max_elixir', prix = 650}, {id = 'orb_escape', prix = 300}, {id = 'seed_joy', prix = 1200}},
  {{id = 'medicine_max_potion', prix = 500}, {id = 'orb_scanner', prix = 300}, {id = 'seed_pure', prix = 400}},
}

-- Stock du jour, persisté dans la sauvegarde : les achats épuisent l'étal,
-- et la sieste au café Spinda fait passer à l'assortiment suivant.
local function stock_kecleon(cle, assortiments, decalage)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.StocksKecleon = SV.Destiny.StocksKecleon or {}
  local jour = SV.Destiny.JourneeVille or 0
  local stock = SV.Destiny.StocksKecleon[cle]
  if stock == nil or stock.Jour ~= jour then
    stock = {Jour = jour, Articles = {}}
    local assortiment = assortiments[((jour + decalage) % #assortiments) + 1]
    for _, article in ipairs(assortiment) do
      table.insert(stock.Articles, {Index = article.id, Amount = 1, Price = article.prix})
    end
    SV.Destiny.StocksKecleon[cle] = stock
  end
  return stock
end

local function ouvrir_boutique(personnage, cle, assortiments, decalage, accueil)
  local stock = stock_kecleon(cle, assortiments, decalage)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue(accueil)
  UI:WaitShowDialogue('Mon assortiment change chaque jour. Après une sieste au café Spinda, revenez voir le nouvel étal !')
  while true do
    UI:SetSpeaker(personnage)
    if #stock.Articles == 0 then
      UI:WaitShowDialogue('Mon étal du jour est épuisé. Revenez demain !')
      break
    end
    local catalogue = {}
    for _, article in ipairs(stock.Articles) do
      table.insert(catalogue, {
        Item = RogueEssence.Dungeon.InvItem(article.Index, false, article.Amount),
        Price = article.Price,
      })
    end
    UI:ShopMenu(catalogue)
    UI:WaitForChoice()
    local panier = UI:ChoiceResult()
    if panier == nil or #panier == 0 then break end
    UI:SetSpeaker(personnage)
    if GAME:GetPlayerBagCount() >= GAME:GetPlayerBagLimit() then
      UI:WaitShowDialogue('Votre sac est plein. Faites un peu de place avant de revenir.')
    else
      local total = 0
      for ii = 1, #panier do total = total + catalogue[panier[ii]].Price end
      if total > GAME:GetPlayerMoney() then
        UI:WaitShowDialogue('Il vous manque un peu d’argent pour tout cela.')
      else
        UI:ChoiceMenuYesNo('Acheter pour ' .. total .. ' Poké ?', false)
        UI:WaitForChoice()
        if UI:ChoiceResult() then
          GAME:RemoveFromPlayerMoney(total)
          for ii = 1, #panier do
            local objet = catalogue[panier[ii]].Item
            GAME:GivePlayerItem(objet.ID, objet.Amount, false)
          end
          for ii = #panier, 1, -1 do table.remove(stock.Articles, panier[ii]) end
          SOUND:PlayBattleSE('DUN_Money')
          UI:SetSpeaker(personnage)
          UI:WaitShowDialogue('Merci ! Prenez soin de vous sur les chemins.')
        end
      end
    end
  end
  UI:ResetSpeaker()
end

function ville.Kecleon_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  ouvrir_boutique(personnage, 'vert', assortiments_kecleon_vert, 0,
    'Bienvenue à la boutique Kecleon ! Des provisions simples, mais qui ont sauvé plus d’une expédition.')
  terminer_dialogue(personnage, 'Kecleon')
end

function ville.Kecleon_Violet_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  ouvrir_boutique(personnage, 'violet', assortiments_kecleon_violet, 1,
    'Mon étal violet garde les articles précieux. Ils coûtent plus cher, mais ils peuvent changer une traversée.')
  terminer_dialogue(personnage, 'Kecleon_Violet')
end

-- Banque de Réverie Town : Mordudor sert les clients à son comptoir.
function ville.NewObject_3_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Des pièces, des pièces ! Je peux garder votre argent dans mon coffre et vous le rendre au Poké près.')
  UI:ResetSpeaker()
  UI:BankMenu()
  UI:WaitForChoice()
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Votre trésor est compté. ' .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. ' garde les objets ; moi, je veille sur les Poké.')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_3')
end

local function dialogue_simple(personnage, repliques)
  for _, replique in ipairs(repliques) do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion(replique[1])
    UI:WaitShowDialogue(replique[2])
  end
  UI:ResetSpeaker()
end

local function conversation(acteurs, repliques)
  for _, replique in ipairs(repliques) do
    local acteur = acteurs[replique[1]]
    if acteur ~= nil then
      UI:SetSpeaker(acteur)
      UI:SetSpeakerEmotion(replique[2])
      UI:WaitShowDialogue(replique[3])
    end
  end
  UI:ResetSpeaker()
end

-- Alakazam : réapprendre une capacité oubliée (250 Poké) ou en oublier une
-- (gratuit), avec les menus natifs utilisés par le tuteur de PMDO.
local function alakazam_se_souvenir(personnage)
  local prix = 250
  if GAME:GetPlayerMoney() < prix then
    UI:SetSpeaker(personnage)
    UI:WaitShowDialogue('Il vous faut ' .. prix .. ' Poké pour éveiller un souvenir. Revenez quand votre bourse sera prête, elle aussi.')
    return
  end
  local etat, membre, capacite = 0, nil, ''
  while etat > -1 do
    if etat == 0 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Qui doit se souvenir d’une capacité ?')
      local choisi = AssemblySelectMenu.run(function(m) return GAME:CanRelearn(m) end, false)
      if choisi ~= nil then membre, etat = choisi, 1 else etat = -1 end
    elseif etat == 1 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Quelle capacité ' .. membre:GetDisplayName(true) .. ' doit-il retrouver ?')
      local resultat = SkillSelectMenu.runRelearnMenu(membre)
      if resultat ~= '' then capacite, etat = resultat, 2 else etat = 0 end
    else
      local entree = _DATA:GetSkill(capacite)
      local appris = COMMON.LearnMoveFlow(membre, capacite,
        membre:GetDisplayName(true) .. ' doit oublier une capacité pour retrouver celle-ci.')
      if appris then
        SOUND:PlayBattleSE('DUN_Money')
        GAME:RemoveFromPlayerMoney(prix)
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Concentrez-vous… laissez le geste remonter, comme un rêve que l’on rattrape au réveil.')
        SOUND:PlayFanfare('Fanfare/LearnSkill')
        UI:WaitShowDialogue(membre:GetDisplayName(true) .. ' se souvient de ' .. entree:GetIconName() .. ' !')
        etat = -1
      else
        etat = 1
      end
    end
  end
end

local function alakazam_oublier(personnage)
  local etat, membre = 0, nil
  while etat > -1 do
    if etat == 0 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Qui doit oublier une capacité ?')
      local choisi = AssemblySelectMenu.run(function(m) return GAME:CanForget(m) end, false)
      if choisi ~= nil then
        membre, etat = choisi, 1
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Quelle capacité ' .. membre:GetDisplayName(true) .. ' doit-il laisser partir ?')
      else
        etat = -1
      end
    else
      UI:ForgetMenu(membre)
      UI:WaitForChoice()
      local resultat = UI:ChoiceResult()
      if resultat > -1 then
        local capacite = GAME:GetCharacterSkill(membre, resultat)
        local entree = _DATA:GetSkill(capacite)
        GAME:ForgetSkill(membre, resultat)
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Voilà… un geste s’efface, et l’esprit respire.')
        SOUND:PlayFanfare('Fanfare/LearnSkill')
        UI:WaitShowDialogue(membre:GetDisplayName(true) .. ' a oublié ' .. entree:GetIconName() .. '.')
        etat = -1
      else
        etat = 0
      end
    end
  end
end

function ville.NewObject_4_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_simple(personnage, {
    {'Normal', 'Une capacité oubliée n’est pas effacée : elle dort dans la mémoire du corps, en attendant un déclic.'},
  })
  UI:SetSpeaker(personnage)
  UI:BeginChoiceMenu('Puis-je vous aider ? Se souvenir coûte 250 Poké ; oublier est gratuit.', {
    'Se souvenir (250 Poké)', 'Oublier une capacité', 'Quitter',
  }, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == 1 then alakazam_se_souvenir(personnage)
  elseif choix == 2 then alakazam_oublier(personnage) end
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_4')
end

-- Tinkaton : ouvrir les boîtes au trésor (150 Poké par boîte), avec le menu
-- natif d'expertise de PMDO.
function ville.NewObject_24_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  local prix = 150
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Une boîte récalcitrante ? Rien ne résiste longtemps à mon marteau… ni à un peu de patience.')
  while true do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion('Normal')
    UI:BeginChoiceMenu('J’ouvre vos boîtes pour ' .. prix .. ' Poké pièce. Que faire ?', {
      'Ouvrir des boîtes', 'Explications', 'Quitter',
    }, 1, 3)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 3 then
      break
    elseif choix == 2 then
      UI:WaitShowDialogue('Les explorateurs rapportent des boîtes scellées des donjons. Personne ne sait ce qu’elles contiennent avant ouverture.')
      UI:WaitShowDialogue('Choisissez vos boîtes, je m’occupe de la serrure. Le contenu vous revient, bien entendu.')
    else
      if GAME:GetPlayerBagCount() + GAME:GetPlayerEquippedCount() == 0 then
        UI:WaitShowDialogue('Votre sac est vide. Rapportez-moi une boîte d’un donjon, et nous verrons ce qu’elle cache.')
      else
        UI:WaitShowDialogue('Montrez-moi les boîtes à ouvrir.')
        UI:AppraiseMenu()
        UI:WaitForChoice()
        local panier = UI:ChoiceResult()
        if panier ~= nil and #panier > 0 then
          local total = #panier * prix
          if total > GAME:GetPlayerMoney() then
            UI:SetSpeaker(personnage)
            UI:WaitShowDialogue('Il vous manque des Poké pour ouvrir tout cela. Choisissez moins de boîtes, ou revenez plus riche.')
          else
            UI:SetSpeaker(personnage)
            UI:ChoiceMenuYesNo('Ouvrir ' .. #panier .. ' boîte(s) pour ' .. total .. ' Poké ?', false)
            UI:WaitForChoice()
            if UI:ChoiceResult() then
              local tresor = {}
              for ii = #panier, 1, -1 do
                local boite
                if panier[ii].IsEquipped then
                  boite = GAME:GetPlayerEquippedItem(panier[ii].Slot)
                  GAME:TakePlayerEquippedItem(panier[ii].Slot, true)
                else
                  boite = GAME:GetPlayerBagItem(panier[ii].Slot)
                  GAME:TakePlayerBagItem(panier[ii].Slot, true)
                end
                local objet_cache = boite.HiddenValue
                local entree = _DATA:GetItem(objet_cache)
                table.insert(tresor, {
                  Box = boite,
                  Item = RogueEssence.Dungeon.InvItem(objet_cache, false, entree.MaxStack),
                })
                if entree.Rarity > 0 and SV.unlocked_trades ~= nil then
                  SV.unlocked_trades[objet_cache] = true
                end
              end
              SOUND:PlayBattleSE('DUN_Money')
              GAME:RemoveFromPlayerMoney(total)
              UI:SetSpeaker(personnage)
              UI:SetSpeakerEmotion('Happy')
              UI:WaitShowDialogue('Reculez un peu… et voilà le travail !')
              SOUND:PlayFanfare('Fanfare/Treasure')
              UI:SpoilsMenu(tresor)
              UI:WaitForChoice()
              for ii = 1, #tresor do
                local objet = tresor[ii].Item
                GAME:GivePlayerItem(objet.ID, objet.Amount, false, objet.HiddenValue)
              end
            end
          end
        end
      end
    end
  end
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Chaque coffre a son secret. Revenez m’en montrer d’autres !')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_24')
end

local dialogues_lombre_ludicolo = {
  {
    {1, 'Normal', 'La cascade chante plus fort ce matin. Les ponts vont encore être glissants.'},
    {2, 'Happy', 'Alors dansons lentement en les traversant. Réverie Town récompense ceux qui gardent le rythme.'},
    {1, 'Happy', 'Facile à dire pour toi ! Mais je suivrai tes pas, comme toujours.'},
  },
  {
    {1, 'Normal', 'Les filaments de la rivière glissent tout seuls aujourd’hui. On dirait qu’elle respire.'},
    {2, 'Happy', 'Elle danse, mon ami ! Et quand la rivière danse, les poissons suivent la mesure.'},
    {1, 'Happy', 'Alors je lancerai ma ligne en rythme. Une-deux, une-deux…'},
  },
  {
    {1, 'Worried', 'Le marché était bondé ce matin. J’ai failli perdre une feuille dans la foule.'},
    {2, 'Happy', 'C’est la preuve que la ville vit ! Demain, nous irons tôt, avant les équipes.'},
    {1, 'Normal', 'D’accord. Mais c’est toi qui porteras les baies, cette fois.'},
  },
}
local function dialogue_lombre_ludicolo(premier, second)
  conversation({premier, second}, repliques_du_jour(dialogues_lombre_ludicolo))
end
function ville.NewObject_7_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lombre_ludicolo(personnage, CH('NewObject_8'))
  terminer_dialogue(personnage, 'NewObject_7')
end
function ville.NewObject_8_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lombre_ludicolo(personnage, CH('NewObject_7'))
  terminer_dialogue(personnage, 'NewObject_8')
end

local dialogues_lux = {
  {
    {1, 'Worried', 'Dis… les Bois Perdus font vraiment aussi peur qu’on le raconte ?'},
    {2, 'Normal', 'Il demande du respect, pas de la peur. On y entre préparé, et jamais en se croyant invincible.'},
    {1, 'Happy', 'Alors je m’entraînerai encore. Un jour, je traverserai à tes côtés.'},
  },
  {
    {1, 'Happy', 'J’ai couru jusqu’au pont de l’est sans m’arrêter ! Tu as vu ?'},
    {2, 'Happy', 'Je regardais, oui. Encore un peu de souffle, et tu tiendras une vraie patrouille.'},
    {1, 'Normal', 'Demain, je vise la place et retour. Chronomètre-moi !'},
  },
  {
    {1, 'Worried', 'Et si une équipe se perd, un jour ? Qui ira la chercher ?'},
    {2, 'Normal', 'Ceux qui connaissent les chemins… et qui ont appris à revenir. C’est pour cela qu’on s’entraîne.'},
    {1, 'Happy', 'Alors un jour, ce sera nous. Promis ?'},
    {2, 'Happy', 'Promis, petit frère.'},
  },
}
local function dialogue_lux(second, premier)
  conversation({second, premier}, repliques_du_jour(dialogues_lux))
end
function ville.NewObject_9_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lux(CH('NewObject_10'), personnage)
  terminer_dialogue(personnage, 'NewObject_9')
end
function ville.NewObject_10_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lux(personnage, CH('NewObject_9'))
  terminer_dialogue(personnage, 'NewObject_10')
end

local dialogues_habitants = {
  NewObject_6 = {
    {{'Happy', 'De là-haut, on voit les toits, les chutes et même un morceau de la falaise. Réverie Town tient dans un battement d’ailes.'}},
    {{'Happy', 'Ce matin, le vent porte jusqu’à la forêt d’ambre. Parfait pour les ailes… et pour les nouvelles.'}},
    {{'Normal', 'Les courants chauds tournent au-dessus de la rivière. Quand ils glissent vers l’est, le beau temps suit toujours.'}},
  },
  NewObject_12 = {
    {{'Normal', 'Je porte les caisses du marché le matin. L’après-midi, je laisse mes bras raconter qu’ils ont bien travaillé.'}},
    {{'Worried', 'Deux livraisons pour les ' .. cinematique.NomEspece('kecleon', 'Kecleon') .. ', une pour la forge… Mes quatre bras ont leur propre emploi du temps, aujourd’hui.'}},
    {{'Happy', 'Une caisse bien portée ne casse jamais. C’est ma devise. Bon, sauf celle de la semaine dernière. Une seule !'}},
  },
  NewObject_13 = {
    {{'Happy', 'J’adore suivre les reflets sur l’eau. Quand une équipe revient de mission, toute la place semble briller.'}},
    {{'Happy', 'Les filets bleu foncé de la rivière voyagent le long des berges. Je les suis du regard jusqu’au pont !'}},
    {{'Normal', 'Aujourd’hui, je compte les équipes qui partent. Demain, je compterai celles qui reviennent. C’est mon rituel.'}},
  },
  NewObject_14 = {
    {{'Normal', 'Les explorateurs pressés oublient souvent de vérifier leur sac. ' .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. ' et les ' .. cinematique.NomEspece('kecleon', 'Kecleon') .. ' existent pour une raison.'}},
    {{'Normal', 'Un sac vérifié le matin vaut deux jambes reposées. Notez-le quelque part, ça vous servira en donjon.'}},
    {{'Worried', 'On prévoit du vent sur les hauteurs. Les équipes sages attendront demain, les autres… apprendront vite.'}},
  },
  Doyen = {
    {{'Normal', 'Je connais chaque courant qui passe au-dessus des cascades. La ville change, mais le vent se souvient.'}},
    {{'Normal', 'Chaque jour, la rivière déplace ses filaments d’un souffle. Rien ne reste, tout continue. Méditez-y.'}},
    {{'Happy', 'Les jeunes Baudrive me demandent des histoires. Je leur raconte la ville… un quartier par jour.'}},
  },
  Drifloon = {
    {{'Happy', 'Le vent m’emmène d’un quartier à l’autre. Aujourd’hui, il a décidé de rester près du Doyen.'}},
    {{'Happy', 'Aujourd’hui, le vent sent les baies du marché. Demain, il sentira peut-être la pluie. Moi, je suivrai !'}},
    {{'Worried', 'Le Doyen dit que le vent se souvient de tout. Alors je lui confie mes secrets… il les garde là-haut.'}},
  },
  NewObject_16 = {
    {{'Normal', 'Je surveille les chemins qui montent vers les hauteurs. Un ciel dégagé annonce souvent une bonne journée d’expédition.'}},
    {{'Normal', 'Ronde du matin terminée : ponts dégagés, sentiers secs. Les équipes peuvent partir tranquilles.'}},
    {{'Worried', 'Des nuages s’accrochent à la falaise. Si vous montez aujourd’hui, restez sur les chemins balisés.'}},
  },
  NewObject_11 = {
    {{'Normal', 'Mon équipe se repose. Savoir s’arrêter à Réverie Town fait aussi partie du métier d’explorateur.'}},
    {{'Happy', 'Hier, les grottes ; aujourd’hui, la place et un vrai repas. Demain ? On verra ce que dit le tableau des missions.'}},
    {{'Normal', 'Je révise nos cartes au bord de l’eau. Le courant m’aide à réfléchir, allez savoir pourquoi.'}},
  },
  NewObject_18 = {
    {{'Normal', 'Zzz… prévenez-moi quand le café Spinda servira le goûter… Zzz…'}},
    {{'Normal', 'Zzz… encore cinq minutes… ou cinq siestes… Zzz…'}},
    {{'Happy', 'Hmm ? On a parlé de goûter ? Non ? Alors je rendors… Zzz…'}},
  },
  NewObject_20 = {
    {{'Normal', 'Les jeunes équipes regardent toujours l’horizon. C’est bon signe : la ville a besoin de rêves neufs.'}},
    {{'Normal', 'De mon temps, on partait avec une carte griffonnée sur une écorce. Vous avez bien de la chance, aujourd’hui.'}},
    {{'Happy', 'Je vois passer les équipes chaque jour. Chacune repart un peu plus grande qu’à l’arrivée. Ça me suffit.'}},
  },
  NewObject_21 = {
    {{'Happy', 'Le parfum des baies du marché me donne des idées de desserts pour tout le quartier !'}},
    {{'Happy', 'Aujourd’hui : tarte aux Baies Pecha. Demain… tarte aux Baies Pecha aussi. On ne change pas un succès !'}},
    {{'Worried', 'Mes réserves de baies fondent plus vite que prévu. Quelqu’un ici fait des réserves dans MON garde-manger ?'}},
  },
  NewObject_15 = {
    {{'Happy', 'Un bon lait chaud après une mission, et les pattes tremblent déjà moins.'}},
    {{'Happy', 'Le lait du matin est le meilleur, parole d’Écrémeuh. Passez avant les expéditions, il part vite !'}},
    {{'Normal', 'Charmilly veut ma crème pour ses décorations. Entre voisines, on s’arrange toujours.'}},
  },
  NewObject_17 = {
    {{'Normal', 'Je fais ma ronde entre les ponts. Si vous cherchez la place, suivez le bruit des boutiques.'}},
    {{'Normal', 'Ronde du jour : ponts, place, berges. La rivière glisse vite aujourd’hui, surveillez vos pas près des quais.'}},
    {{'Happy', 'Les petits m’utilisent comme point de repère. « Au troisième Arcanin, tournez à gauche », disent-ils. Il n’y en a qu’un…'}},
  },
  NewObject_22 = {
    {{'Normal', 'On dit que les ombres des Bois Perdus se déplacent. Moi, je dis surtout de garder une Baie Lum à portée de patte.'}},
    {{'Normal', 'Près de ma grotte, l’air change selon les jours. Quand il sent la mousse froide, les Bois Perdus s’agitent. Restez prudents.'}},
    {{'Worried', 'Les filaments de la rivière fuient vers le sud, comme s’ils évitaient la forêt. Intéressant… non ?'}},
  },
  NewObject_23 = {
    {{'Happy', 'Je décorerais bien la place pour le retour des équipes. Il suffit de peu pour qu’une ville sourie.'}},
    {{'Happy', 'Programme du jour : un ruban de crème sur la fontaine, deux sur le pont. Réverie mérite sa douceur quotidienne !'}},
    {{'Normal', 'Écrémeuh me garde sa meilleure crème. Demain, la place aura droit à une vraie fête des couleurs.'}},
  },
  Pijako_Livreur = {
    {{'Happy', 'Une lettre lue au bon moment peut sauver une expédition. Enfin, presque. Je livre vite, quand même !'}},
    {{'Happy', 'Tournée du jour : poste, place, café, et retour avant midi ! Le courrier de Réverie n’attend jamais.'}},
    {{'Worried', 'Le vent a failli emporter une lettre au-dessus de la chute. Failli ! Un Pijako ne perd jamais son courrier.'}},
  },
  Cradopaud_Pecheur = {
    {{'Normal', 'Les filets d’eau racontent la rivière : quand ils s’agitent, les poissons ne sont pas loin.'}},
    {{'Normal', 'Regardez les filaments descendre le courant : là où ils ralentissent, les poissons se reposent. C’est mon coin, aujourd’hui.'}},
    {{'Happy', 'Hier, trois prises avant le déjeuner. Aujourd’hui, je vise le double… ou une belle sieste. Verdict au couchant.'}},
  },
  Roserade_Fleuriste = {
    {{'Happy', 'Je tresse des guirlandes pour les maisons de la ville. Réverie mérite des fleurs fraîches chaque matin.'}},
    {{'Happy', 'Les fleurs des berges suivent les filaments de la rivière. Là où l’eau glisse douce, elles ouvrent plus tôt.'}},
    {{'Normal', 'Une guirlande par jour, une porte à la fois. Au bout d’une saison, toute la ville fleurit.'}},
  },
  Magneton_Garde = {
    {{'Normal', 'Bzz… Pont surveillé. Passage libre pour les équipes en règle. Bzz.'}},
    {{'Normal', 'Bzz… Contrôle du jour : sacs fermés, badges visibles. Merci de votre coopération. Bzz.'}},
    {{'Worried', 'Bzz… Interférences près de la cascade. Mes trois unités ne sont pas d’accord sur la cause. Bzz.'}},
  },
  Babimanta_Enfant = {
    {{'Happy', 'Quand je serai grand, je traverserai la grande chute en nageant ! Enfin… peut-être en bateau.'}},
    {{'Happy', 'Je fais la course avec les filaments de la rivière ! Ils vont vite… mais moi aussi !'}},
    {{'Worried', 'Marill dit qu’elle comptera les équipes avec moi. Moi, je compte les reflets. On s’échangera nos totaux demain.'}},
  },
  Goinfrex_Voyageur = {
    {{'Happy', 'On m’a dit que le café Spinda servait les meilleurs goûters du pays. Je vérifie. Rigoureusement.'}},
    {{'Happy', 'Jour deux de mes vérifications : le goûter du café Spinda est toujours excellent. La science avance.'}},
    {{'Normal', 'Je devais repartir ce matin… puis Cupcanaille a parlé de tarte. Je reste un jour de plus. Pour la science, toujours.'}},
  },
}
for nom, variantes in pairs(dialogues_habitants) do
  local nom_action, choix = nom, variantes
  ville[nom .. '_Action'] = function(personnage, activator)
    commencer_dialogue(personnage, activator)
    dialogue_simple(personnage, repliques_du_jour(choix))
    terminer_dialogue(personnage, nom_action)
  end
end

return ville
