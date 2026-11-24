-- lua test_wooshes_pmd.lua /chemin/dojo_kingambit_prebatailles.lua
local run = dofile(assert(arg[1],'donner le chemin du module Lua'))
local ids={'normal','fire','water','grass','electric','ice','fighting','poison','ground','flying','psychic','bug','rock','ghost','dragon','dark','steel','fairy'}
local t,white,fallback,fail_fade,fail_sound,events,sfx,log,trace
local function reinit(id,old)
  t,white,fallback,fail_fade,fail_sound,events,sfx,log,trace = 0,false,false,false,false,{},{},{},{}
  _ZONE={CurrentZone={ID='dojo_kingambit_dedales',CurrentMapID={ID=2}},
         CurrentMap={Element=id,MapTeams={Count=1,[0]={Players={Count=3}}}}}
  _DATA={Save={CutsceneMode=old}}
end
Color=function(r,g,b,a) return {r,g,b,a} end
PrintInfo=function(s) log[#log+1]=s end
Direction={Down='Down'}
RogueElements={Loc=function(x,y) return {X=x,Y=y} end}
RogueEssence={Content={
  GraphicsManager={GetBackground=function(str)
    if str=='Pre_Battle' then return {TileHeight=64,TileWidth=256,TotalFrames=4} end
    if fallback then return nil end
    return {TileHeight=64,TileWidth=256,TotalFrames=8}
  end},
  DrawLayer={Top='Top'},FlashEmitter=function() return {} end,FiniteOverlayEmitter=function() return {} end,
  BGAnimData=function(name,ticks,a,b) return {id=name,ticks=ticks,a=a,b=b} end,
},Dungeon={DungeonScene={Instance={ViewRect={X=21,Y=19,Width=320,Height=240}}}}}
GAME={WaitFrames=function(_,n) t=t+n end,CutsceneMode=function(_,b) _DATA.Save.CutsceneMode=b end,
  FadeOut=function(_,w,n)
    assert(w==true and white==false and n==30)
    trace[#trace+1]={'blanc',t,n};t=t+n;white=true
    if fail_fade then error('fondu interrompu') end
  end,
  FadeIn=function(_,n)
    assert(white and (n==0 or n==12));trace[#trace+1]={'reprise',t,n};t=t+n;white=false
  end,
}
DUNGEON={PlayVFX=function(_,e,x,y,dir)
  assert(_DATA.Save.CutsceneMode and dir==Direction.Down and e.Layer=='Top')
  events[#events+1]={e=e,x=x,y=y,t=t}
end}
SOUND={PlayBattleSE=function(_,name)
  sfx[#sfx+1]={name,t};if fail_sound then error('audio indisponible') end
end}

local levels={{-32},{-64,0},{-112,48},{-144,80},{-176,112}}
for _,id in ipairs(ids) do
  reinit(id,false)
  local called=false
  run.Apres(function() called=true;t=t+15 end)(nil,nil,{},{Type=id})
  assert(called and not white and not _DATA.Save.CutsceneMode and #log==0)
  assert(#events==11 and t==15+178 and #sfx==3)
  assert(sfx[1][1]=='EVT_Battle_Flash' and sfx[2][1]=='EVT_Battle_Flash' and sfx[3][1]=='EVT_Battle_Transition')
  assert(events[1].e.Anim.id=='White' and events[2].e.Anim.id=='White' and events[2].t-events[1].t==16)
  assert(trace[1][2]==15+126 and trace[2][2]==15+166)
  local i=3
  for g,ys in ipairs(levels) do
    for _,y in ipairs(ys) do
      local a=events[i];local e=a.e;local dir=g%2==1 and 1 or -1
      assert(a.x==181 and a.y==139+y and a.t==15+66+5*(g-1))
      assert(e.Anim.id=='Kingambit_Prebataille_PMD_'..id and e.Anim.a==math.max(0,g-2)+(dir<0 and 4 or 0))
      assert(e.Movement.X*dir>0 and e.Movement.Y==0 and e.RepeatX and not e.RepeatY)
      assert(a.t+e.TotalTime+e.FadeIn==15+158);i=i+1
    end
  end
end
reinit('fire',true);fallback=true;fail_sound=true
run.Jouer(nil,nil,{},{Type='fire'})
assert(events[3].e.Anim.id=='Pre_Battle' and events[4].e.Anim.a==0 and not white and _DATA.Save.CutsceneMode and #log==3)
reinit('fairy',false);fail_fade=true
run.Jouer(nil,nil,{},{Type='fairy'})
assert(not _DATA.Save.CutsceneMode and not white and #log==1 and trace[2][3]==0)
reinit('rock',false);_ZONE.CurrentZone.CurrentMapID.ID=1
run.Jouer(nil,nil,{},{Type='rock'});assert(#events==0 and #sfx==0 and t==0)
print('PASS : 18 types, flashes, neuf bandes croisées, fondu blanc et reprise ; repli vanilla et restauration sur erreur.')
