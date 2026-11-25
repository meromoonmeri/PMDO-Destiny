-- Météo quotidienne et ambiance (jour/aube/crépuscule/nuit) de Réverie Town
-- et des cartes à 4 variantes d'ambiance. Pilotée par le scénario
-- (SV.Destiny.MomentScenario), indépendante de l'horloge réelle. Les effets
-- PMDO de Ground sont visuels : aucune règle de donjon modifiée.
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

local moments_valides = {jour=true, aube=true, crepuscule=true, nuit=true}
local cartes_cliff = {
  jour = 'cliffdaytest',
  aube = 'cliffdaytest_aube',
  crepuscule = 'cliffdaytest_crepuscule',
  nuit = 'cliffdaytest_nuit',
}
local index_guilde = {jour = 23, aube = 24, crepuscule = 25, nuit = 26}
local cartes_guilde = {
  jour = 'guilde_cliff_jour',
  aube = 'guilde_cliff_aube',
  crepuscule = 'guilde_cliff_crepuscule',
  nuit = 'guilde_cliff_nuit',
}
local index_promontoire = {jour = 0, aube = 1, crepuscule = 2, nuit = 3}
local cartes_promontoire = {
  jour = 'falaise_promontoire_jour',
  aube = 'falaise_promontoire_aube',
  crepuscule = 'falaise_promontoire_crepuscule',
  nuit = 'falaise_promontoire_nuit',
}
local cartes_reveil = {
  jour = 'zrv2_zone_reveil_jour',
  aube = 'zrv2_zone_reveil_aube',
  crepuscule = 'zrv2_zone_reveil_crepuscule',
  nuit = 'zrv2_zone_reveil_nuit',
}
local cartes_etang_doyen = {
  jour = 'etangdudoyen_jour',
  aube = 'etangdudoyen_aube',
  crepuscule = 'etangdudoyen_crepuscule',
  nuit = 'etangdudoyen_nuit',
}
local index_plage_sablefin = {jour = 0, aube = 1, crepuscule = 2, nuit = 3}
local cartes_plage_sablefin = {
  jour = 'plage_sablefin_jour',
  aube = 'plage_sablefin_aube',
  crepuscule = 'plage_sablefin_crepuscule',
  nuit = 'plage_sablefin_nuit',
}

local carte_appliquee = nil
local dernier_moment_applique = nil

local function dark_actif_sur_carte()
  if _ZONE == nil or _ZONE.CurrentGround == nil then return false end
  if not exterieurs[_ZONE.CurrentGround.AssetName] then return false end
  local ok, actif = pcall(function()
    local st = _ZONE.CurrentGround.Status
    return st ~= nil and st:ContainsKey('dark') == true
  end)
  return ok and actif == true
end

-- Le moment de Réverie Town dépend du scénario :
-- 1) Surcharge explicite de chapitre/scène : SV.Destiny.MomentScenario
-- 2) Avant la fin de la première visite en ville : 'jour' (« Le jour se lève »)
-- 3) Statut moteur natif 'dark' sur la carte extérieure active -> 'nuit'
-- 4) Dernier moment synchronisé (SV.Destiny.MomentReverie), sinon 'jour'.
function meteo.Moment()
  local d = SV ~= nil and SV.Destiny or nil
  if d ~= nil and moments_valides[d.MomentScenario] then
    return d.MomentScenario
  end
  if d == nil or d.VisiteVille ~= 'terminee' then
    return 'jour'
  end
  if dark_actif_sur_carte() then
    d.MomentReverie = 'nuit'
    return 'nuit'
  end
  if moments_valides[d.MomentReverie] then
    return d.MomentReverie
  end
  return 'jour'
end

function meteo.EstNuit()
  return meteo.Moment() == 'nuit'
end

function meteo.CarteCliff()
  return cartes_cliff[meteo.Moment()] or 'cliffdaytest'
end

function meteo.IndexGuilde()
  return index_guilde[meteo.Moment()] or 23
end

function meteo.CarteGuilde()
  return cartes_guilde[meteo.Moment()] or 'guilde_cliff_jour'
end

function meteo.IndexPromontoire()
  return index_promontoire[meteo.Moment()] or 0
end

