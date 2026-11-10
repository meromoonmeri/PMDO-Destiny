-- Étage du café Spinda : coin calme et atelier de recyclage en préparation.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local spindacafeetage1 = {}
local transition_cafe_en_cours = false

local function activer(nom, rayon)
  local acteur = CH(nom)
  if acteur == nil then return end
  COMMON.CreateWalkArea(nom,
    math.max(0, acteur.Position.X - rayon),
    math.max(0, acteur.Position.Y - rayon), rayon * 2, rayon * 2)
  AI:EnableCharacterAI(acteur)
end

local function contact(map, nom, x, y, w, h)
  if map == nil then return end
  if map:FindObject(nom) then GROUND:RemoveObject(nom) end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = nom
  porte.Collider = RogueElements.Rect(x,y,w,h)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

local function installer_escalier(map)
  -- À la limite praticable du tapis, et non sur les cases bloquées à y=398.
  contact(map, 'EscalierCafe', 268, 368, 64, 8)
  contact(map, 'PassageSalleCafe', 560, 216, 8, 24)
end

local function synchroniser_zone()
  pcall(function()
    if _ZONE ~= nil and _ZONE.CurrentZone ~= nil and _ZONE.CurrentZone.SyncGroundMaps ~= nil then
      _ZONE.CurrentZone:SyncGroundMaps()
    end
  end)
end

local function tourner_vers(acteur, cible)
  if acteur == nil or cible == nil or acteur == cible then return end
  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(acteur, cible, 4) end)
  elseif GROUND.CharTurnToChar ~= nil then
    pcall(function() GROUND:CharTurnToChar(acteur, cible) end)
  end
end

local function aller_a(index_carte)
  if transition_cafe_en_cours then return end
  transition_cafe_en_cours = true
  synchroniser_zone()
  SV.Destiny = SV.Destiny or {}
  if index_carte == 2 then SV.Destiny.RetourCafeAccueil = 'escalier' end
  if index_carte == 4 then SV.Destiny.ArriveeSalleCafe = true end
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
  nommer('NewObject', '')
  nommer('NewObject_1', 'Bulle')
  nommer('NewObject_2', 'Balou')
end

function spindacafeetage1.Init(map)
  synchroniser_zone()
  nommer_personnel()
  installer_escalier(map)
  activer('NewObject', 32)
  activer('NewObject_1', 28)
  activer('NewObject_2', 28)
end

function spindacafeetage1.Enter(map)
  transition_cafe_en_cours = false
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.RetourCafeEtage == 'spectacle' then
    SV.Destiny.RetourCafeEtage = nil
    local hero, partenaire = CH('PLAYER'), CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 528, 216, Direction.Left) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 504, 216, Direction.Left) end
  end
  suivi_interieurs.Activer(map)
  GAME:FadeIn(30)
end

function spindacafeetage1.GameLoad(map) synchroniser_zone(); nommer_personnel(); suivi_interieurs.Activer(map);
  transition_cafe_en_cours = false
  installer_escalier(map)
  GAME:FadeIn(30)
end

function spindacafeetage1.EscalierCafe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  aller_a(2)
end
function spindacafeetage1.PassageSalleCafe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  aller_a(4)
end

function spindacafeetage1.Update(map, time)
end

function spindacafeetage1.NewObject_Action(personnage, activator)
  tourner_vers(personnage, activator or CH('PLAYER'))
  dire(personnage, 'Happy', 'Cet étage est notre refuge quand l’accueil devient trop animé. On y prépare les réserves et les surprises.')
  UI:ResetSpeaker()
  UI:BeginChoiceMenu('Souhaitez-vous que je vous guide ?', {
    'Redescendre à l’accueil', 'Aller à la salle de spectacle', 'Rester à l’étage',
  }, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  UI:ResetSpeaker()
  if choix == 1 then aller_a(2)
  elseif choix == 2 then aller_a(4) end
end

local function dialogue_atelier(okeoke, qulbutoque, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(okeoke, joueur)
  tourner_vers(qulbutoque, joueur)
  dire(okeoke, 'Happy', 'Ici, nous rangeons les caisses du recyclage : rubans, graines, éclats et petits objets oubliés.')
  tourner_vers(qulbutoque, okeoke)
  dire(qulbutoque, 'Normal', 'Chaque équipe laisse quelque chose derrière elle. Notre travail est de lui trouver une seconde vie.')
  tourner_vers(okeoke, joueur)
  dire(okeoke, 'Normal', 'Encore quelques étagères à monter, et l’atelier pourra recevoir les explorateurs.')
  UI:ResetSpeaker()
end

function spindacafeetage1.NewObject_1_Action(personnage, activator)
  dialogue_atelier(personnage, CH('NewObject_2'), activator)
end

function spindacafeetage1.NewObject_2_Action(personnage, activator)
  dialogue_atelier(CH('NewObject_1'), personnage, activator)
end

return spindacafeetage1
