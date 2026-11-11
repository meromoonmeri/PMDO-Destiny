-- Salle des vasques (9e étage de la Grotte Verdoyante : fgv1_fin_grotte_vasques).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : 1re arrivée face à la Bande des Vasques (Colhomard, 2 Écrapince, Maskadra) tenant Nilo en otage
--   * PreBattle(true)  : revanche abrégée après une défaite au 9F
--   * PostBattle()     : fuite des brigands, retrouvailles Nilo / Lyra, remise de Gelée Royale, AlerteShinx = 'termine'
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

local function invoquer_bande()
  local colhomard = creer_acteur('Colhomard_Boss', 'crawdaunt', Gender.Male, '', 384, 312, Direction.Down)
  local ecr1 = creer_acteur('Ecrapince_1', 'corphish', Gender.Male, '', 336, 336, Direction.Down)
  local ecr2 = creer_acteur('Ecrapince_2', 'corphish', Gender.Female, '', 432, 336, Direction.Down)
  local maskadra = creer_acteur('Maskadra_Boss', 'masquerain', Gender.Female, '', 384, 276, Direction.Down)
  return colhomard, ecr1, ecr2, maskadra
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
  local partenaire = equipe_scene.Partenaire(360, 560, Direction.Up)
  local lyra = creer_acteur('Lyra_Fin', 'luxray', Gender.Female, 'Lyra', 408, 560, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 424, 232, Direction.Down)
  local colhomard, ecr1, ecr2, maskadra = invoquer_bande()

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 384, 560, Direction.Up)
  end

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:MoveCamera(384, 416, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)

  local arrivee = {}
  if hero ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 384, 416, false, 2)
      GROUND:EntTurn(hero, Direction.Up)
    end))
  end
  if partenaire ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partenaire, 360, 424, false, 2)
      GROUND:EntTurn(partenaire, Direction.Up)
    end))
  end
  table.insert(arrivee, TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(lyra, 408, 424, false, 2)
    GROUND:EntTurn(lyra, Direction.Up)
  end))
  TASK:JoinCoroutines(arrivee)

  GAME:MoveCamera(384, 320, 25, false)

  if not is_rematch then
    cinematique.Emote(lyra, 'exclaim', 'EVT_Emote_Exclaim')
    GAME:WaitFrames(10)
    cinematique.Dire(lyra, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' !! Tu es là !', 'droite')
    cinematique.Emote(nilo, 'shock', 'EVT_Emote_Shock')
    cinematique.Dire(nilo, 'Pain', 'Maman !! Au secours ! Ils m’empêchent de sortir !', 'standard')

    SOUND:PlayBGM('Threat.ogg', true)
    GAME:WaitFrames(10)
    SOUND:PlayBattleSE('EVT_Roar')
    GROUND:CharSetAnim(colhomard, 'Attack', false)
    GAME:WaitFrames(15)
    cinematique.Dire(colhomard, 'Normal', 'Héhéhé… Un louveteau curieux, et maintenant une escorte au complet !', 'standard')
    cinematique.Dire(ecr1, 'Normal', 'Patron ' .. cinematique.NomEspece('crawdaunt', 'Colhomard') .. ', on garde les vasques pour nous tout seuls !', 'standard')
    cinematique.Dire(maskadra, 'Normal', 'Personne ne quitte cette salle sans payer son passage… par une bonne correction !', 'droite')
    cinematique.Dire(lyra, 'Determined', 'Laissez mon petit tranquille ! On ne cédera pas devant vous !', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Tiens bon, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! On va les écarter tout de suite !', 'standard')
    end
  else
    SOUND:PlayBGM('Threat.ogg', true)
    cinematique.Dire(colhomard, 'Angry', 'Encore vous ?! Vous n’avez toujours pas compris qui commande dans ces vasques ?', 'standard')
    cinematique.Dire(lyra, 'Determined', 'Cette fois, on ne se laissera pas surprendre ! Libérez ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'droite')
  end

  SOUND:PlayBGM('Boss Battle 2.ogg', true)
  GAME:WaitFrames(15)
  cinematique.Dire(colhomard, 'Angry', 'Bande des Vasques, à l’attaque !', 'standard')
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
  local partenaire = equipe_scene.Partenaire(360, 424, Direction.Up)
  local lyra = creer_acteur('Lyra_Fin', 'luxray', Gender.Female, 'Lyra', 408, 424, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 424, 232, Direction.Down)
  local colhomard, ecr1, ecr2, maskadra = invoquer_bande()

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 384, 416, Direction.Up)
  end
  SOUND:FadeOutBGM(10)
  GAME:MoveCamera(384, 340, 1, false)
  GAME:FadeIn(20)
  GAME:WaitFrames(25)

  cinematique.Emote(colhomard, 'sweatdrop', 'EVT_Emote_Sweatdrop')
  cinematique.Dire(colhomard, 'Pain', 'Argh… Ces gamins cognent trop fort ! Bande des Vasques… repli !', 'standard')
  UI:ResetSpeaker()

  SOUND:PlayBattleSE('EVT_CH03_Scurry')
  local fuite = {}
  table.insert(fuite, TASK:BranchCoroutine(function() GROUND:MoveToPosition(ecr1, 336, 560, true, 3) end))
  table.insert(fuite, TASK:BranchCoroutine(function() GROUND:MoveToPosition(ecr2, 432, 560, true, 3) end))
  table.insert(fuite, TASK:BranchCoroutine(function() GROUND:MoveToPosition(maskadra, 384, 560, true, 3) end))
  table.insert(fuite, TASK:BranchCoroutine(function() GROUND:MoveToPosition(colhomard, 384, 560, true, 3) end))
  TASK:JoinCoroutines(fuite)
  for _, nom in ipairs({'Colhomard_Boss', 'Ecrapince_1', 'Ecrapince_2', 'Maskadra_Boss'}) do
    if CH(nom) ~= nil then GROUND:RemoveCharacter(nom) end
  end

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:MoveCamera(384, 384, 20, false)

  GROUND:MoveToPosition(nilo, 408, 402, true, 3)
  GROUND:EntTurn(nilo, Direction.Down)
  GROUND:EntTurn(lyra, Direction.Up)
  cinematique.Emote(nilo, 'happy')
  cinematique.Dire(nilo, 'Happy', 'Maman !!', 'standard')
  cinematique.Emote(lyra, 'happy')
  cinematique.Dire(lyra, 'Teary-Eyed', 'Mon petit ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! Tu n’as rien ? J’ai eu tellement peur !', 'droite')
  cinematique.Dire(nilo, 'Happy', 'J’ai glissé dans le courant derrière la cascade, puis ces méchants m’ont bloqué ici… Mais vous m’avez retrouvé !', 'standard')

  cinematique.RegarderGroupe({
    {lyra, hero, 0, 4},
    {nilo, hero, 5, 4},
  })
  cinematique.Dire(lyra, 'Happy', 'Merci du fond du cœur à tous les deux ! Sans votre courage, jamais je n’aurais pu sauver mon petit.', 'droite')
  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Happy', 'Tout le monde à Réverie Town va être fou de joie de vous voir rentrer ensemble !', 'standard')
  end
  cinematique.Dire(lyra, 'Happy', 'Acceptez ceci en signe de gratitude, avant que nous rentrions à la maison !', 'droite')
  UI:ResetSpeaker()

  if hero ~= nil then
    COMMON.GiftItem(hero, RogueEssence.Dungeon.InvItem('gummi_royal', false, 1))
  end
  GAME:WaitFrames(20)

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.AlerteShinx = 'termine'
  SV.Destiny.LuxrayAttente = nil
  SV.Destiny.DepartShinxAccepte = nil
  SV.Destiny.GrotteVerdoyanteBossVaincu = true
  SV.Destiny.GrotteVerdoyantePhase = 4
  SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
  if not GAME:DungeonUnlocked('grotte_verdoyante') then
    GAME:UnlockDungeon('grotte_verdoyante')
  end
  missions_reverie.Completer('grotte_verdoyante', true)

  GAME:FadeOut(false, 25)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  finir_vers_reverie()
end

function fgv1.EmptyReturn()
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(360, 560, Direction.Up)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 384, 560, Direction.Up)
  end

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GAME:MoveCamera(384, 384, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)

  local taches = {}
  if hero ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 384, 416, false, 2)
      GROUND:EntTurn(hero, Direction.Up)
    end))
  end
  if partenaire ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partenaire, 360, 424, false, 2)
      GROUND:EntTurn(partenaire, Direction.Up)
    end))
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end

  GAME:WaitFrames(20)
  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Happy', 'Les vasques sont si calmes depuis que la bande de Colhomard a déguerpi… Une belle traversée jusqu’au bout !', 'standard')
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
