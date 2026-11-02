-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local dojo_ossatueur = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function dojo_ossatueur.Init(map) end
function dojo_ossatueur.Enter(map) GAME:FadeIn(20) end
function dojo_ossatueur.GameLoad(map) GAME:FadeIn(20) end
function dojo_ossatueur.Update(map, time) end
function dojo_ossatueur.MarowakDojoExit_Touch(obj, activator) sortir() end

function dojo_ossatueur.Marowak_Action(chara, activator)
  UI:SetSpeaker(chara); UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Ici, on apprend la patience du geste juste. Un marteau, une enclume ou un os : tout demande la même précision.')
  UI:ResetSpeaker()
end
function dojo_ossatueur.MarowakDojoDungeonEntrance_Touch(obj, activator) end

return dojo_ossatueur
