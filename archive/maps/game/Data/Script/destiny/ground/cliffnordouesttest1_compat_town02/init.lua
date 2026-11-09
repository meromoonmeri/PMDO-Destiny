-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local cliffnordouesttest1_compat_town02 = {}

function cliffnordouesttest1_compat_town02.Init(map)
end

function cliffnordouesttest1_compat_town02.Enter(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_compat_town02.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffnordouesttest1_compat_town02.Update(map, time)
end

return cliffnordouesttest1_compat_town02
