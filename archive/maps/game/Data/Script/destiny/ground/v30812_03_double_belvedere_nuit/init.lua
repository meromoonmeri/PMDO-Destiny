-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local v30812_03_double_belvedere_nuit = {}

function v30812_03_double_belvedere_nuit.Init(map)
end

function v30812_03_double_belvedere_nuit.Enter(map)
  GAME:FadeIn(30)
end

function v30812_03_double_belvedere_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function v30812_03_double_belvedere_nuit.Update(map, time)
end

return v30812_03_double_belvedere_nuit
