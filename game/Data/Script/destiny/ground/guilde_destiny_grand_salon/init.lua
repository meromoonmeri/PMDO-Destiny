require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'
local equipe_scene = require 'destiny.equipe_scene'

local guilde_destiny_grand_salon = {}
local sortie_en_cours = false
local carte_courante = nil

function guilde_destiny_grand_salon.Init(map)
  sortie_en_cours = false
  carte_courante = map or carte_courante
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
end

function guilde_destiny_grand_salon.Enter(map)
  carte_courante = map or carte_courante
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_grand_salon.GameLoad(map)
  carte_courante = map or carte_courante
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_grand_salon.Exit(map)
end

function guilde_destiny_grand_salon.Update(map)
  guilde_decors.SynchroniserAmbiance(map, 'guilde_destiny_grand_salon')
end

local function partenaire_de(hero)
  if hero == nil or GAME == nil or GAME.GetPlayerPartyCount == nil then return nil end
  if GAME:GetPlayerPartyCount() <= 1 then return nil end
  local partenaire = (_G.CH and CH('Teammate1')) or nil
  if partenaire ~= nil then return partenaire end
  if equipe_scene ~= nil and equipe_scene.Partenaire ~= nil and hero.Position ~= nil then
    local py = math.min(hero.Position.Y + 24, 384)
    return equipe_scene.Partenaire(hero.Position.X, py, hero.Direction)
  end
  return nil
end

local function retour_au_joueur(hero, partenaire)
  if UI ~= nil and UI.ResetSpeaker ~= nil then UI:ResetSpeaker() end
  if hero ~= nil then hero.CollisionDisabled = false end
  if partenaire ~= nil and equipe_scene ~= nil and equipe_scene.Suivre ~= nil then equipe_scene.Suivre(partenaire, hero) end
  if GAME ~= nil and GAME.MoveCamera ~= nil then GAME:MoveCamera(0, 0, 1, true) end
  if GAME ~= nil and GAME.CutsceneMode ~= nil then GAME:CutsceneMode(false) end
end

function guilde_destiny_grand_salon.OuvrirPorteMaitre(map)
  guilde_decors.OuvrirPorteSalon(map or carte_courante or (GAME and GAME:GetCurrentGround()))
end

function guilde_destiny_grand_salon.FermerPorteMaitre(map)
  guilde_decors.FermerPorteSalon(map or carte_courante or (GAME and GAME:GetCurrentGround()))
end

function guilde_destiny_grand_salon.SeuilSud_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_missions', 'EscalierNordMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 1, 0) end
end
function guilde_destiny_grand_salon.SortieBureauMaitre_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true

  local map = carte_courante or (_G.GAME and GAME.GetCurrentGround and GAME:GetCurrentGround()) or nil
  local hero = (_G.CH and CH('PLAYER')) or activator
  local partenaire = partenaire_de(hero)

  if GAME ~= nil and GAME.CutsceneMode ~= nil then GAME:CutsceneMode(true) end
  if partenaire ~= nil and AI ~= nil and AI.DisableCharacterAI ~= nil then AI:DisableCharacterAI(partenaire) end
  if hero ~= nil then hero.CollisionDisabled = true end
  if TASK ~= nil and TASK.BranchCoroutine ~= nil and TASK.JoinCoroutines ~= nil and GROUND ~= nil and Direction ~= nil then
    local rotations = {}
    if hero ~= nil then
      table.insert(rotations, TASK:BranchCoroutine(function()
        if GROUND.CharAnimateTurnTo ~= nil then
          pcall(function() GROUND:CharAnimateTurnTo(hero, Direction.Up, 4) end)
        elseif GROUND.EntTurn ~= nil then
          GROUND:EntTurn(hero, Direction.Up)
        end
      end))
    end
    if partenaire ~= nil then
      table.insert(rotations, TASK:BranchCoroutine(function()
        if GROUND.CharAnimateTurnTo ~= nil then
          pcall(function() GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 4) end)
        elseif GROUND.EntTurn ~= nil then
          GROUND:EntTurn(partenaire, Direction.Up)
        end
      end))
    end
    if #rotations > 0 then TASK:JoinCoroutines(rotations) end
  else
    if hero ~= nil and GROUND ~= nil and Direction ~= nil then
      if GROUND.CharAnimateTurnTo ~= nil then
        pcall(function() GROUND:CharAnimateTurnTo(hero, Direction.Up, 4) end)
      elseif GROUND.EntTurn ~= nil then
        GROUND:EntTurn(hero, Direction.Up)
      end
    end
    if partenaire ~= nil and GROUND ~= nil and Direction ~= nil then
      if GROUND.CharAnimateTurnTo ~= nil then
        pcall(function() GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 4) end)
      elseif GROUND.EntTurn ~= nil then
        GROUND:EntTurn(partenaire, Direction.Up)
      end
    end
  end

  guilde_decors.OuvrirPorteSalon(map)
  if GAME ~= nil and GAME.WaitFrames ~= nil then GAME:WaitFrames(20) end

  GAME:FadeOut(false, 20)
  guilde_decors.DefinirPorteSalonOuverte(map, false)
  retour_au_joueur(hero, partenaire)
  sortie_en_cours = false
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_bureau_maitre', 'EntreeSudMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 3, 0) end
end
function guilde_destiny_grand_salon.SortieBureauMaitre_Action(obj, activator)
  guilde_destiny_grand_salon.SortieBureauMaitre_Touch(obj, activator)
end
function guilde_destiny_grand_salon.CouloirOuest_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_carrefour', 'EntreeEstMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 4, 0) end
end
function guilde_destiny_grand_salon.CouloirEst_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_couloir_ouest', 'EntreeOuestMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 8, 0) end
end

return guilde_destiny_grand_salon
