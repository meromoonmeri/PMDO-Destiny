-- Salle des vasques (9e étage de la Grotte Verdoyante : fgv1_fin_grotte_vasques, 480x360).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : découverte de Nilo endormi, réveil, panique, double flash blanc et arrivée de Carchacrok
--   * PreBattle(true)  : revanche abrégée après une défaite au 9F
--   * PostBattle()     : défaite de Carchacrok, joie de Nilo, retour vers la célébration à Réverie Town
--   * EmptyReturn()    : visites paisibles après le sauvetage
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'

local fgv1 = {}

local function creer_acteur(nom, espece, genre, surnom, x, y, dir)
  local existant = CH(nom)
  if existant ~= nil then GROUND:RemoveCharacter(nom) end
  local d = RogueEssence.Dungeon.CharData()
  d.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
  d.Nickname = surnom or ''
  local ch = GROUND:CreateCharacterFromCharData(nom, RogueEssence.Dungeon.Character(d), x, y, dir)
  AI:DisableCharacterAI(ch)
  ch.CollisionDisabled = true
  return ch
end

local function flash_blanc()
  local ok = pcall(function()
    local center = GAME:GetCameraCenter()
    local emitter = RogueEssence.Content.FlashEmitter()
    emitter.FadeInTime = 2
    emitter.HoldTime = 2
    emitter.FadeOutTime = 2
    emitter.StartColor = Color(0, 0, 0, 0)
    emitter.Layer = DrawLayer.Top
    emitter.Anim = RogueEssence.Content.BGAnimData('White', 0)
    GROUND:PlayVFX(emitter, center.X, center.Y)
  end)
  if not ok then
    pcall(function() GROUND:MoveScreen(RogueEssence.Content.ScreenMover(0, 3, 6)) end)
  end
  SOUND:PlayBattleSE('EVT_Battle_Flash')
end

local function finir_vers_reverie()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationReverie = nil
  SV.Destiny.ArriveeVille = 'batiment'
  SV.Destiny.RetourBatimentX = 1552
  SV.Destiny.RetourBatimentY = 1600
  COMMON.EndDungeonDay(RogueEssence.Data.GameProgress.ResultType.Cleared, 'town02_waterfallvillage', -1, 0, 0)
end

function fgv1.Init(map)
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
end

