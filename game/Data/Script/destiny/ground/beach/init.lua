-- Quest destiny — point d'entrée du Ground « beach ».
require 'origin.common'

local beach = {}

function beach.Init(map)
end

function beach.Enter(map)
  GAME:FadeIn(20)
end

function beach.GameLoad(map)
  GAME:FadeIn(20)
end

function beach.Update(map, time)
end

return beach
