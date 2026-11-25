-- Passage Aquatique (id passage_aquatique) :
--   GroundMap 0..3 = plage_sablefin_{jour,aube,crepuscule,nuit}
--   GroundMap 4    = passage_aquatique_fond (crique secrète après le 10e étage)
--   Segment 0      = étages 1F à 10F
require 'origin.common'
local recrutement = require 'destiny.recrutement'
local meteo_reverie = require 'destiny.meteo_reverie'

local passage_aquatique = {}

function passage_aquatique.Init(zone)
  DEBUG.EnableDbgCoro()
  recrutement.synchroniser()
end

function passage_aquatique.Rescued(zone, name, mail)
  COMMON.Rescued(zone, name, mail)
end

function passage_aquatique.EnterSegment(zone, rescuing, segmentID, mapID)
  if rescuing ~= true then
    COMMON.BeginDungeon(zone.ID, segmentID, mapID)
  end
end

function passage_aquatique.ExitSegment(zone, result, rescue, segmentID, mapID)
  DEBUG.EnableDbgCoro()
  local exited = COMMON.ExitDungeonMissionCheck(result, rescue, zone.ID, segmentID)
  if exited == true then
    return
  end
  GAME:SetRescueAllowed(false)
  local R = RogueEssence.Data.GameProgress.ResultType
  if result == R.Cleared and segmentID == 0 then
    GAME:EnterZone('passage_aquatique', -1, 4, 0)
    return
  end
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationPassageAquatique = nil
  local idx_plage = meteo_reverie.IndexPlageSablefin ~= nil and meteo_reverie.IndexPlageSablefin() or 0
  COMMON.EndDungeonDay(result, 'passage_aquatique', -1, idx_plage, 2)
end

return passage_aquatique
