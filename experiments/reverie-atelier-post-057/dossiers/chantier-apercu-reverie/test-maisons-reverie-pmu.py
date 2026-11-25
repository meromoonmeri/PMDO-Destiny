from pathlib import Path
from lupa import LuaRuntime
import json,collections
R=Path(__file__).resolve().parent;ground=R/'travail/game/Data/Ground';sources=R/'originaux/game/Data/Ground';scripts=R/'travail/game/Data/Script';names=['reverie_rock_home','reverie_fire_home','reverie_grass_home','reverie_normal_home','reverie_water_home','reverie_electric_home']
known={x['path'][len('game/Content/Tile/'):-len('.tile')] for x in json.loads((R/'arbre.json').read_text())['tree'] if x['path'].startswith('game/Content/Tile/') and x['path'].endswith('.tile')}
for n in names:
 old=json.loads((sources/(n+'.rsground')).read_text(encoding='utf-8-sig'))['Object'];o=json.loads((ground/(n+'.rsground')).read_text(encoding='utf-8-sig'))['Object'];assert len(o['Layers'])==5 and len(o['obstacles'])==80 and len(o['obstacles'][0])==60
 assert all(o[k]==old[k] for k in ('AssetName','Name','Music','Released','Comment'))
 for tp in ('GroundObjects','Markers','Spawners','MapChars'):
  assert [x['EntName'] for x in o['Entities'][0].get(tp,[])]==[x['EntName'] for x in old['Entities'][0].get(tp,[])]
 refs=set()
 for lay in o['Layers']:
  for col in lay['Tiles']:
   for cell in col:
    for ls in cell['Layers']:
     refs.update(f['Sheet'] for f in ls['Frames'] if f['Sheet'])
 assert refs and refs<=known,(n,refs-known)
 for x,y in [(304,352),(328,352),(304,368),(328,368)]:assert all(o['obstacles'][cx][cy]['Tags']==0 for cx in range(x//8,(x+15)//8+1) for cy in range(y//8,(y+15)//8+1))
 lua=LuaRuntime(unpack_returned_tuples=True);lua.globals().package.path=str(scripts/'?.lua')+';'+lua.globals().package.path
 lua.execute("""package.preload['origin.common']=function()return {} end
 package.preload['destiny.suivi_interieurs']=function()return {Activer=function(m) followed=true end}end
 SV={};Direction={Up=0};moved={};actors={PLAYER={Position={X=100,Y=100}},Teammate1={Position={X=150,Y=100}}};function CH(n)return actors[n]end
 GROUND={TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};moved[#moved+1]={x=x,y=y}end}
 GAME={FadeIn=function()end,FadeOut=function()end,EnterGroundMap=function(_,...) call={...}end}
 """)
 mod=lua.execute((scripts/'destiny/ground'/n/'init.lua').read_text());mod.GameLoad(lua.table());assert lua.eval('actors.PLAYER.Position.X')==304 and lua.eval('actors.Teammate1.Position.X')==328 and lua.eval('followed')
 lua.execute('actors.PLAYER.Position.X=320; actors.Teammate1.Position.X=344');mod.GameLoad(lua.table());assert lua.eval('actors.PLAYER.Position.X')==320 and lua.eval('#moved')==2
 lua.execute('SV={};actors.Teammate1=nil;actors.PLAYER.Position.X=100');mod.GameLoad(lua.table());assert lua.eval('actors.PLAYER.Position.X')==304
 trigger=o['Entities'][0]['GroundObjects'][0]['EntName'];mod[trigger+'_Touch'](None,None);assert lua.eval('call[1]')==0 and lua.eval('call[2]')==0 and lua.eval('call[3]')==True
 print('PASS',n,len(refs),'banques ; seuil, entités, migration, sortie sur doublures')
print('Non testé : moteur, collisions d’objets, ancien fichier de sauvegarde et audio réels.')
