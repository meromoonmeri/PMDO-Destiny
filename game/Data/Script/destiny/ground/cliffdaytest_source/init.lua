-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffdaytest_source = {}

function cliffdaytest_source.Init(map)
end

function cliffdaytest_source.Enter(map)
  GAME:FadeIn(30)
end

function cliffdaytest_source.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffdaytest_source.Update(map, time)
end

return cliffdaytest_source
