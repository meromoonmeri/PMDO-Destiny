-- PMD Destiny 0.7.7. Limit the normal follow camera, in native pixels.
-- No tile, map dimension, obstacle, marker or transition is altered.
local M = {}
local bords = {
  guilde_destiny_accueil        = {352, 384},
  guilde_destiny_missions       = {395, 432},
  guilde_destiny_grand_salon    = {383, 432},
  guilde_destiny_bureau_maitre  = {357, 384},
  guilde_destiny_cuisine        = {329, 360},
  guilde_destiny_dortoir_nord_1 = {313, 336},
  guilde_destiny_dortoir_nord_2 = {313, 336},
}
local marge = 8 -- walking/running reserve: stock character movement follows Update.

local function hauteur_vue()
  local g = RogueEssence.Content.GraphicsManager
  return g.ConvertZoom(g.Zoom, g.ScreenHeight, true)
end

function M.Attacher(script, salle)
  local bord = bords[salle]
  if not bord then return end
  local ancienInit, ancienEnter, ancienUpdate = script.Init, script.Enter, script.Update
  local ancienExit, ancienLoad, ancienSave = script.Exit, script.GameLoad, script.GameSave
  local x_pose, y_pose

  local function est_a_nous(c)
    return c ~= nil and x_pose ~= nil and c.X == x_pose and c.Y == y_pose
  end

  local function rendre_la_camera(map)
    if map ~= nil and est_a_nous(map.ViewCenter) then map.ViewCenter = nil end
    x_pose, y_pose = nil, nil
  end

  local function suivre(map)
    if map == nil or map.GroundHeight ~= bord[2] then return end
    local actuel = map.ViewCenter
    if actuel ~= nil and not est_a_nous(actuel) then
      -- A scene with an explicit camera keeps it; this patch only handles normal follow.
      x_pose, y_pose = nil, nil
      return
    end
    local joueur = map.ActiveChar
    if joueur == nil then rendre_la_camera(map); return end
    local h = hauteur_vue()
    if h <= 0 or h > bord[1] then rendre_la_camera(map); return end
    local centre = joueur.Bounds.Center
    local decalage = map.ViewOffset
    local x, y = centre.X + decalage.X, centre.Y + decalage.Y
    local maximum = bord[1] - math.ceil(h / 2)
    if y < maximum - marge then rendre_la_camera(map); return end
    -- Set a bounded center, rather than a negative player offset that could
    -- drift south on the last frame of a step or while a fade coroutine runs.
    y = math.min(y, maximum)
    if not est_a_nous(actuel) or x ~= x_pose or y ~= y_pose then
      map.ViewCenter = RogueElements.Loc(x, y)
      x_pose, y_pose = x, y
    end
  end

  script.Init = function(map, ...)
    x_pose, y_pose = nil, nil
    if ancienInit then ancienInit(map, ...) end
    suivre(map)
  end
  script.Enter = function(map, ...)
    suivre(map)
    if ancienEnter then return ancienEnter(map, ...) end
  end
  script.GameLoad = function(map, ...)
    suivre(map)
    if ancienLoad then return ancienLoad(map, ...) end
  end
  script.Update = function(map, ...)
    if ancienUpdate then ancienUpdate(map, ...) end
    suivre(map)
  end
  script.Exit = function(map, ...)
    rendre_la_camera(map)
    if ancienExit then return ancienExit(map, ...) end
  end
  script.GameSave = function(map, ...)
    rendre_la_camera(map)
    if ancienSave then return ancienSave(map, ...) end
  end
end

return M
