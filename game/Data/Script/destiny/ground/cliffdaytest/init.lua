require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local cliffdaytest = {}
local function anim(ch, name, looped)
  if ch ~= nil then GROUND:CharSetAnim(ch, name, looped) end
end
local function say(ch, emotion, text, placement)
  cinematique.Dire(ch, emotion, text, placement)
end
-- Pendant toute l’altercation avec la Team Dazzling, le héros suit la
-- conversation du regard : il se tourne vers la fille qui parle, puis
-- revient vers le partenaire uniquement quand celui-ci lui répond.
local function hero_regarde_locuteur(hero, locuteur)
  if hero ~= nil and locuteur ~= nil and locuteur ~= hero then
    GROUND:CharTurnToCharAnimated(hero, locuteur, 4)
  end
end
local SON_MER = 'Destiny_Falaise_Mer'
local function demarrer_mer()
  -- La BGM « Cliff Camp.ogg » est portée par la carte ; cette boucle ajoute
  -- le bruit de la mer sous la musique de la falaise.
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end
local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end
local function personnage_dazzling(nom)
  local ch = CH(nom)
  if ch == nil then ch = GROUND:SpawnerDoSpawn(nom) end
  if ch ~= nil then
    GROUND:Unhide(nom)
    AI:DisableCharacterAI(ch)
  end
  return ch
end
-- Le facteur Bekipan de la poste de Réverie Town, spawner dédié du ground.
local function facteur_bekipan()
  local ch = CH('Bekipan')
  if ch == nil then ch = GROUND:SpawnerDoSpawn('Bekipan') end
  if ch ~= nil then
    GROUND:Unhide('Bekipan')
    AI:DisableCharacterAI(ch)
  end
  return ch
end
local MUSIQUE_DAZZLING_SOCIALE = 'Team Dazzling Social.ogg'
local MUSIQUE_DAZZLING_COMBAT = 'Dazzling Fight.ogg'
local WOOSH_DAZZLING_ETOILES = 'Pre_Battle_Dazzling_Etoiles'
local function etoiles_dazzling(ch, avec_son)
  if ch == nil then return end
  -- Un seul Twinkle par cascade : les couronnes suivantes restent visuelles
  -- pour ne pas interrompre le SFX d'Adagio après quelques frames.
  if avec_son ~= false then SOUND:PlayBattleSE('_UNK_DUN_Twinkle') end
  local pos = ch.MapLoc or ch.Position
  -- Deux couronnes discrètes de petites étoiles jaunes PMDO : une basse,
  -- une à hauteur du buste/tête. Lucky_Chant_Star_Yellow fait 16x16 px et
  -- scintille sur 8 frames ; l'émetteur les répartit autour du personnage.
  for _, couronne in ipairs({{10, 28}, {28, 22}}) do
    local emitter = RogueEssence.Content.FiniteAreaEmitter(
      RogueEssence.Content.AnimData('Lucky_Chant_Star_Yellow', 3))
    emitter.Range = couronne[2]
    emitter.Speed = 24
    emitter.TotalParticles = 5
    emitter.LocHeight = couronne[1]
    GROUND:PlayVFX(emitter, pos.X, pos.Y)
  end
end
local function poser_dazzling(ch, avec_son)
  if ch == nil then return end
  UI:ResetSpeaker()
  etoiles_dazzling(ch, avec_son)
  -- PoseGroundAction joue la vraie Pose SpriteCollab (FrameType moteur
  -- Pose = 50 ; l’InternalIndex 13 reste conservé dans les .chara), puis
  -- la maintient sur sa frame de retour pendant la réplique, au lieu de
  -- la laisser retomber en Idle après 14 à 16 ticks.
  local ok = pcall(function()
    local anim_id = RogueEssence.Content.GraphicsManager.GetAnimIndex('Pose')
    GROUND:CharSetAction(ch,
      RogueEssence.Ground.PoseGroundAction(ch.Position, ch.Direction, anim_id))
  end)
  if not ok then anim(ch, 'Pose', false) end
end
local function finir_pose_dazzling(ch)
  if ch ~= nil then GROUND:CharEndAnim(ch) end
end
-- Rotations du trio en parallèle : Adagio mène, Aria suit 3 frames plus
-- tard et Sonata 6 frames plus tard, toutes à la vitesse standard 4.
local function tourner_trio(adagio, Aria, sonata, direction)
  cinematique.TournerGroupe({
    {adagio, direction, 0, 4},
    {Aria, direction, 3, 4},
    {sonata, direction, 6, 4},
  })
end
local function poser_trio(adagio, Aria, sonata)
  poser_dazzling(adagio, true)
  GAME:WaitFrames(7)
  poser_dazzling(Aria, false)
  GAME:WaitFrames(7)
  poser_dazzling(sonata, false)
end
local function finir_pose_trio(adagio, Aria, sonata)
  finir_pose_dazzling(adagio)
  finir_pose_dazzling(Aria)
  finir_pose_dazzling(sonata)
end

-- Fight Woosh étoilé Team Dazzling : overlay plein écran 320×240, indépendant
-- de la carte. On démarre à la frame 12 (première traversée des étoiles) ;
-- à 180 ticks, son flash blanc est plein et masque le passage en donjon.
local function jouer_woosh_dazzling()
  local centre = GAME:GetCameraCenter()
  local emitter = RogueEssence.Content.FiniteOverlayEmitter()
  emitter.Anim = RogueEssence.Content.BGAnimData(WOOSH_DAZZLING_ETOILES, 2, 12, 109)
  emitter.Layer = DrawLayer.Top
  emitter.TotalTime = 196
  emitter.FadeIn = 0
  emitter.FadeOut = 0
  emitter.RepeatX = false
  emitter.RepeatY = false
  GROUND:PlayVFX(emitter, centre.X - 160, centre.Y - 120)
end

-- La musique est lancée sans fondu et le Woosh dans la même frame Lua.
-- La map donjon déclare la même piste : PMDO la laisse donc continuer.
local function lancer_combat_dazzling()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.CombatDazzling = 'en_cours'
  UI:ResetSpeaker()
  arreter_mer()
  SOUND:PlayBGM(MUSIQUE_DAZZLING_COMBAT, false)
  jouer_woosh_dazzling()
  SOUND:PlayBattleSE('EVT_Battle_Transition')
  GAME:WaitFrames(180)
  -- Le woosh se termine sur son blanc plein : on fige ce blanc avant
  -- d’entrer dans le donjon, sinon le fondu du ground réapparaît en noir
  -- pendant le chargement de la .rsmap.
  GAME:FadeOut(true, 0)
  GAME:CutsceneMode(false)
  GAME:EnterDungeon('dazzling_fight', 0, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Progress, false, true)
end

local function retour_destiny_en_attente()
  return SV.Destiny ~= nil and SV.Destiny.RetourAccompli
    and not SV.Destiny.FinaleDestiny
