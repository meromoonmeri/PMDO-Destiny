-- Intérieurs de Réverie : peuplement à l'entrée, rencontres à l'interaction.
local cine = require 'destiny.cinematique'
local recit = require 'destiny.reverie_recit'
local suivi = require 'destiny.suivi_interieurs'
local foyers = require 'destiny.reverie_foyers_recits'
local M = {}

local TAILLE = 16
local replis = {{0,0},{24,0},{-24,0},{0,24},{0,-24},{24,24},{-24,24}}

local function etat_de(cle)
  SV.Destiny = SV.Destiny or {}
  local d = SV.Destiny
  if type(d.FoyersReverie) ~= 'table' then d.FoyersReverie = {} end
  if type(d.FoyersReverie[cle]) ~= 'table' then d.FoyersReverie[cle] = {} end
  return d, d.FoyersReverie[cle]
end

local function phase_de(d)
  return recit.Crique(d) and 'crique' or recit.Acte(d) or 'repos'
end

local function au_foyer(cle, pnj, d)
  if cle ~= 'citrouille' then return true end
  local famille = recit.FamilleAuFoyer(d)
  return (pnj.id == 'Foyer_Zelie') ~= famille
end

local function chevauche(x, y, bx, by, w, h)
  return w > 0 and h > 0 and x < bx+w and bx < x+TAILLE and y < by+h and by < y+TAILLE
end

local function coupe(x, y, rect)
  return rect ~= nil and chevauche(x,y,rect.X,rect.Y,rect.Width,rect.Height)
end

local function case_libre(map, nom, x, y)
  if x < 0 or y < 0 or x+TAILLE > map.TexWidth*8 or y+TAILLE > map.TexHeight*8 then return false end
  for cx = math.floor(x/8), math.floor((x+TAILLE-1)/8) do
    for cy = math.floor(y/8), math.floor((y+TAILLE-1)/8) do
      if map:GetObstacle(cx,cy) ~= 0 then return false end
    end
  end
  local function occupe(a)
    return a ~= nil and a.EntEnabled ~= false and a.EntName ~= nom and a.Position ~= nil
      and chevauche(x,y,a.Position.X,a.Position.Y,TAILLE,TAILLE)
  end
  if occupe(CH('PLAYER')) or occupe(CH('Teammate1')) then return false end
  for couche in luanet.each(map.Entities) do
    if couche.Visible ~= false then
      for a in luanet.each(couche.MapChars) do if occupe(a) then return false end end
      for obj in luanet.each(couche.GroundObjects) do
        if obj.EntEnabled ~= false and coupe(x,y,obj.Collider) then return false end
      end
      -- Également les anciennes entrées d'une sauvegarde (pas seulement la porte active).
      for repere in luanet.each(couche.Markers) do if coupe(x,y,repere.Collider) then return false end end
    end
  end
  return true
end

local function poser(map, pnj, phase)
  local a = map:GetMapChar(pnj.id)
  local p = pnj[phase] or pnj.repos
  local dir = Direction[p[3]]
  for _, delta in ipairs(replis) do
    local x,y = p[1]+delta[1],p[2]+delta[2]
    if case_libre(map,pnj.id,x,y) then
      if a == nil then
        local data = RogueEssence.Dungeon.CharData()
        data.BaseForm = RogueEssence.Dungeon.MonsterID(pnj.espece,0,'normal',Gender[pnj.genre])
        data.Nickname = pnj.nom
        data.Level = 5
        a = GROUND:CreateCharacterFromCharData(pnj.id,RogueEssence.Dungeon.Character(data),x,y,dir)
      end
      AI:DisableCharacterAI(a)
      GROUND:TeleportTo(a,x,y,dir)
      GROUND:Unhide(pnj.id)
      a:ReloadEvents()
      return
    end
  end
  -- Aucun poste ne justifie de pousser le joueur ou de bloquer son retour.
  if a ~= nil then GROUND:Hide(pnj.id) end
end

