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
  SV.Destiny.FinaleDestiny = true
  GAME:WaitFrames(30)
  -- Une caméra absolue de cinématique ne suit pas le joueur : la rendre.
  GAME:MoveCamera(0, 0, 30, true)
  equipe_scene.Suivre(partner, hero)
  GAME:CutsceneMode(false)
end

-- ------------------------------------------------------- scène (hésitation)

function cliffdaytest_nuit.ScenePartenaire()
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  SOUND:PlayBGM("Welcome to the World of Pokémon!.ogg", true)

  -- le héros est allongé, inconscient, ailleurs : seul le partenaire est ici
  local hero = CH('PLAYER')
  GROUND:Hide('PLAYER')

  -- le partenaire apparaît au croisement (spawn réutilisé de la map)
  local partenaire = GAME:GetPlayerPartyMember(1)
  GROUND:SpawnerSetSpawn('Adagio', partenaire)
  partenaire = GROUND:SpawnerDoSpawn('Adagio')
  AI:DisableCharacterAI(partenaire)
  local croisement = MRKR('Pichu_Crossroads')
  -- Le marqueur central se trouve sous une partie opaque du décor en avant-plan.
  -- Garder la caméra au croisement, mais placer le partenaire dans l'ouverture
  -- voisine, sans modifier la carte ni l'ordre de ses calques.
  GROUND:TeleportTo(partenaire, croisement.Position.X + 64, croisement.Position.Y + 28, Direction.Up)
  GAME:MoveCamera(croisement.Position.X, croisement.Position.Y, 1, false)
  -- Le quiz termine sur un fondu noir ; révéler la carte avant les dialogues.
  GAME:FadeIn(30)
  GAME:WaitFrames(30)

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

  -- tutoriel du donjon à son entrée : explications intégrées au récit,
  -- commandes abstraites pour respecter la configuration du joueur
  SV.Destiny = SV.Destiny or {}
  if not SV.Destiny.LostWoodTutorialDone then
    UI:SetSpeakerEmotion("Normal")
    UI:WaitShowDialogue("Avant d'entrer, je dois me rappeler les règles d'un donjon.")
    UI:WaitShowDialogue("[color=#69D98C]Lost Wood[color] compte sept étages. À chaque étage, il faut trouver l'escalier qui descend ; le septième mène au fond de la forêt.")
    UI:WaitShowDialogue("Les déplacements se font avec les commandes de direction. Chaque pas prend un tour : les Pokémon autour de moi peuvent bouger et agir pendant ce temps.")
    UI:WaitShowDialogue("La commande d'attaque permet de frapper tout près. Dans le menu des capacités, je choisis une attaque à distance ou un pouvoir spécial — mais chaque capacité consomme des PP.")
    UI:WaitShowDialogue("Le sac contient des objets utiles : soins, baies et autres outils. Je peux les sélectionner dans le menu des objets ; certains peuvent aussi servir contre les obstacles ou les adversaires.")
    UI:WaitShowDialogue("Je dois surveiller mon ventre : avancer longtemps sans manger épuise. Si je trouve de la nourriture, je la garde pour les moments où j'en aurai besoin.")
    UI:WaitShowDialogue("Je n'ai pas besoin de combattre tout le monde. Je peux contourner un adversaire, utiliser un objet, ou économiser mes PP pour un passage difficile.")
    UI:WaitShowDialogue("Quand j'aurai trouvé l'escalier du septième étage, je sortirai dans la clairière. Alors… en avant !")
    SV.Destiny.LostWoodTutorialDone = true
  end
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
