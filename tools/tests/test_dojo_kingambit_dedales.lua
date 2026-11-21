-- Scénarios du dialogue, des calques de trappe et du cycle d'aventure.
package.preload['origin.common'] = function() return {} end
package.preload['destiny.suivi_interieurs'] = function() return {Activer=function() end} end
package.preload['destiny.equipe_scene'] = function() return {Suivre=function() end} end
local function char(id, x, y)
  return {EntName=id, Position={X=x,Y=y}, LocHeight=0, HideShadow=false, Data={},
    SetLocHeight=function(self,z) self.LocHeight=z end}
end
local h,p,k = char('PLAYER',376,200),char('Teammate1',397,220),char('Kingambit',376,184)
local layer = {Bottom=0,Front=3}
local result = {Failed=1,Cleared=2,TimedOut=4,GaveUp=5,Downed=6}
RogueEssence = {Content={
  DrawLayer=layer, SingleEmitter=function()return {} end,
  AnimData=function(name,t) return {Name=name,Time=t} end,
  StaticAnim=function(a,loop,len) return {Anim=a,Len=len} end,
  ScreenMover=function() return {} end},
  Dungeon={DrawEffect={Absent=4,Transparent=7}}, Data={GameProgress={DungeonStakes={None=0,Progress=1,Risk=2},ResultType=result}}}
SV = {Destiny={DojoKingambitPorteGaucheOuverte=true}}
local map={Layers={},TexWidth=96,TexHeight=72,GetObstacle=function() return 0 end}
for i=0,14 do map.Layers[i]={Visible=true} end
_ZONE={CurrentGround=map}
local solo=false
CH=function(id)
  if id=='PLAYER' then return h elseif id=='Kingambit' then return k elseif id=='Teammate1' and not solo then return p end
