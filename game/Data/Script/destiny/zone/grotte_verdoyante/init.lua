-- Grotte Verdoyante (id grotte_verdoyante) :
--   GroundMap 0 = ewc3_entree_waterfall_cave (entrée avec cascade fermée -> ouverte)
--   GroundMap 1 = fgv1_fin_grotte_vasques (scènes 9F pré-combat, post-combat et visites libres)
--   Segment 0   = étages 1F à 8F
--   Segment 1   = arène de boss 9F (end_grotte_verdoyante)
require 'origin.common'
local recrutement = require 'destiny.recrutement'
local missions_reverie = require 'destiny.missions_reverie'

local grotte_verdoyante = {}

function grotte_verdoyante.Init(zone)
  DEBUG.EnableDbgCoro()
  recrutement.synchroniser()
end

function grotte_verdoyante.Rescued(zone, name, mail)
  COMMON.Rescued(zone, name, mail)
end

function grotte_verdoyante.EnterSegment(zone, rescuing, segmentID, mapID)
  if rescuing ~= true then
    COMMON.BeginDungeon(zone.ID, segmentID, mapID)
  end
end

local function retour_reverie_flags()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationReverie = nil
  SV.Destiny.ArriveeVille = 'batiment'
  SV.Destiny.RetourBatimentX = 1552
  SV.Destiny.RetourBatimentY = 1600
end

local function cause_echec_grotte(result)
  local R = RogueEssence.Data.GameProgress.ResultType
  if result == R.Downed or result == R.Failed or (R.TimedOut ~= nil and result == R.TimedOut) then
    return 'ko'
  end
  return 'repli'
end

function grotte_verdoyante.ExitSegment(zone, result, rescue, segmentID, mapID)
  DEBUG.EnableDbgCoro()
  local exited = COMMON.ExitDungeonMissionCheck(result, rescue, zone.ID, segmentID)
  if exited == true then
    return
  end
  GAME:SetRescueAllowed(false)
  SV.Destiny = SV.Destiny or {}
  local R = RogueEssence.Data.GameProgress.ResultType
  if result ~= R.Cleared then
    if segmentID == 1 then
      SV.Destiny.GrotteVerdoyantePhase = 1
    end
    if SV.Destiny.AlerteShinx ~= 'a_secourir' then
      missions_reverie.Completer('grotte_verdoyante', false)
    end
    local cause = cause_echec_grotte(result)
    SV.Destiny.GrotteVerdoyanteOuverte = true
    SV.Destiny.GrotteVerdoyanteRetourEchec = {
      cause = cause,
      segment = segmentID,
    }
    if cause == 'ko' then
      SV.Destiny.GrotteVerdoyanteNbKO = (SV.Destiny.GrotteVerdoyanteNbKO or 0) + 1
      SV.Destiny.GrotteVerdoyanteDernierKO = true
    end
    if SV.Destiny.AlerteShinx == 'a_secourir' then
      SV.Destiny.LuxrayAttente = 'sortie'
    end
    -- Respawn directement devant l'entrée de la Grotte Verdoyante (GroundMap 0 = ewc3_entree_waterfall_cave).
    COMMON.EndDungeonDay(result, 'grotte_verdoyante', -1, 0, 0)
    return
  end

  if segmentID == 0 then
    -- Fin du 8e étage : arrivée dans la salle des vasques (GroundMap 1 = fgv1_fin_grotte_vasques).
    GAME:EnterZone('grotte_verdoyante', -1, 1, 0)
  elseif segmentID == 1 then
    -- Victoire contre Carchacrok au 9e étage : scène de sauvetage sur fgv1_fin_grotte_vasques.
    SV.Destiny.GrotteVerdoyantePhase = 3
    GAME:EnterZone('grotte_verdoyante', -1, 1, 0)
  else
    missions_reverie.Completer('grotte_verdoyante', true)
    retour_reverie_flags()
    COMMON.EndDungeonDay(result, 'town02_waterfallvillage', -1, 0, 0)
  end
end

return grotte_verdoyante
