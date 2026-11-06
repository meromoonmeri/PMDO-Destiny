-- Hutte aquatique sud raccordée à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local reverie_hutte_aquatique = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function reverie_hutte_aquatique.Init(map) end
function reverie_hutte_aquatique.Enter(map) sortie_en_cours = false; GAME:FadeIn(20) end
function reverie_hutte_aquatique.GameLoad(map) sortie_en_cours = false; GAME:FadeIn(20) end
function reverie_hutte_aquatique.Update(map, time) end
function reverie_hutte_aquatique.Water_Home_Entrance_Touch(obj, activator) sortir() end

return reverie_hutte_aquatique
