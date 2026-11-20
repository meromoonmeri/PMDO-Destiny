-- Fosse Cascade Fond (fin de la Fosse Cascade : fgv1_fin_grotte_vasques, 480x360).
-- Quatre phases selon l'avancement :
--   * PreBattle(false) : Nilo est retrouvé, mais sa mise en garde est interrompue.
--                        Un éclair vide, voix dans le noir, double éclair puis
--                        Kabutops sur le sable, sans animation d'eau.
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
local SOL_HEROS = {x = 220, y = 272}
local SOL_PARTENAIRE = {x = 260, y = 276}
local SOL_NILO_REVEIL = {x = 285, y = 228}
local SOL_NILO_TERREUR = {x = 304, y = 256}
local CAM_FACE = {x = 240, y = 240}
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

local function coup_de_faux(kabutops)
  -- Attack est natif sur Kabutops ; selon la planche, Swing peut l'être aussi.
  local nom = 'Attack'
  local total, impact = temps_animation(kabutops, nom)
  total = total or 24
  impact = math.max(0, math.min(total - 1, impact or 8))
  GROUND:CharSetAnim(kabutops, nom, false)
  if impact > 0 then GAME:WaitFrames(impact) end
  SOUND:PlayBattleSE('DUN_Slash')
  secouer_ecran(1, 3, 12)
  GAME:WaitFrames(total - impact)
  GROUND:CharEndAnim(kabutops)
end

