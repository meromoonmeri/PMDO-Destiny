-- Intérieur Réverie raccordé à Réverie Town (Destiny), coque vide.
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local reverie_normal_home = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function reverie_normal_home.Init(map) end
function reverie_normal_home.Enter(map) suivi_interieurs.Activer(map); GAME:FadeIn(20) end
function reverie_normal_home.GameLoad(map) suivi_interieurs.Activer(map); GAME:FadeIn(20) end
function reverie_normal_home.Update(map, time) end
function reverie_normal_home.Normal_Home_Entrance_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  sortir()
end

return reverie_normal_home