end
-- Dans la scène Destiny, le héros ne parle pas : il répond au partenaire
-- par ses orientations et ses émotes, comme lors des retrouvailles.
-- Règle de mise en scène : quand le héros et le partenaire se parlent, ils
-- se font face ; quand l’un montre une direction, il regarde dans cette
-- direction.
local function se_faire_face(premier, second)
  if premier == nil or second == nil then return end
  cinematique.RegarderGroupe({
    { premier, second, 0, 4 },
    { second, premier, 5, 4 },
  })
end

local function nom_heros()
  local ok, membre = pcall(function() return GAME:GetPlayerPartyMember(0) end)
  if ok and membre ~= nil and membre.Nickname ~= nil and membre.Nickname ~= '' then
    return cinematique.NomColore(membre.Nickname, membre)
  end
  return 'toi'
end

local function nom_partenaire()
  local ok, membre = pcall(function() return GAME:GetPlayerPartyMember(1) end)
  if ok and membre ~= nil and membre.Nickname ~= nil and membre.Nickname ~= '' then
    return cinematique.NomColore(membre.Nickname, membre)
  end
  return 'toi'
end

-- Pensée du héros : portrait et émotion, texte simplement entre
-- parenthèses, exactement comme dans la scène du réveil.
local function pense_heros(hero, emotion, contenu)
  say(hero, emotion, "(" .. contenu .. ")", 'standard')
end

