-- Lost Wood : aller seul, retrouvailles, retour en équipe.
-- Un échec de l'aller ne réintroduit jamais le héros dans la scène du partenaire.
require 'origin.common'

local lost_wood = {}
function lost_wood.Init(zone) end
function lost_wood.Rescued(zone, mail) end

local function terminer(result, zone_id, map_id)
  GAME:EndDungeonRun(result, zone_id, -1, map_id, 0, false, false)
end

function lost_wood.ExitSegment(zone, result, rescue, segmentID, mapID)
  GAME:SetRescueAllowed(false)
  SV.Destiny = SV.Destiny or {}
  local reussi = result == RogueEssence.Data.GameProgress.ResultType.Cleared
  local trajet = SV.Destiny.LostWoodTrip or 'aller'

  if trajet == 'retour' then
    if reussi then
      SV.Destiny.LostWoodRetourEchec = false
      SV.Destiny.RetourAccompli = true
      SV.Destiny.LostWoodTrip = 'termine'
      terminer(result, 'destiny_cliff_tests', 4)
      GAME:EnterZone('destiny_cliff_tests', -1, 4, 0)
    else
      SV.Destiny.LostWoodRetourEchec = true
      terminer(result, 'personality_test', 2)
      GAME:EnterZone('personality_test', -1, 2, 0)
    end
    return
  end

  if reussi then
    SV.Destiny.LostWoodTrip = 'rencontre'
    SV.Destiny.PartenaireParti = true
    SV.Destiny.LostWoodRetourEchec = false
    terminer(result, 'personality_test', 2)
    -- La réunion est faite à l'arrivée sur le panorama. La sauvegarde de fin
    -- reste ainsi cohérente même si le jeu est interrompu avant la transition.
    GAME:EnterZone('personality_test', -1, 2, 0)
  else
    SV.Destiny.LostWoodTrip = 'echec_aller'
    SV.Destiny.PartenaireParti = true
    local R = RogueEssence.Data.GameProgress.ResultType
    SV.Destiny.LostWoodCause = (result == R.Downed or result == R.Failed) and 'ko' or 'abandon'
    terminer(result, 'destiny_cliff_tests', 4)
    GAME:EnterZone('destiny_cliff_tests', -1, 4, 0)
  end
end

return lost_wood