function meteo.CartePromontoire()
  return cartes_promontoire[meteo.Moment()] or 'falaise_promontoire_jour'
end

function meteo.CarteReveil()
  return cartes_reveil[meteo.Moment()] or 'zrv2_zone_reveil_jour'
end

function meteo.CarteEtangDoyen()
  return cartes_etang_doyen[meteo.Moment()] or 'etangdudoyen_jour'
end

function meteo.IndexPlageSablefin()
  return index_plage_sablefin[meteo.Moment()] or 0
end

function meteo.CartePlageSablefin()
  return cartes_plage_sablefin[meteo.Moment()] or 'plage_sablefin_jour'
end

function meteo.DefinirMomentScenario(moment)
  SV.Destiny = SV.Destiny or {}
  if moments_valides[moment] then
    SV.Destiny.MomentScenario = moment
    SV.Destiny.MomentReverie = moment
  else
    SV.Destiny.MomentScenario = nil
    SV.Destiny.MomentReverie = nil
    carte_appliquee = nil
    dernier_moment_applique = nil
    pcall(function() GROUND:RemoveMapStatus('dark') end)
  end
  if _ZONE ~= nil and _ZONE.CurrentGround ~= nil and exterieurs[_ZONE.CurrentGround.AssetName] then
    meteo.Appliquer(_ZONE.CurrentGround)
  end
  return meteo.Moment()
end

function meteo.EffacerMomentScenario()
  return meteo.DefinirMomentScenario(nil)
end

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

function meteo.SynchroniserZone()
  local ok, err = pcall(function()
    if _ZONE ~= nil and _ZONE.CurrentZone ~= nil and _ZONE.CurrentZone.SyncGroundMaps ~= nil then
      _ZONE.CurrentZone:SyncGroundMaps()
    end
  end)
  if not ok then
    print('[Destiny] Synchronisation zone ignorée : '..tostring(err))
  end
end

-- En mode Dev (panneau Travel -> Enter Ground ou Test Map dans l'éditeur),
-- lorsqu'aucun MomentScenario forcé n'est défini, laisser la variante
-- d'ambiance ouverte directement au lieu de rediriger automatiquement vers _jour.
function meteo.AccesDirectDevSansScenario()
  if _ZONE ~= nil then
    local ok_z, in_dev = pcall(function() return _ZONE.InDevZone == true end)
    if ok_z and in_dev then return true end
  end
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil then
    return false
  end
  local ok_d, dev = pcall(function()
    return RogueEssence ~= nil
      and RogueEssence.DiagManager ~= nil
      and RogueEssence.DiagManager.Instance ~= nil
      and RogueEssence.DiagManager.Instance.DevMode == true
  end)
  return ok_d and dev == true
end

-- Ne touche ni aux intérieurs, ni aux donjons, ni aux cartes de cinématique
-- fixes. Les autres effets de carte, notamment clouds_overhead, sont préservés.
-- Les 4 ambiances (jour, aube, crépuscule, nuit) remplacent le voile plat
-- 'dark' par le filtrage LUT natif (monde + sprites) via SetDestinyAmbiance.
function meteo.Appliquer(map)
  meteo.SynchroniserZone()
  if map == nil or not exterieurs[map.AssetName] then return false end
  local temps = meteo.Temps()
  local moment = meteo.Moment()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.MomentReverie = moment
  local ok, err = pcall(function()
    -- La ville possédait déjà ces ombres de nuage : les garder intactes.
    if map.AssetName ~= 'crossroadreverietown2' then
      GROUND:AddMapStatus('clouds_overhead')
    end
    for _, statut in ipairs({'sunny', 'cloudy', 'rain'}) do
      GROUND:RemoveMapStatus(statut)
    end
    if effets[temps] ~= nil then GROUND:AddMapStatus(effets[temps]) end
    GROUND:RemoveMapStatus('dark')
    if map.SetDestinyAmbiance ~= nil then
      map:SetDestinyAmbiance(moment, true)
    end
  end)
  if ok then
    carte_appliquee = map
    dernier_moment_applique = moment
  else
    print('[Destiny] Météo extérieure indisponible : '..tostring(err))
  end
  return ok
end

return meteo
