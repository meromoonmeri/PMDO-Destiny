-- Fosse Cascade Fond (576×528, antichambre au sud et salle haute).
-- 0 : sauvetage de Nilo, accusation, sortie de terre du gardien et de sa garde.
-- 1 : revanche courte, sans rejouer la découverte.
-- 3 : retrouvailles et bilan natif après le duel. 4 : visite paisible.
-- La salle haute commence à x=48 ; l'arène garde son rectangle de 480×360.
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'
local fosse = require 'destiny.fosse_cascade_scene'

local fgv1 = {}

local LIEU_DONJON = '[color=#FFC663]Fosse Cascade[color]'
local LIEU_FOND = '[color=#FFC663]Fosse Cascade Fond[color]'
local LIEU_VILLE = '[color=#FFC663]Réverie Town[color]'

-- Le sol de la scène et les départs du donjon partagent leurs centres.
-- Le duo s’arrête une case devant sa position de duel, puis y est repoussé.
local SALLE_X = fosse.SALLE_X
local function ancre(case)
  local x, y = fosse.AncreAuSol(case)
  return {x=x, y=y}
end
local SOL_BOSS = ancre(fosse.DUEL.boss)
local DUEL_HEROS = ancre(fosse.DUEL.hero)
local DUEL_PARTENAIRE = ancre(fosse.DUEL.partenaire)
local AXE_DUO = math.floor((DUEL_PARTENAIRE.x + DUEL_HEROS.x) / 2)
local SOL_HEROS = {x=DUEL_HEROS.x, y=DUEL_HEROS.y - 24}
local SOL_PARTENAIRE = {x=DUEL_PARTENAIRE.x, y=DUEL_PARTENAIRE.y - 24}
local APPARITION_BOSS = {x=AXE_DUO, y=SOL_BOSS.y}
local SOL_NILO_TERRASSE = fosse.NILO_TERRASSE
local RECUL_Y = DUEL_HEROS.y

-- Placement propre à la phase 3, installé avant le fondu. Les ombres du trio
-- partagent la même ligne, à 32 px de part et d’autre du chef. Ne pas déplacer
-- les ancres d’apparition ou de duel pour obtenir cette formation.
local APRES_DUEL = {boss=AXE_DUO, partenaire=AXE_DUO - 32, hero=AXE_DUO + 32, y=RECUL_Y}
local REUNION = {axe=SOL_NILO_TERRASSE.x, duo_y=RECUL_Y + 16, nilo_y=RECUL_Y + 12, lyra_y=RECUL_Y + 44}
local ENTREE_HEROS = {x = 222, y = 492}
local ENTREE_PARTENAIRE = {x = 198, y = 484}
local COUDE_HEROS = {x = 246, y = 436}
local COUDE_PARTENAIRE = {x = 222, y = 430}
local SEUIL_HEROS = {x = 292, y = 368}
local SEUIL_PARTENAIRE = {x = 268, y = 362}

local CAM_DUEL_X = 300
local CAM_DUEL_Y = 240 -- centre effectif de l'arène une fois clampée
local CAM_ENTREE = {x = 230, y = 406}
local CAM_SEUIL = {x = 278, y = 372}
local CAM_TERRASSE_Y = 216
local CAM_FACE_Y = 226 -- l’arrêt du duo laisse un champ libre derrière lui
local CAM_CERCLE_Y = 246 -- inclut les deux jaillissements dans le sable du passage
local CAM_NILO_REPLI_Y = 218
local CAM_REVANCHE_Y = 242
local CAM_VICTOIRE_X = APRES_DUEL.boss + 8 -- centre de l’ombre de Kabutops
local CAM_VICTOIRE_Y = 242
local CAM_REUNION_Y = 250

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
local EFFETS_DESSIN = {Shaking = 2}

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
local carte_eau, restaurer_eau
local function suspendre_eau_precombat(map)
  -- En cas de réentrée dans la même instance, ne pas prendre la cadence
  -- déjà gelée comme référence. La revanche rend les cadences d'origine.
  if map ~= nil and map == carte_eau then return restaurer_eau end
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
  local function restaurer()
    for _, r in ipairs(reflets) do r[1].FrameLength = r[2] end
    if bulles ~= nil then bulles.Visible = bulles_visibles end
    if carte_eau == map then carte_eau, restaurer_eau = nil, nil end
  end
  carte_eau, restaurer_eau = map, restaurer
  return restaurer
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
      GAME:MoveCamera(CAM_DUEL_X, CAM_FACE_Y, 24, false)
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

