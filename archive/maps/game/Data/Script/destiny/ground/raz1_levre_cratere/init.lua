-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local raz1_levre_cratere = {}

function raz1_levre_cratere.Init(map)
end

function raz1_levre_cratere.Enter(map)
  GAME:FadeIn(30)
end

function raz1_levre_cratere.GameLoad(map)
  GAME:FadeIn(30)
end

function raz1_levre_cratere.Update(map, time)
end

return raz1_levre_cratere
