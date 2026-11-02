-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local metano_inn = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function metano_inn.Init(map) end
function metano_inn.Enter(map) GAME:FadeIn(20) end
function metano_inn.GameLoad(map) GAME:FadeIn(20) end
function metano_inn.Update(map, time) end
function metano_inn.Inn_Entrance_Touch(obj, activator) sortir() end

local function comptoir()
  UI:ResetSpeaker()
  UI:WaitShowDialogue('Le comptoir de l’auberge est libre un instant. Les lits de paille attendent les équipes fatiguées.')
end
function metano_inn.Innkeeper_Desk_Left_Action(obj, activator) comptoir() end
function metano_inn.Innkeeper_Desk_Right_Action(obj, activator) comptoir() end

return metano_inn