-- Voix hors champ sans portrait : les trois filles restent des « ??? »
-- jusqu’à leur entrée.
local function voix_dazzling(contenu)
  UI:SetSpeaker('???', true, '', -1, '', RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue(contenu)
end

local function geste_heros(hero, geste, partner)
  if hero == nil then return end
  cinematique.Respirer(20)
  UI:ResetSpeaker()
  local function vers_partenaire()
    if partner ~= nil then
      GROUND:CharTurnToCharAnimated(hero, partner, 4)
    else
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    end
  end
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    vers_partenaire()
    GAME:WaitFrames(30)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(10)
    vers_partenaire()
    GAME:WaitFrames(12)
  elseif geste == 'oui' then
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
  elseif geste == 'inquiet' then
    GROUND:CharSetEmote(hero, 'sweating', 1)
    vers_partenaire()
    GAME:WaitFrames(36)
  elseif geste == 'determine' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    vers_partenaire()
    GAME:WaitFrames(14)
    -- Le héros montre ensuite la direction à suivre : le sud.
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(24)
  elseif geste == 'idle' then
    GROUND:CharSetAnim(hero, 'Idle', true)
    vers_partenaire()
    GAME:WaitFrames(30)
    GROUND:CharEndAnim(hero)
  end
end

function cliffdaytest.Init(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  DEBUG.EnableDbgCoro()
  local retour_destiny = retour_destiny_en_attente()
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
    -- L'arrivée du retour inverse est une cinématique : le partenaire ne
    -- doit pas encore suivre librement le héros pendant son exposition.
    if not retour_destiny then equipe_scene.Suivre(partner, hero) end
  end
  -- Adagio, Sonata et Aria restent définies par leurs spawners, mais elles
  -- n'entrent en scène que pendant la rencontre Destiny du retour inverse.
end
function cliffdaytest.PlotScripting()
  SV.Destiny = SV.Destiny or {}
  demarrer_mer()
  if SV.Destiny.CombatDazzling == 'victoire'
      or SV.Destiny.CombatDazzling == 'defaite' then
    cliffdaytest.ApresCombatTeamDazzling()
    return
  end
  if retour_destiny_en_attente() then
    cliffdaytest.SceneArriveeDestiny()
    return
  end
  if SV.Destiny.FinaleDestiny and SV.Destiny.VisiteVille == 'en_route' then
    cliffdaytest.AllerEnVille()
    return
  end
  GAME:FadeIn(20)
end
function cliffdaytest.Enter(map)
  cliffdaytest.PlotScripting()
end
function cliffdaytest.Exit(map)
  arreter_mer()
end
function cliffdaytest.Update(map) end
function cliffdaytest.GameSave(map) end
function cliffdaytest.GameLoad(map)
  cliffdaytest.PlotScripting()
end
function cliffdaytest.AllerEnVille()
  SOUND:FadeOutBGM(45)
  arreter_mer()
  GAME:FadeOut(false, 45)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  -- Réverie Town reste une carte distincte, dans sa zone d'origine.
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

-- Première rencontre de la Team Dazzling, sur le chemin de la falaise.
-- Le duo vient de dire « on y va » au warp sud (731, 762) quand la
-- musique se coupe : trois voix « ??? » hors champ, le partenaire
-- réagit avec un « ! », le héros avec un « ? » en léger différé, et
-- le partenaire reconnaît les voix (« Ne me dis pas
-- que… »). Le duo remonte se placer en (712/736, 732) face au nord
-- pendant que la caméra révèle le trio sur le chemin de l’est. Le thème
-- social ne démarre qu’au moment où les filles se mettent en marche :
-- colonne le long de la ligne verte validée (à l’ouest du panneau, entre
-- l’arbre et les souches), puis éventail en (688/712/736, 700).
function cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  local est = MRKR('Dazzling_Exit_East')
  local adagio = personnage_dazzling('Adagio')
  local sonata = personnage_dazzling('Sonata')
  local Aria = personnage_dazzling('Aria')
  if est == nil or hero == nil or partner == nil or adagio == nil
      or sonata == nil or Aria == nil then
    print('[Destiny] Rencontre Team Dazzling suspendue : spawner incomplet.')
    return
  end

  -- Le trio attend hors champ sur le chemin de l’est.
  GROUND:TeleportTo(adagio, est.Position.X - 108, est.Position.Y + 8, Direction.Left)
  GROUND:TeleportTo(Aria, est.Position.X - 80, est.Position.Y - 8, Direction.Left)
  GROUND:TeleportTo(sonata, est.Position.X - 76, est.Position.Y + 24, Direction.Left)

  -- La musique se coupe avant les voix hors champ.
  SOUND:FadeOutBGM(15)
  cinematique.Respirer(15)
  voix_dazzling("Hilarant.")
  voix_dazzling("Je ne vois pas ce qu’il y a de drôle, " .. cinematique.NomColore('Sonata', 'lopunny') .. ". C’est gênant.")
  voix_dazzling("Les filles, assez. Faisons notre super entrée.")

  -- Réaction du duo vers les voix (au nord), puis face à face : c’est
  -- le partenaire qui reconnaît ces voix. Il réagit donc en premier
  -- avec un « ! » (son unique de la réaction) ; le héros répond par un
  -- « ? » en léger différé, avant que le partenaire prenne la parole.
  local reaction_partenaire = TASK:BranchCoroutine(function()
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    GROUND:CharSetEmote(partner, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(partner, Direction.UpRight, 4)
  end)
  local reaction_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(5)
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.UpRight, 4)
  end)
  TASK:JoinCoroutines({ reaction_partenaire, reaction_heros })
  cinematique.Respirer(10)
  se_faire_face(partner, hero)
  say(partner, 'Worried', "Ne me dis pas que…", 'standard')

  -- Le duo remonte de quelques pas et se place face au nord.
  local placement_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, 736, 732, false, 1)
  end)
  local placement_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(6)
    GROUND:MoveToPosition(hero, 712, 732, false, 1)
  end)
  TASK:JoinCoroutines({ placement_partenaire, placement_heros })
  cinematique.TournerGroupe({
    { partner, Direction.Up, 0, 4 },
    { hero, Direction.Up, 5, 4 },
  })

  -- Révélation à l’est, encore dans le silence : le trio se tourne vers
  -- la caméra, prend la Pose, puis regarde vers l’ouest (sa direction).
  GAME:MoveCamera(800, 468, 80, false)
  cinematique.Respirer(20)
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  GAME:WaitFrames(28)
  finir_pose_trio(adagio, Aria, sonata)
  tourner_trio(adagio, Aria, sonata, Direction.Left)

  -- Le thème social démarre pile quand les filles se déplacent vers le
  -- duo, et il durera jusqu’au combat. Colonne Adagio -> Aria -> Sonata le
  -- long de la ligne verte, puis éventail en bas du chemin.
  SOUND:PlayBGM(MUSIQUE_DAZZLING_SOCIALE, true)
  local route_verte = {
    { 800, 447 }, { 709, 441 }, { 693, 462 }, { 677, 489 },
    { 665, 510 }, { 666, 544 }, { 681, 572 }, { 695, 593 },
    { 713, 634 }, { 713, 676 },
  }
  local function marcher_route_verte(fille)
    for _, etape in ipairs(route_verte) do
      GROUND:MoveToPosition(fille, etape[1], etape[2], false, 1.5)
    end
  end
  local entree_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 852, 452, false, 1.5)
    marcher_route_verte(adagio)
    GROUND:MoveToPosition(adagio, 712, 700, false, 1.5)
  end)
  local entree_mawhile = TASK:BranchCoroutine(function()
    GAME:WaitFrames(6)
    marcher_route_verte(Aria)
    GROUND:MoveToPosition(Aria, 688, 700, false, 1.5)
  end)
  local entree_lopunny = TASK:BranchCoroutine(function()
    GAME:WaitFrames(24)
    GROUND:MoveToPosition(sonata, 884, 452, false, 1.5)
    marcher_route_verte(sonata)
    GROUND:MoveToPosition(sonata, 736, 700, false, 1.5)
  end)
  -- La caméra redescend le long du chemin puis se pose sur le face-à-face.
  local suivi_entree = TASK:BranchCoroutine(function()
    GAME:MoveCamera(690, 470, 150, false)
    GAME:MoveCamera(720, 672, 190, false)
  end)
  TASK:JoinCoroutines({ entree_adagio, entree_mawhile, entree_lopunny, suivi_entree })
  cinematique.RegarderGroupe({
    { adagio, partner, 0, 4 },
    { Aria, partner, 5, 4 },
    { sonata, hero, 10, 4 },
    { partner, adagio, 15, 4 },
    { hero, adagio, 20, 4 },
  })
  cinematique.Respirer(20)

  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Happy', "Hello~ [color=#F5D27A]Réverie Town[color] n’est pas un lieu pour des amateurs, voyons.", 'droite')
  hero_regarde_locuteur(hero, partner)
  say(partner, 'Angry', "Mais pour qui vous vous prenez ?!", 'standard')
  cinematique.Respirer(10)
  geste_heros(hero, 'question', partner)

  -- Présentation face caméra, comme une entrée en scène : la vraie Pose
  -- reste tenue pendant les noms, petites étoiles autour des trois.
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  cinematique.Respirer(20)
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Happy', cinematique.NomColore('Adagio', 'tsareena') .. ", cheffe de la [color=#FF9FD8]Team Dazzling[color].", 'droite')
  hero_regarde_locuteur(hero, Aria)
  say(Aria, 'Happy', cinematique.NomColore('Aria', 'mawile') .. ". Retenez le nom : vous l’entendrez souvent.", 'droite')
  hero_regarde_locuteur(hero, sonata)
  say(sonata, 'Joyous', "Et moi, " .. cinematique.NomColore('Sonata', 'lopunny') .. " ! La plus éblouissante des trois !", 'droite')
  hero_regarde_locuteur(hero, Aria)
  say(Aria, 'Normal', "La plus bruyante, surtout.", 'droite')
  cinematique.Respirer(20)
  finir_pose_trio(adagio, Aria, sonata)
  cinematique.RegarderGroupe({
    {adagio, partner, 0, 4},
    {Aria, partner, 3, 4},
    {sonata, hero, 6, 4},
    {partner, adagio, 9, 4},
    {hero, adagio, 12, 4},
  })
  cinematique.Respirer(10)

  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Happy', "Une équipe célèbre ne perd pas son temps avec deux enfants couverts de poussière.", 'droite')
  hero_regarde_locuteur(hero, partner)
  say(partner, 'Determined', "On a traversé les [color=#69D98C]Bois Perdus[color]. Deux fois.", 'standard')
  -- Aria se moque du duo : portrait Joyous canonique.
  hero_regarde_locuteur(hero, Aria)
  say(Aria, 'Joyous', "Deux fois ? Ce n’est pas un exploit, c’est un problème d’orientation.", 'droite')
  -- Aria cherche Sonata du regard pour partager sa pique, puis Sonata rit
  -- au sol (glowing sans SFX) avant de répondre au duo.
  cinematique.Respirer(10)
  GROUND:CharTurnToCharAnimated(Aria, sonata, 4)
  cinematique.Respirer(10)
  cinematique.Emote(sonata, 'glowing')
  cinematique.Respirer(20)
  hero_regarde_locuteur(hero, sonata)
  say(sonata, 'Joyous', "Moi, je trouve ça mignon : ils font presque équipe d’explorateurs.", 'droite')
  cinematique.Respirer(10)
  GROUND:CharTurnToCharAnimated(Aria, partner, 4)
  cinematique.Respirer(10)
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Joyous', "« Presque ». C’est le mot parfait.", 'droite')
  cinematique.Respirer(10)
  cinematique.Emote(partner, 'angry', 'EVT_Emote_Complain')
  cinematique.Respirer(20)
  hero_regarde_locuteur(hero, partner)
  say(partner, 'Angry', "Répète un peu pour voir ?!", 'standard')
  -- Adagio se détourne à 45° : le mépris se lit au sol, pas seulement dans
  -- le portrait, avant qu’elle ne relève finalement la provocation.
  cinematique.Respirer(10)
  GROUND:CharAnimateTurnTo(adagio, Direction.DownRight, 4)
  cinematique.Respirer(10)
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Normal', "Inutile. Les étoiles ne répètent pas pour les figurants.", 'droite')
  cinematique.Respirer(10)
  -- Au lieu de partir, Adagio relève la provocation du partenaire. Le trio
  -- reprend brièvement sa Pose face caméra, puis le vrai combat démarre.
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  cinematique.Respirer(20)
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Determined', "Bon, les microbes…\nmontrez-moi ce que vous avez dans le ventre.", 'droite')
  lancer_combat_dazzling()
