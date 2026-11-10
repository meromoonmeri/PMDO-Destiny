package.preload['destiny.meteo_reverie'] = function()
  return assert(loadfile((arg[1] or '.') .. '/game/Data/Script/destiny/meteo_reverie.lua'))()
end
package.preload['origin.common'] = function() return {} end
package.preload['origin.menu.skill.SkillSelectMenu'] = function() return {} end
package.preload['origin.menu.team.AssemblySelectMenu'] = function() return {} end
package.preload['destiny.equipe_scene'] = function()
  return {
    Partenaire = function(x, y, dir)
      return {EntName = 'Teammate1', Position = {X = x, Y = y}, Direction = dir}
    end,
    Suivre = function() end,
  }
end
package.preload['destiny.cinematique'] = function() return {NomEspece = function(_, n) return n end} end
package.preload['destiny.missions_reverie'] = function() return {} end

Direction = {
  Up = 'Up', Down = 'Down', Left = 'Left', Right = 'Right',
  UpLeft = 'UpLeft', UpRight = 'UpRight', DownLeft = 'DownLeft', DownRight = 'DownRight',
}
Gender = {Male = 'Male', Female = 'Female', Genderless = 'Genderless'}
RogueElements = {Rect = function(x, y, w, h) return {x = x, y = y, w = w, h = h} end}
RogueEssence = {
  Ground = {
    GroundObject = function()
      return {
        OnMapInit = function() end,
        SetTriggerType = function(self, t) self.TriggerType = t end,
      }
    end,
    GroundEntity = {EEntityTriggerTypes = {Touch = 'Touch', Action = 'Action'}},
  },
  Dungeon = {
    BaseMap = {ScrollEdge = {Clamp = 'Clamp'}},
    CharData = function() return {} end,
    MonsterID = function(species) return {Species = species} end,
    Character = function(data) return data end,
  },
}

local player = {EntName = 'PLAYER', Position = {X = 1120, Y = 2352}, Direction = Direction.Down}
local mate = {EntName = 'Teammate1', Position = {X = 1120, Y = 2328}, Direction = Direction.Down}
local current_map
function CH(id)
  if id == 'PLAYER' then return player
  elseif id == 'Teammate1' then return mate
  elseif current_map and current_map.characters then return current_map.characters[id] end
end
AI = {DisableCharacterAI = function() end, EnableCharacterAI = function() end}

local calls = {zone = {}, ground = {}, battle_se_stop = 0, battle_se_fade_in = 0, battle_se_fade_out = 0}
GAME = {
  FadeOut = function() end,
  FadeIn = function() end,
  MoveCamera = function() end,
  CutsceneMode = function() end,
  GetPlayerPartyCount = function() return 2 end,
  EnterZone = function(_, z, s, m, e) table.insert(calls.zone, {z, s, m, e}) end,
  EnterGroundMap = function(_, z, g, mk) table.insert(calls.ground, {z, g, mk}) end,
}
GROUND = {
  AddMapStatus = function() end,
  RemoveMapStatus = function() end,
  Unhide = function() end,
  Hide = function() end,
  RemoveCharacter = function(_, n) if current_map.characters then current_map.characters[n] = nil end end,
  RemoveObject = function(_, n) current_map.objects[n] = nil end,
  TeleportTo = function(_, who, x, y, dir) who.Position = {X = x, Y = y}; who.Direction = dir end,
  EntTurn = function(_, who, dir) who.Direction = dir end,
  CharEndAnim = function() end,
  CharTurnToChar = function() end,
  CreateCharacterFromCharData = function(_, name, data, x, y, dir)
    local c = {EntName = name, Position = {X = x, Y = y}, Direction = dir, Data = data, ReloadEvents = function() end}
    current_map.characters[name] = c
    return c
  end,
}
SOUND = {
  PlayBGM = function() end,
  StopBattleSE = function() calls.battle_se_stop = calls.battle_se_stop + 1 end,
  FadeInBattleSE = function() calls.battle_se_fade_in = calls.battle_se_fade_in + 1 end,
  FadeOutBattleSE = function() calls.battle_se_fade_out = calls.battle_se_fade_out + 1 end,
}

local root = (arg[1] or '.')
local function new_city_map(name)
  local m = {AssetName = name, Width = 200, Height = 500, objects = {}, characters = {}}
  function m:GetMapChar(n) return self.characters[n] end
  function m:FindObject(n) return self.objects[n] end
  function m:AddObject(o) self.objects[o.EntName] = o end
  function m:GetObstacle(x, y) return 0 end
  return m
end

local function new_cliff_map(name)
  local m = {AssetName = name, Width = 80, Height = 64, objects = {}}
  function m:FindObject(n) return self.objects[n] end
  function m:AddObject(o) self.objects[o.EntName] = o end
  function m:GetObstacle(x, y) return 0 end
  return m
end

