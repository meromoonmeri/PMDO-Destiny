-- Tests comportementaux Lua pour Grotte Verdoyante (doublures d'API).
local root = assert(arg[1])

package.preload['origin.common'] = function() return {} end
package.preload['origin.menu.skill.SkillSelectMenu'] = function() return {} end
package.preload['origin.menu.team.AssemblySelectMenu'] = function() return {} end
package.preload['destiny.recrutement'] = function() return {synchroniser=function() end} end
package.preload['destiny.meteo_reverie'] = function()
  return {Appliquer=function() end, SynchroniserZone=function() end, Description=function() return 'Ciel clair.' end}
end
package.preload['destiny.suivi_interieurs'] = function() return {Lancer=function() end, Terminer=function() end} end
package.preload['destiny.equipe_scene'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/equipe_scene.lua'))() end
package.preload['destiny.cinematique'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/cinematique.lua'))() end
package.preload['destiny.missions_reverie'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/missions_reverie.lua'))() end

local events = {}
local function ev(k, ...) events[#events+1] = {k, ...} end

local tick_val = 480 * 2 -- démarrer volontairement hors phase 0 pour tester l'attente synchrone
DEBUG = {EnableDbgCoro=function() end}
Direction = {Up=4, Down=0, Left=2, Right=6, UpLeft=3, UpRight=5, DownLeft=1, DownRight=7}
Gender = {Male=1, Female=2, Genderless=0}
RogueElements = {Rect=function(x,y,w,h) return {X=x,Y=y,W=w,H=h} end}
RogueEssence = {
  Content = {
    GraphicsManager = {TotalFrameTick = tick_val},
    ScreenMover = function(dx, dy, dur) return {dx=dx,dy=dy,dur=dur} end,
  },
  Data = {
    GameProgress = {
      DungeonStakes = {Risk='Risk'},
      ResultType = {Cleared='Cleared', Downed='Downed', Failed='Failed'},
    },
  },
  Ground = {
    GroundObject = function()
      local o = {OnMapInit=function()end, SetTriggerType=function()end}
      return o
    end,
    GroundEntity = {EEntityTriggerTypes={Touch=2, Action=1}},
  },
  Dungeon = {
    BaseMap = {ScrollEdge={Clamp=1}},
    CharData = function() return {} end,
    MonsterID = function(sp, f, sk, g) return {Species=sp, Form=f, Skin=sk, Gender=g} end,
    Character = function(d) return {Data=d} end,
    InvItem = function(id, cursed, amt) return {ID=id, Cursed=cursed, Amount=amt, GetDisplayName=function() return id end} end,
  },
}

local actors = {}
local function make_actor(n, x, y, sp)
  local a = {EntName=n, Position={X=x or 0, Y=y or 0}, Direction=Direction.Down, EntEnabled=true, CollisionDisabled=false, Data={Nickname=n, BaseForm={Species=sp}}}
  function a:GetDisplayName() return self.EntName end
  function a:ReloadEvents() self.reloaded = true end
  actors[n] = a
  return a
end
function CH(n) return actors[n] end

GROUND = {
  CreateCharacterFromCharData = function(_, n, d, x, y, dir) local a = make_actor(n, x, y); a.Data = d.Data; a.Direction = dir; return a end,
  RemoveCharacter = function(_, n) actors[n] = nil; return true end,
  TeleportTo = function(_, a, x, y, dir) a.Position = {X=x, Y=y}; a.Direction = dir end,
  MoveToPosition = function(_, a, x, y) a.Position = {X=x, Y=y} end,
  EntTurn = function(_, a, dir) a.Direction = dir end,
  CharAnimateTurnTo = function(_, a, dir) a.Direction = dir end,
  CharTurnToCharAnimated = function() end,
  CharTurnToChar = function() end,
  CharSetAnim = function() end,
  CharEndAnim = function() end,
  CharSetEmote = function(_, a, em) ev('emote', a.EntName, em) end,
  MoveScreen = function(_, m) ev('shake', m.dy, m.dur) end,
  Hide = function(_, n) if actors[n] then actors[n].EntEnabled = false end end,
  Unhide = function(_, n) if actors[n] then actors[n].EntEnabled = true end end,
}
AI = {DisableCharacterAI=function()end, EnableCharacterAI=function()end, SetCharacterAI=function()end}
TASK = {BranchCoroutine=function(_, f) f(); return true end, JoinCoroutines=function() end}
SOUND = {PlayBGM=function(_, m) ev('bgm', m) end, FadeOutBGM=function() end, PlayBattleSE=function(_, s) ev('se', s) end}
local choice_ret = true
UI = {
  SetSpeaker=function() end, SetSpeakerLoc=function() end, SetSpeakerEmotion=function() end,
  ResetSpeaker=function() end, WaitShowDialogue=function(_, t) ev('dlg', t) end,
  WaitShowTitle=function() end, WaitHideTitle=function() end,
  BeginChoiceMenu=function() end,
  ChoiceMenuYesNo=function() end, WaitForChoice=function() end,
  ChoiceResult=function() return choice_ret end,
}
local unlocked = {}
GAME = {
  CutsceneMode=function() end,
  MoveCamera=function() end,
  FadeIn=function() end,
  FadeOut=function() end,
  WaitFrames=function(_, n)
    tick_val = tick_val + (n or 1) * 120
    RogueEssence.Content.GraphicsManager.TotalFrameTick = tick_val
    ev('wait', n)
  end,
  GetPlayerPartyCount=function() return 2 end,
  GetTeamLeaderIndex=function() return 0 end,
  GetPlayerPartyMember=function(_, i) return {Importance=i==0 and 'Hero' or 'Partner', Data={}} end,
  GetCurrentGround=function() return {Name={ToLocal=function() return 'Grotte Verdoyante' end}} end,
  DungeonUnlocked=function(_, id) return unlocked[id] == true end,
  UnlockDungeon=function(_, id) unlocked[id] = true; ev('unlock', id) end,
  SetRescueAllowed=function() end,
  EnterDungeon=function(_, ...) ev('enter_dungeon', ...) end,
  ContinueDungeon=function(_, ...) ev('continue_dungeon', ...) end,
  EndDungeonRun=function(_, ...) ev('end_run', ...) end,
  EnterZone=function(_, ...) ev('enter_zone', ...) end,
}
COMMON = {
  Rescued=function() end,
  BeginDungeon=function() end,
  ExitDungeonMissionCheck=function() return false end,
  BossTransition=function(p) ev('boss_transition', p) end,
  GiftItem=function(hero, item)
    assert(type(item) == 'table' and type(item.GetDisplayName) == 'function', 'InvItem attendu pour GiftItem')
    ev('gift', item.ID)
  end,
  EndDungeonDay=function(res, z, s, m, e) ev('end_day', res, z, s, m, e) end,
}
function LTBL(m) return {Importance=m.Importance} end

local function make_ewc3_map()
  local m = {AssetName='ewc3_entree_waterfall_cave', Layers={}, Objects={}}
  for i = 0, 20 do m.Layers[i] = {Visible=(i ~= 13 and i ~= 14 and i ~= 18)} end
  function m:FindObject(n) return self.Objects[n] end
  function m:AddObject(o) self.Objects[o.EntName] = o end
  return m
end

-- 1. ewc3 : 1re arrivée (fermée -> ouverture synchrone -> ouverte) puis 2e visite (déjà ouverte)
SV = {Destiny={AlerteShinx='a_secourir'}}
make_actor('PLAYER', 392, 544)
local ewc3 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/ewc3_entree_waterfall_cave/init.lua'))()
local m_ewc3 = make_ewc3_map()
ewc3.Init(m_ewc3)
assert(m_ewc3.Layers[12].Visible and m_ewc3.Layers[17].Visible and not m_ewc3.Layers[14].Visible)
assert(m_ewc3.Objects.SeuilDonjon and m_ewc3.Objects.SortieRetourReverie)
ewc3.Enter(m_ewc3)
assert(SV.Destiny.GrotteVerdoyanteOuverte == true)
assert(not m_ewc3.Layers[12].Visible and not m_ewc3.Layers[13].Visible and m_ewc3.Layers[14].Visible)
assert(actors.Luxray_Ewc3 and actors.Luxray_Ewc3.Position.X == 400 and actors.Luxray_Ewc3.Position.Y == 260 and actors.Luxray_Ewc3.reloaded == true)

-- SeuilDonjon et SortieRetourReverie
ewc3.SeuilDonjon_Touch(nil, actors.PLAYER)
assert(events[#events][1] == 'enter_dungeon' and events[#events][2] == 'grotte_verdoyante')
ewc3.Init(m_ewc3) -- reset sortie_en_cours et vérifie ouverture persistante
assert(m_ewc3.Layers[14].Visible and not m_ewc3.Layers[12].Visible)
ewc3.SortieRetourReverie_Touch(nil, actors.PLAYER)
assert(events[#events][1] == 'enter_zone' and events[#events][2] == 'town02_waterfallvillage' and SV.Destiny.ArriveeVille == 'batiment')

-- 2. zone/grotte_verdoyante : Seg 0 échec garde AlerteShinx ; Seg 0 succès -> fgv1 ; Seg 1 échec -> Phase=1 ; Seg 1 succès -> Phase=3
local zone = assert(loadfile(root .. '/game/Data/Script/destiny/zone/grotte_verdoyante/init.lua'))()
local zobj = {ID='grotte_verdoyante'}
SV.Destiny = {AlerteShinx='a_secourir', ExplorationReverie=true}
events = {}
zone.ExitSegment(zobj, 'Downed', false, 0, 0)
assert(SV.Destiny.AlerteShinx == 'a_secourir' and SV.Destiny.LuxrayAttente == 'sortie' and events[#events][1] == 'end_day')

zone.ExitSegment(zobj, 'Cleared', false, 0, 0)
assert(events[#events][1] == 'enter_zone' and events[#events][2] == 'grotte_verdoyante' and events[#events][4] == 1)

zone.ExitSegment(zobj, 'Failed', false, 1, 0)
assert(SV.Destiny.GrotteVerdoyantePhase == 1 and SV.Destiny.AlerteShinx == 'a_secourir')

zone.ExitSegment(zobj, 'Cleared', false, 1, 0)
assert(SV.Destiny.GrotteVerdoyantePhase == 3 and events[#events][1] == 'enter_zone' and events[#events][4] == 1)

-- 3. fgv1 : PreBattle -> PostBattle (récompense InvItem gummi_royal + AlerteShinx='termine') -> EmptyReturn
local fgv1 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/fgv1_fin_grotte_vasques/init.lua'))()
actors = {}; make_actor('PLAYER', 384, 560)
SV.Destiny = {AlerteShinx='a_secourir', JourneeVille=0}
events = {}
fgv1.Enter({AssetName='fgv1_fin_grotte_vasques'})
assert(SV.Destiny.GrotteVerdoyantePhase == 1)
assert(events[#events][1] == 'continue_dungeon' and events[#events][2] == 'grotte_verdoyante' and events[#events][3] == 1)

SV.Destiny.GrotteVerdoyantePhase = 3
events = {}
fgv1.Enter({AssetName='fgv1_fin_grotte_vasques'})
assert(SV.Destiny.AlerteShinx == 'termine' and SV.Destiny.GrotteVerdoyanteBossVaincu == true and SV.Destiny.GrotteVerdoyantePhase == 4)
assert(SV.Destiny.JourneeVille == 1 and unlocked.grotte_verdoyante == true)
local saw_gift = false
for _, e in ipairs(events) do if e[1] == 'gift' and e[2] == 'gummi_royal' then saw_gift = true end end
assert(saw_gift and events[#events][1] == 'end_day' and events[#events][2] == 'Cleared' and events[#events][3] == 'town02_waterfallvillage')

events = {}
fgv1.Enter({AssetName='fgv1_fin_grotte_vasques'})
assert(events[#events][1] == 'end_day' and not actors.Colhomard_Boss)

-- 4. Réverie post-sauvetage : Nilo_Shinx apparaît en reverie_residentiel à (721, 2412) + mission Grotte Verdoyante jour impair
local ville = assert(loadfile(root .. '/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
local res = {
  AssetName='reverie_residentiel', characters={}, objects={},
  GetMapChar=function(self, n) return self.characters[n] end,
  FindObject=function(self, n) return self.objects[n] end,
  AddObject=function(self, o) self.objects[o.EntName] = o end,
}
actors = {}; make_actor('PLAYER', 800, 1160); make_actor('Teammate1', 772, 1160)
res.characters.NewObject_9 = make_actor('NewObject_9', 733, 2391)
res.characters.NewObject_10 = make_actor('NewObject_10', 709, 2391)
SV.Destiny = {AlerteShinx='termine', GrotteVerdoyanteBossVaincu=true, RetourAccompli=true, JourneeVille=1, PlacementHabitantsReverie={reverie_residentiel=true}}
ville.Init(res)
assert(actors.Nilo_Shinx and actors.Nilo_Shinx.Position.X == 721 and actors.Nilo_Shinx.Position.Y == 2412 and actors.Nilo_Shinx.reloaded == true)
events = {}
ville.Nilo_Shinx_Action(actors.Nilo_Shinx, actors.PLAYER)
local saw_nilo_dlg = false
for _, e in ipairs(events) do if e[1] == 'dlg' and tostring(e[2]):find('Colhomard', 1, true) then saw_nilo_dlg = true end end
assert(saw_nilo_dlg)

local cafe = assert(loadfile(root .. '/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
actors = {}; make_actor('PLAYER', 200, 300); make_actor('Spinda', 200, 220); make_actor('Kirlia', 160, 220)
events = {}
choice_ret = 4
cafe.Kirlia_Action(actors.Kirlia, actors.PLAYER)
local saw_kirlia_termine = false
for _, e in ipairs(events) do if e[1] == 'dlg' and tostring(e[2]):find('Nilo est rentré', 1, true) then saw_kirlia_termine = true end end
assert(saw_kirlia_termine)

local missions = package.preload['destiny.missions_reverie']()
unlocked.lost_wood = true
assert(missions.ZoneOffre() == 'grotte_verdoyante' and missions.Accepter())
assert(missions.Actuelle().Zone == 'grotte_verdoyante')

print('PASS test_grotte_verdoyante.lua : cascade 24f synchrone, zone 9F, boss, sauvetage Nilo, ville et missions.')