function fgv1.PreBattle(is_rematch, map)
  GAME:CutsceneMode(true)
  local retablir_eau = suspendre_eau_precombat(map)
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(240, 344, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo',
    SOL_NILO_REVEIL.x, SOL_NILO_REVEIL.y, Direction.DownLeft)
  if not is_rematch then GROUND:CharSetAnim(nilo, 'EventSleep', true) end
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    SOL_BOSS.x, SOL_BOSS.y, Direction.Down)
  if not is_rematch then GROUND:Hide('Kabutops_Boss') end

  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, 216, 344, Direction.Up)
  end

  GAME:MoveCamera(CAM_ENTREE.x, CAM_ENTREE.y, 1, false)
  if not is_rematch then
    UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 16)
    GAME:WaitFrames(22)
    UI:WaitHideTitle(14)
  end
  GAME:FadeIn(18)
  SOUND:PlayBGM(is_rematch and 'Rising Fear.ogg' or 'Lower Spring Cave.ogg', true)

  -- Repérer Nilo dans le cadre avant de parler. Le duo ne traverse aucune marche.
  local arrivee = {
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 40, false)
    end),
  }
  if hero ~= nil then
    arrivee[#arrivee + 1] = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y, false, 1.6)
      regarder_cible(hero, is_rematch and kabutops or nilo, 3)
    end)
  end
  if partenaire ~= nil then
    arrivee[#arrivee + 1] = TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y, false, 1.8)
      regarder_cible(partenaire, is_rematch and kabutops or nilo, 3)
    end)
  end
  TASK:JoinCoroutines(arrivee)
  GAME:WaitFrames(8)

  if not is_rematch then
    if partenaire ~= nil then
      cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim')
      GAME:WaitFrames(12)
      cinematique.Dire(partenaire, 'Worried', 'Nilo ?[pause=10] Ta maman nous a envoyés. On vient te ramener.', 'standard')
    end
    UI:ResetSpeaker()
    -- Le dialogue a une vraie respiration avant le réveil (repère PMDO : 20 f).
    cinematique.Respirer(20)
    GROUND:CharEndAnim(nilo)
    local duree = temps_animation(nilo, 'Wake')
    if duree ~= nil then
      GROUND:CharSetAnim(nilo, 'Wake', false)
      GAME:WaitFrames(duree)
      GROUND:CharEndAnim(nilo)
    end
    regarder_cible(nilo, partenaire or hero, 3)
    GAME:WaitFrames(20)
    cinematique.Dire(nilo, 'Dizzy', 'Maman…?[pause=10] Attendez. Ne bougez plus.', 'droite')
    UI:ResetSpeaker()

    -- Avertissement interrompu : le choc coupe la musique plutôt que de lancer
    -- aussitôt un autre thème. Au premier éclair, la clairière est encore vide.
    couper_musique_choc()
    GAME:WaitFrames(14)
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    eclair_blanc(3, 11)
    GAME:WaitFrames(8)
    local reactions = {
      TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(nilo, SOL_NILO_TERREUR.x, SOL_NILO_TERREUR.y, true, 2)
        tourner_vers(nilo, Direction.UpLeft, 3)
        trembler_de_peur(nilo)
      end),
    }
    if hero ~= nil then
      reactions[#reactions + 1] = TASK:BranchCoroutine(function()
        tourner_vers(hero, Direction.UpLeft, 3)
        GAME:WaitFrames(10)
        tourner_vers(hero, Direction.UpRight, 3)
      end)
    end
    if partenaire ~= nil then
      reactions[#reactions + 1] = TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        cinematique.Emote(partenaire, 'question', 'EVT_Emote_Confused')
        tourner_vers(partenaire, Direction.Up, 3)
      end)
    end
    TASK:JoinCoroutines(reactions)
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Surprised', 'Tu as vu ?[pause=8] Il n’y avait rien, juste devant nous…', 'standard')
    end
    cinematique.Dire(nilo, 'Crying', 'Cette fois, il est tout près…', 'droite')
    UI:ResetSpeaker()
    cinematique.Respirer(20)

    -- Le noir donne à la voix le temps d’être identifiée avant la révélation.
    -- Aucun portrait ni geyser, et la musique reste coupée sous la voix.
    SOUND:PlayBattleSE('EVT_Tower_Tremor_Weak')
    secouer_ecran(2, 4, 16)
    GAME:FadeOut(false, 10)
    GAME:WaitFrames(30)
    parler_voix_abysses('Vous avez entendu le premier grondement.[pause=12] Le second est pour vous.')
    regarder_cible(hero, kabutops, 3)
    regarder_cible(partenaire, kabutops, 3)
    GAME:FadeIn(12)
    GAME:WaitFrames(20)

    -- Le premier éclat ne montre toujours personne. Le deuxième révèle
    -- Kabutops sur le sable plat, sans déplacement visible pendant le blanc.
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    eclair_blanc(3, 9)
    GAME:WaitFrames(24)
    SOUND:PlayBattleSE('EVT_Battle_Flash')
    GAME:FadeOut(true, 3)
    GROUND:Unhide('Kabutops_Boss')
    GAME:FadeIn(9)
    GAME:WaitFrames(8)
    coup_de_faux(kabutops)
    GAME:WaitFrames(9)
    SOUND:PlayBGM('Rising Fear.ogg', true)

    cinematique.Dire(kabutops, 'Angry', 'Cette fosse m’appartient. Faites demi-tour.', 'droite')
    UI:ResetSpeaker()
    -- Au lieu de rester côte à côte, le duo couvre Nilo : le partenaire se
    -- décale à droite pendant que le héros serre la ligne face au gardien.
    local garde = {}
    if hero ~= nil then
      garde[#garde + 1] = TASK:BranchCoroutine(function()
        GROUND:MoveToPosition(hero, 236, 272, false, 1.4)
        regarder_cible(hero, kabutops, 3)
      end)
    end
    if partenaire ~= nil then
      garde[#garde + 1] = TASK:BranchCoroutine(function()
        GAME:WaitFrames(5)
        GROUND:MoveToPosition(partenaire, 272, 288, false, 1.6)
        regarder_cible(partenaire, kabutops, 3)
      end)
    end
    if #garde > 0 then TASK:JoinCoroutines(garde) end
    if partenaire ~= nil then
      -- La protection devient un échange : le partenaire se place devant Nilo,
      -- puis Nilo lui répond au lieu de passer directement au cri du boss.
      regarder_cible(nilo, partenaire, 4)
      GAME:WaitFrames(18)
      cinematique.Dire(partenaire, 'Determined', 'Nilo, derrière moi.[pause=8] On ne repartira pas sans toi.', 'standard')
      GAME:WaitFrames(12)
      cinematique.Emote(nilo, 'sweating')
      regarder_cible(nilo, partenaire, 4)
      cinematique.Dire(nilo, 'Worried', 'Je… je ne veux pas que vous soyez blessés à cause de moi. Ses faux sont trop rapides…', 'droite')
      cinematique.Respirer(24)
      regarder_cible(partenaire, nilo, 4)
      cinematique.Dire(partenaire, 'Worried', 'Tu as peur, je comprends. Mais tu n’es plus seul, Nilo. Regarde-nous : on reste avec toi.', 'standard')
      GAME:WaitFrames(16)
      regarder_cible(nilo, kabutops, 4)
    end

    -- Kabutops reprend la parole après avoir laissé le duo se placer :
    -- son emote et son regard marquent l’escalade avant la riposte.
    cinematique.Respirer(18)
    cinematique.Emote(kabutops, 'angry', 'EVT_Emote_Complain')
    regarder_cible(kabutops, hero or partenaire, 4)
    cinematique.Dire(kabutops, 'Angry', 'Assez ! Si vous refusez de partir, je vous chasserai moi-même de mes vasques.', 'droite')
    UI:ResetSpeaker()
    cinematique.RegarderGroupe({
      {partenaire, kabutops, 0, 4},
      {hero, kabutops, 5, 4},
      {nilo, kabutops, 10, 4},
    })
    GAME:WaitFrames(20)
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'Alors, il faudra d’abord nous passer sur le corps.', 'standard')
      cinematique.Respirer(18)
    end
  else
    -- Pas de réveil ni de révélation rejoués lors d'une revanche.
    coup_de_faux(kabutops)
    cinematique.Dire(kabutops, 'Angry', 'Vous êtes revenus. La fosse ne vous laissera pas passer deux fois.', 'droite')
    if partenaire ~= nil then
      cinematique.Dire(partenaire, 'Determined', 'On reste ensemble. Cette fois, on ramène Nilo.', 'standard')
    end
  end

  cinematique.Respirer(20)
  cinematique.Dire(kabutops, 'Shouting', 'Alors, tenez bon !', 'droite')
  UI:ResetSpeaker()
  SOUND:FadeOutBGM(18)
  SOUND:PlayBattleSE('EVT_Battle_Transition')
  GAME:FadeOut(false, 18) -- même durée que le fondu de musique
  GAME:WaitFrames(30) -- transition standard entre cinématique et duel
  SOUND:PlayBGM('Boss Battle 2.ogg', true)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  arreter_tremblement(nilo)
  retablir_eau() -- à noir complet, y compris si l'éditeur conserve l'instance
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  lancer_duel_boss()
end

