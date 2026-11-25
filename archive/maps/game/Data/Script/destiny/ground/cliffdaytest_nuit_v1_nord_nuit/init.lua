-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffdaytest_nuit_v1_nord_nuit = {}

function cliffdaytest_nuit_v1_nord_nuit.Init(map)
end

function cliffdaytest_nuit_v1_nord_nuit.Enter(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v1_nord_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v1_nord_nuit.Update(map, time)
end

return cliffdaytest_nuit_v1_nord_nuit
