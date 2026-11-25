-- Tests Lua d'enrôlement à la Grande Guilde sur les 4 ambiances guilde_cliff_*.
local root = assert(arg[1])

package.preload['origin.common'] = function() return {} end
package.preload['destiny.meteo_reverie'] = function()
  return {
    SynchroniserZone = function() end,
    CarteGuilde = function() return current_carte end,
    IndexGuilde = function() return 23 end,
  }
end
package.preload['destiny.equipe_scene'] = function()
  return {
    Partenaire = function(x, y, dir) return CH('Teammate1') end,
    Suivre = function() end,
  }
end
package.preload['destiny.cinematique'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/cinematique.lua'))()
end

Direction = {Up=4, Down=0, Left=2, Right=6, UpLeft=3, UpRight=5, DownLeft=1, DownRight=7}
Gender = {Male=1, Female=2, Genderless=0}
RogueElements = {
  Rect = function(x, y, w, h) return {X=x, Y=y, W=w, H=h} end,
  Loc = function(x, y) return {X=x, Y=y} end,
}

local actors = {}
local function make_actor(n, x, y, sp)
  local a = {
    EntName = n,
    Position = {X = x or 0, Y = y or 0},
    Direction = Direction.Down,
    EntEnabled = true,
    CollisionDisabled = false,
    Data = {Nickname = n, BaseForm = {Species = sp}},
  }
  function a:GetDisplayName() return self.EntName end
  function a:ReloadEvents() self.reloaded = true end
  actors[n] = a
  return a
end
function CH(n) return actors[n] end

local cur_map = nil
local events = {}
local function ev(k, ...) events[#events+1] = {k, ...} end

RogueEssence = {
  Ground = {
    GroundObject = function() return {OnMapInit=function()end, SetTriggerType=function()end} end,
    GroundChar = function(data, loc, dir, name)
      local a = make_actor(name, loc.X, loc.Y)
      a.Data = data
      a.Direction = dir
      return a
    end,
    GroundEntity = {EEntityTriggerTypes = {Touch=2, Action=1}},
  },
  Dungeon = {
    BaseMap = {ScrollEdge = {Clamp=1}},
    CharData = function() return {} end,
    MonsterID = function(sp, f, sk, g) return {Species=sp, Form=f, Skin=sk, Gender=g} end,
    InvItem = function(id) return {ID=id, GetDisplayName=function() return id end} end,
  },
}

luanet = {
  each = function(t)
    local i = 0
    return function()
      i = i + 1
      return t[i]
    end
  end,
}

GROUND = {
  TeleportTo = function(_, a, x, y, dir) a.Position = {X=x, Y=y}; a.Direction = dir end,
  MoveInDirection = function(_, a, dir, amt) a.Position.Y = a.Position.Y + amt end,
  EntTurn = function(_, a, dir) a.Direction = dir end,
  CharAnimateTurnTo = function(_, a, dir) a.Direction = dir end,
  CharTurnToChar = function() end,
  CharSetAnim = function() end,
  CharEndAnim = function() end,
  CharSetEmote = function(_, a, em) ev('emote', a.EntName, em) end,
  RemoveCharacter = function(_, n) actors[n] = nil; return true end,
  RemoveObject = function(_, n) if cur_map and cur_map.Objects then cur_map.Objects[n] = nil end end,
}
AI = {DisableCharacterAI=function()end, EnableCharacterAI=function()end}
SOUND = {
  StopBattleSE = function() end,
  FadeInBattleSE = function() end,
  FadeOutBattleSE = function() end,
  PlayBattleSE = function(_, s) ev('se', s) end,
}
UI = {
  SetSpeaker = function() end,
  SetSpeakerLoc = function() end,
  SetSpeakerEmotion = function() end,
  ResetSpeaker = function() end,
  WaitShowDialogue = function(_, txt) ev('dlg', txt) end,
}
GAME = {
  CutsceneMode = function() end,
  MoveCamera = function() end,
  FadeIn = function() end,
  FadeOut = function() end,
  WaitFrames = function() end,
  GetPlayerPartyCount = function() return 2 end,
  GetTeamLeaderIndex = function() return 0 end,
  GetPlayerPartyMember = function(_, i) return {Importance = i == 0 and 'Hero' or 'Partner', Data = {}} end,
  GetCurrentGround = function() return cur_map end,
  EnterZone = function(_, ...) ev('enter_zone', ...) end,
}
COMMON = {
  GiftItem = function(hero, item)
    assert(hero ~= nil and type(item.ID) == 'string')
    ev('gift', item.ID)
  end,
}
function LTBL(m) return {Importance = m.Importance} end

local function make_map(carte)
  local m = {
    AssetName = carte,
    Objects = {},
    Decorations = {
      {Name='Ombres_Nuages_Cliff', Visible=true},
      {Name='BatimentGuildeOmbre', Visible=true},
      {Name='BatimentGuilde', Visible=true},
      {Name='BatimentGuildeOuverte', Visible=false},
    },
  }
  function m:FindObject(n) return self.Objects[n] end
  function m:AddObject(o) self.Objects[o.EntName] = o end
  function m:AddMapChar(c) actors[c.EntName] = c end
  cur_map = m
  return m
end

for _, amb in ipairs({'jour', 'aube', 'crepuscule', 'nuit'}) do
  current_carte = 'guilde_cliff_' .. amb
  package.loaded['destiny.guilde_cliff_scene'] = nil
  package.preload['destiny.guilde_cliff_scene'] = function()
    return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_cliff_scene.lua'))()
  end
  local mod = assert(loadfile(root .. '/game/Data/Script/destiny/' .. 'ground/' .. current_carte .. '/init.lua'))()

  -- 1. Avant sauvetage de Nilo : porte fermée refusant les intrus
  actors = {}; make_actor('PLAYER', 232, 464); make_actor('Teammate1', 232, 488)
  SV = {Destiny={AlerteShinx='a_secourir'}}
  events = {}
  local m1 = make_map(current_carte)
  mod.Init(m1)
  assert(m1.Objects.PorteGuilde and not m1.Objects.ZoneAccueilGuilde and not actors.Guilde_Chatot)
  mod.PorteGuilde_Touch(m1.Objects.PorteGuilde, actors.PLAYER)
  assert(m1.Decorations[3].Visible == true and m1.Decorations[4].Visible == false, 'porte non refermée')
  assert(actors.PLAYER.Position.Y == 282)

  -- 2. Après sauvetage de Nilo : comité d'accueil + enrôlement + food_apple_perfect
  actors = {}; make_actor('PLAYER', 232, 464); make_actor('Teammate1', 232, 488)
  SV = {Destiny={AlerteShinx='termine'}}
  events = {}
  local m2 = make_map(current_carte)
  mod.Init(m2)
  assert(m2.Objects.ZoneAccueilGuilde and actors.Guilde_Chatot and actors.Guilde_Sunflora and actors.Guilde_Loudred)
  mod.ZoneAccueilGuilde_Touch(m2.Objects.ZoneAccueilGuilde, actors.PLAYER)
  assert(SV.Destiny.EnrolementGuilde == 'termine')
  assert(m2.Decorations[3].Visible == true and m2.Decorations[4].Visible == false)
  assert(not m2.Objects.ZoneAccueilGuilde and not actors.Guilde_Wigglytuff and not actors.Guilde_Chatot)
  local door_se, gift_apple = 0, false
  for _, e in ipairs(events) do
    if e[1] == 'se' and e[2] == 'EVT_Door_Open' then door_se = door_se + 1 end
    if e[1] == 'gift' and e[2] == 'food_apple_perfect' then gift_apple = true end
  end
  assert(door_se >= 1 and gift_apple, amb .. ' porte ou food_apple_perfect manquant')

  -- 3. Après enrôlement : accueil amical devant la porte
  actors = {}; make_actor('PLAYER', 232, 272); make_actor('Teammate1', 208, 280)
  events = {}
  local m3 = make_map(current_carte)
  mod.Init(m3)
  assert(not m3.Objects.ZoneAccueilGuilde)
  mod.PorteGuilde_Touch(m3.Objects.PorteGuilde, actors.PLAYER)
  assert(m3.Decorations[3].Visible == true and m3.Decorations[4].Visible == false)
end

print('PASS test_guilde_enrolement.lua : 4 ambiances, porte ouverte/fermée, accueil et Pomme Dorée.')
