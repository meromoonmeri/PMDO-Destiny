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
  cinematique.Dire(personnage, 'Determined', 'Le passage est grand ouvert. Entrons vite chercher ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'droite')
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
