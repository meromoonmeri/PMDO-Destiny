--[[ init.lua — Clairière fleurie face à la mer et à la montagne (zrv2_zone_reveil_nuit)
     Deux scènes clés du prologue s'y déroulent :
     1. Avant la cinématique du partenaire : le héros dort au milieu des fleurs sous la
        pleine lune, murmure ses questions confuses (« … Où suis-je… ? », « Qui suis-je… ? »,
        « Tout me semble si flou… », « J'ai sommeil… »), puis un fondu au noir mène à
        la scène du partenaire sur cliffdaytest_nuit.
     2. Après la traversée solo de Lost Wood : longue cinématique de rencontre dans l'esprit
        Pokémon Donjon Mystère (5-10 min) :
        - Le héros reste muet : il répond uniquement par des hochements/mouvements de tête,
          petites animations en Idle et pensées intérieures entre parenthèses (...) ;
        - Le partenaire lui demande d'où il vient puis son prénom (saisie via UI:NameMenu)
          et lui répond que c'est un joli prénom ;
        - Le partenaire avance vers le rivage face à la montagne tandis que la caméra monte
          lentement vers la montagne et la pleine lune, avec le portrait émerveillé (Inspired)
          du partenaire racontant son rêve de former une équipe d'explorateurs ;
        - Le partenaire demande au héros s'il a un endroit où aller / ce qu'il compte faire
          (menu à choix multiples façon Donjon Mystère), puis lui propose de le suivre jusqu'à
          Réverie Town, la capitale des explorateurs ;
        - Pose finale du duo devant le paysage nord, fondu au noir et texte blanc sur fond noir
          (« Et c'est ainsi qu'une toute nouvelle histoire commença. »), avant la traversée
          inverse de Lost Wood (7F -> 1F).
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local zrv2_zone_reveil_nuit = {}

local HEROS_SOMMEIL_X, HEROS_SOMMEIL_Y = 376, 312
local ENTREE_FORET_X, ENTREE_FORET_Y = 384, 548
local BELVEDERE_HEROS_X, BELVEDERE_HEROS_Y = 368, 236
local BELVEDERE_PART_X, BELVEDERE_PART_Y = 400, 236

local function tourner(ch, dir)
  if ch == nil or dir == nil then return end
  if GROUND.CharAnimateTurnTo ~= nil then
    GROUND:CharAnimateTurnTo(ch, dir, 4)
  elseif GROUND.EntTurn ~= nil then
    GROUND:EntTurn(ch, dir)
  end
end

local function tourner_instant(ch, dir)
  if ch == nil or dir == nil then return end
  if GROUND.EntTurn ~= nil then
    GROUND:EntTurn(ch, dir)
  elseif GROUND.CharAnimateTurnTo ~= nil then
    GROUND:CharAnimateTurnTo(ch, dir, 1)
  end
end

local function hocher_tete(ch)
  if ch == nil then return end
  GROUND:CharSetAnim(ch, 'Nod', false)
  GAME:WaitFrames(28)
  GROUND:CharSetAnim(ch, 'Idle', true)
end

local function secouer_tete(ch, dir_base)
  if ch == nil then return end
  local g = Direction.UpLeft or Direction.Left
  local d = Direction.UpRight or Direction.Right
  if dir_base == Direction.Right then
    g = Direction.UpRight or Direction.Up
    d = Direction.DownRight or Direction.Down
  elseif dir_base == Direction.Left then
    g = Direction.UpLeft or Direction.Up
    d = Direction.DownLeft or Direction.Down
  elseif dir_base == Direction.Down then
    g = Direction.DownLeft or Direction.Left
    d = Direction.DownRight or Direction.Right
  end
  tourner_instant(ch, g); GAME:WaitFrames(6)
  tourner_instant(ch, d); GAME:WaitFrames(6)
  tourner_instant(ch, g); GAME:WaitFrames(6)
  tourner_instant(ch, d); GAME:WaitFrames(6)
  tourner_instant(ch, dir_base); GAME:WaitFrames(14)
end

local function expliquer_en_gestes(ch, dir_base)
  if ch == nil then return end
  tourner_instant(ch, dir_base)
  GROUND:CharSetAnim(ch, 'Idle', true)
  GAME:WaitFrames(10)
  GROUND:CharSetAnim(ch, 'Nod', false)
  GAME:WaitFrames(24)
  GROUND:CharSetAnim(ch, 'Idle', true)
  GAME:WaitFrames(14)
  GROUND:CharSetAnim(ch, 'Nod', false)
  GAME:WaitFrames(24)
  GROUND:CharSetAnim(ch, 'Idle', true)
  GAME:WaitFrames(18)
end

local function parler(personnage, emotion, texte)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion(emotion or 'Normal')
  UI:WaitShowDialogue(texte)
end

local function penser_heros(hero, nom_connu, emotion, texte)
  if nom_connu then
    UI:SetSpeaker(hero, false)
  elseif hero ~= nil and hero.CurrentForm ~= nil and hero.CurrentForm.Species ~= nil then
    UI:SetSpeaker('[color=#009CFF]???[color]', false, hero.CurrentForm.Species, hero.CurrentForm.Form, hero.CurrentForm.Skin, hero.CurrentForm.Gender)
  else
    UI:SetSpeaker(hero, false)
  end
  UI:SetSpeakerEmotion(emotion or 'Normal')
  UI:WaitShowDialogue(texte)
end

local function texte_noir(texte)
  UI:ResetSpeaker()
  if UI.WaitShowVoiceOver ~= nil then
    UI:WaitShowVoiceOver(texte, -1)
  else
    UI:WaitShowDialogue(texte)
  end
end

local function est_feminin(personnage)
  if personnage == nil or Gender == nil then return false end
  return personnage.CurrentForm ~= nil and personnage.CurrentForm.Gender == Gender.Female
end

local function nom_espece_heros(hero)
  if _DATA ~= nil and _DATA.GetMonster ~= nil and hero ~= nil and hero.CurrentForm ~= nil and hero.CurrentForm.Species ~= nil then
    local ok, mon = pcall(function() return _DATA:GetMonster(hero.CurrentForm.Species) end)
    if ok and mon ~= nil and mon.Name ~= nil then
      return mon.Name:ToLocal()
    end
  end
  return "Pokémon"
end

local function demander_prenom_heros(hero)
  local defaut = nom_espece_heros(hero)
  if defaut == "Pokémon" then defaut = "Alex" end
  local prenom = ""
  local valide = false
  while not valide do
    UI:ResetSpeaker()
    if UI.NameMenu ~= nil then
      UI:NameMenu("Quel est ton prénom ?", "Entre le prénom de ton personnage.", 60)
      UI:WaitForChoice()
      prenom = UI:ChoiceResult()
    else
      prenom = defaut
    end
    if prenom == nil or prenom == "" then
      prenom = defaut
    end
    if UI.ChoiceMenuYesNo ~= nil then
      UI:ChoiceMenuYesNo("Le prénom [color=#009CFF]" .. prenom .. "[color] te convient-il ?", false)
      UI:WaitForChoice()
      valide = UI:ChoiceResult()
    else
      valide = true
    end
  end
  local hero_data = GAME:GetPlayerPartyMember(GAME:GetTeamLeaderIndex())
  if hero_data ~= nil then
    if GAME.SetCharacterNickname ~= nil then
      GAME:SetCharacterNickname(hero_data, prenom)
    else
      hero_data.Nickname = prenom
    end
  end
  return prenom
end

local function lancer_retour_inverse()
  SV.Destiny = SV.Destiny or {}
  if GAME.GivePlayerItem ~= nil and GAME.GetPlayerBagCount ~= nil and GAME:GetPlayerBagCount() == 0 then
    GAME:GivePlayerItem('berry_oran', 2)
    GAME:GivePlayerItem('food_apple', 1)
  end
  SV.Destiny.RetrouvaillesFaites = true
  SV.Destiny.LostWoodTrip = 'retour'
  SV.Destiny.LostWoodRetourEchec = false
  if GAME.UnlockDungeon ~= nil then GAME:UnlockDungeon('lost_wood') end
  local stakes = (RogueEssence ~= nil and RogueEssence.Data ~= nil and RogueEssence.Data.GameProgress ~= nil)
    and RogueEssence.Data.GameProgress.DungeonStakes.Risk or 0
  if GAME.EnterDungeon ~= nil then
    GAME:EnterDungeon('lost_wood', 0, 6, 0, stakes, true, false)
  else
    GAME:EnterZone('lost_wood', 0, 6, 0)
  end
end

function zrv2_zone_reveil_nuit.Init(map)
  if map ~= nil and RogueEssence ~= nil and RogueEssence.Dungeon ~= nil and RogueEssence.Dungeon.BaseMap ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.LostWoodTrip == 'rencontre' or SV.Destiny.LostWoodTrip == 'retour' then
    equipe_scene.RestaurerHeros()
    if GROUND.RefreshPlayer ~= nil then GROUND:RefreshPlayer() end
    local hero = CH('PLAYER')
    if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
      equipe_scene.Partenaire(ENTREE_FORET_X, ENTREE_FORET_Y, Direction.Up)
    end
  else
    if CH('Teammate1') ~= nil then GROUND:Hide('Teammate1') end
  end
end

-- 1) Sommeil brumeux du héros juste avant la scène du partenaire
function zrv2_zone_reveil_nuit.CinematiqueSommeilHeros()
  local hero = CH('PLAYER')
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  if SOUND.StopBGM ~= nil then SOUND:StopBGM() end
  GAME:FadeOut(false, 1)

  if CH('Teammate1') ~= nil then GROUND:Hide('Teammate1') end

  if hero ~= nil then
    hero.CollisionDisabled = true
    GROUND:TeleportTo(hero, HEROS_SOMMEIL_X, HEROS_SOMMEIL_Y, Direction.Right)
    GROUND:CharSetAnim(hero, 'Laying', true)
  end
  GAME:MoveCamera(HEROS_SOMMEIL_X, HEROS_SOMMEIL_Y - 16, 1, false)

  GAME:WaitFrames(40)
  UI:WaitShowDialogue("… Où suis-je… ?")
  UI:WaitShowDialogue("Qui suis-je… ?")

  GAME:FadeIn(90)
  GAME:WaitFrames(35)
  UI:WaitShowDialogue("Tout me semble si flou…")
  GAME:WaitFrames(20)
  UI:WaitShowDialogue("J'ai sommeil…")
  GAME:WaitFrames(30)

  GAME:FadeOut(false, 90)
  GAME:WaitFrames(30)

  if hero ~= nil then
    GROUND:CharEndAnim(hero)
    hero.CollisionDisabled = false
  end
  SV.Destiny.IntroReveilHerosFait = true
  GAME:CutsceneMode(false)
  if GAME.EnterGroundMap ~= nil then
    GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Home_Door')
  else
    GAME:EnterZone('destiny_cliff_tests', -1, 4, 0)
  end
end

-- 2) Cinématique de rencontre PMD (5-10 min) : héros muet en pensées (...), saisie du prénom,
--    lent travelling vers la montagne avec portrait émerveillé, choix multiples, pose finale
--    et narration blanche sur fond noir.
function zrv2_zone_reveil_nuit.CinematiqueRetrouvailles()
  equipe_scene.RestaurerHeros()
  if GROUND.RefreshPlayer ~= nil then GROUND:RefreshPlayer() end

  local hero = CH('PLAYER')
  local partenaire = CH('Teammate1')
  if partenaire == nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(ENTREE_FORET_X, ENTREE_FORET_Y, Direction.Up)
  end
  if hero == nil or partenaire == nil then
    GAME:FadeIn(20)
    print('[Destiny] Retrouvailles suspendues : héros ou partenaire absent, réserve préservée.')
    return
  end

  local part_fem = est_feminin(partenaire)
  local mot_petit = part_fem and "toute petite" or "tout petit"
  local mot_seul = part_fem and "toute seule" or "tout seul"
  local mot_pret = part_fem and "prête" or "prêt"
  local mot_content = part_fem and "contente" or "content"
  local pronom_lui = part_fem and "elle" or "lui"
  local nom_part = partenaire.GetDisplayName ~= nil and partenaire:GetDisplayName() or "Partenaire"
  local espece_heros = nom_espece_heros(hero)

  if SOUND.StopBGM ~= nil then SOUND:StopBGM() end
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GAME:FadeOut(false, 1)

  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  partenaire.CollisionDisabled = true
  GROUND:TeleportTo(hero, HEROS_SOMMEIL_X, HEROS_SOMMEIL_Y, Direction.Right)
  GROUND:CharSetAnim(hero, 'Laying', true)
  GROUND:TeleportTo(partenaire, ENTREE_FORET_X, ENTREE_FORET_Y, Direction.Up)
  GAME:MoveCamera(384, 348, 1, false)

  if UI.WaitShowTitle ~= nil then
    UI:WaitShowTitle("Clairière sous la montagne", 30)
    GAME:WaitFrames(50)
    UI:WaitHideTitle(30)
  end

  SOUND:PlayBGM("Wind.ogg", true)
  GAME:FadeIn(70)

  -- Acte I : Le partenaire sort de Lost Wood et découvre le héros endormi dans les fleurs
  GROUND:MoveToPosition(partenaire, 384, 424, false, 1)
  GROUND:CharSetAnim(partenaire, 'DeepBreath', false)
  GAME:WaitFrames(35)
  GROUND:CharSetAnim(partenaire, 'Idle', true)
  parler(partenaire, 'Sigh', "Pfiou… J'y suis arrivé… Sept étages d'affilée à travers [color=#69D98C]Lost Wood[color]…")
  parler(partenaire, 'Happy', "Mes jambes tremblent encore un peu, mais j'ai tenu bon jusqu'à la sortie !")

  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partenaire, 'exclaim', 1)
  GAME:WaitFrames(30)
  parler(partenaire, 'Surprised', "Hein… ? Attends une minute… Qu'est-ce qu'il y a là-bas, au milieu des fleurs ?!")

  GROUND:MoveToPosition(partenaire, HEROS_SOMMEIL_X + 34, HEROS_SOMMEIL_Y, false, 2)
  tourner_instant(partenaire, Direction.Left)
  parler(partenaire, 'Worried', "Mais… c'est quelqu'un d'évanoui ! En pleine nuit, dans un endroit pareil ?!")
  parler(partenaire, 'Shouting', "Hé ! Hé, tu m'entends ?! Réveille-toi, je t'en prie !")

  GAME:WaitFrames(30)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("(… Mmmh… J'entends une voix qui m'appelle de très loin…)")
  UI:WaitShowDialogue("(La brise est fraîche… et ce parfum d'herbe et d'embruns…)")

  GROUND:CharSetAnim(hero, 'Wake', false)
  GAME:WaitFrames(40)
  GROUND:CharSetAnim(hero, 'Idle', true)
  tourner(hero, Direction.Down)
  GAME:WaitFrames(18)
  tourner(hero, Direction.Right)
  GAME:WaitFrames(20)

  parler(partenaire, 'Sigh', "Ouf… ! Tu ouvres enfin les yeux ! Tu m'as fait une de ces frayeurs !")
  parler(partenaire, 'Worried', "Je t'ai trouvé complètement immobile dans la rosée en sortant de la forêt… Est-ce que tu arrives à tenir debout ?")

  penser_heros(hero, false, 'Pain', "(Ma tête tourne encore un peu… Où est-ce que j'ai bien pu atterrir… ?)")
  tourner(hero, Direction.DownLeft)
  GAME:WaitFrames(20)
  tourner(hero, Direction.DownRight)
  GAME:WaitFrames(20)
  SOUND:PlayBattleSE('EVT_Emote_Shock')
  GROUND:CharSetEmote(hero, 'shock', 1)
  GROUND:CharSetAnim(hero, 'Hop', false)
  GAME:WaitFrames(30)
  GROUND:CharSetAnim(hero, 'Idle', true)

  penser_heros(hero, false, 'Surprised', "(Hein… ?! Attends une seconde… Qu'est-ce que c'est que ces pattes ?!)")
  secouer_tete(hero, Direction.Down)
  penser_heros(hero, false, 'Surprised', "(Et cette silhouette… ?! Mais… je suis un " .. espece_heros .. " ?!)")
  penser_heros(hero, false, 'Worried', "(C'est impossible ! J'étais un être humain ! Pourquoi est-ce que j'ai l'apparence d'un Pokémon ?!)")

  -- Acte II : Le partenaire lui demande d'où il vient et son prénom (saisie joueur)
  SOUND:PlayBattleSE('EVT_Emote_Confused')
  GROUND:CharSetEmote(partenaire, 'question', 1)
  GAME:WaitFrames(30)
  tourner(hero, Direction.Right)
  parler(partenaire, 'Worried', "Euh… ça ne va vraiment pas ? Tu fixes tes pattes avec des yeux ronds comme si tu voyais un fantôme…")
  parler(partenaire, 'Normal', "Dis-moi… d'où est-ce que tu viens au juste ? Et comment es-tu arrivé tout seul de ce côté-ci de [color=#69D98C]Lost Wood[color] ?")

  penser_heros(hero, false, 'Worried', "(D'où je viens… ? Voyons, essaie de te concentrer…)")
  tourner(hero, Direction.Up)
  GAME:WaitFrames(35)
  penser_heros(hero, false, 'Sad', "(… Rien. Pas une image, pas un lieu, pas un seul visage… Tout mon passé se dérobe dans un brouillard complet.)")
  penser_heros(hero, false, 'Normal', "(La seule chose dont je sois absolument sûr, c'est que j'étais un être humain avant de m'endormir…)")
  tourner(hero, Direction.Right)
  penser_heros(hero, false, 'Normal', "(Bon… essayons de lui expliquer ça du mieux possible.)")

  -- Le héros ne parle pas : il mime/explique par de petits hochements et gestes en Idle
  expliquer_en_gestes(hero, Direction.Right)

  SOUND:PlayBattleSE('EVT_Emote_Shock')
  GROUND:CharSetEmote(partenaire, 'shock', 1)
  GROUND:CharSetAnim(partenaire, 'Hop', false)
  GAME:WaitFrames(28)
  GROUND:CharSetAnim(partenaire, 'Idle', true)
  parler(partenaire, 'Surprised', "QUOI ?!")
  parler(partenaire, 'Surprised', "Tu… tu dis que tu étais un être humain ?! Et que tu t'es réveillé ici transformé en Pokémon, sans aucun souvenir ?!")
  parler(partenaire, 'Stunned', "Euh… attends un peu… Une histoire pareille, normalement, je croirais tout de suite à une blague…")

  GROUND:CharSetEmote(hero, 'sweating', 1)
  GAME:WaitFrames(28)
  penser_heros(hero, false, 'Worried', "(Forcément… même moi, j'ai du mal à y croire…)")

  parler(partenaire, 'Worried', "… Et pourtant, tu as l'air tellement sincère. Tes yeux ne mentent pas, et tu tremblais vraiment en découvrant ton corps à l'instant.")
  parler(partenaire, 'Normal', "Tu ne te rappelles vraiment rien du tout de l'endroit d'où tu viens ?")

  secouer_tete(hero, Direction.Right)
  penser_heros(hero, false, 'Sad', "(Pas le moindre souvenir… C'est le vide complet.)")

  parler(partenaire, 'Worried', "Je vois… Ça doit être terrible de se réveiller ainsi sans repères…")
  parler(partenaire, 'Normal', "Et ton prénom ? Est-ce que tu te souviens au moins de comment tu t'appelles ?")

  GAME:WaitFrames(20)
  penser_heros(hero, false, 'Normal', "(Mon prénom… Oui ! Ça, au moins, c'est resté gravé en moi…)")
  penser_heros(hero, false, 'Normal', "(Je m'appelle…)")

  -- Saisie du prénom du héros par le joueur
  local prenom = demander_prenom_heros(hero)
  local nom_hero = hero.GetDisplayName ~= nil and hero:GetDisplayName() or ("[color=#009CFF]" .. prenom .. "[color]")

  hocher_tete(hero)
  GAME:WaitFrames(15)

  parler(partenaire, 'Surprised', nom_hero .. "… ? Tu t'appelles " .. nom_hero .. " ?")
  GROUND:CharSetAnim(partenaire, 'Hop', false)
  GAME:WaitFrames(25)
  GROUND:CharSetAnim(partenaire, 'Idle', true)
  parler(partenaire, 'Joyous', "C'est un joli prénom ! Vraiment, je trouve que ça te va super bien !")
  parler(partenaire, 'Happy', "Moi, je m'appelle " .. nom_part .. " ! Je suis très " .. mot_content .. " de faire ta connaissance, " .. nom_hero .. " !")

  hocher_tete(hero)
  penser_heros(hero, true, 'Happy', "(" .. nom_part .. "… Je ne sais pas encore pourquoi le destin m'a mené ici, mais son sourire me réchauffe déjà le cœur.)")

  -- Acte III : Marche du partenaire vers la montagne + lent mouvement de caméra + portrait émerveillé
  tourner(partenaire, Direction.Up)
  GAME:WaitFrames(20)
  parler(partenaire, 'Normal', "Hé, " .. nom_hero .. "… Maintenant que tu tiens debout, viens voir un peu par là.")
  parler(partenaire, 'Happy', "En débouchant des arbres tout à l'heure, j'en ai presque eu le souffle coupé… Regarde devant nous.")

  SOUND:FadeOutBGM(45)
  GAME:WaitFrames(30)
  SOUND:PlayBGM("Welcome to the World of Pokémon!.ogg", true)

  -- Le partenaire s'avance lentement vers le nord en direction de la montagne ;
  -- la caméra l'accompagne puis continue à monter très lentement vers la montagne et la lune.
  local marche_montagne_part = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, BELVEDERE_PART_X, BELVEDERE_PART_Y, false, 1)
    tourner_instant(partenaire, Direction.Up)
  end)
  local cam_suivi_part = TASK:BranchCoroutine(function()
    GAME:MoveCamera(384, 232, 95, false)
  end)
  TASK:JoinCoroutines({ marche_montagne_part, cam_suivi_part })

  -- La caméra glisse lentement vers la montagne et la pleine lune pendant que
  -- s'affiche la boîte de dialogue avec le portrait émerveillé (Inspired) du partenaire.
  local cam_pan_montagne = TASK:BranchCoroutine(function()
    GAME:MoveCamera(384, 120, 210, false)
  end)
  GAME:WaitFrames(35)
  parler(partenaire, 'Inspired', "Ouah… Regarde cette montagne immense au-dessus des flots… et la pleine lune qui couronne son sommet…")
  TASK:JoinCoroutines({ cam_pan_montagne })

  parler(partenaire, 'Inspired', "On dirait que la mer tout entière s'est changée en un chemin de lumière qui mène droit vers elle…")
  parler(partenaire, 'Inspired', "Depuis que je suis " .. mot_petit .. ", j'observe cette silhouette lointaine depuis ma falaise en rêvant du jour où j'irai voir ce qui se cache derrière ses nuages…")

  -- Le héros s'avance à son tour jusqu'au rivage nord aux côtés du partenaire
  local marche_hero_nord = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(hero, BELVEDERE_HEROS_X, BELVEDERE_HEROS_Y, false, 1)
    tourner_instant(hero, Direction.Up)
  end)
  local cam_duo_nord = TASK:BranchCoroutine(function()
    GAME:MoveCamera(384, 134, 80, false)
  end)
  TASK:JoinCoroutines({ marche_hero_nord, cam_duo_nord })
  GAME:WaitFrames(30)

  penser_heros(hero, true, 'Inspired', "(… C'est à couper le souffle. La lune, l'océan, la montagne… Tout semble suspendu hors du temps.)")
  penser_heros(hero, true, 'Normal', "(Et quand je regarde " .. nom_part .. ", ses yeux brillent autant que le reflet de la lune sur l'eau…)")

  -- Acte IV : Le rêve du partenaire — former une équipe d'explorateurs (longue discussion PMD)
  parler(partenaire, 'Normal', "Tu sais, " .. nom_hero .. "… Si j'ai traversé [color=#69D98C]Lost Wood[color] " .. mot_seul .. " en pleine nuit, ce n'était pas sur un simple coup de tête.")
  parler(partenaire, 'Happy', "J'ai un rêve… Un rêve qui ne me quitte pas d'une semelle, jour après jour.")
  parler(partenaire, 'Inspired', "Mon plus grand rêve… c'est de former ma propre équipe d'explorateurs !")

  tourner(hero, Direction.Right)
  SOUND:PlayBattleSE('EVT_Emote_Confused')
  GROUND:CharSetEmote(hero, 'question', 1)
  GAME:WaitFrames(25)
  penser_heros(hero, true, 'Normal', "(Une équipe d'explorateurs… ?)")

  tourner(partenaire, Direction.Left)
  parler(partenaire, 'Joyous', "Oui ! Dans ce monde, il existe une multitude de donjons mystères et de contrées que personne n'a encore jamais réussi à cartographier !")
  parler(partenaire, 'Inspired', "Des ruines englouties par le temps, des forêts brumeuses, des sommets au-delà des nuages, des trésors oubliés et des légendes anciennes…")
  parler(partenaire, 'Happy', "Les équipes d'explorateurs partent lever le voile sur ces mystères, mais pas seulement ! Elles volent aussi au secours des Pokémon égarés ou en détresse !")

  tourner(partenaire, Direction.Up)
  GAME:WaitFrames(20)
  parler(partenaire, 'Worried', "Pour être tout à fait honnête avec toi… tout à l'heure, sur le chemin devant l'entrée de [color=#69D98C]Lost Wood[color], je n'en menais vraiment pas large.")
  parler(partenaire, 'Sad', "J'avais le cœur serré. Je me demandais : « Est-ce que quelqu'un comme moi est vraiment " .. mot_pret .. " à devenir explorateur ? Et si j'échouais dès le premier pas ? »")
  parler(partenaire, 'Normal', "Certains Pokémon plus aguerris pensent parfois que rêver d'aventure ne suffit pas quand on manque encore d'expérience…")

  tourner(hero, Direction.Up)
  penser_heros(hero, true, 'Worried', "(Alors " .. nom_part .. " aussi a connu le doute avant d'entrer dans cette forêt…)")
  penser_heros(hero, true, 'Normal', "(Et malgré sa peur, " .. pronom_lui .. " a trouvé le courage d'aller jusqu'au bout des sept étages…)")

  tourner(partenaire, Direction.Left)
  parler(partenaire, 'Happy', "Mais je me suis dit que si je faisais demi-tour sans même essayer, je le regretterais toute ma vie !")
  parler(partenaire, 'Inspired', "Et regarde le résultat : j'ai franchi [color=#69D98C]Lost Wood[color], j'ai découvert ce panorama incroyable… et surtout, ma route a croisé la tienne, " .. nom_hero .. " !")
  parler(partenaire, 'Joyous', "Je suis sûr qu'une vraie équipe d'explorateurs, ce n'est pas juste chercher des trésors : c'est avancer à deux, se soutenir quand le chemin fait peur et ne jamais abandonner quelqu'un derrière soi !")

  tourner(hero, Direction.Right)
  hocher_tete(hero)
  penser_heros(hero, true, 'Happy', "(Ses paroles sont tellement sincères… On sent que ce rêve vient du plus profond de son cœur.)")

  -- Acte V : Question du partenaire sur l'avenir du héros + choix multiples façon Donjon Mystère
  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partenaire, 'exclaim', 1)
  GAME:WaitFrames(25)
  parler(partenaire, 'Stunned', "Oh ! Mais écoute-moi parler de moi sans m'arrêter depuis tout à l'heure !")
  parler(partenaire, 'Worried', "C'est de ta situation qu'on devrait s'inquiéter d'abord ! Tu n'as plus aucun souvenir et tu te retrouves dans un monde que tu connais à peine…")
  parler(partenaire, 'Normal', "Dis-moi, " .. nom_hero .. "… Est-ce que tu as un endroit où aller ? Qu'est-ce que tu comptes faire maintenant ?")

  UI:ResetSpeaker()
  local choix_heros = 1
  if UI.BeginChoiceMenu ~= nil then
    UI:BeginChoiceMenu(
      "Que répondre à " .. nom_part .. " ?",
      {
        "Je sais pas…",
        "Je verrai bien…",
        "J'ai des projets haha… ouais t'en fais pas !",
        "Je suis complètement perdu…",
      },
      1,
      1
    )
    UI:WaitForChoice()
    choix_heros = UI:ChoiceResult() or 1
  end

  if choix_heros == 1 then
    penser_heros(hero, true, 'Worried', "(Je sais pas… Franchement, je n'en ai pas la moindre idée…)")
    tourner(hero, Direction.Down)
    GAME:WaitFrames(15)
    secouer_tete(hero, Direction.Right)
    parler(partenaire, 'Worried', "Tu ne sais pas du tout, hein… ? En même temps, sans tes souvenirs et au beau milieu de la nuit, comment pourrais-tu savoir où aller ?")
  elseif choix_heros == 2 then
    penser_heros(hero, true, 'Normal', "(Je verrai bien… Autant avancer au fil du vent et improviser, non ?)")
    expliquer_en_gestes(hero, Direction.Right)
    SOUND:PlayBattleSE('EVT_Emote_Sweating')
    GROUND:CharSetEmote(partenaire, 'sweating', 1)
    GAME:WaitFrames(25)
    parler(partenaire, 'Stunned', "« Je verrai bien… » ?! Tu me réponds ça le plus tranquillement du monde alors que tu viens d'apprendre que tu es devenu un Pokémon ?!")
    parler(partenaire, 'Sigh', "Ça veut surtout dire que tu n'as aucun endroit où dormir ni où aller, pas vrai ?")
  elseif choix_heros == 3 then
    penser_heros(hero, true, 'Happy', "(J'ai des projets haha… ouais, t'en fais pas ! Pas besoin de l'inquiéter pour moi !)")
    GROUND:CharSetAnim(hero, 'Pose', false)
    GAME:WaitFrames(28)
    GROUND:CharSetAnim(hero, 'Idle', true)
    tourner(hero, Direction.UpLeft)
    SOUND:PlayBattleSE('EVT_Emote_Sweating')
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GAME:WaitFrames(30)
    parler(partenaire, 'Stunned', "Euh…")
    parler(partenaire, 'Sigh', "Pourquoi est-ce que tu détournes le regard en transpirant à grosses gouttes juste après avoir pris la pose ?!")
    parler(partenaire, 'Happy', "Haha, ça se voit comme le nez au milieu de la figure que tu dis ça uniquement pour ne pas m'inquiéter ! En réalité, tu n'as nulle part où aller, avoue !")
    tourner(hero, Direction.Right)
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GAME:WaitFrames(20)
  else
    penser_heros(hero, true, 'Sad', "(Je suis complètement perdu… Je ne sais même pas par où commencer.)")
    secouer_tete(hero, Direction.Right)
    parler(partenaire, 'Worried', "C'est bien normal que tu te sentes perdu… N'importe qui le serait à ta place.")
  end

  -- Acte VI : Proposition de suivre le partenaire jusqu'à Réverie Town, capitale des explorateurs
  GAME:WaitFrames(20)
  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partenaire, 'exclaim', 1)
  GROUND:CharSetAnim(partenaire, 'Hop', false)
  GAME:WaitFrames(25)
  GROUND:CharSetAnim(partenaire, 'Idle', true)

  parler(partenaire, 'Joyous', "Hé, mais j'y pense !")
  parler(partenaire, 'Happy', "Puisque tu n'as nulle part où aller pour l'instant… tu n'as qu'à me suivre !")
  parler(partenaire, 'Normal', "Ma maison se trouve juste de l'autre côté de [color=#69D98C]Lost Wood[color], en haut de la falaise.")
  parler(partenaire, 'Inspired', "Et tout au pied de cette falaise s'étend [color=#F5D27A]Réverie Town[color], la capitale des explorateurs !")
  parler(partenaire, 'Happy', "Des équipes venues des quatre coins du monde s'y retrouvent chaque jour, et toutes les nouvelles des terres lointaines finissent par y circuler !")
  parler(partenaire, 'Happy', "En venant avec moi jusqu'à [color=#F5D27A]Réverie Town[color], nous trouverons sûrement des indices sur qui tu es et sur ce qui t'est arrivé !")
  parler(partenaire, 'Worried', "Et puis… je ne pourrais jamais repartir l'esprit tranquille en te laissant ici tout seul dans la nuit. Qu'en dis-tu, " .. nom_hero .. " ?")

  -- Monologue intérieur du héros entre parenthèses (...) avant d'accepter d'un hochement de tête
  tourner(hero, Direction.Up)
  GAME:WaitFrames(25)
  penser_heros(hero, true, 'Normal', "([color=#F5D27A]Réverie Town[color]… la capitale des explorateurs…)")
  penser_heros(hero, true, 'Worried', "(C'est vrai que je n'ai aucun endroit où aller pour le moment…)")
  penser_heros(hero, true, 'Normal', "(Si je dois comprendre comment je suis arrivé ici et pourquoi j'ai été transformé en Pokémon, je ne découvrirai rien en restant immobile dans cette clairière.)")
  penser_heros(hero, true, 'Normal', "(Là-bas, au cœur de la capitale des explorateurs, quelqu'un détiendra peut-être le début d'une réponse…)")
  penser_heros(hero, true, 'Happy', "(Et puis… " .. nom_part .. " m'a tendu la patte sans hésiter une seule seconde. J'ai envie de lui faire confiance.)")

  tourner(hero, Direction.Right)
  GAME:WaitFrames(20)
  hocher_tete(hero)
  GAME:WaitFrames(15)
  expliquer_en_gestes(hero, Direction.Right)
  penser_heros(hero, true, 'Determined', "(C'est décidé : je vais suivre " .. nom_part .. " jusqu'à [color=#F5D27A]Réverie Town[color] !)")

  GROUND:CharSetAnim(partenaire, 'Hop', false)
  GAME:WaitFrames(22)
  GROUND:CharSetAnim(partenaire, 'Hop', false)
  GAME:WaitFrames(22)
  GROUND:CharSetAnim(partenaire, 'Idle', true)
  parler(partenaire, 'Joyous', "C'est vrai ?! Tu acceptes de venir avec moi ?!")
  parler(partenaire, 'Happy', "Youpi ! Tu ne le regretteras pas, " .. nom_hero .. ", je te le promets !")
  parler(partenaire, 'Normal', "Pour rejoindre la falaise puis [color=#F5D27A]Réverie Town[color], il va falloir retraverser les sept étages de [color=#69D98C]Lost Wood[color] dans le sens inverse…")
  parler(partenaire, 'Happy', "Mais à deux, en veillant l'un sur l'autre, on passera sans encombre jusqu'à la lumière du matin !")

  -- Acte VII : Pose finale devant le paysage nord + fondu noir + écriture blanche façon intro PMD
  tourner(partenaire, Direction.Up)
  tourner(hero, Direction.Up)
  GAME:MoveCamera(384, 132, 60, false)
  GAME:WaitFrames(25)

  parler(partenaire, 'Inspired', "Regarde encore un instant la montagne sous la pleine lune, " .. nom_hero .. "…")
  parler(partenaire, 'Joyous', "C'est ici que commence notre route ensemble : en avant vers [color=#F5D27A]Réverie Town[color] !")
  UI:ResetSpeaker()
  GAME:WaitFrames(20)

  -- Le héros et le partenaire font la pose ensemble devant le panorama nord
  GROUND:CharSetAnim(hero, 'Pose', true)
  GROUND:CharSetAnim(partenaire, 'Pose', true)
  GAME:WaitFrames(110)

  -- Fondu au noir lent + texte blanc centré sur fond noir façon Donjon Mystère
  SOUND:FadeOutBGM(120)
  GAME:FadeOut(false, 120)
  GAME:WaitFrames(70)

  texte_noir("Cette nuit-là, face à l'océan baigné par le clair de lune…")
  texte_noir("Une rencontre inattendue venait de sceller le destin\nde deux compagnons au pied de la montagne lointaine.")
  texte_noir("Ils ignoraient encore tout des mystères et des aventures\nqui les attendaient par-delà l'horizon…")
  texte_noir("Et c'est ainsi qu'une toute nouvelle histoire commença.")
  GAME:WaitFrames(60)

  GROUND:CharEndAnim(hero)
  GROUND:CharEndAnim(partenaire)
  hero.CollisionDisabled = false
  partenaire.CollisionDisabled = false
  GAME:CutsceneMode(false)
  lancer_retour_inverse()
