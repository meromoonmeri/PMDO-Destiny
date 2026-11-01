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
     Pendant la rencontre, le héros ne prononce aucun mot : il répond par ses
     orientations, ses émotes et quelques pas. Le partenaire formule les
     questions, lit ces gestes à voix haute et porte seul le dialogue.
     Retour : le segment inverse de Lost Wood ramène le duo vers la falaise,
     cette fois au jour. Échec du retour : bref rappel, puis nouvelle
     tentative en duo.
     Textes originaux PMD Destiny. Transitions et cadrage testés sur un banc
     moteur avec sorties forcées ; parcours complet des étages non testé.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local reveil_nuit = {}

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

-- Le héros reste muet pendant toute la rencontre. Ses réponses sont donc
-- composées uniquement d'orientations et d'émotes déjà utilisées par PMDO :
-- regarder autour de soi, secouer la tête, approuver ou marquer l'inquiétude.
local function hero_geste(hero, geste)
  UI:ResetSpeaker()
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(30)
  elseif geste == 'non' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(16)
  elseif geste == 'oui' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(9)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(10)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 5)
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 5)
    GAME:WaitFrames(16)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 8)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
    GAME:WaitFrames(22)
  elseif geste == 'montagne' then
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
    GAME:WaitFrames(38)
  elseif geste == 'foret' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 8)
    GAME:WaitFrames(34)
  elseif geste == 'inquiet' then
    GROUND:CharSetEmote(hero, 'sweating', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 8)
    GAME:WaitFrames(38)
  elseif geste == 'surpris' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    GROUND:CharSetEmote(hero, 'shock', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(32)
  elseif geste == 'ecoute' then
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 7)
    GAME:WaitFrames(30)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 7)
    GAME:WaitFrames(18)
  elseif geste == 'determine' then
    SOUND:PlayBattleSE('EVT_Emote_Exclaim')
    GROUND:CharSetEmote(hero, 'exclaim', 1)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 6)
    GAME:WaitFrames(26)
  elseif geste == 'remerciement' then
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 6)
    GAME:WaitFrames(20)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 6)
    GAME:WaitFrames(18)
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
  GAME:WaitFrames(35)
  UI:WaitShowVoiceOver("[i]Où suis-je…", -1)
  GAME:WaitFrames(20)
  UI:WaitShowVoiceOver("[i]Qui suis-je…", -1)
  GAME:WaitFrames(20)
  UI:WaitShowVoiceOver("[i]Tout me semble si flou…", -1)
  GAME:WaitFrames(20)
  UI:WaitShowVoiceOver("[i]J’ai sommeil…", -1)
  GAME:WaitFrames(35)

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
  SV.Destiny.LostWoodRetourEchec = false
  SOUND:FadeOutBGM(60)
  GAME:FadeOut(false, 60)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  -- Segment 1 : les sept générateurs d'étage dans l'ordre inverse (7 → 1).
  GAME:EnterDungeon('lost_wood', 1, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
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
      UI:SetSpeaker(partner)
      UI:SetSpeakerEmotion("Worried")
      UI:WaitShowDialogue("Le sentier nous a repoussés cette fois. On reprend notre souffle… puis on repart ensemble.")
      UI:SetSpeakerEmotion("Happy")
      UI:WaitShowDialogue("Nous savons maintenant comment nous aider. [color=#69D98C]Lost Wood[color] ne nous séparera pas.")
      lancer_retour()
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
    UI:SetSpeaker(partner)
    UI:SetSpeakerEmotion(emotion)
    UI:WaitShowDialogue(texte)
  end
  local function geste(nom)
    hero_geste(hero, nom)
  end

  -- Il aperçoit le héros, quitte le chemin et s'approche.
  if points.zrv then
    dire("Happy", "Je l’ai fait… [color=#69D98C]Lost Wood[color], sept étages, et me voilà enfin dans la prairie.")
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
    dire("Normal", "Le vent est tombé d’un coup. On n’entend plus que la mer… attends. Là, dans les fleurs !")
  else
    dire("Happy", "Je l’ai fait… [color=#69D98C]Lost Wood[color], sept étages, et me voilà enfin dans la clairière.")
    dire("Normal", "Le vent est tombé d’un coup. On n’entend plus que— attends. Là, dans l’herbe !")
  end
  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partner, "exclaim", 1)
  dire("Worried", "Hé ! Tu m’entends ? Tu es blessé ?")
  -- Pendant les derniers pas, la caméra remonte du cadre d'approche vers
  -- le cadre de dialogue : les pentes de la montagne et le ciel nocturne
  -- occupent alors le haut de l'image, au-dessus du duo.
  local travelling_approche = nil
  if points.zrv then
    travelling_approche = lancer_camera(points.camera_x, points.camera_y, 110)
  end
  GROUND:MoveToPosition(partner, points.partenaire_pres_x, points.partenaire_pres_y, false, 1)
  GROUND:CharAnimateTurnTo(partner, Direction.Left, 6)
  attendre_camera(travelling_approche)
  GAME:WaitFrames(20)
  dire("Worried", "Tu es inconscient. D’accord… doucement. Personne ne te laissera passer la nuit seul dans cet état.")
  dire("Normal", "Allez. Reviens vers moi. Ouvre les yeux, tout doucement.")
  GAME:WaitFrames(40)

  -- Réveil du héros : aucun mot, seulement le regard et le corps qui
  -- découvrent la clairière comme s'ils la voyaient pour la première fois.
  GROUND:CharSetAnim(hero, 'Wake', false)
  GAME:WaitFrames(35)
  GROUND:CharEndAnim(hero)
  geste('autour')
  geste('question')
  dire("Sigh", "Ah… merci. Tu m’as fait une de ces peurs. Reste tranquille encore un instant ; la tête te tourne peut-être.")
  dire("Normal", "Je t’ai trouvé étendu dans cette prairie. Moi, je ressors à l’instant du donjon dont le sentier s’ouvre au sud, derrière nous. Ici, on l’appelle [color=#69D98C]Lost Wood[color].")
  geste('question')
  dire("Normal", "Ce nom ne te dit rien ? C’est une forêt-donjon : sept étages dont les salles, les couloirs et les escaliers ne se présentent jamais tout à fait de la même manière.")
  geste('foret')
  dire("Normal", "Tu ne connaissais pas cet endroit avant de te réveiller, alors. Au moins, voilà une première chose établie.")
  dire("Worried", "Tu sais comment tu t’appelles ?")
  geste('non')
  dire("Worried", "Et d’où tu viens ? Il y a un foyer, une équipe, quelqu’un qui devrait s’inquiéter pour toi ?")
  geste('non')
  dire("Normal", "D’accord. On ne tire pas sur une porte fermée ; ta mémoire s’ouvrira si elle le peut. Et si les mots ne viennent pas, réponds-moi par gestes. Je saurai écouter autrement.")
  geste('ecoute')
  dire("Normal", "Tu relèves la tête… Tu as entendu quelque chose pendant que tu dormais ?")
  geste('oui')
  dire("Normal", "Une voix ?")
  geste('oui')
  geste('ecoute')
  -- Le souvenir du rêve est entendu par le joueur seul : aucun portrait et
  -- aucune parole du héros. Le partenaire ne retient que son geste.
  UI:ResetSpeaker()
  UI:WaitShowVoiceOver("[i]« Retrouve le chemin que tu as perdu…[br]nos routes finiront par se rejoindre. »", -0.38)
  geste('inquiet')
  dire("Normal", "Tu t’es figé, comme si le rêve revenait. Gardons cette voix comme on garde une étoile entre les nuages : ce n’est pas encore une carte, mais c’est déjà une direction.")
  dire("Normal", "Pour l’instant, laisse tes yeux apprivoiser la nuit. Restons face à la mer ; de ce promontoire, l’horizon entier se laisse deviner.")

  -- Déplacement lent vers le point de vue. Sur la prairie ZRV2, la caméra
  -- bascule en même temps vers le panorama : lune, sommet et mer dominent
  -- le cadre pendant que le duo se place tout en bas, face au nord.
  local travelling_panorama = nil
  if points.zrv then
    travelling_panorama = lancer_camera(points.camera_panorama_x,
      points.camera_panorama_y, 180)
  end
  GROUND:MoveToPosition(partner, points.vue_x, points.vue_y, false, 1)
  GROUND:MoveToPosition(hero, points.vue_x - 20, points.vue_y, false, 1)
  if points.zrv then
    attendre_camera(travelling_panorama)
  else
    GAME:MoveCamera(points.camera_x, points.camera_y, 45, false)
  end
  GAME:WaitFrames(45)
  GROUND:CharAnimateTurnTo(partner, Direction.Up, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
  GAME:WaitFrames(30)

  -- Le partenaire parle ; le héros répond par le regard, une hésitation ou
  -- un signe de tête. Chaque interprétation est formulée par le partenaire.
  dire("Normal", "Tu vois la grande silhouette qui se dresse au-delà de la mer et ferme l’horizon ?")
  -- La question est posée dans le panorama. Pendant que le héros lève la
  -- tête et que le partenaire répond, la caméra redescend lentement vers
  -- le cadre de dialogue, sans perdre le haut des pentes ni le ciel.
  local retour_camera = nil
  if points.zrv then
    retour_camera = lancer_camera(points.camera_x, points.camera_y, 150)
  end
  geste('montagne')
  dire("Happy", "C’est la montagne. Le jour, on distingue ses arêtes, les forêts accrochées à ses pentes, parfois un filet d’eau qui brille entre les pierres. La nuit, elle ne garde que cette ligne immense.")
  attendre_camera(retour_camera)
  geste('question')
  dire("Normal", "Tu cherches un chemin du regard ? Moi aussi, depuis des années. S’il existe un passage jusqu’à sa cime, personne par ici ne peut encore le décrire d’un bout à l’autre.")
  -- Dérive presque immobile pendant l'évocation du rêve : le cadre glisse
  -- de quelques pixels vers l'est et le nord, comme un regard qui suit la
  -- ligne de crête sans quitter les deux personnages.
  local derive_reve = nil
  if points.zrv then
    derive_reve = lancer_camera(points.camera_x + 16, points.camera_y - 8, 300)
  end
  dire("Normal", "Je me demande ce qui se dérobe derrière : une autre vallée, une mer, des villages que nos cartes n’ont jamais nommés… L’inconnu a parfois la forme exacte d’une montagne.")
  geste('question')
  dire("Happy", "Oui, c’est mon rêve. Pas seulement grimper là-haut pour raconter que je l’ai fait. Je veux comprendre les sentiers, les rivières, les cols et les endroits où une équipe peut reprendre souffle.")
  dire("Normal", "Je voudrais tracer une carte assez fidèle pour qu’un voyageur égaré retrouve sa route, et assez honnête pour avouer ce qu’elle ignore encore.")
  geste('oui')
  dire("Happy", "Une carte ne sert à rien si elle demeure roulée au fond d’un sac. Elle doit passer de patte en patte et rendre le chemin un peu moins solitaire.")
  attendre_camera(derive_reve)

  dire("Worried", "Pourtant, quand je suis arrivé devant [color=#69D98C]Lost Wood[color], mes pattes ont hésité. Sept étages… Je me demandais si j’étais assez fort, assez patient, assez lucide pour les traverser seul.")
  geste('surpris')
  dire("Normal", "Oui, même après tout ce beau discours. J’ai failli rebrousser chemin à l’orée. Puis je me suis dit que la peur pouvait marcher avec moi ; elle n’avait pas à choisir la direction.")
  dire("Normal", "La forêt m’a appris des choses simples : regarder avant d’avancer, garder de quoi se soigner, et reconnaître quand un couloir vaut mieux qu’une salle pleine d’ennemis.")
  geste('oui')
  dire("Happy", "Tu retiens vite, on dirait. Retiens surtout ceci : le courage n’est pas l’absence de crainte. C’est un pas fait proprement, puis un autre.")

  -- Retour tout aussi lent au centre du promontoire pendant que le
  -- partenaire explique ce qu'être explorateur signifie pour lui.
  local retour_centre = nil
  if points.zrv then
    retour_centre = lancer_camera(points.camera_x, points.camera_y, 300)
  end
  dire("Normal", "Devenir explorateur, pour moi, ce n’est pas collectionner les exploits. C’est pouvoir répondre lorsqu’un appel vient d’un endroit où presque personne n’ose aller.")
  dire("Worried", "Imagine un Pokémon égaré dans la montagne, blessé, incapable de reconnaître la descente. Je voudrais être de ceux qui savent le retrouver et le ramener auprès des siens.")
  geste('question')
  dire("Normal", "Même si je ne le connais pas ? Oui. On secourt d’abord ; les présentations attendront le retour, autour d’un feu, quand tout le monde respirera de nouveau.")
  geste('remerciement')
  dire("Happy", "Ne me remercie pas comme si je t’avais déjà ramené quelque part. Pour le moment, je t’ai seulement trouvé. C’est un commencement, pas une arrivée.")
  attendre_camera(retour_centre)

  dire("Happy", "Et il y a les découvertes : des passages que personne n’a relevés, des ruines qui gardent la trace d’expéditions anciennes, des trésors endormis sous la poussière.")
  geste('determine')
  dire("Normal", "Un trésor peut équiper une équipe, réparer un toit, remplir les réserves d’un village ou financer une mission de secours. Il prend de la valeur lorsqu’il repart vers les autres.")
  dire("Happy", "Et entre nous… soulever le couvercle d’un coffre après des jours de marche doit rester un plaisir d’enfant. Je ne compte pas faire semblant du contraire.")
  geste('oui')
  dire("Happy", "Les rencontres et les détours font aussi partie de la découverte. Parfois, le plus précieux ne tient pas dans un coffre ; il tient dans la route qui nous y a conduits.")

  dire("Worried", "Mais un explorateur doit également savoir renoncer. Mettre son équipe en danger par orgueil n’a rien d’héroïque.")
  geste('question')
  dire("Normal", "Comment décider ? On regarde les forces qui restent, les objets, la nourriture, les blessures et le chemin déjà parcouru. On ne confond jamais ténacité et entêtement.")
  dire("Normal", "À deux, on peut se signaler ce que l’autre ne voit pas. Un geste franc vaut mieux qu’un silence qui laisse le danger approcher.")

  geste('inquiet')
  dire("Worried", "Tu baisses la tête… Tu te demandes ce que tu pourrais apporter à une équipe, alors que tu ignores jusqu’à ton propre nom ?")
  geste('oui')
  dire("Normal", "Tu n’as pas à arriver avec un passé complet ni un talent déjà prouvé. On apprend en avançant. Ton regard, ta prudence et tes choix diront peu à peu qui tu es.")
  dire("Normal", "Et si tes souvenirs ne reviennent pas tout de suite, nous chercherons des indices sans faire de ta vie une énigme à résoudre avant demain. La voix de ton rêve sera notre premier fil.")

  dire("Normal", "Je ne vais pas te laisser dans cette prairie. Le chemin du retour traverse [color=#69D98C]Lost Wood[color] ; oui, cette même forêt dont je viens de sortir, et ses sept étages dans l’autre sens.")
  geste('foret')
  dire("Normal", "Tu ne la connais pas, alors écoute bien : les salles changent, les Pokémon sauvages y agissent tour après tour, et chaque escalier nous rapproche de la sortie si nous savons le chercher.")
  dire("Normal", "Cette fois, nous veillerons l’un sur l’autre. Soins, nourriture et capacités seront à ménager ; aucun combat ne mérite que nous y laissions toutes nos forces.")
  geste('inquiet')
  dire("Worried", "Tu crains de ralentir mon rêve ?")
  geste('oui')
  dire("Happy", "Alors écoute ma réponse : un rêve qui exige d’abandonner quelqu’un au bord du chemin n’est pas celui que je veux poursuivre.")
  dire("Normal", "Je ne te demande ni promesse ni confiance aveugle. Seulement ceci : veux-tu faire la route avec moi et découvrir, pas à pas, ce que nous pouvons devenir ?")
  geste('determine')
  dire("Happy", "C’est décidé, alors. Notre première expédition commence par un retour, et ce n’est pas le moins beau des commencements.")
  GROUND:MoveToPosition(hero, points.vue_x - 12, points.vue_y, false, 1)
  GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
  GAME:WaitFrames(20)
  dire("Happy", "Un jour, nous suivrons la ligne de cette montagne. Nous porterons secours, nous nommerons les passages, et nous partagerons ce que la route voudra bien nous confier.")
  dire("Normal", "Pour cette nuit, reprenons notre souffle. Quand nous repartirons, personne ne traversera [color=#69D98C]Lost Wood[color] seul.")

  -- Dernier regard vers la montagne, puis seconde traversée à deux. La
  -- caméra remonte une dernière fois vers le panorama et y reste pendant
  -- le fondu de départ : la nuit, la lune et la crête ferment la scène.
  local travelling_final = nil
  if points.zrv then
    travelling_final = lancer_camera(points.camera_panorama_x - 8,
      points.camera_panorama_y, 180)
  end
  GROUND:CharAnimateTurnTo(partner, Direction.UpRight, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.UpRight, 8)
  GAME:WaitFrames(60)
  attendre_camera(travelling_final)
  if points.zrv then GAME:WaitFrames(45) end
  GROUND:CharAnimateTurnTo(partner, Direction.Down, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.Down, 8)
  GAME:WaitFrames(30)

  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RetrouvaillesFaites = true
  SV.Destiny.LostWoodTrip = 'retour'
  SV.Destiny.LostWoodRetourEchec = false
  lancer_retour()
end

return reveil_nuit
