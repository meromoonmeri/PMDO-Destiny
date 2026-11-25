-- Carte d’édition : aucune modification de scénario ni destination jouable.
require 'origin.common'
local carte = {}
function carte.Init(map) end
function carte.Enter(map) GAME:FadeIn(20) end
function carte.GameLoad(map) GAME:FadeIn(20) end
function carte.Update(map, time) end
return carte
