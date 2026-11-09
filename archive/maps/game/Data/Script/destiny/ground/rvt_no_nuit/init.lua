-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local rvt_no_nuit = {}

function rvt_no_nuit.Init(map)
end

function rvt_no_nuit.Enter(map)
  GAME:FadeIn(30)
end

function rvt_no_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function rvt_no_nuit.Update(map, time)
end

return rvt_no_nuit