end

-- Issue canonique après la défaite : le trio reste en formation, de front
-- comme au face-à-face, fonce vers le sud en bousculant le duo — le héros
-- projeté à l’ouest du chemin, le partenaire à l’est — l’humilie, puis
-- repart vite vers Réverie Town ; Sonata part encore en dernière.
function cliffdaytest.SortieDazzlingApresDefaite(hero, partner, adagio, sonata, Aria)
  local sud = MRKR('Dazzling_Entry_South')

  -- Le trio descend de front, sans se mettre en file indienne, jusqu’au
  -- contact avec le duo qui lui barre encore le chemin.
  local avance_Aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 688, 716, false, 1)
  end)
  local avance_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 712, 716, false, 1)
  end)
  local avance_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 736, 716, false, 1)
  end)
  TASK:JoinCoroutines({avance_Aria, avance_adagio, avance_sonata})

  SOUND:PlayBattleSE('DUN_Hit_Neutral')
  -- La bousculade : le héros est projeté à l’ouest du chemin (exclaim), le
  -- partenaire à l’est (shock), pendant que le trio traverse en formation
  -- l’espace qu’ils occupaient et s’arrête juste au sud du face-à-face.
  local pousse_heros = TASK:BranchCoroutine(function()
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:AnimateToPosition(hero, 'Hurt', Direction.Up, 668, 744, 1, 4, 0)
    GROUND:CharEndAnim(hero)
  end)
  local pousse_partenaire = TASK:BranchCoroutine(function()
    GROUND:CharSetEmote(partner, 'shock', 1)
    GROUND:AnimateToPosition(partner, 'Hurt', Direction.Up, 764, 744, 1, 4, 0)
    GROUND:CharEndAnim(partner)
  end)
  local traversee_Aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 688, 728, false, 1)
  end)
  local traversee_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 712, 728, false, 1)
  end)
  local traversee_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 736, 728, false, 1)
  end)
  TASK:JoinCoroutines({pousse_heros, pousse_partenaire, traversee_Aria,
    traversee_adagio, traversee_sonata})
  cinematique.Respirer(15)

  -- Après la bousculade, Adagio humilie le duo écarté des deux côtés du
  -- chemin ; Sonata approuve chacune de ses phrases, et Aria enfonce
  -- le clou. Tous se font face pendant l’échange.
  cinematique.RegarderGroupe({
    {adagio, partner, 0, 4},
    {Aria, hero, 3, 4},
    {sonata, partner, 6, 4},
    {partner, adagio, 9, 4},
    {hero, adagio, 12, 4},
  })
  cinematique.Respirer(10)
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Happy', "Des amateurs jusqu’au bout. Même votre chute manquait de style.", 'droite')
  hero_regarde_locuteur(hero, sonata)
  say(sonata, 'Joyous', "C’est clair !", 'droite')
  hero_regarde_locuteur(hero, Aria)
  say(Aria, 'Joyous', "Bande de losers !", 'droite')
  hero_regarde_locuteur(hero, adagio)
  say(adagio, 'Normal', "Retenez cette leçon, les microbes : on ne barre pas la route à la [color=#FF9FD8]Team Dazzling[color].", 'droite')
  hero_regarde_locuteur(hero, sonata)
  say(sonata, 'Joyous', "Ouais, aanh !", 'droite')
  cinematique.Respirer(10)

  -- Départ rapide, toujours de front : Aria et Adagio filent au sud
  -- entre le héros et le partenaire écartés ; Sonata traîne encore.
  cinematique.TournerGroupe({
    {adagio, Direction.Down, 0, 4},
    {Aria, Direction.Down, 3, 4},
    {sonata, Direction.Down, 6, 4},
  })
  local sortie_Aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, sud.Position.X - 19, sud.Position.Y + 38, false, 2)
    GROUND:Hide('Aria')
  end)
  local sortie_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, sud.Position.X + 5, sud.Position.Y + 38, false, 2)
    GROUND:Hide('Adagio')
  end)
  local regard_partenaire = TASK:BranchCoroutine(function()
    GAME:WaitFrames(30)
    GROUND:CharAnimateTurnTo(partner, Direction.Down, 4)
  end)
  local regard_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(35)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
  end)
  local suivi_sortie = TASK:BranchCoroutine(function()
    GAME:MoveCamera(720, 672, 140, false)
  end)
  TASK:JoinCoroutines({sortie_Aria, sortie_adagio,
    regard_partenaire, regard_heros, suivi_sortie})

  -- Sonata, laissée toute seule, regarde vers les filles déjà parties au sud
  -- avant de détaler à son tour, en courant, en toute dernière.
  GROUND:CharAnimateTurnTo(sonata, Direction.Down, 4)
  cinematique.Emote(sonata, 'sweating')
  cinematique.Respirer(10)
  hero_regarde_locuteur(hero, sonata)
  say(sonata, 'Worried', "Mais attendez !", 'droite')
  SOUND:FadeOutBGM(60)
  GROUND:MoveToPosition(sonata, sud.Position.X + 29, sud.Position.Y + 38, false, 2.5)
  GROUND:Hide('Sonata')

  SV.Destiny.TeamDazzlingRencontree = true

  SOUND:PlayBGM('Cliff Camp.ogg', true)
  GAME:MoveCamera(680, 744, 60, false)
  hero_regarde_locuteur(hero, partner)
  say(partner, 'Angry', "Non mais je rêve ! Elles nous ont bousculés comme si le chemin leur appartenait !", 'standard')
  -- Le partenaire, projeté à l’est du chemin, revient près du héros.
  GROUND:MoveToPosition(partner, 692, 744, false, 1.5)
  cinematique.RegarderGroupe({
    {partner, hero, 0, 4},
    {hero, partner, 5, 4},
  })
  cinematique.Respirer(20)
  say(partner, 'Worried', "La [color=#FF9FD8]Team Dazzling[color]… Brillantes, peut-être. Aimables, sûrement pas.", 'droite')
end


