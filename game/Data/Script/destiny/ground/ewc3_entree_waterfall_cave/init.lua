-- Entrée de la Grotte Verdoyante (ewc3_entree_waterfall_cave).
-- Gère l'état de la cascade :
--   * 1re visite : cascade fermée (L12/L17) -> ouverture synchronisée sur l'horloge
--     globale (L13/L18 sur 24 phases) -> passage ouvert (L14) ;
--   * Visites suivantes : cascade déjà ouverte (L14 visible dès Init).
--   * Triggers : SeuilDonjon (entrée 1F) et SortieRetourReverie (retour à Réverie).
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'

local ewc3 = {}
local sortie_en_cours = false

local LAYER_FERMEE = 12
local LAYER_OUVERTURE = 13
local LAYER_OUVERTE = 14
local LAYER_ECUME_FERMEE = 17
local LAYER_ECUME_OUVERTURE = 18
local TICKS_PAR_CASE = 480 -- FrameTick.FRAME_TICKS_PER_FRAME (120) * FrameLength (4)

local function layer_at(map, idx)
  if map == nil or map.Layers == nil then return nil end
  local ok, lyr = pcall(function() return map.Layers[idx] end)
  if ok and lyr ~= nil then return lyr end
  ok, lyr = pcall(function() return map.Layers:get_Item(idx) end)
  if ok and lyr ~= nil then return lyr end
  return nil
end

local function set_layer_visible(map, idx, vis)
  local lyr = layer_at(map, idx)
  if lyr ~= nil then
    lyr.Visible = vis
  end
end

local function appliquer_cascade_fermee(map)
  set_layer_visible(map, LAYER_FERMEE, true)
  set_layer_visible(map, LAYER_ECUME_FERMEE, true)
  set_layer_visible(map, LAYER_OUVERTURE, false)
  set_layer_visible(map, LAYER_ECUME_OUVERTURE, false)
  set_layer_visible(map, LAYER_OUVERTE, false)
end

local function appliquer_cascade_ouverture(map)
  set_layer_visible(map, LAYER_FERMEE, false)
  set_layer_visible(map, LAYER_ECUME_FERMEE, false)
  set_layer_visible(map, LAYER_OUVERTURE, true)
  set_layer_visible(map, LAYER_ECUME_OUVERTURE, true)
  set_layer_visible(map, LAYER_OUVERTE, false)
end

local function appliquer_cascade_ouverte(map)
  set_layer_visible(map, LAYER_FERMEE, false)
  set_layer_visible(map, LAYER_ECUME_FERMEE, false)
  set_layer_visible(map, LAYER_OUVERTURE, false)
  set_layer_visible(map, LAYER_ECUME_OUVERTURE, false)
  set_layer_visible(map, LAYER_OUVERTE, true)
end

local function phase24()
  local ok, ph = pcall(function()
    local t = tonumber(RogueEssence.Content.GraphicsManager.TotalFrameTick) or 0
    return math.floor(t / TICKS_PAR_CASE) % 24
  end)
  if ok and type(ph) == 'number' then return ph end
  return nil
end

local function installer_declencheur(map, nom, x, y, w, h)
  if map == nil or map:FindObject(nom) then return end
  local obj = RogueEssence.Ground.GroundObject()
  obj.EntName = nom
  obj.Collider = RogueElements.Rect(x, y, w, h)
  obj.Passable = true
  obj:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  obj:OnMapInit()
  map:AddObject(obj)
end

local function installer_declencheurs(map)
  installer_declencheur(map, 'SeuilDonjon', 368, 184, 40, 24)
  installer_declencheur(map, 'SortieRetourReverie', 320, 568, 144, 8)
end

local function creer_personnage(nom, espece, genre, surnom, x, y, dir)
  local existant = CH(nom)
  if existant ~= nil then GROUND:RemoveCharacter(nom) end
  local d = RogueEssence.Dungeon.CharData()
  d.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
  d.Nickname = surnom or ''
  local ch = GROUND:CreateCharacterFromCharData(nom, RogueEssence.Dungeon.Character(d), x, y, dir)
  AI:DisableCharacterAI(ch)
  ch:ReloadEvents()
  ch.CollisionDisabled = true
  return ch
end

local function synchroniser_cascade(map)
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.GrotteVerdoyanteOuverte then
    appliquer_cascade_ouverte(map)
  else
    appliquer_cascade_fermee(map)
  end
end

