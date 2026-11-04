-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cote_v2_promontoire = {}

function cote_v2_promontoire.Init(map)
end

function cote_v2_promontoire.Enter(map)
  GAME:FadeIn(30)
end

function cote_v2_promontoire.GameLoad(map)
  GAME:FadeIn(30)
end

function cote_v2_promontoire.Update(map, time)
end

return cote_v2_promontoire
