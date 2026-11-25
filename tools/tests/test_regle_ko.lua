local script, zones = ...
SINGLE_CHAR_SCRIPT = {}
local party, guests, effects, frames = {}, {}, {}, 0
LTBL = function(c) return c.role end
GAME = {
 GetPlayerPartyCount=function() return #party end,
 GetPlayerGuestCount=function() return #guests end,
 GetPlayerPartyMember=function(_, i) return party[i+1] end,
 GetPlayerGuestMember=function(_, i) return guests[i+1] end,
 WaitFrames=function(_, n) frames=frames+n end,
}
_DUNGEON={ProcessBattleFX=function(_, a,b,fx) assert(a==b and fx=='sendhome'); effects[#effects+1]=a; return a end}
_DATA={SendHomeFX='sendhome'}
TASK={WaitTask=function(_, task) assert(task~=nil) end}
assert(loadfile(script))()
local run=SINGLE_CHAR_SCRIPT.DestinyVerifierKO
local function new(ko, p, f, role) return {Dead=ko, IsPartner=p or false, IsFounder=f or false, role=role and {Importance=role} or nil} end
local function setup(p,g) party=p;guests=g or {};effects={};frames=0 end
local function check(v) run(nil,nil,{User=v},{}) end
-- héros ou partenaire, indices arbitraires et recrue vivante
for id=1,2 do
 local hero, partner, recruit = new(false,true),new(false,true),new(false)
 local arr = id==1 and {hero,partner,recruit} or {partner,recruit,hero}
 setup(arr); local dead=id==1 and hero or partner;dead.Dead=true;check(dead)
 assert(hero.Dead and partner.Dead and recruit.Dead and #effects==2 and frames==120)
end
-- Un KO ordinaire ne cause pas la fin, même si un protagoniste est présent.
local h,p,r=new(false,true),new(false,true),new(true)
setup({h,p,r});check(r);assert(not h.Dead and not p.Dead and #effects==0)
-- Un ennemi marqué ne déclenche jamais l'évacuation.
local enemy=new(true,true);setup({h,p});check(enemy);assert(not h.Dead and not p.Dead and #effects==0)
-- La réanimation réussie remet Dead à false avant cet événement.
local revived=new(false,true); setup({revived,p});check(revived);assert(not revived.Dead and not p.Dead and #effects==0)
-- invité indispensable, invité ordinaire, présence d'un héros seul.
local guest=new(true,true);h=new(false,true);p=new(false);setup({h,p},{guest});check(guest);assert(h.Dead and p.Dead and #effects==2)
h=new(false,true);guest=new(true);setup({h},{guest});check(guest);assert(not h.Dead and #effects==0)
h=new(true,true);setup({h});check(h);assert(h.Dead and #effects==0)
-- Rôles explicites ou ancien marqueur fondateur sans IsPartner.
for _,v in ipairs({new(true,false,true),new(true,false,false,'Hero'),new(true,false,false,'Partner')}) do
 p=new(false);setup({v,p});check(v);assert(p.Dead and #effects==1)
end
-- Les invités survivants sont évacués, déjà K.O. non ré-animés.
h=new(true,true);p=new(false,true);guest=new(false);local old=new(true);setup({h,p},{guest,old});check(h);assert(p.Dead and guest.Dead and #effects==2)
setup({},{});check(new(true,true));run(nil,nil,nil,{});run(nil,nil,{},{});assert(#effects==0)
-- Exercices des vrais scripts de sortie sur les deux résultats de K.O.
package.preload['origin.common']=function() return {} end
package.preload['destiny.recrutement']=function() return {synchroniser=function()end} end
package.preload['destiny.missions_reverie']=function() return {Completer=function()end} end
RogueEssence={Data={GameProgress={ResultType={Cleared='cleared',Failed='failed',Downed='downed'}}}}
GAME.SetRescueAllowed=function()end
local ended,enter
GAME.EndDungeonRun=function(_,...)ended={...}end
GAME.EnterZone=function(_,...)enter={...}end
SV={Destiny={}}
local fight=assert(loadfile(zones..'/dazzling_fight/init.lua'))()
for _,res in ipairs({'failed','downed'}) do fight.ExitSegment(nil,res,false,0,0); assert(SV.Destiny.CombatDazzling=='defaite' and ended[1]==res and enter[1]=='destiny_cliff_tests') end
fight.ExitSegment(nil,'cleared',false,0,0);assert(SV.Destiny.CombatDazzling=='victoire')
local lost=assert(loadfile(zones..'/lost_wood/init.lua'))()
for _,res in ipairs({'failed','downed'}) do
 SV.Destiny={LostWoodTrip='aller'};lost.ExitSegment(nil,res,false,0,0);assert(SV.Destiny.LostWoodCause=='ko' and enter[1]=='destiny_cliff_tests' and enter[3]==1)
 SV.Destiny={LostWoodTrip='retour'};lost.ExitSegment(nil,res,false,1,0);assert(SV.Destiny.LostWoodCause=='ko' and enter[1]=='reverie' and enter[3]==10)
 SV.Destiny={ExplorationReverie=true};lost.ExitSegment(nil,res,false,0,0);assert(SV.Destiny.ExplorationReverie==nil and enter[1]=='town02_waterfallvillage')
end
print('PASS doubles Lua : héros/partenaire/ancien fondateur, invité, recrue, ennemi, réanimation simulée et sorties scénarisées')
