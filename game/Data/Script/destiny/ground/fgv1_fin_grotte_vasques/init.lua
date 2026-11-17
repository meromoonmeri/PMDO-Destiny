-- Fosse Cascade Fond (fin de la Fosse Cascade : fgv1_fin_grotte_vasques, 480x360).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : découverte de Nilo, réveil, coupure franche de la musique, secousses et bouillonnement
--                        des vasques, voix invisible des abysses, jaillissement de Kabutops hors d'un geyser
--                        (mise en scène inspirée de Searing Crucible dans Halcyon, conforme au Cutscene Guide)
--   * PreBattle(true)  : revanche condensée après une défaite face à Kabutops
--   * PostBattle()     : défaite de Kabutops, plongeon dans les vasques, retrouvailles de Nilo et Lyra, Journal de Victoire
--   * EmptyReturn()    : visites paisibles après le sauvetage
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'

local fgv1 = {}

local LIEU_DONJON = '[color=#FFC663]Fosse Cascade[color]'
local LIEU_FOND = '[color=#FFC663]Fosse Cascade Fond[color]'
local LIEU_VILLE = '[color=#FFC663]Réverie Town[color]'

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

local function tourner_vers(ch, dir, vitesse)
  if ch == nil then return end
  if GROUND.CharAnimateTurnTo ~= nil then
    pcall(function() GROUND:CharAnimateTurnTo(ch, dir, vitesse or 4) end)
  else
    GROUND:EntTurn(ch, dir)
  end
end

local function regarder_cible(ch, cible, vitesse)
  if ch == nil or cible == nil then return end
  if GROUND.CharTurnToCharAnimated ~= nil then
    pcall(function() GROUND:CharTurnToCharAnimated(ch, cible, vitesse or 4) end)
  else
    GROUND:CharTurnToChar(ch, cible)
  end
end

local function couper_musique_choc()
  if SOUND.StopBGM ~= nil then
    SOUND:StopBGM()
  else
    SOUND:FadeOutBGM(1)
  end
end

local function secouer_ecran(dx, dy, duree)
  pcall(function()
    GROUND:MoveScreen(RogueEssence.Content.ScreenMover(dx, dy, duree))
  end)
end

local function jouer_particule(nom_anim, frame_time, cycles, x, y, couche)
  pcall(function()
    local anim = RogueEssence.Content.AnimData(nom_anim, frame_time or 2)
    local emitter = RogueEssence.Content.SingleEmitter(anim, cycles or 1)
    if couche ~= nil then
      emitter.Layer = couche
    elseif DrawLayer ~= nil and DrawLayer.Front ~= nil then
      emitter.Layer = DrawLayer.Front
    elseif DrawLayer ~= nil and DrawLayer.Top ~= nil then
      emitter.Layer = DrawLayer.Top
    end
    GROUND:PlayVFX(emitter, x, y)
  end)
end

local function reculer_en_regardant_haut(ch, cible_x, cible_y, frames, vitesse)
  if ch == nil then return end
  if GROUND.AnimateInDirection ~= nil then
    local ok = pcall(function()
      GROUND:AnimateInDirection(ch, 'Walk', Direction.Up, Direction.Down, frames, 1, vitesse)
    end)
    if ok then
      GROUND:TeleportTo(ch, cible_x, cible_y, Direction.Up)
      return
    end
  end
  GROUND:MoveToPosition(ch, cible_x, cible_y, true, vitesse)
  tourner_vers(ch, Direction.Up, 3)
end

local function parler_voix_abysses(texte)
  UI:ResetSpeaker(false)
  local inconnu = (STRINGS ~= nil and STRINGS.Format ~= nil and STRINGS:Format('\\uE040')) or '???'
  local genre_inconnu = (RogueEssence.Data.Gender and RogueEssence.Data.Gender.Unknown) or Gender.Genderless
  UI:SetSpeaker(inconnu, true, '', -1, '', genre_inconnu)
  UI:WaitShowDialogue(texte)
  UI:ResetSpeaker()
end

