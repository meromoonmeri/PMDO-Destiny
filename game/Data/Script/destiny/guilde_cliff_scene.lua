-- Scène partagée des quatre variantes de la falaise de la Grande Guilde.
-- Gère l'ouverture animée de la porte (BatimentGuilde / BatimentGuildeOuverte),
-- le garde pré-sauvetage et l'enrôlement officiel après le sauvetage de Nilo.
require 'origin.common'
local cinematique = require 'destiny.cinematique'
local equipe_scene = require 'destiny.equipe_scene'

local scene = {}
local interaction_en_cours = false

local function partenaire_de(hero)
  if hero == nil or GAME == nil or GAME.GetPlayerPartyCount == nil then return nil end
  if GAME:GetPlayerPartyCount() <= 1 then return nil end
  local partenaire = CH('Teammate1')
  if partenaire ~= nil then return partenaire end
  local py = math.min(hero.Position.Y + 24, 472)
  return equipe_scene.Partenaire(hero.Position.X, py, hero.Direction)
end

local function retour_au_joueur(hero, partenaire)
  UI:ResetSpeaker()
  if hero ~= nil then hero.CollisionDisabled = false end
  if partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:MoveCamera(0, 0, 1, true)
  GAME:CutsceneMode(false)
end

local function definir_porte_ouverte(map, ouverte)
  if map == nil or map.Decorations == nil then return end
  if luanet == nil or luanet.each == nil then return end
  for deco in luanet.each(map.Decorations) do
    if deco.Name == 'BatimentGuilde' then
      deco.Visible = not ouverte
    elseif deco.Name == 'BatimentGuildeOuverte' then
      deco.Visible = ouverte
    end
  end
end

