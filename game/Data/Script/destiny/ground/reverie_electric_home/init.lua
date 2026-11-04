-- Intérieur Réverie raccordé à Réverie Town (Destiny), coque vide.
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local reverie_electric_home = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function reverie_electric_home.Init(map) end
function reverie_electric_home.Enter(map) GAME:FadeIn(20) end
function reverie_electric_home.GameLoad(map) GAME:FadeIn(20) end
function reverie_electric_home.Update(map, time) end
function reverie_electric_home.Electric_Home_Entrance_Touch(obj, activator) sortir() end

return reverie_electric_home
