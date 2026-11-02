-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local metano_grass_home = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function metano_grass_home.Init(map) end
function metano_grass_home.Enter(map) GAME:FadeIn(20) end
function metano_grass_home.GameLoad(map) GAME:FadeIn(20) end
function metano_grass_home.Update(map, time) end
function metano_grass_home.Grass_Home_Entrance_Touch(obj, activator) sortir() end

return metano_grass_home
