-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffnordouesttest1 = {}

function cliffnordouesttest1.Init(map)
end

function cliffnordouesttest1.Enter(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1.Update(map, time)
end

return cliffnordouesttest1
