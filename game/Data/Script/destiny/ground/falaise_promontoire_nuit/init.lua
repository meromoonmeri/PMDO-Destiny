require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local CARTE = 'falaise_promontoire_nuit'
local falaise_promontoire_nuit = {}
local SON_MER = 'Destiny_Falaise_Mer'

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

function falaise_promontoire_nuit.Init(map)
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local py = math.min(hero.Position.Y + 24, 420)
    local partner = equipe_scene.Partenaire(hero.Position.X, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function falaise_promontoire_nuit.Enter(map)
  demarrer_mer()
  GAME:FadeIn(20)
end

function falaise_promontoire_nuit.GameLoad(map)
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  demarrer_mer()
  GAME:FadeIn(20)
end

function falaise_promontoire_nuit.Exit(map)
  arreter_mer()
end

function falaise_promontoire_nuit.GameSave(map)
end

return falaise_promontoire_nuit
