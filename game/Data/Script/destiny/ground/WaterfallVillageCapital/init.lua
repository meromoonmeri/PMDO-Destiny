-- Quest destiny — point d'entrée du Ground « WaterfallVillageCapital ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local WaterfallVillageCapital = {}

function WaterfallVillageCapital.Init(map)
end

function WaterfallVillageCapital.Enter(map)
  GAME:FadeIn(20)
end

function WaterfallVillageCapital.GameLoad(map)
  GAME:FadeIn(20)
end

function WaterfallVillageCapital.Update(map, time)
end

return WaterfallVillageCapital
