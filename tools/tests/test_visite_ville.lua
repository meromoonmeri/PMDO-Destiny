-- Tests simulés de la visite, de sa reprise et des services introduits.
-- Lancer depuis la racine : lua5.4 tools/tests/test_visite_ville.lua
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
package.loaded['origin.common'] = true
local actors, camera, dialogues, choices = {}, {}, {}, {}
local function actor(name, x, y)
  local a = { Nickname = name, Position = { X=x, Y=y }, CollisionDisabled=false, reloads=0 }
  function a:ReloadEvents() self.reloads=self.reloads+1 end
  actors[name]=a
  return a
end
local hero = actor('PLAYER', 0, 0)
local partner = actor('Teammate1', 24, 0)
local follow_count = 0
package.loaded['destiny.equipe_scene'] = {
  Partenaire = function() return partner end,
  Suivre = function(p, h) assert(p==partner and h==hero); follow_count=follow_count+1 end,
}
function CH(name) return actors[name] end
Direction = { Up=1, Down=0, Left=2, Right=3 }
Gender = { Male=1, Female=2 }
RogueEssence = { Dungeon = {
  BaseMap = { ScrollEdge = { Clamp=1 } },
  CharData = function() return {} end,
  MonsterID = function(species) return species end,
  Character = function(data) return data end,
} }
AI = { DisableCharacterAI=function() end }
GROUND = {
  CreateCharacterFromCharData=function(_, name, _, x, y) return actor(name,x,y) end,
  TeleportTo=function(_, a, x, y) a.Position.X=x; a.Position.Y=y end,
  MoveToPosition=function(_, a, x, y) a.Position.X=x; a.Position.Y=y end,
  CharAnimateTurnTo=function() end,
  CharSetEmote=function() end,
}
local money, bag, baglimit, item = 500, 0, 20, nil
GAME = {
  GetPlayerPartyCount=function() return 2 end,
  CutsceneMode=function() end,
  WaitFrames=function() end,
  FadeIn=function() end,
  MoveCamera=function(_, x, y, frames, relative) camera[#camera+1]={x,y,relative} end,
  GetPlayerMoney=function() return money end,
  GetPlayerBagCount=function() return bag end,
  GetPlayerBagLimit=function() return baglimit end,
  GivePlayerItem=function(_, id) item=id; bag=bag+1 end,
  RemoveFromPlayerMoney=function(_, n) money=money-n end,
}
TASK = {
  BranchCoroutine=function(_, f) f(); return true end,
  JoinCoroutines=function() end,
}
SOUND = { PlayBGM=function(_, name) assert(name=='Treasure Town.ogg' or name=='Base Town.ogg') end, PlayBattleSE=function() end }
UI = {
  SetSpeaker=function() end, SetSpeakerEmotion=function() end, ResetSpeaker=function() end,
  WaitShowDialogue=function(_, text) dialogues[#dialogues+1]=text end,
  BeginChoiceMenu=function() end, ChoiceMenuYesNo=function() end, WaitForChoice=function() end,
  ChoiceResult=function() assert(#choices>0); return table.remove(choices,1) end,
}
local stored=0
COMMON = { ShowTeamStorageMenu=function() stored=stored+1 end }
SV = { Destiny = { VisiteVille='en_route' } }
local ville=dofile('game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua')
local map={ EdgeView=0 }
ville.Init(map); assert(map.EdgeView==1 and CH('Kecleon') and CH('Kangourex'))
ville.Enter(map)
assert(SV.Destiny.VisiteVille=='terminee' and not hero.CollisionDisabled)
assert(follow_count==1 and #dialogues>=13)
local landmarks = { ['616,925']=true, ['936,940']=true }
for _, point in ipairs(camera) do landmarks[point[1]..','..point[2]]=nil end
assert(next(landmarks)==nil, 'tous les lieux doivent être cadrés')
local last=camera[#camera]; assert(last[3]==true, 'la caméra doit suivre de nouveau le joueur')
local old_dialogues=#dialogues
ville.GameLoad(map); assert(#dialogues==old_dialogues and follow_count==2)
ville.Init(map); assert(CH('Kecleon').reloads==2 and CH('Kangourex').reloads==2)
ville.Kangourex_Action(CH('Kangourex'),hero); assert(stored==1)
choices={1,true,4}; ville.Kecleon_Action(CH('Kecleon'),hero)
assert(money==450 and bag==1 and item=='food_apple')
money=0; item=nil; choices={2,4}; ville.Kecleon_Action(CH('Kecleon'),hero)
assert(money==0 and bag==1 and item==nil)
money=500; baglimit=1; choices={3,4}; ville.Kecleon_Action(CH('Kecleon'),hero)
assert(money==500 and bag==1 and item==nil)
-- Sans partenaire la visite reste en attente et ne modifie pas le drapeau.
actors.Teammate1=nil; GAME.GetPlayerPartyCount=function() return 1 end
SV.Destiny.VisiteVille='en_route'; ville.Enter(map); assert(SV.Destiny.VisiteVille=='en_route')
print('OK : visite en ville, déplacements de caméra, reprise, dépôt et achat.')
