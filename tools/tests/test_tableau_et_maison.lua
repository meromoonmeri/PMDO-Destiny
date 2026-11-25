local root=assert(arg[1]); package.path=root..'/game/Data/Script/?.lua;'..root..'/game/Data/Script/?/init.lua;'..package.path
package.preload['origin.common']=function()return {}end
local money,unlocked,events=0,false,{}
SV={Destiny={RetourAccompli=true}}
GAME={DungeonUnlocked=function()return unlocked end,UnlockDungeon=function()unlocked=true end,AddToPlayerMoneyBank=function(_,n)money=money+n end,GroundSave=function()events[#events+1]='save' end,FadeIn=function()end,FadeOut=function()end,EnterGroundMap=function(_,zone,map,marker)events[#events+1]={zone,map,marker}end,GetPlayerPartyCount=function()return 1 end}
RogueElements={Loc=function(x,y)return {X=x,Y=y}end}
local stack={}
_MENU={AddMenu=function(_,m)stack[#stack+1]=m end,RemoveMenu=function()assert(#stack>0);table.remove(stack)end}
_GAME={SE=function()end}
local function scriptmenu(label,x,y,w,h,cb)
 local elements={list={}};function elements:Add(v)self.list[#self.list+1]=v end;function elements:Clear()self.list={}end
 return {Elements=elements,Bounds={Width=w,Height=h},callback=cb,label=label}
end
RogueEssence={Menu={ScriptableMenu=scriptmenu,MenuText=function(text,loc)return{text=text,loc=loc}end,MenuDivider=function(loc,width)return{loc=loc,width=width}end},FrameInput={InputType={Confirm=1,Cancel=2,Menu=3}}}
STRINGS={Format=function(_,s)return s end}
UI={SetCustomMenu=function(_,m)_MENU:AddMenu(m)end,WaitForChoice=function()end,ResetSpeaker=function()end,ChoiceMenuYesNo=function()end,ChoiceResult=function()return true end,WaitShowDialogue=function()end}
local function press(n)local top=assert(stack[#stack]);top.callback({JustPressed=function(_,key)return key==n end})end
local missions=require('destiny.missions_reverie')
missions.EtudierTableau();assert(#stack==1);press(1);assert(#stack==2);press(1);assert(#stack==1 and missions.Actuelle().Etat=='en_cours');assert(not missions.Accepter());assert(not missions.Completer('lost_wood',false));assert(not missions.Completer('autre',true));assert(missions.Completer('lost_wood',true));assert(not missions.Completer('lost_wood',true));press(1);assert(#stack==2);press(1);assert(money==300 and missions.Actuelle()==nil and not missions.Reclamer());assert(not missions.OffreDisponible());press(2);assert(#stack==0)
SV.Destiny.JourneeVille=1;missions.EtudierTableau();press(1);press(1);assert(missions.Actuelle().Jour==1);press(2);assert(#stack==0)
print('PASS tableau : ancien état, acceptation unique, échec, réussite, récompense unique, jour suivant')
local ally={Partenaire=function()error('équipe solo')end,Suivre=function()end};package.loaded['destiny.equipe_scene']=ally
function CH()return nil end;Direction={Up=0};local maison=require('destiny.ground.maison_equipe_falaise.init');maison.Init({});maison.LitEquipe_Action({}, {EntName='PLAYER'});assert(events[#events]=='save');local before=#events;UI.ChoiceResult=function()return false end;maison.LitPartenaire_Action({}, {EntName='PLAYER'});assert(#events==before);maison.SortieMaison_Touch({}, {EntName='Teammate1'});assert(#events==before);maison.SortieMaison_Touch({}, {EntName='PLAYER'});assert(SV.Destiny.RetourMaisonEquipe and events[#events][1]=='destiny_cliff_tests' and events[#events][2]=='cliffdaytest' and events[#events][3]=='Pichu_Home_Door');maison.SortieMaison_Touch({}, {EntName='PLAYER'});assert(#events==before+1)
print('PASS maison : refus sauvegarde, sauvegarde confirmée, sortie unique et marqueur retour')
