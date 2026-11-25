#!/usr/bin/env python3
from pathlib import Path
from lupa import LuaRuntime
import json, copy
R=Path(__file__).resolve().parent
B=Path('/home/user/chantier-lostwood-amapola/base-057')
old=json.loads((B/'game/Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))
new=json.loads((R/'candidat/game/Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))
ref=copy.deepcopy(old)
for s in ref['Object']['Segments']:
 for f in s['Floors']:
  rm=[x for x in f['GenSteps'] if any(m.get('Spawn','').startswith('destiny_lost_wood_ruine_') for m in x['Value'].get('Maps',[]))]
  assert len(rm)==1 and len(rm[0]['Value']['Maps'])==6
  f['GenSteps'].remove(rm[0])
assert ref==new, 'Autre différence dans la zone'
script=(B/'game/Data/Script/destiny/mapgen_lost_wood.lua').read_text()
newscript=(R/'candidat/game/Data/Script/destiny/mapgen_lost_wood.lua').read_text()
block=(R/'bloc-fleurs.lua').read_text()
assert newscript.replace(block,'')==script
assert 'map.Rand:' not in block

stub=r'''
FLOOR_GEN_SCRIPT={}
RogueElements={Loc=function(x,y) return {X=x,Y=y} end}
local function list()
 local v={Count=0}
 function v:Add(x) self[self.Count]=x; self.Count=self.Count+1 end
 return v
end
RogueEssence={Dungeon={},Content={},Ground={}}
RogueEssence.Dungeon.Tile=function(id) return {ID=id} end
RogueEssence.Dungeon.TileLayer=function(loc,sheet) return {loc=loc,sheet=sheet} end
RogueEssence.Content.DrawLayer={Bottom=0,Front=1}
RogueEssence.Content.ObjAnimData=function(name,dur) return {AnimIndex=name,FrameTime=dur} end
RogueEssence.Ground.AnimLayer=function(name) return {Name=name,Anims=list()} end
RogueEssence.Ground.GroundAnim=function(anim,loc) return {ObjectAnim=anim,MapLoc=loc} end
function make_map()
 local m={Width=40,Height=32,RoomTerrain='floor',WallTerrain='wall'}
 m.Rand={n=0}
 function m.Rand:Next(a,b)
  self.n=self.n+1
  if b==nil then b=a;a=0 end
  return a+((self.n*31+17)%(b-a))
 end
 m.tiles={}
 for x=0,m.Width-1 do
  m.tiles[x]={}
  for y=0,m.Height-1 do
   local id=(x==0 or y==0 or x==m.Width-1 or y==m.Height-1 or (x>=18 and x<=21)) and 'wall' or 'floor'
   local t={ID=id,Effect={ID=''},Data={StableTex=false}}
   function t:TileEquivalent(v) return self.ID==v end
   m.tiles[x][y]=t
  end
 end
 m.tiles[6][6].Effect.ID='stairs'; m.tiles[8][8].Data.StableTex=true
 function m:GetTile(loc) return self.tiles[loc.X] and self.tiles[loc.X][loc.Y] end
 function m:TileBlocked(loc) local t=self:GetTile(loc);return not t or t.ID~='floor' end
 function m:TrySetTile(loc,t) local old=self:GetTile(loc); old.ID=t.ID;return true end
 m.RoomPlan={HallCount=1}; function m.RoomPlan:GetHall(i) return {Draw={Start={X=2,Y=15},Size={X=36,Y=2}}} end
 m.Map={Layers=list(),Decorations=list()}
 function m.Map:AddLayer(name)
  local layer={Name=name,Tiles={}}
  for x=0,m.Width-1 do layer.Tiles[x]={};for y=0,m.Height-1 do
   local t={Layers=list()};function t:IsEmpty() return self.Layers.Count==0 end;layer.Tiles[x][y]=t
  end end
  self.Layers:Add(layer)
 end
 return m
end
'''
def run(src):
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(stub);lua.execute(src)
 m=lua.eval('make_map()');lua.globals().FLOOR_GEN_SCRIPT.DestinyLostWoodRiviereEtLucioles(m,lua.table())
 return m
before,after=run(script),run(newscript)
assert before.Rand.n==after.Rand.n
assert before.Map.Layers.Count==after.Map.Layers.Count==2
for x in range(40):
 for y in range(32):
  assert before.tiles[x][y].ID==after.tiles[x][y].ID
  for li in range(2):
   a=before.Map.Layers[li].Tiles[x][y].Layers;b=after.Map.Layers[li].Tiles[x][y].Layers
   assert a.Count==b.Count
   for i in range(a.Count):
    assert (a[i].sheet,a[i].loc.X,a[i].loc.Y)==(b[i].sheet,b[i].loc.X,b[i].loc.Y)
lights1=before.Map.Decorations[0];lights2=after.Map.Decorations[0]
assert lights1.Name==lights2.Name=='Lucioles' and lights1.Anims.Count==lights2.Anims.Count
for i in range(lights1.Anims.Count):
 a,b=lights1.Anims[i],lights2.Anims[i];assert (a.MapLoc.X,a.MapLoc.Y,a.ObjectAnim.AnimIndex,a.ObjectAnim.FrameTime)==(b.MapLoc.X,b.MapLoc.Y,b.ObjectAnim.AnimIndex,b.ObjectAnim.FrameTime)
flowers=after.Map.Decorations[1];assert flowers.Name=='Fleurs des Bois Perdus' and flowers.Anims.Count>0
kinds=set()
for i in range(flowers.Anims.Count):
 a=flowers.Anims[i];name=a.ObjectAnim.AnimIndex;kinds.add(name)
 offset=-4 if name in ('Flowers_Town_1','Flowers_Town_2') else 0
 x=(a.MapLoc.X-offset)//24;y=(a.MapLoc.Y-offset)//24
 assert x*24+offset==a.MapLoc.X and y*24+offset==a.MapLoc.Y
 assert 2<=x<38 and 2<=y<30
 assert after.tiles[x][y].Effect.ID=='' and not after.tiles[x][y].Data.StableTex
 assert not (2<=x<38 and 15<=y<17), 'fleur dans le couloir'
 for dx in (-1,0,1):
  for dy in (-1,0,1):assert after.tiles[x+dx][y+dy].ID=='floor' and after.tiles[x+dx][y+dy].Effect.ID==''
print('PASS : 14 étages, retrait exclusif des générateurs de ruines, script original inchangé hors bloc floral')
print('PASS : sur carte doublure, terrain, galets, sentiers, lucioles et RNG identiques')
print('PASS :',flowers.Anims.Count,'fleurs non bloquantes, variétés',sorted(kinds),'; exclusions proximité mur, effet et couloir')
print('Limite : doublures, pas une génération PMDO ni une sauvegarde réelle.')
