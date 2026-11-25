-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local spindacafetest = {}

function spindacafetest.Init(map)
end

function spindacafetest.Enter(map)
  GAME:FadeIn(30)
end

function spindacafetest.GameLoad(map)
  GAME:FadeIn(30)
end

function spindacafetest.Update(map, time)
end

return spindacafetest
