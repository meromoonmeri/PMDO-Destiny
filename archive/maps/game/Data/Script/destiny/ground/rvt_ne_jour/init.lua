-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local rvt_ne_jour = {}

function rvt_ne_jour.Init(map)
end

function rvt_ne_jour.Enter(map)
  GAME:FadeIn(30)
end

function rvt_ne_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function rvt_ne_jour.Update(map, time)
end

return rvt_ne_jour
