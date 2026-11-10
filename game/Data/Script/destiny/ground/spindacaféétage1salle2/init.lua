-- Salle de spectacle du café Spinda : artistes sur scène et habitués attablés.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local spindacafeetage1salle2 = {}
local transition_cafe_en_cours = false

local function fixer_poste(nom, dir)
  local acteur = CH(nom)
  if acteur == nil then return end
  AI:DisableCharacterAI(acteur)
  if dir ~= nil then
    pcall(function() GROUND:EntTurn(acteur, dir) end)
  end
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

local function tourner_dir(acteur, dir)
  if acteur == nil or dir == nil then return end
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(acteur, dir, 4) end)
  elseif GROUND.EntTurn ~= nil then
    pcall(function() GROUND:EntTurn(acteur, dir) end)
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

local orientations_fixes = {
  NewObject = Direction.Down,                      -- Pipo sur scène
  NewObject_1 = Direction.Down,                    -- Asa sur scène
  NewObject_2 = Direction.DownRight or Direction.Down, -- Mina, table gauche
  NewObject_9 = Direction.UpLeft or Direction.Left,    -- Pico, table gauche
  NewObject_8 = Direction.UpRight or Direction.Right,  -- Pistache, table gauche
  NewObject_3 = Direction.Down,                    -- Mirabelle, table basse
  NewObject_7 = Direction.Right,                   -- Mimi, table basse
  NewObject_10 = Direction.Left,                   -- Brume, table basse
  NewObject_4 = Direction.Down,                    -- Nox, table droite
  NewObject_6 = Direction.Right,                   -- Rémi, table droite
  NewObject_5 = Direction.Left,                    -- Lila, table droite
}

-- Les artistes restent sur scène et tous les habitués restent assis côte à
-- côte à leurs tables, sans vagabonder au milieu des tabourets.
local function placer_salle()
  for nom, dir in pairs(orientations_fixes) do
    fixer_poste(nom, dir)
  end
end

function spindacafeetage1salle2.Init(map)
  synchroniser_zone()
  nommer_personnel()
  installer_porte(map)
  placer_salle()
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

function spindacafeetage1salle2.GameLoad(map)
  synchroniser_zone()
  nommer_personnel()
  placer_salle()
  suivi_interieurs.Activer(map)
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
  tourner_dir(personnage, Direction.Down)
  tourner_dir(asa, Direction.Down)
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
  tourner_dir(personnage, Direction.Down)
  tourner_dir(pipo, Direction.Down)
end

local function dialogue_plusle_minun(mina, pico, premier_mina, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(mina, joueur)
  tourner_vers(pico, joueur)
  if premier_mina then
    dire(mina, 'Happy', 'Pico et moi préparons un numéro d’étincelles synchronisées. Réverie Town va briller !')
    tourner_vers(pico, mina)
    tourner_vers(mina, pico)
    dire(pico, 'Happy', 'Dès que tu donnes le signal, je lance la première étincelle !')
  else
    dire(pico, 'Happy', 'Mina compte les temps, je lance la première étincelle. Ne clignez pas des yeux !')
    tourner_vers(mina, pico)
    tourner_vers(pico, mina)
    dire(mina, 'Happy', 'Et Pistache donne le rythme des applaudissements juste à côté !')
  end
  UI:ResetSpeaker()
  tourner_dir(mina, orientations_fixes.NewObject_2)
  tourner_dir(pico, orientations_fixes.NewObject_9)
end

function spindacafeetage1salle2.NewObject_2_Action(personnage, activator)
  dialogue_plusle_minun(personnage, CH('NewObject_9'), true, activator)
end

function spindacafeetage1salle2.NewObject_9_Action(personnage, activator)
  dialogue_plusle_minun(CH('NewObject_2'), personnage, false, activator)
end

local function dialogue_nidoran(lila, remi, premier_lila, activator)
  local joueur = activator or CH('PLAYER')
  tourner_vers(lila, joueur)
  tourner_vers(remi, joueur)
  if premier_lila then
    dire(lila, 'Happy', 'Nous venons écouter les histoires des explorateurs. Certaines valent tous les trésors.')
    tourner_vers(remi, lila)
    tourner_vers(lila, remi)
    dire(remi, 'Normal', 'Et je garde bien nos deux places jusqu’au lever du rideau !')
  else
    dire(remi, 'Normal', 'Je garde nos places pendant qu’elle choisit les boissons. Le spectacle commence toujours trop tôt pour les retardataires.')
    tourner_vers(lila, remi)
    tourner_vers(remi, lila)
    dire(lila, 'Happy', 'Merci, Rémi ! Promis, je ne tarde pas dès que le service rouvre.')
  end
  UI:ResetSpeaker()
  tourner_dir(lila, orientations_fixes.NewObject_5)
  tourner_dir(remi, orientations_fixes.NewObject_6)
end

function spindacafeetage1salle2.NewObject_5_Action(personnage, activator)
  dialogue_nidoran(personnage, CH('NewObject_6'), true, activator)
end

function spindacafeetage1salle2.NewObject_6_Action(personnage, activator)
  dialogue_nidoran(CH('NewObject_5'), personnage, false, activator)
end

local dialogues = {
  NewObject_3 = 'Les récits de donjon prennent une autre couleur sous les lumières de cette salle.',
  NewObject_4 = 'Je cherche un accessoire disparu avant le spectacle. Dans un café, même les ombres ont des cachettes.',
  NewObject_7 = 'Mon déguisement est prêt. J’espère que le public aimera autant le mystère que les chansons.',
  NewObject_8 = 'Je répète mes applaudissements avec Mina et Pico. Les artistes donnent le meilleur quand la table suit la cadence.',
  NewObject_10 = 'Je prépare les ombres de scène. Un bon spectacle a besoin d’un peu de nuit pour faire briller la lumière.',
}
for nom, texte in pairs(dialogues) do
  local nom_ent, replique = nom, texte
  spindacafeetage1salle2[nom .. '_Action'] = function(personnage, activator)
    tourner_vers(personnage, activator or CH('PLAYER'))
    dire(personnage, 'Normal', replique)
    UI:ResetSpeaker()
    tourner_dir(personnage, orientations_fixes[nom_ent])
  end
end

return spindacafeetage1salle2
