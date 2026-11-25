-- Doubles de déplacement/menus, y compris le remplacement de SV au retour d'un duel sans enjeu.
local root = arg[1]
local gestes,acteurs,pages,ajouts={}, {}, {}, {}
local attendu, prochain, retour, segment, choix, sac_max = nil, nil, nil, nil, 2, 2
local d={VisiteVille='terminee',AlerteShinx='termine'}
SV={Destiny=d}
local hero={EntName='PLAYER', Position={X=680,Y=2340}}
acteurs.PLAYER=hero
function CH(id) return acteurs[id] end
Direction={Up=4,Down=0,Left=2,Right=6}
Gender={Female=2,Male=1}
local R={Cleared=2,Downed=0,Failed=1,GaveUp=5}
RogueEssence={Data={GameProgress={ResultType=R,DungeonStakes={None=0}}},Dungeon={
  CharData=function() return {} end, Character=function(data) return data end,
  MonsterID=function(a,b,c,g) return {a,b,c,g} end,
  InvItem=function(id) return {GetDisplayName=function() return id end} end,
}}
local nb, max_stack = 0, 1
_DATA={GetItem=function() return {MaxStack=max_stack} end,Save={ActiveTeam={GetMaxInvSlots=function() return sac_max end}}}
_ZONE={CurrentZoneID='town02_waterfallvillage',CurrentMapID={ID=21},CurrentZone={}}
local function dire(a,_,t) pages[#pages+1]={a.EntName,t}; if attendu ~= nil then assert(a.EntName==attendu) end end
package.loaded['destiny.cinematique']={Dire=dire,RegarderGroupe=function(a) gestes[#gestes+1]=a end,Respirer=function(n) gestes[#gestes+1]=n end}
package.preload['origin.common']=function() end
for _, module in ipairs({'suivi_interieurs','equipe_scene','meteo_reverie'}) do package.loaded['destiny.'..module]={} end
AI={DisableCharacterAI=function(_,a) a.ai=false end}
local created, stops=0,0
GROUND={
  CreateCharacterFromCharData=function(_,id,data,x,y,dir)
    local a={EntName=id,Position={X=x,Y=y},Direction=dir,ReloadEvents=function(self) self.reload=true end,Data=data}
    acteurs[id]=a;created=created+1;return a
  end,
  CharEndAnim=function(_,a) a.marche=false end,
  MoveToPosition=function(_,a,x,y) a.Position={X=x,Y=y} end,
  TeleportTo=function(_,a,x,y,dir) a.Position={X=x,Y=y};a.Direction=dir end,
  RemoveCharacter=function(_,id) acteurs[id]=nil end,
  EntTurn=function(_,a,dir) a.Direction=dir end,
  CharTurnToChar=function() end,
}
TASK={
  StartEntityTask=function(_,a,f) prochain=f;a.marche=true;return {} end,
  StopEntityTask=function(_,a) prochain=nil; stops=stops+1 end,
}
GAME={
  GetPlayerBagCount=function() return nb end,
  GetPlayerBagItem=function() return {ID='berry_oran',Amount=nb,Cursed=false} end,
  GivePlayerItem=function(_,id) ajouts[#ajouts+1]=id;nb=nb+1 end,
  FadeOut=function() end,
  EnterDungeon=function(_,...) segment={...} end,
  EndDungeonRun=function(_,...) retour={...};SV={Destiny={ItinerantsReverie={DuelEnCours=SV.Destiny.ItinerantsReverie.DuelEnCours}}} end,
  EnterZone=function(_,...) gestes[#gestes+1]={...} end,
  SetRescueAllowed=function(_,ok) assert(ok==false) end,
}
SOUND={PlayBattleSE=function() end, PlayFanfare=function() end}
UI={
  ResetSpeaker=function(self) self.acteur=nil end, SetSpeaker=function(self,a) self.acteur=a end,
  SetSpeakerEmotion=function() end,
  WaitShowDialogue=function(self,t) pages[#pages+1]={self.acteur and self.acteur.EntName or 'UI',t} end,
  BeginChoiceMenu=function(_,_,_,defaut) assert(defaut==2) end,
  WaitForChoice=function() end, ChoiceResult=function() return choix end,
}
local m={AssetName='reverie_centre', GetMapChar=function(_,id) return acteurs[id] end, GetObstacle=function() return 0 end}
local lib = require 'destiny.reverie_itinerants'
local c={};lib.Brancher(c)
local libre=function(_,_,x,y) return x~=648 or y~=1408 end
lib.Installer(m,libre)
local mira=CH('Itinerant_Mirabelle'); assert(mira and mira.Position.X==552 and mira.reload and not mira.ai and created==1)
assert(CH('Itinerant_Liane')==nil)
for _=1,40 do lib.Update(true) end
assert(prochain~=nil and mira.marche)
-- Intercepter la marche : ni action résiduelle, ni translation pendant les pages.
local xm=mira.Position.X
sac_max=0;c.Itinerant_Mirabelle_Action(mira,hero);assert(stops==1 and not prochain and mira.Position.X==xm and #ajouts==0)
sac_max=16;c.Itinerant_Mirabelle_Action(mira,hero);assert(ajouts[1]=='berry_oran')
lib.Installer(m,libre);c.Itinerant_Mirabelle_Action(mira,hero);assert(#ajouts==1 and created==1)
for _=1,60 do lib.Update(true) end
assert(prochain~=nil);prochain();assert(mira.Position.X~=xm)
-- Un ancien enregistrement peut encore contenir un acteur devenu indisponible.
d.AlerteShinx='a_secourir';lib.Installer(m,libre);assert(CH('Itinerant_Mirabelle')==nil)
d.AlerteShinx='termine';m.AssetName='reverie_etang';lib.Installer(m,libre)
local t=CH('Itinerant_Tilleul');c.Itinerant_Tilleul_Action(t,hero);assert(ajouts[2]=='food_apple')
m.AssetName='reverie_residentiel';lib.Installer(m,libre)
local su,li=CH('Itinerant_Sureau'),CH('Itinerant_Liane');assert(su and li)
c.Itinerant_Sureau_Action(su,hero);c.Itinerant_Sureau_Action(su,hero);assert(pages[#pages][2]:find('Nilo',1,true))
choix=2;c.Itinerant_Liane_Action(li,hero);assert(segment==nil and not d.ItinerantsReverie.DuelEnCours)
choix=nil;c.Itinerant_Liane_Action(li,hero);assert(segment==nil)
choix=1;c.Itinerant_Liane_Action(li,hero);assert(segment[1]=='reverie_duel' and segment[5]==0 and segment[6]==false and segment[7]==true and retour==nil)
local duel=require 'destiny.zone.reverie_duel.init';duel.EnterSegment(nil);duel.ExitSegment(nil,R.Cleared)
assert(retour[1]==R.Cleared and retour[2]=='town02_waterfallvillage' and retour[4]==21)
assert(SV.Destiny.ItinerantsReverie.DuelRemporte and SV.Destiny.ItinerantsReverie.DernierDuel=='victoire')
assert(SV.Destiny.PassageQuartier.x==680 and SV.Destiny.PassageQuartier.y==2340)
for _, res in ipairs({{R.Downed,'defaite'},{R.GaveUp,'abandon'}}) do
  SV.Destiny.ItinerantsReverie.DuelEnCours={carte=21,x=850,y=2580}
  duel.ExitSegment(nil,res[1]);assert(retour[1]==res[1] and SV.Destiny.PassageQuartier.x==850 and SV.Destiny.ItinerantsReverie.DernierDuel==res[2])
end
SV.Destiny.ItinerantsReverie.DuelEnCours={};lib.AnnulerDuelInterrompu();assert(SV.Destiny.ItinerantsReverie.DuelEnCours==nil)
lib.Quitter()
print('PASS arrêt/reprise, sac plein, cadeaux persistants, refus du duel, retour des trois résultats.')
local cafe = assert(loadfile(root..'/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
acteurs['Okéoké']={EntName='Okéoké'};acteurs['Qulbutoqué']={EntName='Qulbutoqué'}
for _, id in ipairs({'Okéoké','Qulbutoqué'}) do
  pages={};cafe[id..'_Action'](CH(id),hero)
  assert(pages[1][1]==id and #pages>=4)
  local compte, ferme=0,false
  for _,p in ipairs(pages) do
    if p[1]=='Qulbutoqué' then assert(p[2]=='Banco !');compte=compte+1 end
    if p[1]=='Okéoké' and p[2]:find('déballer les caisses',1,true) then ferme=true end
  end
  assert(compte==2 and ferme and UI.acteur==nil and CH('Okéoké').Direction==Direction.Right and CH('Qulbutoqué').Direction==Direction.Left)
end
print('PASS les deux entrées de dialogue : Bulle relance, Balou dit Banco, bourse fermée.')