-- Reprise au retour du segment de combat. Les cinq acteurs sont replacés sur
-- les pixels exacts du face-à-face bas : Aria (688,700), Adagio (712,700)
-- et Sonata (736,700) au nord ; héros (712,732) et partenaire (736,732)
-- au sud, comme sur la .rsmap (tuiles (28-30,29) contre (29-30,30)).
function cliffdaytest.ApresCombatTeamDazzling()
  local hero = CH('PLAYER')
  local partner = equipe_scene.Partenaire(736, 732, Direction.Up)
  local adagio = personnage_dazzling('Adagio')
  local sonata = personnage_dazzling('Sonata')
  local Aria = personnage_dazzling('Aria')
  local point = MRKR('Dazzling_Stand')
  local victoire = SV.Destiny.CombatDazzling == 'victoire'

  if hero == nil or partner == nil or adagio == nil or sonata == nil
      or Aria == nil or point == nil then
    SV.Destiny.CombatDazzling = 'termine'
    SV.Destiny.TeamDazzlingRencontree = true
    GAME:FadeIn(20)
    print('[Destiny] Reprise après combat Dazzling suspendue : acteur absent.')
    return
  end

  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  AI:DisableCharacterAI(partner)
  hero.CollisionDisabled = true
  GROUND:TeleportTo(hero, 712, 732, Direction.Up)
  GROUND:TeleportTo(partner, 736, 732, Direction.Up)
  GROUND:TeleportTo(adagio, 712, 700, Direction.Down)
  GROUND:TeleportTo(Aria, 688, 700, Direction.Down)
  GROUND:TeleportTo(sonata, 736, 700, Direction.Down)
  GAME:MoveCamera(720, 672, 1, false)
  SOUND:PlayBGM(MUSIQUE_DAZZLING_SOCIALE, true)
  GAME:FadeIn(30)
  cinematique.Respirer(20)

  if victoire then
    SV.Destiny.TeamDazzlingVictoire = true
    GROUND:CharSetEmote(sonata, 'shock', 1)
    GROUND:CharSetEmote(Aria, 'sweating', 1)
    cinematique.Respirer(20)
    hero_regarde_locuteur(hero, sonata)
    say(sonata, 'Shock', "Aïe… Non mais… on a perdu ?!", 'droite')
    hero_regarde_locuteur(hero, Aria)
    say(Aria, 'Worried', "Contre eux ? C’est ridicule…", 'droite')
    GROUND:CharSetEmote(adagio, 'shock', 1)
    cinematique.Respirer(20)
    hero_regarde_locuteur(hero, adagio)
    say(adagio, 'Normal', "Assez. La Fédération nous attend à [color=#F5D27A]Réverie Town[color],\net je refuse d’arriver décoiffée.", 'droite')
    hero_regarde_locuteur(hero, partner)
    say(partner, 'Joyous', "Alors ? On continue, les étoiles ?", 'standard')
    hero_regarde_locuteur(hero, adagio)
    say(adagio, 'Normal', "Profitez bien de votre petit miracle, les microbes.\nLa [color=#FF9FD8]Team Dazzling[color] ne perd jamais deux fois.", 'droite')
    cinematique.Respirer(20)

    -- Le duo libère le chemin de lui-même, sans être poussé.
    local pas_partenaire = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partner, 764, 736, false, 1)
    end)
    local pas_heros = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 684, 736, false, 1)
    end)
    TASK:JoinCoroutines({pas_partenaire, pas_heros})
    cinematique.RegarderGroupe({
      {partner, adagio, 0, 4},
      {hero, adagio, 5, 4},
    })

    -- Le trio regarde la direction qu’il va prendre — le sud, vers
    -- Réverie Town — puis détale en évitant le duo, déjà écarté à l’ouest.
    cinematique.TournerGroupe({
      {adagio, Direction.Down, 0, 4},
      {Aria, Direction.Down, 3, 4},
      {sonata, Direction.Down, 6, 4},
    })
    local sud = MRKR('Dazzling_Entry_South')
    local function sortie_sud(dx)
      if sud ~= nil then return sud.Position.X + dx, sud.Position.Y + 38 end
      return point.Position.X + 23 + dx, point.Position.Y + 42
    end
    -- Sortie en couloirs parallèles, comme après une défaite : chacune
    -- descend dans sa propre colonne jusqu'à y=716, puis file au sud.
    -- L'ancien tracé de victoire faisait converger Aria et Adagio vers
    -- x=736 avant de se croiser, pendant que Sonata reculait au nord dans
    -- la même colonne : les actrices se bloquaient entre elles et la
    -- cinématique pouvait rester figée après une victoire.
    partner.CollisionDisabled = true
    adagio.CollisionDisabled = true
    Aria.CollisionDisabled = true
    sonata.CollisionDisabled = true
    local depart_Aria = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(Aria, 688, 716, false, 2)
      local x, y = sortie_sud(-19)
      GROUND:MoveToPosition(Aria, x, y, false, 2)
      Aria.CollisionDisabled = false
      GROUND:Hide('Aria')
    end)
    local depart_adagio = TASK:BranchCoroutine(function()
      GAME:WaitFrames(8)
      GROUND:MoveToPosition(adagio, 712, 716, false, 2)
      local x, y = sortie_sud(5)
      GROUND:MoveToPosition(adagio, x, y, false, 2)
      adagio.CollisionDisabled = false
      GROUND:Hide('Adagio')
    end)
    -- Sonata avance d'un pas dans sa colonne puis s'arrête : laissée
    -- derrière, elle ne détalera qu'après sa réplique, en toute dernière.
    local attente_sonata = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(sonata, 736, 716, false, 1)
    end)
    local regard_partenaire = TASK:BranchCoroutine(function()
      GAME:WaitFrames(45)
      GROUND:CharAnimateTurnTo(partner, Direction.Down, 4)
    end)
    local regard_heros = TASK:BranchCoroutine(function()
      GAME:WaitFrames(50)
      GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    end)
    local suivi_sortie = TASK:BranchCoroutine(function()
      GAME:MoveCamera(720, 672, 140, false)
    end)
    TASK:JoinCoroutines({depart_Aria, depart_adagio, attente_sonata,
      regard_partenaire, regard_heros, suivi_sortie})

    -- Laissée derrière, Sonata appelle les filles vers le sud, puis détale
    -- en courant, en toute dernière.
    GROUND:CharAnimateTurnTo(sonata, Direction.Down, 4)
    cinematique.Emote(sonata, 'sweating')
    cinematique.Respirer(10)
    hero_regarde_locuteur(hero, sonata)
    say(sonata, 'Shock', "Eh ! Attendez-moi, les filles ! Aaanh !", 'droite')
    SOUND:FadeOutBGM(60)
    local x_sonata, y_sonata = sortie_sud(29)
    GROUND:MoveToPosition(sonata, x_sonata, y_sonata, false, 2.5)
    sonata.CollisionDisabled = false
    partner.CollisionDisabled = false
    GROUND:Hide('Sonata')

    SV.Destiny.TeamDazzlingRencontree = true
    SOUND:PlayBGM('Cliff Camp.ogg', true)
    GAME:MoveCamera(696, 736, 60, false)
    se_faire_face(partner, hero)
    cinematique.Respirer(20)
    say(partner, 'Joyous', "On l’a fait… On a vraiment tenu tête à la [color=#FF9FD8]Team Dazzling[color] !", 'standard')
    say(partner, 'Happy', "Brillantes, peut-être. Invincibles, sûrement pas.", 'droite')
  else
    GROUND:CharSetEmote(partner, 'sweating', 1)
    GROUND:CharSetEmote(hero, 'sweating', 1)
    cinematique.Respirer(20)
    hero_regarde_locuteur(hero, adagio)
    say(adagio, 'Happy', "Voilà. C’était bref, mais très instructif.", 'droite')
    hero_regarde_locuteur(hero, partner)
    say(partner, 'Pain', "On… on peut encore se battre !", 'standard')
    hero_regarde_locuteur(hero, sonata)
    say(sonata, 'Joyous', "Bien sûr, trésor. Dès que tes jambes auront décidé de te porter.", 'droite')
    hero_regarde_locuteur(hero, adagio)
    say(adagio, 'Normal', "Allons, les filles. [color=#F5D27A]Réverie Town[color] nous attend.", 'droite')
    hero_regarde_locuteur(hero, Aria)
    say(Aria, 'Normal', "Et dégagez le chemin.", 'droite')
    cinematique.Respirer(20)
    cliffdaytest.SortieDazzlingApresDefaite(hero, partner, adagio, sonata, Aria)
  end

  SV.Destiny.CombatDazzling = 'termine'
  cliffdaytest.ConclureArriveeDestiny(hero, partner, point)
