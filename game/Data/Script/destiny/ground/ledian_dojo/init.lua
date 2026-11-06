-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local ledian_dojo = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function ledian_dojo.Init(map) end
function ledian_dojo.Enter(map) sortie_en_cours = false; GAME:FadeIn(20) end
function ledian_dojo.GameLoad(map) sortie_en_cours = false; GAME:FadeIn(20) end
function ledian_dojo.Update(map, time) end
function ledian_dojo.Dojo_Exit_Touch(obj, activator) sortir() end

function ledian_dojo.Sensei_Action(chara, activator)
  UI:SetSpeaker(chara); UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Un bon explorateur écoute d’abord le rythme de ses pas. Ensuite seulement, il frappe.')
  UI:ResetSpeaker()
end
function ledian_dojo.Gible_Action(chara, activator)
  UI:SetSpeaker(chara); UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Je m’entraîne tous les jours ! Un jour, je traverserai les Bois Perdus sans trembler.')
  UI:ResetSpeaker()
end
function ledian_dojo.Dungeon_Entrance_Touch(obj, activator) end

return ledian_dojo
