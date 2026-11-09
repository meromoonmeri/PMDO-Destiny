-- Doubles d'API : simulation de récupération des deux anciennes cartes.
package.preload['origin.common']=function() return {} end
local root=(arg[1] or '.')..'/game/Data/Script/destiny/ground/'
local log={};GAME={FadeOut=function(_,a,b)log.fade={a,b}end,EnterZone=function(_,...)log.zone={...}end};SV={Destiny={VisiteVille='terminee'}}
for _,name in ipairs({'guild_heros_room','guild_storage_room'}) do
 for _,event in ipairs({'Enter','GameLoad'}) do
  log={};SV.Destiny.VisiteVille='terminee';SV.Destiny.RetourBatimentX=1
  local carte=assert(loadfile(root..name..'/init.lua'))();carte[event](nil)
  assert(SV.Destiny.VisiteVille=='terminee' and SV.Destiny.ArriveeVille=='batiment' and SV.Destiny.RetourBatimentX==800 and SV.Destiny.RetourBatimentY==1160)
  assert(log.zone[1]=='town02_waterfallvillage' and log.zone[2]==-1 and log.zone[3]==0 and log.zone[4]==0)
  log.zone=nil;carte.Enter(nil);assert(log.zone==nil,'transition déclenchée deux fois')
 end
end
print('PASS : les deux anciennes cartes renvoient à Réverie à l’entrée ou au chargement (doubles).')
