-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local caféspindaaccueil = {}

function caféspindaaccueil.Init(map)
end

function caféspindaaccueil.Enter(map)
  GAME:FadeIn(30)
end

function caféspindaaccueil.GameLoad(map)
  GAME:FadeIn(30)
end

function caféspindaaccueil.Update(map, time)
end

return caféspindaaccueil
