--[[ init.lua — Scène du partenaire (map cliffdaytest — version nuit)
     Enchaînement : fin du quiz → faille du rêve → prologue du héros endormi
     dans la prairie ZRV2 (zrv2_zone_reveil_nuit) → cette map, la nuit.
     Le partenaire (celui choisi et
     nommé dans le quiz) sort de sa maison, dépasse le croisement et hésite
     sur le chemin de l'est, devant l'entrée des Bois Perdus, puis part seul.
     Après les retrouvailles, le retour inverse en duo aboutit sur
     cliffdaytest au jour. Le héros reste allongé jusqu'à la rencontre.
     Dialogues originaux Destiny. Réveil solo, retrouvailles et retour
     testés sur un banc moteur avec sorties forcées ; le parcours complet
     des étages reste à tester.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local recrutement = require 'destiny.recrutement'
local meteo_reverie = require 'destiny.meteo_reverie'

local CARTE_CLIFF = 'cliffdaytest_nuit'
local cliffdaytest_nuit = {}
local SON_MER = 'Destiny_Falaise_Mer'
local garde_chemin_sud_en_cours = false
local invite_retour_aller_en_cours = false
local sortie_en_cours = false

local function demarrer_mer()
  -- La BGM « Cliff Camp.ogg » est portée par la carte ; cette boucle ajoute
  -- le ressac de la mer sous la musique pendant toute la visite.
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function installer_sortie_carrefour(map)
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  if map == nil or map:FindObject('SortieCarrefour') then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = 'SortieCarrefour'
  sortie.Collider = RogueElements.Rect(688, 784, 104, 8)
  sortie.Passable = true
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

local function installer_porte_maison(map)
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  if map == nil or map:FindObject('PorteMaisonEquipe') then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteMaisonEquipe'
  porte.Collider = RogueElements.Rect(592, 464, 40, 8)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

-- ------------------------------------------------------------- map callbacks

function cliffdaytest_nuit.Init(map)
  -- Empêcher le cadre de déborder dans le vide aux limites de cette carte.
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_sortie_carrefour(map)
  installer_porte_maison(map)
  if SV.Destiny and (SV.Destiny.FinaleDestiny or SV.Destiny.VisiteVille == 'terminee') then
    local hero = CH('PLAYER')
    if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
      local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
      equipe_scene.Suivre(partner, hero)
    end
  end
end

local function synchroniser_ambiance(avec_fondu)
  if SV == nil or SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then
    return false
  end
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  local attendu = meteo_reverie.CarteCliff()
  SV.Destiny.FalaiseAmbiance = attendu
  if attendu == CARTE_CLIFF then return false end
  if sortie_en_cours then return true end
  sortie_en_cours = true
  if not SV.Destiny.RetourMaisonEquipe then
    local hero = CH('PLAYER')
    if hero ~= nil then
      SV.Destiny.PassageAmbiance = {
        carte = attendu,
        x = hero.Position.X,
        y = hero.Position.Y,
        dir = hero.Direction,
      }
    end
  end
  arreter_mer()
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterGroundMap('destiny_cliff_tests', attendu, 'Dazzling_Entry_South')
  return true
end

local function restaurer_passage()
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbiance or nil
  if passage ~= nil and passage.carte == CARTE_CLIFF then
    SV.Destiny.PassageAmbiance = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        GROUND:TeleportTo(partenaire, math.min(passage.x + 24, 1560), passage.y, passage.dir or hero.Direction)
      end
    end
  end
end

function cliffdaytest_nuit.Enter(map)
  if synchroniser_ambiance(false) then return end
  cliffdaytest_nuit.PlotScripting()
end

function cliffdaytest_nuit.Exit(map)
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  arreter_mer()
end

function cliffdaytest_nuit.GarderCheminSud(joueur)
  if garde_chemin_sud_en_cours or joueur == nil then return end
  garde_chemin_sud_en_cours = true
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  GROUND:CharAnimateTurnTo(joueur, Direction.Up, 4)
  cinematique.Dire(joueur, 'Worried', 'Non. Je ne vais pas me dégonfler.', 'standard')
  cinematique.Dire(joueur, 'Determined', 'Il faut que je sois courageux. Je dois traverser les [color=#69D98C]Bois Perdus[color].', 'standard')
  cinematique.Dire(joueur, 'Normal', 'Je peux souffler un instant, d’accord… mais pas fuir par le chemin du sud. L’entrée est à l’est.', 'standard')
  UI:ResetSpeaker()
  -- Le partenaire remonte de lui-même vers le croisement nord-sud.
  GROUND:MoveToPosition(joueur, 720, 556, false, 1)
  GROUND:CharAnimateTurnTo(joueur, Direction.Right, 4)
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
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.VisiteVille == 'terminee'
      and SV.Destiny.MomentScenario ~= nil and meteo_reverie.CarteCliff() ~= CARTE_CLIFF then
    synchroniser_ambiance(true)
  end
end

function cliffdaytest_nuit.GameSave(map)
end

function cliffdaytest_nuit.GameLoad(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_sortie_carrefour(map)
  installer_porte_maison(map)
  if synchroniser_ambiance(false) then return end
  cliffdaytest_nuit.PlotScripting()
end

function cliffdaytest_nuit.PorteMaisonEquipe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  sortie_en_cours = true
  SV.Destiny.FalaiseAmbiance = meteo_reverie.CarteCliff()
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('destiny_cliff_tests', 'maison_equipe_falaise', 'entree', true)
end

function cliffdaytest_nuit.SortieCarrefour_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('reverie', 'crossroadreverietown2', 'entree_falaise')
end

function cliffdaytest_nuit.PlotScripting()
  SV.Destiny = SV.Destiny or {}
  sortie_en_cours = false
  demarrer_mer()
  if SV.Destiny.RetourMaisonEquipe and SV.Destiny.VisiteVille == 'terminee' then
    SV.Destiny.RetourMaisonEquipe = nil
    local hero = CH('PLAYER')
    local partenaire = CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 600, 476, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 624, 476, Direction.Down) end
    GAME:FadeIn(20)
    if hero ~= nil and partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
    return
  end
  if SV.Destiny.VisiteVille == 'terminee' then
    restaurer_passage()
    GAME:FadeIn(20)
    return
  end
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
  recrutement.synchroniser()
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
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  cinematique.Dire(partenaire, 'Normal', 'Voici l’entrée des [color=#69D98C]Bois Perdus[color].', 'standard')
  UI:ResetSpeaker() -- question système, pas une réplique
  UI:ChoiceMenuYesNo('Souhaitez-vous retourner dans les Bois Perdus ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    cinematique.Dire(partenaire, 'Determined', 'Allez… on y retourne. Cette fois, je vais jusqu’au bout !', 'standard')
    invite_retour_aller_en_cours = false
    cliffdaytest_nuit.LancerAller()
    return
  end
  cinematique.Dire(partenaire, 'Normal', 'Pas tout de suite. Je reviendrai vers l’entrée quand je serai prêt.', 'standard')
  UI:ResetSpeaker()
  -- Reculer hors du seuil évite de rouvrir le menu à la frame suivante.
  GROUND:MoveToPosition(partenaire, entree.Position.X - 56, entree.Position.Y, false, 1)
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  GAME:MoveCamera(0, 0, 30, true)
  GAME:CutsceneMode(false)
  invite_retour_aller_en_cours = false
end

local function jouer_animation_sure(personnage, nom, duree_secours)
  if personnage == nil then return false end
  local ok, duree = pcall(function()
    local gestionnaire = RogueEssence.Content.GraphicsManager
    local index = gestionnaire.GetAnimIndex(nom)
    if index == nil or index < 0 then return 0 end
    local feuille = gestionnaire.GetChara(personnage.CurrentForm:ToCharID())
    if feuille:GetReferencedAnimIndex(index) ~= index then return 0 end
    return feuille:GetTotalTime(index, personnage.Direction)
  end)
  local temps = ok and tonumber(duree) or duree_secours
  if temps == nil or temps <= 0 then return false end
  GROUND:CharSetAnim(personnage, nom, false)
  GAME:WaitFrames(math.max(1, math.floor(temps)))
  GROUND:CharEndAnim(personnage)
  return true
end

function cliffdaytest_nuit.SceneEchecPartenaire()
  -- Le seuil oriental est le marqueur de sortie du chemin existant ; aucune
  -- carte n'est recréée. Le héros reste dans la réserve, donc hors du plan.
  local partenaire, entree = CH('PLAYER'), MRKR('Dazzling_Exit_East')
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  if SV.Destiny.LostWoodCause == 'abandon' then
    -- Abandon volontaire : le partenaire ressort debout du sentier oriental et
    -- reprend son souffle avant de décider de la suite.
    GROUND:TeleportTo(partenaire, entree.Position.X - 18, entree.Position.Y, Direction.Left)
    GAME:MoveCamera(entree.Position.X - 40, entree.Position.Y, 1, false)
    GAME:FadeIn(30)
    GROUND:MoveToPosition(partenaire, entree.Position.X - 40, entree.Position.Y, false, 1)
    if not jouer_animation_sure(partenaire, 'DeepBreath', 45) then
      GAME:WaitFrames(20)
    end
    cinematique.Dire(partenaire, 'Worried', 'Ouf… me voilà ressorti des [color=#69D98C]Bois Perdus[color] à temps.', 'standard')
    cinematique.Dire(partenaire, 'Normal', 'J’ai bien fait de rebrousser chemin avant de me laisser dépasser. Renoncer pour se protéger, ce n’est pas la fin de l’aventure.', 'standard')
  else
    -- K.O. en donjon : le partenaire reprend connaissance allongé devant
    -- l’entrée et se relève péniblement.
    GROUND:TeleportTo(partenaire, entree.Position.X - 40, entree.Position.Y, Direction.Left)
    GROUND:CharSetAnim(partenaire, 'Laying', true)
    GAME:MoveCamera(entree.Position.X - 40, entree.Position.Y, 1, false)
    GAME:FadeIn(30)
    GAME:WaitFrames(25)
    if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
      SOUND:PlayBattleSE('EVT_Emote_Sweating')
    end
    GROUND:CharSetEmote(partenaire, 'sweating', 1)
    GAME:WaitFrames(30)
    GROUND:CharSetAnim(partenaire, 'Wake', false)
    GAME:WaitFrames(35)
    -- Une IdleAnim en boucle ignore les commandes ; revenir à l'action idle
    -- avant d'afficher son portrait éveillé.
    GROUND:CharEndAnim(partenaire)
    cinematique.Respirer(15)
    cinematique.Dire(partenaire, 'Worried', 'Aïe… ma tête… Je suis revenu devant l’entrée des [color=#69D98C]Bois Perdus[color]…', 'standard')
    cinematique.Dire(partenaire, 'Worried', 'J’ai perdu connaissance dans la forêt. Il faut que je reprenne des forces.', 'standard')
    cinematique.Respirer(20)
  end
  cinematique.Dire(partenaire, 'Normal', 'Je peux me reposer ici, puis essayer encore quand je serai prêt.', 'standard')
  -- Il regarde dans la direction qu’il nomme : l’entrée, à l’est.
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  cinematique.Respirer(10)
  cinematique.Dire(partenaire, 'Normal', 'Quand je me rapprocherai de l’entrée, à l’est, je déciderai si je repars dans la forêt.', 'standard')
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
  GAME:WaitFrames(30)
  GAME:CutsceneMode(false)
  -- La ville reste une carte distincte, dans sa zone d'origine.
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function cliffdaytest_nuit.AllerCliffJour()
  SOUND:FadeOutBGM(45)
  arreter_mer()
  GAME:FadeOut(false, 45)
  GAME:WaitFrames(30)
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
  -- lorsque le partenaire entrera dans les Bois Perdus.

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

  -- Suivre le sentier dessiné au sol plutôt que couper dans l'herbe.
  -- MoveToPosition vise le coin haut-gauche de la boîte 16×16 du
  -- personnage ; son ombre standard se trouve à (+8, +12). Les points
  -- ci-dessous placent donc l'ombre sur l'axe du chemin : descente de la
  -- maison (x 608), route basse (y 544), raccord qui remonte derrière le
  -- panneau, puis route de l'est (y 452).
  local route_basse_y = croisement.Position.Y + 14
  local jonction_x = croisement.Position.X + 32
  local raccord_est_x = croisement.Position.X + 68
  local route_est_y = entree.Position.Y - 20

  GROUND:MoveToPosition(partenaire, porte.Position.X, route_basse_y, false, 1)
  GROUND:MoveToPosition(partenaire, jonction_x, route_basse_y, false, 1)

  -- Le raccord vers la route haute dure 92 frames et le tronçon vers l'est
  -- 220 frames à vitesse 1. La caméra accompagne les 312 frames au lieu de
  -- devancer le partenaire pendant qu'il attend au croisement.
  local marche_est = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, raccord_est_x, route_est_y, false, 1)
    GROUND:MoveToPosition(partenaire, entree.Position.X - 40, route_est_y, false, 1)
  end)
  local suivi_camera = TASK:BranchCoroutine(function()
    -- Deux pans calés sur les deux tronçons du trajet en L : raccord nord
    -- en 92 frames, puis route de l'est en 220 frames, sans diagonale
    -- parasite pendant le second tronçon.
    GAME:MoveCamera(raccord_est_x, route_est_y + 12, 92, false)
    GAME:MoveCamera(entree.Position.X - 40, route_est_y + 12, 220, false)
  end)
  TASK:JoinCoroutines({marche_est, suivi_camera})
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  if avant_plan ~= nil then avant_plan.Layer = ordre_avant_plan end
  GAME:WaitFrames(20)

  cinematique.Dire(partenaire, 'Worried', "Bon... voilà le chemin de l’est.\nAu bout, c’est l’entrée du donjon le plus proche : les [color=#69D98C]Bois Perdus[color].", 'standard')
  cinematique.Dire(partenaire, 'Worried', "Devenir explorateur...\nest-ce que je suis vraiment prêt pour ça ?", 'standard')
  cinematique.Dire(partenaire, 'Normal', "Si j'y vais seul et que ça tourne mal...\npersonne ne saura même que je suis parti.", 'standard')
  cinematique.Emote(partenaire, 'question', 'EVT_Emote_Confused')
  cinematique.Respirer(30)
  cinematique.Dire(partenaire, 'Normal', "...Mais si je ne tente rien...\nje le regretterai toute ma vie, c'est certain.", 'standard')

  cinematique.Emote(partenaire, 'exclaim', 'EVT_Emote_Exclaim_2')
  cinematique.Respirer(20)
  cinematique.Dire(partenaire, 'Happy', "C'est décidé ! Je traverserai les [color=#69D98C]Bois Perdus[color] —\net je sortirai de là en vrai explorateur !", 'standard')

  -- Les conseils sont maintenant présentés dans les Bois Perdus, étage par étage.
  SV.Destiny = SV.Destiny or {}
  cinematique.Dire(partenaire, 'Happy', "En route ! La nuit est à moi !", 'standard')
  UI:ResetSpeaker()

  -- le partenaire part seul : le héros est gardé hors de l'équipe jusqu'au réveil
  local heros = GAME:GetPlayerPartyMember(0)
  -- RemovePlayerTeam dépose l'objet tenu dans le sac. Ici on garde le même
  -- Character et son équipement, puis on le range en tête de la réserve.
  _DATA.Save.ActiveTeam.Players:RemoveAt(0)
  GAME:AddPlayerAssembly(heros)
  SV.Destiny.HeroAssemblyIndex = 0
  GAME:SetTeamLeaderIndex(0)
  GROUND:Hide('PLAYER')

  -- Le partenaire s'engage jusqu'au seuil oriental du donjon, toujours
  -- dans l'axe de la route haute pour éviter un dernier écart dans l'herbe.
  GROUND:CharAnimateTurnTo(partenaire, Direction.Right, 4)
  GAME:WaitFrames(20)
  GROUND:MoveToPosition(partenaire, entree.Position.X - 16, route_est_y, false, 1)
  cliffdaytest_nuit.LancerAller()
end

return cliffdaytest_nuit
