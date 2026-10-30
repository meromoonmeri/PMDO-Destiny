-- Quest destiny — point d'entrée du Ground « altere_pond ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local altere_pond = {}

function altere_pond.Init(map)
end

function altere_pond.Enter(map)
  GAME:FadeIn(20)
end

function altere_pond.GameLoad(map)
  GAME:FadeIn(20)
end

function altere_pond.Update(map, time)
end

return altere_pond
