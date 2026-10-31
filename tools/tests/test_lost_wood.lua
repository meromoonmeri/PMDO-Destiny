-- Tests des transitions sans ressources moteur : identité, réserve et caméra.
-- Usage depuis la racine du dépôt : lua tools/tests/test_lost_wood.lua
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
package.preload['origin.common'] = function() return {} end
local function noop() end
local hero = { name='HERO', IsFounder=true, data={ Importance='Hero' }, held='baie', exp=123 }
local partner = { name='PARTNER', IsFounder=true, data={ Importance='Partner' }, exp=234 }
local recruit = { name='RECRUE', IsFounder=false, data={} }
local other = { name='AUTRE', IsFounder=false, data={} }
local party, assembly, leader, actors, events = {}, {}, 0, {}, {}
local choice = false
Direction = { Down=4, Up=0, Left=6, Right=2 }
RogueEssence = { Data = { GameProgress = { ResultType={Cleared=2,Downed=0,Failed=1,GaveUp=5,Escaped=3}, DungeonStakes={Risk=2} } } }
SV = {Destiny={}}
LTBL = function(ch) return ch and ch.data end
CH = function(n) return actors[n] end
MRKR = function(n)
 if n=='Dazzling_Exit_East' then return {Position={X=960,Y=460}} end
 return {Position={X=666,Y=516}}
end
local function actor(ch,x,y) return {Data=ch,Position={X=x or 0,Y=y or 0}} end
GAME = {
 GetPlayerPartyCount=function() return #party end,
 GetPlayerPartyMember=function(_,i) assert(party[i+1]);return party[i+1] end,
 GetPlayerAssemblyCount=function() return #assembly end,
 GetPlayerAssemblyMember=function(_,i) assert(assembly[i+1]);return assembly[i+1] end,
 GetTeamLeaderIndex=function() return leader end,
 SetTeamLeaderIndex=function(_,i) leader=i;actors.PLAYER=actor(party[i+1]) end,
 AddPlayerTeam=function(_,ch) table.insert(party,ch) end,
 RemovePlayerAssembly=function(_,i) table.remove(assembly,i+1) end,
 AddPlayerAssembly=function(_,ch) table.insert(assembly,1,ch) end,
 SetRescueAllowed=noop,
 EndDungeonRun=function(_,r,z,segment,map,entry,display,fanfare) table.insert(events,{'end',r,z,map}) end,
 EnterZone=function(_,z,seg,map,entry) table.insert(events,{'enter',z,map}) end,
 EnterDungeon=function(_,z,...) table.insert(events,{'dungeon',z}) end,
 MoveCamera=function(_,x,y,duration,to_player) table.insert(events,{'camera',x,y,to_player}) end,
 CutsceneMode=function(_,v) table.insert(events,{'cutscene',v}) end,
 FadeOut=noop,FadeIn=noop,WaitFrames=noop,
}
GROUND = {
 RemoveCharacter=function(_,n) actors[n]=nil end,
 CreateCharacterFromCharData=function(_,n,ch,x,y,dir) actors[n]=actor(ch,x,y);return actors[n] end,
 TeleportTo=function(_,ch,x,y,dir) assert(ch);ch.Position={X=x,Y=y} end,
 CharSetAnim=noop,CharEndAnim=noop,Hide=noop,CharAnimateTurnTo=noop,CharSetEmote=noop,
}
AI = { DisableCharacterAI=noop,EnableCharacterAI=noop,SetCharacterAI=function(_,ch,path) assert(ch);ch.ai=path end }
UI = { ResetSpeaker=noop,SetSpeaker=function(_,a) assert(a) end,SetSpeakerEmotion=noop,WaitShowDialogue=noop,ChoiceMenuYesNo=noop,WaitForChoice=noop,ChoiceResult=function() return choice end }
SOUND = {FadeOutBGM=noop,PlayBGM=noop,PlayBattleSE=noop}
local equipe = require 'destiny.equipe_scene'
local zone = require 'destiny.zone.lost_wood.init'
local cliff = require 'destiny.ground.cliffdaytest_nuit.init'
local function setup_solo()
 party={partner};assembly={hero,other};leader=0;actors={PLAYER=actor(partner)};events={}
 SV={Destiny={LostWoodTrip='aller',PartenaireParti=true,HeroAssemblyIndex=0}}
