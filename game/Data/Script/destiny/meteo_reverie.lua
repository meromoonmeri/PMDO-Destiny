-- Météo quotidienne de Réverie, indépendante de l'horloge réelle.
-- Les effets PMDO de Ground sont visuels : aucune règle de donjon modifiée.
local meteo = {}
local descriptions = {
  clair = 'Le temps est clair à Réverie aujourd’hui.',
  soleil = 'Le soleil brille à Réverie aujourd’hui.',
  couvert = 'Le ciel est couvert à Réverie aujourd’hui.',
  pluie = 'Il pleut à Réverie aujourd’hui.',
}
local effets = {soleil='sunny', couvert='cloudy', pluie='rain'}
local exterieurs = {
  WaterfallVillageCapital=true, WaterfallVillageCapital_Dev=true,
  reverie_centre=true, reverie_centre_Dev=true,
  reverie_nord=true, reverie_nord_Dev=true,
  reverie_etang=true, reverie_etang_Dev=true,
  reverie_residentiel=true, reverie_residentiel_Dev=true,
  crossroadreverietown2=true,
}

-- Le tirage n'a lieu qu'une fois par journée de jeu et reste dans la
-- sauvegarde. Une ancienne partie sans ce champ est initialisée à la volée.
function meteo.Temps()
  SV.Destiny = SV.Destiny or {}
  local jour = math.max(0, math.floor(tonumber(SV.Destiny.JourneeVille) or 0))
  local ancienne = SV.Destiny.MeteoReverie
  if type(ancienne) == 'table' and ancienne.jour == jour and descriptions[ancienne.temps] ~= nil then
    return ancienne.temps
  end
  local tirage = math.random(1, 100)
  local temps
  if tirage <= 35 then temps = 'clair'
  elseif tirage <= 55 then temps = 'soleil'
  elseif tirage <= 75 then temps = 'couvert'
  else temps = 'pluie' end
  SV.Destiny.MeteoReverie = {jour=jour, temps=temps}
  return temps
end

function meteo.Description()
  return descriptions[meteo.Temps()]
end

-- Ne touche ni aux intérieurs, ni aux donjons, ni aux cartes de cinématique
-- fixes. Les autres effets de carte, notamment clouds_overhead, sont préservés.
function meteo.Appliquer(map)
  if map == nil or not exterieurs[map.AssetName] then return false end
  local temps = meteo.Temps()
  local ok, err = pcall(function()
    -- La ville possédait déjà ces ombres de nuage : les garder intactes.
    if map.AssetName ~= 'crossroadreverietown2' then
      GROUND:AddMapStatus('clouds_overhead')
    end
    for _, statut in ipairs({'sunny', 'cloudy', 'rain'}) do
      GROUND:RemoveMapStatus(statut)
    end
    if effets[temps] ~= nil then GROUND:AddMapStatus(effets[temps]) end
  end)
  if not ok then print('[Destiny] Météo extérieure indisponible : '..tostring(err)) end
  return ok
end

return meteo
