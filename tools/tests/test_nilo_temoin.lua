-- Le spectateur ne fait pas partie du modèle de combat, même à la reprise.
local root = assert(arg[1])
package.preload['destiny.fosse_cascade_scene'] = function()
  return assert(loadfile(root..'/game/Data/Script/destiny/fosse_cascade_scene.lua'))()
end
local poses = {}
local brushes = {Remove=function(_, pose)
  for i,v in ipairs(poses) do if v == pose then table.remove(poses, i); return true end end
end}
local scene = {Anims={[2]=brushes}}
local gm = {CurrentScene=nil}
local gfx = {TotalFrameTick=0, IdleAction=0, GetChara=function()
  return {GetReferencedAnimIndex=function() return 0 end, AnimData={[0]={SeqAtDir=function()
    return {Frames={Count=2, [0]={EndTime=15}, [1]={EndTime=30}}}
  end}}}
end}
local map = {AssetName='end_grotte_verdoyante', MapTeams={'kabutops'}, AllyTeams={}, MapTurns=0}
_ZONE = {CurrentMap=map}
DrawLayer = {Normal=2}; Direction = {Down=0}; Gender = {Male=1}
RogueElements = {Loc=function(x,y) return {X=x,Y=y} end}
RogueEssence = {
  GameManager={Instance=gm},
  Dungeon={DungeonScene={Instance=scene}, MonsterID=function(s)
    assert(s=='shinx'); return {ToCharID=function() return 'shinx' end}
  end},
  Content={GraphicsManager=gfx, CharAfterImage=function(loc,id,anim,frame,dir,height,time,alpha)
    assert(id=='shinx' and alpha==255 and time>0 and height==0 and dir==Direction.Down)
    return {loc=loc, frame=frame, Finished=false}
  end},
}
DUNGEON = {PlayVFXAnim=function(_, pose, layer) assert(layer == 2); table.insert(poses, pose) end}
EngineServiceEvents = {Update='tick', DungeonFloorExit='exit', DungeonModeEnd='end'}
local callbacks = {}
SCRIPT = {AddService=function(_,name,svc)
  assert(name=='NiloTemoin')
  svc:Subscribe({Subscribe=function(_, _, k, v) callbacks[k] = v end})
end}
assert(loadfile(root..'/game/Data/Script/destiny/services/nilo_temoin/init.lua'))()
callbacks.tick(); assert(#poses==0, 'pas de spectateur hors donjon')
gm.CurrentScene = scene
local minx,maxx,frames = math.huge,-math.huge,{}
for i=0,100 do
  -- Même chemin en entrée et après une sauvegarde : aucun hook de combat requis.
  gfx.TotalFrameTick = i*120
  callbacks.tick()
  local p = assert(poses[1]); assert(#poses==1 and p.loc.Y==160)
  minx, maxx = math.min(minx,p.loc.X), math.max(maxx,p.loc.X); frames[p.frame]=true
end
assert(minx==262 and maxx==266 and frames[0] and frames[1], 'tremblement entier et poses Idle natives')
assert(map.MapTeams[1]=='kabutops' and #map.MapTeams==1 and #map.AllyTeams==0 and map.MapTurns==0)
callbacks.exit(); assert(#poses==0)
_ZONE.CurrentMap = {AssetName='un_autre_etage'}; callbacks.tick(); assert(#poses==0)
_ZONE.CurrentMap = map; callbacks.tick(); assert(#poses==1)
callbacks['end'](); gm.CurrentScene=nil; callbacks.tick(); assert(#poses==0)
print('PASS test_nilo_temoin.lua : pose native, oscille derrière Kabutops, sans cible ni tour ; entrée, reprise et nettoyage.')
