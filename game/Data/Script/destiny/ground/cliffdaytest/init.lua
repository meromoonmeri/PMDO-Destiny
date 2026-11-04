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
  -- PoseGroundAction joue la vraie Pose SpriteCollab (index 13) puis la
  -- maintient sur sa frame de retour pendant la réplique, au lieu de la
  -- laisser retomber en Idle après 14 à 16 ticks.
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
local function geste_heros(hero, geste)
  if hero == nil then return end
  cinematique.Respirer(20)
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(30)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(22)
  elseif geste == 'oui' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(10)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(16)
  elseif geste == 'inquiet' then
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(36)
  elseif geste == 'determine' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(24)
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
-- Le trio arrive par la route de l’est et se dirige vers Réverie Town,
-- où la Fédération des explorateurs l’attend. Trajectoires figées :
--   * révélation à l’est : Adagio (852,468), Aria (880,452),
--     Sonata (884,484), en colonne vers l’ouest ;
--   * descente au carrefour puis éventail au nord du duo :
--     Aria (660,528), Adagio (684,528), Sonata (708,528), face au sud ;
--   * héros (684,560) et partenaire (708,560) barrent le chemin sud,
--     face au nord, puis sont poussés à l’ouest en (656,564)/(680,564) ;
--   * sortie en colonne par x=708 puis le chemin sud vers Réverie Town.
-- Leur thème social (Encounter! Jacinthe) ne couvre pas la voix hors champ :
-- il démarre sur la révélation caméra, lorsque les trois prennent la pose.
function cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  local est = MRKR('Dazzling_Exit_East')
  local adagio = personnage_dazzling('Adagio')
  local sonata = personnage_dazzling('Sonata')
  local Aria = personnage_dazzling('Aria')
  if est == nil or adagio == nil or sonata == nil or Aria == nil then
    print('[Destiny] Rencontre Team Dazzling suspendue : spawner incomplet.')
    return
  end

  GROUND:TeleportTo(adagio, est.Position.X - 108, est.Position.Y + 8, Direction.Left)
  GROUND:TeleportTo(Aria, est.Position.X - 80, est.Position.Y - 8, Direction.Left)
  GROUND:TeleportTo(sonata, est.Position.X - 76, est.Position.Y + 24, Direction.Left)

  -- Voix hors champ, sans portrait : le duo entend Adagio avant de la voir.
  cinematique.Respirer(20)
  UI:SetSpeaker('???', true, '', -1, '', RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue("Mais regardez qui voilà… deux petits morveux.\n(Décidément, ils n’ont aucun style.)")

  local reaction_partenaire = TASK:BranchCoroutine(function()
    SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
    GROUND:CharSetEmote(partner, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(partner, Direction.Right, 4)
  end)
  local reaction_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
  end)
  TASK:JoinCoroutines({reaction_partenaire, reaction_heros})
  say(partner, 'Worried', "Qui va là ?!", 'standard')
  cinematique.Respirer(20)

  -- Le duo descend se placer dans le chemin sud, face à la route de l’est.
  local approche_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, 708, 540, false, 1)
    GROUND:MoveToPosition(partner, 708, 560, false, 1)
  end)
  local approche_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(6)
    GROUND:MoveToPosition(hero, 684, 540, false, 1)
    GROUND:MoveToPosition(hero, 684, 560, false, 1)
  end)
  TASK:JoinCoroutines({approche_partenaire, approche_heros})
  cinematique.TournerGroupe({
    {partner, Direction.Up, 0, 4},
    {hero, Direction.Up, 5, 4},
  })

  SOUND:FadeOutBGM(45)
  GAME:MoveCamera(800, 468, 80, false)
  cinematique.Respirer(20)
  SOUND:PlayBGM(MUSIQUE_DAZZLING_SOCIALE, true)
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  GAME:WaitFrames(28)
  finir_pose_trio(adagio, Aria, sonata)
  tourner_trio(adagio, Aria, sonata, Direction.Left)

  -- Adagio mène la traversée vers l’ouest ; Aria garde le couloir nord et
  -- Sonata le couloir sud avant l’ouverture en éventail face au duo.
  local entree_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 700, 468, false, 1)
    GROUND:MoveToPosition(adagio, 684, 528, false, 1)
  end)
  local entree_aria = TASK:BranchCoroutine(function()
    GAME:WaitFrames(4)
    GROUND:MoveToPosition(Aria, 660, 452, false, 1)
    GROUND:MoveToPosition(Aria, 660, 528, false, 1)
  end)
  local entree_sonata = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(sonata, 716, 484, false, 1)
    GROUND:MoveToPosition(sonata, 708, 528, false, 1)
  end)
  local suivi_entree = TASK:BranchCoroutine(function()
    GAME:MoveCamera(692, 544, 210, false)
  end)
  TASK:JoinCoroutines({entree_adagio, entree_aria, entree_sonata, suivi_entree})
  cinematique.RegarderGroupe({
    {adagio, partner, 0, 4},
    {Aria, partner, 3, 4},
    {sonata, hero, 6, 4},
  })
  cinematique.Respirer(20)

  say(adagio, 'Happy', "Hello~ [color=#F5D27A]Réverie Town[color] n’est pas un lieu pour des amateurs, voyons.", 'droite')
  say(partner, 'Angry', "Mais pour qui vous vous prenez ?!", 'standard')
  cinematique.Respirer(10)
  geste_heros(hero, 'question')

  -- Présentation face caméra, comme une entrée en scène : la vraie Pose
  -- reste tenue pendant les noms, petites étoiles autour des trois.
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  cinematique.Respirer(20)
  say(adagio, 'Happy', "Adagio, cheffe de la [color=#FF9FD8]Team Dazzling[color].", 'droite')
  say(Aria, 'Happy', "Aria. Retenez le nom : vous l’entendrez souvent.", 'droite')
  say(sonata, 'Joyous', "Et moi, Sonata ! La plus éblouissante des trois !", 'droite')
  say(Aria, 'Normal', "La plus bruyante, surtout.", 'droite')
  cinematique.Respirer(20)
  finir_pose_trio(adagio, Aria, sonata)
  cinematique.RegarderGroupe({
    {adagio, partner, 0, 4},
    {Aria, partner, 3, 4},
    {sonata, hero, 6, 4},
  })
  cinematique.Respirer(10)

  say(adagio, 'Happy', "Une équipe célèbre ne perd pas son temps avec deux enfants couverts de poussière.", 'droite')
  say(partner, 'Determined', "On a traversé les [color=#69D98C]Bois Perdus[color]. Deux fois.", 'standard')
  say(Aria, 'Happy', "Deux fois ? Ce n’est pas un exploit, c’est un problème d’orientation.", 'droite')
  -- Aria cherche Sonata du regard pour partager sa pique, puis Sonata rit
  -- au sol (glowing sans SFX) avant de répondre au duo.
  cinematique.Respirer(10)
  GROUND:CharTurnToCharAnimated(Aria, sonata, 4)
  cinematique.Respirer(10)
  cinematique.Emote(sonata, 'glowing')
  cinematique.Respirer(20)
  say(sonata, 'Joyous', "Moi, je trouve ça mignon : ils font presque équipe d’explorateurs.", 'droite')
  cinematique.Respirer(10)
  GROUND:CharTurnToCharAnimated(Aria, partner, 4)
  cinematique.Respirer(10)
  say(adagio, 'Joyous', "« Presque ». C’est le mot parfait.", 'droite')
  cinematique.Respirer(10)
  cinematique.Emote(partner, 'angry', 'EVT_Emote_Complain')
  cinematique.Respirer(20)
  say(partner, 'Angry', "Répète un peu pour voir ?!", 'standard')
  -- Adagio se détourne à 45° : le mépris se lit au sol, pas seulement dans
  -- le portrait, avant qu’elle ne relève finalement la provocation.
  cinematique.Respirer(10)
  GROUND:CharAnimateTurnTo(adagio, Direction.DownRight, 4)
  cinematique.Respirer(10)
  say(adagio, 'Normal', "Inutile. Les étoiles ne répètent pas pour les figurants.", 'droite')
  cinematique.Respirer(10)
  -- Au lieu de partir, Adagio relève la provocation du partenaire. Le trio
  -- reprend brièvement sa Pose face caméra, puis le vrai combat démarre.
  tourner_trio(adagio, Aria, sonata, Direction.Down)
  poser_trio(adagio, Aria, sonata)
  cinematique.Respirer(20)
  say(adagio, 'Determined', "Bon, les microbes…\nmontrez-moi ce que vous avez dans le ventre.", 'droite')
  lancer_combat_dazzling()
