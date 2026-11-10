--[[ Prologue et retrouvailles sur la prairie du réveil
     (zrv2_zone_reveil_nuit ; l'ancien script reveil_nuit reste le module
     partagé de la scène pour garder une seule écriture des dialogues).
     Prologue : juste après le quiz, le héros gît endormi dans la prairie.
     Sur fond noir, quatre pensées traversent son sommeil ; le fondu se lève
     un instant sur lui, puis l'image bascule chez le partenaire.
     Aller : le partenaire traverse les Bois Perdus seul, remonte depuis
     l'entrée sud et arrive au point de réveil où le héros est allongé. Il
     le réveille, ils se présentent — le héros ne se souvient que de son
     prénom, que le joueur saisit alors au clavier — puis le partenaire lui
     nomme la prairie et la forêt, et ils regardent ensemble la montagne qui
     se dresse au-delà de la mer.
     À part son prénom, le héros ne prononce aucun mot : il répond par
     l'animation Nod, son idle, ses orientations et ses émotes. Le partenaire
     formule les questions, réagit à voix haute à ces gestes et porte seul le
     dialogue. Sa déclaration d'explorateur utilise Pose, la patte levée,
     uniquement lorsque la feuille SpriteCollab de son espèce la contient.
     Retour : le segment inverse des Bois Perdus ramène le duo vers la falaise,
     cette fois au jour. Échec du retour : bref rappel, puis nouvelle
     tentative en duo.
     Textes originaux PMD Destiny. Transitions et cadrage testés sur un banc
     moteur avec sorties forcées ; parcours complet des étages non testé.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local recrutement = require 'destiny.recrutement'

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
    -- cadre de dialogue à Y=200 ne conserve qu'une partie de la montagne,
    -- mais place les pieds des acteurs à l'ordonnée écran 160, donc avec
    -- une vraie marge au-dessus de la boîte de texte (qui commence à 188).
    return {
      zrv = true,
      reveil_x = point_reveil.Position.X,
      reveil_y = point_reveil.Position.Y,
      vue_x = point_reveil.Position.X,
      vue_y = point_reveil.Position.Y,
      camera_x = point_reveil.Position.X + 8,
      camera_y = point_reveil.Position.Y - 40,
      camera_ouverture_x = point_reveil.Position.X - 8,
      camera_ouverture_y = point_reveil.Position.Y - 104,
      camera_panorama_x = point_reveil.Position.X + 8,
      camera_panorama_y = point_reveil.Position.Y - 88,
      camera_approche_x = point_reveil.Position.X + 8,
      camera_approche_y = point_reveil.Position.Y + 48,
      entree_x = entree.Position.X,
      entree_y = entree.Position.Y,
      camera_entree_x = entree.Position.X + 8,
      -- Centre sud maximal en Clamp sur la carte 768x576 : 576 - 120.
      camera_entree_y = 456,
      entree_dialogue_x = entree.Position.X,
      entree_dialogue_y = entree.Position.Y - 56,
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

-- La prairie reste en ScrollEdge.Clamp en permanence. L’entrée sud est
-- donc d’abord traversée en silence jusqu’à y=504, première ligne de
-- dialogue réellement visible dans le cadre sud maximal (392, 456).

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

-- Le héros reste muet pendant toute la rencontre. Il répond par le vrai
-- hochement Nod quand son espèce le possède, par son idle lorsqu'il écoute,
-- et par quelques orientations/émotes lisibles pour les autres réactions.
local function hero_geste(hero, geste, respirer)
  if hero == nil then return end
  if respirer ~= false then cinematique.Respirer(20) end
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(30)
  elseif geste == 'non' then
    -- Aucune feuille du pool n'a d'animation « secouer la tête » distincte :
    -- oscillation de 45° autour de Right (le partenaire est à l’est),
    -- plutôt que les anciens demi-tours gauche/droite façon toupie.
    GROUND:CharAnimateTurnTo(hero, Direction.UpRight, 4)
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.UpRight, 4)
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(12)
  elseif geste == 'oui' or geste == 'oui_inquiet' then
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    if not jouer_animation(hero, 'Nod', 20) then
      -- Repli à 45° : DownRight -> Right, deux fois.
      GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
      GAME:WaitFrames(7)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(7)
      GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
      GAME:WaitFrames(7)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(12)
    end
    if geste == 'oui_inquiet' then
      -- Même appel, donc une seule respiration : acquiescement, puis
      -- inquiétude silencieuse en baissant le regard à 45°.
      GROUND:CharSetEmote(hero, 'sweating', 1)
      GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
      GAME:WaitFrames(24)
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
      GAME:WaitFrames(10)
    end
  elseif geste == 'idle' then
    -- Réponse d'écoute : retour à l'idle par défaut, face au partenaire.
    GROUND:CharEndAnim(hero)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(26)
  elseif geste == 'autour' then
    -- Balayage continu à 45° (environ 50 frames) : nord, ouest, sud,
    -- puis retour vers le partenaire à l’est.
    GROUND:CharAnimateTurnTo(hero, Direction.UpRight, 4)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(6)
    GROUND:CharAnimateTurnTo(hero, Direction.UpLeft, 4)
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(6)
    GROUND:CharAnimateTurnTo(hero, Direction.DownLeft, 4)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(6)
    GROUND:CharAnimateTurnTo(hero, Direction.DownRight, 4)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
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
  elseif geste == 'notice' then
    -- Prise de conscience légère : notice silencieuse, retour vers le
    -- partenaire. Le vrai shock reste réservé au reflet.
    GROUND:CharSetEmote(hero, 'notice', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(24)
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
local function partenaire_geste(partenaire, geste, respirer)
  if partenaire == nil then return end
  if respirer ~= false then cinematique.Respirer(20) end
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
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
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
  -- Filet défensif : la prairie reste en Clamp à la sortie.
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
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
-- aucun portrait, aucun locuteur, seulement du texte sur le noir. Il ne se
-- souvient plus de rien — sauf de son prénom.
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

  SOUND:FadeOutBGM(30)
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
  -- Quatre pensées courtes en voix-off. SetAutoFinish(true) donne aux
  -- voix-off le fondu d'entrée et de sortie du TitleDialog PMDO (60 ticks,
  -- comme les textes de fin/crédits de la base) : chaque phrase apparaît
  -- entière, puis s'efface lentement quand le joueur avance.
  UI:SetAutoFinish(true)
  UI:WaitShowVoiceOver("…Où suis-je ?", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("Tout est flou… Je ne me souviens de rien.", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("…Sauf d’une chose.", -1)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver("Mon prénom…", -1)
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
  recrutement.synchroniser()
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
  -- Le partenaire montre d’abord l’entrée, au sud de la carte ZRV.
  cinematique.TournerGroupe({
    {partner, Direction.Down, 0, 4},
    {hero, Direction.Down, 5, 4},
  })
  cinematique.Respirer(10)
  cinematique.Dire(partner, 'Normal', "Voici le chemin du retour, par les [color=#69D98C]Bois Perdus[color]…", 'standard')
  UI:ResetSpeaker() -- question système, pas une réplique
  UI:ChoiceMenuYesNo('Souhaitez-vous retourner dans les Bois Perdus ?', true)
  UI:WaitForChoice()
  -- La réponse s’adresse ensuite au héros : face à face, portrait droite.
  cinematique.RegarderGroupe({
    {partner, hero, 0, 4},
    {hero, partner, 5, 4},
  })
  cinematique.Respirer(10)
  if UI:ChoiceResult() then
    cinematique.Dire(partner, 'Happy', "Alors on repart. Ensemble, cette fois encore.", 'droite')
    invite_retour_en_cours = false
    lancer_retour()
    return
  end
  cinematique.Dire(partner, 'Normal', "D'accord, reposons-nous encore un peu. Je te suivrai quand tu reviendras vers l'entrée.", 'droite')
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
      UI:ResetSpeaker()
      if SV.Destiny.LostWoodCause == 'abandon' then
        -- Abandon volontaire : le duo revient debout depuis le sentier sud
        -- et reprend son souffle après avoir battu en retraite.
        GROUND:TeleportTo(hero, points.vue_x - 20, points.vue_y + 36, Direction.Up)
        GROUND:TeleportTo(partner, points.vue_x, points.vue_y + 36, Direction.Up)
        if points.zrv then
          GAME:MoveCamera(points.camera_x, points.camera_approche_y, 1, false)
        else
          GAME:MoveCamera(points.camera_x, points.camera_y, 1, false)
        end
        GAME:FadeIn(30)
        local retour_heros = TASK:BranchCoroutine(function()
          GROUND:MoveToPosition(hero, points.vue_x - 20, points.vue_y, false, 1)
          GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
        end)
        local retour_partenaire = TASK:BranchCoroutine(function()
          GAME:WaitFrames(4)
          GROUND:MoveToPosition(partner, points.vue_x, points.vue_y, false, 1)
          GROUND:CharAnimateTurnTo(partner, Direction.Down, 4)
        end)
        local retour_cam = nil
        if points.zrv then
          retour_cam = lancer_camera(points.camera_x, points.camera_y, 48)
        end
        TASK:JoinCoroutines({retour_heros, retour_partenaire})
        attendre_camera(retour_cam)
        partenaire_geste(partner, 'souffle', false)
        cinematique.RegarderGroupe({
          {partner, hero, 0, 4},
          {hero, partner, 5, 4},
        })
        cinematique.Respirer(10)
        cinematique.Dire(partner, 'Worried', "Ouf… on a réussi à ressortir des [color=#69D98C]Bois Perdus[color] avant d’être submergés.", 'droite')
        cinematique.Dire(partner, 'Normal', "On a bien fait de battre en retraite ensemble.\nOn reprend notre souffle… puis on décidera de la suite.", 'droite')
      else
        -- K.O. en donjon : les deux partenaires reprennent connaissance au point
        -- de réveil ; le partenaire se relève d’abord et réveille le héros.
        GROUND:TeleportTo(hero, points.vue_x - 20, points.vue_y, Direction.Right)
        GROUND:TeleportTo(partner, points.vue_x + 4, points.vue_y, Direction.Left)
        GROUND:CharSetAnim(hero, 'Laying', true)
        GROUND:CharSetAnim(partner, 'Laying', true)
        if points.zrv then
          GAME:MoveCamera(points.camera_panorama_x, points.camera_panorama_y, 1, false)
          GAME:FadeIn(30)
          GAME:MoveCamera(points.camera_x, points.camera_y, 60, false)
        else
          GAME:MoveCamera(points.camera_x, points.camera_y, 1, false)
          GAME:FadeIn(30)
        end
        if not jouer_animation(partner, 'Wake', 42) then
          GROUND:CharEndAnim(partner)
          GAME:WaitFrames(20)
        end
        GROUND:CharSetEmote(partner, 'sweating', 1)
        GAME:WaitFrames(18)
        SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
        GROUND:CharSetEmote(partner, 'exclaim', 1)
        GAME:WaitFrames(16)
        GROUND:MoveToPosition(partner, points.vue_x, points.vue_y, false, 1)
        GROUND:CharAnimateTurnTo(partner, Direction.Left, 4)
        cinematique.Dire(partner, 'Worried', "Hé ! Tu m’entends… ? Réveille-toi !", 'droite')
        if not jouer_animation(hero, 'Wake', 42) then
          GROUND:CharEndAnim(hero)
          GAME:WaitFrames(20)
        end
        GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
        cinematique.Respirer(12)
        cinematique.Dire(partner, 'Worried', "Ouf… tu ouvres enfin les yeux !", 'droite')
        cinematique.Dire(partner, 'Worried', "On a tous les deux perdu connaissance dans les [color=#69D98C]Bois Perdus[color] et on s’est retrouvés ici…\nOn reprend notre souffle, puis on repartira ensemble quand tu seras prêt.", 'droite')
      end
      cinematique.Dire(partner, 'Happy', "Nous savons maintenant comment nous aider. Les [color=#69D98C]Bois Perdus[color] ne nous sépareront pas.", 'droite')
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
  local membre_heros, index_heros = equipe_scene.Membre('Hero')
  local membre_partenaire, index_partenaire = equipe_scene.Membre('Partner')
  if hero == nil or partner == nil or membre_heros == nil or membre_partenaire == nil
     or index_heros == index_partenaire or index_heros ~= GAME:GetTeamLeaderIndex() then
    print('[Destiny] Retrouvailles suspendues : identité du duo absente ou ambiguë.')
    return
  end
  local points = points_scene()
  local reveil_x, reveil_y = points.reveil_x, points.reveil_y

  SOUND:FadeOutBGM(30)
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
    UI:WaitShowTitle('Champs des Rêves', 20)
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
  local function geste(nom, respirer)
    hero_geste(hero, nom, respirer)
  end
  local function geste_partenaire(nom, respirer)
    partenaire_geste(partner, nom, respirer)
  end
  local function penser(emotion, texte)
    -- Pensée du héros : son portrait à gauche (placement standard), texte
    -- simplement entre parenthèses ; il ne prononce rien à voix haute.
    cinematique.Dire(hero, emotion, "(" .. texte .. ")", 'standard')
  end

  -- Découverte du reflet à deux acteurs : le héros sursaute devant l’eau ;
  -- 5 frames après le début du Hop, le partenaire remarque sa réaction
  -- (notice silencieuse) et se tourne vers lui. Les pensées qui suivent
  -- se déroulent donc face à face.
  local function decouvrir_reflet()
    cinematique.Respirer(20)
    UI:ResetSpeaker()
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(34)
    SOUND:PlayBattleSE('EVT_Emote_Shock')
    GROUND:CharSetEmote(hero, 'shock', 1)
    local reaction_partenaire = TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:CharSetEmote(partner, 'notice', 1)
      GROUND:CharAnimateTurnTo(partner, Direction.Left, 4)
    end)
    local sursaut_heros = TASK:BranchCoroutine(function()
      if not jouer_animation(hero, 'Hop', 24) then
        GAME:WaitFrames(18)
      end
    end)
    TASK:JoinCoroutines({reaction_partenaire, sursaut_heros})
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(16)
  end

  -- Sans second sursaut, le héros montre l’eau au nord ; le partenaire la
  -- regarde 5 frames plus tard, puis les deux se font de nouveau face.
  local function montrer_reflet()
    cinematique.Respirer(20)
    local regard_heros = TASK:BranchCoroutine(function()
      GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
      GAME:WaitFrames(18)
    end)
    local regard_partenaire = TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:CharAnimateTurnTo(partner, Direction.Up, 4)
      GAME:WaitFrames(18)
    end)
    TASK:JoinCoroutines({regard_heros, regard_partenaire})
    cinematique.TournerGroupe({
      {partner, Direction.Left, 0, 4},
      {hero, Direction.Right, 5, 4},
    })
  end

  -- Montagne regardée ensemble : partenaire à t+0, héros à t+5, attente
  -- commune, puis retour face à face en parallèle.
  local function regarder_montagne_ensemble()
    cinematique.Respirer(20)
    local regard_partenaire = TASK:BranchCoroutine(function()
      GROUND:CharAnimateTurnTo(partner, Direction.Up, 4)
      if not jouer_animation(partner, 'LookUp', 18) then
        GAME:WaitFrames(24)
      end
    end)
    local regard_heros = TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
      if not jouer_animation(hero, 'LookUp', 18) then
        GAME:WaitFrames(24)
      end
    end)
    TASK:JoinCoroutines({regard_partenaire, regard_heros})
    GAME:WaitFrames(14)
    cinematique.TournerGroupe({
      {partner, Direction.Left, 0, 4},
      {hero, Direction.Right, 5, 4},
    })
  end

  -- Acceptation en parallèle : une seule respiration commune, héros qui
  -- acquiesce sans respiration interne, partenaire joyeux à +5 frames.
  local function acceptation_parallele()
    cinematique.Respirer(20)
    local oui_heros = TASK:BranchCoroutine(function()
      geste('oui', false)
    end)
    local joie_partenaire = TASK:BranchCoroutine(function()
      GAME:WaitFrames(5)
      geste_partenaire('joie', false)
    end)
    TASK:JoinCoroutines({oui_heros, joie_partenaire})
  end

  -- Le partenaire sort du donjon, souffle un peu, puis aperçoit le héros.
  if points.zrv then
    -- Entrée silencieuse : 56 px depuis (384, 560) jusqu’à (384, 504),
    -- avant tout dialogue. Le DeepBreath suit sans respiration de
    -- 20 frames artificielle, puis les deux premières répliques.
    GROUND:MoveToPosition(partner, points.entree_dialogue_x,
      points.entree_dialogue_y, false, 1)
    geste_partenaire('souffle', false)
    dire("Happy", "Ouf… je suis sorti des [color=#69D98C]Bois Perdus[color].")
    dire("Happy", "Une traversée tout seul… Je l’ai fait !")
    -- Travelling d'accompagnement de 168 frames : le partenaire remonte
    -- (384, 504) -> (376, 400) -> (376, 336) pendant que la caméra glisse
    -- de (392, 456) à (384, 288). La mer puis la montagne entrent ainsi
    -- progressivement dans la viewport.
    local marche_partenaire = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partner, points.palier_x, points.palier_y, false, 1)
      GROUND:MoveToPosition(partner, points.approche_x, points.approche_y, false, 1)
    end)
    local travelling = lancer_camera(points.camera_approche_x,
      points.camera_approche_y, 168)
    TASK:JoinCoroutines({marche_partenaire, travelling})
    dire("Normal", "C’est calme, ici. On entend la mer…")
  else
    dire("Happy", "Ouf… je suis sorti des [color=#69D98C]Bois Perdus[color].")
    geste_partenaire('souffle')
    dire("Normal", "C’est calme, ici. On entend la mer…")
  end
  SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
  GROUND:CharSetEmote(partner, "exclaim", 1)
  GAME:WaitFrames(20)
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
    -- L’espèce n’a pas Wake : ne pas forcer une animation absente.
    GROUND:CharEndAnim(hero)
    GAME:WaitFrames(20)
  end
  -- Laisser le réveil se lire avant le balayage du regard ; le geste
  -- ajoute ensuite sa propre respiration de 20 frames.
  GAME:WaitFrames(15)
  geste('autour')
  geste('question', false)
  dire("Sigh", "Ah ! Enfin réveillé.")
  dire("Happy", "Tu m’as fait peur, tu sais.")
  dire("Worried", "Tu es blessé quelque part ?")
  geste('non')
  dire("Sigh", "Non ? Ouf… tant mieux.")
  dire("Normal", "La tête te tourne ?")
  geste('inquiet')
  dire("Normal", "Un peu, peut-être. Reste tranquille une minute.")
  dire("Normal", "Je t’ai trouvé endormi ici. Je ne sais pas depuis quand.")
  -- Présentations. Le partenaire donne d’abord son prénom (celui choisi
  -- dans le quiz), puis demande celui du héros : c’est la seule chose dont
  -- le héros se souvienne, et le joueur le saisit alors au clavier (même
  -- NameMenu et même secours que le NOM du partenaire dans le quiz).
  local nom_partenaire = membre_partenaire.Nickname
  local nom_heros = membre_heros.Nickname
  dire("Happy", "Au fait, on ne s’est même pas présentés !")
  dire("Happy", "Je m’appelle " .. nom_partenaire .. " !")
  cinematique.Respirer(20)
  dire("Normal", "Et toi, comment tu t’appelles ?")
  UI:ResetSpeaker()
  UI:NameMenu("Quel est ton prénom ?", "C’est tout ce dont tu te souviens.", 60)
  UI:WaitForChoice()
  nom_heros = UI:ChoiceResult()
  if nom_heros == "" then
    nom_heros = _DATA:GetMonster(membre_heros.BaseForm.Species).Name:ToLocal()
  end
  GAME:SetCharacterNickname(membre_heros, nom_heros)
  dire("Happy", "« " .. nom_heros .. " »… ! C’est un joli prénom !")
  geste_partenaire('joie')
  dire("Happy", "Enchanté, " .. nom_heros .. " !")
  geste('sourire')

  -- D’où vient-il ? À part son prénom, le héros ne se rappelle rien.
  dire("Normal", "Dis… tu viens d’où ?")
  dire("Normal", "Et qu’est-ce que tu faisais endormi ici, tout seul, en pleine nuit ?")
  geste('non')
  dire("Worried", "Tu as tout oublié… ?")
  geste('oui_inquiet')
  dire("Normal", "Hé. Ce n’est pas grave.")
  dire("Normal", "Tu t’es peut-être cogné en tombant. Ça te reviendra, tu verras.")

  -- Le héros regarde les lieux : le partenaire lui présente la prairie et
  -- la forêt qu’il vient de traverser, puis dit pourquoi il est venu ce soir.
  geste('autour')
  dire("Normal", "Ici, c’est la prairie des [color=#69D98C]Champs des Rêves[color].")
  dire("Normal", "Elle est tout au bout des [color=#69D98C]Bois Perdus[color], face à la mer.")
  geste_partenaire('foret')
  dire("Normal", "Moi, je viens de les traverser tout seul, ce soir. C’est un donjon : ses sentiers changent à chaque traversée, et des Pokémon sauvages y vivent.")
  dire("Normal", "Je voulais voir le reflet de la lune sur l’eau…")
  dire("Normal", "Et me prouver que j’étais capable de venir jusqu’ici tout seul.")
  geste('ecoute')

  -- Déplacement vers le point de vue. Le héros se décale d'abord vers
  -- l'ouest : sur la ZRV2, le partenaire ne marche ainsi jamais sur sa case
  -- avant de prendre la sienne. La caméra rejoint directement le cadrage
  -- du reflet (camera_panorama_y + 40, soit Y=192) pendant leur courte marche
  -- afin d'éviter toute attente immobile des personnages.
  local travelling_panorama = nil
  if points.zrv then
    travelling_panorama = lancer_camera(points.camera_panorama_x,
      points.camera_panorama_y + 40, 42)
  end
  local marche_vue_heros = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(hero, points.vue_x - 20, points.vue_y, false, 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
  end)
  local marche_vue_partenaire = TASK:BranchCoroutine(function()
    GAME:WaitFrames(5)
    GROUND:MoveToPosition(partner, points.vue_x, points.vue_y, false, 1)
    GROUND:CharAnimateTurnTo(partner, Direction.Up, 4)
  end)
  TASK:JoinCoroutines({marche_vue_heros, marche_vue_partenaire})
  if points.zrv then
    attendre_camera(travelling_panorama)
  else
    GAME:MoveCamera(points.camera_x, points.camera_y, 30, false)
  end

  -- Le héros aperçoit son reflet dans l’eau : il réalise en pensée qu’il
  -- est un humain devenu Pokémon (nom d’espèce et accord depuis le choix
  -- du quiz). Le partenaire, d’abord confus et sceptique, finit par le
  -- croire en voyant sa réaction.
  decouvrir_reflet()
  local espece_heros = _DATA:GetMonster(membre_heros.BaseForm.Species).Name:ToLocal()
  local transforme = "transformé"
  if membre_heros.BaseForm.Gender == Gender.Female then
    transforme = "transformée"
  end
  penser("Surprised", "Je… je suis un Pokémon ?!")
  penser("Worried", "Mais moi, je suis un humain !")
  penser("Surprised", "Pourquoi je me suis " .. transforme .. " en " .. espece_heros .. " ?!")
  cinematique.Respirer(30) -- laisser la révélation marquer un temps
  dire("Worried", "Eh ! Qu’est-ce qui te prend, tout d’un coup ?")
  montrer_reflet()
  dire("Normal", "Ton reflet… ?")
  dire("Normal", "…On dirait que tu vois ton visage pour la première fois.")
  geste('oui')
  dire("Worried", "Attends. Tu essaies de me dire que…")
  dire("Worried", "…tu serais un humain ?!")
  geste('determine')
  dire("Worried", "Un humain devenu Pokémon… ?")
  dire("Worried", nom_heros .. ", tu en es sûr ? Je n’avais jamais entendu une chose pareille…")
  geste('oui_inquiet')
  dire("Normal", "…Mais tout à l’heure, devant ton reflet, tu as sursauté pour de vrai.")
  dire("Normal", "Et tu as l’air tellement perdu… Je ne pense pas que tu plaisantes.")
  dire("Normal", "Pardon d’avoir douté. Je ne comprends pas ce qui t’est arrivé, mais je veux t’aider.")
  dire("Happy", "D’accord, " .. nom_heros .. ". Je te crois.")
  cinematique.Respirer(20)
  dire("Happy", "De toute façon, humain ou Pokémon… pour moi, tu es " .. nom_heros .. " !")
  geste('remerciement')
  dire("Normal", "Allez, relève la tête.")

  -- Regard vers la montagne. Le héros répond par LookUp, Nod ou une émote ;
  -- le partenaire dit à voix haute ce qu'il comprend de chaque geste.
  local retour_camera = nil
  if points.zrv then
    retour_camera = lancer_camera(points.camera_x, points.camera_y, 150)
  end
  dire("Normal", "Tu vois la montagne, de l’autre côté de la mer ?")
  regarder_montagne_ensemble()
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
  -- La patte levée : Pose reste affichée pendant les deux phrases,
  -- jusqu’à « Je veux devenir explorateur. » inclus. Pour les quelques
  -- espèces partenaires sans Pose, un petit Hop déterminé évite une
  -- image figée avant la déclaration.
  local pose_tenue = commencer_pose(partner)
  if not pose_tenue then geste_partenaire('joie') end
  dire("Happy", "Un jour, je ferai la carte de cette montagne !")
  dire("Normal", "Je veux devenir explorateur.")
  terminer_pose(partner)
  geste('question')
  dire("Normal", "Pourquoi ? Pour trouver les chemins où personne ne va.")
  dire("Normal", "Et si un Pokémon se perd là-haut, je veux pouvoir aller le chercher.")
  -- Son rêve rejoint le mystère du héros : explorer, c’est aussi chercher
  -- des réponses — extase (Joyous) sur les mystères du monde.
  dire("Joyous", "Et puis… ce monde est plein de mystères !")
  dire("Joyous", "Qui sait ? À force d’explorer, on découvrira peut-être pourquoi tu es devenu un Pokémon.")
  dire("Happy", "Et peut-être même comment te rendre ta mémoire !")
  geste('notice')
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
  dire("Worried", "Mais devant les [color=#69D98C]Bois Perdus[color], j’ai failli faire demi-tour.")
  geste('notice')
  dire("Normal", "Eh oui. J’avais peur.")
  dire("Normal", "Alors j’ai fait un pas. Puis un autre.")
  dire("Happy", "C’est comme ça que je suis arrivé jusqu’ici.")
  dire("Happy", "Et s’il y a un trésor en route… je ne dirai pas non !")
  geste('sourire')
  dire("Happy", "Ha ! Toi aussi ?")
  dire("Normal", "Mais si ça devient trop dangereux, on rentre. Un trésor ne vaut pas une équipe.")
  geste('oui')
  dire("Normal", "C’est ça. Savoir s’arrêter fait partie du chemin.")
  attendre_camera(retour_centre)

  geste('inquiet')
  dire("Worried", "Qu’est-ce qu’il y a ? Tu penses que tu vas me gêner ?")
  geste('oui')
  dire("Happy", "Non. Pas du tout.")
  dire("Normal", "Tu viens de te réveiller. Tu ne te souviens presque de rien. C’est normal d’avoir peur.")
  dire("Normal", "Moi, je connais un peu la forêt. Toi, tu garderas les yeux ouverts.")
  dire("Normal", "À deux, on se relaie. C’est déjà beaucoup.")

  -- La nuit est tombée : le partenaire propose au héros de le suivre
  -- jusqu’à Réverie Town, la grande ville voisine — ce n’est pas son
  -- village — puis laisse le choix au joueur. Tant que le joueur refuse,
  -- le partenaire insiste ; seul un oui fait continuer la scène.
  dire("Normal", "Là, il fait déjà nuit. Je ne vais pas te laisser dormir ici tout seul.")
  dire("Normal", "Il y a une grande ville pas loin d’ici : [color=#69D98C]Rêverie Town[color] !")
  dire("Normal", "Là-bas, il y a plein de Pokémon, on trouvera bien quelqu’un pour t’aider.")
  geste_partenaire('foret')
  dire("Normal", "Pour y aller, il faut retraverser les [color=#69D98C]Bois Perdus[color]… et tout seul, j’avoue que j’ai un peu peur.")
  geste('foret')
  dire("Normal", "Alors… tu viens avec moi ?")
  local accepte, refus = false, 0
  while not accepte do
    UI:ResetSpeaker() -- choix du joueur, sans portrait
    UI:ChoiceMenuYesNo("Le suivre jusqu’à Réverie Town ?", true)
    UI:WaitForChoice()
    accepte = UI:ChoiceResult()
    if not accepte then
      refus = refus + 1
      geste('non')
      if refus == 1 then
        dire("Worried", "Hein ? Mais tu ne vas quand même pas rester ici tout seul, en pleine nuit ?")
      elseif refus == 2 then
        dire("Normal", "Allez ! À Réverie Town, il y a plein de Pokémon gentils. On te trouvera un endroit où dormir, promis.")
      elseif refus == 3 then
        dire("Worried", "S’il te plaît… De toute façon, tout seul dans la forêt, j’aurai trop peur. Reste avec moi !")
      else
        dire("Normal", "Allez, " .. nom_heros .. " ! On retraversera les [color=#69D98C]Bois Perdus[color] à deux, ce sera beaucoup moins effrayant. Tu viens ?")
      end
    end
  end
  acceptation_parallele()
  dire("Happy", "Super ! Merci, " .. nom_heros .. " !")
  dire("Happy", "Allez, en route pour Réverie Town !")
  dire("Normal", "Et un jour, quand on sera devenus de vrais explorateurs… on ira voir ce qu’il y a derrière cette montagne. Promis ?")

  -- Dernier regard vers la montagne, puis le duo se tourne vers le sud
  -- et descend ensemble le sentier vers la sortie de la prairie pendant
  -- que la caméra accompagne son départ vers les Bois Perdus.
  local travelling_final = nil
  if points.zrv then
    travelling_final = lancer_camera(points.camera_panorama_x - 8,
      points.camera_panorama_y + 24, 48)
  end
  cinematique.TournerGroupe({
    {partner, Direction.Up, 0, 4},
    {hero, Direction.Up, 5, 4},
  })
  GAME:WaitFrames(35)
  attendre_camera(travelling_final)
  cinematique.TournerGroupe({
    {partner, Direction.Down, 0, 4},
    {hero, Direction.Down, 5, 4},
  })
  GAME:WaitFrames(10)
  local cible_sortie_y = points.zrv and (points.approche_y + 32) or (points.vue_y + 48)
  local travelling_sortie = nil
  if points.zrv then
    travelling_sortie = lancer_camera(points.camera_entree_x,
      points.camera_approche_y + 48, 128)
  end
  local marche_sortie_heros = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(hero, points.vue_x - 20, cible_sortie_y, false, 1)
  end)
  local marche_sortie_partenaire = TASK:BranchCoroutine(function()
    GAME:WaitFrames(4)
    GROUND:MoveToPosition(partner, points.vue_x, cible_sortie_y, false, 1)
  end)
  TASK:JoinCoroutines({marche_sortie_heros, marche_sortie_partenaire})
  attendre_camera(travelling_sortie)

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RetrouvaillesFaites = true
  SV.Destiny.LostWoodTrip = 'retour'
  SV.Destiny.LostWoodRetourEchec = false
  lancer_retour()
end

return reveil_nuit