end

-- Conclusion commune de l'arrivée Destiny, que la première rencontre se
-- termine par le combat ou par le repli de secours sans spawner Dazzling.
function cliffdaytest.ConclureArriveeDestiny(hero, partner, point)
  geste_heros(hero, 'determine', partner)
  se_faire_face(partner, hero)
  say(partner, 'Happy', "Tu as raison. On n’a pas traversé les [color=#69D98C]Bois Perdus[color] pour demander la permission d’exister.", 'droite')
  say(partner, 'Normal', "Alors viens. Je vais te présenter [color=#F5D27A]Réverie Town[color].\nNous passerons dire bonjour à tatie " .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. ", puis nous déciderons ensemble de notre prochaine étape.", 'droite')

  UI:ResetSpeaker()
  GROUND:CharEndAnim(hero)
  GROUND:CharEndAnim(partner)
  -- Le duo montre la direction, puis descend au warp sud.
  cinematique.TournerGroupe({
    { partner, Direction.Down, 0, 4 },
    { hero, Direction.Down, 5, 4 },
  })
  local sud = MRKR('Dazzling_Entry_South')
  local depart_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner,
      sud ~= nil and sud.Position.X + 5 or point.Position.X + 28,
      sud ~= nil and sud.Position.Y + 2 or point.Position.Y + 6, false, 1)
  end)
  local depart_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero,
      sud ~= nil and sud.Position.X - 19 or point.Position.X + 8,
      sud ~= nil and sud.Position.Y + 2 or point.Position.Y + 6, false, 1)
  end)
  TASK:JoinCoroutines({depart_partenaire, depart_hero})
  hero.CollisionDisabled = false
  SV.Destiny.FinaleDestiny = true
  SV.Destiny.VisiteVille = 'en_route'
  cliffdaytest.AllerEnVille()
end