end
local R=RogueEssence.Data.GameProgress.ResultType
-- Départ initial : la réserve était déjà non vide, l'indice correct est 0,
-- et le transfert direct conserve l'objet tenu et l'instance du héros.
party={hero,partner};assembly={other};leader=0;actors={PLAYER=actor(hero)};events={}
SV={Destiny={LostWoodTutorialDone=true}}
_DATA={Save={ActiveTeam={Players={RemoveAt=function(_,i) table.remove(party,i+1) end}}}}
local spawn_data
GROUND.SpawnerSetSpawn=function(_,name,ch) spawn_data=ch end
GROUND.SpawnerDoSpawn=function(_,name) return actor(spawn_data) end
cliff.ScenePartenaire()
assert(#party==1 and party[1]==partner and leader==0 and assembly[1]==hero and assembly[2]==other)
assert(SV.Destiny.HeroAssemblyIndex==0 and hero.held=='baie' and hero.exp==123)
-- Un KO et les deux formes d'abandon ne rendent jamais le héros visible.
for _,case in ipairs({{R.Downed,'ko'},{R.Failed,'ko'},{R.GaveUp,'abandon'},{R.Escaped,'abandon'}}) do
 setup_solo();zone.ExitSegment(nil,case[1],false,0,0)
 assert(#party==1 and party[1]==partner and assembly[1]==hero)
 assert(SV.Destiny.LostWoodTrip=='echec_aller' and SV.Destiny.LostWoodCause==case[2])
 assert(events[#events][1]=='enter' and events[#events][2]=='destiny_cliff_tests' and events[#events][3]==4)
 choice=false;cliff.SceneEchecPartenaire()
 assert(actors.PLAYER.Data==partner and actors.Teammate1==nil and assembly[1]==hero)
 assert(actors.PLAYER.Position.X==920 and actors.PLAYER.Position.Y==460)
 assert(SV.Destiny.LostWoodTrip=='pause_aller')
 local camera=events[#events-1];assert(camera[1]=='camera' and camera[2]==0 and camera[3]==0 and camera[4]==true)
 actors.PLAYER.Position.X=945;cliff.Update()
 assert(SV.Destiny.LostWoodTrip=='aller' and events[#events][1]=='dungeon')
end
-- Sur le succès, le héros demeure en réserve pendant EndDungeonRun ; il est
-- réuni uniquement à l'arrivée sur le panorama, même avec une recrue insérée.
setup_solo();zone.ExitSegment(nil,R.Cleared,false,0,0)
assert(#party==1 and assembly[1]==hero and SV.Destiny.LostWoodTrip=='rencontre')
assert(events[#events][2]=='personality_test' and events[#events][3]==2)
table.insert(assembly,1,recruit)
assert(equipe.RestaurerHeros() and #party==2 and party[2]==hero and assembly[1]==recruit and assembly[2]==other)
assert(leader==1 and hero.held=='baie' and hero.exp==123 and partner.exp==234)
assert(equipe.RestaurerHeros() and #party==2) -- idempotent au rechargement
local spawn=equipe.Partenaire(666,516,Direction.Up);assert(spawn and spawn.Data==partner)
events={};SV.Destiny.RetourAccompli=true;cliff.SceneRetour()
assert(SV.Destiny.FinaleDestiny and actors.Teammate1.Data==partner and actors.Teammate1.ai=='origin.ai.ground_partner')
local follow=events[#events-1];assert(follow[1]=='camera' and follow[2]==0 and follow[3]==0 and follow[4])
-- Retour duo : échec et succès conservent les mêmes objets Character.
for _,case in ipairs({{R.Failed,false},{R.GaveUp,false},{R.Cleared,true}}) do
 party={partner,hero};assembly={other};leader=1;events={};SV={Destiny={LostWoodTrip='retour'}}
 zone.ExitSegment(nil,case[1],false,0,0)
 assert(party[1]==partner and party[2]==hero and hero.held=='baie')
 assert(events[#events][2]==(case[2] and 'destiny_cliff_tests' or 'personality_test'))
 assert((SV.Destiny.RetourAccompli or false)==case[2])
end
-- Ne pas sélectionner un mauvais héros si plusieurs fondateurs sont ambigus.
party={partner};assembly={{IsFounder=true,data={}},{IsFounder=true,data={}}};leader=0;SV={Destiny={}}
assert(not equipe.RestaurerHeros() and #party==1 and #assembly==2)
print('Lost Wood : scénarios KO/abandon, pause et reprise, succès solo, rechargement, échec/succès duo, identité et caméra OK.')
