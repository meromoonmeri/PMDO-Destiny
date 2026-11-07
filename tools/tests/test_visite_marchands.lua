-- Test de la cinématique par doublures ; ne teste pas le moteur graphique.
package.preload['origin.common']=function()return {}end
package.preload['origin.menu.skill.SkillSelectMenu']=function()return {}end
package.preload['origin.menu.team.AssemblySelectMenu']=function()return {}end
local actors, events, sound, directions, speaker, interrompu
local function event(t,n,v) events[#events+1]={t,n,v} end
package.preload['destiny.equipe_scene']=function()return {Suivre=function()event('suivi')end}end
package.preload['destiny.missions_reverie']=function()return {Actuelle=function()return nil end}end
package.preload['destiny.cinematique']=function()return {
 NomEspece=function(_,n)return n end,
 Dire=function(a,e,t,placement)assert(a and a.EntEnabled~=false,'locuteur caché');if a.EntName~='Teammate1' then assert(a.idle,'PNJ pas en idle') end;event('dialogue',a.EntName,t);event('portrait',a.EntName,placement)end,
 RegarderGroupe=function(actions)
  local vus={};for i,a in ipairs(actions) do
   assert(a[1] and a[2] and a[1]~=a[2] and a[1].EntEnabled~=false and a[2].EntEnabled~=false)
   assert(not vus[a[1]] and a[3]==(i-1)*5 and a[4]==4,'regards non désynchronisés')
   vus[a[1]]=true;event('regard',a[1].EntName,a[2].EntName)
  end
 end,Respirer=function()end,TournerGroupe=function()end,
}end
Direction={Up=0,Down=1,Left=2,Right=3,UpLeft=4,UpRight=5,DownLeft=6};Gender={Male=0,Female=1,Genderless=2}
RogueEssence={Data={Gender={Unknown='Unknown'}},Dungeon={CharData=function()return {}end,MonsterID=function(s)return s end,Character=function(d)return {Data=d}end}}
luanet={each=function(list)local i=0;return function()i=i+1;return list[i]end end}
function CH(n)return actors[n]end
local function new(name,x,y,species)
 local a={EntName=name,Position={X=x or 800,Y=y or 1160},Direction=Direction.Down,EntEnabled=true,Data={Nickname=name,Species=species}}
 function a:ReloadEvents()end
 function a:GetDisplayName()return self.EntName end
 actors[name]=a;return a
end
GROUND={
 CreateCharacterFromCharData=function(_,n,d,x,y)local a=new(n,x,y);a.Data=d.Data;event('creer',n);return a end,
 RemoveCharacter=function(_,n)assert(actors[n]);actors[n]=nil;event('retirer',n);return true end,
 Hide=function(_,n)assert(actors[n]);actors[n].EntEnabled=false;event('cacher',n)end,
 Unhide=function(_,n)assert(actors[n]);actors[n].EntEnabled=true;event('montrer',n)end,
 TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};a.Direction=d;event('placer',a.EntName,x..','..y)end,
 MoveToPosition=function(_,a,x,y,run,speed)
  if a.EntName=='NewObject_16' or a.EntName=='NewObject_14' then error('habitant fixe déplacé') end
  if a.EntName=='Teammate1' and actors.NewObject_16 then
   local d=actors.NewObject_16.Position;assert(math.abs(x-d.X)>=16 or math.abs(y-d.Y)>=16,'passage partenaire bloqué')
  end
  a.Position={X=x,Y=y};event('marcher',a.EntName,x..','..y)
 end,
 CharAnimateTurnTo=function(_,a,dir)assert(a);event('orientation',a.EntName,dir)end,CharTurnToCharAnimated=function(_,a,b)assert(a and b);event('tourne_vers',a.EntName,b.EntName)end,
 CharSetEmote=function(_,a,emote)assert(a);event('emote',a.EntName,emote)end,
 CharSetAnim=function(_,a,anim,loop)assert(anim=='Idle' and loop);a.idle=true end,CharEndAnim=function(_,a)a.idle=false end,
}
GAME={GetPlayerPartyCount=function()return 2 end,CutsceneMode=function(_,v)event('mode',nil,v)end,WaitFrames=function(_,n)event('attente',nil,n)end,FadeIn=function()end,MoveCamera=function(_,x,y,t,r)event('camera',x,y)end}
TASK={BranchCoroutine=function(_,f)f();return true end,JoinCoroutines=function()end}
SOUND={PlayBGM=function(_,n)event('music',n)end,FadeOutBGM=function()end,PlayBattleSE=function(_,n)event('son',n)end}
UI={ResetSpeaker=function()speaker=nil end,SetSpeaker=function(_,n,keysound,skin,form,texture,genre)
 assert((n=='???' or n=='Teammate1') and keysound and skin=='' and form==-1 and genre=='Unknown');speaker=n;event('nom_sans_portrait',n)
 end,WaitShowDialogue=function(_,t)if speaker=='???' then event('voix','???',t) else assert(speaker=='Teammate1');event('dialogue',speaker,t);event('hors_champ',speaker,t)end end}

