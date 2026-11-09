-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local rvt_ne_nuit = {}

function rvt_ne_nuit.Init(map)
end

function rvt_ne_nuit.Enter(map)
  GAME:FadeIn(30)
end

function rvt_ne_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function rvt_ne_nuit.Update(map, time)
end

return rvt_ne_nuit
