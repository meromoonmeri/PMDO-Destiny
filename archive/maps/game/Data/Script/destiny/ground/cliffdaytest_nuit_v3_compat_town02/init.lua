-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffdaytest_nuit_v3_compat_town02 = {}

function cliffdaytest_nuit_v3_compat_town02.Init(map)
end

function cliffdaytest_nuit_v3_compat_town02.Enter(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v3_compat_town02.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit_v3_compat_town02.Update(map, time)
end

return cliffdaytest_nuit_v3_compat_town02
