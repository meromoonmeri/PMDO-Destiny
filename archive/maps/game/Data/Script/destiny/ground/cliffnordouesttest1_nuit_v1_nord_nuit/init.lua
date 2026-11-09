-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffnordouesttest1_nuit_v1_nord_nuit = {}

function cliffnordouesttest1_nuit_v1_nord_nuit.Init(map)
end

function cliffnordouesttest1_nuit_v1_nord_nuit.Enter(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_nuit_v1_nord_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_nuit_v1_nord_nuit.Update(map, time)
end

return cliffnordouesttest1_nuit_v1_nord_nuit
