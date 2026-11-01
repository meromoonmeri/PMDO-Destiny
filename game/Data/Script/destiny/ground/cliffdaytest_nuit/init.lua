--[[ init.lua — Scène du partenaire (map cliffdaytest — version nuit)
     Enchaînement : fin du quiz → sommeil du héros sur zrv2_zone_reveil_nuit →
     cette map, la nuit. Le partenaire sort de sa maison, suit le chemin jusqu'à
     l'entrée est de Lost Wood (sans s'arrêter devant le croisement), hésite un
     instant puis entre seul dans Lost Wood (7 étages).
     Le retour en duo débouche désormais de jour sur cliffdaytest.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local cliffdaytest_nuit = {}

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

-- ------------------------------------------------------------- map callbacks

function cliffdaytest_nuit.Init(map)
  if map ~= nil and RogueEssence ~= nil and RogueEssence.Dungeon ~= nil and RogueEssence.Dungeon.BaseMap ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  if SV.Destiny and SV.Destiny.FinaleDestiny then
    local hero = CH('PLAYER')
    if hero ~= nil then
      local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
      if partner ~= nil then equipe_scene.Suivre(partner, hero) end
    end
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
       and math.abs(joueur.Position.Y - entree.Position.Y) <= 32 then
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
  if not SV.Destiny.ProvisionsDepartDonnees and GAME.GivePlayerItem ~= nil then
    GAME:GivePlayerItem('berry_oran', 2)
    GAME:GivePlayerItem('food_apple', 1)
    GAME:GivePlayerItem('berry_leppa', 1)
    GAME:GivePlayerItem('seed_reviver', 1)
    SV.Destiny.ProvisionsDepartDonnees = true
  elseif GAME.GivePlayerItem ~= nil and GAME.GetPlayerBagCount ~= nil and GAME:GetPlayerBagCount() == 0 then
    GAME:GivePlayerItem('berry_oran', 1)
    GAME:GivePlayerItem('food_apple', 1)
  end
  SV.Destiny.LostWoodTrip = 'aller'
  SV.Destiny.PartenaireParti = true
  SOUND:FadeOutBGM(60)
  GAME:FadeOut(false, 60)
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  local stakes = (RogueEssence ~= nil and RogueEssence.Data ~= nil and RogueEssence.Data.GameProgress ~= nil)
    and RogueEssence.Data.GameProgress.DungeonStakes.Risk or 0
  if GAME.EnterDungeon ~= nil then
    GAME:EnterDungeon('lost_wood', 0, 0, 0, stakes, true, false)
  else
    GAME:EnterZone('lost_wood', 0, 0, 0)
  end
end

function cliffdaytest_nuit.SceneEchecPartenaire()
  local partenaire, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
  local ex = entree ~= nil and entree.Position.X or 960
  local ey = 468
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:TeleportTo(partenaire, ex - 96, ey, Direction.Right)
  GROUND:CharSetAnim(partenaire, 'Laying', true)
  GAME:MoveCamera(math.min(824, ex - 96), ey, 1, false)
  GAME:FadeIn(30)
  GAME:WaitFrames(30)
  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion('Worried')
  if SV.Destiny.LostWoodCause == 'ko' then
    UI:WaitShowDialogue('Aïe… Je suis revenu sur le chemin devant [color=#69D98C]Lost Wood[color]…')
    UI:WaitShowDialogue('J’ai perdu connaissance dans la forêt. Il faut que je reprenne mon souffle.')
  else
    UI:WaitShowDialogue('Me voilà de retour devant [color=#69D98C]Lost Wood[color]. J’ai bien fait de rebrousser chemin.')
    UI:WaitShowDialogue('Renoncer pour se protéger, ce n’est pas la fin de l’aventure.')
  end
  GROUND:CharSetAnim(partenaire, 'Wake', false)
  GAME:WaitFrames(35)
  GROUND:CharEndAnim(partenaire)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Je peux me reposer ici, puis essayer encore quand je serai prêt.')
  UI:ChoiceMenuYesNo('Repartir dans la forêt maintenant ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    GROUND:MoveToPosition(partenaire, ex, ey, false, 2)
    cliffdaytest_nuit.LancerAller()
  else
    UI:WaitShowDialogue('Je prends une pause. Quand je serai prêt, je retournerai au bout du chemin à l’est.')
    SV.Destiny.LostWoodTrip = 'pause_aller'
    GAME:MoveCamera(0, 0, 30, true)
    GAME:CutsceneMode(false)
  end
end

-- -------------------------------------------------------- compatibilité retour

function cliffdaytest_nuit.AllerEnVille()
  SOUND:FadeOutBGM(45)
  GAME:FadeOut(false, 45)
  GAME:CutsceneMode(false)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

-- Secours de compatibilité si une ancienne sauvegarde invoque SceneRetour sur la carte de nuit :
-- transfère proprement vers la carte de jour cliffdaytest où se joue désormais la scène.
function cliffdaytest_nuit.SceneRetour()
  GAME:FadeOut(false, 1)
  GAME:CutsceneMode(false)
  if GAME.EnterGroundMap ~= nil then
    GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest', 'Dazzling_Exit_East')
  else
    GAME:EnterZone('destiny_cliff_tests', -1, 0, 0)
  end
end

-- ------------------------------------------------------- départ du partenaire

function cliffdaytest_nuit.ScenePartenaire()
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()

  -- Le héros est endormi dans la clairière et le Pichu décoratif de la carte
  -- ne doit pas doubler le partenaire sélectionné au quiz.
  GROUND:Hide('PLAYER')
  if CH('Pichu') ~= nil then GROUND:Hide('Pichu') end

  local partenaire = GAME:GetPlayerPartyMember(1)
  GROUND:SpawnerSetSpawn('Adagio', partenaire)
  partenaire = GROUND:SpawnerDoSpawn('Adagio')
  AI:DisableCharacterAI(partenaire)

  local porte = MRKR('Pichu_Home_Door')
  local entree = MRKR('Dazzling_Exit_East')
  local px = porte ~= nil and porte.Position.X or 600
  local py = porte ~= nil and porte.Position.Y or 442
  local ex = entree ~= nil and entree.Position.X or 960
  local chemin_y = 468

  local avant_plan, ordre_avant_plan = abaisser_canopee_chemin()

  -- Le partenaire sort de sa maison puis marche tout du long sur le chemin
  -- menant à l'entrée est de Lost Wood, sans s'arrêter devant le croisement.
  GROUND:TeleportTo(partenaire, px, py, Direction.Down)
  GAME:MoveCamera(px + 16, py + 34, 1, false)
  GAME:FadeIn(35)
  GAME:WaitFrames(15)

  GROUND:MoveToPosition(partenaire, px + 8, chemin_y + 8, false, 1)

  local marche_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 656, 512, false, 1)
    GROUND:MoveToPosition(partenaire, 696, chemin_y, false, 1)
    GROUND:MoveToPosition(partenaire, ex - 96, chemin_y, false, 1)
    GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  end)
  local suivi_camera = TASK:BranchCoroutine(function()
    GAME:WaitFrames(25)
    GAME:MoveCamera(math.min(824, ex - 120), chemin_y, 130, false)
  end)
  TASK:JoinCoroutines({ marche_partenaire, suivi_camera })
  GAME:WaitFrames(20)

  UI:SetSpeaker(partenaire)
  UI:SetSpeakerEmotion("Worried")
  UI:WaitShowDialogue("Voilà l'entrée de [color=#69D98C]Lost Wood[color] juste au bout de ce chemin…")
  UI:WaitShowDialogue("Devenir explorateur…\n est-ce que je suis vraiment prêt à franchir ces arbres tout seul ?")
  UI:SetSpeakerEmotion("Normal")
  UI:WaitShowDialogue("Si je fais demi-tour maintenant, personne n'en saura rien…")
  SOUND:PlayBattleSE('EVT_Emote_Confused')
  GROUND:CharSetEmote(partenaire, "question", 1)
  GAME:WaitFrames(30)
  UI:WaitShowDialogue("…Mais si je n'ose même pas faire ce premier pas,\n je le regretterai toute ma vie, c'est certain.")

  SOUND:PlayBattleSE('EVT_Emote_Exclaim')
  GROUND:CharSetEmote(partenaire, "exclaim", 1)
  UI:SetSpeakerEmotion("Happy")
  UI:WaitShowDialogue("C'est décidé ! Je vais traverser [color=#69D98C]Lost Wood[color] —\n et montrer que j'ai l'étoffe d'un vrai explorateur !")

  SV.Destiny = SV.Destiny or {}
  UI:WaitShowDialogue("En route ! La forêt m'attend !")

  -- Le partenaire part seul : on conserve l'objet tenu du héros en le plaçant
  -- en réserve jusqu'aux retrouvailles sur zrv2_zone_reveil_nuit.
  local heros = GAME:GetPlayerPartyMember(0)
  _DATA.Save.ActiveTeam.Players:RemoveAt(0)
  GAME:AddPlayerAssembly(heros)
  SV.Destiny.HeroAssemblyIndex = 0
  GAME:SetTeamLeaderIndex(0)
  GROUND:Hide('PLAYER')

  -- Il s'engage jusqu'au seuil oriental de Lost Wood.
  GROUND:MoveToPosition(partenaire, ex, chemin_y, false, 2)
  if avant_plan ~= nil then avant_plan.Layer = ordre_avant_plan end
  cliffdaytest_nuit.LancerAller()
end

return cliffdaytest_nuit
