--[[
  guilde_reveil.lua — la tournée du matin de Mélofée.

  Mélofée réveille la Guilde « à la Audino » : le corps prend la pose de service
  (PoseGroundAction, comme la pose d'Audino dans Halcyon), la cloche `reveil`
  sonne au-dessus de sa tête, le dormeur passe de `Sleep` à `Wake`, puis le
  calot de service (`pose_infirmiere`) reprend sa place.

  Contrainte du moteur : un personnage ne porte qu'UNE émote à la fois
  (`GroundChar.StartEmote` remplace la précédente). La cloche et le calot sont
  donc joués l'un après l'autre, jamais ensemble.
]]

require 'origin.common'
local guilde_effectif = require 'destiny.guilde_effectif'

local guilde_reveil = {}

guilde_reveil.SONNERIES = 2        -- cycles de cloche par réveil
guilde_reveil.SOMMEIL = 30         -- images de sommeil avant la cloche
guilde_reveil.SONNERIE = 64         -- 2 cycles de cloche de 32 images
guilde_reveil.REVEIL = 24          -- images de « Wake » avant de se relever

--[[
  Réveille un dormeur.
  `infirmiere` : Mélofée (peut être nil pour un réveil sans elle).
  `dormeur`    : le personnage à réveiller.
  `options`    : {sonneries, sommeil, sonnerie, reveil}
]]
function guilde_reveil.Reveiller(infirmiere, dormeur, options)
  options = options or {}
  local sonneries = options.sonneries or guilde_reveil.SONNERIES

  -- 1. le dormeur s'installe dans son sommeil (ou garde son attente)
  if dormeur ~= nil then
    guilde_effectif.Animer(dormeur, 'Sleep', true)
    GAME:WaitFrames(options.sommeil or guilde_reveil.SOMMEIL)
  end

  -- 2. Mélofée prend sa pose et fait sonner la cloche
  if infirmiere ~= nil then
    guilde_effectif.Poser(infirmiere, false)       -- corps en pose, sans calot
    pcall(function()
      GROUND:CharSetEmote(infirmiere, guilde_effectif.EMOTE_REVEIL, sonneries)
    end)
  end
  GAME:WaitFrames(options.sonnerie or guilde_reveil.SONNERIE)

  -- 3. le dormeur se réveille : « Wake » s'il l'a, sinon un sursaut
  if dormeur ~= nil then
    if not guilde_effectif.Animer(dormeur, 'Wake', true) then
      pcall(function() GROUND:CharSetEmote(dormeur, 'exclaim', 1) end)
    end
  end
  GAME:WaitFrames(options.reveil or guilde_reveil.REVEIL)

  -- 4. retours : le dormeur se relève, la cloche laisse la place au calot
  if dormeur ~= nil then
    guilde_effectif.Deposer(dormeur)
  end
  if infirmiere ~= nil then
    pcall(function() GROUND:CharSetEmote(infirmiere, '', 0) end)
    guilde_effectif.Poser(infirmiere, true)        -- le calot de service reprend
  end
  return true
end

--[[
  Tournée du matin : passe sur les membres présents, dans l'ordre de l'effectif,
  en sautant l'infirmière et les absents. `options.pause` ajoute un répit entre
  deux réveils.
]]
function guilde_reveil.Tournee(infirmiere, liste, options)
  options = options or {}
  local dormeurs = guilde_effectif.Acteurs(liste)
  local reveilles = 0
  for _, entree in ipairs(dormeurs) do
    if infirmiere == nil or entree.acteur ~= infirmiere then
      guilde_reveil.Reveiller(infirmiere, entree.acteur, options)
      reveilles = reveilles + 1
      local pause = options.pause
      if pause ~= nil and pause > 0 then GAME:WaitFrames(pause) end
    end
  end
  return reveilles
end

return guilde_reveil
