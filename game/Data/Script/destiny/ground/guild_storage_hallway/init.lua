-- Quest destiny — point d'entrée du Ground « guild_storage_hallway ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_storage_hallway = {}

function guild_storage_hallway.Init(map)
end

function guild_storage_hallway.Enter(map)
  GAME:FadeIn(20)
end

function guild_storage_hallway.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_storage_hallway.Update(map, time)
end

return guild_storage_hallway
