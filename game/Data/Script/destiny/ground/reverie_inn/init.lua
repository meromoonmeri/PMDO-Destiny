-- Intérieur Réverie raccordé à Réverie Town (Destiny), coque vide.
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local reverie_inn = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function reverie_inn.Init(map) end
function reverie_inn.Enter(map) sortie_en_cours = false; GAME:FadeIn(20) end
function reverie_inn.GameLoad(map) sortie_en_cours = false; GAME:FadeIn(20) end
function reverie_inn.Update(map, time) end
function reverie_inn.Inn_Entrance_Touch(obj, activator) sortir() end

return reverie_inn
