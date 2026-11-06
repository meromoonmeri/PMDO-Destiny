-- Salle de spectacle du café Spinda : artistes et habitués sérialisés.
require 'origin.common'

local spindacafeetage1salle2 = {}

local function activer(nom, rayon)
  local acteur = CH(nom)
  if acteur == nil then return end
  COMMON.CreateWalkArea(nom,
    math.max(0, acteur.Position.X - rayon),
    math.max(0, acteur.Position.Y - rayon), rayon * 2, rayon * 2)
  AI:EnableCharacterAI(acteur)
end

local function installer_porte(map)
  if map == nil or map:FindObject('PorteSalleCafe') then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteSalleCafe'
  porte.Collider = RogueElements.Rect(24, 204, 16, 32)
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

function spindacafeetage1salle2.Init(map)
  nommer('NewObject', 'Mime Jr.')
  nommer('NewObject_1', 'Rondoudou')
  nommer('NewObject_2', 'Négapi')
  nommer('NewObject_3', 'Magirêve')
  nommer('NewObject_4', 'Goupilou')
  nommer('NewObject_5', 'Nidoran♀')
  nommer('NewObject_6', 'Nidoran♂')
  nommer('NewObject_7', 'Mimiqui')
  nommer('NewObject_8', 'Pachirisu')
  nommer('NewObject_9', 'Posipi')
  nommer('NewObject_10', 'Branette')
  installer_porte(map)
  for i = 0, 10 do
    local nom = i == 0 and 'NewObject' or ('NewObject_' .. i)
    activer(nom, 36)
  end
end

function spindacafeetage1salle2.Enter(map)
  GAME:FadeIn(30)
end

function spindacafeetage1salle2.GameLoad(map)
  installer_porte(map)
  GAME:FadeIn(30)
end

function spindacafeetage1salle2.PorteSalleCafe_Action(obj, activator)
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Retourner à l’accueil du café ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then aller_a(2) end
end

function spindacafeetage1salle2.Update(map, time)
end

function spindacafeetage1salle2.NewObject_Action(personnage, activator)
  dire(personnage, 'Happy', 'Je répète mon numéro de mime. Le mur invisible est juste là… ne le traversez pas trop vite.')
  dire(CH('NewObject_1'), 'Happy', 'Et quand je chanterai, toute la salle devra rester éveillée jusqu’au dernier refrain !')
  UI:SetSpeaker(personnage)
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
  dire(personnage, 'Happy', 'Une chanson douce peut reposer une équipe entière. Enfin… si personne ne s’endort avant la fin.')
  dire(CH('NewObject'), 'Normal', 'Je tiendrai le rideau. Invisible, bien entendu.')
  UI:ResetSpeaker()
end

local dialogues = {
  NewObject_2 = 'Plusle et moi préparons un numéro d’étincelles synchronisées. Réverie Town va briller !',
  NewObject_3 = 'Les récits de donjon prennent une autre couleur sous les lumières de cette salle.',
  NewObject_4 = 'Je cherche un accessoire disparu avant le spectacle. Dans un café, même les ombres ont des cachettes.',
  NewObject_5 = 'Nous venons écouter les histoires des explorateurs. Certaines valent tous les trésors.',
  NewObject_6 = 'Je garde nos places pendant qu’elle choisit les boissons. Le spectacle commence toujours trop tôt pour les retardataires.',
  NewObject_7 = 'Mon déguisement est prêt. J’espère que le public aimera autant le mystère que les chansons.',
  NewObject_8 = 'Je répète mes applaudissements. Les artistes donnent le meilleur quand la salle répond.',
  NewObject_9 = 'Minun compte les temps, je lance la première étincelle. Ne clignez pas des yeux !',
  NewObject_10 = 'Je prépare les ombres de scène. Un bon spectacle a besoin d’un peu de nuit pour faire briller la lumière.',
}
for nom, texte in pairs(dialogues) do
  local replique = texte
  spindacafeetage1salle2[nom .. '_Action'] = function(personnage, activator)
    dire(personnage, 'Normal', replique)
    UI:ResetSpeaker()
  end
end

return spindacafeetage1salle2
