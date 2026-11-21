local dojo = require 'destiny.dojo_kingambit_entrainement'
local zone = {}

function zone.EnterSegment(_zone, _rescuing, _segment, map)
  GAME:SetRescueAllowed(false)
  if map == 0 then SOUND:PlayBattleSE('EVT_EP_Pitfall_Land') end
end

function zone.ExitSegment(_zone, result, _rescue, segment, _map)
  dojo.Retour(result, segment)
end

return zone