local function ouvrir_porte(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  definir_porte_ouverte(map, true)
end

local function fermer_porte(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  definir_porte_ouverte(map, false)
end

local function creer_figurant(nom, espece, genre, surnom, x, y, dir)
  local existant = CH(nom)
  if existant ~= nil then
    GROUND:TeleportTo(existant, x, y, dir or Direction.Down)
    if existant.Data ~= nil and surnom ~= nil then existant.Data.Nickname = surnom end
    return existant
  end
  local chara_data = RogueEssence.Dungeon.CharData()
  chara_data.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
  local acteur = RogueEssence.Ground.GroundChar(
    chara_data,
    RogueElements.Loc(x, y),
    dir or Direction.Down,
    nom
  )
  if acteur.Data ~= nil and surnom ~= nil then acteur.Data.Nickname = surnom end
  pcall(function() acteur:ReloadEvents() end)
  GAME:GetCurrentGround():AddMapChar(acteur)
  return acteur
end

local function retirer_figurant(nom)
  if CH(nom) ~= nil then
    pcall(function() GROUND:RemoveCharacter(nom) end)
  end
end

local function installer_capteur(map, nom, x, y, w, h)
  if map == nil or map:FindObject(nom) then return end
  local obj = RogueEssence.Ground.GroundObject()
  obj.EntName = nom
  obj.Collider = RogueElements.Rect(x, y, w, h)
  obj.Passable = false
  obj:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  obj:OnMapInit()
  map:AddObject(obj)
end

local function pre_enrolement_pret()
  return SV ~= nil and SV.Destiny ~= nil
    and SV.Destiny.AlerteShinx == 'termine'
    and SV.Destiny.EnrolementGuilde ~= 'termine'
end

local function installer_comite_accueil(map)
  if map == nil then return end
  if pre_enrolement_pret() then
    installer_capteur(map, 'ZoneAccueilGuilde', 160, 356, 160, 16)
    creer_figurant('Guilde_Chatot', 'chatot', Gender.Male, 'Pijako', 232, 300, Direction.Down)
    creer_figurant('Guilde_Sunflora', 'sunflora', Gender.Female, 'Héliatronc', 188, 292, Direction.Down)
    creer_figurant('Guilde_Loudred', 'loudred', Gender.Male, 'Ramboum', 276, 292, Direction.Down)
  else
    if map:FindObject('ZoneAccueilGuilde') then GROUND:RemoveObject('ZoneAccueilGuilde') end
    retirer_figurant('Guilde_Chatot')
    retirer_figurant('Guilde_Sunflora')
    retirer_figurant('Guilde_Loudred')
  end
  retirer_figurant('Guilde_Wigglytuff')
end

function scene.Init(map)
  interaction_en_cours = false
  definir_porte_ouverte(map, false)
  installer_capteur(map, 'PorteGuilde', 224, 256, 32, 16)
  installer_comite_accueil(map)
end

local function jouer_enrolement(map, hero)
  local partenaire = partenaire_de(hero)
  GAME:CutsceneMode(true)
  if hero ~= nil then hero.CollisionDisabled = true end
  if partenaire ~= nil then AI:DisableCharacterAI(partenaire) end

  local chatot = creer_figurant('Guilde_Chatot', 'chatot', Gender.Male, 'Pijako', 232, 300, Direction.Down)
  local sunflora = creer_figurant('Guilde_Sunflora', 'sunflora', Gender.Female, 'Héliatronc', 188, 292, Direction.Down)
  local loudred = creer_figurant('Guilde_Loudred', 'loudred', Gender.Male, 'Ramboum', 276, 292, Direction.Down)

  if hero ~= nil then GROUND:TeleportTo(hero, 232, 344, Direction.Up) end
  if partenaire ~= nil then GROUND:TeleportTo(partenaire, 208, 352, Direction.Up) end
  GAME:MoveCamera(240, 296, 1, false)
  GAME:WaitFrames(12)

  pcall(function() GROUND:CharSetEmote(chatot, 'exclaim', 1) end)
  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GAME:WaitFrames(20)
  cinematique.Dire(chatot, 'Surprised', 'Oh ! Mais vous voilà enfin sur la falaise ! La nouvelle a déjà traversé tout Réverie Town !', 'standard')
  cinematique.Dire(sunflora, 'Happy', 'Douce mère nature ! C’est bien la jeune équipe qui a sauvé le petit Nilo jusque dans la Grotte Verdoyante !', 'gauche')
  cinematique.Dire(loudred, 'Angry', 'MOUAIS ! Tenir tête à un Carchacrok, c’est pas mal pour des recrues… MAIS ICI ON FILE DROIT !', 'droite')
  cinematique.Dire(chatot, 'Normal', 'Un peu de tenue, Ramboum ! Maître Grodoudou a tenu à vous accueillir en personne.', 'standard')

  GAME:WaitFrames(10)
  ouvrir_porte(map)
  GAME:WaitFrames(22)

  local wigglytuff = creer_figurant('Guilde_Wigglytuff', 'wigglytuff', Gender.Male, 'Grodoudou', 232, 260, Direction.Down)
  GROUND:MoveInDirection(wigglytuff, Direction.Down, 16, false, 1)
  pcall(function() GROUND:CharSetAnim(wigglytuff, 'Hop', false) end)
  GAME:WaitFrames(18)

  cinematique.Dire(wigglytuff, 'Happy', 'Yoom-tah ! Bienvenue à ma fabuleuse Guilde, les amis-amis !', 'standard')
  cinematique.Dire(wigglytuff, 'Normal', 'Vous avez écouté la détresse d’une maman, bravé une sombre caverne et protégé un tout petit cœur jusqu’au bout.', 'standard')
  cinematique.Dire(wigglytuff, 'Joyous', 'Je vous proclame officiellement ÉQUIPE APPRENTIE DE LA GRANDE GUILDE ! Hourra !', 'standard')

  pcall(function() GROUND:CharSetAnim(sunflora, 'Hop', false) end)
  pcall(function() GROUND:CharSetAnim(loudred, 'Hop', false) end)
  pcall(function() GROUND:CharSetEmote(sunflora, 'happy', 1) end)
  pcall(function() GROUND:CharSetEmote(loudred, 'happy', 1) end)
  GAME:WaitFrames(24)

  cinematique.Dire(wigglytuff, 'Happy', 'Et comme on n’explore jamais le ventre vide… acceptez mon trésor préféré ! Amis-amis !', 'standard')
  UI:ResetSpeaker()
  if hero ~= nil then
    COMMON.GiftItem(hero, RogueEssence.Dungeon.InvItem('food_apple_perfect'))
  end

  cinematique.Dire(chatot, 'Sigh', 'Garde-manger mis à part… Nos dortoirs intérieurs sont encore en plein aménagement pour accueillir toutes les nouvelles recrues.', 'standard')
  cinematique.Dire(chatot, 'Happy', 'En attendant leur ouverture complète, entraînez-vous librement à Réverie Town et revenez frapper à notre grande porte quand vous voudrez !', 'standard')
  cinematique.Dire(wigglytuff, 'Happy', 'À très bientôt sous notre grand arbre, jeunes explorateurs ! Yoom-tah !', 'standard')

  UI:ResetSpeaker()
  GAME:FadeOut(false, 18)
  retirer_figurant('Guilde_Wigglytuff')
  retirer_figurant('Guilde_Chatot')
  retirer_figurant('Guilde_Sunflora')
  retirer_figurant('Guilde_Loudred')
  definir_porte_ouverte(map, false)
  if map ~= nil and map:FindObject('ZoneAccueilGuilde') then
    GROUND:RemoveObject('ZoneAccueilGuilde')
  end
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.EnrolementGuilde = 'termine'
  GAME:FadeIn(18)
  retour_au_joueur(hero, partenaire)
end

function scene.ZoneAccueilGuilde_Touch(map, obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if interaction_en_cours then return end
  if not pre_enrolement_pret() then return end
  interaction_en_cours = true
  jouer_enrolement(map, activator)
  interaction_en_cours = false
end

function scene.PorteGuilde_Touch(map, obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if interaction_en_cours then return end
  interaction_en_cours = true

  if pre_enrolement_pret() then
    jouer_enrolement(map, activator)
    interaction_en_cours = false
    return
  end

  local hero = CH('PLAYER') or activator
  local partenaire = partenaire_de(hero)
  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:EntTurn(hero, Direction.Up)
  end
  if partenaire ~= nil then AI:DisableCharacterAI(partenaire) end

  ouvrir_porte(map)
  GAME:WaitFrames(18)
  local chatot = creer_figurant('Guilde_Chatot', 'chatot', Gender.Male, 'Pijako', 232, 260, Direction.Down)
  GAME:WaitFrames(10)

  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.EnrolementGuilde == 'termine' then
    cinematique.Dire(chatot, 'Happy', 'Toujours prêts pour l’aventure, jeunes apprentis ! Nos salles intérieures achèvent encore leurs derniers travaux, mais le grand plateau reste votre repaire.', 'standard')
  else
    cinematique.Dire(chatot, 'Normal', 'Halte ! La Grande Guilde n’ouvre ses rangs qu’aux équipes ayant déjà fait leurs preuves à Réverie Town. Revenez quand vous aurez accompli un vrai sauvetage !', 'standard')
  end

  UI:ResetSpeaker()
  GAME:WaitFrames(8)
  retirer_figurant('Guilde_Chatot')
  fermer_porte(map)
  if hero ~= nil then GROUND:TeleportTo(hero, 232, 282, Direction.Up) end
  if partenaire ~= nil then GROUND:TeleportTo(partenaire, 208, 290, Direction.Up) end
  GAME:WaitFrames(10)
  retour_au_joueur(hero, partenaire)
  interaction_en_cours = false
end

return scene