-- 1. Only reverie_etang (not centre/nord/residentiel) installs SortieFalaisePromontoire
for _, sec in ipairs({'reverie_centre', 'reverie_nord', 'reverie_residentiel'}) do
  SV = {Destiny = {VisiteVille = 'terminee'}}
  current_map = new_city_map(sec)
  local ville = assert(loadfile(root .. '/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
  ville.Init(current_map)
  assert(current_map.objects.SortieFalaisePromontoire == nil, sec .. ' should not have SortieFalaisePromontoire')
end

-- 2. Round-trip across all 4 ambiances from reverie_etang -> falaise_promontoire_* -> reverie_etang
local ambiances = {
  {'jour',       0, 'falaise_promontoire_jour'},
  {'aube',       1, 'falaise_promontoire_aube'},
  {'crepuscule', 2, 'falaise_promontoire_crepuscule'},
  {'nuit',       3, 'falaise_promontoire_nuit'},
}
for _, cas in ipairs(ambiances) do
  local amb, idx, carte = cas[1], cas[2], cas[3]
  SV = {Destiny = {VisiteVille = 'terminee', MomentScenario = amb, MomentReverie = amb}}
  calls.zone = {}; calls.ground = {}
  current_map = new_city_map('reverie_etang')
  local ville = assert(loadfile(root .. '/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
  ville.Init(current_map)
  local sortie = current_map.objects.SortieFalaisePromontoire
  assert(sortie ~= nil and sortie.Passable == false and sortie.TriggerType == 'Touch')
  assert(sortie.Collider.x == 1584 and sortie.Collider.y == 2024 and sortie.Collider.w == 16 and sortie.Collider.h == 72)

  -- Non-player touch ignored
  ville.SortieFalaisePromontoire_Touch(sortie, mate)
  assert(#calls.zone == 0)
  -- Player touch routes to synced ambiance
  ville.SortieFalaisePromontoire_Touch(sortie, player)
  assert(#calls.zone == 1 and calls.zone[1][1] == 'falaise_promontoire' and calls.zone[1][3] == idx and calls.zone[1][4] == 0)
  -- Double touch guard
  ville.SortieFalaisePromontoire_Touch(sortie, player)
  assert(#calls.zone == 1)

  -- Enter promontory and return west -> reverie_etang facing Left
  calls.zone = {}; calls.ground = {}
  player.Position = {X = 24, Y = 292}; player.Direction = Direction.Right
  current_map = new_cliff_map(carte)
  local prom = assert(loadfile(root .. '/game/Data/Script/destiny/ground/' .. carte .. '/init.lua'))()
  prom.Init(current_map)
  assert(current_map.EdgeView == 'Clamp')
  local ret = current_map.objects.RetourEtangReverie
  assert(ret ~= nil and ret.Passable == false and ret.TriggerType == 'Touch')
  assert(ret.Collider.x == 0 and ret.Collider.y == 176 and ret.Collider.w == 8 and ret.Collider.h == 256)
  prom.Enter(current_map)
  prom.RetourEtangReverie_Touch(ret, mate)
  assert(#calls.ground == 0)
  prom.RetourEtangReverie_Touch(ret, player)
  assert(#calls.ground == 1 and calls.ground[1][1] == 'town02_waterfallvillage' and calls.ground[1][2] == 'reverie_etang' and calls.ground[1][3] == 'entrance')
  prom.RetourEtangReverie_Touch(ret, player)
  assert(#calls.ground == 1)
  local pq = SV.Destiny.PassageQuartier
  assert(pq and pq.x == 1536 and pq.y == 2056 and pq.px == 1560 and pq.py == 2056 and pq.dir == 'Left')

  -- Arrive back on reverie_etang facing Left with safe margin from trigger
  current_map = new_city_map('reverie_etang')
  ville = assert(loadfile(root .. '/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
  ville.Init(current_map)
  ville.Enter(current_map)
  assert(player.Position.X == 1536 and player.Position.Y == 2056 and player.Direction == 'Left')
  assert(mate.Position.X == 1560 and mate.Position.Y == 2056 and mate.Direction == 'Left')
  assert(SV.Destiny.PassageQuartier == nil)
end

-- 3. Automatic ambiance switch when MomentScenario changes while standing on falaise_promontoire_jour
SV = {Destiny = {VisiteVille = 'terminee', MomentScenario = 'nuit', MomentReverie = 'nuit'}}
calls.zone = {}
player.Position = {X = 240, Y = 280}; player.Direction = Direction.Right
current_map = new_cliff_map('falaise_promontoire_jour')
local prom_jour = assert(loadfile(root .. '/game/Data/Script/destiny/ground/falaise_promontoire_jour/init.lua'))()
prom_jour.Init(current_map)
prom_jour.Update(current_map, 0)
assert(#calls.zone == 1 and calls.zone[1][1] == 'falaise_promontoire' and calls.zone[1][3] == 3)
local pa = SV.Destiny.PassageAmbiancePromontoire
assert(pa and pa.carte == 'falaise_promontoire_nuit' and pa.x == 240 and pa.y == 280)
current_map = new_cliff_map('falaise_promontoire_nuit')
local prom_nuit = assert(loadfile(root .. '/game/Data/Script/destiny/ground/falaise_promontoire_nuit/init.lua'))()
prom_nuit.Init(current_map)
prom_nuit.Enter(current_map)
assert(player.Position.X == 240 and player.Position.Y == 280 and SV.Destiny.PassageAmbiancePromontoire == nil)
print('PASS round-trip reverie_etang <-> falaise_promontoire (4 ambiances + synchro auto)')
