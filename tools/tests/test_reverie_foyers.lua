local defs = require 'destiny.reverie_foyers_recits'
local recit = require 'destiny.reverie_recit'
local function rien() end
package.preload['origin.common'] = function() return {} end
package.preload['destiny.suivi_interieurs'] = function() return {Activer=function() CH('Teammate1').AIEnabled=true end} end
local carte, equipe, journal, menu, reponses, sac, limite, cree, sortie
local function each(t)
  local i = 0
  return function() i = i+1; return t[i] end
end
local function acteur(id,x,y,dir,data)
  return {EntName=id, Position={X=x,Y=y}, Direction=dir, AIEnabled=true, EntEnabled=true,
          Data=data, ReloadEvents=rien}
end
function CH(id) return equipe[id] or carte.pnjs[id] end
Direction={}
for _, id in ipairs({'Up','Down','Left','Right','UpLeft','DownLeft','DownRight'}) do Direction[id]=id end
Gender={Male='Male',Female='Female'}
RogueEssence={Dungeon={CharData=function()return{}end,
  MonsterID=function(s,f,c,g)return{Species=s,Gender=g}end, Character=function(d)return d end,
  InvItem=function(id)return{GetDisplayName=function()return id end}end}}
local equipe_save={GetMaxInvSlots=function() return limite end}
_DATA={Save={CutsceneMode=false,ActiveTeam=equipe_save}, GetItem=function() return {MaxStack=0} end}
_ZONE={CurrentZone={}}
luanet={each=each}
GROUND={
  CreateCharacterFromCharData=function(_,id,d,x,y,dir)
    assert(not carte.pnjs[id],'doublon : '..id)
    cree=cree+1
    local a = acteur(id,x,y,dir,d)
    carte.pnjs[id]=a
    table.insert(carte.Entities[1].MapChars,a)
    return a
  end,
  RemoveCharacter=function(_,id)
    for i,a in ipairs(carte.Entities[1].MapChars) do
      if a.EntName==id then table.remove(carte.Entities[1].MapChars,i);break end
    end
    carte.pnjs[id]=nil
  end,
  TeleportTo=function(_,a,x,y,dir)
    assert(a.EntName~='PLAYER' and a.EntName~='Teammate1','équipe déplacée')
    a.Position={X=x,Y=y};a.Direction=dir
  end,
  Unhide=function(_,id) CH(id).EntEnabled=true end,
  Hide=function(_,id) CH(id).EntEnabled=false end,
  CharTurnToCharAnimated=function(_,a,b,f) assert(f==4);a.Direction='Right' end,
  CharSetEmote=function(_,a,emote) assert(emote=='happy') end,
  EntTurn=function(_,a,dir) a.Direction=dir end,
}
AI={DisableCharacterAI=function(_,a) a.AIEnabled=false end, EnableCharacterAI=function(_,a) a.AIEnabled=true end}
GAME={FadeIn=rien, FadeOut=rien, WaitFrames=function(_,n)assert(n>0)end,
      CutsceneMode=function(_,b) _DATA.Save.CutsceneMode=b end,
      EnterZone=function(_,...) sortie={...} end,
      GetPlayerBagCount=function() return #sac end,
      GetPlayerBagItem=function(_,i) return sac[i+1] end,
      GivePlayerItem=function(_,id,n,cursed) assert(n==1 and not cursed and #sac<limite);sac[#sac+1]={ID=id} end}
TASK={BranchCoroutine=function(_,fn)fn();return true end, JoinCoroutines=rien}
SOUND={PlayFanfare=function(_,n) assert(n=='Fanfare/Item') end}
local speaker,fail_text
UI={SetSpeaker=function(_,a)speaker=a.EntName end, ResetSpeaker=function() speaker=nil end,
    SetSpeakerLoc=function(_,x,y) assert((x==8 or x==256) and y==132) end, SetSpeakerEmotion=rien,
    WaitShowDialogue=function(_,txt)
      assert(_DATA.Save.CutsceneMode and not CH('Teammate1').AIEnabled)
      if fail_text and txt:find(fail_text,1,true) then fail_text=nil;error('interruption volontaire') end
      journal[#journal+1]={speaker,txt}
    end,
    BeginChoiceMenu=function(_,question,c,d,annule) assert(d==1 and annule==#c);menu={question,c} end,
    WaitForChoice=rien, ChoiceResult=function() assert(#reponses>0,'menu inattendu : '..menu[1]); return table.remove(reponses,1) end}

local function active(cle, d, base_x, base_y, pax, pay)
  journal, menu, reponses, cree, sortie = {},nil,{},0,nil
  SV={Destiny=d}
  local terrain=CARTES[defs[cle].carte]
  local marker=terrain.entrance
  equipe={PLAYER=acteur('PLAYER',base_x or marker.X,base_y or marker.Y,'Up'),
          Teammate1=acteur('Teammate1',pax or marker.X+24,pay or marker.Y,'Up')}
  carte={AssetName=defs[cle].carte,TexWidth=terrain.w,TexHeight=terrain.h,pnjs={},
    Entities={{Visible=true,MapChars={},GroundObjects={{Collider=terrain.seuil,EntEnabled=true}},Markers={}}}}
  for _, r in ipairs(terrain.markers) do table.insert(carte.Entities[1].Markers,{Collider=r}) end
  function carte:GetObstacle(x,y)return OBSTACLE(self.AssetName,x,y)end
  function carte:GetMapChar(id)return carte.pnjs[id]end
  local t=assert(loadfile(ARG_ROOT..'/game/Data/Script/destiny/ground/'..carte.AssetName..'/init.lua'))()
  t.Init(carte); t.Enter(carte)
  assert(#journal==0 and not _DATA.Save.CutsceneMode)
  return t
end

local function positions()
  local result={}
  for id,p in pairs(carte.pnjs) do
    if p.EntEnabled then result[id]={p.Position.X,p.Position.Y} end
  end
  return result
end

local function action(t,id,...)
  reponses={...};journal={}; menu=nil
  t[id..'_Action'](assert(CH(id)),CH('PLAYER'))
  assert(#reponses==0,'choix non consommé')
  assert(not _DATA.Save.CutsceneMode and CH('Teammate1').AIEnabled and speaker==nil)
end
local function dit(id, fragment)
  for _, v in ipairs(journal) do
    if v[1]==id and v[2]:find(fragment,1,true) then return true end
  end
  return false
end
local function etat(cle) return SV.Destiny.FoyersReverie[cle] end

local phases = {{},{RetourAccompli=true},{AlerteShinx='a_secourir'},
  {AlerteShinx='termine'},{PassageAquatiqueTermine=true},
  {AlerteShinx='termine',SaynetesReverieVues={nilo={famille=true}}},
  {AlerteShinx='termine',PassageAquatiqueTermine=true,SaynetesReverieVues={nilo={famille=true}}}}
for _, cle in ipairs({'pierre','plante','berge','hutte','citrouille'}) do
  for _, d in ipairs(phases) do
    local t=active(cle,d)
    local foyer = cle=='citrouille' and recit.FamilleAuFoyer(d)
    local expected = cle=='hutte' and 2 or (cle=='citrouille' and not foyer and 1 or 3)
    local count=0
    for _, p in ipairs(defs[cle].habitants) do
      local a=CH(p.id)
      if a then
        count=count+1
        assert(a.EntEnabled and a.Data.Nickname==p.nom and a.Data.BaseForm.Gender==p.genre and not a.AIEnabled)
        local phase = recit.Crique(d) and 'crique' or recit.Acte(d) or 'repos'
        assert(p.textes[phase],p.id..' sans réplique du chapitre '..phase)
      end
    end
    assert(count==expected and cree==expected,cle)
    TEST_CHEMINS(carte.AssetName,positions())
    local prev=positions()
    t.GameLoad(carte);assert(cree==expected)
    for id,p in pairs(positions()) do assert(p[1]==prev[id][1] and p[2]==prev[id][2]) end
    local toucher = t[defs[cle].sortie..'_Touch']
    toucher(nil,CH('Teammate1'));assert(not sortie)
    toucher(nil,CH('PLAYER'));assert(sortie[1]=='town02_waterfallvillage' and sortie[3]==0 and SV.Destiny.ArriveeVille=='batiment')
    sortie=nil; toucher(nil,CH('PLAYER'));assert(not sortie)
    t.Enter(carte);toucher(nil,CH('PLAYER'));assert(sortie)
  end
  print('PASS '..cle..' : poses par jalon, genre, porte et vrais trajets 16×16')
end
local t=active('pierre',{},128,136,216,144)
assert(CH('Foyer_Maelle').Position.X~=128 and CH('Foyer_Basalte').Position.X~=216,'repli non appliqué')
assert(CH('PLAYER').Position.X==128 and CH('Teammate1').Position.X==216)
TEST_CHEMINS(carte.AssetName,positions())
print('PASS ancienne sauvegarde sur les ancres : repli local sans déplacer l’équipe')

t=active('citrouille',{AlerteShinx='termine'})
assert(CH('Foyer_Zelie') and not CH('Foyer_Nilo'))
SV.Destiny.SaynetesReverieVues={nilo={famille=true}}
t.GameLoad(carte)
assert(not CH('Foyer_Zelie') and CH('Foyer_Nilo') and CH('Foyer_Lyra') and CH('Foyer_Leo'))
TEST_CHEMINS(carte.AssetName,positions())
print('PASS succession Zélie / famille du retour, sans doublon sur une carte rechargée')

sac={};limite=0
for _, test in ipairs({{'pierre','Foyer_Miette','Foyer_Basalte','berry_pecha'}, {'berge','Foyer_Perle','Foyer_Nacre','orb_escape'}}) do
  local cle,id,hint,obj=table.unpack(test)
  local def=defs[cle].devinette
  sac={};limite=0;t=active(cle,{})
  action(t,id,5);assert(not etat(cle).EnigmeResolue)
  action(t,id,4,4);assert(dit(hint,def.indice) and not etat(cle).EnigmeResolue)
  action(t,id,1);assert(dit(id,def.rate) and not etat(cle).EnigmeResolue)
  action(t,id,4,2);assert(etat(cle).EnigmeResolue and not etat(cle).EnigmeCadeau and #sac==0)
  assert(dit(def.donne_par,'Ton sac est plein'))
  limite=1;t.GameLoad(carte);action(t,id);assert(sac[1].ID==obj and etat(cle).EnigmeCadeau==obj)
  SV.Destiny.JourneeVille=42;t.Enter(carte);action(t,id);assert(dit(id,def.apres) and #sac==1)
end
print('PASS 2 devinettes : erreur, indice, annulation, sac plein, cadeau conservé et unique')

sac={};limite=1;t=active('plante',{RetourAccompli=true})
action(t,'Foyer_Flore',3);assert(not etat('plante').Panier and #sac==0)
action(t,'Foyer_Flore',2);assert(sac[1].ID=='berry_oran')
action(t,'Foyer_Brin');assert(dit('Foyer_Brin','celle que j’avais choisie'))
t.GameLoad(carte);action(t,'Foyer_Flore');assert(#sac==1)
sac={};t=active('plante',{});action(t,'Foyer_Flore',1);assert(sac[1].ID=='food_apple')
print('PASS panier : deux vrais objets au choix, refus sans effet et suivi de Brin')

for _, cle in ipairs({'hutte','citrouille'}) do
  local def=defs[cle].discussion
  local d={AlerteShinx='termine',SaynetesReverieVues={nilo={famille=true}}}
  t=active(cle,d)
  action(t,def.mene,3);assert(not etat(cle)[def.cle])
  fail_text=def.options[1].reponse
  action(t,def.mene,1);assert(not etat(cle)[def.cle],'branche consommée lors d’une interruption')
  for i,option in ipairs(def.options) do
    t=active(cle,{AlerteShinx='termine',SaynetesReverieVues={nilo={famille=true}}})
    action(t,def.mene,i)
    assert(dit(def.repond,option.reponse) and etat(cle)[def.cle]==option.id)
    t.GameLoad(carte);action(t,def.mene);assert(menu==nil and dit(def.mene,option.suivi))
  end
end
assert(not recit.FamilleAuFoyer({AlerteShinx='a_secourir',SaynetesReverieVues={nilo={famille=true}}}))
assert(not recit.FamilleAuFoyer({CelebrationNilo='en_attente',SaynetesReverieVues={nilo={famille=true}}}))
print('PASS message et dessin : deux branches réelles, reprise et choix mémorisés ; alerte et accueil prioritaires')
