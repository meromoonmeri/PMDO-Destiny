-- Fosse Cascade Fond (fin de la Fosse Cascade : fgv1_fin_grotte_vasques, 480x360).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : Nilo reste immobile sur la terrasse et avoue avoir
--                        dérèglé les courants. Un éclair révèle Kabutops,
--                        dont le souffle repousse le duo avant l'affrontement.
--   * PreBattle(true)  : revanche condensée après une défaite face à Kabutops
--   * PostBattle()     : défaite de Kabutops, qui FUIT VERS LE SUD EN COURANT
--                        (plus de plongeon dans les vasques), retrouvailles de
--                        Nilo et Lyra, Journal de Victoire
--   * EmptyReturn()    : visites paisibles après le sauvetage
--
-- L'ancre de Kabutops est le centre de la case (10,10) du duel :
-- (252,252) moins le demi-collider (8,8). Elle est sous toutes les marches.
-- La caméra laisse Nilo, le duo et le gardien visibles au-dessus des dialogues.
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'

local fgv1 = {}

local LIEU_DONJON = '[color=#FFC663]Fosse Cascade[color]'
local LIEU_FOND = '[color=#FFC663]Fosse Cascade Fond[color]'
local LIEU_VILLE = '[color=#FFC663]Réverie Town[color]'

local SOL_BOSS = {x = 244, y = 244}
-- Chacun garde un axe de marche libre, sans zigzag de quelques pixels.
local SOL_HEROS = {x = 240, y = 264}
local SOL_PARTENAIRE = {x = 216, y = 264}
local SOL_NILO_TERRASSE = {x = 256, y = 160}
local RECUL_Y = 288 -- duo à 4 px de ses centres de case dans l’arène
local CAM_FACE = {x = 252, y = 224}
local CAM_DUEL_Y = 240 -- limite Clamp sur la carte 480×360

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

-- Émotes réellement déclarées dans base/Data/Emote (le nom est sensible à la
-- casse) : angry, eating, exclaim, glowing, happy, notice, question, shock,
-- sweatdrop, sweating, reveil, pose_infirmiere. Un identifiant inconnu rend
-- nil dans DataManager.GetEmote et ferait planter StartEmote.
local EMOTES_SURS = {
  angry = true, eating = true, exclaim = true, glowing = true, happy = true,
  notice = true, pose_infirmiere = true, question = true, reveil = true,
  shock = true, sweatdrop = true, sweating = true,
}

local function emote_sur(ch, nom, son)
  if ch == nil then return end
  if not EMOTES_SURS[nom] then
    print('[fgv1] emote inconnue ignoree : ' .. tostring(nom))
    return
  end
  pcall(function()
    cinematique.Emote(ch, nom, son)
  end)
end

local function secouer_ecran(dx, dy, duree)
  pcall(function()
    GROUND:MoveScreen(RogueEssence.Content.ScreenMover(dx, dy, duree))
  end)
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

