-- Doubles d'acteurs : aucun moteur graphique, aucune sauvegarde réelle.
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
local hero={data={Importance='Hero'}}
local partner={data={Importance='Partner'}}
local extra={data={Importance='Other'}}
local party={hero,partner};local leader=0
local actors={PLAYER={Position={X=80,Y=80},Direction=0}}
local created,followed,removed=0,0,0
CH=function(n) return actors[n] end
LTBL=function(c) return c.data end
GAME={GetPlayerPartyCount=function() return #party end,
      GetPlayerPartyMember=function(_,i) return party[i+1] end,
      GetTeamLeaderIndex=function() return leader end}
GROUND={CreateCharacterFromCharData=function(_,name,ch,x,y,d)
  created=created+1;actors[name]={Data=ch,Position={X=x,Y=y},Direction=d};return actors[name]
end,RemoveCharacter=function(_,name) removed=removed+1;actors[name]=nil end}
AI={DisableCharacterAI=function()end,SetCharacterAI=function(_,ch,ai,target)
  assert(ai=='origin.ai.ground_partner' and target==actors.PLAYER);followed=followed+1
end, EnableCharacterAI=function()end}
local obstacles={};local map={TexWidth=30,TexHeight=30,GetObstacle=function(_,x,y) return obstacles[x..','..y] or 0 end}
local suivi=require 'destiny.suivi_interieurs'
-- Entrée normale, répétition et rechargement : un seul acteur créé.
suivi.Activer(map);assert(created==1 and followed==1 and actors.Teammate1.Data==partner)
suivi.Activer(map);assert(created==1 and followed==2 and removed==0)
-- L'absence de partenaire ne doit pas créer un personnage.
actors.Teammate1=nil;party={hero};suivi.Activer(map);assert(created==1)
-- Partenaire leader : aucune création de doublon du joueur.
party={hero,partner};leader=1;suivi.Activer(map);assert(created==1);leader=0
-- Les rôles ambigus ne doivent jamais choisir un personnage au hasard.
party={hero,partner,extra};partner.data={Importance='Hero'};suivi.Activer(map);assert(created==1)
partner.data={Importance='Partner'};party={hero,partner}
-- Première position bloquée, sélectionner une position libre différente.
obstacles['13,10']=1;suivi.Activer(map);assert(created==2 and actors.Teammate1.Position.X==56)
-- Aucune position praticable : ne pas placer dans un mur.
actors.Teammate1=nil;for x=0,29 do for y=0,29 do obstacles[x..','..y]=1 end end
suivi.Activer(map);assert(created==2)
-- Ancienne sauvegarde à deux sans rôles : repli documenté de equipe_scene.
obstacles={};hero.data={};partner.data={};suivi.Activer(map);assert(created==3 and actors.Teammate1.Data==partner)
print('PASS suivi intérieur : entrée, chargement, absence, leader, identité, obstacles et ancien duo')
