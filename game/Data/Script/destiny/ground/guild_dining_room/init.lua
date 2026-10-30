-- Quest destiny — point d'entrée du Ground « guild_dining_room ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_dining_room = {}

function guild_dining_room.Init(map)
end

function guild_dining_room.Enter(map)
  GAME:FadeIn(20)
end

function guild_dining_room.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_dining_room.Update(map, time)
end

return guild_dining_room
