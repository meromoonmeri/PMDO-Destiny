-- Quest destiny — point d'entrée du Ground « luminous_spring ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local luminous_spring = {}

function luminous_spring.Init(map)
end

function luminous_spring.Enter(map)
  GAME:FadeIn(20)
end

function luminous_spring.GameLoad(map)
  GAME:FadeIn(20)
end

function luminous_spring.Update(map, time)
end

return luminous_spring
