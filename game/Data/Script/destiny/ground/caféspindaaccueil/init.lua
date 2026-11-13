-- Accueil du café Spinda : habitants sérialisés de la carte town02.
-- Les dialogues sont originaux Destiny ; les services avancés du café
-- restent à brancher sur les menus natifs dans une tranche ultérieure.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local meteo_reverie = require 'destiny.meteo_reverie'

local cafespindaaccueil = {}
local sortie_cafe_en_cours = false
local horloge_spinda = 0

local function protege(etape, fonction)
  local ok, err = pcall(fonction)
  if not ok then
    print('[Destiny] café Spinda : étape ignorée (' .. tostring(etape) .. ') : ' .. tostring(err))
  end
  return ok
end

local function tourner_dir(acteur, dir)
  if acteur == nil or dir == nil then return end
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(acteur, dir, 4) end)
  elseif GROUND.EntTurn ~= nil then
    pcall(function() GROUND:EntTurn(acteur, dir) end)
  end
end

local function installer_sortie(map)
  if map == nil then return end
  protege('sortie sud', function()
    if map:FindObject('PorteSortieCafe') then GROUND:RemoveObject('PorteSortieCafe') end
    local porte = RogueEssence.Ground.GroundObject()
    porte.EntName = 'PorteSortieCafe'
    porte.Collider = RogueElements.Rect(268, 374, 64, 16)
    porte.Passable = false
    porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
    porte:OnMapInit()
    map:AddObject(porte)
  end)
end

-- L’escalier nord mène à l’étage du café, au contact comme la sortie sud.
local function installer_escalier_nord(map)
  if map == nil then return end
  protege('escalier nord', function()
    if map:FindObject('EscalierNordCafe') then GROUND:RemoveObject('EscalierNordCafe') end
    local porte = RogueEssence.Ground.GroundObject()
    porte.EntName = 'EscalierNordCafe'
    porte.Collider = RogueElements.Rect(272, 120, 48, 8)
    porte.Passable = false
    porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
    porte:OnMapInit()
    map:AddObject(porte)
  end)
end

local function aller_a(index_carte)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, index_carte, 0)
end

local function tourner_vers(acteur, cible)
  if acteur == nil or cible == nil or acteur == cible then return end
  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(acteur, cible, 4) end)
  elseif GROUND.CharTurnToChar ~= nil then
    pcall(function() GROUND:CharTurnToChar(acteur, cible) end)
  end
end

local function dire(acteur, emotion, texte, cote)
  if acteur == nil then return end
  UI:SetSpeaker(acteur)
  if cote == 'droite' then
    if UI.SetSpeakerLoc ~= nil then UI:SetSpeakerLoc(264, 131, true) end
  elseif UI.ResetSpeakerLoc ~= nil then
    UI:ResetSpeakerLoc()
  end
  UI:SetSpeakerEmotion(emotion)
  UI:WaitShowDialogue(texte)
end

local function nommer(nom, affiche)
  local acteur = CH(nom)
  if acteur ~= nil and acteur.Data ~= nil then acteur.Data.Nickname = affiche end
end

local function nommer_personnel()
  nommer('Spinda', '')
  nommer('MrMimeJunior', 'Pipo')
  nommer('Kirlia', 'Alizé')
  nommer('NewObject_13', 'Noisette')
  nommer('Pompot', 'Pompon')
  nommer('Qulbutoqué', 'Balou')
  nommer('Okéoké', 'Bulle')
end

-- Le personnel est installé ensemble en haut de la salle, sans bloquer
-- l'escalier nord et sans placer Kirlia sur la trajectoire de Spinda.
local function placer_personnel()
  for _, poste in ipairs({
    {'Spinda', 224, 160, Direction.Down},
    {'Kirlia', 200, 164, Direction.Down},
    {'MrMimeJunior', 352, 160, Direction.Down},
  }) do
    local acteur = CH(poste[1])
    if acteur ~= nil then
      GROUND:TeleportTo(acteur, poste[2], poste[3], poste[4])
      AI:DisableCharacterAI(acteur)
    end
  end
end

