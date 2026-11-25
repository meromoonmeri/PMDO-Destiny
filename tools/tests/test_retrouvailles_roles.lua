-- Régression isolée, sans ressources ni rendu PMDO : exécute les vrais modules Lua.
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
package.preload['origin.common'] = function() return {} end
package.preload['destiny.recrutement'] = function() return {synchroniser=function() end} end
local dialogues, frames = {}, {}
local speaker = nil
package.preload['destiny.cinematique'] = function()
  return {
    Dire=function(actor, emotion, text) speaker=actor; table.insert(dialogues, {actor=actor, text=text}) end,
    Respirer=function(n) GAME:WaitFrames(n or 20) end,
    TournerGroupe=function() end, RegarderGroupe=function() end,
    Emote=function() end, NomEspece=function(_,fallback) return fallback end,
  }
end
local noop = function() end
local hero = {Nickname='Héros initial', BaseForm={Species='hero_species', Gender=0}, data={Importance='Hero'}}
local partner = {Nickname='Luna', BaseForm={Species='partner_species', Gender=0}, data={Importance='Partner'}}
local third = {Nickname='Autre', data={}}
local party, leader = {partner,hero}, 1
local actors = {PLAYER={Data=hero, Position={X=0,Y=0}}, Teammate1={Data=partner, Position={X=0,Y=0}}}
local input = 'Alex'
local menu = nil
SV = {Destiny={}}
Direction = {Up=0,Down=4,Left=6,Right=2,UpRight=1,UpLeft=7,DownRight=3,DownLeft=5}
Gender = {Female=1}
RogueEssence = {Data={GameProgress={DungeonStakes={Risk=2}}}}
LTBL = function(ch) return ch and ch.data end
CH = function(n) return actors[n] end
MRKR = function(n)
 if n=='reveil' then return {Position={X=376,Y=240}} end
 if n=='entrance' then return {Position={X=384,Y=560}} end
 return {Position={X=500,Y=500}}
end
GAME = setmetatable({
 GetPlayerPartyCount=function() return #party end,
 GetPlayerPartyMember=function(_,i) return assert(party[i+1]) end,
 GetTeamLeaderIndex=function() return leader end,
 WaitFrames=function(_,n) table.insert(frames,n) end,
 SetCharacterNickname=function(_,member,name) member.Nickname=name end,
 EnterDungeon=function() SV.started=true end,
}, {__index=function() return noop end})
GROUND = setmetatable({
 TeleportTo=function(_,ch,x,y) ch.Position={X=x,Y=y} end,
 MoveToPosition=function(_,ch,x,y) ch.Position={X=x,Y=y} end,
}, {__index=function() return noop end})
UI = setmetatable({
 NameMenu=function() menu='name' end,
 ResetSpeaker=function() speaker=nil end,
 ChoiceMenuYesNo=function(_,question)
  if question == 'Souhaitez-vous retourner dans les Bois Perdus ?' or question == 'Le suivre jusqu’à Réverie Town ?' then
   assert(speaker==nil, 'une question système a hérité d’un portrait')
  end
  menu='yesno'
 end,
 ChoiceResult=function() if menu=='name' then return input end return true end,
}, {__index=function() return noop end})
SOUND = setmetatable({}, {__index=function() return noop end})
AI = setmetatable({}, {__index=function() return noop end})
TASK = {BranchCoroutine=function(_,fn) fn(); return {} end,JoinCoroutines=noop}
_DATA = {GetMonster=function(_,species)
 return {Name={ToLocal=function() return species=='hero_species' and 'Espèce héros' or 'Espèce partenaire' end}}
end}
local equipe = require 'destiny.equipe_scene'
local reveil = require 'destiny.ground.reveil_nuit.init'
local function role(role, expected, expected_index)
 local got, index = equipe.Membre(role)
 assert(got == expected and index == expected_index, role..' mal identifié')
end
-- Ordre réel après sortie de la réserve, puis ordre initial et recrue.
role('Hero',hero,1);role('Partner',partner,0)
party={hero,partner};leader=0;role('Hero',hero,0);role('Partner',partner,1)
party={third,partner,hero};leader=2;role('Hero',hero,2);role('Partner',partner,1)
-- Replis anciennes sauvegardes, un rôle marqué ou aucun, seulement à deux.
party={partner,hero};leader=1;hero.data={};role('Hero',hero,1);role('Partner',partner,0)
partner.data={};role('Hero',hero,1);role('Partner',partner,0)
party={hero,partner};leader=0;role('Hero',hero,0);role('Partner',partner,1)
party={hero,partner,third};assert(equipe.Membre('Hero')==nil and equipe.Membre('Partner')==nil)
party={hero,partner};hero.data={Importance='Hero'};partner.data={Importance='Hero'}
assert(equipe.Membre('Hero')==nil and equipe.Membre('Partner')==nil)
-- Retour au cas normal : les deux rôles, inversés, noms réellement saisis.
hero.data={Importance='Hero'};partner.data={Importance='Partner'}
party={partner,hero};leader=1;dialogues={};frames={};SV={Destiny={}}
reveil.CinematiqueRetrouvailles()
assert(hero.Nickname=='Alex' and partner.Nickname=='Luna')
assert(SV.Destiny.RetrouvaillesFaites and SV.started)
local presentation, reponse = false, false
for _,d in ipairs(dialogues) do
 if d.text == 'Je m’appelle Luna !' then presentation = d.actor == actors.Teammate1 end
 if d.text == '« Alex »… ! C’est un joli prénom !' then reponse = d.actor == actors.Teammate1 end
