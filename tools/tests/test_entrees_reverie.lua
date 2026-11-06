-- Régressions avec doublures ; ne remplace pas une partie réelle.
package.preload['origin.common']=function()return {} end
package.preload['origin.menu.skill.SkillSelectMenu']=function()return {} end
package.preload['origin.menu.team.AssemblySelectMenu']=function()return {} end
package.preload['destiny.equipe_scene']=function()return {Suivre=function()end} end
package.preload['destiny.cinematique']=function()return {NomEspece=function(_,n)return n end} end
package.preload['destiny.missions_reverie']=function()return {} end
Direction={Up='Up',Down='Down',Left='Left',Right='Right',UpLeft='UpLeft',UpRight='UpRight',DownLeft='DownLeft'}
Gender={Male='Male',Female='Female',Genderless='Genderless'}
RogueElements={Rect=function(x,y,w,h)return {x=x,y=y,w=w,h=h}end}
RogueEssence={
 Ground={GroundObject=function()return {OnMapInit=function()end,SetTriggerType=function(self,t)self.TriggerType=t end}end,GroundEntity={EEntityTriggerTypes={Touch='Touch',Action='Action'}}},
 Dungeon={BaseMap={ScrollEdge={Clamp='Clamp'}},CharData=function()return {}end,MonsterID=function(species)return {Species=species}end,Character=function(data)return data end},
}
local hero={EntName='PLAYER',Position={X=800,Y=1160},Direction=Direction.Down}
local mate={EntName='Teammate1',Position={X=772,Y=1160},Direction=Direction.Down}
local current
function CH(n)if n=='PLAYER' then return hero elseif n=='Teammate1' then return mate else return current.characters[n] end end
AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end}
GROUND={
 RemoveCharacter=function(_,name)if current.characters[name] then current.characters[name]=nil;return true end;return false end,
 RemoveObject=function(_,name)if current.objects[name] then current.objects[name]=nil;return true end;return false end,
 TeleportTo=function(_,a,x,y,dir)a.Position={X=x,Y=y};a.Direction=dir end,
 EntTurn=function(_,a,dir)a.Direction=dir end,CharEndAnim=function()end,CharTurnToChar=function()end,AddMapStatus=function()end,
 CreateCharacterFromCharData=function(_,name,data,x,y,dir)
  assert(not current.characters[name]);local c={EntName=name,Position={X=x,Y=y},Direction=dir,Data=data,ReloadEvents=function()end};current.characters[name]=c;return c
 end,
}
GAME={GetPlayerPartyCount=function()return 2 end}
local all={
 {'Kecleon','centre'},{'Kecleon_Violet','centre'},{'NewObject_3','centre'},{'NewObject_4','centre'},{'Kangourex','centre'},
 {'NewObject_6','nord'},{'NewObject_7','centre'},{'NewObject_8','centre'},{'NewObject_9','residentiel'},{'NewObject_10','residentiel'},
 {'NewObject_12','centre'},{'NewObject_13','centre'},{'NewObject_14','centre'},{'Doyen','nord'},{'','nord'},{'Drifloon','nord'},
 {'NewObject_16','centre'},{'NewObject_11','residentiel'},{'NewObject_18','centre'},{'NewObject_20','residentiel'},{'NewObject_21','centre'},
 {'NewObject_15','centre'},{'NewObject_17','residentiel'},{'NewObject_22','centre'},{'NewObject_23','centre'},{'NewObject_24','centre'},
 {'Pijako_Livreur','nord'},{'Cradopaud_Pecheur','centre'},{'Roserade_Fleuriste','centre'},{'Magneton_Garde','residentiel'},
 {'Babimanta_Enfant','centre'},{'Goinfrex_Voyageur','centre'},
}
local function newmap(name, include_dynamic)
 local m={AssetName=name,characters={},objects={}}
 for i,e in ipairs(all) do
  if i<=26 or include_dynamic then
   m.characters[e[1]]={EntName=e[1],Position={X=12,Y=12},Direction=Direction.Down,Data={},ReloadEvents=function()end}
  end
 end
 function m:GetMapChar(n)return self.characters[n]end
 function m:FindObject(n)return self.objects[n]end
 function m:AddObject(obj)self.objects[obj.EntName]=obj end
 function m:GetObstacle(x,y)return 0 end
 m.Width=200;m.Height=500
 return m
end
local root=(arg[1] or '.')..'/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'
local function init(m)
 current=m;local ville=assert(loadfile(root))();ville.Init(m);return ville
