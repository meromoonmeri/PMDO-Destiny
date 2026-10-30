-- Quest destiny — point d'entrée du Ground « Brine_Cave_Entrance ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local Brine_Cave_Entrance = {}

function Brine_Cave_Entrance.Init(map)
end

function Brine_Cave_Entrance.Enter(map)
  GAME:FadeIn(20)
end

function Brine_Cave_Entrance.GameLoad(map)
  GAME:FadeIn(20)
end

function Brine_Cave_Entrance.Update(map, time)
end

return Brine_Cave_Entrance
