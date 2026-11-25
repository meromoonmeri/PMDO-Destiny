-- Point d'entrée de la map technique Destiny.
require 'origin.common'

local destiny_hub = {}

function destiny_hub.Init(map)
end

function destiny_hub.Enter(map)
  GAME:FadeIn(30)
  SV.destiny = SV.destiny or { Welcomed = false }
  if not SV.destiny.Welcomed then
    UI:ResetSpeaker()
    UI:WaitShowDialogue('Bienvenue dans Pokémon Mystery Dungeon : Destiny !')
    UI:WaitShowDialogue('Cette clairière est le point de départ technique de ton futur fangame.')
    SV.destiny.Welcomed = true
  end
end

function destiny_hub.GameLoad(map)
  GAME:FadeIn(30)
end

function destiny_hub.Update(map, time)
end

return destiny_hub