-- Arrivée du retour inverse : la même falaise, mais au lever du jour.
-- Le partenaire choisi au quiz présente sa maison, son enfance auprès de
-- tatie Kangourex, Réverie Town, les équipes et les guildes. Le héros
-- continue de répondre uniquement par gestes.
function cliffdaytest.SceneArriveeDestiny()
  local hero = CH('PLAYER')
  local entree = MRKR('Dazzling_Exit_East')
  local porte = MRKR('Pichu_Home_Door')
  local point = MRKR('Dazzling_Stand')
  local partner = equipe_scene.Partenaire(entree.Position.X - 40, entree.Position.Y + 8, Direction.Left)
  if hero == nil or partner == nil then
    GAME:FadeIn(20)
    print('[Destiny] Arrivée à la falaise suspendue : équipe incomplète.')
    return
  end

  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  -- Réinitialiser les actrices si une tentative précédente de la scène a
  -- été interrompue : leurs spawners les recréeront au chemin est.
  for _, nom in ipairs({'Adagio', 'Sonata', 'Aria', 'Bekipan'}) do
    if CH(nom) ~= nil then GROUND:RemoveCharacter(nom) end
  end
  AI:DisableCharacterAI(partner)
  hero.CollisionDisabled = true
  -- Le partenaire devance le héros de quelques pas (il marche devant,
  -- à l’ouest), puis se retourne pour lui parler face à face.
  GROUND:TeleportTo(hero, entree.Position.X - 40, entree.Position.Y - 8, Direction.Left)
  GROUND:TeleportTo(partner, entree.Position.X - 64, entree.Position.Y + 8, Direction.Left)
  GAME:MoveCamera(entree.Position.X - 52, entree.Position.Y, 1, false)
  GAME:FadeIn(45)
  GAME:WaitFrames(25)
  local avance_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, entree.Position.X - 88, entree.Position.Y + 8, false, 1.5)
  end)
  local avance_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, entree.Position.X - 64, entree.Position.Y - 8, false, 1.5)
  end)
  local avance_camera = TASK:BranchCoroutine(function()
    GAME:MoveCamera(entree.Position.X - 76, entree.Position.Y, 40, false)
  end)
  TASK:JoinCoroutines({ avance_partenaire, avance_heros, avance_camera })
  se_faire_face(partner, hero)
  cinematique.Respirer(10)
  say(partner, 'Joyous', "Ohh, " .. nom_heros() .. " ! On est arrivés !", 'droite')

  -- Tout content, le partenaire revient vers le héros.
  GROUND:MoveToPosition(partner, entree.Position.X - 76, entree.Position.Y + 8, false, 1.5)
  se_faire_face(partner, hero)
  say(partner, 'Joyous', "Au fait, tu ne te débrouilles pas trop mal !", 'droite')
  say(partner, 'Happy', "On est ressortis… et regarde : le jour s’est levé\npendant que nous retraversions les [color=#69D98C]Bois Perdus[color].", 'droite')
  geste_heros(hero, 'autour', partner)
  se_faire_face(partner, hero)
  say(partner, 'Happy', "C’est la même falaise que cette nuit !\nOn a juste fait demi-tour dans l’autre sens, et nous voilà chez moi.", 'droite')

  -- Direction la maison : les deux regardent d’abord vers l’ouest.
  cinematique.TournerGroupe({
    { partner, Direction.Left, 0, 4 },
    { hero, Direction.Left, 5, 4 },
  })
  local marche_partenaire_maison = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, 620, 468, false, 1.5)
  end)
  local marche_heros_maison = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, 648, 468, false, 1.5)
  end)
  local camera_maison = TASK:BranchCoroutine(function()
    GAME:MoveCamera(620, 462, 200, false)
  end)
  TASK:JoinCoroutines({ marche_partenaire_maison, marche_heros_maison, camera_maison })

  local orphelin = 'orphelin'
  local ok_feminin, feminin = pcall(function()
    return partner.BaseForm.Gender == Gender.Female
  end)
  if ok_feminin and feminin then orphelin = 'orpheline' end

  -- Le partenaire montre sa maison : les deux regardent la cabane.
  cinematique.TournerGroupe({
    { partner, Direction.UpLeft, 0, 4 },
    { hero, Direction.UpLeft, 5, 4 },
  })
  cinematique.Respirer(10)
  say(partner, 'Happy', "C’est ici que j’habite, d’ailleurs.", 'droite')
  se_faire_face(partner, hero)
  say(partner, 'Happy', "On pourra y vivre le temps de rejoindre une guilde.\nCe n’est pas la grande ville, mais ça fait l’affaire, haha !", 'droite')
  say(partner, 'Normal', "Ce n’est pas très grand, mais c’est mon point d’ancrage :\nun toit, un lit, quelques provisions, et la mer juste derrière.", 'droite')
  say(partner, 'Worried', "Je ne t’ai pas encore parlé de moi. Je n’ai pas connu mes parents ; je suis " .. orphelin .. ".", 'droite')
  geste_heros(hero, 'inquiet', partner)
  se_faire_face(partner, hero)
  say(partner, 'Normal', "C’est tatie " .. cinematique.NomEspece('kangaskhan', 'Kangourex') .. " qui m’a recueilli quand j’étais tout petit.\nTout le monde l’appelle comme ça, même ceux qui ne sont pas de sa famille.", 'droite')
  say(partner, 'Happy', "Elle s’occupe de moi depuis toujours :\nun repas chaud, un conseil avant de partir, un endroit où déposer ce qui compte. Sans elle, cette maison serait bien vide.", 'droite')

  -- Le facteur Bekipan arrive en vol, de profil, depuis l’est. Il se pose
  -- sur la boîte aux lettres (juste à droite de la porte), glisse son bec
  -- dans la fente pour y déposer le courrier, échange quelques mots avec
  -- le partenaire, puis repart en s’envolant dans l’autre sens, vers la mer.
  local bekipan = facteur_bekipan()
  if bekipan ~= nil then
    -- Comme dans PMD Red, Bekipan traverse d’abord le ciel en hauteur :
    -- le 5e argument de TeleportTo est son LocHeight (48 px au-dessus du
    -- sol). MoveToPosition conserve cette hauteur sur le premier trajet,
    -- puis AnimateToPosition le fait descendre progressivement jusqu’à 0
    -- pendant que ses ailes battent en animation Walk.
    GROUND:TeleportTo(bekipan, 790, 372, Direction.Left, 48)
    cinematique.Emote(partner, 'exclaim', 'EVT_Emote_Exclaim_2')
    cinematique.TournerGroupe({
      { partner, Direction.UpRight, 0, 4 },
      { hero, Direction.UpRight, 5, 4 },
    })
    cinematique.Respirer(10)
    say(partner, 'Surprised', "Oh ! C’est " .. cinematique.NomEspece('pelipper', 'Bekipan') .. ", le facteur !", 'droite')
    GROUND:MoveToPosition(bekipan, 712, 408, false, 2)
    GROUND:AnimateToPosition(bekipan, 'Walk', Direction.DownLeft, 659, 444, 1, 2, 0)
    -- Petit saut d’atterrissage sur le couvercle, ailes battantes.
    anim(bekipan, 'Hop', false)
    cinematique.Respirer(24)
    GROUND:CharEndAnim(bekipan)
    cinematique.RegarderGroupe({
      { partner, bekipan, 0, 4 },
      { hero, bekipan, 5, 4 },
    })
    -- Perché sur la boîte et tourné de face, comme sur la référence PMD
    -- Red fournie : l’animation Walk Down native de Pelipper enchaîne
    -- ailes basses, ailes ouvertes puis ailes relevées pendant qu’il
    -- baisse le bec vers la fente. Un cycle complet dure 44 ticks.
    -- Le petit Attack final pousse la lettre au fond de la boîte.
    GROUND:CharAnimateTurnTo(bekipan, Direction.Down, 4)
    anim(bekipan, 'Walk', true)
    cinematique.Respirer(44)
    anim(bekipan, 'Attack', false)
    cinematique.Respirer(28)
    GROUND:CharEndAnim(bekipan)
    -- Le courrier tombe dans la boîte métallique : le « Clunk » de PMD Red,
    -- en narration sans portrait, avec le bruit sourd déjà utilisé en jeu.
    SOUND:PlayBattleSE('DUN_Hit_Neutral')
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Clunk')
    cinematique.Respirer(10)

    -- Bekipan remarque le héros aux côtés du partenaire.
    GROUND:CharAnimateTurnTo(bekipan, Direction.DownLeft, 4)
    hero_regarde_locuteur(hero, bekipan)
    say(bekipan, 'Happy', "Oh tiens, " .. nom_partenaire() .. " !\nTu t’es fait un nouvel ami, à ce que je vois !", 'droite')
    hero_regarde_locuteur(hero, partner)
    say(partner, 'Joyous', cinematique.NomEspece('pelipper', 'Bekipan') .. " ! Oui ! Je te présente " .. nom_heros() .. " !\nOn vient de retraverser les [color=#69D98C]Bois Perdus[color] ensemble !", 'droite')
    se_faire_face(partner, hero)
    say(partner, 'Happy', cinematique.NomEspece('pelipper', 'Bekipan') .. " distribue le courrier partout dans le monde :\nsa société, la poste Bekipan, porte les lettres des équipes par-delà les mers !", 'droite')
    cinematique.RegarderGroupe({
      { partner, bekipan, 0, 4 },
      { hero, bekipan, 5, 4 },
    })
    hero_regarde_locuteur(hero, bekipan)
    say(bekipan, 'Joyous', "Hé hé ! Enchanté, " .. nom_heros() .. " !\nAllez, je file : d’autres lettres m’attendent. Au revoir, et bonne chance pour la suite !", 'droite')
    cinematique.Respirer(10)
    -- Départ dessiné par l’utilisateur (ligne verte) : Bekipan prend
    -- d’abord de l’altitude presque à la verticale au-dessus de la
    -- boîte, dans l’axe x=659 juste à l’est de la maison, puis
    -- traverse le ciel vers l’ouest au-dessus de la mer. Il ne part
    -- plus en diagonale au sol et ne traverse ni le toit ni les
    -- décors hauts.
    GROUND:CharAnimateTurnTo(bekipan, Direction.Up, 4)
    anim(bekipan, 'Hop', false)
    cinematique.Respirer(24)
    GROUND:CharEndAnim(bekipan)
    -- Montée raide initiale : 20 px au sol, mais déjà 48 px d’altitude.
    GROUND:AnimateToPosition(bekipan, 'Walk', Direction.Up, 659, 424, 1, 1, 48)
    -- Suite de la montée verticale jusqu’à 72 px, au-dessus de la côte.
    GROUND:AnimateToPosition(bekipan, 'Walk', Direction.Up, 659, 340, 1, 2, 72)
    -- Vol horizontal vers l’ouest, à altitude constante au-dessus de
    -- la mer (MoveToPosition conserve le LocHeight).
    GROUND:CharAnimateTurnTo(bekipan, Direction.Left, 4)
    GROUND:MoveToPosition(bekipan, 420, 340, false, 2)
    GROUND:Hide('Bekipan')
    cinematique.Respirer(10)

    -- Le partenaire va chercher la lettre dans la boîte, puis revient la
    -- lire face au héros : la Grande Guilde ouvre ses portes.
    GROUND:MoveToPosition(partner, 642, 476, false, 1.5)
    GROUND:CharAnimateTurnTo(partner, Direction.UpRight, 4)
    GROUND:CharTurnToCharAnimated(hero, partner, 4)
    cinematique.Respirer(15)
    GROUND:MoveToPosition(partner, 620, 468, false, 1.5)
    se_faire_face(partner, hero)
    say(partner, 'Normal', "Voyons voir ce qu’il m’a apporté…", 'droite')
    say(partner, 'Normal', "« La [color=#F5D27A]Grande Guilde des Explorateurs[color] de [color=#F5D27A]Réverie Town[color]\nouvre ses portes ! »", 'droite')
    say(partner, 'Normal', "« Équipes de secours et d’exploration, présentez-vous à la guilde :\nles inscriptions sont ouvertes ! »", 'droite')
    say(partner, 'Joyous', "Tu te rends compte, " .. nom_heros() .. " ?\nLa grande guilde accueille de nouvelles équipes !", 'droite')
  end

  -- Le héros reste en Idle, perplexe devant la lettre : le partenaire
  -- réalise alors qu’il ne sait ni ce qu’est une guilde, ni ce qu’est
  -- une équipe.
  geste_heros(hero, 'idle', partner)
  geste_heros(hero, 'question', partner)
  cinematique.Emote(partner, 'exclaim', 'EVT_Emote_Exclaim_2')
  cinematique.Respirer(10)
  se_faire_face(partner, hero)
  say(partner, 'Worried', "Attends… tu te demandes ce que c’est, une guilde ?\nEt une équipe d’exploration ?!", 'droite')
  cinematique.Emote(partner, 'sweating')
  cinematique.Respirer(10)
  se_faire_face(partner, hero)
  say(partner, 'Happy', "Ah oui, c’est vrai… tu dis être un humain.\nHaha, quel étourdi je fais ! Bon, ouais, je t’explique.", 'droite')

  -- Explications face à face, devant la maison.
  say(partner, 'Normal', "Une équipe de secours répond aux appels des Pokémon perdus, blessés ou piégés dans un donjon.\nElle part les chercher et les ramène auprès des leurs.", 'droite')
  say(partner, 'Normal', "Les explorateurs, eux, ouvrent les routes :\nils cartographient des lieux inconnus, signalent les passages dangereux et reviennent parfois avec des trésors ou des récits précieux.", 'droite')
  say(partner, 'Happy', "Beaucoup d’équipes font les deux.\nSecourir quelqu’un et découvrir le chemin qui mène jusqu’à lui, au fond, c’est le même métier du cœur.", 'droite')
  geste_heros(hero, 'question', partner)
  se_faire_face(partner, hero)
  say(partner, 'Normal', "Les guildes ? Ce sont les maisons communes de ces équipes.\nOn y reçoit des demandes, on s’y entraîne, on y apprend les règles des donjons et on y partage les cartes.", 'droite')
  say(partner, 'Normal', "Il y en a dans plusieurs régions du monde.\nChacune a ses maîtres, ses traditions et ses explorateurs célèbres ; aucune ne détient toutes les routes.", 'droite')
  say(partner, 'Happy', "Moi, je rêve qu’un jour notre équipe soit reconnue par une guilde.\nPas pour briller sur une affiche… pour être prête quand un appel viendra de loin.", 'droite')
  say(partner, 'Joyous', "Et avec cette lettre… ce rêve n’a jamais été aussi proche !\nNotre équipe pourrait être de celles-là, tu sais.", 'droite')

  -- En parlant de Réverie Town, le partenaire montre le sud : les deux
  -- regardent dans la direction des cascades.
  cinematique.TournerGroupe({
    { partner, Direction.Down, 0, 4 },
    { hero, Direction.Down, 5, 4 },
  })
  cinematique.Respirer(10)
  say(partner, 'Happy', "D’ailleurs, en parlant de [color=#F5D27A]Réverie Town[color]… suis-moi !\nVers le sud, en longeant les cascades, je t’y emmènerai.", 'droite')
  say(partner, 'Joyous', "C’est un lieu super chouette : des boutiques, des ponts, des Pokémon célèbres et des voyageurs itinérants.\nUn peu la capitale mondiale des explorateurs, quoi !", 'droite')

  -- Le partenaire prend plusieurs pas d’avance et descend jusqu’au warp
  -- sud ; le héros s’arrête un instant en (712, 732) pour réfléchir.
  local sud = MRKR('Dazzling_Entry_South')
  local sud_x = sud ~= nil and sud.Position.X or 731
  local sud_y = sud ~= nil and sud.Position.Y or 762
  local descente_sud = {
    { 660, 480 }, { 677, 489 }, { 665, 510 }, { 666, 544 },
    { 681, 572 }, { 695, 593 }, { 713, 634 }, { 713, 676 },
  }
  local function marcher_descente_sud(marcheur)
    for _, etape in ipairs(descente_sud) do
      GROUND:MoveToPosition(marcheur, etape[1], etape[2], false, 1.5)
    end
  end
  local descente_partenaire = TASK:BranchCoroutine(function()
    marcher_descente_sud(partner)
    GROUND:MoveToPosition(partner, 734, 737, false, 1.5)
    GROUND:MoveToPosition(partner, sud_x, sud_y, false, 1.5)
  end)
  local descente_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(45)
    marcher_descente_sud(hero)
    GROUND:MoveToPosition(hero, 712, 732, false, 1.5)
  end)
  local descente_camera = TASK:BranchCoroutine(function()
    GAME:MoveCamera(720, 672, 300, false)
  end)
  TASK:JoinCoroutines({ descente_partenaire, descente_heros, descente_camera })

  se_faire_face(partner, hero)
  anim(hero, 'Idle', true)
  cinematique.Respirer(20)
  pense_heros(hero, 'Worried', "Je me demande dans quoi je me suis embarqué…")
  GROUND:CharEndAnim(hero)

  -- Le héros rejoint le partenaire au sud, face à face, puis les deux se
  -- tournent vers la sortie.
  GROUND:MoveToPosition(hero, sud_x - 24, sud_y, false, 1)
  se_faire_face(partner, hero)
  say(partner, 'Joyous', "Bon, on y va !", 'droite')
  cinematique.TournerGroupe({
    { partner, Direction.Down, 0, 4 },
    { hero, Direction.Down, 5, 4 },
  })
  cinematique.Respirer(10)

  cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  -- Chemin normal : RencontreTeamDazzling entre en donjon et ne revient
  -- pas ici ; ApresCombatTeamDazzling appellera cette conclusion. Le
  -- présent appel ne sert que si les spawners Dazzling sont absents.
  if SV.Destiny.CombatDazzling ~= 'en_cours' then
    cliffdaytest.ConclureArriveeDestiny(hero, partner, point)
  end
end

return cliffdaytest
