-- Carrefour de Réverie : la carte, Ronflex, les décors et collisions viennent
-- de la sauvegarde de l'utilisateur. Les deux autres chemins restent libres
-- de raccordement futur ; aucune destination n'est supposée pour ceux-ci.
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'
local crossroadreverietown2 = {}
local sortie_en_cours = false

local function installer_sortie(map, nom, x, y, largeur, hauteur)
  if map == nil or map:FindObject(nom) then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = nom
  sortie.Collider = RogueElements.Rect(x, y, largeur, hauteur)
  sortie.Passable = true
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

function crossroadreverietown2.Init(map)
  meteo_reverie.Appliquer(map)
  sortie_en_cours = false
  installer_sortie(map, 'SortieFalaise', 456, 8, 56, 8)
  installer_sortie(map, 'SortieVille', 940, 400, 8, 48)
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local partenaire = equipe_scene.Partenaire(hero.Position.X - 24, hero.Position.Y, Direction.Down)
    equipe_scene.Suivre(partenaire, hero)
  end
end

local function entrer()
  sortie_en_cours = false
  SOUND:PlayBGM("Wigglytuff's Guild.ogg", true)
  GAME:FadeIn(20)
end
function crossroadreverietown2.Enter(map) entrer() end
function crossroadreverietown2.GameLoad(map) meteo_reverie.Appliquer(map); entrer() end
function crossroadreverietown2.Update(map, time)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil
      and SV.Destiny.MomentScenario ~= SV.Destiny.MomentReverie then
    meteo_reverie.Appliquer(map)
  end
end

local function aller(zone, ground, marqueur)
  if sortie_en_cours then return end
  sortie_en_cours = true
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap(zone, ground, marqueur)
end

function crossroadreverietown2.SortieFalaise_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.VisiteVille == 'terminee' then
    local ground = meteo_reverie.CarteCliff()
    SV.Destiny.FalaiseAmbiance = ground
    aller('destiny_cliff_tests', ground, 'Dazzling_Entry_South')
    return
  end
  aller('destiny_cliff_tests', 'cliffdaytest', 'Dazzling_Entry_South')
end
function crossroadreverietown2.SortieVille_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  aller('town02_waterfallvillage', 'WaterfallVillageCapital', 'entrance')
end

-- Le personnage sérialisé d'origine garde son placement ; aucune réplique ni
-- scène ne lui est inventée ici.
function crossroadreverietown2.NewObject_5_Action(chara, activator) end

return crossroadreverietown2
