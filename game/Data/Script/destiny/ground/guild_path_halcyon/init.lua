-- Quest destiny — point d'entrée du Ground « guild_path_halcyon ».
require 'origin.common'

local guild_path_halcyon = {}

function guild_path_halcyon.Init(map)
end

function guild_path_halcyon.Enter(map)
  GAME:FadeIn(20)
end

function guild_path_halcyon.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_path_halcyon.Update(map, time)
end

return guild_path_halcyon
