--[[ init.lua — Scène du partenaire (map cliffdaytest — version nuit)
     Enchaînement : fin du quiz → la faille du rêve → cette map, la nuit.
     Le partenaire (celui choisi et nommé dans le quiz) hésite à devenir
     explorateur au croisement, puis se décide et part seul dans Lost Wood
     (7 étages). Après la rencontre et la longue discussion sous la montagne,
     ils retraversent le donjon ensemble ; le retour aboutit sur cette map.
     Le héros reste allongé jusqu'à la rencontre. Dialogues originaux Destiny.
     Réveil solo, retrouvailles et retour testés sur un banc moteur avec
     sorties forcées ; le parcours complet des étages reste à tester.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local cliffdaytest_nuit = {}

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
end

function cliffdaytest_nuit.Update(map)
  -- Après une pause, rejoindre de nouveau le bord est relance l'aller solo.
  if SV.Destiny and SV.Destiny.LostWoodTrip == 'pause_aller' then
    local joueur, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
    if joueur and entree and joueur.Position.X >= entree.Position.X - 16
       and math.abs(joueur.Position.Y - entree.Position.Y) <= 24 then
      cliffdaytest_nuit.LancerAller()
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
  SV.Destiny.PartenaireParti = true
  SOUND:FadeOutBGM(60)
  GAME:FadeOut(false, 60)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  GAME:EnterDungeon('lost_wood', 0, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
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
  UI:ChoiceMenuYesNo('Repartir dans la forêt maintenant ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    cliffdaytest_nuit.LancerAller()
  else
    UI:WaitShowDialogue('Je prends une pause. Quand je serai prêt, je reviendrai à l’entrée, à l’est.')
    SV.Destiny.LostWoodTrip = 'pause_aller'
    GAME:MoveCamera(0, 0, 30, true)
    GAME:CutsceneMode(false)
  end
end

-- -------------------------------------------------------- retour en duo

function cliffdaytest_nuit.AllerEnVille()
  SOUND:FadeOutBGM(45)
  GAME:FadeOut(false, 45)
  GAME:CutsceneMode(false)
  -- La ville reste une carte distincte, dans sa zone d'origine.
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function cliffdaytest_nuit.SceneRetour()
  local hero = CH('PLAYER')
  local partner = equipe_scene.Partenaire(666, 516, Direction.Up)
  if partner == nil then GAME:FadeIn(20); return end
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:TeleportTo(hero, 648, 516, Direction.Up)
  GROUND:TeleportTo(partner, 666, 516, Direction.Up)
  GAME:MoveCamera(666, 516, 1, false)
  GAME:FadeIn(30)
  GAME:WaitFrames(30)
  UI:SetSpeaker(partner)
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("On est revenus au croisement ! Et cette fois, on a traversé [color=#69D98C]Lost Wood[color] ensemble.")
  UI:WaitShowDialogue("Regarde la montagne, là-bas. Elle n'a pas bougé… mais moi, j'ai l'impression d'avoir fait un grand pas vers elle.")
  UI:SetSpeakerEmotion("Normal")
  UI:WaitShowDialogue("Un jour, on suivra ce chemin jusqu'au pied de cette montagne. On ira secourir ceux qui en ont besoin et découvrir ce qui se cache au-delà.")
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("Et si on trouve un trésor en route, on le partagera avec toute l'équipe !")
  UI:SetSpeaker(hero)
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("Alors, explorateur… on continue ensemble ?")
  UI:SetSpeaker(partner)
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("Ensemble. Notre aventure ne fait que commencer.")
  UI:WaitShowDialogue("Le jour se lève. Viens, je te ramène en ville ; je te présenterai les endroits où nous préparer.")
  GROUND:CharEndAnim(hero)
  GROUND:CharEndAnim(partner)
  hero.CollisionDisabled = true
  local marche_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partner, 694, 522, false, 1)
  end)
  local marche_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, 674, 522, false, 1)
  end)
  TASK:JoinCoroutines({marche_partenaire, marche_hero})
  hero.CollisionDisabled = false
  SV.Destiny.FinaleDestiny = true
  SV.Destiny.VisiteVille = 'en_route'
  cliffdaytest_nuit.AllerEnVille()
end

-- ------------------------------------------------------- scène (hésitation)

function cliffdaytest_nuit.ScenePartenaire()
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  -- Aucun morceau ici : le quiz s'est tu et Tiny Woods démarre dans le donjon.

  -- Le héros est inconscient ailleurs et le Pichu décoratif de la carte ne
  -- doit pas doubler le partenaire sélectionné au quiz.
  GROUND:Hide('PLAYER')
  if CH('Pichu') ~= nil then GROUND:Hide('Pichu') end

  local partenaire = GAME:GetPlayerPartyMember(1)
  GROUND:SpawnerSetSpawn('Adagio', partenaire)
  partenaire = GROUND:SpawnerDoSpawn('Adagio')
  AI:DisableCharacterAI(partenaire)
  local porte, croisement = MRKR('Pichu_Home_Door'), MRKR('Pichu_Crossroads')

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
  -- Le cadre contient la porte, la jonction et le début du chemin du donjon.
  GAME:MoveCamera(croisement.Position.X + 24, croisement.Position.Y - 26, 1, false)
  GAME:FadeIn(30)
  GAME:WaitFrames(10)
  GROUND:MoveToPosition(partenaire, porte.Position.X, porte.Position.Y + 58, false, 1)
  GROUND:MoveToPosition(partenaire, croisement.Position.X + 4, croisement.Position.Y + 12, false, 1)
  GROUND:MoveToPosition(partenaire, croisement.Position.X + 64, croisement.Position.Y + 28, false, 1)
  GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 8)
  if avant_plan ~= nil then avant_plan.Layer = ordre_avant_plan end
  GAME:WaitFrames(20)

  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion("Worried")
  UI:WaitShowDialogue("Bon... le voilà, le croisement.\n Plus loin, c'est le donjon le plus proche : [color=#69D98C]Lost Wood[color].")
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

  -- Le partenaire s'engage dans le chemin du donjon.
  GROUND:CharAnimateTurnTo(partenaire, Direction.Down, 8)
  GAME:WaitFrames(20)
  cliffdaytest_nuit.LancerAller()
end

return cliffdaytest_nuit