-- On gèle les reflets sur la première phase (TileLayer.Draw : FrameLength <= 0)
-- et on masque les bulles. Le décor, ses sols et ses collisions restent en place.
-- C'est uniquement l'instance du pré-combat, pas les vasques de la visite libre.
local function suspendre_eau_precombat(map)
  local reflets, bulles, bulles_visibles = {}, nil, nil
  if map ~= nil and map.Layers ~= nil then
    for i = 0, map.Layers.Count - 1 do
      local calque = map.Layers[i]
      if calque.Name == '06 reflets vasques 12 phases' then
        for x = 0, calque.Width - 1 do
          for y = 0, calque.Height - 1 do
            local pistes = calque.Tiles[x][y].Layers
            for j = 0, pistes.Count - 1 do
              local piste = pistes[j]
              if piste.Frames.Count > 1 and piste.FrameLength > 0 then
                reflets[#reflets + 1] = {piste, piste.FrameLength}
                piste.FrameLength = 0
              end
            end
          end
        end
      elseif calque.Name == '07 bulles source 24 phases' then
        bulles, bulles_visibles = calque, calque.Visible
        bulles.Visible = false
      end
    end
  end
  return function()
    for _, r in ipairs(reflets) do r[1].FrameLength = r[2] end
    if bulles ~= nil then bulles.Visible = bulles_visibles end
  end
end

-- Garde le temps et l'impact de la feuille réellement chargée, pas d'une
-- animation supposée. Une animation absente n'immobilise pas l'acteur.
local function temps_animation(ch, nom)
  local total, impact
  pcall(function()
    local gm = RogueEssence.Content.GraphicsManager
    local idx = gm.GetAnimIndex(nom)
    if idx < 0 then return end
    local feuille = gm.GetChara(ch.CurrentForm:ToCharID())
    if feuille:GetReferencedAnimIndex(idx) ~= idx then return end
    total = tonumber(feuille:GetTotalTime(idx, ch.Direction))
    impact = tonumber(feuille:GetHitTime(idx, ch.Direction))
  end)
  if total ~= nil and total > 0 then return total, impact end
end

-- L'impact de la patte suit la planche réellement chargée. L'appelant
-- choisit le son : un seul effet par action, même quand les deux héros reculent.
local function armer_faux(kabutops)
  local total, impact = temps_animation(kabutops, 'Attack')
  total = total or 24
  impact = math.max(0, math.min(total - 1, impact or 8))
  GROUND:CharSetAnim(kabutops, 'Attack', false)
  if impact > 0 then GAME:WaitFrames(impact) end
  return total - impact
end

local function souffle_du_gardien(kabutops, hero, partenaire)
  local fin_faux = armer_faux(kabutops)
  SOUND:PlayBattleSE('DUN_Gust_Trap')
  secouer_ecran(4, 4, 22)
  local actions = {
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(fin_faux)
      GROUND:CharEndAnim(kabutops)
    end),
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(CAM_FACE.x, CAM_DUEL_Y, 16, false)
    end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(68) -- le souffle de 1,125 s se termine avant la reprise musicale
    end),
  }
  local function glisser(ch, x, delai)
    if ch == nil then return end
    actions[#actions + 1] = TASK:BranchCoroutine(function()
      if delai > 0 then GAME:WaitFrames(delai) end
      -- Hurt maintient le regard vers Kabutops : ils glissent, ils ne font
      -- pas demi-tour pour fuir. Le partenaire encaisse trois images plus tard.
      GROUND:AnimateToPosition(ch, 'Hurt', ch.Direction, x, RECUL_Y, 1, 2.4, 0)
      GROUND:CharEndAnim(ch)
    end)
  end
  glisser(hero, SOL_HEROS.x, 0)
  glisser(partenaire, SOL_PARTENAIRE.x, 3)
  TASK:JoinCoroutines(actions)
end

-- Bandes natives de BossTransition (Pre_Battle), sans son double éclair
-- d'introduction. On garde les bandes visibles pendant les deux temps du
-- woosh, et l'arène déclenche elle-même sa musique. Rien n'est rejoué par
-- l'arène : le woosh se termine avant ContinueDungeon / EnterDungeon.
local function woosh_duel()
  local centre = GAME:GetCameraCenter()
  local bandes = {{-32}, {-64, 0}, {-112, 48}, {-144, 80}, {-176, 112}}
  SOUND:FadeOutBGM(24) -- passage de la musique au son du woosh
  SOUND:PlayBattleSE('EVT_Battle_Transition')
  for groupe, hauteurs in ipairs(bandes) do
    if groupe > 1 then GAME:WaitFrames(5) end
    for _, y in ipairs(hauteurs) do
      local bande = RogueEssence.Content.FiniteOverlayEmitter()
      bande.FadeIn = 24
      bande.TotalTime = 164
      bande.RepeatX = true
      bande.Movement = RogueElements.Loc(groupe % 2 == 1 and 360 or -360, 0)
      bande.Layer = DrawLayer.Top
      local cadre = math.max(0, groupe - 2)
      bande.Anim = RogueEssence.Content.BGAnimData('Pre_Battle', 1, cadre, cadre)
      GROUND:PlayVFX(bande, centre.X, centre.Y + y)
    end
  end
  -- 20 + 112 + 24 + 32 = 188 images : l'OGG fait 3,105 s (187 images
  -- arrondies à 60 i/s). Le noir ne commence qu'après le second accent.
  GAME:WaitFrames(112)
  GAME:FadeOut(false, 24)
  GAME:WaitFrames(32)
end

