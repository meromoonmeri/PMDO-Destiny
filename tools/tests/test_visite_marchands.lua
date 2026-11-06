-- Tests simulés de la scène existante et des trois nouvelles réponses.
package.preload['origin.common']=function()return {}end
package.preload['origin.menu.skill.SkillSelectMenu']=function()return {}end
package.preload['origin.menu.team.AssemblySelectMenu']=function()return {}end
local acteurs,paroles,cameras={}, {}, {}
package.preload['destiny.equipe_scene']=function()return {Suivre=function()end}end
package.preload['destiny.missions_reverie']=function()return {}end
package.preload['destiny.cinematique']=function()return {
 NomEspece=function(_,n)return n end,
 Dire=function(a,e,t,p)paroles[#paroles+1]={a.EntName,t,p}end,
 RegarderGroupe=function()end,Respirer=function()end,TournerGroupe=function()end,
}end
Direction={Up=0,Down=1,Left=2,Right=3,UpLeft=4,UpRight=5,DownLeft=6};Gender={Male=0,Female=1,Genderless=2}
function CH(n)return acteurs[n]end
GROUND={TeleportTo=function(_,a,x,y)a.Position.X=x;a.Position.Y=y end,MoveToPosition=function()end,CharAnimateTurnTo=function()end,CharTurnToCharAnimated=function()end,CharSetEmote=function()end}
GAME={GetPlayerPartyCount=function()return 2 end,CutsceneMode=function()end,WaitFrames=function()end,FadeIn=function()end,MoveCamera=function(_,x,y,frames,relative)cameras[#cameras+1]={x,y,relative}end}
TASK={BranchCoroutine=function(_,fn)fn();return true end,JoinCoroutines=function()end}
SOUND={PlayBGM=function()end,PlayBattleSE=function()end};UI={ResetSpeaker=function()end};AI={DisableCharacterAI=function()end}
local script=(arg[1] or '.')..'/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'
local function run(absent)
 acteurs={};paroles={};cameras={};SV={Destiny={VisiteVille='en_route'}}
 for _,n in ipairs({'PLAYER','Teammate1','Kecleon','Kangourex','NewObject_4','NewObject_3','NewObject_24'}) do
  if n~=absent then acteurs[n]={EntName=n,Position={X=800,Y=1160}} end
 end
 local ville=assert(loadfile(script))();ville.Visite()
 assert(SV.Destiny.VisiteVille=='terminee' and not acteurs.PLAYER.CollisionDisabled)
 local count={};for _,d in ipairs(paroles)do count[d[1]]=(count[d[1]] or 0)+1 end
 for _,n in ipairs({'Kecleon','Kangourex','NewObject_4','NewObject_3','NewObject_24'})do assert((count[n] or 0)==(n==absent and 0 or 1),'réponse incorrecte : '..n)end
 assert((count.Teammate1 or 0)>=13,'dialogue du guide tronqué')
 local b=cameras[#cameras];assert(b[3]==true,'caméra non rendue au joueur')
 for _,p in ipairs(cameras)do assert(not (p[1]==530 and p[2]==2350) and not (p[1]==800 and p[2]==530) and not (p[1]==1425 and p[2]==320),'visite hors centre')end
 print('PASS visite et commerçants ; absent : '..tostring(absent))
end
run(nil);run('NewObject_4');run('NewObject_3');run('NewObject_24')
