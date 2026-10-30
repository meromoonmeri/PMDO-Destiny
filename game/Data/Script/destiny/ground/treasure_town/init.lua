-- Quest destiny — point d'entrée du Ground « treasure_town ».
require 'origin.common'

local treasure_town = {}

function treasure_town.Init(map)
end

function treasure_town.Enter(map)
  GAME:FadeIn(20)
end

function treasure_town.GameLoad(map)
  GAME:FadeIn(20)
end

function treasure_town.Update(map, time)
end

return treasure_town
