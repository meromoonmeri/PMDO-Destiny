-- Dojo Kingambit - Arène de combat (derrière la première porte coulissante à gauche).
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local dojo_kingambit_arene = {}
local sortie_en_cours = false

local function retourner_accueil()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.DojoKingambitPorteGaucheOuverte = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('town02_waterfallvillage', 'dojo_kingambit', 'MarowakDojoDungeonEntranceMarker', true)
end

function dojo_kingambit_arene.Init(map) end
function dojo_kingambit_arene.Enter(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit_arene.GameLoad(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit_arene.Update(map, time) end

function dojo_kingambit_arene.SortieArene_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  retourner_accueil()
end

function dojo_kingambit_arene.EstradeArbitre_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Une devise est gravée dans la pierre de l'estrade d'arbitrage :")
  UI:WaitShowDialogue("« Dans l'octogone des runes ardentes, la force brute s'incline devant la maîtrise du souffle et du pas. »")
end

return dojo_kingambit_arene
