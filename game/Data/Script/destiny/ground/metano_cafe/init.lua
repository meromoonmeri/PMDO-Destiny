-- Quest destiny — point d'entrée du Ground « metano_cafe ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local metano_cafe = {}

function metano_cafe.Init(map)
end

function metano_cafe.Enter(map)
  GAME:FadeIn(20)
end

function metano_cafe.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_cafe.Update(map, time)
end

return metano_cafe
