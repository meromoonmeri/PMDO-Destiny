-- Quest destiny — point d'entrée du Ground « guild_bottom_left_bedroom ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_bottom_left_bedroom = {}

function guild_bottom_left_bedroom.Init(map)
end

function guild_bottom_left_bedroom.Enter(map)
  GAME:FadeIn(20)
end

function guild_bottom_left_bedroom.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_bottom_left_bedroom.Update(map, time)
end

return guild_bottom_left_bedroom
