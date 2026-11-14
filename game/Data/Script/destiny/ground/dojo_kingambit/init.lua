-- Dojo Kingambit : intérieur raccordé à Réverie Town (Destiny).
-- Clone du dojo de l'Ossatueur (town02) reskinné aux couleurs de Kingambit ;
-- les objets et marqueurs sérialisés (MarowakDojo*) sont conservés tels quels
-- pour rester compatibles avec la porte installée côté ville.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local dojo_kingambit = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

local function nommer_maitre()
  local acteur = CH('Kingambit')
  if acteur ~= nil and acteur.Data ~= nil then acteur.Data.Nickname = 'Kaito' end
end
function dojo_kingambit.Init(map) nommer_maitre() end
function dojo_kingambit.Enter(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit.GameLoad(map) nommer_maitre(); suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit.Update(map, time) end
function dojo_kingambit.MarowakDojoExit_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  sortir()
end

function dojo_kingambit.Kingambit_Action(chara, activator)
  UI:SetSpeaker(chara); UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue("Bienvenue au Dojo Kingambit. Ici, chaque pas compte : on n'entre pas dans l'arène sans savoir pourquoi l'on avance.")
  UI:WaitShowDialogue("Observe, respire, puis frappe juste. La lame la plus forte est celle qui ne tremble pas.")
  UI:ResetSpeaker()
end
function dojo_kingambit.MarowakDojoDungeonEntrance_Touch(obj, activator) end
function dojo_kingambit.KingambitDojoNorthDoorRight_Touch(obj, activator) end

return dojo_kingambit
