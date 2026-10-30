-- Quest destiny — point d'entrée du Ground « metano_gen_salon_bas ».
require 'origin.common'

local metano_gen_salon_bas = {}

function metano_gen_salon_bas.Init(map)
end

function metano_gen_salon_bas.Enter(map)
  GAME:FadeIn(20)
end

function metano_gen_salon_bas.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_gen_salon_bas.Update(map, time)
end

return metano_gen_salon_bas
