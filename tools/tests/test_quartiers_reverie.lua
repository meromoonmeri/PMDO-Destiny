-- Tests ciblés avec doublures. Ce fichier ne prétend pas simuler le moteur.
package.preload['origin.common']=function() return {} end
package.preload['origin.menu.skill.SkillSelectMenu']=function() return {} end
package.preload['origin.menu.team.AssemblySelectMenu']=function() return {} end
package.preload['destiny.equipe_scene']=function() return {Suivre=function() end} end
package.preload['destiny.cinematique']=function() return {NomEspece=function(_,n) return n end} end
package.preload['destiny.missions_reverie']=function() return {} end
Direction={Up='Up',Down='Down'}
RogueElements={Rect=function(x,y,w,h)return {x=x,y=y,w=w,h=h} end}
RogueEssence={Ground={GroundObject=function() return {OnMapInit=function()end,SetTriggerType=function(self,t)self.trigger=t end} end,GroundEntity={EEntityTriggerTypes={Touch='Touch',Action='Action'}}}}
local player={EntName='PLAYER',Position={X=800,Y=1160}}
local partner={EntName='Teammate1',Position={X=772,Y=1160}}
function CH(id) if id=='PLAYER' then return player elseif id=='Teammate1' then return partner end end
local call={}
GAME={FadeOut=function()end,FadeIn=function()end,MoveCamera=function()end,CutsceneMode=function()end,GetPlayerPartyCount=function()return 2 end,EnterGroundMap=function(_,...)call.transition={...} end}
GROUND={TeleportTo=function(_,who,x,y,dir)who.Position.X=x;who.Position.Y=y;who.direction=dir end}
SOUND={PlayBGM=function()end}
local root=(arg[1] or '.')..'/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'
local function load()return assert(loadfile(root))() end
local function map(name)
 local m={AssetName=name,Width=200,Height=500,objects={}}
 function m:FindObject(name)return self.objects[name] end
 function m:AddObject(obj)self.objects[obj.EntName]=obj end
 function m:GetObstacle(x,y)assert(x>=0 and x<200 and y>=0 and y<500);return 0 end
 return m
end
local entries={
 {'EscalierN1VersNord','reverie_nord',120,888,120,864},
 {'EscalierN1VersCentre','reverie_centre',120,952,120,976},
 {'EscalierN2VersNord','reverie_nord',776,808,776,784},
 {'EscalierN2VersCentre','reverie_centre',776,872,776,896},
 {'EscalierN3VersNord','reverie_nord',1200,808,1200,784},
 {'EscalierN3VersCentre','reverie_centre',1200,872,1200,896},
 {'EscalierSVersCentre','reverie_centre',700,1904,700,1880},
 {'EscalierSVersResidentiel','reverie_residentiel',700,1976,700,2000},
 {'EscalierPVersEtang','reverie_etang',1120,2352,1120,2328},
 {'EscalierPVersResidentiel','reverie_residentiel',1120,2432,1120,2456},
}
for _,e in ipairs(entries) do
 SV={Destiny={VisiteVille='terminee'}};call.transition=nil;local ville=load()
 ville[e[1]..'_Touch'](nil,partner);assert(not call.transition)
 ville[e[1]..'_Touch'](nil,player);assert(call.transition[1]=='town02_waterfallvillage' and call.transition[2]==e[2] and call.transition[3]=='entrance')
 local p=SV.Destiny.PassageQuartier;assert(p.x==e[3] and p.y==e[4] and p.px==e[5] and p.py==e[6]);call.transition=nil
 ville[e[1]..'_Touch'](nil,player);assert(not call.transition) -- protection double contact
 ville=load();ville.GameLoad(map(e[2]))
 assert(player.Position.X==e[3] and player.Position.Y==e[4] and partner.Position.X==e[5] and partner.Position.Y==e[6] and SV.Destiny.PassageQuartier==nil)
end
-- Anciennes entrées et retours d'intérieurs : migration à la bonne position.
for _,e in ipairs({{800,1160,'reverie_centre'}, {80,520,'reverie_nord'}, {480,2336,'reverie_residentiel'}, {1120,2352,'reverie_etang'}}) do
 SV={Destiny={VisiteVille='terminee',ArriveeVille='batiment',RetourBatimentX=e[1],RetourBatimentY=e[2]}};call.transition=nil;local ville=load()
 ville.Enter(map('WaterfallVillageCapital'));assert(call.transition[2]==e[3] and SV.Destiny.PassageQuartier.x==e[1] and SV.Destiny.PassageQuartier.y==e[2] and not SV.Destiny.ArriveeVille)
 ville=load();ville.Enter(map(e[3]));assert(player.Position.X==e[1] and player.Position.Y==e[2])
end
SV={Destiny={VisiteVille='terminee',ArriveeVille='cafe'}};call.transition=nil;load().Enter(map('WaterfallVillageCapital'));assert(call.transition[2]=='reverie_centre' and SV.Destiny.PassageQuartier.x==1080 and SV.Destiny.PassageQuartier.y==1360)
-- Une ancienne sauvegarde sur la frontière ne se fait pas téléporter.
SV={Destiny={VisiteVille='terminee'}};player.Position.X=776;player.Position.Y=832;call.transition=nil;load().Enter(map('WaterfallVillageCapital'));assert(not call.transition and player.Position.X==776 and player.Position.Y==832)
-- Un chargement installe uniquement les escaliers correspondant au quartier.
SV={Destiny={VisiteVille='terminee'}};player.Position.X=800;player.Position.Y=1160;local m=map('reverie_centre');load().GameLoad(m)
assert(m.objects.EscalierN1VersNord and m.objects.EscalierN2VersNord and m.objects.EscalierN3VersNord and m.objects.EscalierSVersResidentiel)
assert(not m.objects.EscalierN1VersCentre and not m.objects.EscalierPVersEtang)
print('PASS changements de quartier, retours, ancienne sauvegarde sur frontière et pose des capteurs (doublures)')