local function lancer_duel_boss()
  -- En test direct depuis le Ground Editor (-dev : _ZONE.InDevZone == true),
  -- ContinueDungeon passe forceNewZone = false et renvoie à l'éditeur au lieu
  -- de charger le Segment 1 (end_grotte_verdoyante). EnterDungeon force la zone.
  local en_edition_dev = false
  pcall(function()
    if _ZONE ~= nil and _ZONE.InDevZone == true then
      en_edition_dev = true
    end
  end)
  if en_edition_dev then
    GAME:EnterDungeon('grotte_verdoyante', 1, 0, 0, RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
  else
    GAME:ContinueDungeon('grotte_verdoyante', 1, 0, 0)
  end
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

  -- Pré-création du boss caché dans les vasques (modèle Searing Crucible de Halcyon).
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '', 240, 192, Direction.Down)
  if not is_rematch then
    GROUND:Hide('Kabutops_Boss')
  end

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 344, Direction.Up)
  end

  GAME:MoveCamera(240, 232, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)
  -- Cutscene Guide : démarrer la musique après la fin du fondu d'entrée.
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  -- Marche échelonnée (0f / 7f, non-multiple de 4) à 1 px/frame avec panoramique doux.
  local arrivee = {
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(240, 216, 64, false)
    end),
  }
  if hero ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 240, 264, false, 1)
      tourner_vers(hero, Direction.Up, 4)
    end))
  end
  if partenaire ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GAME:WaitFrames(7)
      GROUND:MoveToPosition(partenaire, 216, 272, false, 1)
      tourner_vers(partenaire, Direction.Up, 4)
    end))
  end
  TASK:JoinCoroutines(arrivee)
  GAME:WaitFrames(15)

  if not is_rematch then
    -- 1. Découverte et réveil de Nilo près des vasques supérieures.
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim_2')
      GAME:WaitFrames(25)
    end

    local approche = {
      TASK:BranchCoroutine(function()
        GAME:MoveCamera(240, 184, 32, false)
      end),
    }
    if hero ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, 248, 192, true, 2)
        regarder_cible(hero, nilo, 4)
      end))
    end
    if partenaire ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GAME:WaitFrames(6)
        GROUND:MoveToPosition(partenaire, 224, 200, true, 2)
        regarder_cible(partenaire, nilo, 4)
      end))
    end
    TASK:JoinCoroutines(approche)
    GAME:WaitFrames(15)

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' ! Hé, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! Réveille-toi !', 'standard')
    end
    UI:ResetSpeaker()
    cinematique.Respirer(20)

    local duree_wake = 36
    local wake_dispo = true
    pcall(function()
      local gm = RogueEssence.Content.GraphicsManager
      if gm.GetAnimIndex ~= nil then
        local idx = gm.GetAnimIndex('Wake')
        if idx == nil or idx < 0 then
          wake_dispo = false
        else
          local feuille = gm.GetChara(nilo.CurrentForm:ToCharID())
          if feuille:GetReferencedAnimIndex(idx) ~= idx then
            wake_dispo = false
          else
            local t = tonumber(feuille:GetTotalTime(idx, nilo.Direction))
            if t ~= nil and t > 0 then duree_wake = math.floor(t) end
          end
        end
      end
    end)
    if wake_dispo then
      GROUND:CharSetAnim(nilo, 'Wake', false)
      GAME:WaitFrames(duree_wake)
    else
      GAME:WaitFrames(20)
    end
    if GROUND.CharEndAnim ~= nil then
      GROUND:CharEndAnim(nilo)
    end
    GAME:WaitFrames(20)

    cinematique.Dire(nilo, 'Dizzy', 'Maman… grand frère…', 'droite')
    cinematique.Respirer(15)
    cinematique.Emote(nilo, 'exclaim', 'EVT_Emote_Exclaim')
    GAME:WaitFrames(25)
    cinematique.Dire(nilo, 'Surprised', 'Hein ?! Vous… vous n’êtes pas Maman ni Léo… Qui êtes-vous ?!', 'droite')

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Happy', 'Ne t’inquiète pas, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! On est une équipe de secours ! Ta maman, Lyra, nous a envoyés te chercher jusqu’ici !', 'standard')
    end

    cinematique.Emote(nilo, 'shock', 'EVT_Emote_Shock_2')
    GAME:WaitFrames(25)
    cinematique.Dire(nilo, 'Pain', 'Non… non !! Vous n’auriez pas dû descendre jusqu’au fond… Partez tout de suite !!', 'droite')
    UI:ResetSpeaker()

    -- 2. Coupure franche de la musique et secousse souterraine (modèle Searing Crucible).
    couper_musique_choc()
    SOUND:PlayBattleSE('EVT_Tower_Tremor_Weak')
    secouer_ecran(2, 4, 30)

    local choc_secousse = {}
    if partenaire ~= nil then
      table.insert(choc_secousse, TASK:BranchCoroutine(function()
        cinematique.Emote(partenaire, 'shock', 'EVT_Emote_Shock')
      end))
    end
    if hero ~= nil then
      table.insert(choc_secousse, TASK:BranchCoroutine(function()
        GAME:WaitFrames(6)
        -- Pas de second SFX simultané (Cutscene Guide : un seul SFX d'émote à la fois).
        cinematique.Emote(hero, 'exclaim')
      end))
    end
    if #choc_secousse > 0 then TASK:JoinCoroutines(choc_secousse) end
    GAME:WaitFrames(30)

    -- 3. Bouillonnement des vasques émeraude et recul d'urgence de l'équipe.
    SOUND:PlayBattleSE('EVT_CH05_Hot_Spring_Splash')
    secouer_ecran(1, 3, 24)
    jouer_particule('Bubbles_Blue', 3, 1, 176, 176)
    jouer_particule('Wave_Circle_Blue', 3, 1, 240, 188)
    jouer_particule('Bubbles_Blue', 3, 1, 304, 176)

    cinematique.TournerGroupe({
      {partenaire, Direction.Left, 0, 3},
      {hero, Direction.Right, 7, 3},
      {nilo, Direction.DownLeft, 11, 3},
    })
    GAME:WaitFrames(10)
    cinematique.TournerGroupe({
      {partenaire, Direction.Right, 0, 3},
      {hero, Direction.UpLeft, 5, 3},
    })
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'sweating', 'EVT_Emote_Sweating')
    end
    GAME:WaitFrames(20)

    local repli = {
      TASK:BranchCoroutine(function()
        GAME:MoveCamera(240, 200, 20, false)
      end),
      TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(nilo, 264, 144, true, 2)
        tourner_vers(nilo, Direction.Down, 3)
      end),
    }
    if hero ~= nil then
      table.insert(repli, TASK:BranchCoroutine(function()
        reculer_en_regardant_haut(hero, 240, 232, 20, 2)
      end))
    end
    if partenaire ~= nil then
      table.insert(repli, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        reculer_en_regardant_haut(partenaire, 216, 240, 20, 2)
      end))
    end
    TASK:JoinCoroutines(repli)
    GAME:WaitFrames(15)

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Surprised', 'L’eau des vasques se met à bouillonner de partout ! Qu’est-ce qui remonte du gouffre ?!', 'standard')
    end
    UI:ResetSpeaker()
    cinematique.Respirer(20)

    -- 4. Voix invisible depuis les profondeurs (aucun portrait hors-champ, Cutscene Guide).
    parler_voix_abysses('Qui ose troubler le silence des abysses… au plus profond de la ' .. LIEU_DONJON .. '… ?')

    SOUND:PlayBattleSE('EVT_Emote_Confused_2')
    local regards_voix = {}
    if partenaire ~= nil then
      table.insert(regards_voix, TASK:BranchCoroutine(function()
        cinematique.Emote(partenaire, 'shock')
        tourner_vers(partenaire, Direction.UpRight, 3)
        GAME:WaitFrames(12)
        tourner_vers(partenaire, Direction.UpLeft, 3)
        GAME:WaitFrames(12)
        tourner_vers(partenaire, Direction.Up, 3)
      end))
    end
    if hero ~= nil then
      table.insert(regards_voix, TASK:BranchCoroutine(function()
        GAME:WaitFrames(7)
        cinematique.Emote(hero, 'exclaim')
        tourner_vers(hero, Direction.UpLeft, 3)
        GAME:WaitFrames(12)
        tourner_vers(hero, Direction.UpRight, 3)
        GAME:WaitFrames(12)
        tourner_vers(hero, Direction.Up, 3)
      end))
    end
    if #regards_voix > 0 then TASK:JoinCoroutines(regards_voix) end
    GAME:WaitFrames(15)

    parler_voix_abysses('Ce jeune intrus a déjà brisé la quiétude de mes bassins… Aucun de vous ne remontera à la surface !')

    cinematique.Dire(nilo, 'Crying', 'L’eau centrale va céder… Reculez !! C’est le seigneur du gouffre… ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. ' !!!', 'droite')
    UI:ResetSpeaker()

    -- 5. Montée de la tension (« Rising Fear.ogg ») et éruption du geyser révélant Kabutops.
    SOUND:PlayBGM('Rising Fear.ogg', true)
    GAME:WaitFrames(15)

    SOUND:PlayBattleSE('EVT_Tower_Tremor_Strong')
    secouer_ecran(3, 6, 30)
    jouer_particule('Wave_Circle_Blue', 2, 1, 240, 192)
    GAME:WaitFrames(12)

    SOUND:PlayBattleSE('EVT_CH05_Waterfall_Cave_Geyser')
    jouer_particule('Water_Column_Ranger', 2, 1, 240, 192)
    jouer_particule('Water_Spout_Splash', 2, 1, 240, 192, DrawLayer and DrawLayer.Top or nil)
    GROUND:Unhide('Kabutops_Boss')

    local jaillissement = {
      TASK:BranchCoroutine(function()
        GROUND:CharSetAnim(kabutops, 'Hop', false)
        GAME:WaitFrames(24)
        if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end
      end),
    }
    if hero ~= nil then
      table.insert(jaillissement, TASK:BranchCoroutine(function()
        GAME:WaitFrames(4)
        SOUND:PlayBattleSE('EVT_Emote_Startled')
        cinematique.Emote(hero, 'shock')
        reculer_en_regardant_haut(hero, 240, 248, 8, 2)
      end))
    end
    if partenaire ~= nil then
      table.insert(jaillissement, TASK:BranchCoroutine(function()
        GAME:WaitFrames(9)
        cinematique.Emote(partenaire, 'exclaim')
        reculer_en_regardant_haut(partenaire, 216, 256, 8, 2)
      end))
    end
    TASK:JoinCoroutines(jaillissement)

    -- Coup de faux d'intimidation à la réception.
    SOUND:PlayBattleSE('DUN_Slash')
    jouer_particule('Slash_Ranger', 2, 1, 240, 204)
    GROUND:CharSetAnim(kabutops, 'Swing', false)
    GAME:WaitFrames(16)
    if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end
    GAME:WaitFrames(20)

    -- 6. Face-à-face (tous les acteurs dégagés entre les portraits Y=132..188 et la boîte Y>=188).
    cinematique.Dire(kabutops, 'Angry', 'KSSSHHHAAARRR !! Depuis des âges oubliés, je veille sur la ' .. LIEU_FOND .. ' !', 'droite')
    cinematique.Dire(kabutops, 'Angry', 'Quiconque ose plonger jusqu’à mon sanctuaire englouti goûtera au tranchant de mes faux !', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Nous sommes une équipe de secours ! Nous ne repartirons pas sans ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'standard')
    end
  else
    -- Revanche condensée (PreBattle(true)) : mise en place directe et fluide.
    local mise_en_place = {
      TASK:BranchCoroutine(function()
        GAME:MoveCamera(240, 200, 16, false)
      end),
    }
    if hero ~= nil then
      table.insert(mise_en_place, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, 240, 248, false, 1.5)
        tourner_vers(hero, Direction.Up, 4)
      end))
    end
    if partenaire ~= nil then
      table.insert(mise_en_place, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        GROUND:MoveToPosition(partenaire, 216, 256, false, 1.5)
        tourner_vers(partenaire, Direction.Up, 4)
      end))
    end
    TASK:JoinCoroutines(mise_en_place)

    SOUND:FadeOutBGM(30)
    GAME:WaitFrames(30)
    SOUND:PlayBGM('Rising Fear.ogg', true)
    SOUND:PlayBattleSE('DUN_Slash')
    jouer_particule('Slash_Ranger', 2, 1, 240, 204)
    GROUND:CharSetAnim(kabutops, 'Swing', false)
    GAME:WaitFrames(16)
    if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end
    GAME:WaitFrames(20)

    cinematique.Dire(kabutops, 'Angry', 'Encore vous ?! Vous osez défier à nouveau le gardien de la ' .. LIEU_FOND .. ' ?', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Cette fois, nous ne reculerons pas ! Nous ramènerons ' .. cinematique.NomColore('Nilo', 'shinx') .. ' sain et sauf !', 'standard')
    end
  end

  -- Transition musicale propre (30 frames de fondu avant le thème de boss, Cutscene Guide).
  SOUND:FadeOutBGM(30)
  GAME:WaitFrames(30)
  SOUND:PlayBGM('Boss Battle 2.ogg', true)

  GROUND:MoveToPosition(kabutops, 240, 200, false, 1)
  SOUND:PlayBattleSE('EVT_Roar')
  secouer_ecran(3, 5, 20)
  GROUND:CharSetAnim(kabutops, 'Charge', false)
  GAME:WaitFrames(20)
  if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end

  cinematique.Dire(kabutops, 'Shouting', 'En garde ! Que le torrent des abysses vous emporte !', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  COMMON.BossTransition(true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  lancer_duel_boss()
end

function fgv1.PostBattle()
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(216, 256, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 264, 144, Direction.Down)
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '', 240, 196, Direction.Down)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 248, Direction.Up)
  end
  SOUND:FadeOutBGM(20)
  GAME:MoveCamera(240, 196, 1, false)
  GAME:WaitFrames(20)
  GAME:FadeIn(25)
  GAME:WaitFrames(25)

  cinematique.Emote(kabutops, 'sweatdrop', 'EVT_Emote_Sweatdrop')
  GAME:WaitFrames(25)
  cinematique.Dire(kabutops, 'Pain', 'Ksshh… Votre détermination surpasse la fureur du courant… Emportez ce jeune Lixy et laissez mes vasques retrouver le silence.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  -- Kabutops replonge dans les eaux profondes des vasques.
  SOUND:PlayBattleSE('EVT_CH05_Hot_Spring_Splash')
  jouer_particule('Water_Spout_Splash', 2, 1, 240, 192, DrawLayer and DrawLayer.Top or nil)
  jouer_particule('Wave_Circle_Blue', 2, 1, 240, 192)
  GROUND:CharSetAnim(kabutops, 'Hop', false)
  GAME:WaitFrames(24)
  GROUND:RemoveCharacter('Kabutops_Boss')
  GAME:WaitFrames(20)

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  GROUND:MoveToPosition(nilo, 240, 216, true, 2)
  tourner_vers(nilo, Direction.Down, 4)
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(25)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Vous… vous avez vraiment tenu tête à ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. ' pour me sauver !!', 'droite')

  -- Arrivée de Lyra depuis le couloir sud (x = 256 entièrement libre de y = 344 à y = 200).
  UI:ResetSpeaker(false)
  UI:SetSpeaker('Lyra', true, '', -1, '', (RogueEssence.Data.Gender and RogueEssence.Data.Gender.Unknown) or Gender.Genderless)
  UI:WaitShowDialogue(cinematique.NomColore('Nilo', 'shinx') .. ' !! Est-ce que tout le monde va bien ?!')
  UI:ResetSpeaker()

  SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
  local reactions_appel = {
    TASK:BranchCoroutine(function()
      cinematique.Emote(nilo, 'exclaim')
      tourner_vers(nilo, Direction.Down, 4)
    end),
  }
  if partenaire ~= nil then
    table.insert(reactions_appel, TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      cinematique.Emote(partenaire, 'exclaim')
      tourner_vers(partenaire, Direction.Down, 4)
    end))
  end
  if hero ~= nil then
    table.insert(reactions_appel, TASK:BranchCoroutine(function()
      GAME:WaitFrames(11)
      cinematique.Emote(hero, 'exclaim')
      tourner_vers(hero, Direction.Down, 4)
    end))
  end
  TASK:JoinCoroutines(reactions_appel)
  GAME:WaitFrames(20)

  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', 256, 344, Direction.Up)
  GROUND:MoveToPosition(lyra, 256, 232, true, 2)
  cinematique.RegarderGroupe({
    {lyra, nilo, 0, 4},
    {nilo, lyra, 3, 4},
    {partenaire, lyra, 6, 4},
    {hero, lyra, 10, 4},
  })

  SOUND:PlayBattleSE('EVT_Emote_Startled')
  GROUND:CharSetAnim(nilo, 'Hop', false)
  GAME:WaitFrames(20)
  if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(nilo) end
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(20)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman !! Tu nous as rejoints jusqu’ici !', 'standard')
  cinematique.Respirer(15)
  cinematique.Dire(lyra, 'Teary-Eyed', 'Mon petit ' .. cinematique.NomColore('Nilo', 'shinx') .. '… Quand le fracas du torrent s’est apaisé, je me suis précipitée dans la grotte ! Quel bonheur de te revoir sain et sauf…', 'droite')
  cinematique.Respirer(15)

  regarder_cible(lyra, hero or partenaire, 4)
  cinematique.Dire(lyra, 'Happy', 'Merci infiniment à tous les deux ! Sans votre bravoure, je n’ose même pas imaginer ce qui serait arrivé.', 'droite')
  if partenaire ~= nil then
    cinematique.Respirer(15)
    cinematique.Dire(partenaire, 'Happy', 'L’essentiel, c’est que vous soyez réunis ! Vite, rentrons à ' .. LIEU_VILLE .. ' annoncer la bonne nouvelle à Léo et aux habitants !', 'standard')
  end
  cinematique.Respirer(15)
  cinematique.Dire(nilo, 'Happy', 'Oui !! Rentrons tous ensemble !', 'standard')
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  -- Fondu vers le noir (30f + attente 35f sous écran noir, Cutscene Guide), puis Journal de Victoire.
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
  UI:WaitShowDialogue(cinematique.NomColore('Nilo', 'shinx') .. ' et ' .. cinematique.NomColore('Lyra', 'luxray') .. ' ont retrouvé les leurs sains et saufs au terme de la traversée de la ' .. LIEU_DONJON .. '.')
  if not deja_debloque then
    if SOUND.PlayFanfare ~= nil then pcall(function() SOUND:PlayFanfare('Fanfare/NewArea') end) end
    UI:WaitShowDialogue('L’exploration libre de la ' .. LIEU_DONJON .. ' est désormais ouverte depuis la sortie est de ' .. LIEU_VILLE .. ' !')
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

  GAME:MoveCamera(240, 224, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  GAME:WaitFrames(30)
  UI:WaitHideTitle(20)
  GAME:FadeIn(20)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  local taches = {}
  if hero ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 240, 248, false, 1)
      tourner_vers(hero, Direction.Up, 4)
    end))
  end
  if partenaire ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GAME:WaitFrames(7)
      GROUND:MoveToPosition(partenaire, 216, 256, false, 1)
      tourner_vers(partenaire, Direction.Up, 4)
    end))
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end

  GAME:MoveCamera(240, 192, 24, false)
  GAME:WaitFrames(20)
  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Happy', 'Les vasques de la ' .. LIEU_FOND .. ' sont si paisibles depuis notre duel face à ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. '… Une belle traversée jusqu’au bout !', 'standard')
  else
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Les vasques scintillent paisiblement au cœur de la ' .. LIEU_FOND .. '.')
  end
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  missions_reverie.Completer('grotte_verdoyante', true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
  SOUND:FadeOutBGM(30)
  GAME:FadeOut(false, 30)
  GAME:WaitFrames(30)
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
  -- La carte ne déclare pas de piste (Music = ''), contrairement à
  -- ewc3_entree_waterfall_cave : sans cette relance, une sauvegarde chargée
  -- pendant une scène des vasques restait muette jusqu'à la fin du donjon.
  GAME:FadeIn(20)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
end

function fgv1.Update(map, time) end

return fgv1
