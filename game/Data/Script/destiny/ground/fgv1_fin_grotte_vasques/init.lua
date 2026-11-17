-- Fosse Cascade Fond (fin de la Fosse Cascade : fgv1_fin_grotte_vasques, 480x360).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : découverte de Nilo endormi, réveil, puis mise en scène
--                        resserrée : UN éclair blanc (incomprehension du duo),
--                        tremblement de terreur de Nilo bien visible, DOUBLE
--                        éclair blanc d'où jaillit Kabutops — sans aucune
--                        animation d'eau — puis face-à-face et duel.
--   * PreBattle(true)  : revanche condensée après une défaite face à Kabutops
--   * PostBattle()     : défaite de Kabutops, qui FUIT VERS LE SUD EN COURANT
--                        (plus de plongeon dans les vasques), retrouvailles de
--                        Nilo et Lyra, Journal de Victoire
--   * EmptyReturn()    : visites paisibles après le sauvetage
--
-- Repères de mise en scène (px carte, carte 480x360) :
--   les vasques en terrasses occupent y = 136..208. Aucun acteur ne s'y tient :
--   le boss apparaît sur le sable plat, sous les vasques (y = 232).
--
-- Sons : chaque effet est déclenché sur l'image de son événement visuel, un
-- seul SE à la fois (Cutscene Guide). La musique n'est jamais coupée d'une
-- piste vers une autre : coupure sèche vers le silence pour le choc, puis
-- relance après le fondu d'entrée.
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'

local fgv1 = {}

local LIEU_DONJON = '[color=#FFC663]Fosse Cascade[color]'
local LIEU_FOND = '[color=#FFC663]Fosse Cascade Fond[color]'
local LIEU_VILLE = '[color=#FFC663]Réverie Town[color]'

-- Sable plat, sous la bande des vasques en terrasses (y = 136..208).
local SOL_BOSS = {x = 240, y = 232}
-- Duo face à l'estrade d'eau ; pieds à l'écran sous le repère 160 pour la caméra 236.
local SOL_HEROS = {x = 232, y = 264}
local SOL_PARTENAIRE = {x = 256, y = 268}
-- Nilo endormi entre les vasques hautes, puis recoin est où il tremble à la vue du boss.
local SOL_NILO_REVEIL = {x = 264, y = 176}
local SOL_NILO_TERREUR = {x = 288, y = 248}
local CAM_FACE = {x = 240, y = 236}
local CAM_REVEIL = {x = 240, y = 228}
local CAM_ENTREE = {x = 240, y = 264}

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

-- Éclair blanc plein écran. FadeOut(true, ...) va au blanc et attend la fin du
-- fondu : tout ce qui est joué entre FadeOut et FadeIn se produit donc derrière
-- le blanc, invisible du joueur.
local function eclair_blanc(sortie, entree)
  GAME:FadeOut(true, sortie or 3)
  GAME:FadeIn(entree or 8)
end

-- Valeurs de repli de RogueEssence.Dungeon.DrawEffect lorsque l'énumération
-- n'est pas exposée à Lua (None=-1, Sleeping=0, Stopped=1, Shaking=2,
-- Charging=3, Absent=4, Spinning=5, Hurt=6, Transparent=7, Trembling=8).
local EFFETS_DESSIN = {Shaking = 2, Trembling = 8}

local function effet_dessin(nom)
  local ok, effet = pcall(function() return RogueEssence.Dungeon.DrawEffect[nom] end)
  if ok and effet ~= nil then return effet end
  return EFFETS_DESSIN[nom]
end

-- Tremblement de terreur : DrawEffect.Shaking (oscillation de -2 à +2 px sur
-- 8 images) plutôt que Trembling (1 px), pour que le joueur voie réellement
-- Nilo trembler à l'écran.
local function trembler_de_peur(ch)
  if ch == nil then return end
  local effet = effet_dessin('Shaking')
  if effet == nil then return end
  pcall(function() GROUND:CharSetDrawEffect(ch, effet) end)
end

