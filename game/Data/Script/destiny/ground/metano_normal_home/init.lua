-- Quest destiny — point d'entrée du Ground « metano_normal_home ».
require 'origin.common'

local metano_normal_home = {}

function metano_normal_home.Init(map)
end

function metano_normal_home.Enter(map)
  GAME:FadeIn(20)
end

function metano_normal_home.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_normal_home.Update(map, time)
end

return metano_normal_home