-- Premier plan : la caméra accompagne le coude de l'antichambre, sans
-- encore voir la terrasse. Le partenaire atteint le seuil en premier.
local function traverser_passage(hero, partenaire)
  GAME:MoveCamera(CAM_ENTREE.x, CAM_ENTREE.y, 1, false)
  SOUND:PlayBGM('Lower Spring Cave.ogg', false)
  GAME:FadeIn(18)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(9)
      GAME:MoveCamera(CAM_SEUIL.x, CAM_SEUIL.y, 86, false)
    end),
    TASK:BranchCoroutine(function()
      if partenaire == nil then return end
      GROUND:MoveToPosition(partenaire, COUDE_PARTENAIRE.x, COUDE_PARTENAIRE.y, false, 1.55)
      GROUND:MoveToPosition(partenaire, SEUIL_PARTENAIRE.x, SEUIL_PARTENAIRE.y, false, 1.65)
    end),
    TASK:BranchCoroutine(function()
      if hero == nil then return end
      GAME:WaitFrames(7)
      GROUND:MoveToPosition(hero, COUDE_HEROS.x, COUDE_HEROS.y, false, 1.55)
      GROUND:MoveToPosition(hero, SEUIL_HEROS.x, SEUIL_HEROS.y, false, 1.65)
    end),
  })
end

-- Deuxième plan : un regard motive le panoramique. Nilo entre dans le
-- cadre par le haut ; personne ne parle avant que le duo ait rejoint le pied
-- de sa terrasse, comme au passage de Cotovol au fond du Val Silencieux.
local function au_pied_de_la_terrasse(hero, partenaire, nilo)
  regarder_cible(partenaire or hero, nilo, 4)
  emote_sur(partenaire or hero, 'notice')
  GAME:WaitFrames(16)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() GAME:MoveCamera(CAM_DUEL_X, CAM_TERRASSE_Y, 72, false) end),
    TASK:BranchCoroutine(function()
      if partenaire == nil then return end
      GAME:WaitFrames(5)
      GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, SOL_PARTENAIRE.y, false, 1.65)
    end),
    TASK:BranchCoroutine(function()
      if hero == nil then return end
      GAME:WaitFrames(12)
      GROUND:MoveToPosition(hero, SOL_HEROS.x, SOL_HEROS.y, false, 1.65)
    end),
  })
  cinematique.RegarderGroupe({{partenaire, nilo, 0, 4}, {hero, nilo, 5, 4}})
  cinematique.Respirer(13)
end

local function dire(ch, emotion, texte, cote)
  if ch == nil then return end
  cinematique.Dire(ch, emotion, texte, cote)
  UI:ResetSpeaker()
end

local function premiere_rencontre(hero, partenaire, nilo)
  dire(nilo, 'Worried', 'Vous êtes qui… ? Pourquoi vous êtes venus ici ?', 'droite')
  if partenaire ~= nil then
    regarder_cible(hero, partenaire, 4)
    cinematique.Respirer(18)
    dire(partenaire, 'Normal', 'On est une équipe de secours. Ta maman nous a demandé de te ramener.', 'standard')
  else
    dire(hero, 'Normal', 'Je fais partie d’une équipe de secours. Ta maman m’a demandé de te ramener.', 'standard')
  end
  cinematique.RegarderGroupe({{hero, nilo, 0, 4}, {partenaire, nilo, 5, 4}})
  cinematique.Respirer(20)
  dire(nilo, 'Worried', 'Je la cherchais… J’ai cru l’entendre près de l’eau. Puis le courant a grondé.', 'droite')
  -- Nilo cherche la sortie des yeux. Le héros le laisse finir avant de le rassurer.
  tourner_vers(nilo, Direction.DownLeft, 5)
  cinematique.Respirer(32)
  dire(nilo, 'Teary-Eyed', 'J’ai couru ici et je ne retrouve plus la sortie… Elle m’attend dehors ?', 'droite')
  tourner_vers(nilo, Direction.Down, 5)
  local duree_signe = hero and temps_animation(hero, 'Nod')
  if duree_signe ~= nil then
    GROUND:CharSetAnim(hero, 'Nod', false)
    GAME:WaitFrames(duree_signe)
    GROUND:CharEndAnim(hero)
  end
  cinematique.Respirer(20)
  dire(partenaire or hero, 'Normal', 'Elle t’attend. Reste sur la terrasse, d’accord ? Tu n’es plus tout seul.', 'standard')
  cinematique.Respirer(28)
