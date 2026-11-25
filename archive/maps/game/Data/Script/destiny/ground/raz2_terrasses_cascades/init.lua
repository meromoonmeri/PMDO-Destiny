-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local raz2_terrasses_cascades = {}

function raz2_terrasses_cascades.Init(map)
end

function raz2_terrasses_cascades.Enter(map)
  GAME:FadeIn(30)
end

function raz2_terrasses_cascades.GameLoad(map)
  GAME:FadeIn(30)
end

function raz2_terrasses_cascades.Update(map, time)
end

return raz2_terrasses_cascades