end

-- Issue canonique après la défaite : les Dazzling reprennent leur colonne,
-- poussent physiquement le duo hors du chemin sud et descendent vers
-- Réverie Town.
function cliffdaytest.SortieDazzlingApresDefaite(hero, partner, adagio, sonata, Aria)
  local sud = MRKR('Dazzling_Entry_South')

  -- Aria et Sonata se replacent derrière Adagio, au nord, par leurs
  -- couloirs respectifs ; Adagio gagne le couloir sud en x=708.
  local colonne_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 708, 528, false, 1)
  end)
  local colonne_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 708, 504, false, 1)
  end)
  local colonne_aria = TASK:BranchCoroutine(function()
    GAME:WaitFrames(2)
    GROUND:MoveToPosition(Aria, 660, 480, false, 1)
    GROUND:MoveToPosition(Aria, 708, 480, false, 1)
  end)
  TASK:JoinCoroutines({colonne_adagio, colonne_sonata, colonne_aria})

  local contact_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 708, 544, false, 1)
  end)
  local contact_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 708, 520, false, 1)
  end)
  local contact_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 708, 496, false, 1)
  end)
  TASK:JoinCoroutines({contact_adagio, contact_sonata, contact_aria})

  SOUND:PlayBattleSE('DUN_Hit_Neutral')
  -- Réaction physique simultanée : le partenaire encaisse directement le
  -- passage d’Adagio (shock), le héros est entraîné dans le même mouvement
  -- avec exclaim. Partir ensemble évite aussi que le partenaire, poussé
  -- vers l’ouest, traverse l’espace encore occupé par le héros.
  local pousse_partenaire = TASK:BranchCoroutine(function()
    GROUND:CharSetEmote(partner, 'shock', 1)
    GROUND:AnimateToPosition(partner, 'Hurt', Direction.Up, 680, 564, 1, 4, 0)
    GROUND:CharEndAnim(partner)
  end)
  local pousse_heros = TASK:BranchCoroutine(function()
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:AnimateToPosition(hero, 'Hurt', Direction.Up, 656, 564, 1, 4, 0)
    GROUND:CharEndAnim(hero)
  end)
  local sortie_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 716, 650, false, 1.25)
    GROUND:MoveToPosition(adagio, sud.Position.X, sud.Position.Y + 22, false, 1.25)
  end)
  local sortie_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 716, 626, false, 1.25)
    GROUND:MoveToPosition(sonata, sud.Position.X, sud.Position.Y - 2, false, 1.25)
  end)
  local sortie_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 716, 602, false, 1.25)
    GROUND:MoveToPosition(Aria, sud.Position.X, sud.Position.Y - 26, false, 1.25)
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
    GAME:MoveCamera(716, 672, 140, false)
    GAME:WaitFrames(55)
    SOUND:FadeOutBGM(60)
  end)
  TASK:JoinCoroutines({pousse_heros, pousse_partenaire, sortie_adagio,
    sortie_sonata, sortie_aria, regard_partenaire, regard_heros, suivi_sortie})

  GROUND:Hide('Adagio')
  GROUND:Hide('Sonata')
  GROUND:Hide('Aria')
  SV.Destiny.TeamDazzlingRencontree = true

  SOUND:PlayBGM('Cliff Camp.ogg', true)
  GAME:MoveCamera(668, 560, 60, false)
  say(partner, 'Angry', "Non mais je rêve ! Elles nous ont bousculés comme si le chemin leur appartenait !", 'standard')
  cinematique.RegarderGroupe({
    {partner, hero, 0, 4},
    {hero, partner, 5, 4},
  })
  cinematique.Respirer(20)
  say(partner, 'Worried', "La [color=#FF9FD8]Team Dazzling[color]… Brillantes, peut-être. Aimables, sûrement pas.", 'droite')
