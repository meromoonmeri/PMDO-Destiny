require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local CARTE = 'guilde_cliff_nuit'
local guilde_cliff_nuit = {}
local SON_MER = 'Destiny_Falaise_Mer'
local sortie_en_cours = false

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function installer_retour_ville(map)
  if map == nil or map:FindObject('RetourVille') then return end
  local retour = RogueEssence.Ground.GroundObject()
  retour.EntName = 'RetourVille'
  retour.Collider = RogueElements.Rect(208, 496, 64, 16)
  retour.Passable = false
  retour:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  retour:OnMapInit()
  map:AddObject(retour)
end

local function synchroniser_ambiance(avec_fondu)
  local attendu = meteo_reverie.CarteGuilde()
  if attendu == CARTE then return false end
  if sortie_en_cours then return true end
  sortie_en_cours = true
  local hero = CH('PLAYER')
  if hero ~= nil then
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.PassageAmbiance = {
      carte = attendu,
      x = hero.Position.X,
      y = hero.Position.Y,
      dir = hero.Direction,
    }
  end
  arreter_mer()
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterZone('town02_waterfallvillage', -1, meteo_reverie.IndexGuilde(), 0)
  return true
end

local function restaurer_passage()
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbiance or nil
  if passage ~= nil and passage.carte == CARTE then
    SV.Destiny.PassageAmbiance = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        local py = math.min(passage.y + 24, 472)
        GROUND:TeleportTo(partenaire, passage.x, py, passage.dir or hero.Direction)
      end
    end
  end
end

function guilde_cliff_nuit.Init(map)
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_retour_ville(map)
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local py = math.min(hero.Position.Y + 24, 472)
    local partner = equipe_scene.Partenaire(hero.Position.X, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function guilde_cliff_nuit.Enter(map)
  sortie_en_cours = false
  if synchroniser_ambiance(false) then return end
  restaurer_passage()
  demarrer_mer()
  GAME:FadeIn(20)
end

function guilde_cliff_nuit.GameLoad(map)
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_retour_ville(map)
  if synchroniser_ambiance(false) then return end
  restaurer_passage()
  demarrer_mer()
  GAME:FadeIn(20)
end

function guilde_cliff_nuit.Exit(map)
  arreter_mer()
end

function guilde_cliff_nuit.Update(map, time)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil
      and meteo_reverie.CarteGuilde() ~= CARTE then
    synchroniser_ambiance(true)
  end
end

function guilde_cliff_nuit.GameSave(map)
end

function guilde_cliff_nuit.RetourVille_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  SV.Destiny.RetourBatimentX = 776
  SV.Destiny.RetourBatimentY = 48
  SV.Destiny.RetourBatimentPartenaire = {x=776, y=48, px=748, py=48}
  arreter_mer()
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

return guilde_cliff_nuit
