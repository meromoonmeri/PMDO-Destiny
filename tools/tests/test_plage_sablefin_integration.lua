package.preload['destiny.plage_sablefin_scene'] = function()
  return assert(loadfile((arg[1] or '.') .. '/game/Data/Script/destiny/plage_sablefin_scene.lua'))()
end
package.preload['destiny.meteo_reverie'] = function()
  return assert(loadfile((arg[1] or '.') .. '/game/Data/Script/destiny/meteo_reverie.lua'))()
end
package.preload['origin.common'] = function() return {} end
package.preload['destiny.recrutement'] = function() return {synchroniser = function() end} end
package.preload['destiny.equipe_scene'] = function()
  return {
    Partenaire = function(x, y, dir)
      return {EntName = 'Teammate1', Position = {X = x, Y = y}, Direction = dir}
    end,
    Suivre = function() end,
  }
end
package.preload['destiny.missions_reverie'] = function() return {} end

Direction = {
  Up = 'Up', Down = 'Down', Left = 'Left', Right = 'Right',
  UpLeft = 'UpLeft', UpRight = 'UpRight', DownLeft = 'DownLeft', DownRight = 'DownRight',
}
RogueElements = {Rect = function(x, y, w, h) return {x = x, y = y, w = w, h = h} end}
RogueEssence = {
  Data = {
    GameProgress = {
      DungeonStakes = {Risk = 'Risk'},
      ResultType = {Cleared = 'Cleared', Downed = 'Downed'},
    },
  },
  Ground = {
    GroundObject = function()
      return {
        OnMapInit = function() end,
        SetTriggerType = function(self, t) self.TriggerType = t end,
      }
    end,
    GroundEntity = {EEntityTriggerTypes = {Touch = 'Touch', Action = 'Action'}},
  },
  Dungeon = {BaseMap = {ScrollEdge = {Clamp = 'Clamp'}}},
}

local player = {EntName = 'PLAYER', Position = {X = 488, Y = 912}, Direction = Direction.Down}
local mate = {EntName = 'Teammate1', Position = {X = 488, Y = 888}, Direction = Direction.Down}
function CH(id)
  if id == 'PLAYER' then return player
  elseif id == 'Teammate1' then return mate end
end

local calls = {ground = {}, dungeon = {}, zone = {}, end_day = {}, se = {}}
GAME = {
  FadeOut = function() end,
  FadeIn = function() end,
  GetPlayerPartyCount = function() return 2 end,
  SetRescueAllowed = function() end,
  EnterGroundMap = function(_, z, g, mk) table.insert(calls.ground, {z, g, mk}) end,
  EnterDungeon = function(_, z, s, m) table.insert(calls.dungeon, {z, s, m}) end,
  EnterZone = function(_, z, s, m, e) table.insert(calls.zone, {z, s, m, e}) end,
}
GROUND = {
  AddMapStatus = function() end,
  RemoveMapStatus = function() end,
  TeleportTo = function(_, who, x, y, dir) who.Position = {X = x, Y = y}; who.Direction = dir end,
}
SOUND = {
  PlayBGM = function() end,
  FadeOutBGM = function() end,
  StopBattleSE = function(_, s) table.insert(calls.se, {'stop', s}) end,
  FadeInBattleSE = function(_, s) table.insert(calls.se, {'in', s}) end,
  FadeOutBattleSE = function(_, s) table.insert(calls.se, {'out', s}) end,
}
local choice_res = true
UI = {
  ResetSpeaker = function() end,
  ChoiceMenuYesNo = function() end,
  WaitForChoice = function() end,
  ChoiceResult = function() return choice_res end,
  WaitShowDialogue = function() end,
}
DEBUG = {EnableDbgCoro = function() end}
COMMON = {
  ExitDungeonMissionCheck = function() return false end,
  BeginDungeon = function() end,
  Rescued = function() end,
  EndDungeonDay = function(r, z, s, m, e) table.insert(calls.end_day, {r, z, s, m, e}) end,
}