local function peupler(map, cle, d)
  local def = foyers[cle]
  if map == nil or map.AssetName ~= def.carte then return end
  for _, p in ipairs(def.habitants) do
    if not au_foyer(cle,p,d) and map:GetMapChar(p.id) ~= nil then
      GROUND:RemoveCharacter(p.id)
    end
  end
  local phase = phase_de(d)
  for _, p in ipairs(def.habitants) do
    if au_foyer(cle,p,d) then
      local ok, err = pcall(poser,map,p,phase)
      if not ok then print('[Destiny] foyer '..cle..', pose '..p.id..' : '..tostring(err)) end
    end
  end
end

local function actif(a)
  return a ~= nil and a.EntEnabled ~= false
end

local function dire(a, hero, texte, emotion)
  if not actif(a) or texte == nil then return end
  local placement = a.Position.X > hero.Position.X and 'droite' or 'standard'
  cine.Dire(a,emotion or 'Normal',texte,placement)
end

local function choix(question, options)
  UI:BeginChoiceMenu(question,options,1,#options)
  UI:WaitForChoice()
  return tonumber(UI:ChoiceResult())
end

local function voisin(nom, repli)
  local a = CH(nom)
  return actif(a) and a or repli
end

local function place_pour(id, maximum)
  local nb = GAME:GetPlayerBagCount()
  local limite = _DATA.Save.ActiveTeam:GetMaxInvSlots(_ZONE.CurrentZone)
  if nb < limite then return true end
  if maximum > 1 then
    for i = 0, nb-1 do
      local item = GAME:GetPlayerBagItem(i)
      if item.ID == id and not item.Cursed and item.Amount < maximum then return true end
    end
  end
  return false
end

-- Une seule écriture au moment où l'objet arrive réellement : ni perte
-- si le sac est plein, ni deuxième cadeau après une réentrée ou une sieste.
local function donner(etat, cle, id, a, hero, texte)
  if etat[cle] then return end
  local item = _DATA:GetItem(id)
  if not place_pour(id,item.MaxStack) then
    dire(a,hero,'Ton sac est plein. Je mets ça de côté pour toi ; repasse quand tu auras de la place.','Normal')
    return
  end
  dire(a,hero,texte,'Happy')
  local nom = RogueEssence.Dungeon.InvItem(id):GetDisplayName()
  GAME:GivePlayerItem(id,1,false)
  etat[cle] = id
  UI:ResetSpeaker()
  SOUND:PlayFanfare('Fanfare/Item')
  UI:WaitShowDialogue('Reçu : '..tostring(nom)..' !')
end

local function devinette(def, etat, a, hero)
  if etat.EnigmeCadeau then
    dire(a,hero,def.apres)
    return
  end
  if not etat.EnigmeResolue then
    dire(a,hero,def.texte,'Normal')
    local r = choix('Ta réponse ?',def.choix)
    if r == 4 then
      local parent = voisin(def.indice_par,a)
      if parent ~= a then cine.RegarderGroupe({{a,parent,0,4},{parent,hero,5,4}}) end
      dire(parent,hero,def.indice)
      cine.RegarderGroupe({{a,hero,0,4}})
      -- Après l'indice, proposer une réponse sans réciter toute la devinette.
      dire(a,hero,'Alors, une idée ?')
      r = choix('Ta réponse ?', {def.choix[1],def.choix[2],def.choix[3],def.choix[5]})
      if r == 4 then return end
    end
    if r == nil or r == 5 then return end
    if r ~= def.bonne then
      dire(a,hero,def.rate)
      return
    end
    etat.EnigmeResolue = true
    cine.Emote(a,'happy')
    cine.Respirer(14)
    dire(a,hero,def.trouve,'Happy')
  end
  local parent = voisin(def.donne_par,a)
  if parent ~= a then cine.RegarderGroupe({{a,parent,0,4},{parent,hero,6,4}}) end
  donner(etat,'EnigmeCadeau',def.objet,parent,hero,def.offert)
end

local function panier(def, etat, a, hero)
  if etat.Panier then
    dire(a,hero,'J’ai déjà garni votre sac. Cette fois, c’est avec vous que je partage un moment, pas le panier.')
    return
  end
  local r = choix('Que glisser dans votre sac ?',def.choix)
  local option = r and def.options[r]
  if option then donner(etat,'Panier',option.id,a,hero,option.dit) end
end

local function discussion(def, etat, a, hero)
  for _, option in ipairs(def.options) do
    if etat[def.cle] == option.id then
      dire(a,hero,option.suivi,'Happy')
      return
    end
  end
  dire(a,hero,def.question)
  local r = choix('Qu’en dis-tu ?',def.choix)
  local option = r and def.options[r]
  if option == nil then return end
  dire(a,hero,option.dit)
  UI:ResetSpeaker()
  cine.Respirer(16)
  local proche = CH(def.repond)
  if actif(proche) then
    cine.RegarderGroupe({{a,proche,0,4},{proche,a,6,4}})
    dire(proche,hero,option.reponse,'Happy')
  end
  etat[def.cle] = option.id
end

local function parler(cle, def, pnj, a, hero)
  local d, etat = etat_de(cle)
  cine.RegarderGroupe({{a,hero,0,4},{hero,a,4,4}})
  local phase = phase_de(d)
  local texte = pnj.textes[phase] or pnj.textes.nilo or pnj.textes.repos
  dire(a,hero,texte,phase == 'alerte' and 'Worried' or 'Normal')
  UI:ResetSpeaker()
  cine.Respirer(10)
  if def.devinette and def.devinette.mene == pnj.id then
    devinette(def.devinette,etat,a,hero)
  elseif def.panier and def.panier.mene == pnj.id then
    panier(def.panier,etat,a,hero)
  elseif def.discussion and def.discussion.mene == pnj.id then
    discussion(def.discussion,etat,a,hero)
  elseif cle == 'plante' and pnj.id == 'Foyer_Brin' and etat.Panier then
    for _, option in ipairs(def.panier.options) do
      if option.id == etat.Panier then dire(a,hero,option.suivi,'Happy') end
    end
  elseif pnj.id == 'Foyer_Leo' and etat.Dessin == 'montrer' then
    dire(a,hero,'J’ai reconnu le seuil. Ce que Nilo n’a pas dessiné, c’est le temps qu’on a passé à l’attendre sur ces deux planches.')
  elseif pnj.id == 'Foyer_Leo' and etat.Dessin == 'garder' then
    dire(a,hero,'Je n’ai pas demandé à voir sa feuille. Je lui ai seulement demandé s’il voulait que je m’assoie près de lui.')
  end
end

function M.Carte(cle)
  local def = assert(foyers[cle],cle)
  local carte = {}
  local sortie_en_cours, interaction = false, false
  local function bloquee()
    return interaction or sortie_en_cours or (_DATA and _DATA.Save and _DATA.Save.CutsceneMode)
  end
  local function activer(map)
    sortie_en_cours, interaction = false, false
    suivi.Activer(map)
    peupler(map,cle,SV.Destiny)
    GAME:FadeIn(20)
  end
  function carte.Init(map) end
  carte.Enter, carte.GameLoad = activer, activer
  carte[def.sortie..'_Touch'] = function(obj,activator)
    if (activator ~= nil and activator.EntName ~= 'PLAYER') or bloquee() then return end
    sortie_en_cours = true
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.ArriveeVille = 'batiment'
    GAME:FadeOut(false,20)
    GAME:EnterZone('town02_waterfallvillage',-1,0,0)
  end
  for _, pnj in ipairs(def.habitants) do
    carte[pnj.id..'_Action'] = function(a,hero)
      if not actif(a) or not actif(hero) or hero.EntName ~= 'PLAYER' or bloquee() then return end
      interaction = true
      local directions = {}
      for _, p in ipairs(def.habitants) do
        local proche = CH(p.id)
        if actif(proche) then directions[#directions+1] = {proche,proche.Direction} end
      end
      local partenaire = CH('Teammate1')
      local suit = actif(partenaire) and partenaire.AIEnabled
      GAME:CutsceneMode(true)
      local ok, err = pcall(function()
        if suit then AI:DisableCharacterAI(partenaire) end
        parler(cle,def,pnj,a,hero)
      end)
      UI:ResetSpeaker()
      for _, s in ipairs(directions) do pcall(function() GROUND:EntTurn(s[1],s[2]) end) end
      if suit then pcall(function() AI:EnableCharacterAI(partenaire) end) end
      GAME:CutsceneMode(false)
      interaction = false
      if not ok then print('[Destiny] foyer '..cle..', dialogue '..pnj.id..' : '..tostring(err)) end
    end
  end
  return carte
end

return M
