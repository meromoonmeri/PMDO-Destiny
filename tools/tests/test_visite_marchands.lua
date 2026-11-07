-- Test simulé de la scène : paroles, animation Idle et écartement.
package.preload['origin.common']=function()return {}end
package.preload['origin.menu.skill.SkillSelectMenu']=function()return {}end
package.preload['origin.menu.team.AssemblySelectMenu']=function()return {}end
local acteurs,paroles,cameras,mouvements={}, {}, {}, {}
local interrompre_dracaufeu=false
local passages_partenaire=0
package.preload['destiny.equipe_scene']=function()return {Suivre=function()end}end
package.preload['destiny.missions_reverie']=function()return {}end
package.preload['destiny.cinematique']=function()return {
 NomEspece=function(_,n)return n end,
 Dire=function(a,e,t,p)
  if a.EntName ~= 'Teammate1' and a.EntName ~= 'PLAYER' then assert(a.idle, 'PNJ sans Idle pendant la parole : '..a.EntName) end
  paroles[#paroles+1]={a.EntName,t,p}
 end,
 RegarderGroupe=function()end,Respirer=function()end,TournerGroupe=function()end,
}end
Direction={Up=0,Down=1,Left=2,Right=3,UpLeft=4,UpRight=5,DownLeft=6};Gender={Male=0,Female=1,Genderless=2}
function CH(n)return acteurs[n]end
GROUND={
 TeleportTo=function(_,a,x,y)a.Position.X=x;a.Position.Y=y end,
 MoveToPosition=function(_,a,x,y)
  mouvements[#mouvements+1]={a.EntName,x,y}
  if a.EntName=='NewObject_16' then
   for i=0,100 do
    local dx=a.Position.X+(x-a.Position.X)*i/100;local dy=a.Position.Y+(y-a.Position.Y)*i/100
    for _,nom in ipairs({'PLAYER','Teammate1'}) do
     local autre=acteurs[nom].Position
     assert(math.abs(dx-autre.X)>=48 or math.abs(dy-autre.Y)>=48,'Dracaufeu passe trop près de '..nom)
    end
   end
  end
  if a.EntName=='NewObject_16' and x==900 and interrompre_dracaufeu then return end
  if a.EntName=='Teammate1' and acteurs.NewObject_16 then
   local d=acteurs.NewObject_16.Position
   assert(d.X==900 and d.Y==1214,'Dracaufeu doit avoir quitté le passage avant que le partenaire avance')
   for i=0,100 do
    local px=a.Position.X+(x-a.Position.X)*i/100;local py=a.Position.Y+(y-a.Position.Y)*i/100
    assert(math.abs(px-d.X)>=48 or math.abs(py-d.Y)>=48,'trajet trop proche de Dracaufeu')
   end
   passages_partenaire=passages_partenaire+1
  end
  a.Position.X=x;a.Position.Y=y
 end,
 CharAnimateTurnTo=function()end,CharTurnToCharAnimated=function()end,CharSetEmote=function()end,
 CharSetAnim=function(_,a,anim,loop)assert(anim=='Idle' and loop);a.idle=true end,CharEndAnim=function(_,a)a.idle=false end
}
GAME={GetPlayerPartyCount=function()return 2 end,CutsceneMode=function()end,WaitFrames=function()end,FadeIn=function()end,MoveCamera=function(_,x,y,frames,relative)cameras[#cameras+1]={x,y,relative}end}
TASK={BranchCoroutine=function(_,fn)fn();return true end,JoinCoroutines=function()end}
SOUND={PlayBGM=function()end,PlayBattleSE=function()end};UI={ResetSpeaker=function()end};AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end};COMMON={CreateWalkArea=function()end}
local script=(arg[1] or '.')..'/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'
local function run(absent, interruption)
 acteurs={};paroles={};cameras={};mouvements={};interrompre_dracaufeu=interruption or false;passages_partenaire=0;SV={Destiny={VisiteVille='en_route'}}
 for _,n in ipairs({'PLAYER','Teammate1','Kecleon','Kangourex','NewObject_4','NewObject_3','NewObject_24','NewObject_16','NewObject_7','NewObject_8'}) do
  if n~=absent then acteurs[n]={EntName=n,Position={X=800,Y=1160}} end
 end
 if acteurs.NewObject_16 then acteurs.NewObject_16.Position={X=827,Y=1178} end
 local ville=assert(loadfile(script))();ville.Visite()
 assert(SV.Destiny.VisiteVille=='terminee' and not acteurs.PLAYER.CollisionDisabled)
 local dm=0;for _,v in ipairs(mouvements)do if v[1]=='NewObject_16' then dm=dm+1 end end
 if acteurs.NewObject_16 then
  assert(acteurs.NewObject_16.Position.X==900 and acteurs.NewObject_16.Position.Y==1214, 'Dracaufeu ne dégage pas')
  assert(dm==2 and passages_partenaire==1)
 else assert(dm==0) end
 local count={};for _,d in ipairs(paroles)do count[d[1]]=(count[d[1]] or 0)+1 end
 for _,n in ipairs({'Kecleon','Kangourex','NewObject_4','NewObject_3','NewObject_24'})do assert((count[n] or 0)==(n==absent and 0 or 1),'réponse incorrecte : '..n)end
 assert((count.NewObject_16 or 0)==(absent=='NewObject_16' and 0 or 1) and (count.NewObject_7 or 0)==2 and (count.NewObject_8 or 0)==1, 'accueil manquant')
 assert((count.Teammate1 or 0)>=13,'dialogue du guide tronqué')
 for _,a in pairs(acteurs) do assert(not a.idle, 'Idle non rendu après la visite : '..a.EntName) end
 local trouve=false;for _,d in ipairs(paroles) do if d[2]:find('escalier nord',1,true) and d[2]:find('plus tard dans la journée',1,true) then trouve=true end end;assert(trouve,'information guilde manquante')
 local b=cameras[#cameras];assert(b[3]==true,'caméra non rendue au joueur')
 for _,p in ipairs(cameras)do assert(not (p[1]==530 and p[2]==2350) and not (p[1]==800 and p[2]==530) and not (p[1]==1425 and p[2]==320),'visite hors centre')end
 print('PASS visite et écartement ; absent : '..tostring(absent)..' ; mouvement interrompu : '..tostring(interruption))
end
run(nil);run('NewObject_4');run('NewObject_3');run('NewObject_24');run('NewObject_16');run(nil,true)