end

local function avertissement_hors_champ(texte)
  -- Kabutops est encore masqué. Aucun portrait ne doit trahir son identité.
  UI:ResetSpeaker()
  UI:SetSpeaker('???', true, '', -1, '', RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue(texte)
  UI:ResetSpeaker()
end

local function les_avertissements(hero, partenaire, nilo)
  SOUND:FadeOutBGM(22)
  GAME:WaitFrames(24)
  avertissement_hors_champ('Pas un pas de plus. Ce Lixy a déréglé le courant.')
  cinematique.Respirer(15)
  -- Ils se cherchent du regard, puis le partenaire demande qui parle.
  -- Le héros n'a pas de réplique : le désarroi passe par le jeu du duo.
  if partenaire ~= nil and hero ~= nil then
    cinematique.RegarderGroupe({{partenaire, hero, 0, 4}, {hero, partenaire, 5, 4}})
  else
    tourner_vers(partenaire or hero, Direction.Right, 4)
  end
  emote_sur(partenaire or hero, 'question')
  GAME:WaitFrames(20)
  dire(partenaire or hero, 'Worried', 'Le courant ? Mais… qui parle ?', 'standard')
  cinematique.RegarderGroupe({{hero, nilo, 0, 4}, {partenaire, nilo, 5, 4}})
  cinematique.Respirer(16)
  dire(nilo, 'Worried', 'J’ai rien touché ! Je voulais juste me mettre à l’abri.', 'droite')
  cinematique.Respirer(16)
  avertissement_hors_champ('Dernier avertissement : reculez.')
end

local function terre_tunnel(x, y, cadence, son)
  local terre = RogueEssence.Content.SingleEmitter(RogueEssence.Content.AnimData('Dig', cadence))
  terre.Layer = DrawLayer.Front
  if son then SOUND:PlayBattleSE('DUN_Dig') end
  GROUND:PlayVFX(terre, x + 8, y + 14)
end

-- Sortie du gardien façon Tunnel. La terre devient visible avant le sprite ;
-- le déplacement est vertical, déjà sur l’axe médian du duo. Les éclats
-- natifs de Tunnel couvrent les premiers pixels du corps qui sortent du sol.
local function reveler_gardien(kabutops, hero, partenaire, nilo)
  local centre = GAME:GetCameraCenter()
  local ombre = RogueEssence.Content.FlashEmitter()
  ombre.Anim = RogueEssence.Content.BGAnimData('White', 0)
  ombre.Layer = DrawLayer.Top
  -- Valeur noire prémultipliée : aucun écran blanc par-dessus la sortie de terre.
  ombre.StartColor = Color.Transparent
  ombre.EndColor = Color.Multiply(Color.Black, 0.36)
  ombre.FadeInTime, ombre.HoldTime, ombre.FadeOutTime = 14, 20, 15
  GROUND:PlayVFX(ombre, centre.X, centre.Y)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function()
      cinematique.TournerGroupe({{hero, Direction.UpLeft, 0, 4}, {partenaire, Direction.UpRight, 4, 4}})
    end),
    TASK:BranchCoroutine(function()
      GAME:MoveCamera(CAM_DUEL_X, CAM_FACE_Y - 4, 24, false)
    end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(8)
      secouer_ecran(1, 2, 32)
      emote_sur(partenaire or hero, 'shock')
    end),
  })
  terre_tunnel(APPARITION_BOSS.x, APPARITION_BOSS.y, 3, true)
  GAME:WaitFrames(11)
  kabutops.HideShadow = true
  kabutops:SetLocHeight(-10)
  GROUND:Unhide('Kabutops_Boss')
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function()
      -- Impulsion rapide, sommet bref, puis réception. La faux s’arme
      -- pendant cette courbe : pas de battement entre sortie et recul.
      for _, h in ipairs({-6, -1, 5, 11, 16, 17, 16, 13, 9, 4, 0}) do
        kabutops:SetLocHeight(h)
        GAME:WaitFrames(2)
      end
      kabutops.HideShadow = false
    end),
    TASK:BranchCoroutine(function() souffle_du_gardien(kabutops, hero, partenaire) end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(6)
      emote_sur(hero, 'exclaim')
      GAME:WaitFrames(6)
      emote_sur(nilo, 'sweating')
    end),
  })