end

-- 3) Reprise en cas d'échec lors de la traversée inverse
function zrv2_zone_reveil_nuit.SceneEchecRetour()
  equipe_scene.RestaurerHeros()
  if GROUND.RefreshPlayer ~= nil then GROUND:RefreshPlayer() end

  local hero = CH('PLAYER')
  local partenaire = CH('Teammate1')
  if partenaire == nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(396, 420, Direction.Left)
  end

  GAME:CutsceneMode(true)
  if hero ~= nil then GROUND:TeleportTo(hero, 372, 420, Direction.Right) end
  if partenaire ~= nil then
    AI:DisableCharacterAI(partenaire)
    GROUND:TeleportTo(partenaire, 396, 420, Direction.Left)
  end
  GAME:MoveCamera(384, 404, 1, false)
  SOUND:PlayBGM("Welcome to the World of Pokémon!.ogg", true)
  GAME:FadeIn(35)

  if partenaire ~= nil then
    parler(partenaire, 'Worried', "Le sentier nous a repoussés cette fois… Reprenons notre souffle un instant.")
    parler(partenaire, 'Happy', "À deux, nous finirons par passer ! Retraversons [color=#69D98C]Lost Wood[color] en sens inverse jusqu'à la falaise !")
    if hero ~= nil then
      hocher_tete(hero)
      penser_heros(hero, true, 'Determined', "(Ne lâchons rien. La sortie vers la falaise et [color=#F5D27A]Réverie Town[color] est au bout de la forêt !)")
    end
  else
    UI:ResetSpeaker()
    UI:WaitShowDialogue("Reprenons le chemin du retour à travers [color=#69D98C]Lost Wood[color].")
  end

  SOUND:FadeOutBGM(30)
  GAME:FadeOut(false, 35)
  GAME:CutsceneMode(false)
  lancer_retour_inverse()
