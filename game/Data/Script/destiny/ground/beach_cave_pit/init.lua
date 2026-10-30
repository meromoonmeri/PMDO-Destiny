-- Quest destiny — point d'entrée du Ground « beach_cave_pit ».
require 'origin.common'

local beach_cave_pit = {}

function beach_cave_pit.Init(map)
end

function beach_cave_pit.Enter(map)
  GAME:FadeIn(20)
end

function beach_cave_pit.GameLoad(map)
  GAME:FadeIn(20)
end

function beach_cave_pit.Update(map, time)
end

return beach_cave_pit
