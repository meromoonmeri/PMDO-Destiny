-- Salle de spectacle du café Spinda : artistes et habitués sérialisés.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local spindacafeetage1salle2 = {}
local transition_cafe_en_cours = false

local function activer(nom, rayon)
  local acteur = CH(nom)
  if acteur == nil then return end
  COMMON.CreateWalkArea(nom,
    math.max(0, acteur.Position.X - rayon),
    math.max(0, acteur.Position.Y - rayon), rayon * 2, rayon * 2)
  AI:EnableCharacterAI(acteur)
end

local function installer_porte(map)
  if map == nil then return end
  if map:FindObject('PorteSalleCafe') then GROUND:RemoveObject('PorteSalleCafe') end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteSalleCafe'
  porte.Collider = RogueElements.Rect(8, 216, 8, 24)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
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
  if index_carte == 3 then SV.Destiny.RetourCafeEtage = 'spectacle' end
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
  nommer('NewObject', 'Pipo')
  nommer('NewObject_1', 'Asa')
  nommer('NewObject_2', 'Mina')
  nommer('NewObject_3', 'Mirabelle')
  nommer('NewObject_4', 'Nox')
  nommer('NewObject_5', 'Lila')
  nommer('NewObject_6', 'Rémi')
  nommer('NewObject_7', 'Mimi')
  nommer('NewObject_8', 'Pistache')
  nommer('NewObject_9', 'Pico')
  nommer('NewObject_10', 'Brume')
end

function spindacafeetage1salle2.Init(map)
  synchroniser_zone()
  nommer_personnel()
  installer_porte(map)
  for i = 0, 10 do
    local nom = i == 0 and 'NewObject' or ('NewObject_' .. i)
    activer(nom, 36)
  end
end

function spindacafeetage1salle2.Enter(map)
  transition_cafe_en_cours = false
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.ArriveeSalleCafe then
    SV.Destiny.ArriveeSalleCafe = nil
    local hero, partenaire = CH('PLAYER'), CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 32, 216, Direction.Right) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 56, 216, Direction.Right) end
  end
  suivi_interieurs.Activer(map)
  GAME:FadeIn(30)
end

function spindacafeetage1salle2.GameLoad(map) synchroniser_zone(); nommer_personnel(); suivi_interieurs.Activer(map);
  transition_cafe_en_cours = false
  installer_porte(map)
  GAME:FadeIn(30)
end

function spindacafeetage1salle2.PorteSalleCafe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  aller_a(3)
end

function spindacafeetage1salle2.Update(map, time)
end

function spindacafeetage1salle2.NewObject_Action(personnage, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(personnage, joueur)
  dire(personnage, 'Happy', 'Je répète mon numéro de mime. Le mur invisible est juste là… ne le traversez pas trop vite.')
  local asa = CH('NewObject_1')
  tourner_vers(asa, joueur)
  dire(asa, 'Happy', 'Et quand je chanterai, toute la salle devra rester éveillée jusqu’au dernier refrain !')
  tourner_vers(personnage, joueur)
  UI:ResetSpeaker()
  UI:BeginChoiceMenu('Le rideau invisible peut aussi vous montrer la sortie…', {
    'Retourner à l’accueil', 'Monter à l’étage', 'Rester dans la salle',
  }, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  UI:ResetSpeaker()
  if choix == 1 then aller_a(2)
  elseif choix == 2 then aller_a(3) end
end

function spindacafeetage1salle2.NewObject_1_Action(personnage, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(personnage, joueur)
  dire(personnage, 'Happy', 'Une chanson douce peut reposer une équipe entière. Enfin… si personne ne s’endort avant la fin.')
  local pipo = CH('NewObject')
  tourner_vers(pipo, joueur)
  dire(pipo, 'Normal', 'Je tiendrai le rideau. Invisible, bien entendu.')
  UI:ResetSpeaker()
end

local dialogues = {
  NewObject_2 = 'Pico et moi préparons un numéro d’étincelles synchronisées. Réverie Town va briller !',
  NewObject_3 = 'Les récits de donjon prennent une autre couleur sous les lumières de cette salle.',
  NewObject_4 = 'Je cherche un accessoire disparu avant le spectacle. Dans un café, même les ombres ont des cachettes.',
  NewObject_5 = 'Nous venons écouter les histoires des explorateurs. Certaines valent tous les trésors.',
  NewObject_6 = 'Je garde nos places pendant qu’elle choisit les boissons. Le spectacle commence toujours trop tôt pour les retardataires.',
  NewObject_7 = 'Mon déguisement est prêt. J’espère que le public aimera autant le mystère que les chansons.',
  NewObject_8 = 'Je répète mes applaudissements. Les artistes donnent le meilleur quand la salle répond.',
  NewObject_9 = 'Mina compte les temps, je lance la première étincelle. Ne clignez pas des yeux !',
  NewObject_10 = 'Je prépare les ombres de scène. Un bon spectacle a besoin d’un peu de nuit pour faire briller la lumière.',
}
for nom, texte in pairs(dialogues) do
  local replique = texte
  spindacafeetage1salle2[nom .. '_Action'] = function(personnage, activator)
    tourner_vers(personnage, activator or CH('PLAYER'))
    dire(personnage, 'Normal', replique)
    UI:ResetSpeaker()
  end
end

return spindacafeetage1salle2
