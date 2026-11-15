--[[
  guilde_destiny_decors.lua
  Gestion unifiee pour les 15 salles de `guilde_destiny_interieur` :
  1. Filtre de luminosite et teinte de salle selon les 4 ambiances (`jour`, `aube`, `crepuscule`, `nuit`)
     via `map:SetDestinyAmbiance(moment, true)` synchronise sur `meteo_reverie.Moment()` ou `SV.Destiny.GuildeAmbiance`.
  2. Objets `GroundObject` independants (`.dir`) pour toutes les fenetres cintrees de la Guilde.
  3. Double Porte sculptee du Grand Salon s'ouvrant exactement comme la porte d'entree (`guilde_cliff_scene.lua`) :
     `Decorations` Layer 0 (`PorteSalonFermee` / `PorteSalonOuverte`), capteur `SortieBureauMaitre` devant le seuil,
     son `EVT_Door_Open`, `WaitFrames(20)`, fondu et remise a l'etat ferme.
]]

local meteo_reverie = require 'destiny.meteo_reverie'

local guilde_decors = {}

guilde_decors.FENETRES = {
  ['guilde_destiny_accueil'] = {
    { name = 'Fenetre_Gauche', x = 336, y = 168, w = 144, h = 264, jour = 'Guilde_Fenetre_Accueil_Gauche_Jour', aube = 'Guilde_Fenetre_Accueil_Gauche_Aube', crepuscule = 'Guilde_Fenetre_Accueil_Gauche_Crepuscule', nuit = 'Guilde_Fenetre_Accueil_Gauche_Nuit' },
    { name = 'Fenetre_Droite', x = 1056, y = 168, w = 144, h = 264, jour = 'Guilde_Fenetre_Accueil_Droite_Jour', aube = 'Guilde_Fenetre_Accueil_Droite_Aube', crepuscule = 'Guilde_Fenetre_Accueil_Droite_Crepuscule', nuit = 'Guilde_Fenetre_Accueil_Droite_Nuit' },
  },
  ['guilde_destiny_missions'] = {
    { name = 'Fenetre_Gauche', x = 72, y = 64, w = 56, h = 96, jour = 'Guilde_Fenetre_02_missions_Gauche_Jour', aube = 'Guilde_Fenetre_02_missions_Gauche_Aube', crepuscule = 'Guilde_Fenetre_02_missions_Gauche_Crepuscule', nuit = 'Guilde_Fenetre_02_missions_Gauche_Nuit' },
    { name = 'Fenetre_Droite', x = 448, y = 64, w = 56, h = 96, jour = 'Guilde_Fenetre_02_missions_Droite_Jour', aube = 'Guilde_Fenetre_02_missions_Droite_Aube', crepuscule = 'Guilde_Fenetre_02_missions_Droite_Crepuscule', nuit = 'Guilde_Fenetre_02_missions_Droite_Nuit' },
  },
  ['guilde_destiny_grand_salon'] = {
    { name = 'Fenetre_Gauche', x = 88, y = 64, w = 48, h = 96, jour = 'Guilde_Fenetre_03_grand_salon_central_Gauche_Jour', aube = 'Guilde_Fenetre_03_grand_salon_central_Gauche_Aube', crepuscule = 'Guilde_Fenetre_03_grand_salon_central_Gauche_Crepuscule', nuit = 'Guilde_Fenetre_03_grand_salon_central_Gauche_Nuit' },
    { name = 'Fenetre_Droite', x = 432, y = 64, w = 56, h = 96, jour = 'Guilde_Fenetre_03_grand_salon_central_Droite_Jour', aube = 'Guilde_Fenetre_03_grand_salon_central_Droite_Aube', crepuscule = 'Guilde_Fenetre_03_grand_salon_central_Droite_Crepuscule', nuit = 'Guilde_Fenetre_03_grand_salon_central_Droite_Nuit' },
  },
  ['guilde_destiny_bureau_maitre'] = {
    { name = 'Fenetre_Centre', x = 224, y = 16, w = 64, h = 88, jour = 'Guilde_Fenetre_04_bureau_maitre_Centre_Jour', aube = 'Guilde_Fenetre_04_bureau_maitre_Centre_Aube', crepuscule = 'Guilde_Fenetre_04_bureau_maitre_Centre_Crepuscule', nuit = 'Guilde_Fenetre_04_bureau_maitre_Centre_Nuit' },
  },
  ['guilde_destiny_refectoire'] = {
    { name = 'Fenetre_Gauche', x = 184, y = 40, w = 64, h = 80, jour = 'Guilde_Fenetre_05_refectoire_Gauche_Jour', aube = 'Guilde_Fenetre_05_refectoire_Gauche_Aube', crepuscule = 'Guilde_Fenetre_05_refectoire_Gauche_Crepuscule', nuit = 'Guilde_Fenetre_05_refectoire_Gauche_Nuit' },
    { name = 'Fenetre_Droite', x = 320, y = 40, w = 64, h = 80, jour = 'Guilde_Fenetre_05_refectoire_Droite_Jour', aube = 'Guilde_Fenetre_05_refectoire_Droite_Aube', crepuscule = 'Guilde_Fenetre_05_refectoire_Droite_Crepuscule', nuit = 'Guilde_Fenetre_05_refectoire_Droite_Nuit' },
  },
  ['guilde_destiny_cuisine'] = {
    { name = 'Fenetre_Gauche', x = 136, y = 32, w = 48, h = 72, jour = 'Guilde_Fenetre_06_cuisine_Gauche_Jour', aube = 'Guilde_Fenetre_06_cuisine_Gauche_Aube', crepuscule = 'Guilde_Fenetre_06_cuisine_Gauche_Crepuscule', nuit = 'Guilde_Fenetre_06_cuisine_Gauche_Nuit' },
    { name = 'Fenetre_Droite', x = 296, y = 32, w = 48, h = 72, jour = 'Guilde_Fenetre_06_cuisine_Droite_Jour', aube = 'Guilde_Fenetre_06_cuisine_Droite_Aube', crepuscule = 'Guilde_Fenetre_06_cuisine_Droite_Crepuscule', nuit = 'Guilde_Fenetre_06_cuisine_Droite_Nuit' },
  },
  ['guilde_destiny_dortoir_nord_1'] = {
    { name = 'Fenetre_Centre', x = 192, y = 16, w = 64, h = 72, jour = 'Guilde_Fenetre_09_dortoir_nord_Centre_Jour', aube = 'Guilde_Fenetre_09_dortoir_nord_Centre_Aube', crepuscule = 'Guilde_Fenetre_09_dortoir_nord_Centre_Crepuscule', nuit = 'Guilde_Fenetre_09_dortoir_nord_Centre_Nuit' },
  },
  ['guilde_destiny_dortoir_nord_2'] = {
    { name = 'Fenetre_Centre', x = 192, y = 16, w = 64, h = 72, jour = 'Guilde_Fenetre_09_dortoir_nord_Centre_Miroir_Jour', aube = 'Guilde_Fenetre_09_dortoir_nord_Centre_Miroir_Aube', crepuscule = 'Guilde_Fenetre_09_dortoir_nord_Centre_Miroir_Crepuscule', nuit = 'Guilde_Fenetre_09_dortoir_nord_Centre_Miroir_Nuit' },
  },
  ['guilde_destiny_chambre_heros'] = {
    { name = 'Fenetre_Centre', x = 216, y = 24, w = 56, h = 72, jour = 'Guilde_Fenetre_11_chambre_heros_Centre_Jour', aube = 'Guilde_Fenetre_11_chambre_heros_Centre_Aube', crepuscule = 'Guilde_Fenetre_11_chambre_heros_Centre_Crepuscule', nuit = 'Guilde_Fenetre_11_chambre_heros_Centre_Nuit' },
  },
}

