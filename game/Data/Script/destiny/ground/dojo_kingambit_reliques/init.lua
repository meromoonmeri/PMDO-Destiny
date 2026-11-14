-- Dojo Kingambit - Salle des reliques et archives (derrière la seconde porte coulissante à droite).
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local dojo_kingambit_reliques = {}
local sortie_en_cours = false

local function retourner_accueil()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.DojoKingambitPorteDroiteOuverte = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('town02_waterfallvillage', 'dojo_kingambit', 'KingambitDojoNorthDoorRightMarker', true)
end

function dojo_kingambit_reliques.Init(map) end
function dojo_kingambit_reliques.Enter(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit_reliques.GameLoad(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit_reliques.Update(map, time) end

function dojo_kingambit_reliques.SortieReliques_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  retourner_accueil()
end

function dojo_kingambit_reliques.MonumentRunesNord_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Le grand monument runique veille sur la mémoire du dojo :")
  UI:WaitShowDialogue("« Trois préceptes scellent cette lignée : lucidité dans l'épreuve, loyauté envers son partenaire, retenue dans la victoire. »")
end

function dojo_kingambit_reliques.ParcheminAncienNE_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Un rouleau d'archives soigneusement déroulé répertorie les équipes d'exploration venues parfaire leur garde auprès de Kaito.")
end

function dojo_kingambit_reliques.CoffreReliqueNO_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Un coffre sarcelle riveté renfermant les emblèmes d'épreuve remis aux anciens disciples du dojo.")
end

function dojo_kingambit_reliques.CoffreReliqueSO_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Ce reliquaire scellé protège des fragments de lames cérémonielles polies par le temps.")
end

function dojo_kingambit_reliques.CoffreReliqueSE_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Le coffre est frappé du sceau solaire du dojo ; il abrite les registres des tournois passés.")
end

function dojo_kingambit_reliques.SteleArchiveOuest_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Une stèle de pierre où sont détaillés les déplacements de contre et d'esquive enseignés dans l'arène.")
end

function dojo_kingambit_reliques.SteleArchiveEst_Action(obj, activator)
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Les gravures décrivent l'accord entre deux partenaires : couvrir l'angle mort de l'autre sans un mot.")
end

return dojo_kingambit_reliques