-- Les clients attablés restent assis à leur table, face à leur compagnon,
-- au lieu de quitter leurs tabourets ou de s'éloigner les uns des autres.
local function fixer_clients_attables()
  local bas_gauche = Direction.DownLeft or Direction.Down
  local haut_droite = Direction.UpRight or Direction.Right
  for _, siege in ipairs({
    {'NewObject_13', bas_gauche},
    {'Pompot', haut_droite},
    {'Okéoké', Direction.Right},
    {'Qulbutoqué', Direction.Left},
  }) do
    local acteur = CH(siege[1])
    if acteur ~= nil then
      AI:DisableCharacterAI(acteur)
      pcall(function() GROUND:EntTurn(acteur, siege[2]) end)
    end
  end
  local a, b = CH('Okéoké'), CH('Qulbutoqué')
  if a ~= nil and b ~= nil then
    pcall(function() GROUND:EntTurn(a, Direction.Right); GROUND:EntTurn(b, Direction.Left) end)
  end
  local g, p = CH('NewObject_13'), CH('Pompot')
  if g ~= nil and p ~= nil then
    pcall(function() GROUND:EntTurn(g, bas_gauche); GROUND:EntTurn(p, haut_droite) end)
  end
end

local function pas_spinda_etourdi(spinda)
  if spinda == nil then return end
  pcall(function()
    GROUND:CharSetEmote(spinda, 'happy', 1)
    GROUND:CharAnimateTurnTo(spinda, Direction.Left, 2)
    GROUND:CharAnimateTurnTo(spinda, Direction.Up, 2)
    GROUND:CharAnimateTurnTo(spinda, Direction.Right, 2)
    GROUND:CharAnimateTurnTo(spinda, Direction.Down, 2)
  end)
end

