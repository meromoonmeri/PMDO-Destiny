package.preload['destiny.meteo_reverie']=function()return assert(loadfile(arg[1]..'/game/Data/Script/destiny/meteo_reverie.lua'))()end
-- Test du scénario café avec doublures (pas de rendu ou moteur PMDO).
local walk_calls = 0
package.preload['origin.common']=function()return {CreateWalkArea=function() walk_calls = walk_calls + 1 end}end
local actors, events, fail_suivi, choice, map
local function log(t,n,v)events[#events+1]={t,n,v}end
local function new(n,x,y) local a={EntName=n,Position={X=x,Y=y},Direction=1,EntEnabled=true,Data={Nickname=n}};actors[n]=a;return a end
function CH(n)return actors[n]end
package.preload['destiny.suivi_interieurs']=function()return {Activer=function()
 log('suivi');if fail_suivi then error('simulation erreur suivi') end
 if not actors.Teammate1 then new('Teammate1',314,354) end
end}end
package.preload['destiny.equipe_scene']=function()return {Suivre=function(a,h) assert(a and h);log('reprendre_suivi')end}end
package.preload['destiny.cinematique']=function()return {RegarderGroupe=function(actions)
 for i,a in ipairs(actions) do assert(a[1] and a[2] and a[1]~=a[2] and a[1].EntEnabled~=false and a[2].EntEnabled~=false and a[3]==(i-1)*4 and a[4]==4);log('regard',a[1].EntName,a[2].EntName) end
end}end
luanet={each=function(list)local i=0;return function()i=i+1;return list[i]end end}
Direction={Up=0,Down=1,Left=2,Right=3}
RogueEssence={Ground={GroundObject=function()return {OnMapInit=function()end,SetTriggerType=function()end}end,GroundEntity={EEntityTriggerTypes={Touch=0}}}}
RogueElements={Rect=function(x,y,w,h)return {x,y,w,h} end}
GROUND={
 RemoveObject=function()end,TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};a.Direction=d end,
 MoveToPosition=function(_,a,x,y,run,speed)a.Position={X=x,Y=y};log('marche',a.EntName,x..','..y)end,
 CharTurnToCharAnimated=function(_,a,b)assert(a and b);log('tourne',a.EntName,b.EntName)end,CharSetEmote=function(_,a,e)assert(a);log('emote',a.EntName,e)end,CharSetAnim=function(_,a,anim,loop)assert(anim=='Idle' and loop);a.idle=true;log('idle_debut',a.EntName)end,CharEndAnim=function(_,a)a.idle=false;log('idle_fin',a.EntName)end,EntTurn=function(_,a,d)a.Direction=d;log('restaure',a.EntName,d)end,CharAnimateTurnTo=function(_,a,d)a.Direction=d end,
}
AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end}
TASK={BranchCoroutine=function(_,f)f();return 1 end,JoinCoroutines=function()end}
GAME={MoveCamera=function(_,x,y,t,follow)log('camera',x,y)end,FadeIn=function()log('fade_in')end,FadeOut=function()log('fade_out')end,WaitFrames=function()end,CutsceneMode=function(_,v)log('cutscene',nil,v)end,EnterZone=function(_,zone,seg,idx,entry)log('zone',zone,idx)end}
UI={SetSpeaker=function(_,a)assert(a);log('speaker',a.EntName)end,SetSpeakerEmotion=function()end,WaitShowDialogue=function(_,t)log('dialogue',nil,t)end,ResetSpeaker=function()log('reset_speaker')end,BeginChoiceMenu=function(_,prompt,options)log('menu',prompt,#options)end,WaitForChoice=function()end,ChoiceResult=function()return choice end}
local cafe=assert(loadfile(arg[1]..'/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
local function reset(missing,bloc)
 actors={};events={};fail_suivi=false;choice=2;SV={Destiny={AlerteShinx='a_secourir'}}
 new('PLAYER',290,354);if missing~='Spinda' then new('Spinda',224,160)end;if missing~='Kirlia' then new('Kirlia',200,164)end
 if missing~='Pipo' then new('MrMimeJunior',352,160) end
 local list={};for _,n in ipairs({'Spinda','Kirlia','MrMimeJunior'}) do if actors[n] then list[#list+1]=actors[n] end end
 local client=new('Client_Cafe',350,230);list[#list+1]=client
 local cache=new('Client_Cache',340,230);cache.EntEnabled=false;list[#list+1]=cache
 if bloc then list[#list+1]=new('bloc',256,200)end
 map={Entities={{Visible=true,MapChars=list,TemporaryChars={}}}}
end
local function find(t,sub)
 for i,v in ipairs(events)do if v[1]==t and (sub==nil or tostring(v[3] or ''):find(sub,1,true))then return i end end
 return nil
end
reset();cafe.Enter(map)
assert(SV.Destiny.VisiteCafeSpinda=='terminee')
assert(find('fade_in')<find('suivi') and find('suivi')<find('dialogue','Bienvenue'))
assert(find('marche','272,248') and actors.Spinda.Position.X==224 and actors.Spinda.Position.Y==160 and find('fade_out'))
assert(find('dialogue','président de la Fédération') and find('dialogue','sacré personnage') and find('dialogue','rénovation') and find('dialogue','Nilo'))
assert(find('reprendre_suivi') and events[#events][1]=='cutscene' and events[#events][3]==false)
local function regard(a,c) for _,v in ipairs(events) do if v[1]=='regard' and v[2]==a and v[3]==c then return true end end return false end
assert(regard('MrMimeJunior','Spinda') and regard('MrMimeJunior','Kirlia') and regard('Spinda','Kirlia'))
assert(find('emote','question') and find('emote','exclaim'))
local idle,fin,cache,restaure=false,false,false,false;for _,v in ipairs(events)do if v[1]=='idle_debut' and v[2]=='Client_Cafe' then idle=true end;if v[1]=='idle_fin' and v[2]=='Client_Cafe' then fin=true end;if v[1]=='idle_debut' and v[2]=='Client_Cache' then cache=true end;if v[1]=='restaure' and v[2]=='MrMimeJunior' and v[3]==1 then restaure=true end end
assert(idle and fin and not actors.Client_Cafe.idle and not cache and restaure,'animation ou retour du personnel incorrect')
local n=#events;cafe.Enter(map);for i=n+1,#events do assert(not (events[i][1]=='dialogue' and tostring(events[i][3]):find('président',1,true)))end
print('PASS première entrée, introduction unique, suivi, actualité et retour Spinda')
reset('Kirlia');cafe.Enter(map);assert(not SV.Destiny.VisiteCafeSpinda and find('fade_in'));print('PASS employé absent : écran visible et scène différée')
reset(nil,true);cafe.Enter(map);assert(SV.Destiny.VisiteCafeSpinda=='terminee' and not find('marche','272,248'));print('PASS trajet Spinda occupé : dialogue sans forcer')
reset();fail_suivi=true;cafe.Enter(map);assert(find('fade_in') and not SV.Destiny.VisiteCafeSpinda);print('PASS suivi indisponible : fondu déjà effectué')
reset();SV.Destiny.RetourCafeAccueil='escalier';cafe.Enter(map);assert(not SV.Destiny.VisiteCafeSpinda and actors.PLAYER.Position.Y==152);print('PASS retour étage : pas de première visite artificielle')
reset();cafe.EscalierNordCafe_Touch(nil,actors.PLAYER);assert(find('dialogue','fermé pendant les travaux') and not find('zone'));print('PASS escalier fermé pendant rénovation')
reset();SV.Destiny.CafeRenovationTerminee=true;cafe.EscalierNordCafe_Touch(nil,actors.PLAYER);assert(find('zone') and events[#events][3]==3);print('PASS escalier préservé pour une réouverture future')
reset();cafe.Spinda_Action(actors.Spinda,actors.PLAYER);assert(find('menu') and not find('zone'));print('PASS accueil pendant rénovation, pas de téléportation vers salles fermées')

reset('Pipo');cafe.Enter(map);assert(SV.Destiny.VisiteCafeSpinda=='terminee' and find('reprendre_suivi'));print('PASS Pipo absent : scène et suivi conservés')

-- La sieste avance le même compteur que les étals et annonce la météo sans portrait.
reset();choice=1;local avant=SV.Destiny.JourneeVille or 0;cafe.Spinda_Action(actors.Spinda,actors.PLAYER)
assert(SV.Destiny.JourneeVille==avant+1 and SV.Destiny.MeteoReverie.jour==avant+1)
assert(find('dialogue','Une nouvelle journée commence') and find('reset_speaker'))
assert(not find('statut_meteo'));print('PASS sieste : nouveau jour et annonce sans effet intérieur')

-- Placement côte à côte de Kirlia et Spinda, clients attablés fixes, pas de CreateWalkArea.
reset();walk_calls=0;new('Okéoké',381,227);new('Qulbutoqué',453,227);new('NewObject_13',187,205);new('Pompot',125,244)
cafe.Init(map)
assert(walk_calls==0 and actors.Kirlia.Position.X==200 and actors.Spinda.Position.X==224)
assert(actors['Okéoké'].Direction==Direction.Right and actors['Qulbutoqué'].Direction==Direction.Left)
-- Menu interactif enrichi de Kirlia (choix 2 puis 4 pour quitter).
local seq={2,4}; local idx=0; UI.ChoiceResult=function() idx=idx+1; return seq[idx] or 4 end
events={}; cafe.Kirlia_Action(actors.Kirlia,actors.PLAYER)
assert(find('dialogue','Spinda a beau tournoyer') and find('dialogue','Prenez soin de vous'))
-- Balancement non bloquant de Spinda en Update.
SV.Destiny.VisiteCafeSpinda='terminee'; for _=1,128 do cafe.Update(map, nil) end
assert(actors.Spinda.Direction==Direction.Right)
print('PASS Kirlia côte à côte, clients fixes, dialogue Kirlia et balancement Spinda')
