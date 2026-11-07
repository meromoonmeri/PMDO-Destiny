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

local function activer(nom, rayon)
  local acteur = CH(nom)
  if acteur == nil then return end
  COMMON.CreateWalkArea(nom,
    math.max(0, acteur.Position.X - rayon),
    math.max(0, acteur.Position.Y - rayon), rayon * 2, rayon * 2)
  AI:EnableCharacterAI(acteur)
end

-- La carte ne sérialise aucune sortie : un objet invisible sur le tapis sud
-- sert de porte vers Réverie Town, et le personnel guide vers les autres
-- salles en attendant des portes sérialisées dans la carte.
local function installer_sortie(map)
  if map == nil then return end
  if map:FindObject('PorteSortieCafe') then GROUND:RemoveObject('PorteSortieCafe') end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteSortieCafe'
  porte.Collider = RogueElements.Rect(268, 374, 64, 16)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

-- L’escalier nord mène à l’étage du café, au contact comme la sortie sud.
local function installer_escalier_nord(map)
  if map == nil then return end
  if map:FindObject('EscalierNordCafe') then GROUND:RemoveObject('EscalierNordCafe') end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'EscalierNordCafe'
  porte.Collider = RogueElements.Rect(272, 120, 48, 8)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

local function aller_a(index_carte)
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, index_carte, 0)
end

local function dire(acteur, emotion, texte)
  if acteur == nil then return end
  UI:SetSpeaker(acteur)
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

local function placer_personnel()
  -- Dégager les trois employés de l’escalier nord sans changer la carte.
  for _, poste in ipairs({{'Spinda',224,160}, {'MrMimeJunior',352,160}, {'Kirlia',224,184}}) do
    local acteur = CH(poste[1])
    if acteur ~= nil then
      GROUND:TeleportTo(acteur, poste[2], poste[3], Direction.Down)
      AI:DisableCharacterAI(acteur)
    end
  end
end

function cafespindaaccueil.Init(map)
  nommer_personnel()
  installer_sortie(map)
  installer_escalier_nord(map)
  placer_personnel()
  activer('NewObject_13', 36)
  activer('Pompot', 36)
  activer('Qulbutoqué', 28)
  activer('Okéoké', 28)
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
  -- Pipo reste à son poste ; il peut écouter la conversation sans trajet
  -- supplémentaire. Les regards sont limités aux participants présents.
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
  -- L'entrée est cadrée avant toute prise de parole ; déplacements uniquement
  -- depuis des positions connues, sans téléportation à travers les occupants.
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
  local parcours = {{224,160},{256,160},{256,248},{272,248}}
  local depart = {x=spinda.Position.X,y=spinda.Position.Y,dir=spinda.Direction}
  if depart.x == 224 and depart.y == 160 and passage_libre(map,spinda,parcours,hero,partenaire) then
    for i=2,#parcours do
      if not passage_libre(map,spinda,{parcours[i-1],parcours[i]},hero,partenaire) then break end
      GROUND:MoveToPosition(spinda,parcours[i][1],parcours[i][2],false,1)
    end
  end
  GROUND:CharTurnToCharAnimated(spinda, hero, 4)
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  GAME:WaitFrames(8)
  dire(spinda, 'Happy', 'Bienvenue, bienvenue ! Vous tombez bien : il reste juste assez de place pour deux nouvelles histoires !')
  dire(spinda, 'Happy', 'Moi, c’est Spinda ! Entrez donc, même si mes murs ont encore besoin d’un petit coup de neuf !')
  UI:ResetSpeaker()
  GROUND:CharSetEmote(partenaire, 'question', 1)
  GAME:WaitFrames(10)
  ecouter_cafe(partenaire, spinda, hero, kirlia, pipo)
  dire(partenaire, 'Normal', 'Oh ! Bonjour… Vous êtes un employé comme les autres ?')
  GROUND:CharTurnToCharAnimated(kirlia, partenaire, 4)
  ecouter_cafe(kirlia, partenaire, hero, spinda, pipo)
  dire(kirlia, 'Happy', 'Vous ne l’avez pas reconnu ? C’est Spinda, le président de la Fédération des Explorateurs !')
  dire(kirlia, 'Normal', 'Et le grand patron des cafés Spinda. Ils accueillent secouristes et explorateurs de toutes les guildes, partout dans le monde.')
  GROUND:CharTurnToCharAnimated(spinda, partenaire, 4)
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  dire(spinda, 'Happy', 'Des récits, des rencontres et des boissons ! Enfin… surtout des récits et des rencontres, pour le moment !')
  UI:ResetSpeaker()
  GROUND:CharSetEmote(hero, 'exclaim', 1)
  GAME:WaitFrames(10)
  -- Le partenaire remarque la réaction du héros ; les autres ne peuvent
  -- pas entendre sa pensée intérieure.
  GROUND:CharTurnToCharAnimated(partenaire, hero, 4)
  dire(hero, 'Surprised', '(Bah dis donc… quel sacré personnage !)')
  ecouter_cafe(spinda, partenaire, hero, kirlia, pipo)
  dire(spinda, 'Normal', 'Le café est fermé pour rénovation. En attendant, notre accueil reste ici ; passez nous voir, nous vous renseignerons !')
  if SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(spinda, 'Worried', 'Kirlia m’a parlé de Nilo. Préparez-vous bien avant de rejoindre Lyra ; nous pensons à lui.')
  end
  UI:ResetSpeaker()
  GAME:WaitFrames(20)
  -- Revenir à son poste si le trajet est toujours dégagé ; sinon rester en place.
  for i=#parcours,2,-1 do
    if spinda.Position.X == parcours[i][1] and spinda.Position.Y == parcours[i][2]
      and passage_libre(map,spinda,{parcours[i],parcours[i-1]},hero,partenaire) then
      GROUND:MoveToPosition(spinda,parcours[i-1][1],parcours[i-1][2],false,1)
    end
  end
  if spinda.Position.X == depart.x and spinda.Position.Y == depart.y then GROUND:EntTurn(spinda, depart.dir) end
  for _, a in ipairs(fond_cafe) do pcall(function() GROUND:CharEndAnim(a) end) end
  if pipo ~= nil and pipo.EntEnabled ~= false and direction_pipo ~= nil then GROUND:EntTurn(pipo, direction_pipo) end
  SV.Destiny.VisiteCafeSpinda = 'terminee'
  GAME:MoveCamera(0,0,45,true)
  equipe_scene.Suivre(partenaire,hero)
  GAME:CutsceneMode(false)
  return true
