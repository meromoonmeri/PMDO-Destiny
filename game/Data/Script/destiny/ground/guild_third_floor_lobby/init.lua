-- Quest destiny — point d'entrée du Ground « guild_third_floor_lobby ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_third_floor_lobby = {}

function guild_third_floor_lobby.Init(map)
end

function guild_third_floor_lobby.Enter(map)
  GAME:FadeIn(20)
end

function guild_third_floor_lobby.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_third_floor_lobby.Update(map, time)
end

return guild_third_floor_lobby
