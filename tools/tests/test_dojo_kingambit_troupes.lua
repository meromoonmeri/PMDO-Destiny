-- Double de l'entrée en finale. Le moteur réel est validé séparément.
local M=require 'destiny.dojo_kingambit_troupes'
local function loc(x,y) return {X=x,Y=y} end
local function anim(n,loc,dir) return {nom=n,AnimLoc=loc,CharDir=dir} end
Direction={Down=0,Right=6,Left=2}
RogueElements={Loc=loc}
local C={DrawLayer={Bottom=0,Front=3}}
C.SingleEmitter=function() return {} end
C.AnimData=function(n,t,a,b) return {name=n,time=t,min=a,max=b} end
C.StaticAnim=function(data,loops,dur) return {data=data,loops=loops,dur=dur} end
RogueEssence={Content=C,Dungeon={
  CharAbsentAnim=function(p,d) return anim('masque',p,d) end,
  CharAnimIdle=function(p,d) return anim('pose',p,d) end,
  CharAnimWalk=function(p,q,d) return {nom='marche',FromLoc=p,ToLoc=q,CharDir=d} end,
  CharAnimJump=function() return {nom='bond'} end,
  CharAnimDrop=function() return {nom='pique'} end,
}}
local groupe={Count=3}
local carte={MapTeams={Count=1,[0]={Players=groupe}},Element='psychic'}
_ZONE={CurrentZone={ID='dojo_kingambit_dedales',CurrentMapID={ID=2}},CurrentMap=carte}
_DATA={Save={CutsceneMode=false}}
local t,sfx,fx,log,simuler_erreur,avertissements
local function armer(typ)
  carte.Element=typ
  t=0;sfx={};fx={};log={};simuler_erreur=false;avertissements=0
  for i,p in ipairs({loc(7,3),loc(5,4),loc(9,4)}) do groupe[i-1]={CharLoc=p,HP=10,PP=3,ix=i} end
end
GAME={
  CutsceneMode=function(_,b) _DATA.Save.CutsceneMode=b end,
  WaitFrames=function(_,delta) assert(_DATA.Save.CutsceneMode); t=t+delta end,
}
SOUND={PlayBattleSE=function(_,nom) sfx[#sfx+1]={t,nom} end}
DUNGEON={
  CharSetAction=function(_,c,a) log[#log+1]={t,c.ix,a.nom,a.AnimLoc or a.ToLoc};c.CharLoc=a.AnimLoc or a.ToLoc;c.pose=a.nom end,
  PlayVFX=function(_,e,x,y,d)
    assert(d==Direction.Down and x%24==12 and y%24==12)
    if simuler_erreur then error('ressource indisponible') end
    fx[#fx+1]={t,e.Anim.data.name,e.Layer,e.Anim.dur}
  end,
}
PrintInfo=function(a) assert(a:find('ressource indisponible'));avertissements=avertissements+1 end
local function e(typ,mode,pose,p)
  return {Type=typ,Mode=mode,Pose=pose,Origines=p or {{7,2},{5,3},{9,3}}}
end
armer('psychic')
local psy=e('psychic','warp',6,{{6,2},{4,2},{10,2}})
M.Masquer(nil,nil,{User=groupe[0]},psy);assert(#log==0)
M.Masquer(nil,nil,{},psy);assert(#log==3 and groupe[0].pose=='masque')
M.Jouer(nil,nil,{},psy)
assert(#sfx==1 and sfx[1][2]=='Kingambit_Whoosh_psychic')
assert(#fx==9 and fx[1][1]==8 and fx[1][2]=='Kingambit_Entree_psychic_Depart')
assert(fx[4][1]==20 and fx[4][3]==0 and fx[5][3]==3)
assert(log[4][3]=='pose' and log[4][4].X==6 and log[4][4].Y==2)
assert(log[7][3]=='masque' and log[7][1]==16)
assert(log[10][1]==44 and log[10][4].X==7 and log[10][4].Y==3)
assert(t==96 and not _DATA.Save.CutsceneMode and groupe[0].HP==10 and groupe[0].PP==3)
-- Les quatre entrées météo/cyclone ont leur cadence propre dans le test dédié.
for _,cas in ipairs({{'ghost','shadow',7,'marche'},{'fairy','idle',10,'pose'},{'ground','emerge',6,'bond'},{'bug','idle',7,'pose'}}) do
  local typ,mode,pose,animation=table.unpack(cas)
  armer(typ);local args=e(typ,mode,pose)
  M.Masquer(nil,nil,{},args); M.Jouer(nil,nil,{},args)
  assert(#sfx==1 and sfx[1][2]=='Kingambit_Whoosh_'..typ)
  assert(#fx==6 and fx[1][1]==0 and fx[3][1]==6 and fx[5][1]==12)
  assert(log[4][1]==pose*4 and log[4][3]==animation)
  assert(t==76 and not _DATA.Save.CutsceneMode and groupe[0].pose=='pose')
end
armer('normal');simuler_erreur=true
local normal=e('normal','walk',5)
_ZONE.CurrentZone.CurrentMapID.ID=1;M.Masquer(nil,nil,{},normal); M.Jouer(nil,nil,{},normal)
assert(#log==0 and #sfx==0)
_ZONE.CurrentZone.CurrentMapID.ID=2; M.Masquer(nil,nil,{},normal); M.Jouer(nil,nil,{},normal)
assert(avertissements==1 and not _DATA.Save.CutsceneMode and groupe[0].pose=='pose' and groupe[0].HP==10)
print('PASS intro Lua : avant combat, Psy à deux positions, ombres, pétales avant révélation, restauration sûre.')
