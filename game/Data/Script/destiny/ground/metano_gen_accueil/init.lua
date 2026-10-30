-- Quest destiny — point d'entrée du Ground « metano_gen_accueil ».
require 'origin.common'

local metano_gen_accueil = {}

function metano_gen_accueil.Init(map)
end

function metano_gen_accueil.Enter(map)
  GAME:FadeIn(20)
end

function metano_gen_accueil.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_gen_accueil.Update(map, time)
end

return metano_gen_accueil
