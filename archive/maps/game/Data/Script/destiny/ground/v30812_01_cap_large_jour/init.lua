-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local v30812_01_cap_large_jour = {}

function v30812_01_cap_large_jour.Init(map)
end

function v30812_01_cap_large_jour.Enter(map)
  GAME:FadeIn(30)
end

function v30812_01_cap_large_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function v30812_01_cap_large_jour.Update(map, time)
end

return v30812_01_cap_large_jour
