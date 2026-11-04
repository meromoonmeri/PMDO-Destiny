-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local raz3_fond_cristallin = {}

function raz3_fond_cristallin.Init(map)
end

function raz3_fond_cristallin.Enter(map)
  GAME:FadeIn(30)
end

function raz3_fond_cristallin.GameLoad(map)
  GAME:FadeIn(30)
end

function raz3_fond_cristallin.Update(map, time)
end

return raz3_fond_cristallin