function fgv1.PostBattle()
  local hero = CH('PLAYER')
  -- Formation aérée au centre du cadre : les deux membres du duo restent
  -- séparés de 40 px et aucun trajet de retrouvailles ne traverse leur ligne.
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
  GAME:MoveCamera(CAM_FACE.x, CAM_FACE.y, 1, false)
  GAME:WaitFrames(12)
  GAME:FadeIn(20)
  GAME:WaitFrames(12)
  trembler_de_peur(nilo)

  cinematique.Emote(kabutops, 'sweatdrop', 'EVT_Emote_Sweatdrop')
  GAME:WaitFrames(12)
  cinematique.Dire(kabutops, 'Pain', 'Ksshh… Votre détermination surpasse la fureur du courant… Emportez le petit et laissez mes vasques en paix.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(24)
  cinematique.RegarderGroupe({
    {nilo, kabutops, 0, 4},
    {partenaire, kabutops, 4, 4},
    {hero, kabutops, 8, 4},
  })
  GAME:WaitFrames(12)
  cinematique.Dire(nilo, 'Worried', 'Tu… tu nous laisses vraiment partir ?', 'droite')
  cinematique.Respirer(18)
  regarder_cible(kabutops, nilo, 4)
  cinematique.Dire(kabutops, 'Pain', 'Tu m’as vaincu. Ne me force pas à changer d’avis : partez.', 'droite')
  cinematique.Respirer(18)
  if partenaire ~= nil then
    regarder_cible(partenaire, kabutops, 4)
    cinematique.Dire(partenaire, 'Determined', 'On ne te cherchera pas querelle. On rentre avec Nilo.', 'standard')
    cinematique.Respirer(20)
  end

  -- Kabutops détourne le regard et choisit de se retirer; Nilo cesse alors de trembler.
  tourner_vers(kabutops, Direction.Down, 4)
  GAME:WaitFrames(18)
  arreter_tremblement(nilo)

  -- Kabutops vaincu fuit vers le sud EN COURANT (plus aucun effet d'eau).
  GAME:WaitFrames(4)
  local fuite = {
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(240, 240, 16, false)
    end),
    TASK:BranchCoroutine(function()
      -- Le pas part avec le premier mouvement, pas avant la course.
      SOUND:PlayBattleSE('DUN_Tile_Step')
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
      -- Nilo rejoint le côté droit du cadre, sans croiser l'axe d'arrivée de Lyra.
      GROUND:MoveToPosition(nilo, 296, 272, true, 2)
      tourner_vers(nilo, Direction.Down, 4)
    end),
  }
  TASK:JoinCoroutines(retour_nilo)
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(20)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Vous… vous avez vraiment tenu tête à ' .. cinematique.NomEspece('kabutops', 'Kabutops') .. ' pour me sauver !!', 'droite')
  cinematique.Respirer(20)

  -- Lyra monte par le couloir sud dégagé (x = 256). Les positions du duo et
  -- de Nilo laissent cet axe libre : aucune trajectoire ne traverse un autre acteur.
  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', 256, 344, Direction.Up)
  GROUND:MoveToPosition(lyra, 256, 248, true, 2)
  cinematique.RegarderGroupe({
    {lyra, nilo, 0, 4},
    {nilo, lyra, 3, 4},
    {partenaire, lyra, 6, 4},
    {hero, lyra, 10, 4},
  })
  GAME:WaitFrames(10) -- laisser le groupe enregistrer l'arrivée avant la réplique

  -- Ne pas afficher le portrait de Lyra avant son entrée à l'écran.
  cinematique.Dire(lyra, 'Worried', cinematique.NomColore('Nilo', 'shinx') .. ' !! Est-ce que tout le monde va bien ?!', 'standard')
  local reactions_appel = {
    TASK:BranchCoroutine(function()
      cinematique.Emote(nilo, 'exclaim', 'EVT_Emote_Exclaim_2')
    end),
  }
  if partenaire ~= nil then
    table.insert(reactions_appel, TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      cinematique.Emote(partenaire, 'exclaim')
    end))
  end
  if hero ~= nil then
    table.insert(reactions_appel, TASK:BranchCoroutine(function()
      GAME:WaitFrames(11)
      cinematique.Emote(hero, 'exclaim')
    end))
  end
  TASK:JoinCoroutines(reactions_appel)
  GAME:WaitFrames(30) -- laisser finir le SFX de groupe avant le son du saut

  SOUND:PlayBattleSE('EVT_Emote_Startled')
  GROUND:CharSetAnim(nilo, 'Hop', false)
  GAME:WaitFrames(16)
  if GROUND.CharEndAnim ~= nil then GROUND:CharEndAnim(nilo) end
  cinematique.Emote(nilo, 'happy')
  GAME:WaitFrames(20)
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman !! Tu nous as rejoints jusqu’ici !', 'droite')
  cinematique.Respirer(20)
  cinematique.Dire(lyra, 'Teary-Eyed', 'Mon petit ' .. cinematique.NomColore('Nilo', 'shinx') .. '… Quand le fracas du torrent s’est apaisé, je me suis précipitée dans la grotte ! Quel bonheur de te revoir sain et sauf…', 'standard')
  cinematique.Respirer(20)

  regarder_cible(lyra, hero or partenaire, 4)
  cinematique.Dire(lyra, 'Happy', 'Merci infiniment à tous les deux ! Sans votre bravoure, je n’ose même pas imaginer ce qui serait arrivé.', 'droite')
  if partenaire ~= nil then
    cinematique.Respirer(20)
    cinematique.Dire(partenaire, 'Happy', 'L’essentiel, c’est que vous soyez réunis ! Vite, rentrons à ' .. LIEU_VILLE .. ' annoncer la bonne nouvelle à Léo et aux habitants !', 'standard')
  end
  cinematique.Respirer(20)
  cinematique.Dire(nilo, 'Happy', 'Oui !! Rentrons tous ensemble !', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(20)

  -- Dernier fondu des retrouvailles ; COMMON.EndDungeonDay ouvre ensuite le bilan natif.
  -- Retrouvailles émotionnelles : fondu musique/image prolongé et apparié.
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
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)
end

function fgv1.Update(map, time) end

return fgv1
