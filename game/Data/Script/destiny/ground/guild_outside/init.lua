-- Quest destiny — point d'entrée du Ground « guild_outside ».
require 'origin.common'

local guild_outside = {}

function guild_outside.Init(map)
end

function guild_outside.Enter(map)
  GAME:FadeIn(20)
end

function guild_outside.GameLoad(map)
  GAME:FadeIn(20)
end

function guild_outside.Update(map, time)
end

return guild_outside
