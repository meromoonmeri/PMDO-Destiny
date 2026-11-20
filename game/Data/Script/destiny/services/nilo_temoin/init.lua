-- Nilo est un spectateur filmé, pas un monstre, un allié ou un obstacle.
-- Le renderer de CharAfterImage sait dessiner la feuille d’un Pokémon dans
-- les couches d’animation du donjon. On ne conserve qu’une pose opaque
-- à la fois ; aucun sprite recopié, tour, collider, effet de statut ou cible.
local fosse = require 'destiny.fosse_cascade_scene'
local scene = RogueEssence.Dungeon.DungeonScene.Instance
local gm = RogueEssence.GameManager.Instance
local gfx = RogueEssence.Content.GraphicsManager
local layer = DrawLayer.Normal
local normal = tonumber(layer) or 2 -- DrawLayer.Normal dans Anims (index .NET)
local service = {}
local state

local function retirer_pose()
  if state ~= nil and state.pose ~= nil then
    scene.Anims[normal]:Remove(state.pose)
    state.pose = nil
  end
end

function service:Effacer()
  retirer_pose()
  state = nil
end

function service:MettreAJour()
  -- Le test de la carte courante fonctionne aussi en reprise de sauvegarde :
  -- les animations de scène ne sont pas sérialisées avec le donjon.
  local map = gm.CurrentScene == scene and _ZONE.CurrentMap or nil
  if map == nil or map.AssetName ~= fosse.ARENE then
    self:Effacer()
    return
  end
  if state == nil or map ~= state.map then
    self:Effacer()
    local id = RogueEssence.Dungeon.MonsterID('shinx', 0, 'normal', Gender.Male):ToCharID()
    local planche = gfx.GetChara(id)
    local idle = planche:GetReferencedAnimIndex(gfx.IdleAction)
    local frames = planche.AnimData[idle]:SeqAtDir(Direction.Down).Frames
    state = {map=map, id=id, idle=idle, frames=frames, total=frames[frames.Count - 1].EndTime}
  end
  local t = math.floor(tonumber(gfx.TotalFrameTick) / 120)
  local phase = t % state.total
  local frame = 0
  while phase >= state.frames[frame].EndTime do frame = frame + 1 end
  -- Même amplitude que Shaking au sol, un peu plus lente pour rester lisible
  -- une fois le contrôle rendu (Update servi environ toutes les 20 ms).
  local oscillation = math.floor(t * 2 / 3) % 8
  local dx = oscillation > 4 and 6 - oscillation or oscillation - 2
  if state.pose ~= nil and state.dx == dx and state.frame == frame and not state.pose.Finished then return end
  retirer_pose()
  state.dx, state.frame = dx, frame
  local loc = RogueElements.Loc(fosse.NILO_ARENE.x + dx, fosse.NILO_ARENE.y)
  state.pose = RogueEssence.Content.CharAfterImage(loc, state.id, state.idle, frame, Direction.Down, 0, 120, 255, 0)
  DUNGEON:PlayVFXAnim(state.pose, layer)
end

function service:Subscribe(med)
  med:Subscribe('NiloTemoin', EngineServiceEvents.Update, function() self:MettreAJour() end)
  med:Subscribe('NiloTemoin', EngineServiceEvents.DungeonFloorExit, function() self:Effacer() end)
  med:Subscribe('NiloTemoin', EngineServiceEvents.DungeonModeEnd, function() self:Effacer() end)
end

function service:UnSubscribe(med)
  self:Effacer()
end

SCRIPT:AddService('NiloTemoin', service)
return service
