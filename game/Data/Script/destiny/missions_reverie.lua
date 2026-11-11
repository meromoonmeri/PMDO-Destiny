-- Missions quotidiennes autonomes de Réverie ; aucune dépendance à Halcyon.
-- Les champs Destiny sont ajoutés à la sauvegarde existante, sans toucher au scénario.
local missions = {}
local RECOMPENSE = 300

local function destiny()
  SV.Destiny = SV.Destiny or {}
  return SV.Destiny
end

local function grotte_sauvetage_accompli()
  local d = destiny()
  return d.AlerteShinx == 'termine' or d.GrotteVerdoyanteBossVaincu == true
end

function missions.Jour()
  return math.max(0, math.floor(tonumber(destiny().JourneeVille) or 0))
end

function missions.ActualiserDeblocages()
  if destiny().RetourAccompli and not GAME:DungeonUnlocked('lost_wood') then
    GAME:UnlockDungeon('lost_wood')
  end
  if grotte_sauvetage_accompli() and not GAME:DungeonUnlocked('grotte_verdoyante') then
    GAME:UnlockDungeon('grotte_verdoyante')
  end
end

function missions.ZoneOffre()
  missions.ActualiserDeblocages()
  local bois = GAME:DungeonUnlocked('lost_wood')
  local grotte = grotte_sauvetage_accompli() and GAME:DungeonUnlocked('grotte_verdoyante')
  if bois and grotte then
    return (missions.Jour() % 2 == 1) and 'grotte_verdoyante' or 'lost_wood'
  elseif grotte then
    return 'grotte_verdoyante'
  elseif bois then
    return 'lost_wood'
  end
  return nil
end

function missions.Actuelle()
  local m = destiny().MissionReverie
  if type(m) == 'table'
    and (m.Zone == 'lost_wood' or m.Zone == 'grotte_verdoyante')
    and (m.Etat == 'en_cours' or m.Etat == 'reussie') then
    return m
  end
  return nil
end

function missions.OffreDisponible()
  return missions.Actuelle() == nil
    and destiny().DernierJourMissionReverie ~= missions.Jour()
    and missions.ZoneOffre() ~= nil
end

function missions.Accepter()
  if not missions.OffreDisponible() then return false end
  local zone = missions.ZoneOffre()
  if zone == nil then return false end
  local jour = missions.Jour()
  destiny().MissionReverie = {Zone=zone, Etat='en_cours', Jour=jour, Recompense=RECOMPENSE}
  destiny().DernierJourMissionReverie = jour
  return true
end

function missions.Completer(zone, reussi)
  local m = missions.Actuelle()
  if m ~= nil and m.Etat == 'en_cours' and m.Zone == zone and reussi then
    m.Etat = 'reussie'
    return true
  end
  return false
end

function missions.Reclamer()
  local m = missions.Actuelle()
  if m == nil or m.Etat ~= 'reussie' then return false end
  GAME:AddToPlayerMoneyBank(RECOMPENSE)
  destiny().MissionReverie = nil
  return true
end

function missions.EtudierTableau()
  missions.ActualiserDeblocages()
  require('destiny.interface_tableau_reverie').Ouvrir(missions)
end

function missions.LireGazette()
  missions.ActualiserDeblocages()
  local m = missions.Actuelle()
  UI:WaitShowDialogue('Gazette de Réverie — jour ' .. tostring(missions.Jour() + 1) .. '\nLes habitants échangent les nouvelles du jour.')
  if destiny().AlerteShinx == 'termine' then
    UI:WaitShowDialogue('Le petit Nilo a été retrouvé sain et sauf derrière la cascade de la Grotte Verdoyante !')
  end
  if m ~= nil and m.Etat == 'reussie' then
    UI:WaitShowDialogue('Une mission accomplie attend sa récompense au tableau.')
  elseif m ~= nil then
    local lieu = m.Zone == 'grotte_verdoyante' and 'la Grotte Verdoyante' or 'les Bois Perdus'
    UI:WaitShowDialogue('Une équipe se prépare à explorer ' .. lieu .. '.')
  elseif grotte_sauvetage_accompli() and GAME:DungeonUnlocked('grotte_verdoyante') then
    UI:WaitShowDialogue('Les Bois Perdus et la Grotte Verdoyante sont ouverts aux équipes d’exploration.')
  elseif GAME:DungeonUnlocked('lost_wood') then
    UI:WaitShowDialogue('Les Bois Perdus sont accessibles aux équipes d’exploration.')
  else
    UI:WaitShowDialogue('Aucun donjon d’exploration n’est encore ouvert.')
  end
end

function missions.OuvrirTableau()
  UI:ResetSpeaker()
  UI:BeginChoiceMenu('Que souhaitez-vous consulter ?', {'Missions', 'Gazette', 'Fermer'}, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == 1 then missions.EtudierTableau()
  elseif choix == 2 then missions.LireGazette() end
end

return missions
