-- Tests sans moteur des leçons neutres (aller + retour inverse) et de l'installation des statues.
-- Lancer depuis la racine du dépôt : lua5.4 tools/tests/test_lostwood_lecons_statue.lua
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
local battle_loaded = false
package.preload['destiny.event_battle'] = function() battle_loaded = true; return true end
package.preload['destiny.mapgen_lost_wood'] = function() return true end

SINGLE_CHAR_SCRIPT = {}
local leader, autre = {}, {}
local pending, pages, fanfares, resets = nil, {}, 0, 0

STRINGS = {
  LocalKeyString = function(_, idx) return '<Touche' .. tostring(idx) .. '>' end,
}
SOUND = {
  PlayFanfare = function(_, nom)
    assert(nom == 'Fanfare/Note')
    fanfares = fanfares + 1
  end,
}
GAME = {
  GetTeamLeaderIndex = function() return 0 end,
  GetPlayerPartyMember = function(_, i) if i == 0 then return leader end end,
  QueueLeaderEvent = function(_, f) assert(pending == nil); pending = f end,
  WaitFrames = function() end,
}
UI = {
  SetSpeaker = function() error('le tutoriel Halcyon doit rester neutre sans orateur') end,
  SetSpeakerEmotion = function() error('aucune émotion de portrait attendue') end,
  ResetSpeaker = function() resets = resets + 1 end,
  WaitShowDialogue = function(_, msg) pages[#pages + 1] = msg end,
}

SV = { Destiny = { LostWoodTrip = 'aller' } }
dofile('game/Data/Script/destiny/event.lua')
assert(battle_loaded, 'les événements de combat existants doivent rester chargés')

local lesson = SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson
local function apply(user, floor)
  lesson(nil, nil, { User = user }, { Etage = floor })
end

-- Aller (1F -> 7F) : uniquement pour le meneur, neutre (ResetSpeaker + Fanfare/Note), touches dynamiques.
apply(autre, 1); assert(pending == nil)
for etage = 1, 7 do
  pages = {}
  local fanfares_avant = fanfares
  apply(leader, etage); assert(pending); pending(); pending = nil
  assert(SV.Destiny.LostWoodLessonsSeen[tostring(etage)] and #pages == 2)
  assert(fanfares == fanfares_avant + 1 and resets >= 2)
  if etage == 1 then assert(pages[2]:find('<Touche2>', 1, true)) end
  -- Ne pas rejouer la même leçon deux fois sur le même trajet.
  apply(leader, etage); assert(pending == nil)
end
assert(SV.Destiny.LostWoodTutorialDone == true)

-- Retour inverse (7F -> 1F) : leçons complémentaires d'équipe + inversion des escaliers en stairs_back_up.
RogueElements = { Loc = function(x, y) return { X = x, Y = y } end }
RogueEssence = { Dungeon = { SegLoc = function(seg, id) return { Segment = seg, ID = id } end } }
PMDC = { Dungeon = { DestState = function(secloc, back) return { Dest = secloc, Back = back } end } }

local function creer_carte_test(id_escalier)
  local tuile_escalier = {
    Effect = {
      ID = id_escalier or 'stairs_go_down',
      states = {},
      TileStates = { Set = function(self_ts, st) self_ts.last = st end },
    },
  }
  return {
    Width = 2, Height = 2,
    escalier = tuile_escalier,
    GetTile = function(self, loc)
      if loc.X == 1 and loc.Y == 1 then return self.escalier end
      return { Effect = { ID = '' } }
    end,
  }
end

SV.Destiny.LostWoodTrip = 'retour'
for etage = 7, 1, -1 do
  local carte = creer_carte_test('stairs_go_down')
  _ZONE = { CurrentMap = carte }
  pages = {}
  apply(leader, etage); assert(pending); pending(); pending = nil
  assert(SV.Destiny.LostWoodLessonsSeen['retour_' .. tostring(etage)] and #pages == 2)
  assert(carte.escalier.Effect.ID == 'stairs_back_up')
  local st = carte.escalier.Effect.TileStates.last
  assert(st and st.Dest.Segment == 0 and st.Dest.ID == -1 and st.Back == true and st.PreserveMusic == true)
end
assert(SV.Destiny.LostWoodReturnTutorialDone == true)

-- Même quand la leçon du retour a déjà été vue (nouvelle tentative), l'escalier reste inversé !
local carte_reprise = creer_carte_test('stairs_go_down')
_ZONE = { CurrentMap = carte_reprise }
apply(leader, 7)
assert(pending == nil and carte_reprise.escalier.Effect.ID == 'stairs_back_up')
_ZONE = nil

-- Une interruption au milieu d'une leçon ne la marque pas comme terminée.
SV.Destiny = { LostWoodTrip = 'aller' }
local normal = UI.WaitShowDialogue
UI.WaitShowDialogue = function() error('interruption simulée') end
apply(leader, 1); assert(pending); assert(not pcall(pending)); pending = nil
assert(not SV.Destiny.LostWoodLessonsSeen['1'])
UI.WaitShowDialogue = normal
apply(leader, 1); assert(pending); pending(); pending = nil
assert(SV.Destiny.LostWoodLessonsSeen['1'])

-- Simule les collections .NET, la classe de service et les callbacks de carte.
package.loaded['origin.common'] = true
package.loaded['origin.services.baseservice'] = true
BaseService = { initialize = function() end }
function Class(_, base)
  local c = {}; c.__index = c; setmetatable(c, { __index = base })
  function c:new() local inst = setmetatable({}, self); inst:initialize(); return inst end
  return c
end
local triggers = { None = 0, Action = 1, Touch = 2, TouchOnce = 3 }
RogueEssence.Ground = { GroundEntity = { EEntityTriggerTypes = triggers,
                                         EEntTypes = { Object = 0, Character = 1 } } }
EngineServiceEvents = { GroundMapInit = 'GroundMapInit' }
local registered
SCRIPT = { AddService = function(_, name, inst) assert(name == 'StatueKangourex'); registered = inst end }
local stores = 0
COMMON = { ShowTeamStorageMenu = function() stores = stores + 1 end }
local function obj(name, animation, trigger)
  return {
    EntName = name, ObjectAnim = { AnimIndex = animation }, trigger = trigger, reloads = 0,
    GetTriggerType = function(self) return self.trigger end,
    SetTriggerType = function(self, t) self.trigger = t end,
    ReloadEvents = function(self) self.reloads = self.reloads + 1 end,
    GetEntityType = function() return 0 end,
  }
end
local a = obj('NewObject', 'Statue_Kangourex', triggers.None)
local b = obj('NewObject', 'Statue_Kangourex', triggers.None)
local normal_object = obj('Autre', 'Storage', triggers.None)
local nested = obj('arbre.espace.statue', 'Statue_Kangourex', triggers.None)
local broken = obj('', 'Statue_Kangourex', triggers.None)
local touch = obj('Toucher', 'Statue_Kangourex', triggers.TouchOnce)
local layer0 = { GroundObjects = { Count = 4, [0] = a, [1] = b, [2] = normal_object, [3] = nested } }
local layer1 = { GroundObjects = { Count = 2, [0] = broken, [1] = touch } }
local map = { Entities = { Count = 2, [0] = layer0, [1] = layer1 } }
function map:GetObj(name)
  for i = 0, self.Entities.Count - 1 do
    local list = self.Entities[i].GroundObjects
    for j = 0, list.Count - 1 do if list[j].EntName == name then return list[j] end end
  end
end
local old_calls = 0
CURMAPSCR = { NewObject_Action = function() old_calls = old_calls + 1 end,
              Toucher_Touch = function() old_calls = old_calls + 1 end }
local service = dofile('game/Data/Script/destiny/services/statue_kangourex/init.lua')
assert(registered == service)
local events = {}
local med = {
  Subscribe = function(_, svc, event, fn) assert(svc == 'StatueKangourex'); events[event] = fn end,
  UnSubscribe = function(_, svc, event) events[event] = nil end,
}
service:Subscribe(med)
events.GroundMapInit(service, { [0] = 'une_carte', [1] = map })
assert(a.trigger == triggers.Action and b.trigger == triggers.Action and nested.trigger == triggers.Action)
assert(touch.trigger == triggers.TouchOnce and normal_object.trigger == triggers.None)
assert(a.reloads == 1 and b.reloads == 1 and nested.reloads == 1 and broken.reloads == 1)
CURMAPSCR.NewObject_Action(a, leader); CURMAPSCR.NewObject_Action(b, leader)
assert(stores == 2 and old_calls == 2)
-- Un autre objet ou personnage partageant le nom conserve son ancien callback.
CURMAPSCR.NewObject_Action(normal_object, leader)
CURMAPSCR.NewObject_Action({ GetEntityType = function() return 1 end }, leader)
assert(stores == 2 and old_calls == 4)
CURMAPSCR.arbre.espace.statue_Action(nested, leader)
CURMAPSCR[broken.EntName .. '_Action'](broken, leader)
CURMAPSCR.Toucher_Touch(touch, leader)
assert(stores == 5 and old_calls == 5)
-- Réinitialiser une carte ne doit pas empiler les enveloppes.
events.GroundMapInit(service, { [0] = 'une_carte', [1] = map })
CURMAPSCR.NewObject_Action(a, leader); assert(stores == 6 and old_calls == 6)
-- Une carte sans aucun script est également prise en charge.
CURMAPSCR = nil
service:OnGroundMapInit(map)
assert(CURMAPSCR and CURMAPSCR.NewObject_Action)
CURMAPSCR.NewObject_Action(a, leader); assert(stores == 7)
service:UnSubscribe(med); assert(events.GroundMapInit == nil)
print('OK : leçons neutres aller (1..7) et retour inverse (7..1), escaliers inversés, statues et callbacks conservés.')
