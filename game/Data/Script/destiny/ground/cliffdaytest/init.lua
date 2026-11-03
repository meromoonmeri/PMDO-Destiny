require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cliffdaytest = {}
local function anim(ch, name, looped)
  if ch ~= nil then GROUND:CharSetAnim(ch, name, looped) end
end
local function say(ch, emotion, text)
  UI:SetSpeaker(ch)
  UI:SetSpeakerEmotion(emotion)
  UI:WaitShowDialogue(text)
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
local function etoiles_dazzling(ch)
  if ch == nil then return end
  SOUND:PlayBattleSE('_UNK_DUN_Twinkle')
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
local function poser_dazzling(ch)
  if ch == nil then return end
  UI:ResetSpeaker()
  etoiles_dazzling(ch)
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
local function retour_destiny_en_attente()
  return SV.Destiny ~= nil and SV.Destiny.RetourAccompli
    and not SV.Destiny.FinaleDestiny
end
-- Dans la scène Destiny, le héros ne parle pas : il répond au partenaire
-- par ses orientations et ses émotes, comme lors des retrouvailles.
local function geste_heros(hero, geste)
  if hero == nil then return end
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(30)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
    GAME:WaitFrames(22)
  elseif geste == 'oui' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(9)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(10)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(16)
  elseif geste == 'inquiet' then
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 8)
    GAME:WaitFrames(36)
  elseif geste == 'determine' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 6)
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
  GAME:CutsceneMode(false)
  -- Réverie Town reste une carte distincte, dans sa zone d'origine.
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