end
for _,sector in ipairs({'centre','nord','residentiel','etang'}) do
 for _,fullsave in ipairs({true,false}) do
  SV={Destiny={}};local m=newmap('reverie_'..sector,fullsave);local ville=init(m)
  local count=0
  for _,e in ipairs(all) do
   local a=m.characters[e[1]]
   if e[2]==sector then assert(a,'PNJ local manquant : '..sector..' '..e[1]);count=count+1
   else assert(not a,'PNJ étranger conservé : '..sector..' '..e[1])end
  end
  for a,aa in pairs(m.characters) do
   for b,bb in pairs(m.characters) do
    if a < b then
     assert(math.abs(aa.Position.X-bb.Position.X)>=16 or math.abs(aa.Position.Y-bb.Position.Y)>=16,
       'PNJ superposés : '..sector..' '..a..' / '..b)
    end
   end
  end
  assert(hero.Position.X==800 and hero.Position.Y==1160 and mate.Position.X==772 and mate.Position.Y==1160,'équipe déplacée')
  assert(SV.Destiny.PlacementHabitantsReverie[m.AssetName]==true)
  -- Revenir / recharger ne recrée pas de PNJ et ne replace pas un flâneur local.
  local wander=sector=='centre' and m.characters.NewObject_13 or sector=='residentiel' and m.characters.NewObject_11 or nil
  if wander then wander.Position.X=wander.Position.X+8 end
  local oldx=wander and wander.Position.X;ville.Init(m);if wander then assert(wander.Position.X==oldx,'flâneur réinitialisé à chaque entrée')end
  local total=0;for _ in pairs(m.characters) do total=total+1 end;assert(total==count)
  if sector=='centre' then
   assert(m.objects.SortieCarrefour and m.objects.SortieExplorationE2 and m.objects.TableauReverieCentre)
   assert(not m.objects.TableauReverieNord and not m.objects.PortePosteBekipan)
  elseif sector=='nord' then
   assert(not m.objects.SortieCarrefour and not m.objects.SortieExplorationE2 and m.objects.TableauReverieNord and m.objects.PortePosteBekipan)
   assert(not m.objects.TableauReverieCentre)
  else assert(not m.objects.SortieCarrefour and not m.objects.SortieExplorationE2) end
  print('PASS '..sector..' : '..count..' habitants locaux ; état '..(fullsave and 'ancienne sauvegarde' or 'carte native'))
 end
end
-- La carte historique reste complète pour la visite et les anciennes entrées.
SV={Destiny={}};local legacy=newmap('WaterfallVillageCapital',true);init(legacy)
for _,e in ipairs(all)do assert(legacy.characters[e[1]],'PNJ perdu de la carte historique') end
print('PASS carte historique préservée ; équipe conservée')

local call={}
GAME.FadeOut=function()end;GAME.FadeIn=function()end;GAME.MoveCamera=function()end;GAME.CutsceneMode=function()end
GAME.EnterGroundMap=function(_,...)call.transition={...}end
GAME.EnterZone=function(_,...)call.zone={...}end
SOUND={PlayBGM=function()end};COMMON={CreateWalkArea=function()end}
local doors={
 {'PortePosteBekipan','reverie_nord','reverie_post_office','entrance_south',56,504,32,8,80,528,56,528},
 {'PorteCitrouilleNordOuest','reverie_nord','reverie_inn','Main_Entrance_Marker',400,592,48,8,432,616,408,616},
 {'PorteHutteNordEst','reverie_nord','reverie_water_home','Main_Entrance_Marker',1048,648,32,8,1064,680,1040,680},
 {'PorteDojoKingambit','reverie_nord','dojo_kingambit','MarowakDojoExitMarker',1440,392,48,8,1460,416,1436,416},
 {'PorteHutteSud','reverie_centre','reverie_hutte_aquatique','Main_Entrance_Marker',648,1720,32,8,656,1744,680,1744},
 {'PorteMaisonPierre','reverie_residentiel','reverie_rock_home','Main_Entrance_Marker',448,2336,32,8,456,2360,472,2344},
 {'PorteMaisonPlanteSud','reverie_residentiel','reverie_grass_home','Main_Entrance_Marker',576,2544,24,8,584,2568,560,2568},
 {'PorteCitrouilleSud','reverie_residentiel','reverie_fire_home','Main_Entrance_Marker',760,2528,40,8,776,2552,752,2552},
}
for _,d in ipairs(doors) do
 SV={Destiny={VisiteVille='terminee'}};hero.Position={X=800,Y=1160};mate.Position={X=772,Y=1160};call.transition=nil
 local m=newmap(d[2],false)
 -- Une sauvegarde d'avant la correction porte encore l'objet Action.
 m.objects[d[1]]={EntName=d[1],TriggerType='Action'}
 local ville=init(m);local obj=m.objects[d[1]];assert(obj and obj.TriggerType=='Touch' and obj.Passable==false,d[1])
 assert(obj.Collider.x==d[5] and obj.Collider.y==d[6] and obj.Collider.w==d[7] and obj.Collider.h==d[8])
 ville[d[1]..'_Touch'](obj,mate);assert(call.transition==nil,'un partenaire ouvre la porte')
 ville[d[1]..'_Touch'](obj,hero);assert(call.transition[1]=='town02_waterfallvillage' and call.transition[2]==d[3] and call.transition[3]==d[4],d[1])
 local b=SV.Destiny.RetourBatimentPartenaire;assert(SV.Destiny.RetourBatimentX==d[9] and SV.Destiny.RetourBatimentY==d[10] and b.px==d[11] and b.py==d[12]);call.transition=nil
 ville[d[1]..'_Touch'](obj,hero);assert(call.transition==nil,'double déclenchement')
 -- Sortie de l'intérieur : la carte historique redirige dans le bon quartier.
 SV.Destiny.ArriveeVille='batiment';local old=newmap('WaterfallVillageCapital',true);current=old
 ville.Enter(old);assert(call.transition and call.transition[2]==d[2]);local passage=SV.Destiny.PassageQuartier
 assert(passage.x==d[9] and passage.y==d[10] and passage.px==d[11] and passage.py==d[12],d[1]..' retour')
 local dst=newmap(d[2],false);ville=init(dst);ville.Enter(dst)
 assert(hero.Position.X==d[9] and hero.Position.Y==d[10] and mate.Position.X==d[11] and mate.Position.Y==d[12],d[1]..' équipe')
 print('PASS entrée et retour simulés '..d[1])
