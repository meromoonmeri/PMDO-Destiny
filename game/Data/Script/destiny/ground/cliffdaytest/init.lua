--[[ init.lua — Falaise de Réverie (jour)
     Scène principale du prologue après la traversée inverse de Lost Wood :
     - Le duo débouche à l'est au lever du jour ;
     - Devant sa maison, le partenaire explique que c'est là où il/elle vit,
       qu'il/elle est orphelin(e) et que Tatie Kangourex veille sur lui/elle ;
     - Au croisement, le partenaire présente Réverie Town, les équipes de secours
       et d'exploration ainsi que les Guildes à travers le monde ;
     - Tous deux descendent ensuite la route du sud vers Réverie Town.
     Hors prologue (SV.Destiny.RetourAccompli absent), la saynète Team Dazzling
     d'origine reste disponible pour les tests dédiés.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local cliffdaytest = {}

local function anim(ch, name, looped)
  if ch ~= nil then GROUND:CharSetAnim(ch, name, looped) end
end

local function say(ch, emotion, text)
  UI:SetSpeaker(ch)
  UI:SetSpeakerEmotion(emotion or 'Normal')
  UI:WaitShowDialogue(text)
end

local function penser_heros(hero, emotion, text)
  UI:SetSpeaker(hero, false)
  UI:SetSpeakerEmotion(emotion or 'Normal')
  UI:WaitShowDialogue(text)
end

local function tourner(ch, dir)
  if ch == nil then return end
  if GROUND.EntTurn ~= nil then
    GROUND:EntTurn(ch, dir)
  elseif GROUND.CharAnimateTurnTo ~= nil then
    GROUND:CharAnimateTurnTo(ch, dir, 4)
  end
end

local function hocher_tete(ch)
  if ch == nil then return end
  GROUND:CharSetAnim(ch, 'Nod', false)
  GAME:WaitFrames(26)
  GROUND:CharSetAnim(ch, 'Idle', true)
end

local function abaisser_canopee_chemin()
  if _ZONE == nil or _ZONE.CurrentGround == nil or _ZONE.CurrentGround.Layers == nil then
    return nil, nil
  end
  local carte = _ZONE.CurrentGround
  for i = 0, carte.Layers.Count - 1 do
    local couche = carte.Layers[i]
    if couche.Name == 'Canopée — avant-plan' then
      local ordre = couche.Layer
      if DrawLayer ~= nil then couche.Layer = DrawLayer.Normal end
      return couche, ordre
    end
  end
  return nil, nil
end

local function est_partenaire_feminin(partenaire)
  if partenaire == nil or Gender == nil then return false end
  if partenaire.CurrentForm ~= nil and partenaire.CurrentForm.Gender == Gender.Female then
    return true
  end
  return false
end

function cliffdaytest.Init(map)
  if map ~= nil and RogueEssence ~= nil and RogueEssence.Dungeon ~= nil and RogueEssence.Dungeon.BaseMap ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  if DEBUG ~= nil and DEBUG.EnableDbgCoro ~= nil then DEBUG.EnableDbgCoro() end

  if SV.Destiny ~= nil and SV.Destiny.RetourAccompli then
    equipe_scene.RestaurerHeros()
    GROUND:RefreshPlayer()
    if CH('Pichu') ~= nil then GROUND:Hide('Pichu') end
    local hero = CH('PLAYER')
    if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
      local partner = CH('Teammate1') or equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
      if SV.Destiny.FinaleDestiny and partner ~= nil then
        equipe_scene.Suivre(partner, hero)
      end
    end
    return
  end

  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
    if partner ~= nil then equipe_scene.Suivre(partner, hero) end
  end
  if not SV.PichuDazzling or not SV.PichuDazzling.Seen then
    for _, nom in ipairs({'Adagio', 'Sonata', 'Aria'}) do
      if CH(nom) == nil then GROUND:SpawnerDoSpawn(nom) end
    end
  end
end

function cliffdaytest.AllerEnVille()
  SOUND:FadeOutBGM(50)
  GAME:FadeOut(false, 50)
  GAME:CutsceneMode(false)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function cliffdaytest.SceneRetourJour()
  equipe_scene.RestaurerHeros()
  GROUND:RefreshPlayer()
  if CH('Pichu') ~= nil then GROUND:Hide('Pichu') end

  local hero = CH('PLAYER')
  local partenaire = CH('Teammate1')
  if partenaire == nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(944, 468, Direction.Left)
  end
  if hero == nil or partenaire == nil then
    GAME:FadeIn(20)
    return
  end

  local feminin = est_partenaire_feminin(partenaire)
  local mot_orphelin = feminin and "orpheline" or "orphelin"
  local mot_seul = feminin and "toute seule" or "tout seul"
  local mot_petit = feminin and "toute petite" or "tout petit"
  local mot_reconnu = feminin and "reconnue" or "reconnu"

  local avant_plan, ordre_avant_plan = abaisser_canopee_chemin()

  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  partenaire.CollisionDisabled = true

  GROUND:TeleportTo(partenaire, 944, 468, Direction.Left)
  GROUND:TeleportTo(hero, 968, 468, Direction.Left)
  GAME:MoveCamera(824, 468, 1, false)

  UI:WaitShowTitle("Falaise de Réverie", 30)
  GAME:WaitFrames(45)
  UI:WaitHideTitle(30)

  SOUND:PlayBGM("Cliff Camp.ogg", true)
  GAME:FadeIn(50)

  -- 1. Sortie du chemin est de Lost Wood au grand jour
  local sortie_part = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 748, 468, false, 1)
    tourner(partenaire, Direction.Right)
  end)
  local sortie_hero = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(hero, 780, 468, false, 1)
    tourner(hero, Direction.Left)
  end)
  local sortie_cam = TASK:BranchCoroutine(function()
    GAME:MoveCamera(764, 468, 90, false)
  end)
  TASK:JoinCoroutines({ sortie_part, sortie_hero, sortie_cam })

  say(partenaire, 'Inspired', "Nous sommes sortis de [color=#69D98C]Lost Wood[color] ! Et regarde : le jour s'est levé pendant notre traversée !")
  hocher_tete(hero)
  penser_heros(hero, 'Happy', "(Quelle clarté… Tout semble bien plus paisible à la lumière du matin.)")
  say(partenaire, 'Happy', "Viens par ici une minute, je vais te montrer l'endroit où j'habite !")

  -- 2. Arrêt devant la maison du partenaire : sa vie ici, orphelin(e), Tatie Kangourex
  local maison_part = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 696, 468, false, 1)
    GROUND:MoveToPosition(partenaire, 656, 512, false, 1)
    GROUND:MoveToPosition(partenaire, 600, 476, false, 1)
    tourner(partenaire, Direction.Up)
  end)
  local maison_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(10)
    GROUND:MoveToPosition(hero, 696, 468, false, 1)
    GROUND:MoveToPosition(hero, 656, 512, false, 1)
    GROUND:MoveToPosition(hero, 628, 480, false, 1)
    tourner(hero, Direction.Up)
  end)
  local maison_cam = TASK:BranchCoroutine(function()
    GAME:MoveCamera(608, 468, 110, false)
  end)
  TASK:JoinCoroutines({ maison_part, maison_hero, maison_cam })
  GAME:WaitFrames(20)

  tourner(partenaire, Direction.Right)
  tourner(hero, Direction.Left)
  say(partenaire, 'Happy', "Voilà ma maison ! C'est ici que je vis, tout en haut de la falaise.")
  penser_heros(hero, 'Normal', "(On s'y sent tout de suite bien, avec le bruit des vagues au loin… Je me demande si sa famille habite ici aussi.)")
  if GROUND.CharSetEmote ~= nil then GROUND:CharSetEmote(hero, 'question', 1) end
  GAME:WaitFrames(20)
  say(partenaire, 'Sad', "Tu te demandes sûrement où est ma famille ? En fait… je suis " .. mot_orphelin .. ". Je n'ai pas de souvenirs de mes parents, alors j'habite dans cette maison par mes propres moyens.")
  say(partenaire, 'Happy', "Mais je ne suis pas " .. mot_seul .. " ! [color=#F5D27A]Tatie Kangourex[color] s'occupe de moi et veille sur moi depuis que je suis " .. mot_petit .. ".")
  say(partenaire, 'Normal', "Elle a un cœur immense : elle s'assure toujours que je ne manque de rien, et en ville elle garde aussi les provisions des voyageurs.")
  hocher_tete(hero)
  penser_heros(hero, 'Happy', "(Tatie Kangourex a l'air d'être quelqu'un d'exceptionnel. J'ai hâte de faire sa connaissance.)")

  -- 3. Au croisement : Réverie Town, équipes de secours/explorateurs et Guildes à travers le monde
  local crois_part = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 656, 526, false, 1)
    tourner(partenaire, Direction.Down)
  end)
  local crois_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, 628, 526, false, 1)
    tourner(hero, Direction.Down)
  end)
  local crois_cam = TASK:BranchCoroutine(function()
    GAME:MoveCamera(656, 526, 45, false)
  end)
  TASK:JoinCoroutines({ crois_part, crois_hero, crois_cam })
  GAME:WaitFrames(15)

  say(partenaire, 'Happy', "Tout en bas de ce sentier se trouve [color=#F5D27A]Réverie Town[color], la capitale des explorateurs ! C'est une ville bâtie autour de grandes cascades et de ponts de pierre.")
  say(partenaire, 'Normal', "Les habitants y vivent en harmonie, et d'innombrables Pokémon s'y croisent avant de partir en expédition.")
  tourner(partenaire, Direction.Left)
  tourner(hero, Direction.Right)
  if GROUND.CharSetEmote ~= nil then GROUND:CharSetEmote(hero, 'question', 1) end
  GAME:WaitFrames(18)
  penser_heros(hero, 'Normal', "(Des expéditions… ? Comme dans les donjons mystères tels que [color=#69D98C]Lost Wood[color] ?)")
  say(partenaire, 'Inspired', "Exactement ! Comme les donjons mystères changent sans cesse de forme, des Pokémon s'associent pour former des équipes de secours et des équipes d'explorateurs.")
  say(partenaire, 'Normal', "Les équipes de secours portent assistance aux Pokémon perdus ou en danger, tandis que les équipes d'explorateurs cartographient des lieux inconnus et percent les mystères anciens.")
  say(partenaire, 'Happy', "Et à travers le monde entier, il existe des Guildes qui rassemblent, forment et soutiennent ces équipes : elles coordonnent les missions d'entraide et les grandes expéditions !")
  say(partenaire, 'Inspired', "Il y a même une célèbre Guilde sur les hauteurs de [color=#F5D27A]Réverie Town[color]. Mon plus grand rêve, c'est d'y fonder une vraie équipe et d'être " .. mot_reconnu .. " comme explorateur !")
  hocher_tete(hero)
  penser_heros(hero, 'Happy', "(Secourir ceux qui en ont besoin et explorer ce monde… En restant ici, je découvrirai peut-être aussi comment je suis devenu un Pokémon.)")
  say(partenaire, 'Happy', "Alors descendons vite à [color=#F5D27A]Réverie Town[color] ! Je vais te présenter Tatie Kangourex et te montrer toute la ville !")

  -- 4. Descente par la route du sud vers Réverie Town
  local sud_part = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 708, 556, false, 1)
    GROUND:MoveToPosition(partenaire, 716, 650, false, 1)
    GROUND:MoveToPosition(partenaire, 732, 748, false, 1)
  end)
  local sud_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(10)
    GROUND:MoveToPosition(hero, 708, 556, false, 1)
    GROUND:MoveToPosition(hero, 716, 650, false, 1)
    GROUND:MoveToPosition(hero, 732, 720, false, 1)
  end)
  local sud_cam = TASK:BranchCoroutine(function()
    GAME:MoveCamera(716, 650, 95, false)
  end)
  TASK:JoinCoroutines({ sud_part, sud_hero, sud_cam })

  if avant_plan ~= nil then avant_plan.Layer = ordre_avant_plan end
  hero.CollisionDisabled = false
  partenaire.CollisionDisabled = false
  equipe_scene.Suivre(partenaire, hero)
  GAME:MoveCamera(0, 0, 30, true)
  SV.Destiny.FinaleDestiny = true
  SV.Destiny.VisiteVille = 'en_route'
  cliffdaytest.AllerEnVille()
