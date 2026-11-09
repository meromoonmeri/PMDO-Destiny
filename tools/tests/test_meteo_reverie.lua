-- Tests du module de production sur doublures ; pas de rendu PMDO.
local m=assert(loadfile(arg[1]..'/game/Data/Script/destiny/meteo_reverie.lua'))()
local result,draws=1,0
math.random=function(a,b)assert(a==1 and b==100);draws=draws+1;return result end
local statuses,calls={},{}
GROUND={
 AddMapStatus=function(_,name)statuses[name]=true;calls[#calls+1]='+'..name end,
 RemoveMapStatus=function(_,name)statuses[name]=nil;calls[#calls+1]='-'..name end,
}
SV={Destiny={}}
local function day(n,roll,want)
 SV.Destiny.JourneeVille=n;result=roll;local before=draws
 assert(m.Temps()==want and draws==before+1 and SV.Destiny.MeteoReverie.jour==n)
 assert(m.Temps()==want and draws==before+1,'retirage le même jour')
end
day(0,1,'clair');day(1,35,'clair');day(2,36,'soleil');day(3,55,'soleil');day(4,56,'couvert');day(5,75,'couvert');day(6,76,'pluie');day(7,100,'pluie')
assert(m.Description():find('pleut',1,true));print('PASS quatre temps, bornes et tirage unique par jour')
local maps={'WaterfallVillageCapital','WaterfallVillageCapital_Dev','reverie_centre','reverie_centre_Dev','reverie_nord','reverie_nord_Dev','reverie_etang','reverie_etang_Dev','reverie_residentiel','reverie_residentiel_Dev','crossroadreverietown2'}
for _,name in ipairs(maps) do
 statuses={rain=true,sunny=true,cloudy=true,decoration=true};calls={};local before=draws
 assert(m.Appliquer({AssetName=name}) and draws==before)
 assert(statuses.rain and not statuses.sunny and not statuses.cloudy and statuses.decoration)
 assert((statuses.clouds_overhead==true)==(name~='crossroadreverietown2'))
end
print('PASS dix variantes et carrefour : pluie identique, autres statuts conservés')
statuses={autre=true};calls={};local before=draws
for _,name in ipairs({'caféspindaaccueil','maison_equipe_falaise','cliffdaytest','donjon',''}) do assert(not m.Appliquer({AssetName=name})) end
assert(not m.Appliquer(nil) and #calls==0 and draws==before and statuses.autre)
print('PASS aucun effet et aucun tirage dans les intérieurs ou cartes exclues')
-- Simule une sauvegarde/rechargement, sans appeler le générateur de nombres.
local saved={jour=SV.Destiny.MeteoReverie.jour,temps=SV.Destiny.MeteoReverie.temps}
SV={Destiny={JourneeVille=7,MeteoReverie=saved}};result=1;assert(m.Temps()=='pluie' and draws==before)
SV.Destiny.JourneeVille=8;assert(m.Temps()=='clair' and draws==before+1)
SV={Destiny={}};result=50;assert(m.Temps()=='soleil' and SV.Destiny.MeteoReverie.jour==0)
print('PASS rechargement, jour suivant et migration ancienne sauvegarde simulés')
SV.Destiny.MeteoReverie={jour=0,temps='non_valide'};result=57;assert(m.Temps()=='couvert')
GROUND.RemoveMapStatus=function()error('simulation erreur moteur')end
assert(m.Appliquer({AssetName='reverie_centre'})==false);print('PASS effet indisponible : erreur confinée')
-- Intégration du vrai script du carrefour aux deux points d'entrée.
GROUND.RemoveMapStatus=function(_,n)statuses[n]=nil end
package.preload['origin.common']=function()return {}end
package.preload['destiny.equipe_scene']=function()return {}end
package.preload['destiny.meteo_reverie']=function()return m end
RogueElements={Rect=function()return {}end}
RogueEssence={Ground={GroundObject=function()return {SetTriggerType=function()end,OnMapInit=function()end}end,GroundEntity={EEntityTriggerTypes={Touch=1}}}}
function CH()return nil end
GAME={FadeIn=function()end};SOUND={PlayBGM=function()end}
local map={AssetName='crossroadreverietown2',objects={}}
function map:FindObject(n)return self.objects[n]end
function map:AddObject(o)self.objects[o.EntName]=o end
SV={Destiny={JourneeVille=5,MeteoReverie={jour=5,temps='pluie'}}};statuses={}
local cross=assert(loadfile(arg[1]..'/game/Data/Script/destiny/ground/crossroadreverietown2/init.lua'))()
cross.Init(map);assert(statuses.rain and not statuses.clouds_overhead)
statuses={sunny=true};cross.GameLoad(map);assert(statuses.rain and not statuses.sunny)
assert(map.objects.SortieFalaise and map.objects.SortieVille)
print('PASS carrefour Init et GameLoad, sorties intactes')
