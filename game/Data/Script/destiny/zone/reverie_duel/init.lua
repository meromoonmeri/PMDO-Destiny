-- Manche d'entraînement : la victoire, le K.O. ou l'abandon ramènent en ville.
local itinerants = require 'destiny.reverie_itinerants'
local zone = {}
function zone.EnterSegment(_zone, rescuing, segmentID, mapID)
  GAME:SetRescueAllowed(false)
end
function zone.ExitSegment(_zone, result, rescue, segmentID, mapID)
  itinerants.RetourDuel(result)
end
return zone
