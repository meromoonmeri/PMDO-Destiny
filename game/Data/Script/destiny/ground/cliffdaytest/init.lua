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
local function poser_dazzling(ch, animation)
  if ch == nil then return end
  UI:ResetSpeaker()
  GROUND:CharSetEmote(ch, 'glowing', 4)
  local emitter = RogueEssence.Content.FiniteAreaEmitter(
    RogueEssence.Content.AnimData('Sparkle_RSE', 3))
  emitter.Range = 36
  emitter.Speed = 16
  emitter.TotalParticles = 7
  emitter.LocHeight = 18
  local pos = ch.MapLoc or ch.Position
  GROUND:PlayVFX(emitter, pos.X, pos.Y)
  anim(ch, animation or 'Pose', false)
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

-- La Team Dazzling remonte le chemin du sud en direction d'une mission à
-- l'est et croise le duo au panorama. Adagio (Tsareena) mène l'équipe avec
-- une arrogance très calculée ; Aria (Mawile) raille tout ce qui bouge ;
-- Sonata (Lopunny) transforme chaque réplique en numéro de scène, souvent
-- sous les corrections acides d'Aria. Leurs poses sont soulignées par
-- l'émote lumineuse et une pluie discrète de sparkles.
function cliffdaytest.RencontreTeamDazzling(hero, partner, point)
  local sud = MRKR('Dazzling_Entry_South')
  local adagio = personnage_dazzling('Adagio')
  local sonata = personnage_dazzling('Sonata')
  local Aria = personnage_dazzling('Aria')
  if adagio == nil or sonata == nil or Aria == nil then
    print('[Destiny] Rencontre Team Dazzling suspendue : spawner incomplet.')
    return
  end

  GROUND:TeleportTo(adagio, sud.Position.X + 8, sud.Position.Y + 8, Direction.Up)
  GROUND:TeleportTo(sonata, sud.Position.X - 14, sud.Position.Y + 10, Direction.Up)
  GROUND:TeleportTo(Aria, sud.Position.X + 34, sud.Position.Y + 11, Direction.Up)

  say(adagio, 'Joyous', "Oh oh oh… Une guilde ? Vous deux ? J’ai failli manquer le début de la comédie.")
  geste_heros(hero, 'question')
  GROUND:CharTurnToCharAnimated(partner, adagio, 4)
  say(partner, 'Worried', "Qui va là ?")
  GAME:MoveCamera(700, 600, 45, false)

  local entree_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 716, 650, false, 1)
    GROUND:MoveToPosition(adagio, 708, 560, false, 1)
    GROUND:MoveToPosition(adagio, point.Position.X + 20, point.Position.Y + 8, false, 1)
  end)
  local entree_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 704, 668, false, 1)
    GROUND:MoveToPosition(sonata, 702, 574, false, 1)
    GROUND:MoveToPosition(sonata, point.Position.X + 38, point.Position.Y - 10, false, 1)
  end)
  local entree_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 728, 664, false, 1)
    GROUND:MoveToPosition(Aria, 718, 578, false, 1)
    GROUND:MoveToPosition(Aria, point.Position.X + 40, point.Position.Y + 28, false, 1)
  end)
  TASK:JoinCoroutines({entree_adagio, entree_sonata, entree_aria})
  GAME:MoveCamera(point.Position.X + 14, point.Position.Y + 10, 35, false)
  GROUND:CharTurnToCharAnimated(hero, adagio, 4)
  GROUND:CharTurnToCharAnimated(partner, adagio, 4)
  GROUND:CharTurnToCharAnimated(adagio, partner, 4)
  GROUND:CharTurnToCharAnimated(sonata, partner, 4)
  GROUND:CharTurnToCharAnimated(Aria, partner, 4)

  poser_dazzling(adagio, 'Pose')
  GAME:WaitFrames(18)
  say(adagio, 'Happy', "Moi, c’est Adagio, meneuse de la [color=#FF9FD8]Team Dazzling[color]. Exploratrice recherchée, admirée… et en route pour une vraie mission.")
  poser_dazzling(sonata, 'Appeal')
  GAME:WaitFrames(14)
  say(sonata, 'Joyous', "Et moi, c’est Sonata ! On pose, on brille, et tout le monde sait qu’on est les meilleures !")
  poser_dazzling(Aria, 'Rotate')
  GAME:WaitFrames(14)
  say(Aria, 'Angry', "Non, Sonata. Tout le monde sait surtout que tu es capable de saluer l’affiche d’une mission au lieu de la lire.")
  say(sonata, 'Worried', "Eh ! Elle était très bien encadrée, cette affiche.")
  say(adagio, 'Normal', "Aria voit juste, même quand sa langue pique. Deux novices couverts de feuilles, à peine sortis de Lost Wood, et déjà le mot « guilde » à la bouche…")
  say(partner, 'Determined', "Nous avons traversé [color=#69D98C]Lost Wood[color]. À l’aller, puis au retour.")
  say(Aria, 'Happy', "Deux traversées ? Vous confondez persévérance et sens de l’orientation défaillant.")
  say(sonata, 'Joyous', "Ou alors la forêt offre un ruban à la deuxième traversée ! Il est où, le vôtre ?")
  say(Aria, 'Normal', "Au même endroit imaginaire que leur réputation.")
  poser_dazzling(adagio, 'Pose')
  GAME:WaitFrames(14)
  say(adagio, 'Happy', "Écoutez le conseil gratuit d’une aînée : la société des explorateurs n’est pas une cour de récréation.")
  say(adagio, 'Joyous', "Réverie Town n’a que faire d’amateurs comme vous. Des perdants feraient mieux d’aller briller ailleurs. Hahaha !")
  poser_dazzling(sonata, 'Appeal')
  say(sonata, 'Happy', "Briller en marchant, moi, je sais faire !")
  say(Aria, 'Angry', "Briller, oui. Marcher droit, c’est encore en chantier.")

  say(adagio, 'Normal', "Et ton compagnon silencieux, là ? Il attend que tu lui prêtes aussi ton courage ?")
  GROUND:MoveToPosition(hero, point.Position.X - 6, point.Position.Y, false, 1)
  geste_heros(hero, 'determine')
  say(partner, 'Determined', "Il n’a pas besoin de parler pour tenir debout. Et moi non plus, je ne demanderai pas la permission d’avancer.")
  say(sonata, 'Joyous', "Oh ! La pose du héros muet ! Aria, tu crois que je peux l’apprendre ?")
  say(Aria, 'Normal', "Commence par fermer la bouche dix secondes. Ce sera ton premier exploit.")
  say(adagio, 'Happy', "Touchant. Gardez cette belle assurance pour le jour où une guilde vous rira au nez.")
  say(adagio, 'Joyous', "Et si, par miracle, elle vous ouvre sa porte, prévenez-moi. J’adore assister aux miracles… surtout lorsqu’ils s’effondrent en public.")
  say(adagio, 'Normal', "Allons, les filles. Une mission nous attend à l’est, et notre réputation déteste patienter.")
  poser_dazzling(adagio, 'Pose')
  poser_dazzling(sonata, 'Appeal')
  poser_dazzling(Aria, 'Rotate')
  GAME:WaitFrames(22)
  say(sonata, 'Happy', "Bye-bye, les presque-explorateurs !")
  say(Aria, 'Angry', "Sonata, on ne fait pas de signes à la concurrence.")
  say(sonata, 'Joyous', "Ah, pardon : au revoir, la concurrence !")

  local sortie_adagio = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 696, 468, false, 1)
    GROUND:MoveToPosition(adagio, 968, 468, false, 1)
  end)
  local sortie_sonata = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 704, 468, false, 1)
    GROUND:MoveToPosition(sonata, 960, 468, false, 1)
  end)
  local sortie_aria = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(Aria, 712, 468, false, 1)
    GROUND:MoveToPosition(Aria, 952, 468, false, 1)
  end)
  TASK:JoinCoroutines({sortie_adagio, sortie_sonata, sortie_aria})
  GROUND:RemoveCharacter('Adagio')
  GROUND:RemoveCharacter('Sonata')
  GROUND:RemoveCharacter('Aria')
  SV.Destiny.TeamDazzlingRencontree = true

  GAME:MoveCamera(point.Position.X, point.Position.Y, 45, false)
  GROUND:CharTurnToCharAnimated(partner, hero, 4)
  GROUND:CharTurnToCharAnimated(hero, partner, 4)
  say(partner, 'Normal', "La [color=#FF9FD8]Team Dazzling[color]… On dit qu’elles sont brillantes en mission. Pour les manières, la mer pourrait leur donner des leçons de profondeur.")
  say(partner, 'Worried', "Elles savent exactement où appuyer pour faire douter.")
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
