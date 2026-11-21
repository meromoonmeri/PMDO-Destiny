-- Banc pur Lua : vérifie les instants et les arguments du script réellement livré.
local mod=require('destiny.dojo_kingambit_troupes')
local clock,fx,acts,son,failed,warning
local function loc(x,y) return {X=x,Y=y} end
local C={DrawLayer={Bottom=0,Front=3,Top=4},SingleEmitter=function()return{}end,FiniteOverlayEmitter=function()return{}end}
C.AnimData=function(n,t,a,b)return{nom=n,t=t,a=a,b=b}end
C.BGAnimData=C.AnimData
C.StaticAnim=function(a,loops,duration)return{nom=a.nom,t=a.t,a=a.a,b=a.b,duration=duration}end
Direction={Down=0,Right=6,Left=2}
RogueElements={Loc=loc};RogueEssence={Content=C,Dungeon={
  CharAnimIdle=function(p,d)return{kind='idle',ToLoc=p}end,
  CharAbsentAnim=function(p,d)return{kind='hide',ToLoc=p}end,
  CharAnimJump=function() return{kind='jump'}end,
  CharAnimDrop=function() return{kind='drop'}end,
  CharAnimWalk=function(from,to,dir,speed) return{kind='walk',FromLoc=from,ToLoc=to}end}}
local team={Count=3};local map={MapTeams={Count=1,[0]={Players=team}}}
_ZONE={CurrentMap=map,CurrentZone={ID='dojo_kingambit_dedales',CurrentMapID={ID=2}}};_DATA={Save={CutsceneMode=false}}
GAME={WaitFrames=function(_,dt)assert(dt>=1 and _DATA.Save.CutsceneMode);clock=clock+dt end,CutsceneMode=function(_,v)_DATA.Save.CutsceneMode=v end}
SOUND={PlayBattleSE=function(_,n)son[#son+1]=n end}
DUNGEON={CharSetAction=function(_,ch,a)acts[#acts+1]={clock,ch.i,a};ch.CharLoc=a.ToLoc or a.AnimLoc;ch.pose=a.kind end,
         PlayVFX=function(_,e,x,y,dir)
           if failed then error('banc : banque absente') end
           assert(dir==0 and e.Anim.t==4)
           fx[#fx+1]={clock,e,x,y}
         end}
PrintInfo=function(s)assert(s:find('banque absente'));warning=true end
local o={{7,2},{5,3},{9,3}}
local p={loc(7,3),loc(5,4),loc(9,4)}
local function run(typ,mode,pose,err)
  fx={};acts={};son={};clock=0;failed=err;warning=false;map.Element=typ
  for i=1,3 do team[i-1]={CharLoc=p[i],HP=42,i=i,Form=0} end
  local a={Type=typ,Mode=mode,Pose=pose,Origines=o}
  mod.Masquer(nil,nil,{},a);assert(#acts==3 and team[0].pose=='hide')
  mod.Jouer(nil,nil,{},a)
  for i=1,3 do assert(team[i-1].CharLoc==p[i] and team[i-1].Form==0 and team[i-1].HP==42 and team[i-1].pose=='idle') end
  assert(#son==1 and son[1]=='Kingambit_Whoosh_'..typ and not _DATA.Save.CutsceneMode)
  if err then assert(warning);return end
  assert(clock==76)
end
for _,typ in ipairs({'water','fire','ground','rock'})do
  local col=typ=='water' or typ=='fire'
  run(typ,col and 'column' or 'emerge',6)
  local delai={0,6,12}
  for i=1,3 do
    local s,a=fx[i*2-1],fx[i*2];assert(s[1]==delai[i] and a[1]==delai[i]);assert(s[4]==o[i][2]*24+12 and a[4]==s[4]);assert(a[3]==o[i][1]*24+12)
    assert(s[2].Layer==0 and a[2].Layer==3 and a[2].Anim.a==0 and a[2].Anim.b==15)
    assert(acts[3+i][1]==delai[i]+24 and acts[3+i][3].kind==(col and 'walk' or 'jump'))
  end
end
run('electric','storm',5);assert(#fx==2 and fx[1][1]==0 and fx[2][3]==180 and fx[2][4]==84 and acts[4][1]==20)
run('ice','whiteout',6);assert(#fx==1 and fx[1][2].Layer==4 and fx[1][2].RepeatX and fx[1][2].RepeatY and fx[1][2].TotalTime==64)
for i=1,3 do assert(acts[i+3][1]==24+(i-1)*4) end
run('poison','mist',8);assert(#fx==7 and fx[1][2].Anim.nom=='Kingambit_Entree_poison_Ecran' and acts[4][1]==32)
run('water','column',6,true)
print('PASS 3 colonnes et sorties distinctes, brèches, éclair unique, nappes plein écran et retour des poses en cas d’erreur.')