local function arreter_tremblement(ch)
  if ch == nil then return end
  local effet = effet_dessin('Shaking')
  if effet == nil then return end
  pcall(function() GROUND:CharEndDrawEffect(ch, effet) end)
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
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo',
    SOL_NILO_REVEIL.x, SOL_NILO_REVEIL.y, Direction.Down)
  GROUND:CharSetAnim(nilo, 'EventSleep', true)

  -- Le boss est créé sur le sable plat, sous les vasques : il n'apparaît jamais
  -- sur les terrasses d'eau (l'« escalier »).
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    SOL_BOSS.x, SOL_BOSS.y, Direction.Down)
  if not is_rematch then
    GROUND:Hide('Kabutops_Boss')
  end

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 344, Direction.Up)
  end

  GAME:MoveCamera(CAM_ENTREE.x, CAM_ENTREE.y, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 16)
  GAME:WaitFrames(18)
  UI:WaitHideTitle(14)
  GAME:FadeIn(16)
  -- Cutscene Guide : démarrer la musique après la fin du fondu d'entrée.
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  -- 1. Montée rapide du duo vers la clairière (1 px/frame, décalage 5f).
  local arrivee = {
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 36, false)
    end),
  }
  if hero ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y, false, 1.5)
      tourner_vers(hero, Direction.Up, 4)
    end))
  end
  if partenaire ~= nil then
    table.insert(arrivee, TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y, false, 1.5)
      tourner_vers(partenaire, Direction.Up, 4)
    end))
  end
  TASK:JoinCoroutines(arrivee)
  GAME:WaitFrames(6)

  if not is_rematch then
    -- 2. Découverte : Nilo dort entre les vasques hautes.
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim_2')
      GAME:WaitFrames(10)
    end

    local approche = {
      TASK:BranchCoroutine(function()
        GAME:MoveCamera(CAM_REVEIL.x, CAM_REVEIL.y, 16, false)
      end),
    }
    if hero ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y, true, 2)
        regarder_cible(hero, nilo, 3)
      end))
    end
    if partenaire ~= nil then
      table.insert(approche, TASK:BranchCoroutine(function()
        GAME:WaitFrames(4)
        GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y, true, 2)
        regarder_cible(partenaire, nilo, 3)
      end))
    end
    TASK:JoinCoroutines(approche)
    GAME:WaitFrames(6)

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' ! Hé, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! Réveille-toi !', 'standard')
    end
    UI:ResetSpeaker()
    cinematique.Respirer(10)

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
      GAME:WaitFrames(18)
    end
    if GROUND.CharEndAnim ~= nil then
      GROUND:CharEndAnim(nilo)
    end
    GAME:WaitFrames(8)

    cinematique.Dire(nilo, 'Dizzy', 'Maman… grand frère…', 'droite')
    cinematique.Respirer(8)
    cinematique.Emote(nilo, 'exclaim', 'EVT_Emote_Exclaim')
    GAME:WaitFrames(10)
    cinematique.Dire(nilo, 'Surprised', 'Hein ?! Vous… vous n’êtes pas Maman ni Léo… Qui êtes-vous ?!', 'droite')

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Happy', 'Ne t’inquiète pas, ' .. cinematique.NomColore('Nilo', 'shinx') .. ' ! On est une équipe de secours ! Ta maman, Lyra, nous a envoyés te chercher jusqu’ici !', 'standard')
    end

    cinematique.Emote(nilo, 'shock', 'EVT_Emote_Shock_2')
    GAME:WaitFrames(10)
    cinematique.Dire(nilo, 'Pain', 'Non !! Vous n’auriez pas dû descendre jusqu’au fond… Partez tout de suite !!', 'droite')
    UI:ResetSpeaker()

    -- 3. Nilo recule vers le recoin est : il reste à l'écran, tremblant.
    local recul_nilo = {
      TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(nilo, SOL_NILO_TERREUR.x, SOL_NILO_TERREUR.y, true, 2)
        tourner_vers(nilo, Direction.DownLeft, 3)
      end),
    }
    TASK:JoinCoroutines(recul_nilo)
    if partenaire ~= nil then
      regarder_cible(partenaire, nilo, 3)
    end
    trembler_de_peur(nilo)
    GAME:WaitFrames(4)

    -- 4. UN éclair blanc : les héros ne comprennent pas ce qu'ils viennent de voir.
    couper_musique_choc()
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    eclair_blanc(3, 9)
    GAME:WaitFrames(3)

    local incomprehension = {}
    if partenaire ~= nil then
      table.insert(incomprehension, TASK:BranchCoroutine(function()
        cinematique.Emote(partenaire, 'question', 'EVT_Emote_Confused')
        tourner_vers(partenaire, Direction.UpRight, 3)
        GAME:WaitFrames(10)
        tourner_vers(partenaire, Direction.UpLeft, 3)
      end))
    end
    if hero ~= nil then
      table.insert(incomprehension, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        -- Pas de second SFX simultané (Cutscene Guide : un seul SE d'émote).
        cinematique.Emote(hero, 'question')
        tourner_vers(hero, Direction.UpLeft, 3)
        GAME:WaitFrames(10)
        tourner_vers(hero, Direction.UpRight, 3)
      end))
    end
    if #incomprehension > 0 then TASK:JoinCoroutines(incomprehension) end
    GAME:WaitFrames(4)

    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Surprised', 'Un éclair blanc… ici, sous la pierre ?! Qu’est-ce que c’était que ça ?', 'standard')
    end
    -- Voix hors-champ des profondeurs (aucun portrait, Cutscene Guide) : une
    -- seule réplique, pour ne pas casser le rythme soutenu.
    parler_voix_abysses('Qui ose troubler le silence des abysses… au plus profond de la ' .. LIEU_DONJON .. '… ?')

    cinematique.Dire(nilo, 'Crying', 'Reculez !! C’est lui… Le seigneur du gouffre… ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. ' !!!', 'droite')
    UI:ResetSpeaker()

    -- 5. Secousse et DOUBLE éclair blanc : Kabutops est là, sur le sable.
    SOUND:PlayBattleSE('EVT_Tower_Tremor_Weak')
    secouer_ecran(2, 4, 18)
    GAME:WaitFrames(6)

    SOUND:PlayBattleSE('EVT_Battle_Flash')
    GAME:FadeOut(true, 2)
    GROUND:Unhide('Kabutops_Boss')
    GAME:WaitFrames(2)
    GAME:FadeIn(6)
    GAME:WaitFrames(3)
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    GAME:FadeOut(true, 2)
    GAME:WaitFrames(1)
    GAME:FadeIn(8)

    -- Réception au sol : un seul SE d'impact, coordonné avec le saut.
    SOUND:PlayBattleSE('EVT_Roar')
    secouer_ecran(3, 5, 18)
    GROUND:CharSetAnim(kabutops, 'Hop', false)
    GAME:WaitFrames(18)
    if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end

    -- Musique de tension lancée une fois l'image revenue (Cutscene Guide).
    SOUND:PlayBGM('Rising Fear.ogg', true)
    GAME:WaitFrames(8)

    -- Coup de faux d'intimidation : le SE tombe sur la même image que le geste.
    SOUND:PlayBattleSE('DUN_Slash')
    GROUND:CharSetAnim(kabutops, 'Swing', false)
    GAME:WaitFrames(14)
    if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end
    GAME:WaitFrames(6)

    -- Le recul de terreur du duo reste synchronisé avec Nilo qui tremble.
    local recul_duo = {}
    if hero ~= nil then
      table.insert(recul_duo, TASK:BranchCoroutine(function()
        cinematique.Emote(hero, 'shock')
        GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y + 8, true, 2)
        tourner_vers(hero, Direction.Up, 3)
      end))
    end
    if partenaire ~= nil then
      table.insert(recul_duo, TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        cinematique.Emote(partenaire, 'exclaim')
        GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y + 8, true, 2)
        tourner_vers(partenaire, Direction.Up, 3)
      end))
    end
    if #recul_duo > 0 then TASK:JoinCoroutines(recul_duo) end
    GAME:WaitFrames(6)

    -- 6. Face-à-face (acteurs dégagés entre les portraits Y=132..188 et la boîte Y>=188).
    cinematique.Dire(kabutops, 'Angry', 'KSSSHHHAAARRR !! Depuis des âges oubliés, je veille sur la ' .. LIEU_FOND .. ' !', 'droite')
    cinematique.Dire(kabutops, 'Angry', 'Quiconque ose plonger jusqu’à mon sanctuaire goûtera au tranchant de mes faux !', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Nous sommes une équipe de secours ! Nous ne repartirons pas sans ' .. cinematique.NomColore('Nilo', 'shinx') .. ' !', 'standard')
    end
  else
    -- Revanche condensée (PreBattle(true)) : mise en place directe et fluide.
    local mise_en_place = {
      TASK:BranchCoroutine(function()
        GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 12, false)
      end),
    }
    if hero ~= nil then
      table.insert(mise_en_place, TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y, false, 1.5)
        tourner_vers(hero, Direction.Up, 4)
      end))
    end
    if partenaire ~= nil then
      table.insert(mise_en_place, TASK:BranchCoroutine(function()
        GAME:WaitFrames(4)
        GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y, false, 1.5)
        tourner_vers(partenaire, Direction.Up, 4)
      end))
    end
    TASK:JoinCoroutines(mise_en_place)

    SOUND:FadeOutBGM(15)
    GAME:WaitFrames(15)
    SOUND:PlayBattleSE('DUN_Slash')
    GROUND:CharSetAnim(kabutops, 'Swing', false)
    GAME:WaitFrames(14)
    if GROUND.CharEndAnim ~= nil then GROUND.CharEndAnim(kabutops) end
    SOUND:PlayBGM('Rising Fear.ogg', true)
    GAME:WaitFrames(10)

    cinematique.Dire(kabutops, 'Angry', 'Encore vous ?! Vous osez défier à nouveau le gardien de la ' .. LIEU_FOND .. ' ?', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Cette fois, nous ne reculerons pas ! Nous ramènerons ' .. cinematique.NomColore('Nilo', 'shinx') .. ' sain et sauf !', 'standard')
    end
  end

  -- Transition musicale propre (fondu court : pacing soutenu), puis thème de boss.
  SOUND:FadeOutBGM(15)
  GAME:WaitFrames(15)
  SOUND:PlayBGM('Boss Battle 2.ogg', true)

  SOUND:PlayBattleSE('EVT_Tower_Tremor_Strong')
  secouer_ecran(3, 5, 16)
  GROUND:CharSetAnim(kabutops, 'Charge', false)
  GAME:WaitFrames(16)
  if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(kabutops) end

  cinematique.Dire(kabutops, 'Shouting', 'En garde ! Que le torrent des abysses vous emporte !', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(12)

  COMMON.BossTransition(true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  arreter_tremblement(nilo)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  lancer_duel_boss()
end

function fgv1.PostBattle()
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(216, 268, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 296, 240, Direction.Left)
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    SOL_BOSS.x, SOL_BOSS.y, Direction.Down)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 240, 264, Direction.Up)
  end
  SOUND:FadeOutBGM(12)
  GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 1, false)
  GAME:WaitFrames(12)
  GAME:FadeIn(20)
  GAME:WaitFrames(12)
  trembler_de_peur(nilo)

  cinematique.Emote(kabutops, 'sweatdrop', 'EVT_Emote_Sweatdrop')
  GAME:WaitFrames(12)
  cinematique.Dire(kabutops, 'Pain', 'Ksshh… Votre détermination surpasse la fureur du courant… Emportez le petit et laissez mes vasques en paix.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(10)

  -- 7. Kabutops vaincu fuit vers le sud EN COURANT (plus aucun effet d'eau).
  arreter_tremblement(nilo)
  tourner_vers(kabutops, Direction.Down, 3)
  GAME:WaitFrames(4)
  SOUND:PlayBattleSE('DUN_Tile_Step')
  local fuite = {
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(240, 240, 16, false)
    end),
    TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(kabutops, 240, 352, true, 3)
    end),
  }
  TASK:JoinCoroutines(fuite)
  GROUND:RemoveCharacter('Kabutops_Boss')
  GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 10, false)
  GAME:WaitFrames(8)

  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  -- Nilo se relève et rejoint le duo.
  local retour_nilo = {
    TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(nilo, 256, 248, true, 2)
      tourner_vers(nilo, Direction.Down, 4)
    end),
  }
  TASK:JoinCoroutines(retour_nilo)
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(10)
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
  GAME:WaitFrames(12)

  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', 256, 344, Direction.Up)
  GROUND:MoveToPosition(lyra, 256, 240, true, 2)
  cinematique.RegarderGroupe({
    {lyra, nilo, 0, 4},
    {nilo, lyra, 3, 4},
    {partenaire, lyra, 6, 4},
    {hero, lyra, 10, 4},
  })

  SOUND:PlayBattleSE('EVT_Emote_Startled')
  GROUND:CharSetAnim(nilo, 'Hop', false)
  GAME:WaitFrames(16)
  if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(nilo) end
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(10)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman !! Tu nous as rejoints jusqu’ici !', 'standard')
  cinematique.Respirer(10)
  cinematique.Dire(lyra, 'Teary-Eyed', 'Mon petit ' .. cinematique.NomColore('Nilo', 'shinx') .. '… Quand le fracas du torrent s’est apaisé, je me suis précipitée dans la grotte ! Quel bonheur de te revoir sain et sauf…', 'droite')
  cinematique.Respirer(10)

  regarder_cible(lyra, hero or partenaire, 4)
  cinematique.Dire(lyra, 'Happy', 'Merci infiniment à tous les deux ! Sans votre bravoure, je n’ose même pas imaginer ce qui serait arrivé.', 'droite')
  if partenaire ~= nil then
    cinematique.Respirer(10)
    cinematique.Dire(partenaire, 'Happy', 'L’essentiel, c’est que vous soyez réunis ! Vite, rentrons à ' .. LIEU_VILLE .. ' annoncer la bonne nouvelle à Léo et aux habitants !', 'standard')
  end
  cinematique.Respirer(10)
  cinematique.Dire(nilo, 'Happy', 'Oui !! Rentrons tous ensemble !', 'standard')
  UI:ResetSpeaker()
  cinematique.Respirer(12)

  -- Fondu vers le noir (30f + attente sous écran noir, Cutscene Guide), puis Journal de Victoire.
  SOUND:FadeOutBGM(24)
  GAME:FadeOut(false, 24)
  GAME:WaitFrames(30)
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
  GAME:WaitFrames(12)
  UI:WaitShowDialogue('— Journal d’Exploration —\nMission de secours accomplie avec succès !')
  UI:WaitShowDialogue(cinematique.NomColore('Nilo', 'shinx') .. ' et ' .. cinematique.NomColore('Lyra', 'luxray') .. ' ont retrouvé les leurs sains et saufs au terme de la traversée de la ' .. LIEU_DONJON .. '.')
  if not deja_debloque then
    if SOUND.PlayFanfare ~= nil then pcall(function() SOUND:PlayFanfare('Fanfare/NewArea') end) end
    UI:WaitShowDialogue('L’exploration libre de la ' .. LIEU_DONJON .. ' est désormais ouverte depuis la sortie est de ' .. LIEU_VILLE .. ' !')
  end
  if UI.SetCenter ~= nil then pcall(function() UI:SetCenter(false) end) end
  UI:ResetSpeaker()
  SOUND:FadeOutBGM(24)
  GAME:WaitFrames(24)

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
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 18)
  GAME:WaitFrames(24)
  UI:WaitHideTitle(16)
  GAME:FadeIn(18)
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

  GAME:MoveCamera(240, 192, 20, false)
  GAME:WaitFrames(14)
  if partenaire ~= nil then
    cinematique.Dire(partenaire, 'Happy', 'Les vasques de la ' .. LIEU_FOND .. ' sont si paisibles depuis notre duel face à ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. '… Une belle traversée jusqu’au bout !', 'standard')
  else
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Les vasques scintillent paisiblement au cœur de la ' .. LIEU_FOND .. '.')
  end
  UI:ResetSpeaker()
  cinematique.Respirer(16)

  missions_reverie.Completer('grotte_verdoyante', true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1
  SOUND:FadeOutBGM(24)
  GAME:FadeOut(false, 24)
  GAME:WaitFrames(26)
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