end

-- La garde n'existe côté ground que le temps du précombat. Sous le noir,
-- la vraie équipe ennemie de l'arène reprend chacune des quatre positions.
local function retirer_garde()
  for _, ancre in ipairs(fosse.GARDE) do
    if CH(ancre.nom) ~= nil then GROUND:RemoveCharacter(ancre.nom) end
  end
end

local function placer_garde(en_place)
  local garde = {}
  for i, ancre in ipairs(fosse.GARDE) do
    local x, y = fosse.AncreAuSol(ancre)
    local dir = Direction[ancre.face]
    local depart = ancre.depart
    local ch = creer_acteur(ancre.nom, 'kabuto', Gender.Male, '',
      en_place and x or depart[1], en_place and y or depart[2], dir)
    if not en_place then GROUND:Hide(ancre.nom) end
    garde[i] = {ch=ch, ancre=ancre, x=x, y=y, dir=dir}
  end
  return garde
end

local function pas_de_griffe(k, ax, ay, bx, by, dir, fermer)
  local total, impact = temps_animation(k.ch, 'Attack')
  total = total or 28
  local duree = fermer and 22 or 17
  local frappe = math.max(5, math.min(duree - 4, math.floor((impact or 8) * duree / total)))
  local distance = math.max(math.abs(bx - ax), math.abs(by - ay))
  local function bondir()
    GROUND:AnimateToPosition(k.ch, 'Attack', dir, bx, by, total / (duree + 1), distance / duree, 0)
    GROUND:CharEndAnim(k.ch)
  end
  if not fermer then bondir(); return end
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(bondir),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(frappe)
      local t = frappe / duree
      local trace = RogueEssence.Content.SingleEmitter(RogueEssence.Content.AnimData('Scratch', 3))
      trace.Layer, trace.Offset, trace.LocHeight = DrawLayer.Front, 9, 4
      if k.ancre.signal then SOUND:PlayBattleSE('DUN_Scratch') end
      GROUND:PlayVFX(trace, math.floor(ax + (bx - ax) * t + 8),
        math.floor(ay + (by - ay) * t + 8), dir)
    end),
  })
end

local function surgir_kabuto(k)
  local spec, ch = k.ancre, k.ch
  GAME:WaitFrames(spec.delai)
  terre_tunnel(spec.depart[1], spec.depart[2], 2, spec.signal)
  GAME:WaitFrames(8)
  ch.HideShadow = true
  ch:SetLocHeight(-7)
  GROUND:Unhide(spec.nom)
  for _, h in ipairs({-4, 0, 5, 9, 7, 3, 0}) do
    ch:SetLocHeight(h)
    GAME:WaitFrames(2)
  end
  ch.HideShadow = false
  GAME:WaitFrames(5)
  -- Ils ne foncent pas droit sur une cible. D’abord ils gagnent l’angle,
  -- puis menacent et bouchent la sortie après une hésitation.
  GROUND:MoveToPosition(ch, spec.passage[1], spec.passage[2], false, 1.35)
  local direction = Direction[spec.avance]
  pas_de_griffe(k, spec.passage[1], spec.passage[2], spec.menace[1], spec.menace[2], direction, false)
  GAME:WaitFrames(spec.attente)
  tourner_vers(ch, k.dir, 3)
  pas_de_griffe(k, spec.menace[1], spec.menace[2], k.x, k.y, k.dir, true)
end

local function pas_du_duo(ch, dir, x, y)
  if ch ~= nil then
    GROUND:AnimateToPosition(ch, 'Walk', dir, x, y, 1, 0.7, 0)
    GROUND:CharEndAnim(ch)
  end
end