guilde_decors.PORTE_SALON = {
  x = 224,
  y = 64,
  w = 128,
  h = 96,
  fermee = 'Guilde_Destiny_Porte_Salon_Fermee',
  ouverte = 'Guilde_Destiny_Porte_Salon_Ouverte',
}

function guilde_decors.MomentActuel()
  if SV and SV.Destiny and type(SV.Destiny.GuildeAmbiance) == 'string' and SV.Destiny.GuildeAmbiance ~= '' then
    local m = string.lower(SV.Destiny.GuildeAmbiance)
    if m == 'jour' or m == 'aube' or m == 'crepuscule' or m == 'nuit' then
      return m
    end
  end
  local ok, res = pcall(meteo_reverie.Moment)
  if ok and (res == 'jour' or res == 'aube' or res == 'crepuscule' or res == 'nuit') then
    return res
  end
  return 'jour'
end

local function supprimer_si_existe(map, ent_name)
  if map == nil or map.Entities == nil or map.Entities.Count == 0 then return end
  local layer = map.Entities[0]
  if layer == nil or layer.GroundObjects == nil then return end
  for i = layer.GroundObjects.Count - 1, 0, -1 do
    local o = layer.GroundObjects[i]
    if o ~= nil and o.EntName == ent_name then
      layer.GroundObjects:RemoveAt(i)
    end
  end
end

