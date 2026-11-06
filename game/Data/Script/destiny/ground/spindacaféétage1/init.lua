-- Étage du café Spinda : coin calme et atelier de recyclage en préparation.
require 'origin.common'

local spindacafeetage1 = {}

local function activer(nom, rayon)
  local acteur = CH(nom)
  if acteur == nil then return end
  COMMON.CreateWalkArea(nom,
    math.max(0, acteur.Position.X - rayon),
    math.max(0, acteur.Position.Y - rayon), rayon * 2, rayon * 2)
  AI:EnableCharacterAI(acteur)
end

local function installer_escalier(map)
  if map == nil or map:FindObject('EscalierCafe') then return end
  local escalier = RogueEssence.Ground.GroundObject()
  escalier.EntName = 'EscalierCafe'
  escalier.Collider = RogueElements.Rect(268, 398, 64, 16)
  escalier:OnMapInit()
  map:AddObject(escalier)
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

function spindacafeetage1.Init(map)
  nommer('NewObject', 'Spinda')
  nommer('NewObject_1', 'Okéoké')
  nommer('NewObject_2', 'Qulbutoké')
  installer_escalier(map)
  activer('NewObject', 32)
  activer('NewObject_1', 28)
  activer('NewObject_2', 28)
end

function spindacafeetage1.Enter(map)
  GAME:FadeIn(30)
end

function spindacafeetage1.GameLoad(map)
  installer_escalier(map)
  GAME:FadeIn(30)
end

function spindacafeetage1.EscalierCafe_Action(obj, activator)
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Redescendre à l’accueil du café ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then aller_a(2) end
end

function spindacafeetage1.Update(map, time)
end

function spindacafeetage1.NewObject_Action(personnage, activator)
  dire(personnage, 'Happy', 'Cet étage est notre refuge quand l’accueil devient trop animé. On y prépare les réserves et les surprises.')
  UI:SetSpeaker(personnage)
  UI:BeginChoiceMenu('Souhaitez-vous que je vous guide ?', {
    'Redescendre à l’accueil', 'Aller à la salle de spectacle', 'Rester à l’étage',
  }, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  UI:ResetSpeaker()
  if choix == 1 then aller_a(2)
  elseif choix == 2 then aller_a(4) end
end

local function dialogue_atelier(okeoke, qulbutoque)
  dire(okeoke, 'Happy', 'Ici, nous rangeons les caisses du recyclage : rubans, graines, éclats et petits objets oubliés.')
  dire(qulbutoque, 'Normal', 'Chaque équipe laisse quelque chose derrière elle. Notre travail est de lui trouver une seconde vie.')
  dire(okeoke, 'Normal', 'Encore quelques étagères à monter, et l’atelier pourra recevoir les explorateurs.')
  UI:ResetSpeaker()
end

function spindacafeetage1.NewObject_1_Action(personnage, activator)
  dialogue_atelier(personnage, CH('NewObject_2'))
end

function spindacafeetage1.NewObject_2_Action(personnage, activator)
  dialogue_atelier(CH('NewObject_1'), personnage)
end

return spindacafeetage1
