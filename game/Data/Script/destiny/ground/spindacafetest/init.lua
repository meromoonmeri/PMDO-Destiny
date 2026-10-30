-- Quest destiny — point d'entrée du Ground « spindacafetest ».
require 'origin.common'

local spindacafetest = {}

function spindacafetest.Init(map)
end

function spindacafetest.Enter(map)
  GAME:FadeIn(20)
end

function spindacafetest.GameLoad(map)
  GAME:FadeIn(20)
end

function spindacafetest.Update(map, time)
end

return spindacafetest
