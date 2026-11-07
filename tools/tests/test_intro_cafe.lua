-- Test du scénario café avec doublures (pas de rendu ou moteur PMDO).
package.preload['origin.common']=function()return {CreateWalkArea=function()end}end
local actors, events, fail_suivi, choice, map
local function log(t,n,v)events[#events+1]={t,n,v}end
local function new(n,x,y) local a={EntName=n,Position={X=x,Y=y},Direction=1,EntEnabled=true,Data={Nickname=n}};actors[n]=a;return a end
function CH(n)return actors[n]end
package.preload['destiny.suivi_interieurs']=function()return {Activer=function()
 log('suivi');if fail_suivi then error('simulation erreur suivi') end
 if not actors.Teammate1 then new('Teammate1',314,354) end
end}end
package.preload['destiny.equipe_scene']=function()return {Suivre=function(a,h) assert(a and h);log('reprendre_suivi')end}end
luanet={each=function(list)local i=0;return function()i=i+1;return list[i]end end}
Direction={Up=0,Down=1,Left=2,Right=3}
RogueEssence={Ground={GroundObject=function()return {OnMapInit=function()end,SetTriggerType=function()end}end,GroundEntity={EEntityTriggerTypes={Touch=0}}}}
RogueElements={Rect=function(x,y,w,h)return {x,y,w,h} end}
GROUND={
 RemoveObject=function()end,TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};a.Direction=d end,
 MoveToPosition=function(_,a,x,y,run,speed)a.Position={X=x,Y=y};log('marche',a.EntName,x..','..y)end,
 CharTurnToCharAnimated=function(_,a,b)assert(a and b)end,EntTurn=function(_,a,d)a.Direction=d end,
}
AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end}
TASK={BranchCoroutine=function(_,f)f();return 1 end,JoinCoroutines=function()end}
GAME={MoveCamera=function(_,x,y,t,follow)log('camera',x,y)end,FadeIn=function()log('fade_in')end,FadeOut=function()log('fade_out')end,WaitFrames=function()end,CutsceneMode=function(_,v)log('cutscene',nil,v)end,EnterZone=function(_,zone,seg,idx,entry)log('zone',zone,idx)end}
UI={SetSpeaker=function(_,a)assert(a);log('speaker',a.EntName)end,SetSpeakerEmotion=function()end,WaitShowDialogue=function(_,t)log('dialogue',nil,t)end,ResetSpeaker=function()end,BeginChoiceMenu=function(_,prompt,options)log('menu',prompt,#options)end,WaitForChoice=function()end,ChoiceResult=function()return choice end}
local cafe=assert(loadfile(arg[1]..'/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
local function reset(missing,bloc)
 actors={};events={};fail_suivi=false;choice=2;SV={Destiny={AlerteShinx='a_secourir'}}
 new('PLAYER',290,354);if missing~='Spinda' then new('Spinda',224,160)end;if missing~='Kirlia' then new('Kirlia',224,184)end
 local list={actors.Spinda,actors.Kirlia}; if bloc then list[#list+1]=new('bloc',256,200)end
 map={Entities={{Visible=true,MapChars=list,TemporaryChars={}}}}
end
local function find(t,sub)
 for i,v in ipairs(events)do if v[1]==t and (sub==nil or tostring(v[3] or ''):find(sub,1,true))then return i end end
 return nil
end
reset();cafe.Enter(map)
assert(SV.Destiny.VisiteCafeSpinda=='terminee')
assert(find('fade_in')<find('suivi') and find('suivi')<find('dialogue','Bienvenue'))
assert(find('marche','272,248') and actors.Spinda.Position.X==224 and actors.Spinda.Position.Y==160)
assert(find('dialogue','président de la Fédération') and find('dialogue','sacré personnage') and find('dialogue','rénovation') and find('dialogue','Nilo'))
assert(find('reprendre_suivi') and events[#events][1]=='cutscene' and events[#events][3]==false)
local n=#events;cafe.Enter(map);for i=n+1,#events do assert(not (events[i][1]=='dialogue' and tostring(events[i][3]):find('président',1,true)))end
print('PASS première entrée, introduction unique, suivi, actualité et retour Spinda')
reset('Kirlia');cafe.Enter(map);assert(not SV.Destiny.VisiteCafeSpinda and find('fade_in'));print('PASS employé absent : écran visible et scène différée')
reset(nil,true);cafe.Enter(map);assert(SV.Destiny.VisiteCafeSpinda=='terminee' and not find('marche','272,248'));print('PASS trajet Spinda occupé : dialogue sans forcer')
reset();fail_suivi=true;cafe.Enter(map);assert(find('fade_in') and not SV.Destiny.VisiteCafeSpinda);print('PASS suivi indisponible : fondu déjà effectué')
reset();SV.Destiny.RetourCafeAccueil='escalier';cafe.Enter(map);assert(not SV.Destiny.VisiteCafeSpinda and actors.PLAYER.Position.Y==152);print('PASS retour étage : pas de première visite artificielle')
reset();cafe.EscalierNordCafe_Touch(nil,actors.PLAYER);assert(find('dialogue','fermé pendant les travaux') and not find('zone'));print('PASS escalier fermé pendant rénovation')
reset();SV.Destiny.CafeRenovationTerminee=true;cafe.EscalierNordCafe_Touch(nil,actors.PLAYER);assert(find('zone') and events[#events][3]==3);print('PASS escalier préservé pour une réouverture future')
reset();cafe.Spinda_Action(actors.Spinda,actors.PLAYER);assert(find('menu') and not find('zone'));print('PASS accueil pendant rénovation, pas de téléportation vers salles fermées')
