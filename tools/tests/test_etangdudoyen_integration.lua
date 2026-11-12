package.preload['destiny.etangdudoyen_scene'] = function()
  return assert(loadfile((arg[1] or '.') .. '/game/Data/Script/destiny/etangdudoyen_scene.lua'))()
end
package.preload['destiny.meteo_reverie'] = function()
  return assert(loadfile((arg[1] or '.') .. '/game/Data/Script/destiny/meteo_reverie.lua'))()
end
package.preload['origin.common'] = function() return {} end
package.preload['destiny.equipe_scene'] = function()
  return {
    Partenaire = function(x, y, dir)
      return {EntName = 'Teammate1', Position = {X = x, Y = y}, Direction = dir}
    end,
    Suivre = function() end,
  }
end

Direction = {
  Up = 'Up', Down = 'Down', Left = 'Left', Right = 'Right',
  UpLeft = 'UpLeft', UpRight = 'UpRight', DownLeft = 'DownLeft', DownRight = 'DownRight',
}
RogueElements = {
  Loc = function(x, y) return {X = x, Y = y} end,
}
RogueEssence = {
  Dungeon = {BaseMap = {ScrollEdge = {Clamp = 'Clamp'}}},
}

local player = {EntName = 'PLAYER', Position = {X = 232, Y = 336}, Direction = Direction.Up}
local mate = {EntName = 'Teammate1', Position = {X = 232, Y = 360}, Direction = Direction.Up}
local doyen = nil
function CH(id)
  if id == 'PLAYER' then return player
  elseif id == 'Teammate1' then return mate
  elseif id == 'Grand_Doyen' then return doyen end
end

local calls = {ground = {}, bgm = {}, amb = {}}
GAME = {
  FadeOut = function() end,
  FadeIn = function() end,
  GetPlayerPartyCount = function() return 2 end,
  EnterGroundMap = function(_, z, g, mk) table.insert(calls.ground, {z, g, mk}) end,
}
GROUND = {
  TeleportTo = function(_, who, x, y, dir)
    who.Position = {X = x, Y = y}
    who.Direction = dir
  end,
  EntTurn = function(_, who, dir)
    who.Direction = dir
  end,
}
SOUND = {
  PlayBGM = function(_, track) table.insert(calls.bgm, track) end,
}

local root = (arg[1] or '.')
local meteo = require 'destiny.meteo_reverie'
local function new_pond_map(name)
  local anim = {MapLoc = {X = 172, Y = 174}, ObjectAnim = {AnimIndex = 'Etang_Nage_Ondes_Jour'}}
  local deco = {Name = 'Nage_Grand_Doyen', Visible = true, Anims = {anim}}
  local m = {
    AssetName = name, Width = 60, Height = 45,
    Decorations = {deco},
  }
  function m:GetObstacle() return 0 end
  function m:SetDestinyAmbiance(a) table.insert(calls.amb, {name, a}) end
  return m, deco, anim
end

for _, amb in ipairs({'jour', 'aube', 'crepuscule', 'nuit'}) do
  SV = {Destiny = {MomentScenario = amb}}
  assert(meteo.CarteEtangDoyen() == 'etangdudoyen_' .. amb)
  package.loaded['destiny.etangdudoyen_scene'] = nil
  local m, deco, _ = new_pond_map('etangdudoyen_' .. amb)
  doyen = nil
  local mod = assert(loadfile(root .. '/game/Data/Script/destiny/ground/etangdudoyen_' .. amb .. '/init.lua'))()
  mod.Init(m)
  assert(m.EdgeView == 'Clamp')
  assert(deco.Visible == false)
end

SV = {Destiny = {MomentScenario = 'jour'}}
package.loaded['destiny.etangdudoyen_scene'] = nil
local m_jour, deco_jour, anim_jour = new_pond_map('etangdudoyen_jour')
doyen = {EntName = 'Grand_Doyen', Position = {X = 0, Y = 0}, Direction = Direction.Down, HideShadow = false}
local mod_jour = assert(loadfile(root .. '/game/Data/Script/destiny/ground/etangdudoyen_jour/init.lua'))()
mod_jour.Init(m_jour)
mod_jour.PreparerNage(m_jour, doyen, 180, 170, Direction.UpRight)
assert(doyen.Position.X == 180 and doyen.Position.Y == 170 and doyen.Direction == Direction.UpRight)
assert(doyen.HideShadow == true)
assert(deco_jour.Visible == true)
assert(anim_jour.MapLoc.X == 172 and anim_jour.MapLoc.Y == 174)
mod_jour.Enter(m_jour)
assert(calls.bgm[#calls.bgm] == 'Luminous Spring.ogg')

SV = {Destiny = {MomentScenario = 'nuit'}}
calls.ground = {}
player.Position = {X = 232, Y = 290}; player.Direction = Direction.Up
mod_jour.Update(m_jour, 0)
assert(#calls.ground == 1 and calls.ground[1][1] == 'reverie' and calls.ground[1][2] == 'etangdudoyen_nuit')
local pa = SV.Destiny.PassageAmbianceEtangDoyen
assert(pa and pa.carte == 'etangdudoyen_nuit' and pa.x == 232 and pa.y == 290)

package.loaded['destiny.etangdudoyen_scene'] = nil
local m_nuit, deco_nuit, _ = new_pond_map('etangdudoyen_nuit')
local mod_nuit = assert(loadfile(root .. '/game/Data/Script/destiny/ground/etangdudoyen_nuit/init.lua'))()
mod_nuit.Init(m_nuit)
mod_nuit.Enter(m_nuit)
assert(player.Position.X == 232 and player.Position.Y == 290 and SV.Destiny.PassageAmbianceEtangDoyen == nil)
assert(deco_nuit.Visible == true and doyen.HideShadow == true)
print('PASS etangdudoyen 4 ambiances + swim prep + HideShadow + AnimLayer alignment')