local function encercler_duo(kabutops, hero, partenaire)
  SOUND:PlayBGM('Rising Fear.ogg', false)
  local garde = placer_garde(false)
  local mouvements = {}
  for _, k in ipairs(garde) do
    mouvements[#mouvements + 1] = TASK:BranchCoroutine(function() surgir_kabuto(k) end)
  end
  mouvements[#mouvements + 1] = TASK:BranchCoroutine(function()
    -- Déplacer le cadre sur un seul axe, avant la poussière à l’arrière.
    GAME:WaitFrames(44)
    GAME:MoveCamera(CAM_DUEL_X, CAM_CERCLE_Y, 22, false)
  end)
  mouvements[#mouvements + 1] = TASK:BranchCoroutine(function()
    GAME:WaitFrames(13)
    secouer_ecran(1, 1, 14)
    cinematique.RegarderGroupe({{partenaire or hero, garde[1].ch, 0, 3}, {partenaire and hero, garde[2].ch, 18, 3}})
    GAME:WaitFrames(11)
    -- Pris de flanc, le duo se resserre en se couvrant, sans se percuter.
    TASK:JoinCoroutines({
      TASK:BranchCoroutine(function() pas_du_duo(partenaire, Direction.Left, DUEL_PARTENAIRE.x + 2, RECUL_Y + 4) end),
      TASK:BranchCoroutine(function() pas_du_duo(hero, Direction.Right, DUEL_HEROS.x - (partenaire and 2 or 0), RECUL_Y - 2) end),
    })
    GAME:WaitFrames(12)
    -- Le bruit au sud attire le regard du duo vers le sable qui remue.
    emote_sur(hero, 'exclaim')
    cinematique.RegarderGroupe({{partenaire or hero, garde[3].ch, 0, 4}, {partenaire and hero, garde[4].ch, 9, 4}})
    emote_sur(partenaire, 'sweatdrop')
  end)
  TASK:JoinCoroutines(mouvements)
  GAME:WaitFrames(25) -- tenir le plan d’ensemble avant de rendre la parole à Kabutops
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() pas_du_duo(hero, Direction.Up, DUEL_HEROS.x, RECUL_Y) end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(6)
      pas_du_duo(partenaire, Direction.Up, DUEL_PARTENAIRE.x, RECUL_Y)
    end),
  })
  cinematique.RegarderGroupe({{hero, kabutops, 0, 4}, {partenaire, kabutops, 5, 4}})
end

local function la_vallee_et_le_choix(kabutops, hero, partenaire, nilo)
  cinematique.Respirer(20)
  regarder_cible(kabutops, nilo, 5)
  dire(kabutops, 'Normal', 'Avant, on venait boire ici sans crainte. Depuis peu, même les sentiers ne sont plus sûrs.', 'droite')
  cinematique.RegarderGroupe({{partenaire, nilo, 0, 4}, {hero, nilo, 6, 4}})
  cinematique.Respirer(26)
  dire(kabutops, 'Determined', 'Quand l’eau se déchaîne, elle emporte les berges. Des familles entières ont quitté la vallée.', 'droite')
  tourner_vers(kabutops, Direction.Down, 5)
  regarder_cible(partenaire or hero, kabutops, 4)
  cinematique.Respirer(20)
  dire(partenaire or hero, 'Determined', 'Mais Nilo se cachait. Être près de l’eau ne veut pas dire qu’il y a touché !', 'standard')
  -- Le gardien se place dans l’axe du duel seulement après l’apparition.
  GROUND:MoveToPosition(kabutops, SOL_BOSS.x, SOL_BOSS.y, false, 1.25)
  tourner_vers(kabutops, Direction.Down, 4)
  dire(kabutops, 'Angry', 'Je l’ai vu près de la source. Ça vient sûrement de lui, de ce Pokémon électrique.', 'droite')
  emote_sur(kabutops, 'angry')
  cinematique.Respirer(24)
  dire(kabutops, 'Angry', 'Il ne contrôle plus ses éclairs. Tant qu’il rôde, aucun village en aval n’est en sécurité.', 'droite')

  -- La caméra et les regards reviennent à Nilo un instant
  -- avant la décision : l’accusation est celle du gardien, pas de la scène.
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() GAME:MoveCamera(CAM_DUEL_X, CAM_NILO_REPLI_Y, 28, false) end),
    TASK:BranchCoroutine(function()
      cinematique.RegarderGroupe({{hero, nilo, 0, 4}, {partenaire, nilo, 7, 4}})
    end),
  })
  cinematique.Respirer(26)
  dire(nilo, 'Teary-Eyed', 'Mais je ne comprends pas… Je veux juste rentrer avec maman.', 'droite')
  regarder_cible(hero, kabutops, 5)
  cinematique.Respirer(36)
  cinematique.RegarderGroupe({{hero, partenaire, 0, 4}, {partenaire, hero, 9, 4}})
  GAME:MoveCamera(CAM_DUEL_X, CAM_FACE_Y, 22, false)
  dire(hero, 'Determined', "Ce Pokémon est beaucoup trop en colère pour entendre raison... Nous n'avons pas le choix.", 'droite')
  cinematique.Respirer(20)
  dire(partenaire, 'Determined', 'D’accord. On les retient ici. Nilo, reste à l’abri, on ne t’abandonne pas.', 'standard')
  cinematique.RegarderGroupe({{partenaire, kabutops, 0, 4}, {hero, kabutops, 5, 4}})
  cinematique.Respirer(30)