end

function cafespindaaccueil.Enter(map)
  sortie_cafe_en_cours = false
  SV.Destiny = SV.Destiny or {}
  local retour_escalier = SV.Destiny.RetourCafeAccueil == 'escalier'
  if retour_escalier then
    SV.Destiny.RetourCafeAccueil = nil
    local hero, partenaire = CH('PLAYER'), CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 288, 152, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 312, 160, Direction.Down) end
  end
  -- Ne jamais garder l'écran noir pendant l'initialisation facultative du suivi.
  GAME:MoveCamera(0,0,1,true)
  GAME:FadeIn(30)
  local ok, err = pcall(suivi_interieurs.Activer, map)
  if not ok then print('[Destiny] Suivi intérieur indisponible : '..tostring(err)) end
  if not retour_escalier and SV.Destiny.VisiteCafeSpinda ~= 'terminee' then
    premiere_visite(map, CH('PLAYER'), CH('Teammate1'))
  end
end

function cafespindaaccueil.GameLoad(map)
  nommer_personnel()
  placer_personnel()
  sortie_cafe_en_cours = false
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

function cafespindaaccueil.Update(map, time)
end

function cafespindaaccueil.Spinda_Action(personnage, activator)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(personnage, 'Worried', 'Je pense à Nilo et à Lyra. Préparez-vous bien, et ne perdez pas courage.')
  end
  dire(personnage, 'Happy', 'Bienvenue à l’accueil du café Spinda ! Ici, les explorateurs partagent leurs récits de mission.')
  dire(CH('MrMimeJunior'), 'Happy', 'Je prépare les verres sans dire un mot. Le spectacle commence dès le comptoir !')
  dire(CH('Kirlia'), 'Normal', 'Et moi, j’écoute les équipes. Certaines histoires commencent par une simple boisson partagée.')
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
    return
  end
  UI:ResetSpeaker()
  if choix == 1 then aller_a(3)
  elseif choix == 2 then
    SV.Destiny = SV.Destiny or {}; SV.Destiny.ArriveeSalleCafe = true
    aller_a(4)
  end
end

function cafespindaaccueil.MrMimeJunior_Action(personnage, activator)
  dire(personnage, 'Happy', 'Je mime le verseur parfait : pas une goutte imaginaire ne tombe à côté.')
  dire(CH('Spinda'), 'Happy', 'Et pendant les travaux, nous accueillons les visiteurs ensemble !')
  UI:ResetSpeaker()
end

function cafespindaaccueil.Kirlia_Action(personnage, activator)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    dire(personnage, 'Worried', 'Lyra doit être si inquiète pour Nilo… J’espère qu’il tient bon.')
    UI:ResetSpeaker()
    return
  end
  dire(personnage, 'Normal', 'Les voyageurs laissent parfois une émotion derrière eux. Je la transforme en conseil pour l’équipe suivante.')
  UI:ResetSpeaker()
end

local function dialogue_recyclage(okeoke, qulbutoque)
  dire(okeoke, 'Happy', 'Nous trions les petits trésors que les explorateurs ne savent plus où ranger.')
  dire(qulbutoque, 'Normal', 'Rien ne se perd au café : un objet délaissé peut devenir une surprise pour quelqu’un d’autre.')
  dire(okeoke, 'Normal', 'Notre atelier de recyclage ouvrira quand toutes les caisses seront enfin rangées.')
  UI:ResetSpeaker()
end

cafespindaaccueil['Qulbutoqué_Action'] = function(personnage, activator)
  dialogue_recyclage(CH('Okéoké'), personnage)
end

cafespindaaccueil['Okéoké_Action'] = function(personnage, activator)
  dialogue_recyclage(personnage, CH('Qulbutoqué'))
end

function cafespindaaccueil.NewObject_13_Action(personnage, activator)
  dire(personnage, 'Happy', 'Je goûte chaque nouveauté du comptoir. Pour le travail, évidemment. Uniquement pour le travail.')
  UI:ResetSpeaker()
end

function cafespindaaccueil.Pompot_Action(personnage, activator)
  dire(personnage, 'Normal', 'Après les Bois Perdus, même une chaise tranquille ressemble à un trésor. Réverie Town sait accueillir les pattes fatiguées.')
  UI:ResetSpeaker()
end

return cafespindaaccueil
