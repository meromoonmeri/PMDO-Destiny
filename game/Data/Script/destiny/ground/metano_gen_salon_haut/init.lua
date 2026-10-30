-- Quest destiny — point d'entrée du Ground « metano_gen_salon_haut ».
require 'origin.common'

local metano_gen_salon_haut = {}

function metano_gen_salon_haut.Init(map)
end

function metano_gen_salon_haut.Enter(map)
  GAME:FadeIn(20)
end

function metano_gen_salon_haut.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_gen_salon_haut.Update(map, time)
end

return metano_gen_salon_haut
