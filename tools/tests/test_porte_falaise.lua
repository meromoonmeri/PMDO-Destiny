local root=assert(arg[1]);package.path=root..'/game/Data/Script/?.lua;'..root..'/game/Data/Script/?/init.lua;'..package.path
package.preload['origin.common']=function()return{}end
local suivi=0;package.preload['destiny.equipe_scene']=function()return{Suivre=function()suivi=suivi+1 end}end
package.preload['destiny.cinematique']=function()return{}end
local trajets={};GAME={FadeOut=function()end,FadeIn=function()end,EnterGroundMap=function(_,zone,map,marker)trajets[#trajets+1]={zone,map,marker}end}
SOUND={StopBattleSE=function()end,FadeInBattleSE=function()end};Direction={Down=4};local hero,partenaire={EntName='PLAYER'}, {EntName='Teammate1'}
function CH(n)if n=='PLAYER'then return hero elseif n=='Teammate1'then return partenaire end end
GROUND={TeleportTo=function(_,a,x,y,dir)a.x=x;a.y=y;a.dir=dir end}
local cliff=require('destiny.ground.cliffdaytest.init')
SV={Destiny={}};cliff.PorteMaisonEquipe_Touch({},hero);assert(#trajets==0)
SV.Destiny.VisiteVille='terminee';cliff.PorteMaisonEquipe_Touch({},partenaire);assert(#trajets==0)
cliff.PorteMaisonEquipe_Touch({},hero);assert(#trajets==1 and trajets[1][1]=='destiny_cliff_tests' and trajets[1][2]=='maison_equipe_falaise' and trajets[1][3]=='entree')
SV.Destiny.RetourMaisonEquipe=true;cliff.PlotScripting();assert(not SV.Destiny.RetourMaisonEquipe and hero.x==600 and hero.y==476 and partenaire.x==624 and partenaire.y==476 and suivi==1)
print('PASS porte bloquée avant visite, partenaire ignoré, entrée et retour sans chevauchement')
