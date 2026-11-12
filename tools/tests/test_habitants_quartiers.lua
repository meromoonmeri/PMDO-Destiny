package.preload['destiny.meteo_reverie']=function()return assert(loadfile((arg[1] or '.')..'/game/Data/Script/destiny/meteo_reverie.lua'))()end
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
 Ground={GroundObject=function()return {OnMapInit=function()end,SetTriggerType=function()end}end,GroundEntity={EEntityTriggerTypes={Touch='Touch',Action='Action'}}},
 Dungeon={BaseMap={ScrollEdge={Clamp='Clamp'}},CharData=function()return {}end,MonsterID=function(species)return {Species=species}end,Character=function(data)return data end},
}
local hero={EntName='PLAYER',Position={X=800,Y=1160},Direction=Direction.Down}
local mate={EntName='Teammate1',Position={X=772,Y=1160},Direction=Direction.Down}
local current
function CH(n)if n=='PLAYER' then return hero elseif n=='Teammate1' then return mate else return current.characters[n] end end
AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end}
GROUND={
 Unhide=function(_,n)if current.characters[n] then current.characters[n].EntEnabled=true end end,
 Hide=function(_,n)if current.characters[n] then current.characters[n].EntEnabled=false end end,
 RemoveCharacter=function(_,name)if current.characters[name] then current.characters[name]=nil;return true end;return false end,
 RemoveObject=function(_,name)if current.objects[name] then current.objects[name]=nil;return true end;return false end,
 TeleportTo=function(_,a,x,y,dir)a.Position={X=x,Y=y};a.Direction=dir end,
 EntTurn=function(_,a,dir)a.Direction=dir end,CharEndAnim=function()end,CharTurnToChar=function()end,AddMapStatus=function()end,RemoveMapStatus=function()end,
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
 {'Babimanta_Enfant','centre'},{'Goinfrex_Voyageur','centre'},{'Bellossom_Boutique','centre'},
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
   if e[2]==sector or ((sector=='centre' or sector=='nord') and (e[2]=='centre' or e[2]=='nord')) then assert(a,'PNJ local manquant : '..sector..' '..e[1]);count=count+1
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
  if sector=='centre' or sector=='nord' then
   assert(m.objects.SortieCarrefour and m.objects.SortieExplorationE2 and m.objects.TableauReverieCentre and m.objects.TableauReverieNord and m.objects.PortePosteBekipan)
  else assert(not m.objects.SortieCarrefour and not m.objects.SortieExplorationE2) end
  print('PASS '..sector..' : '..count..' habitants locaux ; état '..(fullsave and 'ancienne sauvegarde' or 'carte native'))
 end
end
-- La carte historique reste complète pour la visite et les anciennes entrées.
SV={Destiny={}};local legacy=newmap('WaterfallVillageCapital',true);init(legacy)
for _,e in ipairs(all)do assert(legacy.characters[e[1]],'PNJ perdu de la carte historique') end
print('PASS carte historique préservée ; équipe conservée')

SV={Destiny={AlerteShinx='a_secourir',LuxrayAttente='place'}}
local centre=newmap('reverie_centre',true); local ville=init(centre)
local lux=centre.characters.Luxray_Alerte
assert(lux and lux.Position.X==800 and lux.Position.Y==1224 and lux.Data.Nickname=='Lyra' and not centre.characters.NewObject_9)
ville.Init(centre);assert(centre.characters.Luxray_Alerte==lux)
SV.Destiny.LuxrayAttente='sortie';ville.Init(centre);assert(lux.Position.X==1504 and lux.Position.Y==1584 and lux.Data.Nickname=='Lyra')
local residentiel=newmap('reverie_residentiel',true);current=residentiel;ville.Init(residentiel)
assert(not residentiel.characters.Luxray_Alerte and residentiel.characters.NewObject_9.EntEnabled==false and residentiel.characters.NewObject_9.Data.Nickname=='Lyra' and residentiel.characters.NewObject_10.Data.Nickname=='Léo')
SV.Destiny.AlerteShinx='termine';ville.Init(residentiel);assert(residentiel.characters.NewObject_9.EntEnabled==true)
current=centre;ville.Init(centre);assert(not centre.characters.Luxray_Alerte)
print('PASS attente de Lyra : états persistants, réentrée, doublons et quartier résidentiel')
