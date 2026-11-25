-- Test d'ordre et de repli, sans émuler le rendu (contrôlé séparément dans PMDO).
local M=require 'destiny.dojo_kingambit_cinematiques'
local P=require 'destiny.dojo_kingambit_plans'
local types=require 'destiny.dojo_kingambit_types'
local function loc(x,y)return {X=x,Y=y} end
local function char(k,x,y)
  return {CharLoc=loc(x,y),CharDir=2,CurrentForm={Species=k},Appearance={Species=k,Form=0,Skin='normal',Gender=0}}
end
local hero,ami=char('riolu',7,8),char('shinx',6,8)
local centre = loc(160,144)
local groupe={Count=3,[0]=char('altaria',7,3),[1]=char('swablu',5,4),[2]=char('swablu',9,4)}
local map={ViewCenter=centre,Music='Marowak Dojo.ogg',MapTeams={Count=1,[0]={Players=groupe}}}
local scene={ActiveTeam={Players={Count=2,[0]=hero,[1]=ami}},FocusedCharacter=hero,ViewRect={X=12,Y=6,Width=320,Height=240}}
_ZONE={CurrentZone={ID='dojo_kingambit_dedales',CurrentMapID={ID=2}}, CurrentMap=map}
_DATA={Save={CutsceneMode=false}}
local entree=0;local raccord=0;local voie;local voix;local couleur;local seq;local noir=false;local malade;local son;local rapport
local function signe(s)seq[#seq+1]=s end
Color=function(...)return {...}end
RogueElements={Loc=loc}
RogueEssence={Content={GraphicsManager={GetBackground=function(n)
  assert(n=='Kingambit_Signaux_'..map.Element)
  return malade=='banque' and {TileWidth=8} or {TileWidth=384,TileHeight=288,TotalFrames=16}
end,IdleAction=3},
  OverlayAnim=function(p,b,c,omni,m,d)
    assert(p.X==-12 and p.Y==-12 and omni and d==96)
    return {EndAnim=function()signe('end')end}
  end,BGAnimData=function(n,t,a,b)assert(t==6 and a==0 and b==15);return n end,DrawLayer={Top=5}},
  Dungeon={DungeonScene={Instance=scene},IdleAnimAction=function()return {}end,CharAnimNone=function()return {}end},
  Data={Gender={Unknown=2}}}
GAME={CutsceneMode=function(_,v)_DATA.Save.CutsceneMode=v end,
  WaitFrames=function(_,n)assert(n>0 and _DATA.Save.CutsceneMode)end,
  FadeOut=function(_,blanc,t)assert(not blanc and t==26);noir=true;signe('noir')end,
  FadeIn=function(_,t)assert(t==12 or t==0);noir=false;signe('rallume')end}
SOUND={GetCurrentSong=function()return son end,FadeOutBGM=function(_,t)assert(t==26);son=''end,
  PlayBattleSE=function(_,s)assert(not noir);signe(s)end,
  PlayBGM=function(_,s,b)assert(not b);son=s end}
UI={ResetSpeaker=function()voix,visage=nil,nil end, SetSpeaker=function(_,n,_,e,f)
    voix,visage=n,e;if noir then assert(n=='???' and e=='' and f==-1)end
  end,SetSpeakerEmotion=function()end,
  WaitShowDialogue=function(_,s)
    if noir then
      assert(voix=='???' and visage=='' and s==voie.noir and son=='');signe('anonyme')
      if malade=='voix' then error('Dialogue injecté en panne') end
    else assert(voix==voie.chef and visage=='altaria' and s==voie.replique and entree==1);signe('portrait') end
  end}
DUNGEON={PlayVFXAnim=function(_,e,l)assert(noir and l==5);signe('signaux')end,
  CharSetEmote=function()end,CharTurnToChar=function(_,c,h)c.CharDir=4 end,
  CharSetAction=function()end,CharEndAnim=function()end}
TASK={BranchCoroutine=function(_,f)return f end,JoinCoroutines=function(_,tt)tt[1]()end}
PrintInfo=function(s)rapport[#rapport+1]=s end
local hook=M.Avec(function(_,_,c,a)
  assert(not noir and _DATA.Save.CutsceneMode);entree=entree+1;signe('entrée')
end,function()
  assert(not noir and not _DATA.Save.CutsceneMode and not voix and not visage)
  assert(hero.CharDir==2 and ami.CharDir==2 and map.ViewCenter==centre)
  raccord=raccord+1;signe('précombat')
end)
local function run(k,panne)
  seq,rapport,malade,entree,raccord,son,voie={},{},panne,0,0,'Marowak Dojo.ogg',P[k]
  map.Element=k
  hook(nil,nil,{}, {Type=k,Pose=6})
  assert(entree==1 and raccord==1 and son==map.Music and not noir and not _DATA.Save.CutsceneMode)
  if not panne then
    assert(#rapport==0)
    assert(table.concat(seq,'|')=='noir|anonyme|signaux|rallume|'..table.concat(voie.sons,'|')..'|entrée|portrait|précombat')
  else
    assert(#rapport==1)
    assert(table.concat(seq,'|')=='noir|anonyme|rallume|entrée|précombat')
  end
end
for _,t in ipairs(types) do run(t[1]) end
run('dragon','banque')
run('ghost','voix')
scene.ActiveTeam.Players.Count=1;run('normal')
for _,c in ipairs({{}, {User=hero}}) do hook(nil,nil,c,{Type='notype'}) end
assert(entree==1 and raccord==1)
print('PASS Cinématiques Lua — 18 introductions, noir indépendant du dialogue, 3 accents, portrait, caméra et musique restaurées ; solo et deux pannes récupérées.')