function fgv1.PreBattle(is_rematch, map)
  -- Une interruption suivie d'une réentrée ne doit pas rejouer la découverte.
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  GAME:CutsceneMode(true)
  local retablir_eau = suspendre_eau_precombat(map)
  local hero = CH('PLAYER')
  local entree_y = is_rematch and 320 or 344
  local partenaire = equipe_scene.Partenaire(SOL_PARTENAIRE.x, entree_y, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo',
    SOL_NILO_TERRASSE.x, SOL_NILO_TERRASSE.y, Direction.Down)
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    SOL_BOSS.x, SOL_BOSS.y, Direction.Down)
  if not is_rematch then GROUND:Hide('Kabutops_Boss') end
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, SOL_HEROS.x, entree_y, Direction.Up)
  end

  GAME:MoveCamera(CAM_FACE.x, CAM_DUEL_Y, 1, false)
  GAME:FadeIn(18)
  SOUND:PlayBGM(is_rematch and 'Rising Fear.ogg' or 'Lower Spring Cave.ogg', false)

  local cible = is_rematch and kabutops or nilo
  local arrivee = {TASK:BranchCoroutine(function()
    if not is_rematch then GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 38, false) end
  end)}
  local function approcher(ch, sol, delai)
    if ch == nil then return end
    arrivee[#arrivee + 1] = TASK:BranchCoroutine(function()
      if delai > 0 then GAME:WaitFrames(delai) end
      GROUND:MoveToPosition(ch, sol.x, sol.y, false, 1.6)
      regarder_cible(ch, cible, 4)
    end)
  end
  approcher(partenaire, SOL_PARTENAIRE, 0)
  approcher(hero, SOL_HEROS, 5)
  TASK:JoinCoroutines(arrivee)
  cinematique.Respirer(12)

  if not is_rematch then
    if partenaire ~= nil then
      emote_sur(partenaire, 'notice')
      GAME:WaitFrames(8)
      cinematique.Dire(partenaire, 'Worried', 'Nilo ! On vient te ramener. Ta mère t’attend.', 'standard')
      UI:ResetSpeaker()
      cinematique.Respirer(12)
    end
    -- Nilo ne descend pas et ne tremble pas : sa phrase porte son inquiétude.
    cinematique.Dire(nilo, 'Worried', 'J’ai touché aux vasques… Depuis, le courant a changé. C’est ma faute.', 'droite')
    UI:ResetSpeaker()
    SOUND:FadeOutBGM(20)
    GAME:WaitFrames(24)

    -- Une seule révélation. Le joueur voit d'abord le gardien, puis le coup
    -- qui déclenche le souffle, sans bruit d'eau ni deuxième éclair de boss.
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    GAME:FadeOut(true, 3)
    GROUND:Unhide('Kabutops_Boss')
    GAME:FadeIn(12)
    cinematique.RegarderGroupe({{partenaire, kabutops, 0, 4}, {hero, kabutops, 5, 4}})
    GAME:WaitFrames(14)
    souffle_du_gardien(kabutops, hero, partenaire)
    SOUND:PlayBGM('Rising Fear.ogg', false)
    cinematique.Dire(kabutops, 'Angry', 'Ces vasques sont sous ma garde. Le petit vous a dit ce qu’il a fait ?', 'droite')
    UI:ResetSpeaker()
    if partenaire ~= nil then
      regarder_cible(partenaire, nilo, 4)
      cinematique.Respirer(10)
      regarder_cible(partenaire, kabutops, 4)
      cinematique.Dire(partenaire, 'Determined', 'On n’est pas venus se battre. Laisse-nous repartir avec lui.', 'standard')
      UI:ResetSpeaker()
    end
    cinematique.Respirer(16)
    cinematique.Dire(kabutops, 'Determined', 'Pas un pas de plus.', 'droite')
  else
    -- Même raccord d'arène, sans réveil, éclair ou souffle rejoué.
    cinematique.Dire(kabutops, 'Determined', 'Encore vous ? Cette fois, tenez-vous prêts.', 'droite')
  end

  UI:ResetSpeaker()
  cinematique.Respirer(18)
  woosh_duel()
  retablir_eau() -- à noir complet, y compris si l'éditeur conserve l'instance
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  lancer_duel_boss()
end

