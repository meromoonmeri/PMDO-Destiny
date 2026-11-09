from pathlib import Path
from lupa import LuaRuntime
import json,collections,hashlib
R=Path(__file__).resolve().parent
p=R/'travail/game/Data/Ground/maison_equipe_falaise.rsground';m=json.loads(p.read_text(encoding='utf-8-sig'))['Object'];o=m['obstacles'];assert (len(o),len(o[0]))==(80,60)
e=m['Entities'][0];obj={x['EntName']:x for x in e['GroundObjects']};assert set(obj)=={'LitEquipe','LitPartenaire','SortieMaison'}
assert len(m['Layers'])==5 and all(len(l['Tiles'])==80 and len(l['Tiles'][0])==60 for l in m['Layers'])
known={x['path'].removeprefix('game/Content/Tile/').removesuffix('.tile') for x in json.loads((R/'arbre.json').read_text())['tree'] if x['path'].startswith('game/Content/Tile/') and x['path'].endswith('.tile')}
refs=collections.Counter()
for l in m['Layers']:
 for col in l['Tiles']:
  for cell in col:
   for lay in cell['Layers']:
    for fr in lay['Frames']:
     if fr['Sheet']:refs[fr['Sheet']]+=1
assert refs and set(refs)<=known;print('PASS tuiles référencées :',len(refs),'banques publiées,',sum(refs.values()),'sous-cases')
def clear(x,y):return all(o[i][j]['Tags']==0 for i in range(x//8,(x+15)//8+1) for j in range(y//8,(y+15)//8+1))
assert all(clear(*xy) for xy in [(304,384),(328,384),(304,400),(328,400)])
assert obj['SortieMaison']['Collider']=={'X':288,'Y':416,'Width':64,'Height':8}
print('PASS seuils héros/partenaire et sortie, événements et dimensions')
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute("""package.preload['origin.common']=function() return {} end
package.preload['destiny.suivi_interieurs']=function()return {Activer=function(m) count=count+1 end}end
package.preload['destiny.equipe_scene']=function()return {}end
Direction={Up=0}; count=0; moved={}; actors={PLAYER={Position={X=200,Y=240}},Teammate1={Position={X=224,Y=240}}}
function CH(n)return actors[n]end
GROUND={TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};moved[#moved+1]={x=x,y=y} end}
GAME={FadeIn=function()end,FadeOut=function()end,EnterGroundMap=function(_,...) last={...} end,GroundSave=function() saved=true end}
UI={ResetSpeaker=function()end,ChoiceMenuYesNo=function()end,WaitForChoice=function()end,ChoiceResult=function()return true end,WaitShowDialogue=function()end}
SV={Destiny={}}
""")
mod=lua.execute(p.parent.parent.joinpath('Script/destiny/ground/maison_equipe_falaise/init.lua').read_text(encoding='utf8'))
mod.GameLoad(lua.table()); assert lua.eval('actors.PLAYER.Position.X')==304 and lua.eval('actors.Teammate1.Position.X')==328 and lua.eval('SV.Destiny.VersionMaisonEquipePMU')==1
lua.execute('actors.PLAYER.Position.X=336;actors.Teammate1.Position.X=360')
mod.GameLoad(lua.table());assert lua.eval('actors.PLAYER.Position.X')==336 and lua.eval('actors.Teammate1.Position.X')==360 and lua.eval('#moved')==2
lua.execute('SV={Destiny={}};actors.Teammate1=nil;actors.PLAYER.Position.X=100')
mod.GameLoad(lua.table());assert lua.eval('actors.PLAYER.Position.X')==304 and lua.eval('SV.Destiny.VersionMaisonEquipePMU')==1
mod.LitEquipe_Action(None,None);assert lua.eval('saved')
mod.SortieMaison_Touch(None,None);assert lua.eval('last[1]')=='destiny_cliff_tests' and lua.eval('last[2]')=='cliffdaytest' and lua.eval('last[4]')==True
print('PASS migrations et répétitions, partenaire absent, lit sauvegarde et sortie sur doublures')
print('Non testé : moteur PMDO, collision objets et sauvegardes réelles ; rythme et rendu jour/nuit')
