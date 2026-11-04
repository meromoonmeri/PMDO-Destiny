-- Bois Perdus (id lost_wood) : segment 0 pour l'aller seul, segment 1 pour le retour inverse
-- en équipe. Un échec de l'aller ne réintroduit jamais le héros dans la
-- scène du partenaire ; le succès de l'aller et l'échec du retour arrivent
-- dans la prairie du réveil, tandis que le succès du retour arrive sur la
-- falaise au jour.
require 'origin.common'
local recrutement = require 'destiny.recrutement'

local lost_wood = {}
function lost_wood.Init(zone)
  -- Couvre aussi les sauvegardes commencées avant l’ajout du verrou :
  -- aucun recrutement dans les Bois Perdus tant que le futur déblocage
  -- Assemblée / Zones d’Accueil n’a pas eu lieu.
  recrutement.synchroniser()
end
function lost_wood.Rescued(zone, mail) end

local function terminer(result, zone_id, map_id)
  GAME:EndDungeonRun(result, zone_id, -1, map_id, 0, false, false)
end

local function cause_echec(result)
  local R = RogueEssence.Data.GameProgress.ResultType
  return (result == R.Downed or result == R.Failed) and 'ko' or 'abandon'
end

function lost_wood.ExitSegment(zone, result, rescue, segmentID, mapID)
  GAME:SetRescueAllowed(false)
  SV.Destiny = SV.Destiny or {}
  local reussi = result == RogueEssence.Data.GameProgress.ResultType.Cleared
  local trajet = SV.Destiny.LostWoodTrip or 'aller'
  -- Le segment 1 est sans ambiguïté le chemin inverse. Conserver aussi
  -- l'ancien drapeau pour une sauvegarde déjà engagée dans le segment 0.
  if segmentID == 1 then trajet = 'retour' end

  if trajet == 'retour' or trajet == 'pause_retour' then
    if reussi then
      SV.Destiny.LostWoodRetourEchec = false
      SV.Destiny.LostWoodRetry = nil
      SV.Destiny.LostWoodCause = nil
      SV.Destiny.RetourAccompli = true
      SV.Destiny.LostWoodTrip = 'termine'
      -- Ground 0 de destiny_cliff_tests : cliffdaytest, version jour.
      terminer(result, 'destiny_cliff_tests', 0)
      GAME:EnterZone('destiny_cliff_tests', -1, 0, 0)
    else
      SV.Destiny.LostWoodRetourEchec = true
      SV.Destiny.LostWoodRetry = 'retour'
      SV.Destiny.LostWoodCause = cause_echec(result)
      SV.Destiny.LostWoodEchecsRetour = (SV.Destiny.LostWoodEchecsRetour or 0) + 1
      SV.Destiny.LostWoodTrip = 'retour'
      -- Ground 10 de reverie : zrv2_zone_reveil_nuit, entrée 0 = reveil.
      terminer(result, 'reverie', 10)
      GAME:EnterZone('reverie', -1, 10, 0)
    end
    return
  end

  if reussi then
    SV.Destiny.LostWoodTrip = 'rencontre'
    SV.Destiny.PartenaireParti = true
    SV.Destiny.LostWoodRetry = nil
    SV.Destiny.LostWoodCause = nil
    SV.Destiny.LostWoodRetourEchec = false
    -- Ground 10 de reverie : zrv2_zone_reveil_nuit, entrée 0 = reveil.
    terminer(result, 'reverie', 10)
    -- La réunion est faite à l'arrivée dans la prairie. La sauvegarde de fin
    -- reste ainsi cohérente même si le jeu est interrompu avant la transition.
    GAME:EnterZone('reverie', -1, 10, 0)
  else
    SV.Destiny.LostWoodTrip = 'echec_aller'
    SV.Destiny.PartenaireParti = true
    SV.Destiny.LostWoodRetry = 'aller'
    SV.Destiny.LostWoodCause = cause_echec(result)
    SV.Destiny.LostWoodEchecsAller = (SV.Destiny.LostWoodEchecsAller or 0) + 1
    terminer(result, 'destiny_cliff_tests', 4)
    GAME:EnterZone('destiny_cliff_tests', -1, 4, 0)
  end
end

return lost_wood