function fgv1.PostBattle()
  local hero = CH('PLAYER')
  -- Axe central x=256 laissé libre pour l'arrivée de Lyra depuis le sud.
  local partenaire = equipe_scene.Partenaire(208, 240, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo', 296, 240, Direction.Left)
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    SOL_BOSS.x, SOL_BOSS.y, Direction.Down)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 208, 280, Direction.Up)
  end
  SOUND:FadeOutBGM(12)
  GAME:MoveCamera(CAM_FACE.x, CAM_DUEL_Y, 1, false)
  GAME:WaitFrames(12)
  GAME:FadeIn(20)
  GAME:WaitFrames(16)
  trembler_de_peur(nilo)

  emote_sur(kabutops, 'sweatdrop')
  GAME:WaitFrames(10)
  cinematique.Dire(kabutops, 'Pain', 'Vous avez gagné… Emmenez le petit.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(16)
  cinematique.RegarderGroupe({{nilo, kabutops, 0, 4}, {partenaire, kabutops, 5, 4}, {hero, kabutops, 9, 4}})
  cinematique.Dire(nilo, 'Worried', 'On peut vraiment rentrer ?', 'droite')
  UI:ResetSpeaker()
  regarder_cible(kabutops, nilo, 4)
  cinematique.Respirer(12)
  cinematique.Dire(kabutops, 'Pain', 'Partez. Ne me faites pas regretter de vous laisser passer.', 'droite')
  UI:ResetSpeaker()

  -- La caméra garde le groupe dans le champ. Kabutops sort réellement
  -- par le couloir sud ; le bruit de pas part avec son premier déplacement.
  tourner_vers(kabutops, Direction.Down, 4)
  cinematique.Respirer(16)
  arreter_tremblement(nilo)
  SOUND:PlayBattleSE('DUN_Tile_Step')
  GROUND:MoveToPosition(kabutops, 256, 344, true, 3)
  GAME:WaitFrames(8)
  GROUND:RemoveCharacter('Kabutops_Boss')
  cinematique.Respirer(12)
  SOUND:PlayBGM('Lower Spring Cave.ogg', false)
  GROUND:MoveToPosition(nilo, 296, 272, false, 1.4)
  regarder_cible(nilo, hero or partenaire, 4)
  cinematique.Dire(nilo, 'Teary-Eyed', 'J’ai cru que je ne reverrais pas maman… Merci d’être venus.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(18)

  -- L'arrivée de Lyra motive les regards. Le duo ne tourne pas le dos à
  -- Lyra pour jouer une émote après qu'elle s'est déjà placée devant lui.
  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', 256, 344, Direction.Up)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() GROUND:MoveToPosition(lyra, 256, 248, true, 2) end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(16)
      if nilo ~= nil then emote_sur(nilo, 'exclaim', 'EVT_Emote_Exclaim_2') end
      cinematique.RegarderGroupe({{nilo, lyra, 0, 4}, {partenaire, lyra, 5, 4}, {hero, lyra, 9, 4}})
    end),
  })
  cinematique.RegarderGroupe({{lyra, nilo, 0, 4}, {nilo, lyra, 5, 4}, {partenaire, lyra, 7, 4}, {hero, lyra, 11, 4}})
  cinematique.Respirer(10)
  cinematique.Dire(lyra, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' ! Tu n’as rien ?', 'standard')
  UI:ResetSpeaker()
  cinematique.Respirer(14)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman… Je suis désolé.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(18)
  cinematique.Dire(lyra, 'Teary-Eyed', 'Tu es là. C’est tout ce qui compte.', 'standard')
  UI:ResetSpeaker()
  cinematique.Respirer(20)
  regarder_cible(lyra, hero or partenaire, 4)
  cinematique.Dire(lyra, 'Happy', 'Merci à vous deux. On rentre à ' .. LIEU_VILLE .. ' ?', 'standard')
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  -- Dernier fondu des retrouvailles ; durée musique/image alignée sur le guide.
  SOUND:FadeOutBGM(60)
  GAME:FadeOut(false, 60)
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
  if not GAME:DungeonUnlocked('grotte_verdoyante') then
    GAME:UnlockDungeon('grotte_verdoyante')
    SV.Destiny.AvisOuvertureFosse = true
  end
  missions_reverie.Completer('grotte_verdoyante', true)

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
    fgv1.PreBattle(true, map)
  else
    fgv1.PreBattle(false, map)
  end
end

function fgv1.GameLoad(map)
  -- La carte ne déclare pas de piste (Music = ''), contrairement à
  -- ewc3_entree_waterfall_cave : sans cette relance, une sauvegarde chargée
  -- pendant une scène des vasques restait muette jusqu'à la fin du donjon.
  GAME:FadeIn(20)
  -- Pendant la révélation de Kabutops, la scène a coupé la musique et joue
  -- Rising Fear : ne pas la remplacer sous la scène en cours.
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.GrotteVerdoyantePhase ~= 1 then
    SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  end
end

function fgv1.Update(map, time) end

return fgv1