end

function cliffdaytest.PlotScripting()
  if SV.Destiny ~= nil and SV.Destiny.RetourAccompli then
    if not SV.Destiny.FinaleDestiny then
      cliffdaytest.SceneRetourJour()
    elseif SV.Destiny.VisiteVille == 'en_route' then
      cliffdaytest.AllerEnVille()
    else
      GAME:FadeIn(20)
    end
    return
  end

  SV.PichuDazzling = SV.PichuDazzling or {}
  if not SV.PichuDazzling.Seen then
    cliffdaytest.Cinematique_Rencontre_Team_Dazzling()
  else
    GAME:FadeIn(20)
  end
end

function cliffdaytest.Enter(map)
  cliffdaytest.PlotScripting()
end

function cliffdaytest.Exit(map) end
function cliffdaytest.Update(map) end
function cliffdaytest.GameSave(map) end
function cliffdaytest.GameLoad(map)
  cliffdaytest.PlotScripting()
end

function cliffdaytest.Cinematique_Rencontre_Team_Dazzling()
  local pichu = CH('Pichu')
  local adagio = CH('Adagio')
  local sonata = CH('Sonata')
  local aria = CH('Aria')
  GAME:CutsceneMode(true)
  if pichu ~= nil then AI:DisableCharacterAI(pichu); anim(pichu, 'Idle', true) end
  if adagio ~= nil then AI:DisableCharacterAI(adagio) end
  if sonata ~= nil then AI:DisableCharacterAI(sonata) end
  if aria ~= nil then AI:DisableCharacterAI(aria) end
  GAME:MoveCamera(608, 476, 1, false)
  GAME:FadeIn(30)
  GROUND:MoveToPosition(pichu, 608, 476, false, 1)
  anim(pichu, 'Idle', true)
  say(pichu, 'Happy', 'Ouah… Quel bon vent marin ce matin !')
  say(pichu, 'Joyous', 'On entend les vagues jusque devant la porte !')
  GROUND:MoveToPosition(pichu, 556, 476, false, 1)
  GROUND:CharSetAnim(pichu, 'Idle', true)
  say(pichu, 'Inspired', 'Un jour, je partirai explorer des endroits dont personne ne connaît encore le nom.')
  GROUND:MoveToPosition(pichu, 612, 476, false, 1)
  GROUND:MoveToPosition(pichu, 640, 526, false, 1)
  GAME:MoveCamera(640, 526, 30, false)
  say(pichu, 'Determined', 'La Guilde… C’est là que commencent les grandes aventures !')
  say(pichu, 'Determined', 'Je vais leur montrer que moi aussi, je peux devenir explorateur !')
  GAME:MoveCamera(700, 600, 30, false)
  local a = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(adagio, 716, 650, false, 1)
    GROUND:MoveToPosition(adagio, 708, 560, false, 1)
    GROUND:MoveToPosition(adagio, 674, 524, false, 1)
  end)
  local b = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(sonata, 704, 668, false, 1)
    GROUND:MoveToPosition(sonata, 702, 574, false, 1)
    GROUND:MoveToPosition(sonata, 692, 506, false, 1)
  end)
  local c = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(aria, 728, 664, false, 1)
    GROUND:MoveToPosition(aria, 718, 578, false, 1)
    GROUND:MoveToPosition(aria, 694, 542, false, 1)
  end)
  TASK:JoinCoroutines({a, b, c})
  GAME:MoveCamera(660, 526, 24, false)
  GROUND:CharTurnToCharAnimated(sonata, pichu, 4)
  say(sonata, 'Happy', 'Ohhh, regardez-moi ce tout petit bout de chou ! Tu t’es perdu loin de ton nid, bonhomme ?')
  GROUND:CharTurnToCharAnimated(pichu, sonata, 4)
  anim(pichu, 'Hop', false)
  say(pichu, 'Shouting', 'Je ne suis pas un bébé ! Je vais rejoindre la Guilde et devenir explorateur !')
  anim(aria, 'Attack', false)
  say(aria, 'Happy', 'Au premier coup de vent dans un donjon, tu risques de t’envoler avant le premier étage !')
  anim(sonata, 'Appeal', false)
  say(sonata, 'Joyous', 'Et tes joues, elles crépitent toujours quand tu te donnes de grands airs ?')
  anim(pichu, 'Charge', false)
  say(pichu, 'Determined', 'Je peux me débrouiller ! Regardez bien !')
  anim(pichu, 'Shock', false)
  GAME:WaitFrames(18)
  anim(pichu, 'Pain', false)
  say(pichu, 'Pain', 'Bzzzt ! Aïe… mes joues !')
  anim(adagio, 'Kick', false)
  say(adagio, 'Angry', 'La Guilde, ce n’est pas une garderie pour bébés Pokémon en quête d’histoires !')
  anim(aria, 'Rotate', false)
  say(aria, 'Happy', 'Commence par maîtriser tes étincelles avant de rêver aux donjons !')
  anim(pichu, 'Hurt', false)
  say(pichu, 'Worried', 'Je… je vais m’entraîner. Je ne laisserai pas ça m’arrêter.')
  GROUND:CharSetAnim(adagio, 'Walk', true)
  GROUND:CharSetAnim(sonata, 'Walk', true)
  GROUND:CharSetAnim(aria, 'Walk', true)
  say(adagio, 'Happy', 'Allez, les filles. On n’a pas toute la journée.')
  local d = TASK:BranchCoroutine(function() GROUND:MoveToPosition(adagio, 696, 468, false, 1); GROUND:MoveToPosition(adagio, 968, 468, false, 1) end)
  local e = TASK:BranchCoroutine(function() GROUND:MoveToPosition(sonata, 704, 468, false, 1); GROUND:MoveToPosition(sonata, 960, 468, false, 1) end)
  local f = TASK:BranchCoroutine(function() GROUND:MoveToPosition(aria, 712, 468, false, 1); GROUND:MoveToPosition(aria, 952, 468, false, 1) end)
  TASK:JoinCoroutines({d, e, f})
  GAME:MoveCamera(640, 526, 24, false)
  anim(pichu, 'Sit', true)
  say(pichu, 'Teary-Eyed', 'Peut-être qu’elles ont raison… Je n’ai même pas réussi à lancer une étincelle.')
  anim(pichu, 'DeepBreath', false)
  say(pichu, 'Determined', 'Non. Leur rire ne décidera pas de ce que je vaux.')
  anim(pichu, 'Pose', false)
  say(pichu, 'Shouting', 'Je rejoindrai la Guilde. Et je deviendrai explorateur, quoi qu’il arrive !')
  anim(pichu, 'Walk', true)
  GROUND:MoveToPosition(pichu, 708, 556, false, 1)
  GROUND:MoveToPosition(pichu, 716, 650, false, 1)
  GAME:MoveCamera(716, 650, 30, false)
  GROUND:MoveToPosition(pichu, 736, 770, false, 1)
  GAME:WaitFrames(30)
  SV.PichuDazzling.Seen = true
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
end

return cliffdaytest