end
assert(presentation and reponse)
-- Nom vide : repli espèce du héros, jamais du partenaire.
hero.Nickname='Avant';partner.Nickname='Luna';input='';dialogues={};SV={Destiny={}}
reveil.CinematiqueRetrouvailles()
assert(hero.Nickname=='Espèce héros' and partner.Nickname=='Luna')
-- Un joueur peut choisir volontairement le même prénom : ne pas interdire ce choix.
hero.Nickname='Avant';partner.Nickname='Luna';input='Luna';dialogues={};SV={Destiny={}}
reveil.CinematiqueRetrouvailles()
assert(hero.Nickname=='Luna' and partner.Nickname=='Luna')
-- Identité incohérente : ne jamais appliquer le nom au mauvais objet.
hero.data={Importance='Hero'};partner.data={Importance='Hero'}
hero.Nickname='Conservé';partner.Nickname='Luna';input='Alex';SV={Destiny={}}
reveil.CinematiqueRetrouvailles()
assert(hero.Nickname=='Conservé' and partner.Nickname=='Luna' and not SV.started)
-- Si le héros marqué n'est pas le leader affiché, ne pas renommer non plus.
hero.data={Importance='Hero'};partner.data={Importance='Partner'};leader=0
hero.Nickname='Conservé';partner.Nickname='Luna';SV={Destiny={}}
reveil.CinematiqueRetrouvailles()
assert(hero.Nickname=='Conservé' and partner.Nickname=='Luna' and not SV.started)

-- Exécuter aussi la scène de jour jusqu'au départ de Bekipan, avec des
-- doubles d'acteurs qui enregistrent leur état au moment des mouvements.
hero.data={Importance='Hero'};partner.data={Importance='Partner'}
hero.Nickname='Alex';partner.Nickname='Luna';party={partner,hero};leader=1
actors={PLAYER={Data=hero, Position={X=0,Y=0}}};dialogues={};SV={Destiny={}}
local flight={}
GROUND.RemoveCharacter=function(_,n) actors[n]=nil end
GROUND.CreateCharacterFromCharData=function(_,n,ch,x,y)
 actors[n]={Data=ch,BaseForm=ch.BaseForm,Position={X=x,Y=y}};return actors[n]
end
GROUND.SpawnerDoSpawn=function(_,n)
 if n~='Bekipan' then return nil end
 actors[n]={name=n,Position={X=0,Y=0}};return actors[n]
end
GROUND.Unhide=function(_,n) assert(actors[n].HideShadow==true) end
GROUND.Hide=function(_,n) assert(actors[n].HideShadow==true); actors[n].hidden=true end
GROUND.TeleportTo=function(_,ch,x,y)
 ch.Position={X=x,Y=y}
 if ch.name=='Bekipan' then table.insert(flight,{'teleport',x,y,ch.HideShadow}) end
end
GROUND.MoveToPosition=function(_,ch,x,y)
 ch.Position={X=x,Y=y}
 if ch.name=='Bekipan' then table.insert(flight,{'move',x,y,ch.HideShadow}) end
end
GROUND.AnimateToPosition=function(_,ch,anim,dir,x,y)
 ch.Position={X=x,Y=y};table.insert(flight,{'animate',x,y,ch.HideShadow})
end
local cliff=require 'destiny.ground.cliffdaytest.init'
cliff.RencontreTeamDazzling=function() SV.Destiny.CombatDazzling='en_cours' end
cliff.SceneArriveeDestiny()
assert(#flight==4)
for _,event in ipairs(flight) do assert(event[4]==true, 'ombre visible pendant le vol') end
assert(flight[1][1]=='teleport' and flight[1][2]==656 and flight[1][3]==340)
assert(flight[2][1]=='animate' and flight[2][2]==656 and flight[2][3]==444)
assert(flight[3][1]=='animate' and flight[3][2]==656 and flight[3][3]==390)
assert(flight[4][1]=='move' and flight[4][2]==420 and flight[4][3]==390)
assert(actors.Bekipan.hidden and actors.Bekipan.HideShadow==false)
local salut, presentation_hero = false, false
for _,d in ipairs(dialogues) do
 if d.text:find('Oh tiens, Luna !',1,true) then salut=true end
 if d.text:find('Je te présente Alex !',1,true) then presentation_hero=true end
end
assert(salut and presentation_hero)
print('PASS : rôles, prénoms, retrouvailles et scène de Bekipan simulées ; noms vides et cas ambigus.')
