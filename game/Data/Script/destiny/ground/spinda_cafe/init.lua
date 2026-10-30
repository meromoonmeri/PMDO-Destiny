-- Quest destiny — point d'entrée du Ground « spinda_cafe ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local spinda_cafe = {}

function spinda_cafe.Init(map)
end

function spinda_cafe.Enter(map)
  GAME:FadeIn(20)
end

function spinda_cafe.GameLoad(map)
  GAME:FadeIn(20)
end

function spinda_cafe.Update(map, time)
end

return spinda_cafe
