-- Quest destiny — point d'entrée du Ground « metano_gen_cafe ».
require 'origin.common'

local metano_gen_cafe = {}

function metano_gen_cafe.Init(map)
end

function metano_gen_cafe.Enter(map)
  GAME:FadeIn(20)
end

function metano_gen_cafe.GameLoad(map)
  GAME:FadeIn(20)
end

function metano_gen_cafe.Update(map, time)
end

return metano_gen_cafe
