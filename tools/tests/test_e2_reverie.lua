package.preload['destiny.meteo_reverie']=function()return assert(loadfile((arg[1] or '.')..'/game/Data/Script/destiny/meteo_reverie.lua'))()end
-- Tests de logique ciblés avec doubles d'API, pas un test en jeu.
package.preload['origin.common']=function() return {} end
package.preload['origin.menu.skill.SkillSelectMenu']=function() return {} end
package.preload['origin.menu.team.AssemblySelectMenu']=function() return {} end
package.preload['destiny.equipe_scene']=function() return {} end
package.preload['destiny.cinematique']=function() return {NomEspece=function(_,n) return n end} end
package.preload['destiny.recrutement']=function() return {synchroniser=function() end} end
local s={unlocked={lost_wood=false, grotte_verdoyante=false},menu=nil,choice=nil,confirm=false,calls={}}
SV={Destiny={}}
RogueEssence={Data={DataManager={DataType={Zone='Zone'}},GameProgress={DungeonStakes={Risk='Risk'},ResultType={Cleared='Cleared',Downed='Downed',Failed='Failed'}}},Dungeon={ZoneLoc=function(id,seg,map,entry) return {ID=id,seg=seg,map=map,entry=entry} end}}
local NAMES={lost_wood='Bois Perdus', grotte_verdoyante='Grotte Verdoyante'}
_DATA={DataIndices={Zone={Get=function(_,id) assert(NAMES[id]);return {GetColoredName=function() return NAMES[id] end} end}}}
STRINGS={Format=function(_,s) return s end}
UI={ResetSpeaker=function()end,WaitShowDialogue=function(_,t)s.dialogue=t end,DestinationMenu=function(_,d)s.menu=d end,WaitForChoice=function()end,ChoiceMenuYesNo=function()end,BeginChoiceMenu=function(_,p,opts)s.choice_opts=opts end,ChoiceResult=function() if not s.asked then s.asked=true;return s.choice else return s.confirm end end}
SOUND={FadeOutBGM=function()end}
GAME={
  DungeonUnlocked=function(_,id)assert(NAMES[id]);return s.unlocked[id]==true end,
  UnlockDungeon=function(_,id)assert(NAMES[id]);s.unlocked[id]=true end,
  FadeOut=function()end,
  EnterDungeon=function(_,...)s.enter={...}end,
  SetRescueAllowed=function()end,
  EndDungeonRun=function(_,...)s.ended={...}end,
  EnterZone=function(_,...)s.zone={...}end,
}
local root=(arg[1] or '.')..'/game/Data/Script/destiny/'
package.preload['destiny.missions_reverie']=function() return assert(loadfile(root..'missions_reverie.lua'))() end
local ville=assert(loadfile(root..'ground/WaterfallVillageCapital/init.lua'))()
ville.SortieExplorationE2_Touch(nil,{EntName='Teammate1'});assert(not s.dialogue and not s.menu)
ville.SortieExplorationE2_Touch(nil,{EntName='PLAYER'});assert(not s.unlocked.lost_wood and s.dialogue and not s.menu and not s.enter)
s.dialogue=nil;s.asked=false;SV.Destiny.RetourAccompli=true;SV.TakenBoard={{Zone='lost_wood',Taken=true}};s.choice=nil
ville.SortieExplorationE2_Touch();assert(s.unlocked.lost_wood and #s.menu==1 and string.find(s.menu[1].Name,'E10F',1,true) and not s.enter)
SV.TakenBoard=nil;SV.Destiny.MissionReverie={Zone='lost_wood',Etat='en_cours'};s.asked=false;s.choice=nil;ville.SortieExplorationE2_Touch();assert(string.find(s.menu[1].Name,'E10F',1,true))
s.asked=false;s.choice=1;s.confirm=true;SV.Destiny.DonjonHistoireCourant='lost_wood';ville.SortieExplorationE2_Touch();assert(string.find(s.menu[1].Name,'E111',1,true));assert(s.enter[1]=='lost_wood' and s.enter[2]==0 and s.enter[5]=='Risk' and s.enter[6]==true and s.enter[7]==false and SV.Destiny.ExplorationReverie==true)

-- Déblocage / entrée directe de Grotte Verdoyante pendant et après le sauvetage
SV.Destiny.ExplorationReverie=nil;SV.Destiny.AlerteShinx='a_secourir';SV.Destiny.DepartShinxAccepte=true
s.asked=false;s.choice=1;s.zone=nil
ville.SortieExplorationE2_Touch(nil,{EntName='PLAYER'})
assert(s.unlocked.grotte_verdoyante and SV.Destiny.ExplorationReverie==true)
assert(s.zone and s.zone[1]=='grotte_verdoyante' and s.zone[2]==-1 and s.zone[3]==0 and s.zone[4]==0)

SV.Destiny.AlerteShinx='termine';SV.Destiny.DepartShinxAccepte=nil;SV.Destiny.ExplorationReverie=nil
s.asked=false;s.choice=2;s.confirm=true;s.zone=nil;s.enter=nil
ville.SortieExplorationE2_Touch(nil,{EntName='PLAYER'})
assert(#s.menu==2 and s.menu[2].Id=='grotte_verdoyante')
assert(s.zone and s.zone[1]=='grotte_verdoyante' and s.zone[2]==-1 and s.zone[3]==0)

local zone=assert(loadfile(root..'zone/lost_wood/init.lua'))()
for _,result in ipairs({'Cleared','Downed','Failed'}) do
 SV.Destiny.ExplorationReverie=true;SV.Destiny.LostWoodTrip='termine';SV.Destiny.PartenaireParti=false;SV.Destiny.LostWoodEchecsAller=5;s.zone=nil;s.ended=nil
 zone.ExitSegment(nil,result,false,0,0)
 assert(SV.Destiny.ExplorationReverie==nil and SV.Destiny.LostWoodTrip=='termine' and SV.Destiny.PartenaireParti==false and SV.Destiny.LostWoodEchecsAller==5)
 assert(SV.Destiny.ArriveeVille=='batiment' and SV.Destiny.RetourBatimentX==1552 and SV.Destiny.RetourBatimentY==1600)
 assert(s.ended[1]==result and s.ended[2]=='town02_waterfallvillage' and s.zone[1]=='town02_waterfallvillage' and s.zone[3]==0)
end
SV.Destiny.ExplorationReverie=nil;SV.Destiny.LostWoodTrip='aller';s.zone=nil;zone.ExitSegment(nil,'Cleared',false,0,0);assert(SV.Destiny.LostWoodTrip=='rencontre' and SV.Destiny.PartenaireParti==true and s.zone[1]=='reverie')
SV.Destiny.ExplorationReverie=nil;SV.Destiny.LostWoodTrip='retour';s.zone=nil;zone.ExitSegment(nil,'Cleared',false,1,0);assert(SV.Destiny.LostWoodTrip=='termine' and SV.Destiny.RetourAccompli==true and s.zone[1]=='destiny_cliff_tests')
print('PASS E2 : déblocage, menu, annulation, indicateurs, Bois Perdus et Grotte Verdoyante (doubles d’API)')
