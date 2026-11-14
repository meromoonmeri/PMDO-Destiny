-- Simulation Lua aller-retour :
-- PorteGuilde (guilde_cliff_*) <-> guilde_destiny_accueil <-> guilde_destiny_missions.
local root = assert(arg[1])

local current_carte = 'guilde_cliff_jour'
local current_idx = 23

package.preload['origin.common'] = function() return {} end
package.preload['destiny.meteo_reverie'] = function()
  return {
    SynchroniserZone = function() end,
    CarteGuilde = function() return current_carte end,
    IndexGuilde = function() return current_idx end,
  }
end
package.preload['destiny.equipe_scene'] = function()
  return {
    Partenaire = function(x, y, dir) return CH('Teammate1') end,
    Suivre = function() end,
  }
end
package.preload['destiny.suivi_interieurs'] = function()
  local act = 0
  return {
    Activer = function() act = act + 1 end,
    Compteur = function() return act end,
  }
end
package.preload['destiny.cinematique'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/cinematique.lua'))()
end

Direction = {Up=4, Down=0, Left=2, Right=6}
Gender = {Male=1, Female=2, Genderless=0}
RogueElements = {
  Rect = function(x, y, w, h) return {X=x, Y=y, W=w, H=h} end,
  Loc = function(x, y) return {X=x, Y=y} end,
}

local actors = {}
local function make_actor(n, x, y)
  local a = {
    EntName = n,
    Position = {X = x or 0, Y = y or 0},
    Direction = Direction.Down,
    CollisionDisabled = false,
  }
  actors[n] = a
  return a
end
function CH(n) return actors[n] end

local transitions = {}

RogueEssence = {
  Ground = {
    GroundObject = function() return {OnMapInit=function()end, SetTriggerType=function()end} end,
    GroundChar = function(_, loc, dir, name)
      local a = make_actor(name, loc.X, loc.Y)
      a.Direction = dir
      return a
    end,
    GroundEntity = {EEntityTriggerTypes = {Touch=2, Action=1}},
  },
  Dungeon = {
    BaseMap = {ScrollEdge = {Clamp=1}},
    CharData = function() return {} end,
    MonsterID = function(sp, f, sk, g) return {Species=sp, Form=f, Skin=sk, Gender=g} end,
    InvItem = function(id) return {ID=id} end,
  },
}
luanet = {each = function(t) local i=0; return function() i=i+1; return t[i] end end}

GROUND = {
  TeleportTo = function(_, a, x, y, dir) a.Position = {X=x, Y=y}; a.Direction = dir end,
  EntTurn = function(_, a, dir) a.Direction = dir end,
  CharAnimateTurnTo = function(_, a, dir) a.Direction = dir end,
  RemoveCharacter = function(_, n) actors[n] = nil; return true end,
  RemoveObject = function() end,
}
AI = {DisableCharacterAI=function()end, EnableCharacterAI=function()end}
SOUND = {StopBattleSE=function()end, FadeInBattleSE=function()end, FadeOutBattleSE=function()end, PlayBattleSE=function()end}
UI = {SetSpeaker=function()end, SetSpeakerLoc=function()end, SetSpeakerEmotion=function()end, ResetSpeaker=function()end, WaitShowDialogue=function()end}
GAME = {
  CutsceneMode = function() end,
  MoveCamera = function() end,
  FadeIn = function() end,
  FadeOut = function() end,
  WaitFrames = function() end,
  GetPlayerPartyCount = function() return 2 end,
  GetTeamLeaderIndex = function() return 0 end,
  GetPlayerPartyMember = function(_, i) return {Importance = i == 0 and 'Hero' or 'Partner', Data = {}} end,
  GetCurrentGround = function() return nil end,
  EnterGroundMap = function(_, zone, carte, marker, keep_music)
    transitions[#transitions + 1] = {'ground_map', zone, carte, marker, keep_music}
  end,
  EnterZone = function(_, zone, seg, map_id, entry_id)
    transitions[#transitions + 1] = {'zone', zone, seg, map_id, entry_id}
  end,
}
function LTBL(m) return {Importance = m.Importance} end

local accueil = assert(loadfile(root .. '/game/Data/Script/destiny/ground/guilde_destiny_accueil/init.lua'))()
local missions = assert(loadfile(root .. '/game/Data/Script/destiny/ground/guilde_destiny_missions/init.lua'))()

local ambiances = {
  {'jour', 23},
  {'aube', 24},
  {'crepuscule', 25},
  {'nuit', 26},
}

for _, info in ipairs(ambiances) do
  current_carte, current_idx = 'guilde_cliff_' .. info[1], info[2]
  package.loaded['destiny.guilde_cliff_scene'] = nil
  package.preload['destiny.guilde_cliff_scene'] = function()
    return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_cliff_scene.lua'))()
  end
  local cliff = assert(loadfile(root .. '/game/Data/Script/destiny/ground/' .. current_carte .. '/init.lua'))()

  actors = {}
  make_actor('PLAYER', 232, 272)
  make_actor('Teammate1', 208, 280)
  SV = {Destiny = {AlerteShinx = 'termine', EnrolementGuilde = 'termine'}}
  transitions = {}

  local m = {
    AssetName = current_carte,
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

  cliff.Init(m)
  cliff.PorteGuilde_Touch(m.Objects.PorteGuilde, actors.PLAYER)
  assert(#transitions == 1, current_carte .. ' doit entrer dans guilde_destiny_accueil')
  assert(transitions[1][1] == 'ground_map' and transitions[1][2] == 'guilde_destiny_interieur' and transitions[1][3] == 'guilde_destiny_accueil' and transitions[1][4] == 'EntreeSudMarker')
  assert(m.Decorations[3].Visible == true and m.Decorations[4].Visible == false)

  -- Transition Accueil -> Grande Salle (EscalierNord)
  local m_int = {EdgeView = 0}
  accueil.Init(m_int)
  accueil.Enter(m_int)
  assert(m_int.EdgeView == 1)

  transitions = {}
  accueil.EscalierNord_Touch({}, actors.Teammate1)
  assert(#transitions == 0, 'Le partenaire ne doit pas déclencher EscalierNord')
  accueil.EscalierNord_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][1] == 'ground_map' and transitions[1][2] == 'guilde_destiny_interieur' and transitions[1][3] == 'guilde_destiny_missions' and transitions[1][4] == 'ArriveeDepuisAccueilMarker' and transitions[1][5] == true)

  -- Transition Grande Salle -> Accueil (EscalierNord)
  local m_mis = {EdgeView = 0}
  missions.Init(m_mis)
  missions.Enter(m_mis)
  assert(m_mis.EdgeView == 1)

  transitions = {}
  missions.EscalierNord_Touch({}, actors.Teammate1)
  assert(#transitions == 0, 'Le partenaire ne doit pas déclencher EscalierNord dans missions')
  missions.EscalierNord_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][1] == 'ground_map' and transitions[1][2] == 'guilde_destiny_interieur' and transitions[1][3] == 'guilde_destiny_accueil' and transitions[1][4] == 'EscalierNordMarker' and transitions[1][5] == true)

  -- Réentrée dans Accueil puis sortie vers la falaise
  accueil.Enter(m_int)
  transitions = {}
  accueil.SortieGuilde_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][1] == 'zone' and transitions[1][2] == 'town02_waterfallvillage' and transitions[1][4] == current_idx)
  assert(SV.Destiny.PassageAmbiance ~= nil and SV.Destiny.PassageAmbiance.carte == current_carte and SV.Destiny.PassageAmbiance.x == 232 and SV.Destiny.PassageAmbiance.y == 282)

  cliff.Enter(m)
  assert(actors.PLAYER.Position.X == 232 and actors.PLAYER.Position.Y == 282 and actors.PLAYER.Direction == Direction.Down)
  assert(SV.Destiny.PassageAmbiance == nil)
end

print('PASS test_guilde_destiny_accueil.lua : aller-retour falaise <-> accueil <-> grande salle validé sur les 4 ambiances.')