end

function fgv1.PreBattle(is_rematch, map)
  -- Une interruption suivie d'une réentrée ne doit pas rejouer la découverte.
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GrotteVerdoyantePhase = 1
  GAME:CutsceneMode(true)
  retirer_garde() -- une réentrée ne garde pas les acteurs d’une prise interrompue
  local retablir_eau = suspendre_eau_precombat(map)
  local hero = CH('PLAYER')
  local depart_h = is_rematch and {x=DUEL_HEROS.x, y=RECUL_Y + 20} or ENTREE_HEROS
  local depart_p = is_rematch and {x=DUEL_PARTENAIRE.x, y=RECUL_Y + 20} or ENTREE_PARTENAIRE
  local partenaire = equipe_scene.Partenaire(depart_p.x, depart_p.y, Direction.Up)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo',
    SOL_NILO_TERRASSE.x, SOL_NILO_TERRASSE.y, Direction.Down)
  local seuil_boss = is_rematch and SOL_BOSS or APPARITION_BOSS
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    seuil_boss.x, seuil_boss.y, Direction.Down)
  if not is_rematch then GROUND:Hide('Kabutops_Boss') end
  trembler_de_peur(nilo) -- déjà actif quand la caméra découvre la terrasse
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, depart_h.x, depart_h.y, Direction.Up)
  end

  if not is_rematch then
    traverser_passage(hero, partenaire)
    au_pied_de_la_terrasse(hero, partenaire, nilo)
    premiere_rencontre(hero, partenaire, nilo)
    les_avertissements(hero, partenaire, nilo)
    reveler_gardien(kabutops, hero, partenaire, nilo)
    encercler_duo(kabutops, hero, partenaire)
    la_vallee_et_le_choix(kabutops, hero, partenaire, nilo)
  else
    placer_garde(true)
    GAME:MoveCamera(CAM_DUEL_X, CAM_REVANCHE_Y, 1, false)
    SOUND:PlayBGM('Rising Fear.ogg', false)
    GAME:FadeIn(18)
    TASK:JoinCoroutines({
      TASK:BranchCoroutine(function()
        if partenaire ~= nil then GROUND:MoveToPosition(partenaire, SOL_PARTENAIRE.x, RECUL_Y, false, 1.6) end
      end),
      TASK:BranchCoroutine(function()
        if hero == nil then return end
        GAME:WaitFrames(5)
        GROUND:MoveToPosition(hero, SOL_HEROS.x, RECUL_Y, false, 1.6)
      end),
    })
    cinematique.Respirer(10)
    cinematique.Dire(kabutops, 'Determined', 'Encore vous ? Cette fois, tenez-vous prêts.', 'droite')
  end

  UI:ResetSpeaker()
  -- Même axe, même échelle et même centre que la première image jouable.
  -- On quitte le cadrage décalé qui laissait la place à la boîte de texte.
  GAME:MoveCamera(CAM_DUEL_X, CAM_DUEL_Y, 20, false)
  woosh_duel()
  retirer_garde()
  retablir_eau() -- à noir complet, y compris si l'éditeur conserve l'instance
  arreter_tremblement(nilo) -- le spectateur de l’arène prend le relais
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:CutsceneMode(false)
  lancer_duel_boss()
end