AI={DisableCharacterAI=function()end,EnableCharacterAI=function()end};COMMON={CreateWalkArea=function()end}
local root=arg[1] or '.'
local ville=assert(loadfile(root..'/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
local function find(t,sub)
 for i,v in ipairs(events)do if v[1]==t and (v[3] or ''):find(sub,1,true) then return i end end
 error('événement absent : '..t..' '..sub)
end
local function count(name,e)
 local n=0;for _,v in ipairs(events)do if v[1]=='emote' and v[2]==name and (not e or v[3]==e)then n=n+1 end end;return n
end
local function scenario(species,legacy,missing)
 actors={};events={};SV={Destiny={VisiteVille='en_route'}}
 new('PLAYER');new('Teammate1',800,1160,species)
 local names={'Kecleon','Kecleon_Violet','Kangourex','NewObject_3','NewObject_4','NewObject_6','NewObject_7','NewObject_8','NewObject_12','NewObject_13','NewObject_14','Doyen','','Drifloon','NewObject_16','NewObject_18','NewObject_21','NewObject_15','NewObject_22','NewObject_23','NewObject_24','Pijako_Livreur','Cradopaud_Pecheur','Roserade_Fleuriste','Babimanta_Enfant','Goinfrex_Voyageur','PNJ_Supplementaire'}
 local list={};for _,n in ipairs(names)do if n~=missing then list[#list+1]=new(n)end end
 if actors.NewObject_16 then actors.NewObject_16.Position={X=827,Y=1178} end;if actors.NewObject_14 then actors.NewObject_14.Position={X=857,Y=1179} end;interrompu=false
 if legacy then list[#list+1]=new('NewObject_9',718,2527)end
 local hidden=new('PNJ_Cache');hidden.EntEnabled=false;list[#list+1]=hidden
 local extra=new('PNJ_Temporaire');local map={Entities={{Visible=true,MapChars=list,TemporaryChars={extra,actors.Teammate1}}}}
 ville.Visite(map)
 assert(SV.Destiny.VisiteVille=='terminee' and SV.Destiny.AlerteShinx=='a_secourir' and not actors.PLAYER.CollisionDisabled)
 assert(actors.Teammate1.Data.Species==species,'le partenaire choisi a été modifié')
 if actors.NewObject_4 then assert(actors.NewObject_4.EntEnabled and actors.NewObject_4.Position.X==360)end
 assert(legacy or actors.Luxray_Alerte)
 if legacy then assert(actors.NewObject_9.Position.X==718 and actors.NewObject_9.Position.Y==2527)end
 for _,n in ipairs(names)do if n~='NewObject_4' and n~=missing then assert(count(n)>=2,'témoin sans deux réactions : '..n)end end
 assert(count('PNJ_Temporaire')>=2 and count('PNJ_Cache')==0)
 assert(count('PLAYER')>=2 and count('Teammate1')>=2)
 assert(count('PLAYER','shock')==0 and count('Teammate1','shock')>=1,'réactions du duo insuffisamment nuancées')
 if actors.NewObject_14 then assert(actors.NewObject_14.Position.X==857)end;if actors.NewObject_16 then assert(actors.NewObject_16.Position.X==827)end
 local hors=0;local portraits=0
 for _,v in ipairs(events)do if v[1]=='hors_champ' then hors=hors+1 end;if v[1]=='portrait' and v[2]=='NewObject_16' then assert(v[3]=='droite');portraits=portraits+1 end end
 assert(hors>=(missing=='NewObject_4' and 8 or 10) and (missing=='NewObject_16' or portraits>=3),'portrait ou locuteur hors champ incorrect')
 local a=find('voix','À l’aide');local b=find('dialogue','Vous avez entendu');local c=find('dialogue','On dirait Lyra');local d=find('marcher','800,1224');local e=find('dialogue','Hah… Hah');local f=find('dialogue','tombé dans un fossé');local g=find('dialogue','en expédition');local h=find('dialogue','Nous pouvons y aller');local i=missing=='NewObject_4' and #events or find('dialogue','Laisse donc ces jeunes')
 assert(a<b and b<c and c<d and d<e and e<f and f<g and g<h and h<i,'ordre de la scène incorrect')
 local musique={};for _,v in ipairs(events)do if v[1]=='music' then musique[#musique+1]=v[2] end end
 assert( #musique==3 and musique[1]=='Treasure Town.ogg' and musique[2]=='Threat.ogg' and musique[3]=='Treasure Town.ogg')
 if missing~='NewObject_4' then assert(find('placer','648,1152')<find('marcher','720,1152')) end
 assert(not find('dialogue','Bienvenue à Réverie Town !')==false)
 local function regard_entre(debut,fin,nom,cible)
  for k=debut+1,fin-1 do local v=events[k];if v[1]=='regard' and v[2]==nom and v[3]==cible then return true end end
  error('Regard absent : '..nom..' vers '..cible)
 end
 local lyra=legacy and 'NewObject_9' or 'Luxray_Alerte'
 regard_entre(d,e,'Teammate1',lyra);regard_entre(d,e,'PLAYER',lyra)
 if missing~='NewObject_4' then
  local entree=find('marcher','720,1152');regard_entre(entree,i,'Teammate1','NewObject_4');regard_entre(entree,i,lyra,'NewObject_4')
  local confiance=find('dialogue','Nous ferons de notre mieux');regard_entre(i,confiance,'NewObject_4','Teammate1')
 end
 local camera=false;for _,v in ipairs(events)do if v[1]=='camera' and v[2]==840 and v[3]==1208 then camera=true end end
 assert(camera,'cadrage arrivée Alakazam absent')
 for _,v in ipairs(events)do if v[1]=='dialogue' then assert(not v[3]:find('je vous laisse le passage',1,true))end end
 print('PASS partenaire '..species..', carte '..(legacy and 'historique' or 'centrale')..', témoins nommés, anonyme, temporaire et caché')
end
scenario('riolu',false);scenario('eevee',false);scenario('vulpix',true);scenario('pikachu',false,'NewObject_4');scenario('skitty',false,'NewObject_14')
-- Absence du partenaire : scène suspendue sans cacher Alakazam.
actors={};events={};new('PLAYER');new('NewObject_4');SV={Destiny={VisiteVille='en_route'}};GAME.GetPlayerPartyCount=function()return 1 end
ville.Visite({Entities={}});assert(SV.Destiny.VisiteVille=='en_route' and actors.NewObject_4.EntEnabled and not SV.Destiny.AlerteShinx)
print('PASS partenaire absent : visite suspendue')

-- Préparation, choix, annulation et départ sans fausse destination.
STRINGS={Format=function(_,s)return s end}
local choix_restants, messages, menus
UI.BeginChoiceMenu=function(_,prompt,options,default,cancel) assert(speaker==nil,'choix avec portrait');menus[#menus+1]={prompt=prompt,options=options} end
UI.WaitForChoice=function()end
UI.ChoiceResult=function()return table.remove(choix_restants,1)end
UI.WaitShowDialogue=function(_,t)messages[#messages+1]=t end
GAME.FadeOut=function()end
GAME.DungeonUnlocked=function()return false end
local function suite(choices)
 actors={};events={};messages={};menus={};choix_restants=choices
 SV={Destiny={AlerteShinx='a_secourir',VisiteVille='terminee'}}
 local h=new('PLAYER',760,1176);new('Teammate1',784,1152,'eevee');local l=new('Luxray_Alerte',800,1224)
 ville.Luxray_Alerte_Action(l,h);return h,l
end
local hero,lux=suite({2})
assert(not SV.Destiny.DepartShinxAccepte and hero.Position.X==760 and lux.Position.X==800 and find('dialogue','Nilo'))
assert(find('dialogue','je vous attends ici') and not hero.CollisionDisabled)
hero,lux=suite({1,1})
assert(SV.Destiny.DepartShinxAccepte and SV.Destiny.LuxrayAttente=='sortie' and hero.Position.X==1552 and not hero.CollisionDisabled)
assert(#menus==2 and menus[2].options[1]:find('Grotte Verdoyante',1,true) and messages[1]:find('pas encore disponible',1,true))
hero,lux=suite({1,3});assert(not hero.CollisionDisabled and #messages==0 and SV.Destiny.DepartShinxAccepte)
print('PASS suite Lyra / Nilo : choix, annulation, déplacement et destination non fabriquée')
actors={};events={};new('PLAYER');new('Teammate1');new('NewObject_4');new('NewObject_14',857,1179);new('NewObject_16',784,1200)
SV={Destiny={VisiteVille='en_route'}};GAME.GetPlayerPartyCount=function()return 2 end
ville.Visite({Entities={}})
assert(SV.Destiny.VisiteVille=='en_route' and not SV.Destiny.AlerteShinx and not actors.PLAYER.CollisionDisabled and actors.NewObject_4.EntEnabled)
print('PASS placement inattendu : visite suspendue sans traverser un habitant')