local function jouer_ouverture_cascade(map)
  -- TileLayer.Draw indexe L12/L13/L14 sur GraphicsManager.TotalFrameTick.
  -- Attendre la phase 0 (mod 24) assure L12[0] == L13[0] (0 octet d'écart),
  -- puis couper sur la phase 23 assure L13[23] == L14[11] sans clignotement.
  local ph = phase24()
  if ph ~= nil then
    local garde = 0
    while ph ~= 0 and garde < 96 do
      GAME:WaitFrames(1)
      garde = garde + 1
      local suivant = phase24()
      if suivant == ph and garde >= 8 then break end
      ph = suivant
    end
  end
  appliquer_cascade_ouverture(map)
  SOUND:PlayBattleSE('DUN_Waterfall')
  pcall(function() GROUND:MoveScreen(RogueEssence.Content.ScreenMover(0, 4, 80)) end)

  ph = phase24()
  local debut = ph
  if ph ~= nil then
    local frames = 0
    while frames < 96 do
      GAME:WaitFrames(1)
      frames = frames + 1
      local cur = phase24()
      if cur == 23 then break end
      if cur == debut and frames >= 12 then
        -- Double horloge figée (ex. doublure de test)
        GAME:WaitFrames(80)
        break
      end
    end
  else
    GAME:WaitFrames(92)
  end
  appliquer_cascade_ouverte(map)
end

local function cinematique_ouverture(map)
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(368, 544, Direction.Up)
  local lyra = nil
  local en_sauvetage = (SV.Destiny.AlerteShinx == 'a_secourir')

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 384, 544, Direction.Up)
  end
  if en_sauvetage then
    lyra = creer_personnage('Luxray_Ewc3', 'luxray', Gender.Female, 'Lyra', 400, 544, Direction.Up)
  end

  GAME:MoveCamera(0, 0, 1, true)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(30)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  local function tourner_direction_animee(acteur, dir)
    if acteur == nil then return end
    if GROUND.CharAnimateTurnTo ~= nil then
      pcall(function() GROUND:CharAnimateTurnTo(acteur, dir, 4) end)
    else
      GROUND:EntTurn(acteur, dir)
    end
  end

  local taches = {}
  if hero ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 384, 248, false, 2)
      tourner_direction_animee(hero, Direction.Up)
    end))
  end
  if partenaire ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:MoveToPosition(partenaire, 368, 260, false, 2)
      tourner_direction_animee(partenaire, Direction.Up)
    end))
  end
  if lyra ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GAME:WaitFrames(9)
      GROUND:MoveToPosition(lyra, 400, 260, false, 2)
      tourner_direction_animee(lyra, Direction.Up)
    end))
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end

  GAME:MoveCamera(384, 200, 25, false)
  GAME:WaitFrames(20)

  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Worried', 'Voilà la cascade dont parlait tout le monde… Mais le mur d’eau bouche complètement la falaise !', 'standard')
  end
  if lyra ~= nil then
    cinematique.Respirer(15)
    cinematique.Dire(lyra, 'Worried', 'Non… ' .. cinematique.NomColore('Nilo', 'shinx') .. ' a dû tomber juste derrière ce rideau d’eau ! Comment passer ?', 'droite')
  end
  UI:ResetSpeaker()
  GAME:WaitFrames(20)

  -- Tremblement / déclic mystérieux devant la cascade.
  SOUND:PlayBattleSE('EVT_CH05_Waterfall_Gem_Click')
  GAME:WaitFrames(12)
  SOUND:PlayBattleSE('EVT_Tower_Tremor_Weak')
  pcall(function() GROUND:MoveScreen(RogueEssence.Content.ScreenMover(0, 3, 24)) end)
  if partenaire ~= nil then cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim') end
  if lyra ~= nil then
    GAME:WaitFrames(5)
    cinematique.Emote(lyra, 'exclaim')
  end
  if hero ~= nil then
    GAME:WaitFrames(4)
    cinematique.Emote(hero, 'exclaim')
  end
  GAME:WaitFrames(25)

  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Surprised', 'Hein ?! Regardez l’eau… Elle commence à s’écarter !', 'standard')
  end
  UI:ResetSpeaker()

  jouer_ouverture_cascade(map)
  SV.Destiny.GrotteVerdoyanteOuverte = true
  GAME:WaitFrames(20)

  if lyra ~= nil then
    cinematique.Dire(lyra, 'Surprised', 'Un passage caché s’ouvre derrière la chute ! ' .. cinematique.NomColore('Nilo', 'shinx') .. ' est sûrement là-dedans !', 'droite')
  end
  if partenaire ~= nil then
    cinematique.Respirer(15)
    cinematique.Dire(partenaire, 'Determined', 'La voie est libre ! En avant dans la Grotte Verdoyante !', 'standard')
  end
  if lyra ~= nil then
    cinematique.Respirer(15)
    cinematique.Dire(lyra, 'Determined', 'Passez devant, je couvre vos arrières !', 'droite')
  end
  UI:ResetSpeaker()

  GAME:MoveCamera(0, 0, 20, true)
  if hero ~= nil then hero.CollisionDisabled = false end
  if lyra ~= nil then lyra.CollisionDisabled = false end
  if partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
