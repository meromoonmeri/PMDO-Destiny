-- Quest destiny — point d'entrée du Ground « forest_magenta_v1 ».
require 'origin.common'

local forest_magenta_v1 = {}

function forest_magenta_v1.Init(map)
end

function forest_magenta_v1.Enter(map)
  GAME:FadeIn(20)
end

function forest_magenta_v1.GameLoad(map)
  GAME:FadeIn(20)
end

function forest_magenta_v1.Update(map, time)
end

return forest_magenta_v1