local root = (arg[1] or '.')
local function new_map(name)
  local m = {AssetName = name, Width = 120, Height = 120, objects = {}}
  function m:FindObject(n) return self.objects[n] end
  function m:AddObject(o) self.objects[o.EntName] = o end
  function m:GetObstacle() return 0 end
  return m
end

for _, cas in ipairs({{'jour', 0}, {'aube', 1}, {'crepuscule', 2}, {'nuit', 3}}) do
  local amb, idx = cas[1], cas[2]
  SV = {Destiny = {MomentScenario = amb, MomentReverie = amb}}
  calls.ground = {}; calls.dungeon = {}
  local m_cr = new_map('crossroadreverietown2')
  local cr = assert(loadfile(root .. '/game/Data/Script/destiny/ground/crossroadreverietown2/init.lua'))()
  cr.Init(m_cr)
  assert(m_cr.objects.SortiePlage ~= nil and m_cr.objects.SortiePlage.TriggerType == 'Touch')
  cr.SortiePlage_Touch(m_cr.objects.SortiePlage, mate)
  assert(#calls.ground == 0)
  cr.SortiePlage_Touch(m_cr.objects.SortiePlage, player)
  assert(#calls.ground == 1 and calls.ground[1][1] == 'passage_aquatique'
    and calls.ground[1][2] == 'plage_sablefin_' .. amb and calls.ground[1][3] == 'entrance')

  package.loaded['destiny.plage_sablefin_scene'] = nil
  calls.ground = {}
  local m_pl = new_map('plage_sablefin_' .. amb)
  local pl = assert(loadfile(root .. '/game/Data/Script/destiny/ground/plage_sablefin_' .. amb .. '/init.lua'))()
  pl.Init(m_pl)
  pl.Enter(m_pl)
  pl.SortieCarrefour_Touch(nil, mate)
  assert(#calls.ground == 0)
  pl.SortieCarrefour_Touch(nil, player)
  assert(#calls.ground == 1 and calls.ground[1][1] == 'reverie'
    and calls.ground[1][2] == 'crossroadreverietown2' and calls.ground[1][3] == 'entree_plage')
end

SV = {Destiny = {MomentScenario = 'crepuscule'}}
calls.dungeon = {}; calls.zone = {}; calls.end_day = {}; calls.ground = {}
package.loaded['destiny.plage_sablefin_scene'] = nil
local pl_crep = assert(loadfile(root .. '/game/Data/Script/destiny/ground/plage_sablefin_crepuscule/init.lua'))()
local m_crep = new_map('plage_sablefin_crepuscule')
pl_crep.Init(m_crep)
choice_res = false
pl_crep.SeuilPassageAquatique_Touch(nil, player)
assert(#calls.dungeon == 0)
choice_res = true
pl_crep.SeuilPassageAquatique_Touch(nil, player)
assert(#calls.dungeon == 1 and calls.dungeon[1][1] == 'passage_aquatique' and SV.Destiny.ExplorationPassageAquatique == true)

local zpa = assert(loadfile(root .. '/game/Data/Script/destiny/zone/passage_aquatique/init.lua'))()
zpa.ExitSegment({ID = 'passage_aquatique'}, 'Cleared', false, 0, 9)
assert(#calls.zone == 1 and calls.zone[1][1] == 'passage_aquatique' and calls.zone[1][3] == 4)

local paf = assert(loadfile(root .. '/game/Data/Script/destiny/ground/passage_aquatique_fond/init.lua'))()
local m_paf = new_map('passage_aquatique_fond')
paf.Init(m_paf)
paf.Enter(m_paf)
paf.SortieTunnelSud_Touch(nil, player)
assert(#calls.end_day == 1 and calls.end_day[1][2] == 'passage_aquatique' and calls.end_day[1][4] == 2 and calls.end_day[1][5] == 2)
assert(SV.Destiny.ExplorationPassageAquatique == nil)

zpa.ExitSegment({ID = 'passage_aquatique'}, 'Downed', false, 0, 4)
assert(#calls.end_day == 2 and calls.end_day[2][1] == 'Downed' and calls.end_day[2][4] == 2 and calls.end_day[2][5] == 2)
print('PASS plage_sablefin + passage_aquatique 10F + crique secrete + crossroad connection')
