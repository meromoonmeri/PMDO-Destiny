-- Rencontres sur les chemins, sans modifier les PNJ résidents ni le partenaire.
local cine = require 'destiny.cinematique'
local defs = require 'destiny.reverie_itinerants_recits'
local M = {}
local zone_ville, zone_duel = 'town02_waterfallvillage', 'reverie_duel'
local marches, par_id, tic = {}, {}, 0

local function etat()
  SV.Destiny = SV.Destiny or {}
  local d = SV.Destiny
  d.ItinerantsReverie = d.ItinerantsReverie or {}
  return d,d.ItinerantsReverie
end

local function autorises()
  local d = SV and SV.Destiny
  return d ~= nil and d.VisiteVille == 'terminee' and d.AlerteShinx ~= 'a_secourir'
end

local function est_actif(a)
  return a ~= nil and a.EntEnabled ~= false
end

local function arreter(s)
  if s.marche then
    TASK:StopEntityTask(s.acteur)
    s.marche = false
  end
  GROUND:CharEndAnim(s.acteur)
end

function M.Quitter()
  for _, s in ipairs(marches) do
    if s.marche then arreter(s) end
  end
  marches, par_id, tic = {}, {}, 0
end

local function installer(map, p, est_libre, visible)
  local a = map:GetMapChar(p.id)
  if visible then
    for _, i in ipairs({2,1,3}) do
      local x = p.x[i]
      if est_libre(map,p.id,x,p.y) then
        local dir = i == 3 and Direction.Left or Direction.Right
        if a == nil then
          local data = RogueEssence.Dungeon.CharData()
          data.BaseForm = RogueEssence.Dungeon.MonsterID(p.espece,0,'normal',Gender[p.genre])
          data.Nickname = p.nom
          data.Level = 5
          a = GROUND:CreateCharacterFromCharData(p.id,RogueEssence.Dungeon.Character(data),x,p.y,dir)
        else
          GROUND:TeleportTo(a,x,p.y,dir)
        end
        AI:DisableCharacterAI(a)
        a:ReloadEvents()
        local sens = i == 3 and -1 or 1
        local s = {acteur=a, def=p, indice=i, cible=i+sens, sens=sens, apres=p.repos}
        marches[#marches+1], par_id[p.id] = s,s
        return
      end
    end
  end
  -- Cas du GameLoad : un acteur sauvegardé ne doit pas survivre à une alerte
  -- ni réapparaître sur le joueur si tous ses points de départ sont occupés.
  if a ~= nil then GROUND:RemoveCharacter(p.id) end
end

function M.Installer(map, est_libre)
  M.Quitter()
  if map == nil or map.GetMapChar == nil or map.GetObstacle == nil then return end
  local n = map.AssetName
  local complete = n == 'WaterfallVillageCapital' or n == 'WaterfallVillageCapital_Dev'
  for _, def in ipairs(defs) do
    if complete or n == def.carte then installer(map,def,est_libre,autorises()) end
  end
end

function M.Update(libre)
  if #marches == 0 then return end
  tic = tic + 1
  -- N'interroge le moteur qu'aux départs ; le déplacement se fait à son pas natif.
  for _, s in ipairs(marches) do
    local a,p = s.acteur,s.def
    if libre and not s.parle and not s.marche and tic >= s.apres and est_actif(a) and not a.IsInteracting then
      local x = p.x[s.cible]
      s.marche = true
      local tache = TASK:StartEntityTask(a, function()
        GROUND:MoveToPosition(a,x,p.y,false,p.vitesse)
        s.marche = false
        if math.abs(a.Position.X-x) <= 1 then
          s.indice = s.cible
        else
          -- Un passant ou le joueur barre la route : rebrousser chemin sans
          -- pousser, sans téléportation, puis retenter après une courte pause.
          s.sens = -s.sens
        end
        if s.indice + s.sens < 1 or s.indice + s.sens > #p.x then s.sens = -s.sens end
        s.cible = s.indice + s.sens
        s.apres = tic + p.repos
      end)
      if tache == nil then s.marche, s.apres = false, tic + 30 end
    elseif s.marche and (not libre or a.IsInteracting) then
      arreter(s)
      s.apres = tic + s.def.repos
    end
  end
end

local function dire(a, hero, texte, emotion)
  cine.Dire(a,emotion,texte,a.Position.X > hero.Position.X and 'droite' or 'standard')
end

local function cadeau(p, a, hero, e)
  local nb = GAME:GetPlayerBagCount()
  local place = nb < _DATA.Save.ActiveTeam:GetMaxInvSlots(_ZONE.CurrentZone)
  local max = _DATA:GetItem(p.objet).MaxStack
  if not place and max > 1 then
    for i = 0,nb-1 do
      local item = GAME:GetPlayerBagItem(i)
      if item.ID == p.objet and not item.Cursed and item.Amount < max then place = true; break end
    end
  end
  if not place then
    dire(a,hero,'Ton sac est plein. Je garde le cadeau pour toi jusqu’à notre prochaine rencontre.',p.emotion)
    return
  end
  dire(a,hero,p.cadeau,p.emotion)
  GAME:GivePlayerItem(p.objet,1,false)
  e[p.id] = p.objet
  UI:ResetSpeaker()
  SOUND:PlayFanfare('Fanfare/Item')
  UI:WaitShowDialogue('Reçu : '..tostring(RogueEssence.Dungeon.InvItem(p.objet):GetDisplayName())..' !')
end

local function duel(p, a, hero, e)
  if e.DernierDuel == 'victoire' then
    dire(a,hero,'Tu m’as bien eue sur le tapis. Encore un tour ? Cette fois, j’essaierai de lire tes pas.',p.emotion)
  elseif e.DernierDuel == 'defaite' then
    dire(a,hero,'Tu veux réessayer ? Ne fixe pas mes pattes : regarde plutôt où je porte mon poids.',p.emotion)
  elseif e.DernierDuel == 'abandon' then
    dire(a,hero,'On peut reprendre quand tu veux. Savoir s’arrêter, ça aussi, ça s’apprend.',p.emotion)
  else
    dire(a,hero,p.texte,p.emotion)
  end
  if _ZONE.CurrentZoneID ~= zone_ville then return end
  dire(a,hero,'Vous deux contre moi, un seul round. Même si vous tombez, on reviendra ici avec le même sac.',p.emotion)
  UI:ResetSpeaker()
  -- Le refus est sélectionné par défaut ; annuler équivaut à refuser.
  UI:BeginChoiceMenu('Défier Liane au dojo ?',{'Accepter le duel','Pas maintenant'},2,2)
  UI:WaitForChoice()
  if tonumber(UI:ChoiceResult()) ~= 1 then
    dire(a,hero,'Alors je continue mon tour. Tu sais où me trouver.', 'Happy')
    return
  end
  local pos = hero.Position
  local partenaire = CH('Teammate1')
  local pp = partenaire and partenaire.Position
  e.DuelEnCours = {carte=_ZONE.CurrentMapID.ID, x=pos.X, y=pos.Y,
    px=pp and pp.X or pos.X-24, py=pp and pp.Y or pos.Y, dir='Down'}
  UI:ResetSpeaker()
  SOUND:PlayBattleSE('EVT_Battle_Transition')
  GAME:FadeOut(false,24)
  GAME:EnterDungeon(zone_duel,0,0,0,RogueEssence.Data.GameProgress.DungeonStakes.None,false,true)
end

function M.Interagir(id, a, hero)
  local s = par_id[id]
  if s == nil or s.parle or not est_actif(a) or not est_actif(hero)
      or hero.EntName ~= 'PLAYER' or not autorises() then return end
  s.parle = true
  arreter(s) -- l'action est stoppée même si le joueur l'aborde en pleine marche
  local ok, erreur = pcall(function()
    local d,e = etat()
    local p = s.def
    cine.RegarderGroupe({{a,hero,0,4},{hero,a,4,4}})
    if p.duel then
      duel(p,a,hero,e)
    elseif p.objet then
      dire(a,hero,e[id] and p.suite or p.texte,p.emotion)
      if not e[id] then cadeau(p,a,hero,e) end
    else
      local texte = d.AlerteShinx == 'termine' and e[id] and p.apres_nilo or (e[id] and p.suite or p.texte)
      dire(a,hero,texte,p.emotion)
      e[id] = not e[id] or nil
    end
  end)
  UI:ResetSpeaker()
  s.parle, s.apres = false, tic + s.def.repos
  if not ok then print('[Destiny] dialogue itinérant '..id..' : '..tostring(erreur)) end
end

function M.AnnulerDuelInterrompu()
  -- Le moteur présauvegarde en ville. Fermer le jeu dans l'arène ne piège
  -- personne dans un combat sans reprise ni même sans choix.
  local d = SV and SV.Destiny
  if d and d.ItinerantsReverie then d.ItinerantsReverie.DuelEnCours = nil end
end

function M.RetourDuel(result)
  local _, e = etat()
  local r = e.DuelEnCours
  local carte = r and r.carte or 21 -- repli : quartier résidentiel (index town02)
  local R = RogueEssence.Data.GameProgress.ResultType
  local bilan = result == R.Cleared and 'victoire'
    or ((result == R.Downed or result == R.Failed) and 'defaite' or 'abandon')
  -- Stakes.None reprend l'état présauvegardé, inventaire compris, et réinstalle
  -- SV. N'écrire le résultat et le point de retour qu'après cet appel.
  GAME:EndDungeonRun(result,zone_ville,-1,carte,0,false,false)
  local d, nouveau = etat()
  nouveau.DuelEnCours = nil
  nouveau.DernierDuel = bilan
  if bilan == 'victoire' then nouveau.DuelRemporte = true end
  d.PassageQuartier = r or {x=920,y=2544,px=896,py=2544,dir='Down'}
  GAME:EnterZone(zone_ville,-1,carte,0)
end

function M.Brancher(carte)
  for _, p in ipairs(defs) do
    local id = p.id
    carte[id..'_Action'] = function(pnj, joueur) M.Interagir(id,pnj,joueur) end
  end
end

return M
