-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local guild_heros_room = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function guild_heros_room.Init(map) end
function guild_heros_room.Enter(map) GAME:FadeIn(20) end
function guild_heros_room.GameLoad(map) GAME:FadeIn(20) end
function guild_heros_room.Update(map, time) end
function guild_heros_room.Bedroom_Exit_Touch(obj, activator) sortir() end

function guild_heros_room.Book_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue('[i]Un journal d’exploration, encore plein de pages blanches. Les prochaines aventures de l’équipe y trouveront leur place.')
end
function guild_heros_room.Save_Point_Touch(obj, activator) end

return guild_heros_room