end
Direction={Up=4}
AI={DisableCharacterAI=function(_,ch) assert(ch==p) end}
TASK={StopEntityTask=function(_,ch) assert(ch==p) end}
local vfx,sons,entrees,profondeurs,ticks,cut,moved,retour,menus={},{},{},{},0,false,0,{},{}
local selections={}
local dernier_menu
UI={
  SetSpeaker=function() end,SetSpeakerEmotion=function() end,ResetSpeaker=function() end,
  BeginMultiPageMenu=function(_,x,y,w,name,opts,n,def,cancel)
    assert(x>=0 and y>=0 and x+w<=320 and n==7 and def==1 and cancel==19)
    assert(#opts==19 and opts[19]=='Annuler')
    assert(opts[1]:find('Normal') and opts[18]:find('Fée') and name:find('Dédales'))
    dernier_menu=opts;menus[#menus+1]='types'
  end,
  BeginChoiceMenu=function(_,prompt,opts,def,cancel)
    assert(prompt:find('Deux étages') and opts[1]=='Descendre' and def==cancel and def==2)
    menus[#menus+1]='confirmer'
  end,
  WaitForChoice=function() end,
  ChoiceResult=function() return table.remove(selections,1) end,
}
GROUND={
  CharEndAnim=function() end,
  MoveToPosition=function(_,ch,x,y) assert(ch==p and cut);p.Position={X=x,Y=y};moved=moved+1 end,
  PlayVFX=function(_,e,x,y) vfx[#vfx+1]={ticks,e.Layer,x,y,e.Anim.Anim.Name} end,
  MoveScreen=function() end,
  CharSetAnim=function(_,ch,act) assert(act=='Hurt' and ch.HideShadow) end,
  CharSetDrawEffect=function(_,ch,e)
    if e==7 then assert(ch.LocHeight==-11);ch.transparent=true
    else assert(e==4 and ch.transparent and ch.LocHeight==-16);ch.absent=true end
  end,
  CharEndDrawEffect=function(_,ch,e)
    if e==4 then ch.absent=false else assert(e==7);ch.transparent=false end
  end,
}
SOUND={PlayBattleSE=function(_,s) sons[#sons+1]=s end}
GAME={
  FadeIn=function() end,
  FadeOut=function() assert(h.absent and h.LocHeight<0 and cut); assert(#profondeurs>=16) end,
  CutsceneMode=function(_,b) cut=b end,
  WaitFrames=function(_,t) ticks=ticks+t;if h.LocHeight<0 then profondeurs[#profondeurs+1]=h.LocHeight end end,
  SetRescueAllowed=function(_,b) assert(b==false) end,
  EnterDungeon=function(_,z,s,m,e,stakes,recorded,norestrict)
    assert(not cut and h.LocHeight==0 and not h.HideShadow and not h.absent and not h.transparent)
    assert(p.LocHeight==0 and not p.HideShadow and not p.absent and not p.transparent)
    assert(z=='dojo_kingambit_dedales' and stakes==1 and m==0 and e==0 and not recorded and norestrict)
    entrees[#entrees+1]=s
  end,
  EndDungeonRun=function(_,res,z,seg,g,e,show,fan)
    assert(z=='town02_waterfallvillage' and seg==-1 and g==17 and e==3 and not show and not fan)
    assert(SV.Destiny.EntrainementKingambit.Dernier.Issue)
    retour[#retour+1]=res
  end,
  EnterZone=function(_,z,seg,g,e) assert(z=='town02_waterfallvillage' and seg==-1 and g==17 and e==3) end,
}
local types=require('destiny.dojo_kingambit_types')
local a=require('destiny.ground.dojo_kingambit.init')
local zone=require('destiny.zone.dojo_kingambit_dedales.init')
a.Init(map);a.Enter(map)
a.Kingambit_Action(k,p); assert(#menus==0)
selections={19};a.Kingambit_Action(k,h)
selections={1,2};a.Kingambit_Action(k,h)
assert(#entrees==0 and #vfx==0 and #sons==0 and moved==0)
assert(#menus==3 and SV.Destiny.EntrainementKingambit==nil)
for seg=0,17 do
  a.Enter(map)
  vfx,sons,profondeurs,ticks = {},{},{},0
  solo=seg%2==1
  selections={seg+1,1}
  a.Kingambit_Action(k,h)
  assert(entrees[#entrees]==seg and #vfx==2 and #sons==2)
  assert(h.Position.X==376 and h.Position.Y==200 and vfx[1][4]==212)
  assert(vfx[1][3]==(solo and 384 or 395) and vfx[1][2]==layer.Bottom and vfx[2][2]==layer.Front)
  local bank='Kingambit_Trappe_'..types[seg+1][1]..'_'
  assert(vfx[1][5]==bank..'Sol' and vfx[2][5]==bank..'Rebord')
  local precedent=0
  for _,z in ipairs(profondeurs) do assert(z<=precedent);precedent=z end
  assert(precedent==-36)
  a.Kingambit_Action(k,h);assert(#entrees==seg+1) -- verrou, pas de double départ.
end
assert(#entrees==18 and moved==9)
-- Deux puits si le partenaire est trop loin pour partager le même rebord.
solo=false;p.Position={X=456,Y=228}
a.Enter(map);vfx={};selections={1,1};a.Kingambit_Action(k,h)
assert(moved==9 and #vfx==4 and vfx[1][3]==384 and vfx[1][4]==212)
assert(vfx[3][3]==464 and vfx[3][4]==240 and vfx[4][2]==layer.Front)
zone.EnterSegment({},false,17,0)
assert(sons[#sons]=='EVT_EP_Pitfall_Land')
zone.ExitSegment({},result.GaveUp,false,17,0)
assert(SV.Destiny.EntrainementKingambit.Dernier.Type=='fairy')
assert(SV.Destiny.EntrainementKingambit.Dernier.Issue=='abandon')
assert(not SV.Destiny.EntrainementKingambit.Reussis.fairy)
zone.ExitSegment({},result.Cleared,false,17,2)
assert(SV.Destiny.EntrainementKingambit.Reussis.fairy)
zone.ExitSegment({},result.Failed,false,3,1)
assert(SV.Destiny.EntrainementKingambit.Dernier.Issue=='ko')
zone.ExitSegment({},result.TimedOut,false,3,0)
assert(SV.Destiny.EntrainementKingambit.Dernier.Issue=='temps')
assert(SV.Destiny.EntrainementKingambit.Reussis.fairy and not SV.Destiny.EntrainementKingambit.Reussis.grass)
assert(#retour==4 and SV.Destiny.DojoKingambitPorteGaucheOuverte==true)
a.Enter(map);selections={19};a.Kingambit_Action(k,h)
assert(dernier_menu[18]:find('+',1,true) and not dernier_menu[4]:find('+',1,true))
print('PASS Kingambit Lua — 18 routes, annulation, trappe duo/solo immobile, victoire, K.O., délai et abandon.')
