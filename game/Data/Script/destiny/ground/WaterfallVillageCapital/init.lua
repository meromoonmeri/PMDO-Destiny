-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local WaterfallVillageCapital = {}

function WaterfallVillageCapital.Init(map)
end

function WaterfallVillageCapital.Enter(map)
  GAME:FadeIn(30)
end

function WaterfallVillageCapital.GameLoad(map)
  GAME:FadeIn(30)
end

function WaterfallVillageCapital.Update(map, time)
end

return WaterfallVillageCapital
