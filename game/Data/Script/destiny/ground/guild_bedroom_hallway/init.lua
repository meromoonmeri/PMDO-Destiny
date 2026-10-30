-- Quest destiny — point d'entrée du Ground « guild_bedroom_hallway ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guild_bedroom_hallway = {}

function guild_bedroom_hallway.Init(map)
end

function guild_bedroom_hallway.Enter(map)
  GAME:FadeIn(20)
end

function guild_bedroom_hallway.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_bedroom_hallway.Update(map, time)
end

return guild_bedroom_hallway