function fgv1.PreBattle(is_rematch)
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(216, 344, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 264, 152, Direction.Down)
  GROUND:CharSetAnim(nilo, 'EventSleep', true)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 344, Direction.Up)
  end

  local carchacrok = nil
  if is_rematch then
    carchacrok = creer_acteur('Carchacrok_Boss', 'garchomp', Gender.Male, '', 240, 196, Direction.Down)
  end

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:MoveCamera(240, 224, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)

  local arrivee = {}
  if hero ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 240, 240, false, 2)
      GROUND:EntTurn(hero, Direction.Up)
    end))
  end
  if partenaire ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partenaire, 216, 248, false, 2)
      GROUND:EntTurn(partenaire, Direction.Up)
    end))
  end
  if #arrivee > 0 then TASK:JoinCoroutines(arrivee) end

  GAME:MoveCamera(240, 180, 25, false)

  if not is_rematch then
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim')
      GAME:WaitFrames(25)
    end
    local approche = {}
    if hero ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, 248, 196, false, 2)
        if GROUND.CharTurnToCharAnimated ~= nil then
          pcall(function() GROUND:CharTurnToCharAnimated(hero, nilo, 4) end)
        else
          GROUND:CharTurnToChar(hero, nilo)
        end
      end))
    end
    if partenaire ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        GROUND:MoveToPosition(partenaire, 224, 204, false, 2)
        if GROUND.CharTurnToCharAnimated ~= nil then
          pcall(function() GROUND:CharTurnToCharAnimated(partenaire, nilo, 4) end)
        else
          GROUND:CharTurnToChar(partenaire, nilo)
        end
      end))
    end
    if #approche > 0 then TASK:JoinCoroutines(approche) end

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' ! Hé, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! Réveille-toi !', 'standard')
    end
    UI:ResetSpeaker()

    GROUND:CharSetAnim(nilo, 'Wake', false)
    GAME:WaitFrames(36)
    if GROUND.CharEndAnim ~= nil then
      GROUND:CharEndAnim(nilo)
    end
    GAME:WaitFrames(15)

    cinematique.Dire(nilo, 'Dizzy', 'Maman… grand frère…', 'droite')
    GAME:WaitFrames(15)
    cinematique.Emote(nilo, 'exclaim', 'EVT_Emote_Exclaim')
    GAME:WaitFrames(25)
    cinematique.Dire(nilo, 'Surprised', 'Hein ?! Vous… vous n’êtes pas Maman ni Léo… Qui êtes-vous ?!', 'droite')

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Happy', 'Ne t’inquiète pas, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! On est une équipe de secours ! Ta maman, Lyra, nous a envoyés te chercher jusqu’ici !', 'standard')
    end

    cinematique.Emote(nilo, 'shock', 'EVT_Emote_Shock')
    GAME:WaitFrames(25)
    cinematique.Dire(nilo, 'Pain', 'Non… non !! Vous n’auriez pas dû venir… Partez tout de suite !!', 'droite')
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'question', 'EVT_Emote_Confused')
      GAME:WaitFrames(25)
      cinematique.Dire(partenaire, 'Surprised', 'Comment ça, « non » ?! Tu es enfin en sécurité ! Qu’est-ce qui se passe ?!', 'standard')
    end
    cinematique.Dire(nilo, 'Crying', 'Le sol tremble encore… Il arrive… ' .. cinematique.NomEspece('garchomp', 'Carchacrok') .. ' !!!', 'droite')
    UI:ResetSpeaker()

    -- Secousse puis double flash blanc révélant Carchacrok au centre des vasques
    SOUND:FadeOutBGM(20)
    SOUND:PlayBattleSE('EVT_Tower_Tremor_Weak')
    pcall(function() GROUND:MoveScreen(RogueEssence.Content.ScreenMover(0, 4, 30)) end)
    GAME:WaitFrames(20)

    flash_blanc()
    GAME:WaitFrames(16)
    flash_blanc()
    GAME:WaitFrames(4)

    carchacrok = creer_acteur('Carchacrok_Boss', 'garchomp', Gender.Male, '', 240, 196, Direction.Down)
    local recul = {}
    if hero ~= nil then
      table.insert(recul, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, 240, 260, true, 3)
        GROUND:EntTurn(hero, Direction.Up)
      end))
    end
    if partenaire ~= nil then
      table.insert(recul, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        GROUND:MoveToPosition(partenaire, 216, 268, true, 3)
        GROUND:EntTurn(partenaire, Direction.Up)
      end))
    end
    table.insert(recul, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(nilo, 264, 144, true, 3)
      GROUND:EntTurn(nilo, Direction.Down)
    end))
    TASK:JoinCoroutines(recul)

    SOUND:PlayBattleSE('EVT_Roar')
    GROUND:CharSetAnim(carchacrok, 'Attack', false)
    SOUND:PlayBGM('Threat.ogg', true)
    GAME:WaitFrames(20)

    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'shock', 'EVT_Emote_Shock')
      GAME:WaitFrames(25)
    end
    cinematique.Dire(carchacrok, 'Angry', 'GRRRROOOAAARRR !! Qui ose encore troubler la paix de ma caverne ?!', 'droite')
    cinematique.Dire(carchacrok, 'Angry', 'Ce petit Lixy m’a déjà réveillé en chutant dans mes vasques… Et voilà que d’autres intrus débarquent pour faire du vacarme !', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Nous sommes une équipe de secours ! Nous ne repartirons pas sans ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'standard')
    end
  else
    SOUND:PlayBGM('Threat.ogg', true)
    SOUND:PlayBattleSE('EVT_Roar')
    GROUND:CharSetAnim(carchacrok, 'Attack', false)
    GAME:WaitFrames(20)
    cinematique.Dire(carchacrok, 'Angry', 'Encore vous ?! Vous tenez vraiment à mesurer vos forces face au maître des vasques ?', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Cette fois, nous ne reculerons pas ! Nous ramènerons ' .. cinematique.NomColore('Nilo', 'shinx') .. ' à la maison !', 'standard')
    end
  end

  SOUND:FadeOutBGM(25)
  GAME:WaitFrames(25)
  SOUND:PlayBGM('Boss Battle 2.ogg', true)
  GAME:WaitFrames(15)
  cinematique.Dire(carchacrok, 'Angry', 'Assez parlé ! Montrez-moi ce que vous valez !', 'droite')
  UI:ResetSpeaker()
  GAME:WaitFrames(20)

  COMMON.BossTransition(true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  GAME:ContinueDungeon('grotte_verdoyante', 1, 0, 0)
end

function fgv1.PostBattle()
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(216, 268, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 264, 144, Direction.Down)
  local carchacrok = creer_acteur('Carchacrok_Boss', 'garchomp', Gender.Male, '', 240, 196, Direction.Down)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 260, Direction.Up)
  end
  SOUND:FadeOutBGM(15)
  GAME:MoveCamera(240, 180, 1, false)
  GAME:FadeIn(25)
  GAME:WaitFrames(25)

  cinematique.Emote(carchacrok, 'sweatdrop', 'EVT_Emote_Sweatdrop')
  GAME:WaitFrames(25)
  cinematique.Dire(carchacrok, 'Pain', 'Grrr… Pas mal pour une jeune équipe de secours… Emportez ce petit Lixy et laissez-moi retrouver mon calme.', 'droite')
  UI:ResetSpeaker()

  SOUND:PlayBattleSE('EVT_CH03_Scurry')
  GROUND:CharSetAnim(carchacrok, 'Hop', false)
  GAME:WaitFrames(20)
  GROUND:RemoveCharacter('Carchacrok_Boss')

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GROUND:MoveToPosition(nilo, 240, 224, true, 3)
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(nilo, Direction.Down, 4) end)
  else
    GROUND:EntTurn(nilo, Direction.Down)
  end
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(25)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Vous… vous avez vraiment tenu tête à ' .. cinematique.NomEspece('garchomp', 'Carchacrok') .. ' pour me sauver !!', 'droite')

  -- Arrivée de Lyra depuis le couloir sud (x = 256 entièrement libre de y = 344 à y = 200).
  UI:ResetSpeaker()
  UI:SetSpeaker('Lyra', true, '', -1, '', (RogueEssence.Data.Gender and RogueEssence.Data.Gender.Unknown) or Gender.Unknown)
  UI:WaitShowDialogue(cinematique.NomColore('Nilo', 'shinx') .. ' !! Est-ce que tout le monde va bien ?!')
  UI:ResetSpeaker()

  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  cinematique.Emote(nilo, 'exclaim', false)
  if partenaire ~= nil then
    GAME:WaitFrames(5)
    cinematique.Emote(partenaire, 'exclaim', false)
    if GROUND.CharAnimateTurnTo ~= nil then
      pcall(function() GROUND:CharAnimateTurnTo(partenaire, Direction.Down, 4) end)
    else
      GROUND:EntTurn(partenaire, Direction.Down)
    end
  end
  if hero ~= nil then
    GAME:WaitFrames(5)
    cinematique.Emote(hero, 'exclaim', false)
    if GROUND.CharAnimateTurnTo ~= nil then
      pcall(function() GROUND:CharAnimateTurnTo(hero, Direction.Down, 4) end)
    else
      GROUND:EntTurn(hero, Direction.Down)
    end
  end
  GAME:WaitFrames(20)

  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', 256, 344, Direction.Up)
  GROUND:MoveToPosition(lyra, 256, 240, true, 2)
  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(lyra, nilo, 4) end)
    pcall(function() GROUND:CharTurnToCharAnimated(nilo, lyra, 4) end)
  else
    GROUND:CharTurnToChar(lyra, nilo)
    GROUND:CharTurnToChar(nilo, lyra)
  end
  if partenaire ~= nil then
    if GROUND.CharTurnToCharAnimated ~= nil then
      pcall(function() GROUND:CharTurnToCharAnimated(partenaire, lyra, 4) end)
    else
      GROUND:CharTurnToChar(partenaire, lyra)
    end
  end
  if hero ~= nil then
    GAME:WaitFrames(5)
    if GROUND.CharTurnToCharAnimated ~= nil then
      pcall(function() GROUND:CharTurnToCharAnimated(hero, lyra, 4) end)
    else
      GROUND:CharTurnToChar(hero, lyra)
    end
  end

  GROUND:CharSetAnim(nilo, 'Hop', false)
  GAME:WaitFrames(20)
  GROUND:CharEndAnim(nilo)
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(20)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman !! Tu nous as rejoints jusqu’ici !', 'standard')
  cinematique.Respirer(15)
  cinematique.Dire(lyra, 'Teary-Eyed', 'Mon petit ' .. cinematique.NomColore('Nilo', 'shinx') .. '… Quand le rugissement s’est tu, je me suis précipitée dans la grotte ! Quel bonheur de te revoir sain et sauf…', 'droite')
  cinematique.Respirer(15)

  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(lyra, hero or partenaire, 4) end)
  elseif hero ~= nil then
    GROUND:CharTurnToChar(lyra, hero)
  end
  cinematique.Dire(lyra, 'Happy', 'Merci infiniment à tous les deux ! Sans votre bravoure, je n’ose même pas imaginer ce qui serait arrivé.', 'droite')
  if partenaire ~= nil then
    cinematique.Respirer(15)
    cinematique.Dire(partenaire, 'Happy', 'L’essentiel, c’est que vous soyez réunis ! Vite, rentrons à Réverie Town annoncer la bonne nouvelle à Léo et aux habitants !', 'standard')
  end
  cinematique.Respirer(15)
  cinematique.Dire(nilo, 'Happy', 'Oui !! Rentrons tous ensemble !', 'standard')
  UI:ResetSpeaker()
  GAME:WaitFrames(20)

  -- Fondu vers le noir, puis Journal de Victoire façon Halcyon avec sa musique dédiée avant de quitter le donjon.
  SOUND:FadeOutBGM(30)
  GAME:FadeOut(false, 30)
  GAME:WaitFrames(35)
  GROUND:RemoveCharacter('Lyra_Grotte')
  GROUND:RemoveCharacter('Nilo_Grotte')

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.AlerteShinx = 'termine'
  SV.Destiny.LuxrayAttente = nil
  SV.Destiny.DepartShinxAccepte = nil
  SV.Destiny.GrotteVerdoyanteRetourEchec = nil
  SV.Destiny.GrotteVerdoyanteDernierKO = nil
  SV.Destiny.GrotteVerdoyanteBossVaincu = true
  SV.Destiny.GrotteVerdoyantePhase = 4
  SV.Destiny.CelebrationNilo = 'en_attente'
  SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
  local deja_debloque = GAME:DungeonUnlocked('grotte_verdoyante')
  if not deja_debloque then
    GAME:UnlockDungeon('grotte_verdoyante')
  end
  missions_reverie.Completer('grotte_verdoyante', true)

  -- Journal de victoire (style Halcyon) : texte centré sur écran noir accompagné de "Job Clear!.ogg".
  UI:ResetSpeaker(false)
  if UI.SetCenter ~= nil then pcall(function() UI:SetCenter(true) end) end
  SOUND:PlayBGM('Job Clear!.ogg', false)
  GAME:WaitFrames(15)
  UI:WaitShowDialogue('— Journal d’Exploration —\nMission de secours accomplie avec succès !')
  UI:WaitShowDialogue(cinematique.NomColore('Nilo', 'shinx') .. ' et ' .. cinematique.NomColore('Lyra', 'luxray') .. ' ont retrouvé les leurs sains et saufs au terme de la traversée de la [color=#7FE092]Grotte Verdoyante[color].')
  if not deja_debloque then
    if SOUND.PlayFanfare ~= nil then pcall(function() SOUND:PlayFanfare('Fanfare/NewArea') end) end
    UI:WaitShowDialogue('L’exploration libre de la [color=#7FE092]Grotte Verdoyante[color] est désormais ouverte depuis la sortie est de [color=#F5D27A]Réverie Town[color] !')
  end
  if UI.SetCenter ~= nil then pcall(function() UI:SetCenter(false) end) end
  UI:ResetSpeaker()
  SOUND:FadeOutBGM(30)
  GAME:WaitFrames(30)

  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  finir_vers_reverie()
