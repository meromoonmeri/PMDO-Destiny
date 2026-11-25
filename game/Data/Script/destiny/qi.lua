-- QI individuel pour les Mégaévolutions de Destiny.
-- Le stockage est propre à chaque Character (LuaData sérialisé par PMDO).
-- Les gains reprennent la formule documentée d'Explorers of Sky ; leur
-- identité exacte avec source 2.3.28 reste à confirmer dans la ROM.
local M = {}
M.SEUIL_MEGA = 410
M.MAX_QI = 999

function M.lire(pokemon)
  local table_perso = LTBL(pokemon)
  if not table_perso then return 0 end
  return math.max(0, math.min(M.MAX_QI, tonumber(table_perso.DestinyQI) or 0))
end

function M.ajouter(pokemon, points)
  local table_perso = LTBL(pokemon)
  if not table_perso then return 0 end
  local avant = M.lire(pokemon)
  table_perso.DestinyQI = math.min(M.MAX_QI, avant + math.max(0, math.floor(points)))
  return table_perso.DestinyQI - avant
end

-- Une gelée de même type donne 5 points ; sinon super efficace 4,
-- neutre 3, résistée 2 et immunisée 1. Pour deux types on prend le
-- meilleur résultat, pas la somme. Gelée Miracle : 15 points.
function M.points_gelee(pokemon, element)
  if element == 'wonder' then return 15 end
  local mon = _DATA:GetMonster(pokemon.BaseForm.Species)
  local forme = mon.Forms[pokemon.BaseForm.Form]
  local type1, type2 = forme.Element1, forme.Element2
  if element == type1 or element == type2 then return 5 end

  local calc = PMDC.Dungeon.PreTypeEvent.CalculateTypeMatchup
  local neutre = calc('normal', 'normal')
  local immunite = calc('normal', 'ghost')
  local function score(defense)
    if not defense or defense == '' or defense == 'none' then return 0 end
    local eff = calc(element, defense)
    if eff == immunite then return 1 end
    if eff > neutre then return 4 end
    if eff == neutre then return 3 end
    return 2
  end
  return math.max(score(type1), score(type2))
end

function M.gelee(pokemon, element)
  if not pokemon or not element then return 0 end
  return M.ajouter(pokemon, M.points_gelee(pokemon, element))
end

return M