end

function zrv2_zone_reveil_nuit.PlotScripting()
  SV.Destiny = SV.Destiny or {}

  if not SV.Destiny.IntroReveilHerosFait and not SV.Destiny.PartenaireParti and SV.Destiny.LostWoodTrip == nil then
    zrv2_zone_reveil_nuit.CinematiqueSommeilHeros()
    return
  end

  if SV.Destiny.LostWoodTrip == 'rencontre' and not SV.Destiny.RetrouvaillesFaites then
    zrv2_zone_reveil_nuit.CinematiqueRetrouvailles()
    return
  end

  if SV.Destiny.RetrouvaillesFaites and SV.Destiny.LostWoodTrip == 'retour' and SV.Destiny.LostWoodRetourEchec then
    zrv2_zone_reveil_nuit.SceneEchecRetour()
    return
  end

  GAME:FadeIn(20)
end

function zrv2_zone_reveil_nuit.Enter(map)
  zrv2_zone_reveil_nuit.PlotScripting()
end

function zrv2_zone_reveil_nuit.Exit(map) end
function zrv2_zone_reveil_nuit.Update(map) end
function zrv2_zone_reveil_nuit.GameSave(map) end
function zrv2_zone_reveil_nuit.GameLoad(map)
  zrv2_zone_reveil_nuit.PlotScripting()
end

return zrv2_zone_reveil_nuit
