-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffdaytest_nuit_v2_animee = {}

function cliffdaytest_nuit_v2_animee.Init(map)
end

function cliffdaytest_nuit_v2_animee.Enter(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v2_animee.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v2_animee.Update(map, time)
end

return cliffdaytest_nuit_v2_animee
