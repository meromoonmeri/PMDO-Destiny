-- Quest destiny — point d'entrée du Ground « crooked_cavern_entrance ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local crooked_cavern_entrance = {}

function crooked_cavern_entrance.Init(map)
end

function crooked_cavern_entrance.Enter(map)
  GAME:FadeIn(20)
end

function crooked_cavern_entrance.GameLoad(map)
  GAME:FadeIn(20)
end

function crooked_cavern_entrance.Update(map, time)
end

return crooked_cavern_entrance
