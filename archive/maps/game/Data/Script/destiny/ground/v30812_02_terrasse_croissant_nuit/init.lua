-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local v30812_02_terrasse_croissant_nuit = {}

function v30812_02_terrasse_croissant_nuit.Init(map)
end

function v30812_02_terrasse_croissant_nuit.Enter(map)
  GAME:FadeIn(30)
end

function v30812_02_terrasse_croissant_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function v30812_02_terrasse_croissant_nuit.Update(map, time)
end

return v30812_02_terrasse_croissant_nuit
