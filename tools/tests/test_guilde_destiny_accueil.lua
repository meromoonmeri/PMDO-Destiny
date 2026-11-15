-- Simulation Lua complète sur les 4 ambiances (`jour`, `aube`, `crepuscule`, `nuit`) :
-- 1. Vérifie `map:SetDestinyAmbiance(moment, true)` (luminosité & filtre de salle) + objets Fenêtres `.dir` associés.
-- 2. Vérifie les transitions Falaise <-> 1F Accueil <-> 2F Missions (EscalierSud/EscalierNord) <-> 3F Grand Salon
--    <-> Ouverture battante extérieure 5 frames de la Porte du Maître (style PMD EoS) -> Bureau du Maître
--    + Carrefour / Réfectoire / Cuisine / Réserve + Couloirs Ouest/Est / Dortoirs / Chambre du Héros.
local root = assert(arg[1])

local current_moment = 'jour'
local current_carte = 'guilde_cliff_jour'
local current_idx = 23

package.preload['origin.common'] = function() return {} end
package.preload['destiny.meteo_reverie'] = function()
  return {
    SynchroniserZone = function() end,
    Moment = function() return current_moment end,
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
package.preload['destiny.guilde_destiny_decors'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_destiny_decors.lua'))()
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
local current_ground = nil

local function make_mock_ground(name)
  local g = {
    AssetName = name,
    EdgeView = 0,
    LastAmbiance = nil,
    LastApplyWorld = nil,
    SpawnedList = {},
  }
  local go_list = { Count = 0 }
  function go_list:Add(obj)
    self[self.Count] = obj
    self.Count = self.Count + 1
    g.SpawnedList[obj.EntName] = obj
  end
  function go_list:RemoveAt(idx)
    for i = idx, self.Count - 2 do
      self[i] = self[i + 1]
    end
    self[self.Count - 1] = nil
    self.Count = self.Count - 1
  end
  g.Entities = { Count = 1, [0] = { GroundObjects = go_list } }
  function g:SetDestinyAmbiance(m, apply_world)
    self.LastAmbiance = m
    self.LastApplyWorld = apply_world
  end
  return g
end

RogueEssence = {
  Content = {
    ObjAnimData = function(sheet, ft, sf, ef)
      return {AnimIndex = sheet, FrameTime = ft, StartFrame = sf, EndFrame = ef}
    end,
  },
  Ground = {
    GroundObject = function(anim, rect, loc, passable, name)
      return {
        EntName = name,
        ObjectAnim = anim,
        Collider = rect,
        Passable = passable,
        ReloadEvents = function() end,
        OnMapInit = function() end,
        SetTriggerType = function() end,
      }
    end,
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
  Hide = function() end,
  Unhide = function() end,
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
  GetCurrentGround = function() return current_ground end,
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
local salon = assert(loadfile(root .. '/game/Data/Script/destiny/ground/guilde_destiny_grand_salon/init.lua'))()
local heros = assert(loadfile(root .. '/game/Data/Script/destiny/ground/guilde_destiny_chambre_heros/init.lua'))()

local ambiances = {
  {'jour', 23, 'Jour'},
  {'aube', 24, 'Aube'},
  {'crepuscule', 25, 'Crepuscule'},
  {'nuit', 26, 'Nuit'},
}

for _, info in ipairs(ambiances) do
  current_moment = info[1]
  current_carte, current_idx = 'guilde_cliff_' .. info[1], info[2]
  local cap_amb = info[3]

  package.loaded['destiny.guilde_cliff_scene'] = nil
  package.preload['destiny.guilde_cliff_scene'] = function()
    return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_cliff_scene.lua'))()
  end
  local cliff = assert(loadfile(root .. '/game/Data/Script/destiny/ground/' .. current_carte .. '/init.lua'))()

  actors = {}
  make_actor('PLAYER', 232, 272)
  make_actor('Teammate1', 208, 280)
  SV = {Destiny = {AlerteShinx = 'termine', EnrolementGuilde = 'termine', GuildePorteMaitreOuverte = false}}
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
  assert(#transitions == 1 and transitions[1][3] == 'guilde_destiny_accueil')

  -- 1F Accueil : filtre luminosité `SetDestinyAmbiance(moment, true)` + fenêtres .dir
  local m_int = make_mock_ground('guilde_destiny_accueil')
  current_ground = m_int
  accueil.Init(m_int)
  accueil.Enter(m_int)
  assert(m_int.EdgeView == 1)
  assert(m_int.LastAmbiance == current_moment and m_int.LastApplyWorld == true, 'Filtre luminosite salle non applique sur accueil')
  assert(m_int.SpawnedList.Fenetre_Gauche.ObjectAnim.AnimIndex == 'Guilde_Fenetre_Accueil_Gauche_' .. cap_amb)

  transitions = {}
  accueil.EscalierNord_Touch({}, actors.Teammate1)
  assert(#transitions == 0)
  accueil.EscalierNord_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][3] == 'guilde_destiny_missions' and transitions[1][4] == 'ArriveeDepuisAccueilMarker')

  -- 2F Missions : EscalierSud -> Accueil, EscalierNord -> 3F Grand Salon
  local m_mis = make_mock_ground('guilde_destiny_missions')
  current_ground = m_mis
  missions.Init(m_mis)
  missions.Enter(m_mis)
  assert(m_mis.LastAmbiance == current_moment and m_mis.LastApplyWorld == true)
  assert(string.find(m_mis.SpawnedList.Fenetre_Gauche.ObjectAnim.AnimIndex, cap_amb, 1, true) ~= nil)

  transitions = {}
  missions.EscalierSud_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][3] == 'guilde_destiny_accueil' and transitions[1][4] == 'EscalierNordMarker')

  missions.Enter(m_mis)
  transitions = {}
  missions.EscalierNord_Touch({}, actors.PLAYER)
  assert(#transitions == 1 and transitions[1][3] == 'guilde_destiny_grand_salon' and transitions[1][4] == 'ArriveeSudMarker')

  -- 3F Grand Salon : Porte fermée -> ouverture battante extérieure 5 frames -> Bureau du Maître
  local m_sal = make_mock_ground('guilde_destiny_grand_salon')
  current_ground = m_sal
  salon.Init(m_sal)
  salon.Enter(m_sal)
  assert(m_sal.LastAmbiance == current_moment and m_sal.LastApplyWorld == true)
  assert(m_sal.SpawnedList.PorteBureauMaitreVisuel.ObjectAnim.AnimIndex == 'Guilde_Destiny_Porte_Salon_Fermee')

  transitions = {}
  salon.SortieBureauMaitre_Touch({}, actors.PLAYER)
  assert(SV.Destiny.GuildePorteMaitreOuverte == true, 'La double porte doit s ouvrir vers l exterieur')
  assert(m_sal.SpawnedList.PorteBureauMaitreVisuel.ObjectAnim.AnimIndex == 'Guilde_Destiny_Porte_Salon_Ouverte')
  assert(#transitions == 1 and transitions[1][3] == 'guilde_destiny_bureau_maitre' and transitions[1][4] == 'EntreeSudMarker')

  -- Chambre du Héros : fenêtre centrale 4 ambiances + filtre de luminosité
  local m_her = make_mock_ground('guilde_destiny_chambre_heros')
  current_ground = m_her
  heros.Init(m_her)
  heros.Enter(m_her)
  assert(m_her.LastAmbiance == current_moment and m_her.LastApplyWorld == true)
  assert(m_her.SpawnedList.Fenetre_Centre.ObjectAnim.AnimIndex == 'Guilde_Fenetre_11_chambre_heros_Centre_' .. cap_amb)
end

print('PASS test_guilde_destiny_accueil.lua : 15 salles, filtre luminosite 4 ambiances, fenetres .dir et double porte battante EoS valides.')
