local racine = arg[1] .. '/game/Data/Script/destiny/'
for _, n in ipairs({'origin.common', 'origin.menu.skill.SkillSelectMenu', 'origin.menu.team.AssemblySelectMenu'}) do
  package.preload[n] = function() return {} end
end
package.preload['destiny.equipe_scene'] = function() return {Suivre=function(a) a.AIEnabled=true end} end
package.preload['destiny.meteo_reverie'] = function() return {Appliquer=function()end} end
package.preload['destiny.missions_reverie'] = function() return {NotifierRetour=function()end} end
local magasins = {}
package.preload['destiny.boutiques_kecleon'] = function()
  return {Ouvrir=function(_, etal) magasins[#magasins+1] = etal end}
end
local recit = require 'destiny.reverie_recit'
local ville = assert(loadfile(racine .. 'ground/WaterfallVillageCapital/init.lua'))()
local lire = require 'destiny.reverie_saynetes'

local carte, equipe, notes, camera, paroles, mouvements, tours, pauses, destination, erreurs = nil
local function acteur(n,x,y,espece)
  return {EntName=n, Position={X=x,Y=y}, EntEnabled=true, Direction='Down', AIEnabled=true,
    Data={BaseForm={Species=espece}}, ReloadEvents=function() end}
end
function CH(n) return equipe[n] or (carte and carte.personnages[n]) end
Direction = {}; for _,d in ipairs({'Up','Down','Left','Right','UpLeft','UpRight','DownLeft','DownRight'}) do Direction[d]=d end
Gender={Male='Male', Female='Female', Genderless='Genderless'}
RogueElements = {Rect=function(x,y,w,h) return {X=x,Y=y,Width=w,Height=h} end}
RogueEssence={Ground={GroundObject=function() return {OnMapInit=function()end,SetTriggerType=function(self,t) self.type=t end} end,
  GroundEntity={EEntityTriggerTypes={Action='Action',Touch='Touch'}}},
  Dungeon={BaseMap={ScrollEdge={Clamp='Clamp'}},CharData=function()return{}end,
    MonsterID=function(s)return{Species=s}end,Character=function(d)return d end}}
luanet={each=function(tab) local i=0;return function() i=i+1;return tab[i] end end}
_DATA={Save={CutsceneMode=false}}
local function rien() end
local clic = 3
UI={ResetSpeaker=function() notes.speaker=nil end, SetSpeaker=function(_,p) notes.speaker=p;assert(p) end,
  SetSpeakerLoc=function(_,x,y) assert((x==8 or x==256) and y==132); notes.portrait=x end,
  SetSpeakerEmotion=rien, WaitShowDialogue=function(_,t) paroles[#paroles+1]={notes.speaker and notes.speaker.EntName,t} end,
  BeginChoiceMenu=function() notes.menu=(notes.menu or 0)+1 end, WaitForChoice=rien, ChoiceResult=function() return clic end,
  BankMenu=function() notes.banque=true end}
TASK={BranchCoroutine=function(_,fn) fn();return true end,JoinCoroutines=rien}
GAME={GetCurrentGround=function()return carte end, GetPlayerPartyCount=function()return 2 end,
  MoveCamera=function(_,x,y,t,player) camera[#camera+1]={x,y,t,player} end, FadeIn=rien,FadeOut=rien,
  WaitFrames=function(_,n) assert(n>0);pauses[#pauses+1]=n end,
  CutsceneMode=function(_,b) _DATA.Save.CutsceneMode=b end,
  EnterGroundMap=function(_,z,n) destination={z,n} end}
SOUND={PlayBGM=rien}
AI={DisableCharacterAI=function(_,a)a.AIEnabled=false end,EnableCharacterAI=function(_,a)a.AIEnabled=true end}
GROUND={TeleportTo=function(_,a,x,y,d)a.Position={X=x,Y=y};a.Direction=d end,
  MoveToPosition=function(self,a,x,y,collision,speed)
    assert(_DATA.Save.CutsceneMode and not collision and speed==1)
    mouvements[#mouvements+1]={a.EntName,x,y};self:TeleportTo(a,x,y,a.Direction)
  end,
  CharTurnToCharAnimated=function(_,a,b,f) assert(f==4); tours[#tours+1]={a.EntName,b.EntName};a.Direction='Right' end,
  CharAnimateTurnTo=function(_,a,d,f) assert(f==4);a.Direction=d end,
  EntTurn=function(_,a,d)a.Direction=d end,CharSetAnim=rien,CharEndAnim=rien,
  CharSetEmote=function(_,a,e)
    if erreurs then erreurs=false;error('interruption volontaire') end
    assert(e=='question' or e=='sweatdrop' or e=='happy' or e=='exclaim');notes.emote=a.EntName
  end,
  CreateCharacterFromCharData=function(_,n,d,x,y) assert(carte.personnages[n]==nil,'doublon '..n)
    local a=acteur(n,x,y,d.BaseForm.Species);a.Data=d;carte.personnages[n]=a;return a end,
  RemoveObject=function(_,n)carte.objets[n]=nil end,
  RemoveCharacter=function(_,n)if carte.personnages[n]==nil then return false end;carte.personnages[n]=nil;return true end,
  Hide=function(_,n)CH(n).EntEnabled=false end,Unhide=function(_,n)CH(n).EntEnabled=true end}
COMMON={CreateWalkArea=rien}

local function nettoyer()
  notes,camera,paroles,mouvements,tours,pauses={},{},{},{},{},{}
end
local function charge(n, x,y, px,py)
  nettoyer()
  carte={AssetName=n,Width=200,Height=500,personnages={},objets={}}
  local layer={MapChars={},GroundObjects={}}
  carte.Entities={layer}
  for _, p in ipairs(NATIFS[n]) do
    local a=acteur(p[1],p[2],p[3],p[4]);carte.personnages[p[1]]=a
    layer.MapChars[#layer.MapChars+1]=a
  end
  function carte:GetMapChar(id)return self.personnages[id] end
  function carte:FindObject(id)return self.objets[id] end
  function carte:AddObject(obj)self.objets[obj.EntName]=obj;layer.GroundObjects[#layer.GroundObjects+1]=obj end
  function carte:GetObstacle(cx,cy)return OBSTACLE(self.AssetName,cx,cy)end
  equipe={PLAYER=acteur('PLAYER',x,y,'eevee'),Teammate1=acteur('Teammate1',px,py,'riolu')}
  ville.Init(carte);ville.Enter(carte)
  assert(not _DATA.Save.CutsceneMode and #paroles==0,'une saynète s’est lancée à l’entrée')
end

local natifs = {}
for _, a in ipairs(NATIFS.WaterfallVillageCapital) do natifs[a[1]]=true end
for _, n in ipairs({'Pijako_Livreur','Cradopaud_Pecheur','Roserade_Fleuriste','Magneton_Garde',
                    'Babimanta_Enfant','Goinfrex_Voyageur','Bellossom_Boutique','Nilo_Shinx'}) do natifs[n]=true end
for _, phase in ipairs({'bois','alerte','nilo','crique'}) do
  local vues, n, scenes = {}, 0, {}
  for id in pairs(natifs) do
    assert(ville[id..'_Action'], 'action manquante : '..id)
    if id ~= 'Nilo_Shinx' or phase=='nilo' or phase=='crique' then
      local texte = assert(recit.Replique(id,phase),phase..' : '..id)
      assert(not vues[texte], 'réplique dupliquée '..phase..' '..id);vues[texte]=true;n=n+1
      local s=recit.Scene(id,phase)
      assert(s or (id=='NewObject_9' and phase=='alerte'), phase..' : saynète absente '..id)
      if s then scenes[s.id]=true end
      if phase ~= 'bois' then assert(texte~=recit.Replique(id,'bois')) end
    end
  end
  local ns=0;for _ in pairs(scenes) do ns=ns+1 end
  print('PASS couverture '..phase..' : '..n..' répliques individuelles / '..ns..' saynètes')
end
assert(recit.Acte({})==nil and not recit.Crique({}))
assert(recit.Acte({RetourAccompli=true,VisiteVille='en_route'})==nil)
assert(recit.Acte({RetourAccompli=true,JourneeVille=321})=='bois')
assert(recit.Acte({AlerteShinx='a_secourir',GrotteVerdoyanteBossVaincu=true})=='alerte')
assert(recit.Acte({AlerteShinx='termine',CelebrationNilo='en_attente'})==nil)
assert(recit.Acte({GrotteVerdoyantePhase=4})=='nilo')
assert(recit.Acte({AlerteShinx='termine',PassageAquatiqueTermine=true})=='nilo' and recit.Crique({PassageAquatiqueTermine=true}))
assert(not recit.Crique({PassageAquatiqueTermine=true,AlerteShinx='a_secourir'}))
print('PASS ancien état, priorité visite / alerte / accueil, crique additive')

local cas = {{RetourAccompli=true}, {AlerteShinx='a_secourir'}, {AlerteShinx='termine'},
             {PassageAquatiqueTermine=true}, {AlerteShinx='termine',PassageAquatiqueTermine=true}}
local debut = {reverie_centre={800,1224,776,1224},reverie_residentiel={700,2000,700,2024},reverie_etang={1120,2352,1120,2328}}
for _, d in ipairs(cas) do
  SV={Destiny=d}
  for _, p in ipairs(recit.Placements(d)) do
    assert(ACCESSIBLE(p[2],p[3],p[4]), 'poste sans chemin : '..p[1]..' '..p[2])
    charge(p[2], table.unpack(debut[p[2]]))
    local a=assert(CH(p[1]),'absent : '..p[1])
    assert(a.Position.X==p[3] and a.Position.Y==p[4], ('poste %s : %d,%d au lieu de %d,%d'):format(p[1],a.Position.X,a.Position.Y,p[3],p[4]))
    assert(a.AIEnabled==false, 'ancrage remis en flânerie : '..p[1])
    local ax,ay=a.Position.X,a.Position.Y
    ville.GameLoad(carte)
    assert(CH(p[1])==a and a.Position.X==ax and a.Position.Y==ay)
  end
end
print('PASS tous les ancrages sur les collisions natives et accessibles ; rechargement stable')

SV={Destiny={AlerteShinx='termine'}}
charge('reverie_centre',592,956,624,956)
assert(CH('Pijako_Livreur')==nil and CH('Babimanta_Enfant')==nil and CH('Luxray_Alerte')==nil)
assert(carte.objets.ComptoirKecleon and carte.objets.SortieExplorationE2 and carte.objets.EscalierSVersResidentiel)
local zig,zag=CH('Kecleon'),CH('Kecleon_Violet')
local zx,zy=zig.Position.X,zig.Position.Y
nettoyer();ville.ComptoirKecleon_Action(nil,CH('PLAYER'))
assert(#paroles==4 and paroles[1][1]=='Kecleon' and paroles[3][1]=='Kecleon_Violet')
assert(#camera==2 and not camera[1][4] and camera[2][4] and #tours>=8 and #pauses>=8)
assert(not _DATA.Save.CutsceneMode and CH('Teammate1').AIEnabled and not zag.AIEnabled and not zig.AIEnabled)
assert(SV.Destiny.SaynetesReverieVues.nilo.etals and magasins[1]=='vert')
assert(zig.Position.X==zx and zig.Position.Y==zy and zig.Direction=='Down')
SV.Destiny.JourneeVille=60
ville.ComptoirKecleonViolet_Action(nil,CH('PLAYER'))
assert(#paroles==4 and #camera==2 and magasins[2]=='violet','saynète rejouée ou service modifié')
ville.GameLoad(carte)
ville.ComptoirKecleon_Action(nil,CH('PLAYER'))
assert(magasins[3]=='vert' and #paroles==4)
print('PASS deux services, mise en scène et trace « vue » commune, pas de rejeu après sieste ou chargement')

charge('reverie_etang',1092,2200,1124,2200)
local pip,ondine=assert(CH('Pijako_Livreur')),assert(CH('Babimanta_Enfant'))
assert(pip.Position.Y==2224 and ondine.Position.Y==2224,'pas de repli sur sauvegarde occupée')
assert(equipe.PLAYER.Position.X==1092 and equipe.PLAYER.Position.Y==2200 and equipe.Teammate1.Position.X==1124)
charge('reverie_etang',1068,2216,1068,2240)
pip=CH('Pijako_Livreur');nettoyer();ville.Pijako_Livreur_Action(pip,CH('PLAYER'))
assert(#mouvements==2 and mouvements[1][2]==1100 and mouvements[2][2]==1092 and pip.Position.X==1092)
assert(SV.Destiny.SaynetesReverieVues.nilo.carnet_etang)
ville.EscalierPVersResidentiel_Touch(nil,CH('PLAYER'))
assert(destination[2]=='reverie_residentiel' and SV.Destiny.PassageQuartier.y==2432)
SV.Destiny.PassageQuartier=nil
print('PASS changement de quartier, repli sans déplacer le joueur, pas de Pip et sortie vers le résidentiel')

charge('reverie_residentiel',700,2428,672,2428)
nettoyer();erreurs=true
local rendu=lire.Reagir(SV.Destiny,'NewObject_10',CH('NewObject_10'),false)
assert(rendu and not _DATA.Save.CutsceneMode and CH('Teammate1').AIEnabled and not SV.Destiny.SaynetesReverieVues.nilo.famille)
assert(camera[#camera][4]==true)
nettoyer();ville.NewObject_10_Action(CH('NewObject_10'),CH('PLAYER'))
assert(SV.Destiny.SaynetesReverieVues.nilo.famille and #paroles==5 and paroles[4][1]=='Nilo_Shinx')
assert(not CH('NewObject_9').AIEnabled and not _DATA.Save.CutsceneMode)
SV.Destiny.PassageAquatiqueTermine=true
nettoyer();ville.NewObject_10_Action(CH('NewObject_10'),CH('PLAYER'))
assert(SV.Destiny.SaynetesReverieVues.crique.maree_famille and #paroles==4)
print('PASS interruption récupérable, trio en famille, salle disponible pour les échanges de la crique')
