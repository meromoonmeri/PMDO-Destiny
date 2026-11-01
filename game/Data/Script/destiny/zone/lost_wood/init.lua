-- Lost Wood (7 étages) :
-- 1) Aller solo du partenaire (1F -> 7F) :
--    - succès : zrv2_zone_reveil_nuit (reverie, map 10) pour les retrouvailles ;
--    - échec  : cliffdaytest_nuit (destiny_cliff_tests, map 4) sans réintroduire le héros.
-- 2) Retour en duo en sens inverse (7F -> 1F) :
--    - succès : cliffdaytest de jour (destiny_cliff_tests, map 0) ;
--    - échec  : zrv2_zone_reveil_nuit (reverie, map 10) pour reprendre souffle.
require 'origin.common'

local lost_wood = {}
function lost_wood.Init(zone) end
function lost_wood.EnterSegment(zone, rescuing, segmentID, mapID) end
function lost_wood.Rescued(zone, name, mail) end

local function terminer(result, zone_id, map_id, entry_id, display, fanfare)
  GAME:EndDungeonRun(result, zone_id, -1, map_id, entry_id or 0, display or false, fanfare or false)
end

function lost_wood.ExitSegment(zone, result, rescue, segmentID, mapID)
  GAME:SetRescueAllowed(false)
  SV.Destiny = SV.Destiny or {}
  local R = RogueEssence.Data.GameProgress.ResultType
  local reussi = (result == R.Cleared)
  local trajet = SV.Destiny.LostWoodTrip or 'aller'

  if trajet == 'retour' then
    if reussi then
      SV.Destiny.LostWoodRetourEchec = false
      SV.Destiny.RetourAccompli = true
      SV.Destiny.LostWoodTrip = 'termine'
      terminer(result, 'destiny_cliff_tests', 0, 3, true, true)
      GAME:EnterZone('destiny_cliff_tests', -1, 0, 3)
    else
      SV.Destiny.LostWoodCause = (result == R.Downed or result == R.Failed) and 'ko' or 'abandon'
      SV.Destiny.LostWoodRetourEchec = true
      terminer(result, 'reverie', 10, 0, false, false)
      GAME:EnterZone('reverie', -1, 10, 0)
    end
    return
  end

  if reussi then
    SV.Destiny.LostWoodEchec = false
    SV.Destiny.LostWoodTrip = 'rencontre'
    SV.Destiny.PartenaireParti = true
    SV.Destiny.LostWoodRetourEchec = false
    -- Le héros reste dans la réserve jusqu'à l'arrivée sur zrv2_zone_reveil_nuit.
    terminer(result, 'reverie', 10, 0, false, false)
    GAME:EnterZone('reverie', -1, 10, 0)
  else
    SV.Destiny.LostWoodEchec = true
    SV.Destiny.LostWoodTrip = 'echec_aller'
    SV.Destiny.PartenaireParti = true
    SV.Destiny.LostWoodCause = (result == R.Downed or result == R.Failed) and 'ko' or 'abandon'
    terminer(result, 'destiny_cliff_tests', 4, 3, false, false)
    GAME:EnterZone('destiny_cliff_tests', -1, 4, 3)
  end
end

return lost_wood