-- Première rencontre de la Team Dazzling, sur le chemin de la falaise.
-- Trajectoires figées sur les chemins de cliffdaytest :
--   * révélation au sud : Adagio (726,704), Aria (708,720), Sonata (750,720) ;
--   * remontée en colonne par le couloir x=716, puis éventail face au duo :
--     Adagio (700,560), Aria (684,572), Sonata (724,572) ;
--   * héros (680,528) et partenaire (700,528) barrent le chemin, puis sont
--     poussés à l'ouest en (648,532) et (672,532) ;
--   * sortie en colonne par (700,468), puis vers l'est et Hide hors champ.
-- Leur thème social (Encounter! Jacinthe) ne couvre pas la voix hors champ :
-- il démarre sur la révélation caméra, lorsque les trois prennent la pose.
function cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  local sud = MRKR('Dazzling_Entry_South')
  local adagio = personnage_dazzling('Adagio')
  local sonata = personnage_dazzling('Sonata')
  local Aria = personnage_dazzling('Aria')
  if adagio == nil or sonata == nil or Aria == nil then
    print('[Destiny] Rencontre Team Dazzling suspendue : spawner incomplet.')
    return
  end

  GROUND:TeleportTo(adagio, sud.Position.X - 5, sud.Position.Y - 58, Direction.Up)
  GROUND:TeleportTo(Aria, sud.Position.X - 23, sud.Position.Y - 42, Direction.Up)
  GROUND:TeleportTo(sonata, sud.Position.X + 19, sud.Position.Y - 42, Direction.Up)

  -- Voix hors champ, sans portrait : le duo entend Adagio avant de la voir.
  GAME:WaitFrames(18)
  UI:SetSpeaker('???', true, '', -1, '', RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue("Mais regardez qui voilà… deux petits morveux. (Décidément, ils n’ont aucun style.)")

  local reaction_partenaire = TASK:BranchCoroutine(function()
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    GROUND:CharSetEmote(partner, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(partner, Direction.Down, 4)
  end)
  local reaction_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
  end)
  TASK:JoinCoroutines({reaction_partenaire, reaction_heros})
  say(partner, 'Worried', "Qui va là ?!")

  -- Le duo gagne le couloir qui descend au sud pour voir d'où vient la voix.
  local approche_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, 700, 516, false, 1)
    GROUND:MoveToPosition(partner, 700, 528, false, 1)
  end)
  local approche_heros = TASK:BranchCoroutine(function()
    GAME:WaitFrames(6)
    GROUND:MoveToPosition(hero, 680, 516, false, 1)
    GROUND:MoveToPosition(hero, 680, 528, false, 1)
  end)
  TASK:JoinCoroutines({approche_partenaire, approche_heros})

  SOUND:FadeOutBGM(45)
  GAME:MoveCamera(726, 688, 80, false)
  GAME:WaitFrames(10)
  SOUND:PlayBGM(MUSIQUE_DAZZLING_SOCIALE, true)
  GROUND:CharAnimateTurnTo(adagio, Direction.Down, 4)
  GROUND:CharAnimateTurnTo(Aria, Direction.Down, 5)
  GROUND:CharAnimateTurnTo(sonata, Direction.Down, 6)
  poser_dazzling(adagio)
  GAME:WaitFrames(7)
  poser_dazzling(Aria)
  GAME:WaitFrames(7)
  poser_dazzling(sonata)
  GAME:WaitFrames(28)
  finir_pose_dazzling(adagio)
  finir_pose_dazzling(Aria)
  finir_pose_dazzling(sonata)
  GROUND:CharAnimateTurnTo(adagio, Direction.Up, 4)
  GROUND:CharAnimateTurnTo(Aria, Direction.Up, 5)
  GROUND:CharAnimateTurnTo(sonata, Direction.Up, 6)

  -- Adagio mène la remontée ; ses deux coéquipières se rabattent derrière
  -- elle dans l'étroit chemin du sud avant de s'ouvrir en éventail.
  local entree_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 716, 650, false, 1)
    GROUND:MoveToPosition(adagio, 708, 592, false, 1)
    GROUND:MoveToPosition(adagio, 700, 560, false, 1)
  end)
  local entree_aria = TASK:BranchCoroutine(function()
    GAME:WaitFrames(6)
    GROUND:MoveToPosition(Aria, 716, 674, false, 1)
    GROUND:MoveToPosition(Aria, 704, 604, false, 1)
    GROUND:MoveToPosition(Aria, 684, 572, false, 1)
  end)
  local entree_sonata = TASK:BranchCoroutine(function()
    GAME:WaitFrames(12)
    GROUND:MoveToPosition(sonata, 716, 698, false, 1)
    GROUND:MoveToPosition(sonata, 712, 616, false, 1)
    GROUND:MoveToPosition(sonata, 724, 572, false, 1)
  end)
  local suivi_entree = TASK:BranchCoroutine(function()
    GAME:MoveCamera(700, 544, 175, false)
  end)
  TASK:JoinCoroutines({entree_adagio, entree_aria, entree_sonata, suivi_entree})
  GROUND:CharTurnToCharAnimated(adagio, partner, 4)
  GROUND:CharTurnToCharAnimated(Aria, partner, 5)
  GROUND:CharTurnToCharAnimated(sonata, hero, 5)

  say(adagio, 'Happy', "Hello~ [color=#F5D27A]Réverie Town[color] n’est pas un lieu pour des amateurs, voyons.")
  say(partner, 'Angry', "Mais pour qui vous vous prenez ?!")
  geste_heros(hero, 'question')

  -- Présentation face caméra, comme une entrée en scène : la vraie Pose
  -- reste tenue pendant les noms, petites étoiles autour des trois.
  GROUND:CharAnimateTurnTo(adagio, Direction.Down, 4)
  GROUND:CharAnimateTurnTo(Aria, Direction.Down, 5)
  GROUND:CharAnimateTurnTo(sonata, Direction.Down, 6)
  poser_dazzling(adagio)
  GAME:WaitFrames(7)
  poser_dazzling(Aria)
  GAME:WaitFrames(7)
  poser_dazzling(sonata)
  GAME:WaitFrames(18)
  say(adagio, 'Happy', "Adagio, cheffe de la [color=#FF9FD8]Team Dazzling[color].")
  say(Aria, 'Happy', "Aria. Retenez le nom : vous l’entendrez souvent.")
  say(sonata, 'Joyous', "Et moi, Sonata ! La plus éblouissante des trois !")
  say(Aria, 'Normal', "La plus bruyante, surtout.")
  finir_pose_dazzling(adagio)
  finir_pose_dazzling(Aria)
  finir_pose_dazzling(sonata)
  GROUND:CharAnimateTurnTo(adagio, Direction.Up, 4)
  GROUND:CharAnimateTurnTo(Aria, Direction.Up, 5)
  GROUND:CharAnimateTurnTo(sonata, Direction.Up, 6)

  say(adagio, 'Happy', "Une équipe célèbre ne perd pas son temps avec deux enfants couverts de poussière.")
  say(partner, 'Determined', "On a traversé [color=#69D98C]Lost Wood[color]. Deux fois.")
  say(Aria, 'Happy', "Deux fois ? Ce n’est pas un exploit, c’est un problème d’orientation.")
  say(sonata, 'Joyous', "Moi, je trouve ça mignon : ils font presque équipe d’explorateurs.")
  say(adagio, 'Joyous', "« Presque ». C’est le mot parfait.")
  say(partner, 'Angry', "Répète un peu pour voir ?!")
  say(adagio, 'Normal', "Inutile. Les étoiles ne répètent pas pour les figurants.")
  say(adagio, 'Normal', "Allons, les filles. L’est nous attend.")
  say(sonata, 'Happy', "Bye-bye, les presque-explorateurs !")
  say(Aria, 'Normal', "Et dégagez le chemin.")

  -- Aria et Sonata se replacent derrière Adagio ; le trio reprend le même
  -- couloir au lieu de contourner poliment le duo.
  local colonne_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 700, 584, false, 1)
  end)
  local colonne_aria = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(Aria, 700, 608, false, 1)
  end)
  TASK:JoinCoroutines({colonne_sonata, colonne_aria})

  local contact_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 700, 544, false, 1)
  end)
  local contact_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 700, 568, false, 1)
  end)
  local contact_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 700, 592, false, 1)
  end)
  TASK:JoinCoroutines({contact_adagio, contact_sonata, contact_aria})

  SOUND:PlayBattleSE('DUN_Hit_Neutral')
  local pousse_heros = TASK:BranchCoroutine(function()
    GROUND:AnimateToPosition(hero, 'Hurt', Direction.Down, 648, 532, 1, 4, 0)
    GROUND:CharEndAnim(hero)
    GROUND:CharSetEmote(hero, 'shock', 1)
  end)
  local pousse_partenaire = TASK:BranchCoroutine(function()
    GAME:WaitFrames(3)
    GROUND:AnimateToPosition(partner, 'Hurt', Direction.Down, 672, 532, 1, 4, 0)
    GROUND:CharEndAnim(partner)
    GROUND:CharSetEmote(partner, 'shock', 1)
  end)
  local sortie_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 700, 468, false, 1.25)
    GROUND:MoveToPosition(adagio, 976, 468, false, 1.25)
  end)
  local sortie_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 700, 468, false, 1.25)
    GROUND:MoveToPosition(sonata, 952, 468, false, 1.25)
  end)
  local sortie_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 700, 468, false, 1.25)
    GROUND:MoveToPosition(Aria, 928, 468, false, 1.25)
  end)
  local regard_duo = TASK:BranchCoroutine(function()
    GAME:WaitFrames(45)
    GROUND:CharAnimateTurnTo(partner, Direction.Right, 5)
    GAME:WaitFrames(5)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
  end)
  local suivi_sortie = TASK:BranchCoroutine(function()
    GAME:MoveCamera(740, 520, 120, false)
    GAME:WaitFrames(55)
    SOUND:FadeOutBGM(60)
  end)
  TASK:JoinCoroutines({pousse_heros, pousse_partenaire, sortie_adagio,
    sortie_sonata, sortie_aria, regard_duo, suivi_sortie})

  GROUND:Hide('Adagio')
  GROUND:Hide('Sonata')
  GROUND:Hide('Aria')
  SV.Destiny.TeamDazzlingRencontree = true

  SOUND:PlayBGM('Cliff Camp.ogg', true)
  GAME:MoveCamera(660, 528, 60, false)
  say(partner, 'Angry', "Non mais je rêve ! Elles nous ont bousculés comme si le chemin leur appartenait !")
  GROUND:CharTurnToCharAnimated(partner, hero, 4)
  GROUND:CharTurnToCharAnimated(hero, partner, 5)
  say(partner, 'Worried', "La [color=#FF9FD8]Team Dazzling[color]… Brillantes, peut-être. Aimables, sûrement pas.")
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
  -- été interrompue : leurs spawners les recréeront au chemin sud.
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
  GROUND:CharAnimateTurnTo(partner, Direction.Up, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
  GAME:WaitFrames(25)

  local orphelin = 'orphelin'
  local ok_feminin, feminin = pcall(function()
    return partner.BaseForm.Gender == Gender.Female
  end)
  if ok_feminin and feminin then orphelin = 'orpheline' end

  say(partner, 'Happy', "On est ressortis… et regarde : le jour s’est levé pendant que nous retraversions [color=#69D98C]Lost Wood[color].")
  geste_heros(hero, 'autour')
  say(partner, 'Normal', "C’est la même falaise que cette nuit, mais dans l’autre sens. Le chemin de l’est nous a ramenés chez moi.")
  GAME:MoveCamera(porte.Position.X + 20, porte.Position.Y + 20, 75, false)
  say(partner, 'Happy', "La petite maison que tu vois là-bas… c’est là que je vis.")
  say(partner, 'Normal', "Ce n’est pas très grand, mais c’est mon point d’ancrage : un toit, un lit, quelques provisions, et la mer juste derrière.")
  say(partner, 'Worried', "Je ne t’ai pas encore parlé de moi. Je n’ai pas connu mes parents ; je suis " .. orphelin .. ".")
  geste_heros(hero, 'inquiet')
  say(partner, 'Normal', "C’est tatie Kangourex qui m’a recueilli quand j’étais tout petit. Tout le monde l’appelle comme ça, même ceux qui ne sont pas de sa famille.")
  say(partner, 'Happy', "Elle s’occupe de moi depuis toujours : un repas chaud, un conseil avant de partir, un endroit où déposer ce qui compte. Sans elle, cette maison serait bien vide.")

  GAME:MoveCamera(point.Position.X, point.Position.Y, 75, false)
  geste_heros(hero, 'question')
  say(partner, 'Normal', "Tu te demandes où nous sommes exactement ? La falaise surplombe les chemins qui descendent vers [color=#F5D27A]Réverie Town[color].")
  say(partner, 'Happy', "C’est la ville d’en bas : des boutiques, des ponts, des voyageurs, des équipes qui préparent leurs expéditions… et tatie Kangourex, qui garde les objets des explorateurs.")
  say(partner, 'Normal', "Là-bas, une équipe de secours répond aux appels des Pokémon perdus, blessés ou piégés dans un donjon. Elle part les chercher et les ramène auprès des leurs.")
  say(partner, 'Normal', "Les explorateurs, eux, ouvrent les routes : ils cartographient des lieux inconnus, signalent les passages dangereux et reviennent parfois avec des trésors ou des récits précieux.")
  say(partner, 'Happy', "Beaucoup d’équipes font les deux. Secourir quelqu’un et découvrir le chemin qui mène jusqu’à lui, au fond, c’est le même métier du cœur.")
  geste_heros(hero, 'question')
  say(partner, 'Normal', "Les guildes ? Ce sont les maisons communes de ces équipes. On y reçoit des demandes, on s’y entraîne, on y apprend les règles des donjons et on y partage les cartes.")
  say(partner, 'Normal', "Il y en a dans plusieurs régions du monde. Chacune a ses maîtres, ses traditions et ses explorateurs célèbres ; aucune ne détient toutes les routes.")
  say(partner, 'Happy', "Moi, je rêve qu’un jour notre équipe soit reconnue par une guilde. Pas pour briller sur une affiche… pour être prête quand un appel viendra de loin.")
  cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  geste_heros(hero, 'determine')
  say(partner, 'Happy', "Tu as raison. On n’a pas traversé [color=#69D98C]Lost Wood[color] pour demander la permission d’exister.")
  say(partner, 'Normal', "Alors viens. Je vais te présenter [color=#F5D27A]Réverie Town[color]. Nous passerons dire bonjour à tatie Kangourex, puis nous déciderons ensemble de notre prochaine étape.")

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

return cliffdaytest