end

function fgv1.EmptyReturn()
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(216, 344, Direction.Up)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 344, Direction.Up)
  end

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:MoveCamera(240, 224, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)

  local taches = {}
  if hero ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 240, 240, false, 2)
      GROUND:EntTurn(hero, Direction.Up)
    end))
  end
  if partenaire ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partenaire, 216, 248, false, 2)
      GROUND:EntTurn(partenaire, Direction.Up)
    end))
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end

  GAME:MoveCamera(240, 180, 20, false)
  GAME:WaitFrames(15)
  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Happy', 'Les vasques sont si calmes depuis le combat face à Carchacrok… Une belle traversée jusqu’au bout !', 'standard')
  else
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Les vasques scintillent paisiblement au bout de la Grotte Verdoyante.')
  end
  UI:ResetSpeaker()

  missions_reverie.Completer('grotte_verdoyante', true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
  GAME:FadeOut(false, 20)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  finir_vers_reverie()
end

function fgv1.Enter(map)
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.GrotteVerdoyantePhase == 3 then
    fgv1.PostBattle()
  elseif SV.Destiny.GrotteVerdoyanteBossVaincu == true or SV.Destiny.GrotteVerdoyantePhase == 4 then
    fgv1.EmptyReturn()
  elseif SV.Destiny.GrotteVerdoyantePhase == 1 then
    fgv1.PreBattle(true)
  else
    fgv1.PreBattle(false)
  end
end

function fgv1.GameLoad(map)
  GAME:FadeIn(20)
end

function fgv1.Update(map, time) end

return fgv1
