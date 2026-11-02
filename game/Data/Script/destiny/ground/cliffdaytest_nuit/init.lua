--[[ init.lua — Scène du partenaire (map cliffdaytest — version nuit)
     Enchaînement : fin du quiz → faille du rêve → prologue du héros endormi
     dans la prairie ZRV2 (zrv2_zone_reveil_nuit) → cette map, la nuit.
     Le partenaire (celui choisi et
     nommé dans le quiz) sort de sa maison, dépasse le croisement et hésite
     sur le chemin de l'est, devant l'entrée de Lost Wood, puis part seul.
     Après les retrouvailles, le retour inverse en duo aboutit sur
     cliffdaytest au jour. Le héros reste allongé jusqu'à la rencontre.
     Dialogues originaux Destiny. Réveil solo, retrouvailles et retour
     testés sur un banc moteur avec sorties forcées ; le parcours complet
     des étages reste à tester.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local cliffdaytest_nuit = {}
local SON_MER = 'Destiny_Falaise_Mer'
local garde_chemin_sud_en_cours = false
local invite_retour_aller_en_cours = false

local function demarrer_mer()
  -- La BGM « Cliff Camp.ogg » est portée par la carte ; cette boucle ajoute
  -- le ressac de la mer sous la musique pendant toute la visite.
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

-- ------------------------------------------------------------- map callbacks

function cliffdaytest_nuit.Init(map)
  -- Empêcher le cadre de déborder dans le vide aux limites de cette carte.
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  if SV.Destiny and SV.Destiny.FinaleDestiny then
    local hero = CH('PLAYER')
    local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
    equipe_scene.Suivre(partner, hero)
  end
end

function cliffdaytest_nuit.Enter(map)
  cliffdaytest_nuit.PlotScripting()
end

function cliffdaytest_nuit.Exit(map)
  arreter_mer()
end

function cliffdaytest_nuit.GarderCheminSud(joueur)
  if garde_chemin_sud_en_cours or joueur == nil then return end
  garde_chemin_sud_en_cours = true
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:CharAnimateTurnTo(joueur, Direction.Up, 8)
  UI:SetSpeaker(joueur)
  UI:SetSpeakerEmotion('Worried')
  UI:WaitShowDialogue('Non. Je ne vais pas me dégonfler.')
  UI:SetSpeakerEmotion('Determined')
  UI:WaitShowDialogue('Il faut que je sois courageux. Je dois traverser [color=#69D98C]Lost Wood[color].')
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Je peux souffler un instant, d’accord… mais pas fuir par le chemin du sud. L’entrée est à l’est.')
  UI:ResetSpeaker()
  -- Le partenaire remonte de lui-même vers le croisement nord-sud.
  GROUND:MoveToPosition(joueur, 720, 556, false, 1)
  GROUND:CharAnimateTurnTo(joueur, Direction.Right, 8)
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
  garde_chemin_sud_en_cours = false
end

function cliffdaytest_nuit.Update(map)
  -- Après une pause, se rapprocher du bord est ouvre le dialogue de reprise :
  -- le donjon n'est jamais relancé sans le choix explicite du joueur.
  if SV.Destiny and SV.Destiny.LostWoodTrip == 'pause_aller'
     and not invite_retour_aller_en_cours then
    local joueur, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
    if joueur and entree and joueur.Position.X >= entree.Position.X - 16
       and math.abs(joueur.Position.Y - entree.Position.Y) <= 24 then
      cliffdaytest_nuit.DemanderRetourAller()
      return
    end
    -- Le sentier vertical qui descend vers le sud ramènerait le partenaire
    -- loin de son objectif : il se ressaisit et remonte vers le croisement.
    if joueur and joueur.Position.Y >= 600
       and joueur.Position.X >= 670 and joueur.Position.X <= 785 then
      cliffdaytest_nuit.GarderCheminSud(joueur)
    end
  end
end

function cliffdaytest_nuit.GameSave(map)
end

function cliffdaytest_nuit.GameLoad(map)
  cliffdaytest_nuit.PlotScripting()
end

function cliffdaytest_nuit.PlotScripting()
  SV.Destiny = SV.Destiny or {}
  demarrer_mer()
  if SV.Destiny.RetourAccompli then
    if not SV.Destiny.FinaleDestiny then
      cliffdaytest_nuit.SceneRetour()
    elseif SV.Destiny.VisiteVille == 'en_route' then
      -- Reprendre la transition si elle a été interrompue après le retour.
      cliffdaytest_nuit.AllerEnVille()
    else
      GAME:FadeIn(20)
    end
    return
  end
  if SV.Destiny.LostWoodTrip == 'echec_aller' then
    cliffdaytest_nuit.SceneEchecPartenaire()
    return
  end
  if SV.Destiny.LostWoodTrip == 'pause_aller' or SV.Destiny.PartenaireParti then
    GAME:FadeIn(20)
    return
  end
  cliffdaytest_nuit.ScenePartenaire()
end

function cliffdaytest_nuit.LancerAller()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.LostWoodTrip = 'aller'
  SV.Destiny.LostWoodRetry = nil
  SV.Destiny.PartenaireParti = true
  SOUND:FadeOutBGM(60)
  arreter_mer()
  GAME:FadeOut(false, 60)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  GAME:EnterDungeon('lost_wood', 0, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
end

function cliffdaytest_nuit.DemanderRetourAller()
  if invite_retour_aller_en_cours then return end
  local partenaire, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
  if partenaire == nil or entree == nil then return end
  invite_retour_aller_en_cours = true
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 8)
  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Voici l’entrée de [color=#69D98C]Lost Wood[color].')
  UI:ChoiceMenuYesNo('Souhaitez-vous retourner dans Lost Wood ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    UI:SetSpeaker(partenaire)
    UI:SetSpeakerEmotion('Determined')
    UI:WaitShowDialogue('Allez… on y retourne. Cette fois, je vais jusqu’au bout !')
    invite_retour_aller_en_cours = false
    cliffdaytest_nuit.LancerAller()
    return
  end
  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Pas tout de suite. Je reviendrai vers l’entrée quand je serai prêt.')
  UI:ResetSpeaker()
  -- Reculer hors du seuil évite de rouvrir le menu à la frame suivante.
  GROUND:MoveToPosition(partenaire, entree.Position.X - 56, entree.Position.Y, false, 1)
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 8)
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
  invite_retour_aller_en_cours = false
end

function cliffdaytest_nuit.SceneEchecPartenaire()
  -- Le seuil oriental est le marqueur de sortie du chemin existant ; aucune
  -- carte n'est recréée. Le héros reste dans la réserve, donc hors du plan.
  local partenaire, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:TeleportTo(partenaire, entree.Position.X - 40, entree.Position.Y, Direction.Left)
  GROUND:CharSetAnim(partenaire, 'Laying', true)
  GAME:MoveCamera(entree.Position.X - 40, entree.Position.Y, 1, false)
  GAME:FadeIn(30)
  GAME:WaitFrames(30)
  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion('Worried')
  if SV.Destiny.LostWoodCause == 'ko' then
    UI:WaitShowDialogue('Aïe… Je suis devant l’entrée de [color=#69D98C]Lost Wood[color]…')
    UI:WaitShowDialogue('J’ai perdu connaissance dans la forêt. Il faut que je reprenne mon souffle.')
  else
    UI:WaitShowDialogue('Me voilà de retour devant [color=#69D98C]Lost Wood[color]. J’ai bien fait de rebrousser chemin.')
    UI:WaitShowDialogue('Renoncer pour se protéger, ce n’est pas la fin de l’aventure.')
  end
  GROUND:CharSetAnim(partenaire, 'Wake', false)
  GAME:WaitFrames(35)
  -- Une IdleAnim en boucle ignore les commandes ; revenir à l'action idle.
  GROUND:CharEndAnim(partenaire)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Je peux me reposer ici, puis essayer encore quand je serai prêt.')
  UI:WaitShowDialogue('Quand je me rapprocherai de l’entrée, à l’est, je déciderai si je repars dans la forêt.')
  UI:ResetSpeaker()
  SV.Destiny.LostWoodTrip = 'pause_aller'
  SV.Destiny.LostWoodRetry = 'aller'
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
end

-- -------------------------------------------------------- retour en duo

function cliffdaytest_nuit.AllerEnVille()
  SOUND:FadeOutBGM(45)
  arreter_mer()
  GAME:FadeOut(false, 45)
  GAME:CutsceneMode(false)
  -- La ville reste une carte distincte, dans sa zone d'origine.
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function cliffdaytest_nuit.AllerCliffJour()
  SOUND:FadeOutBGM(45)
  arreter_mer()
  GAME:FadeOut(false, 45)
  GAME:WaitFrames(20)
  GAME:CutsceneMode(false)
  GAME:EnterZone('destiny_cliff_tests', -1, 0, 0)
end

-- Compatibilité avec une sauvegarde déjà revenue sur la version nuit :
-- la scène d'arrivée se joue désormais sur la même falaise au jour.
function cliffdaytest_nuit.SceneRetour()
  cliffdaytest_nuit.AllerCliffJour()
end

-- ------------------------------------------------------- scène (hésitation)

function cliffdaytest_nuit.ScenePartenaire()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PrologueHeros = 'termine'
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  -- La carte joue Cliff Camp et le ressac ; Tiny Woods prendra le relais
  -- lorsque le partenaire entrera dans Lost Wood.

  -- Le héros est inconscient ailleurs : seul le partenaire choisi au quiz
  -- doit apparaître dans cette scène.
  GROUND:Hide('PLAYER')

  local partenaire = GAME:GetPlayerPartyMember(1)
  GROUND:SpawnerSetSpawn('Adagio', partenaire)
  partenaire = GROUND:SpawnerDoSpawn('Adagio')
  AI:DisableCharacterAI(partenaire)
  local porte, croisement, entree = MRKR('Pichu_Home_Door'), MRKR('Pichu_Crossroads'),
    MRKR('Dazzling_Exit_East')

  -- Sur cette carte, l'avant-plan contient aussi un morceau opaque du chemin.
  -- Pendant la marche seulement, le dessiner avec le sol : le décor reste
  -- identique mais ne masque plus le Pokémon. L'ordre natif est ensuite remis.
  local avant_plan, ordre_avant_plan
  local carte = _ZONE.CurrentGround
  for i = 0, carte.Layers.Count - 1 do
    local couche = carte.Layers[i]
    if couche.Name == 'Canopée — avant-plan' then
      avant_plan, ordre_avant_plan = couche, couche.Layer
      couche.Layer = DrawLayer.Normal
      break
    end
  end

  GROUND:TeleportTo(partenaire, porte.Position.X, porte.Position.Y, Direction.Down)
  -- Le cadre contient d'abord la porte et la jonction. Le partenaire les
  -- dépasse : son hésitation a lieu plus loin, sur le chemin de l'est et
  -- non devant le croisement.
  GAME:MoveCamera(croisement.Position.X + 24, croisement.Position.Y - 26, 1, false)
  GAME:FadeIn(30)
  GAME:WaitFrames(10)
  GROUND:MoveToPosition(partenaire, porte.Position.X, porte.Position.Y + 58, false, 1)
  GROUND:MoveToPosition(partenaire, croisement.Position.X + 4, croisement.Position.Y + 12, false, 1)
  GROUND:MoveToPosition(partenaire, croisement.Position.X + 64, croisement.Position.Y + 28, false, 1)
  GAME:MoveCamera(entree.Position.X - 40, entree.Position.Y, 110, false)
  GROUND:MoveToPosition(partenaire, entree.Position.X - 40, entree.Position.Y, false, 1)
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 8)
  if avant_plan ~= nil then avant_plan.Layer = ordre_avant_plan end
  GAME:WaitFrames(20)

  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion("Worried")
  UI:WaitShowDialogue("Bon... voilà le chemin de l’est.\n Au bout, c’est l’entrée du donjon le plus proche : [color=#69D98C]Lost Wood[color].")
  UI:WaitShowDialogue("Devenir explorateur...\n est-ce que je suis vraiment prêt pour ça ?")
  UI:SetSpeakerEmotion("Normal")
  UI:WaitShowDialogue("Si j'y vais seul et que ça tourne mal...\n personne ne saura même que je suis parti.")
  SOUND:PlayBattleSE('EVT_Emote_Confused')
  GROUND:CharSetEmote(partenaire, "question", 1)
  GAME:WaitFrames(30)
  UI:WaitShowDialogue("...Mais si je ne tente rien...\n je le regretterai toute ma vie, c'est certain.")

  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partenaire, "exclaim", 1)
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("C'est décidé ! Je traverserai [color=#69D98C]Lost Wood[color] —\n et je sortirai de là en vrai explorateur !")

  -- Les conseils sont maintenant présentés dans Lost Wood, étage par étage.
  SV.Destiny = SV.Destiny or {}
  UI:WaitShowDialogue("En route ! La nuit est à moi !")

  -- le partenaire part seul : le héros est gardé hors de l'équipe jusqu'au réveil
  local heros = GAME:GetPlayerPartyMember(0)
  -- RemovePlayerTeam dépose l'objet tenu dans le sac. Ici on garde le même
  -- Character et son équipement, puis on le range en tête de la réserve.
  _DATA.Save.ActiveTeam.Players:RemoveAt(0)
  GAME:AddPlayerAssembly(heros)
  SV.Destiny.HeroAssemblyIndex = 0
  GAME:SetTeamLeaderIndex(0)
  GROUND:Hide('PLAYER')

  -- Le partenaire s'engage jusqu'au seuil oriental du donjon.
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 8)
  GAME:WaitFrames(20)
  GROUND:MoveToPosition(partenaire, entree.Position.X - 16, entree.Position.Y, false, 1)
  cliffdaytest_nuit.LancerAller()
end

return cliffdaytest_nuit
