-- Quest destiny — point d'entrée du Ground « guild_bottom_right_bedroom ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_bottom_right_bedroom = {}

function guild_bottom_right_bedroom.Init(map)
end

function guild_bottom_right_bedroom.Enter(map)
  GAME:FadeIn(20)
end

function guild_bottom_right_bedroom.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_bottom_right_bedroom.Update(map, time)
end

return guild_bottom_right_bedroom
