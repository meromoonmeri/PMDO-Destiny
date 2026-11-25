-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local eaz1_entree_zone_zero = {}

function eaz1_entree_zone_zero.Init(map)
end

function eaz1_entree_zone_zero.Enter(map)
  GAME:FadeIn(30)
end

function eaz1_entree_zone_zero.GameLoad(map)
  GAME:FadeIn(30)
end

function eaz1_entree_zone_zero.Update(map, time)
end

return eaz1_entree_zone_zero