-- Le retour inverse la sortie de terre : une impulsion, la terre au ras du
-- sol, puis le corps s’enfonce dans le nuage. Aucun acteur ne court en coulisse.
local function s_enfouir(ch, nom, son, grand)
  local x, y = ch.Position.X, ch.Position.Y
  arreter_tremblement(ch)
  GROUND:CharSetAnim(ch, 'Hurt', false)
  GAME:WaitFrames(5)
  terre_tunnel(x, y, grand and 3 or 2, son)
  ch.HideShadow = true
  for _, h in ipairs({2, 5, 7, 4, 0, -5, -10, -16, -22}) do
    ch:SetLocHeight(h)
    GAME:WaitFrames(2)
  end
  GROUND:Hide(nom)
  GROUND:RemoveCharacter(nom)
  GAME:WaitFrames(grand and 20 or 9)
end

local function la_fuite_sous_terre(kabutops, garde, hero, partenaire)
  local reactions = {}
  for i, k in ipairs(garde) do
    reactions[#reactions + 1] = TASK:BranchCoroutine(function()
      GAME:WaitFrames((i - 1) * 7)
      -- Un petit recul sans tourner le dos ; les autres hésitent à leur tour.
      emote_sur(k.ch, i % 2 == 1 and 'shock' or 'sweating', i == 1 and 'EVT_Emote_Shock' or nil)
      trembler_de_peur(k.ch)
      local repli = k.ancre.recul
      GROUND:AnimateToPosition(k.ch, 'Hurt', k.dir, k.x + repli[1], k.y + repli[2], 0.8, 0.85, 0)
      GROUND:CharEndAnim(k.ch)
      GAME:WaitFrames(11)
      regarder_cible(k.ch, kabutops, 3)
    end)
  end
  reactions[#reactions + 1] = TASK:BranchCoroutine(function()
    GAME:WaitFrames(10)
    cinematique.RegarderGroupe({{partenaire or hero, garde[1].ch, 0, 4}, {partenaire and hero, garde[2].ch, 10, 4}})
  end)
  TASK:JoinCoroutines(reactions)
  GAME:WaitFrames(28) -- les quatre restent visibles, tremblants, avant le signal
  regarder_cible(kabutops, garde[2].ch, 3)
  tourner_vers(kabutops, Direction.Down, 4)
  local duree = temps_animation(kabutops, 'Nod')
  if duree ~= nil then
    GROUND:CharSetAnim(kabutops, 'Nod', false)
    GAME:WaitFrames(duree)
    GROUND:CharEndAnim(kabutops)
  end

  -- L’arrière garde fuit d’abord ; les deux flancs cèdent ensuite.
  local delais = {22, 34, 0, 11}
  local sorties = {}
  for i, k in ipairs(garde) do
    sorties[#sorties + 1] = TASK:BranchCoroutine(function()
      if delais[i] > 0 then GAME:WaitFrames(delais[i]) end
      s_enfouir(k.ch, k.ancre.nom, k.ancre.signal, false)
    end)
  end
  sorties[#sorties + 1] = TASK:BranchCoroutine(function()
    GAME:WaitFrames(12)
    cinematique.RegarderGroupe({{hero, garde[4].ch, 0, 4}, {partenaire, garde[3].ch, 7, 4}})
  end)
  TASK:JoinCoroutines(sorties)
  cinematique.Respirer(12) -- la poussière des derniers Kabuto retombe

  -- Les regards reviennent vers le chef, au centre, après les quatre départs.
  tourner_vers(kabutops, Direction.Down, 4)
  cinematique.RegarderGroupe({{partenaire, kabutops, 0, 4}, {hero, kabutops, 6, 4}})
  cinematique.Respirer(22)
  s_enfouir(kabutops, 'Kabutops_Boss', true, true)
end

