-- Scénarios autonomes sur doubles d'API : cycle, réussite, échec et récompense.
local root=(arg[1] or '.')..'/game/Data/Script/destiny/'
package.preload['origin.common']=function() return {} end
package.preload['destiny.recrutement']=function() return {synchroniser=function() end} end
local bank, unlocked, calls = 0, false, {}
SV={Destiny={}};GAME={DungeonUnlocked=function(_,zone)assert(zone=='lost_wood');return unlocked end,UnlockDungeon=function(_,zone)assert(zone=='lost_wood');unlocked=true end,AddToPlayerMoneyBank=function(_,money)bank=bank+money end,SetRescueAllowed=function()end,EndDungeonRun=function()end,EnterZone=function(_,...)calls.zone={...} end}
UI={WaitShowDialogue=function(_,s)calls.last=s end,ResetSpeaker=function()end,BeginChoiceMenu=function()end,WaitForChoice=function()end,ChoiceMenuYesNo=function()end,ChoiceResult=function()return true end}
RogueEssence={Data={GameProgress={ResultType={Cleared='Cleared',Downed='Downed',Failed='Failed'}}}}
local missions=assert(loadfile(root..'missions_reverie.lua'))();package.preload['destiny.missions_reverie']=function()return missions end
assert(missions.Jour()==0 and not missions.OffreDisponible());SV.Destiny.RetourAccompli=true
assert(missions.OffreDisponible() and unlocked and missions.Accepter());assert(not missions.OffreDisponible() and not missions.Accepter());assert(missions.Actuelle().Etat=='en_cours')
assert(not missions.Completer('ailleurs',true) and not missions.Completer('lost_wood',false));assert(not missions.Reclamer() and bank==0)
SV.Destiny.JourneeVille=1;assert(missions.Actuelle().Etat=='en_cours' and not missions.OffreDisponible())
local lost=assert(loadfile(root..'zone/lost_wood/init.lua'))();SV.Destiny.LostWoodTrip='termine';SV.Destiny.ExplorationReverie=true;lost.ExitSegment(nil,'Downed',false,0,0);assert(missions.Actuelle().Etat=='en_cours' and SV.Destiny.LostWoodTrip=='termine')
SV.Destiny.ExplorationReverie=true;lost.ExitSegment(nil,'Cleared',false,0,0);assert(missions.Actuelle().Etat=='reussie' and SV.Destiny.LostWoodTrip=='termine' and calls.zone[1]=='town02_waterfallvillage')
assert(missions.Reclamer());assert(bank==300 and missions.Actuelle()==nil and not missions.Reclamer() and bank==300);assert(missions.OffreDisponible() and missions.Accepter());assert(not missions.OffreDisponible());missions.Completer('lost_wood',true);assert(missions.Reclamer() and bank==600 and not missions.OffreDisponible())
SV.Destiny.JourneeVille=2;assert(missions.OffreDisponible());missions.LireGazette();assert(calls.last and string.find(calls.last,'Bois Perdus',1,true))
print('PASS : mission quotidienne débloquée, acceptation, échec, réussite, récompense unique, renouvellement et gazette (doubles).')
