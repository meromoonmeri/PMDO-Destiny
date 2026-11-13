--[[ init.lua — cliffdaytest_crepuscule
     Carte d'ambiance de la falaise Cliff : même géométrie, mêmes collisions et
     mêmes objets que cliffdaytest ; seuls le ciel et la teinte changent.
     Exploration libre post-prologue avec partenaire, maison de l'équipe et
     retour au carrefour de Réverie, synchronisée sur l'ambiance de Réverie Town.
]]

require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local CARTE_CLIFF = 'cliffdaytest_crepuscule'
local cliffdaytest_crepuscule = {}
local SON_MER = 'Destiny_Falaise_Mer'
local sortie_en_cours = false

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function installer_sortie_carrefour(map)
  if map == nil or map:FindObject('SortieCarrefour') then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = 'SortieCarrefour'
  sortie.Collider = RogueElements.Rect(688, 784, 104, 8)
  sortie.Passable = true
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

local function installer_porte_maison(map)
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  if map == nil or map:FindObject('PorteMaisonEquipe') then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = 'PorteMaisonEquipe'
  porte.Collider = RogueElements.Rect(592, 464, 40, 8)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

local function synchroniser_ambiance(avec_fondu)
  if not avec_fondu and meteo_reverie.AccesDirectDevSansScenario ~= nil
      and meteo_reverie.AccesDirectDevSansScenario() then
    return false
  end
  if SV == nil or SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then
    return false
  end
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  local attendu = meteo_reverie.CarteCliff()
  SV.Destiny.FalaiseAmbiance = attendu
  if attendu == CARTE_CLIFF then return false end
  if sortie_en_cours then return true end
  sortie_en_cours = true
  if not SV.Destiny.RetourMaisonEquipe then
    local hero = CH('PLAYER')
    if hero ~= nil then
      SV.Destiny.PassageAmbiance = {
        carte = attendu,
        x = hero.Position.X,
        y = hero.Position.Y,
        dir = hero.Direction,
      }
    end
  end
  arreter_mer()
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterGroundMap('destiny_cliff_tests', attendu, 'Dazzling_Entry_South')
  return true
end

local function restaurer_passage()
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbiance or nil
  if passage ~= nil and passage.carte == CARTE_CLIFF then
    SV.Destiny.PassageAmbiance = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        GROUND:TeleportTo(partenaire, math.min(passage.x + 24, 1560), passage.y, passage.dir or hero.Direction)
      end
    end
  end
end

function cliffdaytest_crepuscule.Init(map)
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_sortie_carrefour(map)
  installer_porte_maison(map)
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local partner = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
    equipe_scene.Suivre(partner, hero)
  end
end

local function entrer(map)
  SV.Destiny = SV.Destiny or {}
  sortie_en_cours = false
  installer_sortie_carrefour(map)
  installer_porte_maison(map)
  if synchroniser_ambiance(false) then return end
  demarrer_mer()
  if SV.Destiny.RetourMaisonEquipe then
    SV.Destiny.RetourMaisonEquipe = nil
    local hero = CH('PLAYER')
    local partenaire = CH('Teammate1')
    if hero ~= nil then GROUND:TeleportTo(hero, 600, 476, Direction.Down) end
    if partenaire ~= nil then GROUND:TeleportTo(partenaire, 624, 476, Direction.Down) end
    GAME:FadeIn(20)
    if hero ~= nil and partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
    return
  end
  restaurer_passage()
  GAME:FadeIn(20)
end

function cliffdaytest_crepuscule.Enter(map)
  entrer(map)
end

function cliffdaytest_crepuscule.GameLoad(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  entrer(map)
end

function cliffdaytest_crepuscule.Exit(map)
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  arreter_mer()
end

function cliffdaytest_crepuscule.Update(map, time)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.VisiteVille == 'terminee'
      and SV.Destiny.MomentScenario ~= nil and meteo_reverie.CarteCliff() ~= CARTE_CLIFF then
    synchroniser_ambiance(true)
  end
end

function cliffdaytest_crepuscule.GameSave(map)
end

function cliffdaytest_crepuscule.PorteMaisonEquipe_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  sortie_en_cours = true
  SV.Destiny.FalaiseAmbiance = meteo_reverie.CarteCliff()
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('destiny_cliff_tests', 'maison_equipe_falaise', 'entree', true)
end

function cliffdaytest_crepuscule.SortieCarrefour_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('reverie', 'crossroadreverietown2', 'entree_falaise')
end

return cliffdaytest_crepuscule
