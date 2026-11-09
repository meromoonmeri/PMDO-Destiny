-- Espace technique pour préserver les indices et récupérer les parties anciennes.
require 'origin.common'
local guild_heros_room = {}
local sortie_en_cours = false
local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  SV.Destiny.RetourBatimentX = 800
  SV.Destiny.RetourBatimentY = 1160
  GAME:FadeOut(false, 1)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end
function guild_heros_room.Init(map) end
function guild_heros_room.Enter(map) sortir() end
function guild_heros_room.GameLoad(map) sortir() end
function guild_heros_room.Update(map, time) end
function guild_heros_room.Bedroom_Exit_Touch(obj, activator) sortir() end
return guild_heros_room
