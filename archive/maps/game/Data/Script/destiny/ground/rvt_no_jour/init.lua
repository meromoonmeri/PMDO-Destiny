-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local rvt_no_jour = {}

function rvt_no_jour.Init(map)
end

function rvt_no_jour.Enter(map)
  GAME:FadeIn(30)
end

function rvt_no_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function rvt_no_jour.Update(map, time)
end

return rvt_no_jour
