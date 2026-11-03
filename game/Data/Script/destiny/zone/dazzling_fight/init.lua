require 'origin.common'

local dazzling_fight = {}

function dazzling_fight.Init(zone) end

function dazzling_fight.Rescued(zone, name, mail) end

function dazzling_fight.EnterSegment(zone, rescuing, segmentID, mapID)
  GAME:SetRescueAllowed(false)
end

-- Combat scénarisé : il n'y a ni game over ordinaire ni retour au checkpoint.
-- Le résultat est seulement transmis à cliffdaytest, qui reprend la scène au
-- même endroit (poussée du duo en cas de défaite, recul des Dazzling si le
-- joueur parvient secrètement à gagner).
function dazzling_fight.ExitSegment(zone, result, rescue, segmentID, mapID)
  GAME:SetRescueAllowed(false)
  SV.Destiny = SV.Destiny or {}
  if result == RogueEssence.Data.GameProgress.ResultType.Cleared then
    SV.Destiny.CombatDazzling = 'victoire'
  else
    SV.Destiny.CombatDazzling = 'defaite'
  end
  GAME:EndDungeonRun(result, 'destiny_cliff_tests', -1, 0, 0, false, false)
  GAME:EnterZone('destiny_cliff_tests', -1, 0, 0)
end

return dazzling_fight
