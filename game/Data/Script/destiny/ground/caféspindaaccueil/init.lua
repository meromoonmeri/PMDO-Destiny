-- Accueil du café Spinda : habitants sérialisés de la carte town02.
-- Les dialogues sont originaux Destiny ; les services avancés du café
-- restent à brancher sur les menus natifs dans une tranche ultérieure.
require 'origin.common'

local caféspindaaccueil = {}

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
  if map == nil or map:FindObject('PorteSortieCafe') then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteSortieCafe'
  porte.Collider = RogueElements.Rect(268, 374, 64, 16)
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

function caféspindaaccueil.Init(map)
  nommer('NewObject_13', 'Goinfrex')
  nommer('Pompot', 'Pohm')
  nommer('Qulbutoqué', 'Qulbutoké')
  nommer('Okéoké', 'Okéoké')
  installer_sortie(map)
  activer('Spinda', 20)
  activer('MrMimeJunior', 20)
  activer('Kirlia', 20)
  activer('NewObject_13', 36)
  activer('Pompot', 36)
  activer('Qulbutoqué', 28)
  activer('Okéoké', 28)
end

function caféspindaaccueil.Enter(map)
  GAME:FadeIn(30)
end

function caféspindaaccueil.GameLoad(map)
  installer_sortie(map)
  GAME:FadeIn(30)
end

function caféspindaaccueil.PorteSortieCafe_Action(obj, activator)
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Sortir du café et revenir à Réverie Town ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.ArriveeVille = 'cafe'
    aller_a(0)
  end
end

function caféspindaaccueil.Update(map, time)
end

function caféspindaaccueil.Spinda_Action(personnage, activator)
  dire(personnage, 'Happy', 'Bienvenue au café Spinda ! Ici, les explorateurs reprennent des forces entre deux récits de mission.')
  dire(CH('MrMimeJunior'), 'Happy', 'Je prépare les verres sans dire un mot. Le spectacle commence dès le comptoir !')
  dire(CH('Kirlia'), 'Normal', 'Et moi, j’écoute les équipes. Certaines histoires commencent par une simple boisson partagée.')
  dire(personnage, 'Normal', 'Installez-vous. L’étage est plus calme, et la salle voisine accueille nos petits spectacles.')
  UI:SetSpeaker(personnage)
  UI:BeginChoiceMenu('Souhaitez-vous que je vous guide, ou faire une sieste jusqu’à demain ?', {
    'Monter à l’étage', 'Aller à la salle de spectacle', 'Faire une sieste', 'Rester à l’accueil',
  }, 1, 4)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == 3 then
    UI:WaitShowDialogue('Installez-vous dans un coin tranquille. Demain, les Kecleon auront renouvelé leurs étals.')
    UI:ResetSpeaker()
    GAME:FadeOut(false, 60)
    GAME:WaitFrames(90)
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
    SV.Destiny.StocksKecleon = {}
    GAME:FadeIn(60)
    UI:ResetSpeaker()
    UI:WaitShowDialogue('[i]Une nouvelle journée commence à Réverie Town…')
    return
  end
  UI:ResetSpeaker()
  if choix == 1 then aller_a(3)
  elseif choix == 2 then aller_a(4) end
end

function caféspindaaccueil.MrMimeJunior_Action(personnage, activator)
  dire(personnage, 'Happy', 'Je mime le verseur parfait : pas une goutte imaginaire ne tombe à côté.')
  dire(CH('Spinda'), 'Happy', 'Et pendant ce temps, je sers les vraies boissons. Nous formons une belle équipe !')
  UI:ResetSpeaker()
end

function caféspindaaccueil.Kirlia_Action(personnage, activator)
  dire(personnage, 'Normal', 'Les voyageurs laissent parfois une émotion derrière eux. Je la transforme en conseil pour l’équipe suivante.')
  UI:ResetSpeaker()
end

local function dialogue_recyclage(okéoké, qulbutoqué)
  dire(okéoké, 'Happy', 'Nous trions les petits trésors que les explorateurs ne savent plus où ranger.')
  dire(qulbutoqué, 'Normal', 'Rien ne se perd au café : un objet délaissé peut devenir une surprise pour quelqu’un d’autre.')
  dire(okéoké, 'Normal', 'Notre atelier de recyclage ouvrira quand toutes les caisses seront enfin rangées.')
  UI:ResetSpeaker()
end

caféspindaaccueil['Qulbutoqué_Action'] = function(personnage, activator)
  dialogue_recyclage(CH('Okéoké'), personnage)
end

caféspindaaccueil['Okéoké_Action'] = function(personnage, activator)
  dialogue_recyclage(personnage, CH('Qulbutoqué'))
end

function caféspindaaccueil.NewObject_13_Action(personnage, activator)
  dire(personnage, 'Happy', 'Je goûte chaque nouveauté du comptoir. Pour le travail, évidemment. Uniquement pour le travail.')
  UI:ResetSpeaker()
end

function caféspindaaccueil.Pompot_Action(personnage, activator)
  dire(personnage, 'Normal', 'Après Lost Wood, même une chaise tranquille ressemble à un trésor. Réverie Town sait accueillir les pattes fatiguées.')
  UI:ResetSpeaker()
end

return caféspindaaccueil
