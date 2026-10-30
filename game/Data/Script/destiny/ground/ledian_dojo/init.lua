-- Quest destiny — point d'entrée du Ground « ledian_dojo ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local ledian_dojo = {}

function ledian_dojo.Init(map)
end

function ledian_dojo.Enter(map)
  GAME:FadeIn(20)
end

function ledian_dojo.GameLoad(map)
  GAME:FadeIn(20)
end

function ledian_dojo.Update(map, time)
end

return ledian_dojo
