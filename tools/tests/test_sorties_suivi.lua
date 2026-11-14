-- Les capteurs des intérieurs ne doivent pas se déclencher pour le suiveur.
package.path='game/Data/Script/?.lua;game/Data/Script/?/init.lua;'..package.path
package.preload['origin.common']=function() return {} end
package.preload['destiny.suivi_interieurs']=function() return {Activer=function()end} end
local count=0
GAME={FadeOut=function()end,EnterZone=function() count=count+1 end}
SV={Destiny={}}
local tests={
 {'reverie_electric_home','Electric_Home_Entrance_Touch'},
 {'reverie_fire_home','Fire_Home_Entrance_Touch'},
 {'reverie_grass_home','Grass_Home_Entrance_Touch'},
 {'reverie_hutte_aquatique','Water_Home_Entrance_Touch'},
 {'reverie_inn','Inn_Entrance_Touch'},
 {'reverie_normal_home','Normal_Home_Entrance_Touch'},
 {'reverie_post_office','South_Exit_Touch'},
 {'reverie_rock_home','Rock_Home_Entrance_Touch'},
 {'reverie_water_home','Water_Home_Entrance_Touch'},
 {'dojo_kingambit','MarowakDojoExit_Touch'},
 {'guilde_destiny_accueil','SortieGuilde_Touch'},
 {'guilde_destiny_missions','EscalierNord_Touch'},
 {'ledian_dojo','Dojo_Exit_Touch'},
}
for _,t in ipairs(tests) do
 local module=require('destiny.ground.'..t[1]..'.init')
 local n=count
 module[t[2]]({}, {EntName='Teammate1'});assert(count==n,t[1]..' suiveur déclenche la sortie')
 module[t[2]]({}, {EntName='PLAYER'});assert(count==n+1,t[1]..' joueur ne sort pas')
 module[t[2]]({}, {EntName='PLAYER'});assert(count==n+1,t[1]..' sortie doublée')
end
print('PASS 13 sorties : partenaire ignoré, joueur accepté, double sortie évitée')
