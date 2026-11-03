--[[ Prologue et retrouvailles sur la prairie du réveil
     (zrv2_zone_reveil_nuit ; l'ancien script reveil_nuit reste le module
     partagé de la scène pour garder une seule écriture des dialogues).
     Prologue : juste après le quiz, le héros gît endormi dans la prairie.
     Sur fond noir, quatre pensées traversent son sommeil ; le fondu se lève
     un instant sur lui, puis l'image bascule chez le partenaire.
     Aller : le partenaire traverse Lost Wood seul, remonte depuis l'entrée
     sud et arrive au point de réveil où le héros est allongé. Il le réveille,
     lui apprend le nom et la nature de la forêt, puis ils regardent ensemble
     la montagne qui se dresse au-delà de la mer.
     Pendant la rencontre, le héros ne prononce aucun mot : il répond par
     l'animation Nod, son idle, ses orientations et ses émotes. Le partenaire
     formule les questions, réagit à voix haute à ces gestes et porte seul le
     dialogue. Sa déclaration d'explorateur utilise Pose, la patte levée,
     uniquement lorsque la feuille SpriteCollab de son espèce la contient.
     Retour : le segment inverse de Lost Wood ramène le duo vers la falaise,
     cette fois au jour. Échec du retour : bref rappel, puis nouvelle
     tentative en duo.
     Textes originaux PMD Destiny. Transitions et cadrage testés sur un banc
     moteur avec sorties forcées ; parcours complet des étages non testé.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'

local reveil_nuit = {}
local invite_retour_en_cours = false
local invite_retour_armee = false

-- Points de mise en scène selon la carte réellement chargée. La prairie ZRV2
-- possède ses propres marqueurs (reveil au nord, entrance au sud) ; le repli
-- historique conserve les marqueurs de l'ancienne reveil_nuit pour qu'une
-- sauvegarde déjà placée sur cette carte continue de fonctionner.
local function points_scene()
  local point_reveil = MRKR('reveil')
  local entree = MRKR('entrance')
  if point_reveil ~= nil and entree ~= nil then
    -- PMDO affiche 320 × 240 pixels logiques et MoveCamera vise le centre
    -- du cadre. Sur cette carte de 768 × 576, le centre (384, 136) montre
    -- Y 16..256 : lune, sommet, mer et héros tout en bas. Le panorama à
    -- Y=152 garde le sommet tout en laissant davantage de prairie ; le
    -- cadre de dialogue à Y=184 ne conserve qu'une partie de la montagne,
    -- mais place les acteurs juste au-dessus de la boîte de texte.
    return {
      zrv = true,
      reveil_x = point_reveil.Position.X,
      reveil_y = point_reveil.Position.Y,
      vue_x = point_reveil.Position.X,
      vue_y = point_reveil.Position.Y,
      camera_x = point_reveil.Position.X + 8,
      camera_y = point_reveil.Position.Y - 56,
      camera_ouverture_x = point_reveil.Position.X - 8,
      camera_ouverture_y = point_reveil.Position.Y - 104,
      camera_panorama_x = point_reveil.Position.X + 8,
      camera_panorama_y = point_reveil.Position.Y - 88,
      camera_approche_x = point_reveil.Position.X + 8,
      camera_approche_y = point_reveil.Position.Y + 48,
      entree_x = entree.Position.X,
      entree_y = entree.Position.Y,
      camera_entree_x = entree.Position.X + 8,
      camera_entree_y = entree.Position.Y - 104,
      palier_x = point_reveil.Position.X,
      palier_y = point_reveil.Position.Y + 160,
      approche_x = point_reveil.Position.X,
      approche_y = point_reveil.Position.Y + 96,
      partenaire_pres_x = point_reveil.Position.X + 24,
      partenaire_pres_y = point_reveil.Position.Y,
    }
  end

  local wake = MRKR('WakeupLocation')
  local overlook = MRKR('ScenicOverlook')
  local reveil_x, reveil_y = wake.Position.X + 112, wake.Position.Y - 16
  return {
    zrv = false,
    reveil_x = reveil_x,
    reveil_y = reveil_y,
    vue_x = overlook.Position.X,
    vue_y = overlook.Position.Y,
    camera_x = overlook.Position.X,
    camera_y = overlook.Position.Y,
    camera_ouverture_x = overlook.Position.X,
    camera_ouverture_y = overlook.Position.Y,
    camera_panorama_x = overlook.Position.X,
    camera_panorama_y = overlook.Position.Y,
    camera_approche_x = overlook.Position.X,
    camera_approche_y = overlook.Position.Y,
    entree_x = (MRKR('Dazzling_Exit_East') or MRKR('Main_Entrance_Marker')).Position.X,
    entree_y = (MRKR('Dazzling_Exit_East') or MRKR('Main_Entrance_Marker')).Position.Y,
    partenaire_pres_x = reveil_x + 24,
    partenaire_pres_y = reveil_y,
  }
end

-- Déplacements de caméra en parallèle d'une marche, d'un geste ou d'un
-- fondu. Chaque travelling lancé ici est rejoint avant le mouvement de
-- caméra suivant afin que deux coroutines ne se disputent jamais le cadre.
local function lancer_camera(x, y, duree)
  return TASK:BranchCoroutine(function()
    GAME:MoveCamera(x, y, duree, false)
  end)
end

local function attendre_camera(tache)
  if tache ~= nil then TASK:JoinCoroutines({tache}) end
end

-- Les feuilles SpriteCollab livrées avec Destiny ne contiennent pas toutes
-- les animations d'événement des starters. Avant de jouer Nod, Pose, Wake,
-- LookUp ou DeepBreath, on demande donc à la feuille de l'acteur si le groupe
-- demandé existe réellement (et ne se résout pas vers un simple fallback).
-- Si l'API graphique ne répond pas, la durée relevée dans l'inventaire des
-- fichiers .chara sert de repli ; si le groupe est absent, l'appelant utilise
-- un geste d'orientation ou l'idle par défaut.
local function duree_animation(personnage, nom)
  if personnage == nil then return 0 end
  local ok, duree = pcall(function()
    local gestionnaire = RogueEssence.Content.GraphicsManager
    local index = gestionnaire.GetAnimIndex(nom)
    if index == nil or index < 0 then return 0 end
    local feuille = gestionnaire.GetChara(personnage.CurrentForm:ToCharID())
    if feuille:GetReferencedAnimIndex(index) ~= index then return 0 end
    return feuille:GetTotalTime(index, personnage.Direction)
  end)
  if ok then
    local valeur = tonumber(duree)
    if valeur ~= nil then return valeur end
  end
  return nil
end

local function jouer_animation(personnage, nom, duree_si_inconnue)
  if personnage == nil then return false end
  local duree = duree_animation(personnage, nom)
  if duree == nil then duree = duree_si_inconnue or 20 end
  if duree <= 0 then return false end
  GROUND:CharSetAnim(personnage, nom, false)
  GAME:WaitFrames(math.max(1, math.floor(duree)))
  GROUND:CharEndAnim(personnage)
  return true
end

-- Pose est l'animation SpriteCollab de la patte levée. PoseGroundAction la
-- maintient pendant la réplique, comme dans les camps de base PMDO, au lieu
-- de la laisser se terminer après ses 22 ticks.
local function commencer_pose(personnage)
  if personnage == nil then return false end
  local duree = duree_animation(personnage, 'Pose')
  if duree ~= nil and duree <= 0 then return false end
  local ok = pcall(function()
    local anim_id = RogueEssence.Content.GraphicsManager.GetAnimIndex('Pose')
    GROUND:CharSetAction(personnage,
      RogueEssence.Ground.PoseGroundAction(personnage.Position,
        personnage.Direction, anim_id))
  end)
  if ok then
    GAME:WaitFrames(8)
    return true
  end
  return jouer_animation(personnage, 'Pose', 22)
end

local function terminer_pose(personnage)
  if personnage ~= nil then GROUND:CharEndAnim(personnage) end
end

-- Vision du rêve, façon Cri Dimensionnel d'Explorateurs du Ciel : le flash
-- s'ouvre jusqu'au blanc plein (frames 0–21 de Dimensional_Scream), la voix
-- résonne sur le halo doré de l'intro Arceus de Pokémon Relict
-- (Vision_Halo_Dore, boucle animée), puis le flash se referme (frames
-- 22–32). Les sons EVT_Dimensional_Scream_Start/End sont ceux de la base
-- PMDO. Une overlay 320×240 se dessine depuis son coin supérieur gauche :
-- on vise donc le coin du cadre caméra, pas son centre.
local function coin_camera()
  local centre = GAME:GetCameraCenter()
  return centre.X - 160, centre.Y - 120
end

local function jouer_cri_dimensionnel(debut, fin, temps_frame)
  local x, y = coin_camera()
  pcall(function()
    local emitter = RogueEssence.Content.FiniteOverlayEmitter()
    emitter.Anim = RogueEssence.Content.BGAnimData(
      'Dimensional_Scream', temps_frame, debut, fin)
    emitter.Layer = DrawLayer.Top
    emitter.TotalTime = (fin - debut + 1) * temps_frame
    emitter.FadeIn = 0
    emitter.FadeOut = 0
    emitter.RepeatX = false
    emitter.RepeatY = false
    GROUND:PlayVFX(emitter, x, y)
  end)
end

local function demarrer_halo_vision()
  local x, y = coin_camera()
  local halo = nil
  pcall(function()
    halo = RogueEssence.Content.OverlayEmitter()
    halo.Anim = RogueEssence.Content.BGAnimData('Vision_Halo_Dore', 4)
    halo.Layer = DrawLayer.Top
    halo.FadeIn = 0
    halo.FadeOut = 12
    halo:SetupEmit(RogueElements.Loc(x, y), RogueElements.Loc(x, y),
      RogueElements.Dir8.Down)
    _GROUND:CreateAnim(halo, DrawLayer.NoDraw)
  end)
  return halo
end

local function vision_cri_dimensionnel()
  UI:ResetSpeaker()
  SOUND:PlayBattleSE('EVT_Dimensional_Scream_Start')
  jouer_cri_dimensionnel(0, 21, 3)
  -- À 63 ticks, la frame blanche (21) vient d'apparaître : le halo la
  -- remplace sans raccord visible, pendant que le son finit de résonner.
  GAME:WaitFrames(63)
  local halo = demarrer_halo_vision()
  GAME:WaitFrames(12)
  UI:WaitShowVoiceOver("« Retrouve le chemin que tu as perdu…[br]nos routes finiront par se rejoindre. »", -0.38)
  SOUND:PlayBattleSE('EVT_Dimensional_Scream_End')
  jouer_cri_dimensionnel(22, 32, 4)
  if halo ~= nil then pcall(function() halo:SwitchOff() end) end
  GAME:WaitFrames(44)
end

-- Le héros reste muet pendant toute la rencontre. Il répond par le vrai
-- hochement Nod quand son espèce le possède, par son idle lorsqu'il écoute,
-- et par quelques orientations/émotes lisibles pour les autres réactions.
local function hero_geste(hero, geste)
  if hero == nil then return end
  cinematique.Respirer(20)
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(30)
  elseif geste == 'non' then
    -- Aucune feuille du pool n'a d'animation « secouer la tête » distincte :
    -- le va-et-vient d'orientation reste le signe « non » le plus lisible.
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(16)
  elseif geste == 'oui' then
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    if not jouer_animation(hero, 'Nod', 20) then
      GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
      GAME:WaitFrames(9)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(10)
      GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
      GAME:WaitFrames(7)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(16)
    end
  elseif geste == 'idle' then
    -- Réponse d'écoute : retour à l'idle par défaut, face au partenaire.
    GROUND:CharEndAnim(hero)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(26)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(20)
  elseif geste == 'montagne' then
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    if jouer_animation(hero, 'LookUp', 18) then
      GAME:WaitFrames(14)
    else
      GAME:WaitFrames(38)
    end
  elseif geste == 'foret' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(24)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
  elseif geste == 'inquiet' then
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(30)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(10)
  elseif geste == 'surpris' then
    SOUND:PlayBattleSE('EVT_Emote_Shock')
    GROUND:CharSetEmote(hero, 'shock', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(32)
  elseif geste == 'ecoute' then
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    if not jouer_animation(hero, 'LookUp', 18) then
      GAME:WaitFrames(24)
    end
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(18)
  elseif geste == 'determine' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    if not jouer_animation(hero, 'Nod', 20) then
      GAME:WaitFrames(18)
    end
  elseif geste == 'remerciement' then
    GROUND:CharSetEmote(hero, 'happy', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    if not jouer_animation(hero, 'Nod', 20) then
      GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
      GAME:WaitFrames(18)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(14)
    end
  elseif geste == 'sourire' then
    GROUND:CharSetEmote(hero, 'happy', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(24)
  end
end

-- Petits gestes du partenaire : montrer la forêt au sud, lever les yeux vers
-- la montagne, reprendre son souffle après le donjon ou sauter de joie.
-- Dans cette scène, le partenaire se tient toujours à droite du héros ; Left
-- le ramène donc face à son interlocuteur.
local function partenaire_geste(partenaire, geste)
  if partenaire == nil then return end
  cinematique.Respirer(20)
  if geste == 'foret' then
    GROUND:CharAnimateTurnTo(partenaire, Direction.Down, 4)
    GAME:WaitFrames(18)
    GROUND:CharAnimateTurnTo(partenaire, Direction.Left, 4)
    GAME:WaitFrames(8)
  elseif geste == 'montagne' then
    GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 4)
    if not jouer_animation(partenaire, 'LookUp', 18) then
      GAME:WaitFrames(24)
    end
    GROUND:CharAnimateTurnTo(partenaire, Direction.Left, 4)
    GAME:WaitFrames(8)
  elseif geste == 'souffle' then
    if not jouer_animation(partenaire, 'DeepBreath', 62) then
      GROUND:CharEndAnim(partenaire)
      GAME:WaitFrames(20)
    end
  elseif geste == 'joie' then
    GROUND:CharSetEmote(partenaire, 'happy', 1)
    if not jouer_animation(partenaire, 'Hop', 24) then
      GAME:WaitFrames(18)
    end
  end
end

function reveil_nuit.Init(map)
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.LostWoodTrip == 'rencontre' then
    equipe_scene.RestaurerHeros()
  end
  local hero = CH('PLAYER')
  local prologue = SV.Destiny.PrologueHeros
  -- Pendant le prologue, seul le héros endormi doit apparaître : ne pas
  -- matérialiser l'acteur du partenaire avant la vraie rencontre.
  if hero ~= nil and prologue ~= 'a_voir' and prologue ~= 'en_cours'
     and prologue ~= 'vers_partenaire' then
    equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
  end
end

function reveil_nuit.Enter(map)
  reveil_nuit.PlotScripting()
end

function reveil_nuit.Exit(map)
end

function reveil_nuit.Update(map)
  if invite_retour_en_cours then return end
  if SV.Destiny == nil or SV.Destiny.LostWoodTrip ~= 'pause_retour' then return end
  local hero = CH('PLAYER')
  if hero == nil then return end
  local points = points_scene()
  local dx = hero.Position.X - points.entree_x
  local dy = hero.Position.Y - points.entree_y
  local dist2 = dx * dx + dy * dy
  if dist2 > 110 * 110 then
    invite_retour_armee = true
  elseif invite_retour_armee and dist2 <= 64 * 64 then
    invite_retour_armee = false
    reveil_nuit.DemanderRepriseRetour()
  end
end

function reveil_nuit.GameSave(map)
end

function reveil_nuit.GameLoad(map)
  reveil_nuit.PlotScripting()
end

local function aller_scene_partenaire(deja_noir)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PrologueHeros = 'vers_partenaire'
  if not deja_noir then
    GAME:FadeOut(false, 60)
    GAME:WaitFrames(30)
  end
  GAME:CutsceneMode(false)
  GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Home_Door')
end

-- Le héros est déjà allongé dans la prairie avant même que le partenaire
-- quitte sa maison. Les quatre phrases sont ses pensées dans le sommeil :
-- aucun portrait, aucun locuteur, seulement du texte sur le noir.
function reveil_nuit.PrologueHerosEndormi()
  local hero = CH('PLAYER')
  if hero == nil then
    GAME:FadeIn(20)
    print('[Destiny] Prologue du héros suspendu : joueur absent.')
    return
  end

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PrologueHeros = 'en_cours'
  local points = points_scene()

  SOUND:StopBGM()
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  if CH('Teammate1') ~= nil then GROUND:Hide('Teammate1') end
  GROUND:CharSetAnim(hero, 'Laying', true)
  GROUND:TeleportTo(hero, points.reveil_x, points.reveil_y, Direction.Right)
  -- Derrière le noir, préparer le plan le plus haut : lorsque le fondu se
  -- lèvera, la viewport contiendra la lune, le sommet et la mer.
  GAME:MoveCamera(points.camera_ouverture_x, points.camera_ouverture_y, 1, false)

  GAME:FadeOut(false, 1)
  GAME:WaitFrames(45)
  -- Quatre pensées courtes, sans balise [i]. SetAutoFinish(true) donne aux
  -- voix-off le fondu d'entrée et de sortie du TitleDialog PMDO (60 ticks,
  -- comme les textes de fin/crédits de la base) : chaque phrase apparaît
  -- entière, puis s'efface lentement quand le joueur avance.
  UI:SetAutoFinish(true)
  UI:WaitShowVoiceOver("…Où suis-je ?", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("Il fait noir…", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("Je ne me souviens de rien…", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("J’ai sommeil…", -1)
  UI:SetAutoFinish(false)
  SV.Destiny.PenseesReveilVues = true
  GAME:WaitFrames(45)

  -- Le noir se lève lentement : le héros dort toujours, seul face à la mer.
  -- Pendant le fondu, un premier travelling descend du ciel vers le
  -- panorama ; un second, encore plus lent, rapproche ensuite le cadre du
  -- héros tout en gardant une partie de la montagne dans le haut de l'image.
  if points.zrv then
    local travelling = lancer_camera(points.camera_panorama_x,
      points.camera_panorama_y, 150)
    GAME:FadeIn(100)
    GAME:WaitFrames(70)
    attendre_camera(travelling)
    GAME:MoveCamera(points.camera_x + 8, points.camera_y, 210, false)
    GAME:WaitFrames(35)
  else
    GAME:FadeIn(100)
    GAME:WaitFrames(180)
  end

  -- Puis la nuit referme le plan et la scène rejoint le partenaire.
  GAME:FadeOut(false, 100)
  GAME:WaitFrames(45)
  aller_scene_partenaire(true)
end

local function lancer_retour()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.LostWoodTrip = 'retour'
  SV.Destiny.LostWoodRetry = nil
  SV.Destiny.LostWoodCause = nil
  SV.Destiny.LostWoodRetourEchec = false
  SOUND:FadeOutBGM(60)
  GAME:FadeOut(false, 60)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  -- Segment 1 : les sept générateurs d'étage dans l'ordre inverse (7 → 1).
  GAME:EnterDungeon('lost_wood', 1, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
end

function reveil_nuit.DemanderRepriseRetour()
  if invite_retour_en_cours then return end
  local hero, partner = CH('PLAYER'), CH('Teammate1')
  if hero == nil or partner == nil then return end
  invite_retour_en_cours = true
  GAME:CutsceneMode(true)
  AI:DisableCharacterAI(partner)
  UI:ResetSpeaker()
  cinematique.Dire(partner, 'Normal', "Voici le chemin du retour, par [color=#69D98C]Lost Wood[color]…", 'standard')
  UI:ChoiceMenuYesNo('Souhaitez-vous retourner dans Lost Wood ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    cinematique.Dire(partner, 'Happy', "Alors on repart. Ensemble, cette fois encore.", 'standard')
    invite_retour_en_cours = false
    lancer_retour()
    return
  end
  cinematique.Dire(partner, 'Normal', "D'accord, reposons-nous encore un peu. Je te suivrai quand tu reviendras vers l'entrée.", 'standard')
  UI:ResetSpeaker()
  equipe_scene.Suivre(partner, hero)
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
  invite_retour_en_cours = false
end

function reveil_nuit.PlotScripting()
  SV.Destiny = SV.Destiny or {}
  local prologue = SV.Destiny.PrologueHeros
  if prologue == 'a_voir' or prologue == 'en_cours' then
    reveil_nuit.PrologueHerosEndormi()
    return
  end
  if prologue == 'vers_partenaire' and not SV.Destiny.PartenaireParti
     and SV.Destiny.LostWoodTrip == nil then
    aller_scene_partenaire(false)
    return
  end
  if SV.Destiny.RetrouvaillesFaites then
    if SV.Destiny.LostWoodTrip == 'pause_retour' then
      local hero, partner = CH('PLAYER'), CH('Teammate1')
      GAME:FadeIn(20)
      invite_retour_armee = true
      equipe_scene.Suivre(partner, hero)
      return
    end
    if SV.Destiny.LostWoodTrip == 'retour' and SV.Destiny.LostWoodRetourEchec then
      local hero, partner = CH('PLAYER'), CH('Teammate1')
      if hero == nil or partner == nil then
        GAME:FadeIn(20)
        print('[Destiny] Retour à deux impossible : membre de l’équipe absent.')
        return
      end
      local points = points_scene()
      GAME:CutsceneMode(true)
      GROUND:TeleportTo(hero, points.vue_x - 20, points.vue_y, Direction.Up)
      GROUND:TeleportTo(partner, points.vue_x, points.vue_y, Direction.Up)
      if points.zrv then
        -- Même courte reprise, même respiration : ouvrir sur la montagne,
        -- puis descendre vers le duo avant les deux répliques.
        GAME:MoveCamera(points.camera_panorama_x, points.camera_panorama_y, 1, false)
        GAME:FadeIn(30)
        GAME:MoveCamera(points.camera_x, points.camera_y, 90, false)
      else
        GAME:MoveCamera(points.camera_x, points.camera_y, 1, false)
        GAME:FadeIn(30)
      end
      if SV.Destiny.LostWoodCause == 'abandon' then
        cinematique.Dire(partner, 'Worried', "Nous avons rebroussé chemin à temps.\nOn reprend notre souffle… puis on décidera ensemble de la suite.", 'droite')
      else
        cinematique.Dire(partner, 'Worried', "Le sentier nous a repoussés cette fois.\nOn reprend notre souffle… puis on repartira ensemble, quand tu seras prêt.", 'droite')
      end
      cinematique.Dire(partner, 'Happy', "Nous savons maintenant comment nous aider. [color=#69D98C]Lost Wood[color] ne nous séparera pas.", 'droite')
      cinematique.Dire(partner, 'Happy', "Rapproche-toi de l'entrée de la forêt quand tu voudras décider de notre départ.", 'droite')
      UI:ResetSpeaker()
      SV.Destiny.LostWoodTrip = 'pause_retour'
      SV.Destiny.LostWoodRetry = 'retour'
      SV.Destiny.LostWoodRetourEchec = true
      invite_retour_armee = true
      equipe_scene.Suivre(partner, hero)
      GAME:MoveCamera(0, 0, 30, true)
      GAME:CutsceneMode(false)
    end
    return
  end
  if CH('PLAYER') == nil or CH('Teammate1') == nil then
    GAME:FadeIn(20)
    print('[Destiny] Retrouvailles suspendues : héros ou partenaire absent, réserve préservée.')
    return
  end
  reveil_nuit.CinematiqueRetrouvailles()
end

-- ----------------------------------------------------- réveil + discussion

function reveil_nuit.CinematiqueRetrouvailles()
  local hero = CH('PLAYER')
  local partner = CH('Teammate1')
  local points = points_scene()
  local reveil_x, reveil_y = points.reveil_x, points.reveil_y

  SOUND:StopBGM()
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  AI:DisableCharacterAI(partner)

  -- Le héros attend, inconscient, au marqueur de réveil. Sur la prairie ZRV2,
  -- le partenaire entre par le sud et remonte le sentier jusqu'à lui ; sur
  -- l'ancienne carte, conserver l'arrivée latérale historique.
  GROUND:CharSetAnim(hero, 'Laying', true)
  GROUND:TeleportTo(hero, reveil_x, reveil_y, Direction.Right)
  if points.zrv then
    GROUND:TeleportTo(partner, points.entree_x, points.entree_y, Direction.Up)
    GAME:MoveCamera(points.camera_entree_x, points.camera_entree_y, 1, false)
    UI:WaitShowTitle('Zone de réveil', 20)
  else
    GROUND:TeleportTo(partner, reveil_x + 48, reveil_y, Direction.Up)
    GAME:MoveCamera(points.camera_x, points.camera_y, 1, false)
    UI:WaitShowTitle(GAME:GetCurrentGround().Name:ToLocal(), 20)
  end
  GAME:WaitFrames(45)
  UI:WaitHideTitle(20)
  GAME:FadeIn(60)
  SOUND:PlayBGM("Welcome to the World of Pokémon!.ogg", true)

  local function dire(emotion, texte)
    -- Le partenaire se tient à l'est du héros : portrait de droite, tourné
    -- vers lui, pendant toute la conversation des retrouvailles.
    cinematique.Dire(partner, emotion, texte, 'droite')
  end
  local function geste(nom)
    hero_geste(hero, nom)
  end
  local function geste_partenaire(nom)
    partenaire_geste(partner, nom)
  end

  -- Le partenaire sort du donjon, souffle un peu, puis aperçoit le héros.
  if points.zrv then
    dire("Happy", "Ouf… je suis sorti de [color=#69D98C]Lost Wood[color].")
    geste_partenaire('souffle')
    dire("Happy", "Sept étages, tout seul… Je l’ai fait !")
    -- Travelling d'accompagnement : le partenaire remonte les 224 pixels
    -- qui séparent l'entrée du point d'approche pendant que la caméra
    -- glisse, à la même vitesse, du sud vers un cadre contenant déjà les
    -- deux personnages. La mer puis la base de la montagne entrent ainsi
    -- progressivement dans la viewport.
    local marche_partenaire = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partner, points.palier_x, points.palier_y, false, 1)
      GROUND:MoveToPosition(partner, points.approche_x, points.approche_y, false, 1)
    end)
    local travelling = lancer_camera(points.camera_approche_x,
      points.camera_approche_y, 224)
    TASK:JoinCoroutines({marche_partenaire, travelling})
    dire("Normal", "C’est calme, ici. On entend la mer…")
  else
    dire("Happy", "Ouf… je suis sorti de [color=#69D98C]Lost Wood[color].")
    geste_partenaire('souffle')
    dire("Normal", "C’est calme, ici. On entend la mer…")
  end
  SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
  GROUND:CharSetEmote(partner, "exclaim", 1)
  dire("Worried", "Hé ! Là, dans l’herbe !")
  -- Pendant les derniers pas, la caméra remonte du cadre d'approche vers
  -- le cadre de dialogue : les pentes de la montagne et le ciel nocturne
  -- occupent alors le haut de l'image, au-dessus du duo.
  local travelling_approche = nil
  if points.zrv then
    travelling_approche = lancer_camera(points.camera_x, points.camera_y, 110)
  end
  GROUND:MoveToPosition(partner, points.partenaire_pres_x, points.partenaire_pres_y, false, 1)
  GROUND:CharAnimateTurnTo(partner, Direction.Left, 4)
  attendre_camera(travelling_approche)
  GAME:WaitFrames(20)
  dire("Worried", "Hé… tu m’entends ?")
  GAME:WaitFrames(30)
  dire("Worried", "Tu ne réponds pas…")
  dire("Normal", "Allez. Ouvre les yeux. Doucement.")
  GAME:WaitFrames(40)

  -- Réveil du héros : Wake est jouée dans sa durée réelle pour les espèces
  -- qui la possèdent. Le héros découvre ensuite les lieux du regard.
  if not jouer_animation(hero, 'Wake', 42) then
    GROUND:CharSetAnim(hero, 'Wake', false)
    GAME:WaitFrames(20)
    GROUND:CharEndAnim(hero)
  end
  geste('autour')
  geste('question')
  dire("Sigh", "Ah ! Enfin réveillé.")
  dire("Happy", "Tu m’as fait peur, tu sais.")
  dire("Worried", "Tu es blessé quelque part ?")
  geste('non')
  dire("Sigh", "Non ? Ouf… tant mieux.")
  dire("Normal", "La tête te tourne ?")
  geste('idle')
  dire("Normal", "Un peu, peut-être. Reste tranquille une minute.")
  dire("Normal", "Je t’ai trouvé endormi ici. Je ne sais pas depuis quand.")
  geste_partenaire('foret')
  dire("Normal", "Moi, je viens de traverser [color=#69D98C]Lost Wood[color]. C’est la forêt, au sud.")
  geste('question')
  dire("Normal", "Tu ne connais pas ?")
  geste('non')
  dire("Normal", "Non ? Alors retiens juste ça.")
  dire("Normal", "C’est un donjon. Sept étages.")
  dire("Normal", "Les chemins changent à chaque fois. Et des Pokémon sauvages y vivent.")
  geste('inquiet')
  dire("Worried", "Ça t’inquiète ?")
  geste('oui')
  dire("Normal", "C’est normal. Moi aussi, au début.")
  dire("Normal", "On avance pas à pas. On cherche les escaliers. On garde de quoi manger et se soigner.")
  geste('idle')
  dire("Happy", "Voilà. Le reste, on l’apprendra en marchant.")

  dire("Worried", "Au fait… comment tu t’appelles ?")
  geste('non')
  dire("Worried", "Tu ne t’en souviens pas ?")
  geste('oui')
  dire("Worried", "Et tu viens d’où ?")
  geste('non')
  dire("Worried", "Ça non plus…")
  geste('inquiet')
  dire("Normal", "Hé. Ce n’est pas grave.")
  dire("Normal", "On ne force pas les souvenirs. Ils reviendront peut-être tout seuls.")
  geste('ecoute')
  dire("Normal", "Qu’est-ce qu’il y a ? Tu as entendu quelque chose ?")
  geste('oui')
  dire("Normal", "Pendant que tu dormais ?")
  geste('oui')
  -- Le souvenir du rêve est entendu par le joueur seul : aucun portrait et
  -- aucune parole du héros. Le partenaire ne retient que son geste. La voix
  -- revient en vision : Cri Dimensionnel, halo doré, puis fermeture.
  vision_cri_dimensionnel()
  geste('inquiet')
  dire("Normal", "Une voix, alors…")
  dire("Normal", "Je ne sais pas qui c’était. Mais c’est un début.")
  dire("Normal", "On le garde comme indice. D’accord ?")
  geste('oui')
  dire("Happy", "D’accord. On cherchera après.")

  -- Déplacement lent vers le point de vue. Le héros se décale d'abord vers
  -- l'ouest : sur la ZRV2, le partenaire ne marche ainsi jamais sur sa case
  -- avant de prendre la sienne. Sur la prairie ZRV2, la caméra bascule en
  -- même temps vers le panorama : lune, sommet et mer dominent le cadre
  -- pendant que le duo se place tout en bas, face au nord.
  local travelling_panorama = nil
  if points.zrv then
    travelling_panorama = lancer_camera(points.camera_panorama_x,
      points.camera_panorama_y, 180)
  end
  local marche_vue_heros = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(hero, points.vue_x - 20, points.vue_y, false, 1)
  end)
  local marche_vue_partenaire = TASK:BranchCoroutine(function()
    GAME:WaitFrames(5)
    GROUND:MoveToPosition(partner, points.vue_x, points.vue_y, false, 1)
  end)
  TASK:JoinCoroutines({marche_vue_heros, marche_vue_partenaire})
  if points.zrv then
    attendre_camera(travelling_panorama)
  else
    GAME:MoveCamera(points.camera_x, points.camera_y, 45, false)
  end
  GAME:WaitFrames(45)
  cinematique.TournerGroupe({
    {partner, Direction.Up, 0, 4},
    {hero, Direction.Up, 5, 4},
  })
  cinematique.Respirer(30)

  -- Regard vers la montagne. Le héros répond par LookUp, Nod ou une émote ;
  -- le partenaire dit à voix haute ce qu'il comprend de chaque geste.
  local retour_camera = nil
  if points.zrv then
    retour_camera = lancer_camera(points.camera_x, points.camera_y, 150)
  end
  dire("Normal", "Tu vois la montagne, de l’autre côté de la mer ?")
  geste('montagne')
  geste('oui')
  GROUND:CharAnimateTurnTo(partner, Direction.Left, 4)
  dire("Happy", "Personne ici ne connaît le chemin jusqu’en haut.")
  attendre_camera(retour_camera)
  geste('question')
  dire("Normal", "Tu te demandes ce qu’il y a derrière ?")
  geste('oui')
  dire("Happy", "Moi aussi. Tous les jours.")
  -- Dérive presque immobile pendant l'évocation du rêve : le cadre glisse
  -- de quelques pixels vers l'est et le nord, comme un regard qui suit la
  -- ligne de crête sans quitter les deux personnages.
  local derive_reve = nil
  if points.zrv then
    derive_reve = lancer_camera(points.camera_x + 16, points.camera_y - 8, 300)
  end
  -- La patte levée : Pose reste affichée pendant toute la réplique. Pour
  -- les quelques espèces partenaires sans Pose, un petit Hop déterminé
  -- (présent dans toutes les feuilles du pool) évite une image figée.
  local pose_tenue = commencer_pose(partner)
  if not pose_tenue then geste_partenaire('joie') end
  dire("Happy", "Un jour, je ferai la carte de cette montagne !")
  terminer_pose(partner)
  dire("Normal", "Je veux devenir explorateur.")
  geste('question')
  dire("Normal", "Pourquoi ? Pour trouver les chemins où personne ne va.")
  dire("Normal", "Et si un Pokémon se perd là-haut, je veux pouvoir aller le chercher.")
  geste('surpris')
  dire("Happy", "Ça te surprend ?")
  geste('non')
  dire("Happy", "Non ? Hmm… tu as raison. C’est simple, au fond.")
  dire("Normal", "Explorer. Aider. Et revenir raconter le chemin.")
  geste('oui')
  dire("Happy", "Tu approuves ? Merci.")
  attendre_camera(derive_reve)

  -- Retour tout aussi lent au centre du promontoire pendant que le
  -- partenaire avoue sa peur, puis parle trésors et prudence.
  local retour_centre = nil
  if points.zrv then
    retour_centre = lancer_camera(points.camera_x, points.camera_y, 300)
  end
  dire("Worried", "Mais devant [color=#69D98C]Lost Wood[color], j’ai failli faire demi-tour.")
  geste('surpris')
  dire("Normal", "Eh oui. J’avais peur.")
  dire("Normal", "Alors j’ai fait un pas. Puis un autre.")
  geste('idle')
  dire("Happy", "C’est comme ça que je suis arrivé jusqu’ici.")
  dire("Happy", "Et s’il y a un trésor en route… je ne dirai pas non !")
  geste('sourire')
  dire("Happy", "Ha ! Toi aussi ?")
  dire("Normal", "Mais si ça devient trop dangereux, on rentre. Un trésor ne vaut pas une équipe.")
  geste('idle')
  dire("Normal", "C’est ça. Savoir s’arrêter fait partie du chemin.")
  attendre_camera(retour_centre)

  geste('inquiet')
  dire("Worried", "Qu’est-ce qu’il y a ? Tu penses que tu vas me gêner ?")
  geste('oui')
  dire("Happy", "Non. Pas du tout.")
  dire("Normal", "Tu viens de te réveiller. Tu ne te souviens de rien. C’est normal d’avoir peur.")
  geste('idle')
  dire("Normal", "Moi, je connais un peu la forêt. Toi, tu garderas les yeux ouverts.")
  dire("Normal", "À deux, on se relaie. C’est déjà beaucoup.")

  geste_partenaire('foret')
  dire("Normal", "Pour rentrer, on doit retraverser [color=#69D98C]Lost Wood[color].")
  geste('foret')
  geste('inquiet')
  dire("Worried", "Je sais. Ça fait peur.")
  dire("Normal", "Mais je ne te laisse pas seul ici.")
  geste('remerciement')
  dire("Happy", "Tu me remercies ? Attends qu’on soit rentrés.")
  dire("Normal", "On restera ensemble. Pas de course. Pas de risque inutile.")
  geste('idle')
  dire("Normal", "Alors… tu viens avec moi ?")
  geste('idle')
  dire("Normal", "Prends ton temps.")
  geste('determine')
  dire("Happy", "Vraiment ?")
  geste('oui')
  geste_partenaire('joie')
  dire("Happy", "C’est décidé ! On traverse ensemble !")
  GROUND:MoveToPosition(hero, points.vue_x - 12, points.vue_y, false, 1)
  cinematique.TournerGroupe({
    {partner, Direction.Up, 0, 4},
    {hero, Direction.Up, 5, 4},
  })
  cinematique.Respirer(20)
  dire("Happy", "Un jour, on ira voir derrière cette montagne.")
  dire("Normal", "Mais d’abord, rentrons.")

  -- Dernier regard vers la montagne, puis seconde traversée à deux. La
  -- caméra remonte une dernière fois vers le panorama et y reste pendant
  -- le fondu de départ : la nuit, la lune et la crête ferment la scène.
  local travelling_final = nil
  if points.zrv then
    travelling_final = lancer_camera(points.camera_panorama_x - 8,
      points.camera_panorama_y, 180)
  end
  cinematique.TournerGroupe({
    {partner, Direction.UpRight, 0, 4},
    {hero, Direction.UpRight, 5, 4},
  })
  GAME:WaitFrames(60)
  attendre_camera(travelling_final)
  if points.zrv then GAME:WaitFrames(45) end
  cinematique.TournerGroupe({
    {partner, Direction.Down, 0, 4},
    {hero, Direction.Down, 5, 4},
  })
  cinematique.Respirer(30)

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RetrouvaillesFaites = true
  SV.Destiny.LostWoodTrip = 'retour'
  SV.Destiny.LostWoodRetourEchec = false
  lancer_retour()
end

return reveil_nuit
