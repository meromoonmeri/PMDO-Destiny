-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cote_v2_terrasse = {}

function cote_v2_terrasse.Init(map)
end

function cote_v2_terrasse.Enter(map)
  GAME:FadeIn(30)
end

function cote_v2_terrasse.GameLoad(map)
  GAME:FadeIn(30)
end

function cote_v2_terrasse.Update(map, time)
end

return cote_v2_terrasse
