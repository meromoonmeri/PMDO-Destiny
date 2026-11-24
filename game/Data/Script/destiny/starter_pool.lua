-- Liste commune au quiz de personnalité et au vestiaire.
local source = require 'destiny.ground.personality_test.starters_source'
local quiz = require 'destiny.ground.personality_test.quiz_data'
local M = {}

function M.construire(espece_exclue)
  local pool, deja_vu = {}, {}
  local function ajouter(s)
    local key = s.espece .. ':' .. tostring(s.forme)
    if s.espece ~= espece_exclue and not deja_vu[key] then
      deja_vu[key] = true
      table.insert(pool, s)
    end
  end
  for _, s in ipairs(source.starters) do ajouter(s) end
  for _, s in pairs(quiz.starters) do ajouter(s) end
  table.sort(pool, function(a, b)
    if a.gen ~= b.gen then return a.gen < b.gen end
    return a.nom < b.nom
  end)
  return pool
end

return M