end

local function tourner_anime(ent, dir, frames_par_45)
  if ent == nil then return end
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(ent, dir, frames_par_45 or 4) end)
  else
    pcall(function() GROUND:EntTurn(ent, dir) end)
  end
end

local function tourner_vers_cible(ent, cible, frames_par_45)
  if ent == nil or cible == nil then return end
  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(ent, cible, frames_par_45 or 4) end)
  else
    pcall(function() GROUND:CharTurnToChar(ent, cible) end)
  end
end

local function se_regarder(a, b, frames_par_45)
  if a == nil or b == nil then return end
  local f = frames_par_45 or 4
  tourner_vers_cible(a, b, f)
  GAME:WaitFrames(5)
  tourner_vers_cible(b, a, f)
end

local function cinematique_retour_echec(map, retour)
  SV.Destiny = SV.Destiny or {}
  local en_sauvetage = (SV.Destiny.AlerteShinx == 'a_secourir')
  local cause = (type(retour) == 'table' and retour.cause) or 'ko'
  local segment = (type(retour) == 'table' and retour.segment) or 0

  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(344, 256, Direction.Down)
  local lyra = nil
  if en_sauvetage then
    lyra = CH('Luxray_Ewc3') or creer_personnage('Luxray_Ewc3', 'luxray', Gender.Female, 'Lyra', 400, 224, Direction.Up)
  end

  GAME:CutsceneMode(true)
  UI:ResetSpeaker()

  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 368, 248, Direction.Down)
  end
  if partenaire ~= nil then
    GROUND:TeleportTo(partenaire, 344, 256, Direction.Down)
  end
  if lyra ~= nil then
    lyra.CollisionDisabled = true
    GROUND:TeleportTo(lyra, 400, 224, Direction.Up)
  end

  if cause ~= 'ko' then
    -- Repli volontaire : retour debout devant la cascade ouverte.
    GAME:MoveCamera(376, 232, 1, false)
    GAME:FadeIn(25)
    SOUND:PlayBGM('Lower Spring Cave.ogg', true)
    GAME:WaitFrames(15)
    if lyra ~= nil then
      tourner_vers_cible(lyra, hero or partenaire, 4)
      GAME:WaitFrames(10)
      cinematique.Dire(lyra, 'Worried', 'Vous voilà ressortis ! Si le passage est trop périlleux sans provisions, n’hésitez pas à redescendre au sud vers Réverie Town avant d’y retourner.', 'droite')
      UI:ResetSpeaker()
      GROUND:MoveToPosition(lyra, 400, 260, false, 1)
      tourner_anime(lyra, Direction.Up, 4)
    elseif partenaire ~= nil then
      tourner_vers_cible(partenaire, hero, 4)
      cinematique.Dire(partenaire, 'Worried', 'Mieux valait battre en retraite à temps… Reprenons des forces avant de retourner dans la Grotte Verdoyante.', 'standard')
      UI:ResetSpeaker()
    end
    GAME:MoveCamera(0, 0, 20, true)
    if hero ~= nil then hero.CollisionDisabled = false end
    if lyra ~= nil then lyra.CollisionDisabled = false end
    if partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
    GAME:CutsceneMode(false)
    return
  end

  -- K.O. dans le donjon : le duo gît au bord du bassin devant la cascade ouverte (aucun portrait éveillé avant Wake).
  if hero ~= nil then
    GROUND:CharSetAnim(hero, 'Laying', true)
  end
  if partenaire ~= nil then
    GROUND:CharSetAnim(partenaire, 'Laying', true)
  end

  GAME:MoveCamera(376, 228, 1, false)
  GAME:FadeIn(30)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:WaitFrames(25)

  if lyra ~= nil then
    cinematique.Emote(lyra, 'exclaim', 'EVT_Emote_Exclaim')
    tourner_vers_cible(lyra, hero or partenaire, 4)
    GAME:WaitFrames(25)

    -- Course verticale pure le long de x = 400 (32 px d'écart net avec le héros en Laying à x = 368).
    GROUND:MoveToPosition(lyra, 400, 248, false, 2)
    tourner_anime(lyra, Direction.Left, 4)
    GAME:WaitFrames(10)

    if segment == 1 then
      cinematique.Dire(lyra, 'Worried', 'Non !! Vous avez été projetés jusqu’à l’entrée… Ce rugissement au fond des vasques, c’était terrible ! Réveillez-vous, je vous en prie !', 'droite')
    else
      cinematique.Dire(lyra, 'Worried', 'Oh non !! Vous voilà revenus à bout de forces devant la cascade… Hé ! Est-ce que vous m’entendez ?!', 'droite')
    end
    UI:ResetSpeaker()
    GAME:WaitFrames(15)
  end

  -- Le duo reprend connaissance et se relève en léger décalage (5-6 frames).
  SOUND:PlayBattleSE('EVT_Emote_Sweating')
  if partenaire ~= nil then
    cinematique.Emote(partenaire, 'sweating', false)
  end
  if hero ~= nil then
    GAME:WaitFrames(5)
    cinematique.Emote(hero, 'sweating', false)
  end
  GAME:WaitFrames(30)

  if partenaire ~= nil then
    GROUND:CharSetAnim(partenaire, 'Wake', false)
  end
  if hero ~= nil then
    if partenaire ~= nil then GAME:WaitFrames(6) end
    GROUND:CharSetAnim(hero, 'Wake', false)
  end
  GAME:WaitFrames(36)
  if partenaire ~= nil then
    GROUND:CharEndAnim(partenaire)
    GROUND:EntTurn(partenaire, Direction.Down)
  end
  if hero ~= nil then
    GROUND:CharEndAnim(hero)
    GROUND:EntTurn(hero, Direction.Down)
  end
  GAME:WaitFrames(15)

  if lyra ~= nil then
    if partenaire ~= nil then
      tourner_vers_cible(partenaire, lyra, 4)
    end
    if hero ~= nil then
      if partenaire ~= nil then GAME:WaitFrames(5) end
      tourner_vers_cible(hero, lyra, 4)
    end
    GAME:WaitFrames(10)

    if partenaire ~= nil then
      if segment == 1 then
        cinematique.Dire(partenaire, 'Pain', 'Aïe… ' .. cinematique.NomEspece('garchomp', 'Carchacrok') .. ' est d’une force redoutable… Pardon, Lyra, on a dû céder si près de ' .. cinematique.NomColore('Nilo', 'shinx') .. '…', 'standard')
      else
        cinematique.Dire(partenaire, 'Pain', 'Aïe… la grotte est plus rude qu’elle n’en a l’air… Désolé, Lyra, on s’est fait mettre K.O. avant d’atteindre ' .. cinematique.NomColore('Nilo', 'shinx') .. '…', 'standard')
      end
      cinematique.Respirer(15)
    end

    cinematique.Dire(lyra, 'Worried', 'Ne vous excusez surtout pas ! Voir que vous êtes sains et saufs me soulage déjà tellement…', 'droite')
    cinematique.Respirer(15)
    cinematique.Dire(lyra, 'Determined', 'Reprenez votre souffle ici. Si vos réserves sont épuisées, redescendez au sud vers Réverie Town pour vous préparer avant de repartir chercher ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'droite')

    if partenaire ~= nil then
      cinematique.Respirer(15)
      se_regarder(hero, partenaire, 4)
      GAME:WaitFrames(10)
      tourner_vers_cible(partenaire, lyra, 4)
      if hero ~= nil then
        GAME:WaitFrames(5)
        tourner_vers_cible(hero, lyra, 4)
      end
      cinematique.Dire(partenaire, 'Determined', 'Merci, Lyra ! Pas question d’abandonner maintenant : dès qu’on sera prêts, on retournera jusqu’au fond de la Grotte Verdoyante !', 'standard')
    end
    UI:ResetSpeaker()
    GAME:WaitFrames(10)

    -- Lyra reprend son poste de garde devant la cascade ouverte (400, 260, Direction.Up).
    GROUND:MoveToPosition(lyra, 400, 260, false, 1)
    tourner_anime(lyra, Direction.Up, 4)
  else
    se_regarder(hero, partenaire, 4)
    GAME:WaitFrames(10)
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Pain', 'Ouf… ma tête… On a fini K.O. dans la Grotte Verdoyante, mais on a réussi à ressortir jusqu’à la cascade.', 'standard')
      cinematique.Respirer(15)
      cinematique.Dire(partenaire, 'Determined', 'Vérifions notre sac avant d’y retourner, ou rentrons au sud vers Réverie Town faire le plein de provisions !', 'standard')
      UI:ResetSpeaker()
    end
  end

  GAME:MoveCamera(0, 0, 20, true)
  if hero ~= nil then hero.CollisionDisabled = false end
  if lyra ~= nil then lyra.CollisionDisabled = false end
  if partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
end

function ewc3.Init(map)
  sortie_en_cours = false
  SV.Destiny = SV.Destiny or {}
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_declencheurs(map)
  synchroniser_cascade(map)
  if SV.Destiny.GrotteVerdoyanteOuverte and SV.Destiny.AlerteShinx == 'a_secourir' then
    local lyra = creer_personnage('Luxray_Ewc3', 'luxray', Gender.Female, 'Lyra', 400, 260, Direction.Up)
    lyra.CollisionDisabled = false
  end
end

function ewc3.Enter(map)
  sortie_en_cours = false
  SV.Destiny = SV.Destiny or {}
  synchroniser_cascade(map)
  if not SV.Destiny.GrotteVerdoyanteOuverte then
    cinematique_ouverture(map)
    return
  end
  if SV.Destiny.GrotteVerdoyanteRetourEchec ~= nil then
    local retour = SV.Destiny.GrotteVerdoyanteRetourEchec
    SV.Destiny.GrotteVerdoyanteRetourEchec = nil
    cinematique_retour_echec(map, retour)
    return
  end
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(368, 544, Direction.Up)
  if hero ~= nil then
    GROUND:TeleportTo(hero, 384, 544, Direction.Up)
  end
  GAME:MoveCamera(0, 0, 1, true)
  GAME:FadeIn(20)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  if partenaire ~= nil then
    equipe_scene.Suivre(partenaire, hero)
  end
end

function ewc3.GameLoad(map)
  sortie_en_cours = false
  SV.Destiny = SV.Destiny or {}
  installer_declencheurs(map)
  synchroniser_cascade(map)
  GAME:MoveCamera(0, 0, 1, true)
  GAME:FadeIn(20)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
end

function ewc3.Update(map, time) end

function ewc3.Luxray_Ewc3_Action(personnage, activator)
  if personnage == nil then return end
  pcall(function() GROUND:CharTurnToCharAnimated(personnage, activator or CH('PLAYER'), 4) end)
  if SV.Destiny and SV.Destiny.GrotteVerdoyanteDernierKO then
    cinematique.Dire(personnage, 'Worried', 'Ne forcez pas si vous êtes encore sonnés ! Le sentier au sud ramène à Réverie Town pour refaire le plein de provisions.', 'droite')
    cinematique.Respirer(15)
    cinematique.Dire(personnage, 'Determined', 'Dès que vous vous sentirez d’attaque, le passage derrière la cascade vous attend pour sauver ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'droite')
  else
    cinematique.Dire(personnage, 'Determined', 'Le passage est grand ouvert. Entrons vite chercher ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'droite')
  end
  UI:ResetSpeaker()
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(personnage, Direction.Up, 4) end)
  else
    pcall(function() GROUND:EntTurn(personnage, Direction.Up) end)
  end
end

function ewc3.SeuilDonjon_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Entrer dans la Grotte Verdoyante ?', true)
  UI:WaitForChoice()
  if not UI:ChoiceResult() then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationReverie = true
  SV.Destiny.GrotteVerdoyanteDernierKO = nil
  SOUND:FadeOutBGM(20)
  GAME:FadeOut(false, 20)
  GAME:EnterDungeon('grotte_verdoyante', 0, 0, 0, RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
end

function ewc3.SortieRetourReverie_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Retourner à Réverie Town ?', true)
  UI:WaitForChoice()
  if not UI:ChoiceResult() then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationReverie = nil
  SV.Destiny.ArriveeVille = 'batiment'
  SV.Destiny.RetourBatimentX = 1552
  SV.Destiny.RetourBatimentY = 1600
  if SV.Destiny.AlerteShinx == 'a_secourir' then
    SV.Destiny.LuxrayAttente = 'sortie'
  end
  SOUND:FadeOutBGM(20)
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

return ewc3
