-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local etc1_tour_celeste = {}

function etc1_tour_celeste.Init(map)
end

function etc1_tour_celeste.Enter(map)
  GAME:FadeIn(30)
end

function etc1_tour_celeste.GameLoad(map)
  GAME:FadeIn(30)
end

function etc1_tour_celeste.Update(map, time)
end

return etc1_tour_celeste
