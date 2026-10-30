-- Quest destiny — point d'entrée du Ground « amp_plains_entrance ».
require 'origin.common'

local amp_plains_entrance = {}

function amp_plains_entrance.Init(map)
end

function amp_plains_entrance.Enter(map)
  GAME:FadeIn(20)
end

function amp_plains_entrance.GameLoad(map)
  GAME:FadeIn(20)
end

function amp_plains_entrance.Update(map, time)
end

return amp_plains_entrance
