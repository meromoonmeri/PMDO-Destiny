-- Quest destiny — point d'entrée du Ground « drenched_bluff_entrance ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local drenched_bluff_entrance = {}

function drenched_bluff_entrance.Init(map)
end

function drenched_bluff_entrance.Enter(map)
  GAME:FadeIn(20)
end

function drenched_bluff_entrance.GameLoad(map)
  GAME:FadeIn(20)
end

function drenched_bluff_entrance.Update(map, time)
end

return drenched_bluff_entrance