function cafespindaaccueil.Init(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  protege('noms du personnel', nommer_personnel)
  installer_sortie(map)
  installer_escalier_nord(map)
  protege('placement du personnel', placer_personnel)
  protege('clients attablés', fixer_clients_attables)
end

-- Tests d'occupation prudents : on ne force pas un trajet si les personnages
-- présents ou la liste des entités ne peuvent pas être vérifiés.
local function passage_libre(map, acteur, points, hero, partenaire)
  if map == nil or map.Entities == nil or acteur == nil or acteur.EntEnabled == false then return false end
  local function croise(autre)
    if autre == nil or autre == acteur or autre.EntEnabled == false or autre.Position == nil then return false end
    local x,y = autre.Position.X, autre.Position.Y
    for i=1,#points-1 do
      local a,b = points[i],points[i+1]
      if x < math.max(a[1],b[1])+16 and x+16 > math.min(a[1],b[1])
        and y < math.max(a[2],b[2])+16 and y+16 > math.min(a[2],b[2]) then return true end
    end
    return false
  end
  if croise(hero) or croise(partenaire) then return false end
  local ok, libre = pcall(function()
    for couche in luanet.each(map.Entities) do
      if couche.Visible then
        for autre in luanet.each(couche.MapChars) do if croise(autre) then return false end end
        for autre in luanet.each(couche.TemporaryChars) do if croise(autre) then return false end end
      end
    end
    return true
  end)
  return ok and libre
end

local function premiere_visite(map, hero, partenaire)
  local spinda, kirlia, pipo = CH('Spinda'), CH('Kirlia'), CH('MrMimeJunior')
  if hero == nil or partenaire == nil or spinda == nil or kirlia == nil then return false end
  local function ecouter_cafe(locuteur, ...)
    if locuteur == nil or locuteur.EntEnabled == false then return end
    local regards, vus = {}, {}
    for i=1,select('#', ...) do
      local a = select(i, ...)
      if a ~= nil and a ~= locuteur and a.EntEnabled ~= false and not vus[a]
        and (a ~= pipo or (a.Position ~= nil and math.abs(a.Position.X-280) <= 160
          and math.abs(a.Position.Y-250) <= 120)) then
        vus[a] = true
        table.insert(regards, {a, locuteur, #regards * 4, 4})
      end
    end
    if #regards > 0 then cinematique.RegarderGroupe(regards) end
  end
  GAME:CutsceneMode(true)
  local direction_pipo = pipo ~= nil and pipo.Direction or nil
  local fond_cafe, vus_fond = {}, {}
  local function ajouter_fond_cafe(a)
    if a == nil or a == hero or a == partenaire or a == spinda or a == kirlia
      or a == pipo or a.EntEnabled == false or a.Position == nil or vus_fond[a]
      or math.abs(a.Position.X-280) > 160 or math.abs(a.Position.Y-250) > 120 then return end
    vus_fond[a] = true
    local ok = pcall(function() GROUND:CharSetAnim(a, 'Idle', true) end)
    if ok then table.insert(fond_cafe, a) end
  end
  pcall(function()
    if map == nil or map.Entities == nil then return end
    for couche in luanet.each(map.Entities) do
      if couche.Visible ~= false then
        for a in luanet.each(couche.MapChars) do ajouter_fond_cafe(a) end
        for a in luanet.each(couche.TemporaryChars) do ajouter_fond_cafe(a) end
      end
    end
  end)
  AI:DisableCharacterAI(partenaire)
  AI:DisableCharacterAI(spinda)
  local h = {{hero.Position.X,hero.Position.Y},{hero.Position.X,280}}
  local p = {{partenaire.Position.X,partenaire.Position.Y},{partenaire.Position.X,280}}
  if hero.Position.X >= 280 and hero.Position.X <= 296 and hero.Position.Y >= 328 and hero.Position.Y <= 360
    and partenaire.Position.X >= 304 and partenaire.Position.X <= 320 and partenaire.Position.Y >= 328 and partenaire.Position.Y <= 360
    and passage_libre(map,hero,h,hero,partenaire) and passage_libre(map,partenaire,p,hero,partenaire) then
    local avance = TASK:BranchCoroutine(function() GROUND:MoveToPosition(hero,h[2][1],h[2][2],false,1) end)
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(partenaire,p[2][1],p[2][2],false,1)
    TASK:JoinCoroutines({avance})
  end
  GAME:MoveCamera(280, 250, 55, false)
  GAME:WaitFrames(12)
  -- Démarche titubante caractéristique de Spinda : quelques pas en zigzags
  -- joyeux puis petite pirouette devant le duo (sans traverser Kirlia).
  local parcours = {{224,160},{248,168},{248,200},{264,216},{252,232},{272,248}}
  local depart = {x=spinda.Position.X,y=spinda.Position.Y,dir=spinda.Direction}
  if depart.x == 224 and depart.y == 160 and passage_libre(map,spinda,parcours,hero,partenaire) then
    if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
      SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    end
    pcall(function() GROUND:CharSetEmote(spinda, 'exclaim', 1) end)
    GAME:WaitFrames(25)
    for i=2,#parcours do
      if not passage_libre(map,spinda,{parcours[i-1],parcours[i]},hero,partenaire) then break end
      GROUND:MoveToPosition(spinda,parcours[i][1],parcours[i][2],false,1)
      if i == 3 or i == 5 then
        pcall(function() GROUND:CharSetEmote(spinda, 'happy', 1) end)
      end
    end
    pas_spinda_etourdi(spinda)
  end
  GROUND:CharTurnToCharAnimated(spinda, hero, 4)
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  GAME:WaitFrames(15)
  dire(spinda, 'Happy', 'Bienvenue, bienvenue ! Vous tombez bien : il reste juste assez de place pour deux nouvelles histoires !')
  dire(spinda, 'Happy', 'Moi, c’est Spinda ! Entrez donc, même si mes murs ont encore besoin d’un petit coup de neuf !')
  UI:ResetSpeaker()
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
  end
  GROUND:CharSetEmote(partenaire, 'question', 1)
  GAME:WaitFrames(25)
  ecouter_cafe(partenaire, spinda, hero, kirlia, pipo)
  dire(partenaire, 'Normal', 'Oh ! Bonjour… Vous êtes un employé comme les autres ?', 'droite')
  GROUND:CharTurnToCharAnimated(kirlia, partenaire, 4)
  ecouter_cafe(kirlia, partenaire, hero, spinda, pipo)
  dire(kirlia, 'Happy', 'Vous ne l’avez pas reconnu ? C’est Spinda, le président de la Fédération des Explorateurs !')
  dire(kirlia, 'Normal', 'Et le grand patron des cafés Spinda. Ils accueillent secouristes et explorateurs de toutes les guildes, partout dans le monde.')
  GROUND:CharTurnToCharAnimated(spinda, partenaire, 4)
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  dire(spinda, 'Happy', 'Des récits, des rencontres et des boissons ! Enfin… surtout des récits et des rencontres, pour le moment !')
  UI:ResetSpeaker()
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  end
  GROUND:CharSetEmote(hero, 'exclaim', 1)
  GAME:WaitFrames(25)
  GROUND:CharTurnToCharAnimated(partenaire, hero, 4)
  dire(hero, 'Surprised', '(Bah dis donc… quel sacré personnage !)')
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  dire(spinda, 'Normal', 'Le café est fermé pour rénovation. En attendant, notre accueil reste ici ; passez nous voir, nous vous renseignerons !', 'droite')
  if SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(spinda, 'Worried', 'Kirlia m’a parlé de Nilo. Préparez-vous bien avant de rejoindre Lyra ; nous pensons à lui.', 'droite')
  elseif SV.Destiny.AlerteShinx == 'termine' then
    dire(spinda, 'Happy', 'Tout le café se réjouit de savoir le petit Nilo sain et sauf aux côtés de Lyra !', 'droite')
  end
  UI:ResetSpeaker()
  GAME:WaitFrames(20)
  -- Fondu de fin de cinématique : Spinda rejoint son poste derrière l'écran noir.
  if GAME.FadeOut ~= nil then GAME:FadeOut(false, 30) end
  GAME:WaitFrames(30)
  GROUND:TeleportTo(spinda, depart.x, depart.y, depart.dir)
  if kirlia ~= nil then GROUND:EntTurn(kirlia, Direction.Down) end
  for _, a in ipairs(fond_cafe) do pcall(function() GROUND:CharEndAnim(a) end) end
  if pipo ~= nil and pipo.EntEnabled ~= false and direction_pipo ~= nil then GROUND:EntTurn(pipo, direction_pipo) end
  SV.Destiny.VisiteCafeSpinda = 'terminee'
  GAME:MoveCamera(0, 0, 1, true)
  equipe_scene.Suivre(partenaire, hero)
  GAME:FadeIn(30)
  GAME:CutsceneMode(false)
  return true
end

function cafespindaaccueil.Enter(map)
  sortie_cafe_en_cours = false
  horloge_spinda = 0
  SV.Destiny = SV.Destiny or {}
  local retour_escalier = SV.Destiny.RetourCafeAccueil == 'escalier'
  if retour_escalier then
    SV.Destiny.RetourCafeAccueil = nil
    local hero, partenaire = CH('PLAYER'), CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 288, 152, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 312, 160, Direction.Down) end
  end
  GAME:MoveCamera(0,0,1,true)
  GAME:FadeIn(30)
  local ok, err = pcall(suivi_interieurs.Activer, map)
  if not ok then print('[Destiny] Suivi intérieur indisponible : '..tostring(err)) end
  if not retour_escalier and SV.Destiny.VisiteCafeSpinda ~= 'terminee' then
    premiere_visite(map, CH('PLAYER'), CH('Teammate1'))
  end
end

function cafespindaaccueil.GameLoad(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  protege('noms au chargement', nommer_personnel)
  protege('placement au chargement', placer_personnel)
  protege('clients au chargement', fixer_clients_attables)
  sortie_cafe_en_cours = false
  horloge_spinda = 0
  installer_sortie(map)
  installer_escalier_nord(map)
  GAME:MoveCamera(0,0,1,true)
  GAME:FadeIn(30)
  local ok, err = pcall(suivi_interieurs.Activer, map)
  if not ok then print('[Destiny] Suivi intérieur indisponible au chargement : '..tostring(err)) end
end

function cafespindaaccueil.EscalierNordCafe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_cafe_en_cours then return end
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.CafeRenovationTerminee ~= true then
    UI:ResetSpeaker()
    UI:WaitShowDialogue('L’étage est fermé pendant les travaux. L’accueil reste ouvert ici.')
    return
  end
  sortie_cafe_en_cours = true
  aller_a(3)
end

function cafespindaaccueil.PorteSortieCafe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_cafe_en_cours then return end
  sortie_cafe_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'cafe'
  aller_a(0)
end

-- Animation d'ambiance non bloquante : Spinda se dandine doucement à son
-- poste aux côtés de Kirlia sans quitter sa place ni gêner le passage.
function cafespindaaccueil.Update(map, time)
  if sortie_cafe_en_cours then return end
  if SV == nil or SV.Destiny == nil or SV.Destiny.VisiteCafeSpinda ~= 'terminee' then return end
  horloge_spinda = horloge_spinda + 1
  if horloge_spinda % 64 ~= 0 then return end
  local spinda = CH('Spinda')
  if spinda == nil or spinda.EntEnabled == false then return end
  pcall(function()
    if spinda.IsInteracting then return end
    local cycle = math.floor(horloge_spinda / 64) % 4
    local dirs = {
      Direction.DownLeft or Direction.Left,
      Direction.Down,
      Direction.DownRight or Direction.Right,
      Direction.Down,
    }
    GROUND:EntTurn(spinda, dirs[cycle + 1])
    if cycle == 2 and (math.floor(horloge_spinda / 256) % 2 == 0) then
      GROUND:CharSetEmote(spinda, 'happy', 1)
    end
  end)
end

function cafespindaaccueil.Spinda_Action(personnage, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(personnage, joueur)
  pas_spinda_etourdi(personnage)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(personnage, 'Worried', 'Je pense à Nilo et à Lyra. Préparez-vous bien, et ne perdez pas courage.')
  elseif SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'termine' then
    dire(personnage, 'Happy', 'Savoir Nilo sain et sauf aux côtés de Lyra met du baume au cœur à tout le café !')
  end
  dire(personnage, 'Happy', 'Bienvenue à l’accueil du café Spinda ! Ici, les explorateurs partagent leurs récits de mission.')
  local pipo = CH('MrMimeJunior')
  tourner_vers(pipo, joueur)
  dire(pipo, 'Happy', 'Je prépare les verres sans dire un mot. Le spectacle commence dès le comptoir !')
  local kirlia = CH('Kirlia')
  tourner_vers(kirlia, joueur)
  dire(kirlia, 'Normal', 'Et moi, j’écoute les équipes. Certaines histoires commencent par une simple boisson partagée.')
  tourner_vers(personnage, joueur)
  if SV.Destiny ~= nil and SV.Destiny.CafeRenovationTerminee == true then
    dire(personnage, 'Normal', 'Installez-vous. L’étage est plus calme, et la salle voisine accueille nos petits spectacles.')
  else
    dire(personnage, 'Normal', 'L’accueil reste ouvert pendant les travaux ; les autres salles attendront la fin de la rénovation.')
  end
  UI:ResetSpeaker()
  SV.Destiny = SV.Destiny or {}
  local travaux = SV.Destiny.CafeRenovationTerminee ~= true
  local choix
  if travaux then
    UI:WaitShowDialogue('Le café est en rénovation ; seul l’accueil est ouvert pour le moment.')
    UI:BeginChoiceMenu('Que souhaitez-vous faire ?', {'Faire une sieste', 'Rester à l’accueil'}, 2, 2)
    UI:WaitForChoice()
    choix = UI:ChoiceResult() == 1 and 3 or 4
  else
    UI:BeginChoiceMenu('Souhaitez-vous que je vous guide, ou faire une sieste jusqu’à demain ?', {
      'Monter à l’étage', 'Aller à la salle de spectacle', 'Faire une sieste', 'Rester à l’accueil',
    }, 1, 4)
    UI:WaitForChoice()
    choix = UI:ChoiceResult()
  end
  if choix == 3 then
    dire(personnage, 'Normal', 'Installez-vous dans un coin tranquille. Demain, Basil et Félix auront renouvelé leurs étals.')
    UI:ResetSpeaker()
    GAME:FadeOut(false, 60)
    GAME:WaitFrames(90)
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
    SV.Destiny.StocksKecleon = {}
    GAME:FadeIn(60)
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Une nouvelle journée commence à Réverie Town… ' .. meteo_reverie.Description())
    tourner_dir(personnage, Direction.Down)
    tourner_dir(kirlia, Direction.Down)
    tourner_dir(pipo, Direction.Down)
    return
  end
  UI:ResetSpeaker()
  tourner_dir(personnage, Direction.Down)
  tourner_dir(kirlia, Direction.Down)
  tourner_dir(pipo, Direction.Down)
  if choix == 1 then aller_a(3)
  elseif choix == 2 then
    SV.Destiny = SV.Destiny or {}; SV.Destiny.ArriveeSalleCafe = true
    aller_a(4)
  end
end

function cafespindaaccueil.MrMimeJunior_Action(personnage, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(personnage, joueur)
  pcall(function() GROUND:CharSetEmote(personnage, 'music', 1) end)
  dire(personnage, 'Happy', 'Je mime le verseur parfait : pas une goutte imaginaire ne tombe à côté.')
  local kirlia = CH('Kirlia')
  if kirlia ~= nil then
    tourner_vers(kirlia, personnage)
    dire(kirlia, 'Happy', 'Pipo s’entraîne déjà à servir le Jus Spécial sans renverser une seule baie invisible.')
    tourner_vers(personnage, kirlia)
  end
  local spinda = CH('Spinda')
  tourner_vers(spinda, joueur)
  dire(spinda, 'Happy', 'Et pendant les travaux, nous accueillons les visiteurs ensemble !')
  UI:ResetSpeaker()
  tourner_dir(personnage, Direction.Down)
  tourner_dir(kirlia, Direction.Down)
  tourner_dir(spinda, Direction.Down)
end

local conseils_kirlia = {
  'Avant une expédition, passez voir Mado pour déposer vos objets précieux et Écu pour mettre vos Poké à l’abri.',
  'Les étals de Basil et Félix changent après chaque sieste ici au café : jetez un œil à leurs réserves quand le jour se lève.',
  'Alakazam aide les équipes à retrouver une capacité oubliée, tandis qu’Iris ouvre les coffres ramenés des donjons.',
}

function cafespindaaccueil.Kirlia_Action(personnage, activator)
  local joueur = activator or CH('PLAYER')
  local spinda = CH('Spinda')
  local pipo = CH('MrMimeJunior')
  tourner_vers(personnage, joueur)
  pcall(function() GROUND:CharSetEmote(personnage, 'happy', 1) end)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(personnage, 'Worried', 'Lyra doit être si inquiète pour Nilo… Je sens toute son angoisse jusqu’ici.')
    if spinda ~= nil then
      tourner_vers(spinda, joueur)
      dire(spinda, 'Normal', 'Prenez le temps de souffler ou de faire vos réserves. Quand Nilo sera rentré, sa place sera prête ici.')
      tourner_vers(personnage, joueur)
    end
  elseif SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'termine' then
    dire(personnage, 'Happy', 'Je ressens un immense soulagement depuis la place ! Nilo est rentré auprès de Lyra grâce à vous.')
    if spinda ~= nil then
      tourner_vers(spinda, joueur)
      dire(spinda, 'Happy', 'Bravo pour la Grotte Verdoyante ! Venez souffler ici entre deux expéditions.')
      tourner_vers(personnage, joueur)
    end
  else
    dire(personnage, 'Normal', 'Bonjour ! Je perçois les émotions des voyageurs et j’aide Spinda à veiller sur le café.')
  end
  while true do
    UI:ResetSpeaker()
    UI:BeginChoiceMenu('Souhaitez-vous discuter d’autre chose ?', {
      'Conseils pour les préparatifs',
      'Parler de Spinda et du café',
      'Ressentir l’ambiance du jour',
      'Rien pour le moment',
    }, 1, 4)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 1 then
      local jour = (SV.Destiny and SV.Destiny.JourneeVille) or 0
      dire(personnage, 'Happy', conseils_kirlia[(jour % #conseils_kirlia) + 1])
      if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
        dire(personnage, 'Normal', 'Si vous manquez de baies avant de retrouver Lyra, une petite sieste auprès de Spinda renouvellera aussi les étals.')
      end
    elseif choix == 2 then
      tourner_vers(personnage, spinda or joueur)
      dire(personnage, 'Happy', 'Spinda a beau tournoyer sans arrêt, il garde toujours une attention incroyable pour chaque équipe.')
      if spinda ~= nil then
        tourner_vers(spinda, personnage)
        pas_spinda_etourdi(spinda)
        dire(spinda, 'Happy', 'Héhé ! Sans Alizé pour me remettre d’aplomb, j’aurais déjà servi deux fois le même jus à l’envers !', 'droite')
        tourner_dir(spinda, Direction.Down)
      end
      if pipo ~= nil then
        tourner_vers(personnage, pipo)
        tourner_vers(pipo, personnage)
        pcall(function() GROUND:CharSetEmote(pipo, 'happy', 1) end)
        dire(personnage, 'Normal', 'Quant à Pipo, ses mimes mettent tout le monde de bonne humeur. Bulle et Balou préparent aussi l’atelier de recyclage.')
      end
      tourner_vers(personnage, joueur)
    elseif choix == 3 then
      dire(personnage, 'Normal', 'Dehors, le temps est ainsi : ' .. meteo_reverie.Description())
      dire(personnage, 'Happy', 'Ici, l’air est doux et plein d’élan. J’espère qu’il portera chance à votre équipe !')
    else
      break
    end
  end
  dire(personnage, 'Normal', 'Prenez soin de vous sur les chemins. Mon regard vous accompagne toujours un peu.')
  UI:ResetSpeaker()
  tourner_dir(personnage, Direction.Down)
  tourner_dir(spinda, Direction.Down)
  tourner_dir(pipo, Direction.Down)
end

local function dialogue_recyclage(okeoke, qulbutoque, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(okeoke, joueur)
  tourner_vers(qulbutoque, joueur)
  dire(okeoke, 'Happy', 'Nous trions les petits trésors que les explorateurs ne savent plus où ranger.')
  tourner_vers(qulbutoque, okeoke)
  tourner_vers(okeoke, qulbutoque)
  dire(qulbutoque, 'Normal', 'Rien ne se perd au café : un objet délaissé peut devenir une surprise pour quelqu’un d’autre.')
  tourner_vers(okeoke, joueur)
  dire(okeoke, 'Normal', 'Notre atelier de recyclage ouvrira quand toutes les caisses seront enfin rangées.')
  UI:ResetSpeaker()
  tourner_dir(okeoke, Direction.Right)
  tourner_dir(qulbutoque, Direction.Left)
end

cafespindaaccueil['Qulbutoqué_Action'] = function(personnage, activator)
  dialogue_recyclage(CH('Okéoké'), personnage, activator)
end

cafespindaaccueil['Okéoké_Action'] = function(personnage, activator)
  dialogue_recyclage(personnage, CH('Qulbutoqué'), activator)
end

local function dialogue_table_gauche(noisette, pompon, activator)
  local joueur = activator or CH('PLAYER')
  local bas_gauche = Direction.DownLeft or Direction.Down
  local haut_droite = Direction.UpRight or Direction.Right
  tourner_vers(noisette, joueur)
  tourner_vers(pompon, joueur)
  dire(noisette, 'Happy', 'Je goûte chaque nouveauté du comptoir. Pour le travail, évidemment. Uniquement pour le travail.')
  if pompon ~= nil then
    tourner_vers(pompon, noisette)
    tourner_vers(noisette, pompon)
    dire(pompon, 'Normal', 'Après les Bois Perdus, même une chaise tranquille ressemble à un trésor. Et Noisette surveille déjà la cuisine !')
  end
  UI:ResetSpeaker()
  tourner_dir(noisette, bas_gauche)
  tourner_dir(pompon, haut_droite)
end

function cafespindaaccueil.NewObject_13_Action(personnage, activator)
  dialogue_table_gauche(personnage, CH('Pompot'), activator)
end

function cafespindaaccueil.Pompot_Action(personnage, activator)
  local noisette = CH('NewObject_13')
  if noisette ~= nil then
    local joueur = activator or CH('PLAYER')
    local bas_gauche = Direction.DownLeft or Direction.Down
    local haut_droite = Direction.UpRight or Direction.Right
    tourner_vers(personnage, joueur)
    tourner_vers(noisette, joueur)
    dire(personnage, 'Normal', 'Après les Bois Perdus, même une chaise tranquille ressemble à un trésor. Réverie Town sait accueillir les pattes fatiguées.')
    tourner_vers(noisette, personnage)
    dire(noisette, 'Happy', 'Et dès que le service ouvrira, je te garde une place au premier rang pour le goûter !')
    UI:ResetSpeaker()
    tourner_dir(noisette, bas_gauche)
    tourner_dir(personnage, haut_droite)
  else
    tourner_vers(personnage, activator or CH('PLAYER'))
    dire(personnage, 'Normal', 'Après les Bois Perdus, même une chaise tranquille ressemble à un trésor. Réverie Town sait accueillir les pattes fatiguées.')
    UI:ResetSpeaker()
  end
end

return cafespindaaccueil
