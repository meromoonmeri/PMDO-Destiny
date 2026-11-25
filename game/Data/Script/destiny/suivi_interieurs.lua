-- Suivi de l'équipe dans les intérieurs de Réverie et du café.
local equipe = require 'destiny.equipe_scene'
local M = {}
local function libre(map, x, y)
  if x < 0 or y < 0 or x + 16 > map.TexWidth * 8 or y + 16 > map.TexHeight * 8 then return false end
  for cx = math.floor(x / 8), math.floor((x + 15) / 8) do
    for cy = math.floor(y / 8), math.floor((y + 15) / 8) do
      if map:GetObstacle(cx, cy) ~= 0 then return false end
    end
  end
  return true
end
function M.Activer(map)
  local hero = CH('PLAYER')
  local membre, index = equipe.Membre('Partner')
  if not map or not hero or not membre or index == GAME:GetTeamLeaderIndex() then return end
  -- Au chargement, conserver l'acteur sauvegardé plutôt que le dupliquer.
  local acteur = CH('Teammate1')
  if acteur == nil then
    local x, y = hero.Position.X, hero.Position.Y
    local candidats = {{24,0}, {-24,0}, {0,-24}, {0,24}, {32,0}, {-32,0}, {0,-32}, {0,32}, {24,-24}, {-24,-24}, {24,24}, {-24,24}}
    for _, delta in ipairs(candidats) do
      if libre(map, x + delta[1], y + delta[2]) then
        acteur = equipe.Partenaire(x + delta[1], y + delta[2], hero.Direction)
        break
      end
    end
  end
  if acteur ~= nil then equipe.Suivre(acteur, hero) end
end
return M