local function ajouter_objet_decor(map, ent_name, anim_sheet, x, y, w, h, passable, start_f, end_f)
  if RogueEssence == nil or RogueElements == nil or map == nil or map.Entities == nil or map.Entities.Count == 0 then
    return nil
  end
  supprimer_si_existe(map, ent_name)
  local sf = start_f or 0
  local ef = end_f or 0
  local anim = RogueEssence.Content.ObjAnimData(anim_sheet, 1, sf, ef)
  local obj = RogueEssence.Ground.GroundObject(
    anim,
    RogueElements.Rect(x, y, w, h),
    RogueElements.Loc(0, 0),
    false,
    ent_name
  )
  if passable then
    obj.Passable = true
    if RogueEssence.Ground.GroundEntity and RogueEssence.Ground.GroundEntity.EEntityTriggerTypes and RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.None ~= nil then
      pcall(function() obj:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.None) end)
    end
  end
  obj:ReloadEvents()
  map.Entities[0].GroundObjects:Add(obj)
  return obj
end

-- Rafraîchissement en direct : `meteo.Appliquer` ne touche pas les intérieurs,
-- donc une salle occupée gardait l'ambiance de son entrée. On réapplique quand
-- le moment change (vérification légère, une fois toutes les 30 frames).
local dernier_moment = nil
local compteur = 0

function guilde_decors.SynchroniserAmbiance(map, map_id)
  if map == nil then return end
  compteur = compteur + 1
  if compteur < 30 then return end
  compteur = 0
  local moment = guilde_decors.MomentActuel()
  if moment == dernier_moment then return end
  dernier_moment = moment
  guilde_decors.AppliquerAmbianceEtFenetres(map, map_id, moment)
end

-- Force l'ambiance d'une salle (cinématique, événement scénarisé...).
-- Écrit `SV.Destiny.GuildeAmbiance`, qui est prioritaire sur `meteo_reverie.Moment()`
-- et persiste en sauvegarde. `LibererAmbiance` rend la main à l'horloge du monde.
local MOMENTS = { jour = true, aube = true, crepuscule = true, nuit = true }

function guilde_decors.ForcerAmbiance(map, map_id, moment)
  if moment == nil or not MOMENTS[moment] then return false end
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.GuildeAmbiance = moment
  dernier_moment = moment
  guilde_decors.AppliquerAmbianceEtFenetres(map, map_id, moment)
  return true
end

function guilde_decors.LibererAmbiance(map, map_id)
  if SV and SV.Destiny then SV.Destiny.GuildeAmbiance = nil end
  dernier_moment = nil
  if map ~= nil then
    compteur = 30          -- force la réévaluation au prochain Update
  end
end

function guilde_decors.AppliquerAmbianceEtFenetres(map, map_id, ambiance_forcee)
  local moment = ambiance_forcee or guilde_decors.MomentActuel()
  dernier_moment = moment
  -- 1. Applique le filtre natif de luminosite & teinte de salle + personnages (`SetDestinyAmbiance(moment, true)`)
  if map ~= nil and map.SetDestinyAmbiance ~= nil then
    map:SetDestinyAmbiance(moment, true)
  end
  -- 2. Instancie / met a jour les objets Fenetres `.dir` independants correspondant a l'ambiance
  local slots = guilde_decors.FENETRES[map_id]
  if slots ~= nil then
    for _, slot in ipairs(slots) do
      local sheet = slot[moment] or slot.jour
      ajouter_objet_decor(map, slot.name, sheet, slot.x, slot.y, slot.w, slot.h, true, 0, 0)
    end
  end
end

function guilde_decors.DefinirPorteSalonOuverte(map, ouverte)
  local est_ouverte = (ouverte == true)
  if map == nil or map.Decorations == nil then return end
  if luanet ~= nil and luanet.each ~= nil then
    for deco in luanet.each(map.Decorations) do
      if deco.Name == 'PorteSalonFermee' then
        deco.Visible = not est_ouverte
      elseif deco.Name == 'PorteSalonOuverte' then
        deco.Visible = est_ouverte
      end
    end
  elseif type(map.Decorations) == 'table' then
    for _, deco in ipairs(map.Decorations) do
      if deco.Name == 'PorteSalonFermee' then
        deco.Visible = not est_ouverte
      elseif deco.Name == 'PorteSalonOuverte' then
        deco.Visible = est_ouverte
      end
    end
  end
end

function guilde_decors.OuvrirPorteSalon(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  guilde_decors.DefinirPorteSalonOuverte(map, true)
end

function guilde_decors.FermerPorteSalon(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  guilde_decors.DefinirPorteSalonOuverte(map, false)
end

function guilde_decors.SynchroniserPorteSalon(map)
  -- Comme `scene.Init` de la porte d'entree (`guilde_cliff_scene.lua`) :
  -- la porte demarre fermee et `SortieBureauMaitre` reste actif devant le seuil.
  guilde_decors.DefinirPorteSalonOuverte(map, false)
end

function guilde_decors.OuvrirPorteSalonDirect(map)
  guilde_decors.OuvrirPorteSalon(map)
end

return guilde_decors