end
-- Un retour extérieur (E2 ou guilde) ne réutilise pas la position d'un partenaire mémorisée pour un autre bâtiment.
SV={Destiny={VisiteVille='terminee',ArriveeVille='batiment',RetourBatimentX=1552,RetourBatimentY=1600,RetourBatimentPartenaire={x=80,y=528,px=56,py=528}}};call.transition=nil
local old=newmap('WaterfallVillageCapital',true);current=old;local ville=assert(loadfile(root))();ville.Enter(old)
assert(SV.Destiny.PassageQuartier.px==1524 and SV.Destiny.PassageQuartier.py==1600)
-- Café : contact direct, pas de dialogue ; sortie peut être empruntée plusieurs fois.
SV={Destiny={VisiteVille='terminee'}};local m=newmap('reverie_centre',false);ville=init(m);local obj=m.objects.PorteCafeSpinda
assert(obj.TriggerType=='Touch' and obj.Collider.y==1344);call.zone=nil;ville.PorteCafeSpinda_Touch(obj,mate);assert(not call.zone)
ville.PorteCafeSpinda_Touch(obj,hero);assert(call.zone and call.zone[3]==2);call.zone=nil;ville.PorteCafeSpinda_Touch(obj,hero);assert(not call.zone)
local cafe=assert(loadfile((arg[1] or '.')..'/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
SV={Destiny={}};local c=newmap('caféspindaaccueil',false);current=c;call.zone=nil;cafe.Init(c);assert(c.objects.PorteSortieCafe.TriggerType=='Touch')
cafe.PorteSortieCafe_Touch(nil,mate);assert(not call.zone);cafe.PorteSortieCafe_Touch(nil,hero);assert(call.zone and call.zone[3]==0 and SV.Destiny.ArriveeVille=='cafe')
call.zone=nil;cafe.PorteSortieCafe_Touch(nil,hero);assert(not call.zone);cafe.Enter(c);cafe.PorteSortieCafe_Touch(nil,hero);assert(call.zone)
-- Les coques gardent la sortie réutilisable, même si Lua garde le module chargé.
for _,e in ipairs({{'reverie_post_office','South_Exit'},{'reverie_inn','Inn_Entrance'},{'reverie_water_home','Water_Home_Entrance'},{'reverie_rock_home','Rock_Home_Entrance'},{'reverie_grass_home','Grass_Home_Entrance'},{'reverie_fire_home','Fire_Home_Entrance'},{'ledian_dojo','Dojo_Exit'}})do
 local t=assert(loadfile((arg[1] or '.')..'/game/Data/Script/destiny/ground/'..e[1]..'/init.lua'))();SV={Destiny={}};call.zone=nil
 t[e[2]..'_Touch']();assert(call.zone);call.zone=nil;t[e[2]..'_Touch']();assert(not call.zone)
 t.Enter({});t[e[2]..'_Touch']();assert(call.zone,'sortie non réinitialisée '..e[1])
end
print('PASS garde, états anciens, café et sorties répétées (doublures)')
