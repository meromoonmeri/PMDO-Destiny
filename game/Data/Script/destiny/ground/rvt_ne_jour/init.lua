-- Quest destiny — point d'entrée du Ground « rvt_ne_jour ».
require 'origin.common'

local rvt_ne_jour = {}

function rvt_ne_jour.Init(map)
end

function rvt_ne_jour.Enter(map)
  GAME:FadeIn(20)
end

function rvt_ne_jour.GameLoad(map)
  GAME:FadeIn(20)
end

function rvt_ne_jour.Update(map, time)
end

return rvt_ne_jour
