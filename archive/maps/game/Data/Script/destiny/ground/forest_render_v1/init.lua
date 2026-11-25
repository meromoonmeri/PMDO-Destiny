-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local forest_render_v1 = {}

function forest_render_v1.Init(map)
end

function forest_render_v1.Enter(map)
  GAME:FadeIn(30)
end

function forest_render_v1.GameLoad(map)
  GAME:FadeIn(30)
end

function forest_render_v1.Update(map, time)
end

return forest_render_v1