function fgv1.PostBattle()
  GAME:CutsceneMode(true)
  local hero = CH('PLAYER')
  local partenaire = equipe_scene.Partenaire(APRES_DUEL.partenaire, APRES_DUEL.y, Direction.Right)
  local garde = placer_garde(true)
  local nilo = creer_acteur('Nilo_Grotte', 'shinx', Gender.Male, 'Nilo',
    SOL_NILO_TERRASSE.x, SOL_NILO_TERRASSE.y, Direction.Down)
  local kabutops = creer_acteur('Kabutops_Boss', 'kabutops', Gender.Male, '',
    APRES_DUEL.boss, APRES_DUEL.y, Direction.Down)

  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, APRES_DUEL.hero, APRES_DUEL.y, Direction.Left)
  end
  SOUND:FadeOutBGM(12)
  GAME:MoveCamera(CAM_VICTOIRE_X, CAM_VICTOIRE_Y, 1, false)
  trembler_de_peur(nilo)
  GAME:WaitFrames(12)
  GAME:FadeIn(20)
  GAME:WaitFrames(16)

  emote_sur(kabutops, 'sweatdrop')
  GAME:WaitFrames(10)
  regarder_cible(kabutops, hero or partenaire, 4)
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

  la_fuite_sous_terre(kabutops, garde, hero, partenaire)
  -- Nilo ne quitte la terrasse qu'une fois le passage redevenu sûr.
  arreter_tremblement(nilo)
  cinematique.Respirer(12)
  SOUND:PlayBGM('Lower Spring Cave.ogg', false)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() GROUND:MoveToPosition(nilo, REUNION.axe, REUNION.nilo_y, false, 1.65) end),
    -- Le duo reste sur les côtés. Ni Nilo ni Lyra ne traversent un acteur.
    TASK:BranchCoroutine(function()
      if partenaire ~= nil then GROUND:MoveToPosition(partenaire, REUNION.axe - 32, REUNION.duo_y, false, 1.1) end
    end),
    TASK:BranchCoroutine(function()
      if hero ~= nil then
        GAME:WaitFrames(8)
        GROUND:MoveToPosition(hero, REUNION.axe + 32, REUNION.duo_y, false, 1.1)
      end
    end),
    TASK:BranchCoroutine(function()
      GAME:WaitFrames(16)
      GAME:MoveCamera(CAM_VICTOIRE_X, CAM_REUNION_Y, 22, false)
    end),
  })
  cinematique.RegarderGroupe({{nilo, hero or partenaire, 0, 4}, {partenaire, nilo, 5, 4}, {hero, nilo, 9, 4}})
  cinematique.Dire(nilo, 'Teary-Eyed', 'J’ai cru que je ne reverrais pas maman… Merci d’être venus.', 'droite')
  UI:ResetSpeaker()
  cinematique.Respirer(18)

  -- L'arrivée de Lyra motive les regards. Le duo ne tourne pas le dos à
  -- Lyra pour jouer une émote après qu'elle s'est déjà placée devant lui.
  local lyra = creer_acteur('Lyra_Grotte', 'luxray', Gender.Female, 'Lyra', REUNION.axe, 344, Direction.Up)
  TASK:JoinCoroutines({
    TASK:BranchCoroutine(function() GROUND:MoveToPosition(lyra, REUNION.axe, REUNION.lyra_y, true, 2) end),
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
  cinematique.Dire(nilo, 'Teary-Eyed', 'Maman… Je ne retrouvais plus la sortie.', 'droite')
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
  local partenaire = equipe_scene.Partenaire(SALLE_X + 216, 344, Direction.Up)

  GAME:CutsceneMode(true)
  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, SALLE_X + 240, 344, Direction.Up)
  end

  GAME:MoveCamera(SALLE_X + 240, 224, 1, false)
  UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 18)
  GAME:WaitFrames(24)
  UI:WaitHideTitle(16)
  GAME:FadeIn(18)
  SOUND:PlayBGM('Lower Spring Cave.ogg', true)

  local taches = {}
  if hero ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, SALLE_X + 240, 248, false, 1)
      tourner_vers(hero, Direction.Up, 4)
    end))
  end
  if partenaire ~= nil then
    table.insert(taches, TASK:BranchCoroutine(function()
      GAME:WaitFrames(7)
      GROUND:MoveToPosition(partenaire, SALLE_X + 216, 256, false, 1)
      tourner_vers(partenaire, Direction.Up, 4)
    end))
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end

  GAME:MoveCamera(SALLE_X + 240, 192, 20, false)
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
  -- Pendant la sortie du sol, la scène a coupé la musique et joue ensuite
  -- Rising Fear : ne pas la remplacer sous la scène en cours.
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.GrotteVerdoyantePhase ~= 1 then
    SOUND:PlayBGM('Lower Spring Cave.ogg', true)
  end
end

function fgv1.Update(map, time) end

return fgv1
