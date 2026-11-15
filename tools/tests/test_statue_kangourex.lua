-- Tests comportementaux de la statue Kangourex (doublures d'API moteur).
-- Reproduit la chaîne réelle : GroundMap.OnInit -> service (GroundMapInit)
-- -> GroundEntity.RunEvent (callback « CURMAPSCR.<nom>_Action »).
local root = assert(arg[1])

Class = assert(loadfile(root .. '/base/Data/Script/lib/middleclass.lua'))()

-- Compteurs globaux observés par les assertions
STORAGE_APPELS = 0
DIALOGUES = {}

package.preload['origin.common'] = function()
  local m = {}
  function m.ShowTeamStorageMenu() STORAGE_APPELS = STORAGE_APPELS + 1 end
  return m
end
package.preload['origin.services.baseservice'] = function()
  BaseService = Class('BaseService')
  function BaseService:initialize() end
  function BaseService:Update() end
  return BaseService
end
package.preload['destiny.equipe_scene'] = function()
  return {Partenaire=function() return nil end, Suivre=function() end}
end
package.preload['destiny.statue_kangourex'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/statue_kangourex.lua'))()
end
package.preload['destiny.cinematique'] = function()
  return {Dire=function(_, _, texte) DIALOGUES[#DIALOGUES + 1] = tostring(texte) end,
          Respirer=function() end, Emote=function() end,
          NomColore=function(nom) return nom end, NomEspece=function(_, repli) return repli end}
end

local services = {}
SCRIPT = {
  AddService = function(_, nom, inst) services[nom] = inst end,
  GetService = function(_, nom) return services[nom] end,
}
EngineServiceEvents = {GroundMapInit='GroundMapInit'}

DEBUG = {EnableDbgCoro=function() end}
Direction = {Up=4, Down=0, Left=2, Right=6, UpLeft=3, UpRight=5, DownLeft=1, DownRight=7}
Gender = {Male=1, Female=2, Genderless=0}
RogueElements = {Rect=function(x,y,w,h) return {X=x,Y=y,W=w,H=h} end,
                 Loc=function(x,y) return {X=x,Y=y} end}
local TRIG = {None=0, Action=1, Touch=2, TouchOnce=3}
local ENTS = {Invalid=-1, Object=0, Character=1, Marker=2}
RogueEssence = {
  Content = {
    GraphicsManager={TotalFrameTick=960},
    ScreenMover=function() return {} end,
    FlashEmitter=function() return {} end,
    BGAnimData=function(n) return {name=n} end,
    ObjAnimData=function(idx, fr) return {AnimIndex=idx, FrameTime=fr} end,
  },
  Data = {GameProgress={DungeonStakes={Risk='Risk'},
                        ResultType={Cleared='Cleared', Downed='Downed', Failed='Failed'}}},
  Ground = {
    GroundEntity = {EEntityTriggerTypes=TRIG, EEntTypes=ENTS},
    GroundObject = function()
      return {OnMapInit=function() end, SetTriggerType=function() end}
    end,
  },
  Dungeon = {BaseMap={ScrollEdge={Clamp=1}}, CharData=function() return {} end,
             MonsterID=function() return {} end, Character=function(d) return {Data=d} end},
}
function Color(r,g,b,a) return {r=r,g=g,b=b,a=a} end
DrawLayer = {Top='Top'}
function LTBL() return {} end

local function make_character(nom, x, y, dir)
  local c = {EntName=nom, Position={X=x,Y=y}, Direction=dir or Direction.Down, EntEnabled=true,
             CollisionDisabled=false, Data={}, ReloadEvents=function() end}
  function c:GetDisplayName() return self.EntName end
  return c
end
local characters = {PLAYER=make_character('PLAYER', 432, 252, Direction.Up),
                    Teammate1=make_character('Teammate1', 404, 252, Direction.Up)}
function CH(nom) return characters[nom] end

GROUND = {
  CreateCharacterFromCharData=function(_, n, _, x, y, dir)
    return make_character(n, x, y, dir)
  end,
  RemoveCharacter=function() end, TeleportTo=function() end, MoveToPosition=function() end,
  EntTurn=function() end, CharAnimateTurnTo=function() end, CharTurnToCharAnimated=function() end,
  CharTurnToChar=function() end, CharSetAnim=function() end, CharEndAnim=function() end,
  CharSetEmote=function() end, MoveScreen=function() end, PlayVFX=function() end,
}
AI = {DisableCharacterAI=function() end, EnableCharacterAI=function() end,
      SetCharacterAI=function() end}
TASK = {BranchCoroutine=function(_, f) f() return true end, JoinCoroutines=function() end}
SOUND = {PlayBGM=function() end, FadeOutBGM=function() end, PlayBattleSE=function() end,
         PlayFanfare=function() end}
UI = {
  SetSpeaker=function() end, SetSpeakerLoc=function() end, SetSpeakerEmotion=function() end,
  SetCenter=function() end, ResetSpeaker=function() end,
  WaitShowDialogue=function() end, WaitShowTitle=function() end, WaitHideTitle=function() end,
  BeginChoiceMenu=function() end, ChoiceMenuYesNo=function() end,
  WaitForChoice=function() end, ChoiceResult=function() return true end,
}
GAME = {
  CutsceneMode=function() end, MoveCamera=function() end, FadeIn=function() end,
  FadeOut=function() end, WaitFrames=function() end,
  GetPlayerPartyCount=function() return 2 end, GetTeamLeaderIndex=function() return 0 end,
  GetPlayerPartyMember=function(_, i) return {Importance=(i==0) and 'Hero' or 'Partner'} end,
  GetCurrentGround=function() return {Name={ToLocal=function() return 'Grotte' end}} end,
  GetCameraCenter=function() return {X=240,Y=180} end,
  DungeonUnlocked=function() return true end, UnlockDungeon=function() end,
  SetRescueAllowed=function() end, EnterDungeon=function() end, ContinueDungeon=function() end,
  EndDungeonRun=function() end, EnterZone=function() end,
}
COMMON = package.preload['origin.common']()
SV = {Destiny={AlerteShinx='a_secourir', GrotteVerdoyanteOuverte=true, StatueKangourexExpliquee=true}}

-- Faux GroundObject : même contrat que le moteur (GetTriggerType, ReloadEvents)
local function make_object(nom, anim, trigger, passable, collider)
  local o = {EntName=nom, ObjectAnim={AnimIndex=anim}, CurrentAnim={AnimIndex=''},
             Passable=passable, Direction=0, EntEnabled=true,
             Collider=collider or {X=0, Y=0, W=8, H=8}, _trigger=trigger, events={}}
  function o:GetTriggerType() return self._trigger end
  function o:SetTriggerType(t) self._trigger = t end
  function o:GetEntityType() return RogueEssence.Ground.GroundEntity.EEntTypes.Object end
  -- GroundEntity.ReloadEvents : cache le callback « CURMAPSCR.<nom>_<Evt> »
  function o:ReloadEvents()
    local chemin = 'CURMAPSCR.' .. self.EntName .. '_Action'
    local valeur = _G
    for morceau in chemin:gmatch('[^.]+') do valeur = valeur and valeur[morceau] end
    self.events.Action = valeur
    local chemin_touch = 'CURMAPSCR.' .. self.EntName .. '_Touch'
    valeur = _G
    for morceau in chemin_touch:gmatch('[^.]+') do valeur = valeur and valeur[morceau] end
    self.events.Touch = valeur
  end
  return o
end

-- Les listes .NET exposées à Lua sont indexées à partir de 0.
local function make_map(asset, objets)
  local liste = {Count=#objets}
  for i, o in ipairs(objets) do liste[i - 1] = o end
  local map = {AssetName=asset, Layers={}, Objects={}, Entities={Count=1, [0]={GroundObjects=liste}}}
  for i = 0, 20 do map.Layers[i] = {Visible=(i ~= 13 and i ~= 14 and i ~= 18)} end
  for _, o in ipairs(objets) do map.Objects[o.EntName] = o end
  function map:FindObject(n) return self.Objects[n] end
  function map:AddObject(o) self.Objects[o.EntName] = o end
  function map:GetObj(n) return self.Objects[n] end
  return map
end

local service = assert(loadfile(root .. '/game/Data/Script/destiny/services/statue_kangourex/init.lua'))()
local ewc3 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/ewc3_entree_waterfall_cave/init.lua'))()
CURMAPSCR = ewc3

-- 1. Carte ewc3 : statue posée par l'éditeur (Action, non passable), + seuils
local statue = make_object('Statue_Kangourex', 'Statue_Kangourex', TRIG.Action, false,
                           {X=428, Y=236, W=24, H=12})
local map = make_map('ewc3_entree_waterfall_cave', {statue})
ewc3.Init(map)
local svc = assert(SCRIPT:GetService('StatueKangourex'), 'service StatueKangourex non enregistré')
svc:OnGroundMapInit(map)
statue:ReloadEvents()
assert(type(statue.events.Action) == 'function', 'callback Action de la statue non raccordé')

-- 1a. Première interaction : explication puis un seul stockage
STORAGE_APPELS, DIALOGUES = 0, {}
SV.Destiny.StatueKangourexExpliquee = nil
statue.events.Action(statue, characters.PLAYER)
assert(#DIALOGUES > 0, 'explication d’arrivée attendue avant le stockage')
assert(SV.Destiny.StatueKangourexExpliquee == true, 'StatueKangourexExpliquee doit être posé')
assert(STORAGE_APPELS == 1, 'un seul stockage doit s’ouvrir, obtenu ' .. tostring(STORAGE_APPELS))

-- 1b. Interactions suivantes : stockage seul, sans dialogue, sans doublon
DIALOGUES = {}
statue.events.Action(statue, characters.PLAYER)
assert(#DIALOGUES == 0, 'l’explication ne doit pas se répéter')
assert(STORAGE_APPELS == 2, 'le stockage doit se rouvrir à chaque interaction, obtenu ' .. tostring(STORAGE_APPELS))

-- 1c. Trois interactions d'affilée = trois menus au maximum (pas de doublon)
statue.events.Action(statue, characters.PLAYER)
statue.events.Action(statue, characters.PLAYER)
assert(STORAGE_APPELS == 4, 'doublon d’ouverture détecté, obtenu ' .. tostring(STORAGE_APPELS))

-- 2. Carte sans callback : le service installe seul l'ouverture du stockage
CURMAPSCR = {}
local nue = make_object('Statue_Kangourex', 'Statue_Kangourex', TRIG.None, false,
                        {X=40, Y=40, W=24, H=12})
local map_nue = make_map('carte_sans_script', {nue})
svc:OnGroundMapInit(map_nue)
assert(nue:GetTriggerType() == TRIG.Action, 'le déclencheur « Aucun » doit devenir « Action »')
assert(type(CURMAPSCR['Statue_Kangourex_Action']) == 'function',
       'le service doit fournir Statue_Kangourex_Action')
nue:ReloadEvents()
STORAGE_APPELS = 0
nue.events.Action(nue, characters.PLAYER)
assert(STORAGE_APPELS == 1, 'statue sans script de carte : stockage attendu, obtenu ' .. tostring(STORAGE_APPELS))

-- 3. Objet quelconque : ni callback ajouté, ni stockage
CURMAPSCR = {}
local seuil = make_object('SeuilDonjon', '', TRIG.Touch, true, {X=368, Y=184, W=40, H=24})
svc:Installer(seuil, map_nue)
assert(CURMAPSCR['SeuilDonjon_Touch'] == nil, 'un objet non-statue ne doit pas être raccordé')
assert(seuil:GetTriggerType() == TRIG.Touch, 'le déclencheur d’un objet non-statue ne doit pas changer')

print('PASS test_statue_kangourex.lua : stockage Kangourex (dépôt, retrait, argent) raccordé sans doublon.')
