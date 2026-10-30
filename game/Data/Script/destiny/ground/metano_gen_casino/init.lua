-- Quest destiny — point d'entrée du Ground « metano_gen_casino ».
require 'origin.common'

local metano_gen_casino = {}

function metano_gen_casino.Init(map)
end

function metano_gen_casino.Enter(map)
  GAME:FadeIn(20)
end

function metano_gen_casino.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_gen_casino.Update(map, time)
end

return metano_gen_casino
