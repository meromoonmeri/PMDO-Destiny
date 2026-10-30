-- Quest destiny — point d'entrée du Ground « guild_first_floor ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_first_floor = {}

function guild_first_floor.Init(map)
end

function guild_first_floor.Enter(map)
  GAME:FadeIn(20)
end

function guild_first_floor.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_first_floor.Update(map, time)
end

return guild_first_floor
