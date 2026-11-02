-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local guild_storage_room = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function guild_storage_room.Init(map) end
function guild_storage_room.Enter(map) GAME:FadeIn(20) end
function guild_storage_room.GameLoad(map) GAME:FadeIn(20) end
function guild_storage_room.Update(map, time) end
function guild_storage_room.Left_Exit_Touch(obj, activator) sortir() end

return guild_storage_room