end


-- Reprise au retour du segment de combat. Les cinq acteurs sont replacés sur
-- les tuiles exactes du face-à-face : Aria (660,528), Adagio (684,528) et
-- Sonata (708,528) au nord ; héros (684,560) et partenaire (708,560) au sud.
function cliffdaytest.ApresCombatTeamDazzling()
  local hero = CH('PLAYER')
  local partner = equipe_scene.Partenaire(708, 560, Direction.Up)
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
  GROUND:TeleportTo(hero, 684, 560, Direction.Up)
  GROUND:TeleportTo(partner, 708, 560, Direction.Up)
  GROUND:TeleportTo(adagio, 684, 528, Direction.Down)
  GROUND:TeleportTo(Aria, 660, 528, Direction.Down)
  GROUND:TeleportTo(sonata, 708, 528, Direction.Down)
  GAME:MoveCamera(692, 544, 1, false)
  SOUND:PlayBGM(MUSIQUE_DAZZLING_SOCIALE, true)
  GAME:FadeIn(30)
  cinematique.Respirer(20)

  if victoire then
    SV.Destiny.TeamDazzlingVictoire = true
    GROUND:CharSetEmote(sonata, 'shock', 1)
    GROUND:CharSetEmote(Aria, 'sweating', 1)
    cinematique.Respirer(20)
    say(sonata, 'Shock', "Aïe… Non mais… on a perdu ?!", 'droite')
    say(Aria, 'Worried', "Contre eux ? C’est ridicule…", 'droite')
    GROUND:CharSetEmote(adagio, 'shock', 1)
    cinematique.Respirer(20)
    say(adagio, 'Normal', "Assez. La Fédération nous attend à [color=#F5D27A]Réverie Town[color],\net je refuse d’arriver décoiffée.", 'droite')
    say(partner, 'Joyous', "Alors ? On continue, les étoiles ?", 'standard')
    say(adagio, 'Normal', "Profitez bien de votre petit miracle, les microbes.\nLa [color=#FF9FD8]Team Dazzling[color] ne perd jamais deux fois.", 'droite')
    cinematique.Respirer(20)

    -- Le duo libère le chemin de lui-même, sans être poussé.
    local pas_partenaire = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(partner, 680, 564, false, 1)
    end)
    local pas_heros = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(hero, 656, 564, false, 1)
    end)
    TASK:JoinCoroutines({pas_partenaire, pas_heros})
    cinematique.RegarderGroupe({
      {partner, adagio, 0, 4},
      {hero, adagio, 5, 4},
    })

    local sud = MRKR('Dazzling_Entry_South')
    local colonne_sonata = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(sonata, 708, 504, false, 1)
      GROUND:MoveToPosition(sonata, 716, 626, false, 1.25)
      GROUND:MoveToPosition(sonata, sud.Position.X, sud.Position.Y - 2, false, 1.25)
    end)
    local colonne_aria = TASK:BranchCoroutine(function()
      GAME:WaitFrames(2)
      GROUND:MoveToPosition(Aria, 660, 480, false, 1)
      GROUND:MoveToPosition(Aria, 708, 480, false, 1)
      GROUND:MoveToPosition(Aria, 716, 602, false, 1.25)
      GROUND:MoveToPosition(Aria, sud.Position.X, sud.Position.Y - 26, false, 1.25)
    end)
    local depart_adagio = TASK:BranchCoroutine(function()
      GROUND:MoveToPosition(adagio, 708, 528, false, 1)
      GROUND:MoveToPosition(adagio, 716, 650, false, 1.25)
      GROUND:MoveToPosition(adagio, sud.Position.X, sud.Position.Y + 22, false, 1.25)
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
      GAME:MoveCamera(716, 672, 140, false)
      GAME:WaitFrames(55)
      SOUND:FadeOutBGM(60)
    end)
    TASK:JoinCoroutines({depart_adagio, colonne_sonata, colonne_aria,
      regard_partenaire, regard_heros, suivi_sortie})

    GROUND:Hide('Adagio')
    GROUND:Hide('Sonata')
    GROUND:Hide('Aria')
    SV.Destiny.TeamDazzlingRencontree = true
    SOUND:PlayBGM('Cliff Camp.ogg', true)
    GAME:MoveCamera(668, 560, 60, false)
    say(partner, 'Joyous', "On l’a fait… On a vraiment tenu tête à la [color=#FF9FD8]Team Dazzling[color] !", 'standard')
    cinematique.RegarderGroupe({
      {partner, hero, 0, 4},
      {hero, partner, 5, 4},
    })
    cinematique.Respirer(20)
    say(partner, 'Happy', "Brillantes, peut-être. Invincibles, sûrement pas.", 'droite')
  else
    GROUND:CharSetEmote(partner, 'sweating', 1)
    GROUND:CharSetEmote(hero, 'sweating', 1)
    cinematique.Respirer(20)
    say(adagio, 'Happy', "Voilà. C’était bref, mais très instructif.", 'droite')
    say(partner, 'Pain', "On… on peut encore se battre !", 'standard')
    say(sonata, 'Joyous', "Bien sûr, trésor. Dès que tes jambes auront décidé de te porter.", 'droite')
    say(adagio, 'Normal', "Allons, les filles. [color=#F5D27A]Réverie Town[color] nous attend.", 'droite')
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
  geste_heros(hero, 'determine')
  say(partner, 'Happy', "Tu as raison. On n’a pas traversé les [color=#69D98C]Bois Perdus[color] pour demander la permission d’exister.", 'droite')
  say(partner, 'Normal', "Alors viens. Je vais te présenter [color=#F5D27A]Réverie Town[color].\nNous passerons dire bonjour à tatie Kangourex, puis nous déciderons ensemble de notre prochaine étape.", 'droite')

  UI:ResetSpeaker()
  GROUND:CharEndAnim(hero)
  GROUND:CharEndAnim(partner)
  local depart_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, point.Position.X + 28, point.Position.Y + 6, false, 1)
  end)
  local depart_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, point.Position.X + 8, point.Position.Y + 6, false, 1)
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
  for _, nom in ipairs({'Adagio', 'Sonata', 'Aria'}) do
    if CH(nom) ~= nil then GROUND:RemoveCharacter(nom) end
  end
  AI:DisableCharacterAI(partner)
  hero.CollisionDisabled = true
  GROUND:TeleportTo(hero, entree.Position.X - 40, entree.Position.Y - 8, Direction.Left)
  GROUND:TeleportTo(partner, entree.Position.X - 40, entree.Position.Y + 8, Direction.Left)
  GAME:MoveCamera(entree.Position.X - 40, entree.Position.Y, 1, false)
  GAME:FadeIn(45)
  GAME:WaitFrames(25)

  local marche_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, point.Position.X, point.Position.Y, false, 1.5)
  end)
  local marche_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, point.Position.X - 20, point.Position.Y, false, 1.5)
  end)
  local suivi = TASK:BranchCoroutine(function()
    GAME:MoveCamera(point.Position.X, point.Position.Y, 170, false)
  end)
  TASK:JoinCoroutines({marche_partenaire, marche_hero, suivi})
  cinematique.TournerGroupe({
    {partner, Direction.Up, 0, 4},
    {hero, Direction.Up, 5, 4},
  })
  cinematique.Respirer(25)

  local orphelin = 'orphelin'
  local ok_feminin, feminin = pcall(function()
    return partner.BaseForm.Gender == Gender.Female
  end)
  if ok_feminin and feminin then orphelin = 'orpheline' end

  say(partner, 'Happy', "On est ressortis… et regarde : le jour s’est levé pendant que nous retraversions les [color=#69D98C]Bois Perdus[color].", 'droite')
  geste_heros(hero, 'autour')
  say(partner, 'Normal', "C’est la même falaise que cette nuit, mais dans l’autre sens.\nLe chemin de l’est nous a ramenés chez moi.", 'droite')
  GAME:MoveCamera(porte.Position.X + 20, porte.Position.Y + 20, 75, false)
  say(partner, 'Happy', "La petite maison que tu vois là-bas… c’est là que je vis.", 'droite')
  say(partner, 'Normal', "Ce n’est pas très grand, mais c’est mon point d’ancrage :\nun toit, un lit, quelques provisions, et la mer juste derrière.", 'droite')
  say(partner, 'Worried', "Je ne t’ai pas encore parlé de moi. Je n’ai pas connu mes parents ; je suis " .. orphelin .. ".", 'droite')
  geste_heros(hero, 'inquiet')
  say(partner, 'Normal', "C’est tatie Kangourex qui m’a recueilli quand j’étais tout petit.\nTout le monde l’appelle comme ça, même ceux qui ne sont pas de sa famille.", 'droite')
  say(partner, 'Happy', "Elle s’occupe de moi depuis toujours :\nun repas chaud, un conseil avant de partir, un endroit où déposer ce qui compte. Sans elle, cette maison serait bien vide.", 'droite')

  GAME:MoveCamera(point.Position.X, point.Position.Y, 75, false)
  geste_heros(hero, 'question')
  say(partner, 'Normal', "Tu te demandes où nous sommes exactement ?\nLa falaise surplombe les chemins qui descendent vers [color=#F5D27A]Réverie Town[color].", 'droite')
  say(partner, 'Happy', "C’est la ville d’en bas : des boutiques, des ponts, des voyageurs,\ndes équipes qui préparent leurs expéditions…\net tatie Kangourex, qui garde les objets des explorateurs.", 'droite')
  say(partner, 'Normal', "Là-bas, une équipe de secours répond aux appels des Pokémon perdus, blessés ou piégés dans un donjon.\nElle part les chercher et les ramène auprès des leurs.", 'droite')
  say(partner, 'Normal', "Les explorateurs, eux, ouvrent les routes :\nils cartographient des lieux inconnus, signalent les passages dangereux et reviennent parfois avec des trésors ou des récits précieux.", 'droite')
  say(partner, 'Happy', "Beaucoup d’équipes font les deux.\nSecourir quelqu’un et découvrir le chemin qui mène jusqu’à lui, au fond, c’est le même métier du cœur.", 'droite')
  geste_heros(hero, 'question')
  say(partner, 'Normal', "Les guildes ? Ce sont les maisons communes de ces équipes.\nOn y reçoit des demandes, on s’y entraîne, on y apprend les règles des donjons et on y partage les cartes.", 'droite')
  say(partner, 'Normal', "Il y en a dans plusieurs régions du monde.\nChacune a ses maîtres, ses traditions et ses explorateurs célèbres ; aucune ne détient toutes les routes.", 'droite')
  say(partner, 'Happy', "Moi, je rêve qu’un jour notre équipe soit reconnue par une guilde.\nPas pour briller sur une affiche… pour être prête quand un appel viendra de loin.", 'droite')
  cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  -- Chemin normal : RencontreTeamDazzling entre en donjon et ne revient
  -- pas ici ; ApresCombatTeamDazzling appellera cette conclusion. Le
  -- présent appel ne sert que si les spawners Dazzling sont absents.
  if SV.Destiny.CombatDazzling ~= 'en_cours' then
    cliffdaytest.ConclureArriveeDestiny(hero, partner, point)
  end
end

return cliffdaytest
