-- Réverie Town : arrivée après Lost Wood et présentation des lieux existants.
-- La version town02 étendue contient ses habitants, objets et marqueurs ;
-- Kecleon et Kangourex sérialisés sont réutilisés, avec création en repli
-- uniquement si une ancienne sauvegarde/carte ne les fournit pas.
require 'origin.common'
require 'origin.menu.skill.SkillSelectMenu'
require 'origin.menu.team.AssemblySelectMenu'
local equipe_scene = require 'destiny.equipe_scene'

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
}
local positions_habitants = {}
local vie_ville_activee = false

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

-- Porte du café Spinda : la carte town02 ne sérialise aucune sortie, on
-- installe donc un objet invisible sur le tapis rouge de l'annexe café
-- (centre relevé sur le rendu de la carte : x≈1188, y≈1605).
local function installer_porte_cafe(map)
  if map == nil or map:FindObject('PorteCafeSpinda') then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteCafeSpinda'
  porte.Collider = RogueElements.Rect(1160, 1588, 56, 20)
  porte:OnMapInit()
  map:AddObject(porte)
end

function ville.Init(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  installer_porte_cafe(map)
  habitant('Kecleon', 'kecleon', Gender.Male, 616, 948)
  habitant('Kangourex', 'kangaskhan', Gender.Female, 936, 964)
  positions_habitants = {}
  for _, nom in ipairs(habitants_vivants) do
    local acteur = CH(nom)
    if acteur ~= nil then
      positions_habitants[nom] = {x = acteur.Position.X, y = acteur.Position.Y}
    end
  end
  vie_ville_activee = false
  partenaire_pour(CH('PLAYER'))
end

local function parler(personnage, emotion, texte)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion(emotion)
  UI:WaitShowDialogue(texte)
end

-- Le héros ne parle pas pendant la visite : le partenaire lit ses gestes.
local function geste_heros(hero, geste)
  if hero == nil then return end
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(28)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
    GAME:WaitFrames(22)
  else
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(9)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(10)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(16)
  end
end

local function activer_vie_ville()
  if vie_ville_activee then return end
  vie_ville_activee = true
  local comptoirs = {
    Kecleon = true, Kecleon_Violet = true, Kangourex = true,
    NewObject_3 = true, NewObject_4 = true, NewObject_24 = true,
  }
  for _, nom in ipairs(habitants_vivants) do
    local acteur, depart = CH(nom), positions_habitants[nom]
    if acteur ~= nil and depart ~= nil then
      local rayon = comptoirs[nom] and 28 or 56
      COMMON.CreateWalkArea(nom,
        math.max(0, depart.x - rayon), math.max(0, depart.y - rayon),
        rayon * 2, rayon * 2)
      AI:EnableCharacterAI(acteur)
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
  GAME:CutsceneMode(true)
  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  GROUND:TeleportTo(hero, ENTREE_X - 8, ENTREE_Y, Direction.Up)
  GROUND:TeleportTo(partenaire, ENTREE_X + 12, ENTREE_Y - 20, Direction.Up)
  GAME:MoveCamera(ENTREE_X, ENTREE_Y - 30, 1, false)
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(45)

  parler(partenaire, 'Happy', 'Nous y voilà ! Bienvenue à [color=#F5D27A]Réverie Town[color].')
  parler(partenaire, 'Normal', 'Le jour se lève. Reste avec moi : je vais te montrer les endroits importants.')
  geste_heros(hero, 'oui')
  parler(partenaire, 'Happy', 'Après cette nuit, tu n’arrives pas ici tout seul. On avance ensemble.')

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
  GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
  parler(partenaire, 'Happy', 'Voici la place. Les chemins, les ponts et les boutiques se rejoignent ici.')

  GAME:MoveCamera(616, 925, 90, false)
  parler(partenaire, 'Normal', 'Là-bas, c’est la boutique de Kecleon. On peut y acheter des provisions pour les expéditions.')
  if kecleon ~= nil then parler(kecleon, 'Happy', 'Bienvenue ! Une pomme ou une baie peut toujours être utile en chemin.') end
  geste_heros(hero, 'oui')
  parler(partenaire, 'Happy', 'C’est ça : on vérifiera notre sac avant chaque départ.')

  GAME:MoveCamera(936, 940, 100, false)
  parler(partenaire, 'Normal', 'Et voici Kangourex. Elle garde les objets que nous préférons laisser en sécurité.')
  if kangourex ~= nil then parler(kangourex, 'Happy', 'Confiez-moi vos affaires et revenez les chercher quand vous voudrez.') end
  geste_heros(hero, 'question')
  parler(partenaire, 'Normal', 'Exactement : ce que nous laissons à tatie Kangourex n’a pas à traverser le donjon avec nous.')

  GAME:MoveCamera(1100, 950, 75, false)
  parler(partenaire, 'Happy', 'Juste à côté, il y a aussi cet étal aux couleurs vives. Le quartier du marché est plein de surprises !')
  GAME:MoveCamera(500, 1010, 110, false)
  parler(partenaire, 'Normal', 'Et de l’autre côté de la place, d’autres comptoirs nous attendent. Nous aurons le temps de les découvrir ensemble.')
  GAME:MoveCamera(530, 2350, 200, false)
  parler(partenaire, 'Happy', 'Plus au sud, les chemins passent devant les maisons. C’est un coin tranquille, entouré d’arbres.')
  GAME:MoveCamera(800, 530, 240, false)
  parler(partenaire, 'Normal', 'Regarde les ponts et les cascades : ils relient les différents quartiers de la ville.')
  GAME:MoveCamera(1425, 320, 135, false)
  parler(partenaire, 'Happy', 'Et ce grand bâtiment, là-haut… un jour, nous irons voir ce qui nous attend de ce côté !')
  GAME:MoveCamera(PLACE_X, PLACE_Y, 135, false)
  geste_heros(hero, 'autour')
  parler(partenaire, 'Normal', 'Tu ne te souviens toujours pas de ton passé, mais tu commences à trouver tes repères. Ça se voit.')
  parler(partenaire, 'Happy', 'Tu n’as pas besoin de tout retenir d’un coup. On explorera la ville et les alentours à notre rythme.')
  parler(partenaire, 'Normal', 'Pour l’instant, reposons-nous. Notre prochaine aventure commencera quand nous serons prêts.')

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
  if SV.Destiny.ArriveeVille == 'cafe' then
    -- Retour du café Spinda : réapparaître devant sa porte, au sud du tapis.
    SV.Destiny.ArriveeVille = nil
    if hero ~= nil then GROUND:TeleportTo(hero, 1188, 1652, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 1160, 1652, Direction.Down) end
  end
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(20)
  retour_au_joueur(hero, partenaire)
end

function ville.Enter(map) entrer() end
function ville.GameLoad(map) installer_porte_cafe(map) entrer() end
function ville.Exit(map) end
function ville.Update(map, time) end

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

-- Les habitants sont visibles pendant la visite et restent utilisables après.
-- Kangourex ne garde que les objets : dépôt et retrait, jamais l'argent.
-- La banque est assurée par Gimmighoul (NewObject_3), plus bas.
function ville.Kangourex_Action(personnage, activator)
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
  ouvrir_boutique(personnage, 'vert', assortiments_kecleon_vert, 0,
    'Bienvenue à la boutique Kecleon ! Des provisions simples, mais qui ont sauvé plus d’une expédition.')
end

function ville.Kecleon_Violet_Action(personnage, activator)
  ouvrir_boutique(personnage, 'violet', assortiments_kecleon_violet, 1,
    'Mon étal violet garde les articles précieux. Ils coûtent plus cher, mais ils peuvent changer une traversée.')
end

-- Gimmighoul ambulant : seule banque de Réverie Town.
function ville.NewObject_3_Action(personnage, activator)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Des pièces, des pièces ! Je peux garder votre argent dans mon coffre et vous le rendre au Poké près.')
  UI:ResetSpeaker()
  UI:BankMenu()
  UI:WaitForChoice()
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Votre trésor est compté. Kangourex garde les objets ; moi, je veille sur les Poké.')
  UI:ResetSpeaker()
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
end

-- Tinkaton : ouvrir les boîtes au trésor (150 Poké par boîte), avec le menu
-- natif d'expertise de PMDO.
function ville.NewObject_24_Action(personnage, activator)
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
end

local function dialogue_lombre_ludicolo(premier, second)
  conversation({premier, second}, {
    {1, 'Normal', 'La cascade chante plus fort ce matin. Les ponts vont encore être glissants.'},
    {2, 'Happy', 'Alors dansons lentement en les traversant. Réverie Town récompense ceux qui gardent le rythme.'},
    {1, 'Happy', 'Facile à dire pour toi ! Mais je suivrai tes pas, comme toujours.'},
  })
end
function ville.NewObject_7_Action(personnage, activator)
  dialogue_lombre_ludicolo(personnage, CH('NewObject_8'))
end
function ville.NewObject_8_Action(personnage, activator)
  dialogue_lombre_ludicolo(personnage, CH('NewObject_7'))
end

local function dialogue_lux(second, premier)
  conversation({second, premier}, {
    {1, 'Worried', 'Dis… Lost Wood fait vraiment aussi peur qu’on le raconte ?'},
    {2, 'Normal', 'Il demande du respect, pas de la peur. On y entre préparé, et jamais en se croyant invincible.'},
    {1, 'Happy', 'Alors je m’entraînerai encore. Un jour, je traverserai à tes côtés.'},
  })
end
function ville.NewObject_9_Action(personnage, activator)
  dialogue_lux(CH('NewObject_10'), personnage)
end
function ville.NewObject_10_Action(personnage, activator)
  dialogue_lux(personnage, CH('NewObject_9'))
end

local dialogues_habitants = {
  NewObject_6 = {{'Happy', 'De là-haut, on voit les toits, les chutes et même un morceau de la falaise. Réverie Town tient dans un battement d’ailes.'}},
  NewObject_12 = {{'Normal', 'Je porte les caisses du marché le matin. L’après-midi, je laisse mes bras raconter qu’ils ont bien travaillé.'}},
  NewObject_13 = {{'Happy', 'J’adore suivre les reflets sur l’eau. Quand une équipe revient de mission, toute la place semble briller.'}},
  NewObject_14 = {{'Normal', 'Les explorateurs pressés oublient souvent de vérifier leur sac. Kangourex et les Kecleon existent pour une raison.'}},
  Doyen = {{'Normal', 'Je connais chaque courant qui passe au-dessus des cascades. La ville change, mais le vent se souvient.'}},
  Drifloon = {{'Happy', 'Le vent m’emmène d’un quartier à l’autre. Aujourd’hui, il a décidé de rester près du Doyen.'}},
  NewObject_16 = {{'Normal', 'Je surveille les chemins qui montent vers les hauteurs. Un ciel dégagé annonce souvent une bonne journée d’expédition.'}},
  NewObject_11 = {{'Normal', 'Mon équipe se repose. Savoir s’arrêter à Réverie Town fait aussi partie du métier d’explorateur.'}},
  NewObject_18 = {{'Normal', 'Zzz… prévenez-moi quand le café Spinda servira le goûter… Zzz…'}},
  NewObject_20 = {{'Normal', 'Les jeunes équipes regardent toujours l’horizon. C’est bon signe : la ville a besoin de rêves neufs.'}},
  NewObject_21 = {{'Happy', 'Le parfum des baies du marché me donne des idées de desserts pour tout le quartier !'}},
  NewObject_15 = {{'Happy', 'Un bon lait chaud après une mission, et les pattes tremblent déjà moins.'}},
  NewObject_17 = {{'Normal', 'Je fais ma ronde entre les ponts. Si vous cherchez la place, suivez le bruit des boutiques.'}},
  NewObject_22 = {{'Normal', 'On dit que les ombres de Lost Wood se déplacent. Moi, je dis surtout de garder une Baie Lum à portée de patte.'}},
  NewObject_23 = {{'Happy', 'Je décorerais bien la place pour le retour des équipes. Il suffit de peu pour qu’une ville sourie.'}},
}
for nom, repliques in pairs(dialogues_habitants) do
  local texte = repliques
  ville[nom .. '_Action'] = function(personnage, activator)
    dialogue_simple(personnage, texte)
  end
end

return ville
