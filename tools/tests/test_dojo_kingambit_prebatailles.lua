-- Banc unitaire Lua sans moteur : ordre, durée, enveloppe de scène et garde.
local p=require 'destiny.dojo_kingambit_prebatailles'
local list={'normal','fire','water','grass','electric','ice','fighting','poison','ground','flying','psychic','bug','rock','ghost','dragon','dark','steel','fairy'}
local tick,seq,absent,fail_son,fail_vfx,warn
local z={ID='dojo_kingambit_dedales',CurrentMapID={ID=2}}
local m={MapTeams={Count=1,[0]={Players={Count=3}}}}
_ZONE={CurrentZone=z,CurrentMap=m}
_DATA={Save={CutsceneMode=false}}
Direction={Down=0}
local rect={X=17,Y=63,Width=320,Height=240}
local C={
  GraphicsManager={GetBackground=function(name)
    assert(name=='Kingambit_Prebataille_' .. m.Element)
    if absent then return {TileWidth=1,TileHeight=1,TotalFrames=1} end
    return {TileWidth=320,TileHeight=240,TotalFrames=28}
  end},
  DrawLayer={Top=4},
  FiniteOverlayEmitter=function()return{}end,
  BGAnimData=function(n,t,f,l)return{name=n,t=t,f=f,l=l}end
}
RogueEssence={Content=C,Dungeon={DungeonScene={Instance={ViewRect=rect}}}}
GAME={WaitFrames=function(_,dt)assert(dt>=1 and _DATA.Save.CutsceneMode);tick=tick+dt end,
      CutsceneMode=function(_,mode)_DATA.Save.CutsceneMode=mode end}
DUNGEON={PlayVFX=function(_,e,x,y,dir)
  assert(_DATA.Save.CutsceneMode and tick==4 and dir==0)
  assert(x==rect.X+math.floor((rect.Width-320)/2) and y==rect.Y+math.floor((rect.Height-240)/2))
  assert(e.Anim.name=='Kingambit_Prebataille_'..m.Element and e.Anim.t==3 and e.Anim.f==0 and e.Anim.l==27)
  assert(e.Layer==4 and not e.RepeatX and not e.RepeatY and e.TotalTime==84 and e.FadeIn==0 and e.FadeOut==0)
  if fail_vfx then error('échec simulateur de rendu') end
  seq[#seq+1]='overlay'
end}
SOUND={PlayBattleSE=function(_,name)
  assert(tick==4 and name=='Kingambit_Prebataille_'..m.Element)
  if fail_son then error('son indisponible') end
  seq[#seq+1]='son'
end}
PrintInfo=function(s)warn=s end

local function reset(id)
  tick,seq,warn=0,{},nil
  absent,fail_son,fail_vfx=false,false,false
  m.Element=id
end
local fun=p.Apres(function(_,_,c,a)assert(c.User==nil and a.Type==m.Element);seq[#seq+1]='troupe' end)
for _,id in ipairs(list) do
  reset(id)
  fun(nil,nil,{}, {Type=id})
  assert(table.concat(seq,',')=='troupe,overlay,son' and tick==90 and not _DATA.Save.CutsceneMode and not warn)
end
reset('dark');rect.Width,rect.Height=360,256
_DATA.Save.CutsceneMode=true
p.Jouer(nil,nil,{}, {Type='dark'})
assert(_DATA.Save.CutsceneMode and tick==90)
_DATA.Save.CutsceneMode=false
reset('fairy');absent=true;p.Jouer(nil,nil,{}, {Type='fairy'})
assert(tick==0 and #seq==0 and not _DATA.Save.CutsceneMode and warn:find('banque non chargée'))
reset('grass');fail_son=true;p.Jouer(nil,nil,{}, {Type='grass'})
assert(tick==90 and #seq==1 and not _DATA.Save.CutsceneMode and warn:find('son indisponible'))
reset('steel');fail_vfx=true;p.Jouer(nil,nil,{}, {Type='steel'})
assert(tick==4 and #seq==0 and not _DATA.Save.CutsceneMode and warn:find('simulateur'))
reset('normal');p.Jouer(nil,nil,{User={}}, {Type='normal'})
p.Jouer(nil,nil,{}, {Type='psy'});p.Jouer(nil,nil,{}, {Type='water'})
z.CurrentMapID.ID=1;p.Jouer(nil,nil,{}, {Type='normal'})
z.CurrentMapID.ID=2;z.ID='grotte_verdoyante';p.Jouer(nil,nil,{}, {Type='normal'})
z.ID='dojo_kingambit_dedales';m.MapTeams[0].Players.Count=1;p.Jouer(nil,nil,{}, {Type='normal'})
assert(tick==0 and #seq==0 and not warn and not _DATA.Save.CutsceneMode)
print('PASS : 18 wooshes après la troupe, position caméra et 90 ticks ; hors finale ignoré, récupération si banque, son ou rendu manque.')
