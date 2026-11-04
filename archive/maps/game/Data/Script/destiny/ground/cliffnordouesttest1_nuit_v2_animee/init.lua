-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffnordouesttest1_nuit_v2_animee = {}

function cliffnordouesttest1_nuit_v2_animee.Init(map)
end

function cliffnordouesttest1_nuit_v2_animee.Enter(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_nuit_v2_animee.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_nuit_v2_animee.Update(map, time)
end

return cliffnordouesttest1_nuit_v2_animee
