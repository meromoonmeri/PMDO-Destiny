-- Quest destiny — point d'entrée du Ground « vast_steppe_entrance ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local vast_steppe_entrance = {}

function vast_steppe_entrance.Init(map)
end

function vast_steppe_entrance.Enter(map)
  GAME:FadeIn(20)
end

function vast_steppe_entrance.GameLoad(map)
  GAME:FadeIn(20)
end

function vast_steppe_entrance.Update(map, time)
end

return vast_steppe_entrance
