-- Accueil et chutes du dojo ; le dédale et ses combats restent natifs à PMDO.
local types = require 'destiny.dojo_kingambit_types'
local equipe = require 'destiny.equipe_scene'
local sceau = require 'destiny.dojo_kingambit_sceau'
local M = {Zone = 'dojo_kingambit_dedales'}

local function etat()
  SV.Destiny = SV.Destiny or {}
  local d = SV.Destiny
  d.EntrainementKingambit = d.EntrainementKingambit or {Reussis = {}}
  return d.EntrainementKingambit
end

function M.Choisir(maitre)
  local fini = (SV.Destiny and SV.Destiny.EntrainementKingambit or {}).Reussis or {}
  local choix = {}
  for i, t in ipairs(types) do
    choix[i] = '[color=' .. t[4] .. ']' .. t[2] .. '[color] — ' .. t[3]
    if fini[t[1]] then choix[i] = choix[i] .. '  [color=#ffd38a]+[color]' end
  end
  local annuler = #types + 1
  choix[annuler] = 'Annuler'
  UI:ResetSpeaker()
  UI:BeginMultiPageMenu(16, 20, 288, 'Dédales d’entraînement', choix, 7, 1, annuler)
  UI:WaitForChoice()
  local i = tonumber(UI:ChoiceResult())
  local t = types[i]
  if not t then return nil end
  UI:SetSpeaker(maitre)
  UI:SetSpeakerEmotion('Normal')
  UI:BeginChoiceMenu('Dédale ' .. t[3] .. ' (' .. t[2] .. ').\nDeux étages, puis le maître et sa troupe. Descendre ?', {'Descendre', 'Pas maintenant'}, 2, 2)
  UI:WaitForChoice()
  local ok = tonumber(UI:ChoiceResult()) == 1
  UI:ResetSpeaker()
  return ok and i-1 or nil
end

local function effet(typ, name, layer, x, y)
  local c = RogueEssence.Content
  local e = c.SingleEmitter()
  e.Layer = layer
  e.Anim = c.StaticAnim(c.AnimData('Kingambit_Trappe_' .. typ .. '_' .. name, 5, 0, 9), 1, 50)
  GROUND:PlayVFX(e, x, y)
end

local function marcher(acteur, chemin)
  for _, p in ipairs(chemin) do
    if acteur.Position.X ~= p.X or acteur.Position.Y ~= p.Y then
      GROUND:MoveToPosition(acteur,p.X,p.Y,false,2.5)
    end
  end
  GROUND:CharAnimateTurnTo(acteur, Direction.Down, 2)
end

local function refuser()
  UI:ResetSpeaker()
  UI:WaitShowDialogue('Le passage jusqu’au sceau n’est pas libre. Approchez-vous ensemble et réessayez.')
  return false
end

function M.Descendre(segment, maitre, joueur, map)
  local t = types[segment+1]
  if not t or not joueur or not maitre or not map then return false end
  local kaito = maitre.Position -- observateur immobile, jamais acteur ni déclencheur de l’effet
  local heros, ih = equipe.Membre('Hero')
  local partenaire, ip = equipe.Membre('Partner')
  local leader = GAME:GetTeamLeaderIndex()
  local inverse = partenaire ~= nil and ip == leader
  local autre = inverse and heros or (not inverse and ih == leader and partenaire or nil)
  if heros and partenaire and not autre then return refuser() end
  local suivant = autre and CH('Teammate1') or nil
  -- Un acteur du chef d'équipe inversé (ou absent d'une vieille sauvegarde)
  -- est créé seulement après validation des trajets, à côté du chef.
  if suivant and suivant.Data ~= autre then suivant = nil end
  local a = joueur.Position
  local b = suivant and suivant.Position or nil
  if autre and not b then
    for _, d in ipairs({{24,0},{-24,0},{0,24},{0,-24}}) do
      if sceau.Libre(map,a.X+d[1],a.Y+d[2],kaito,a) then b={X=a.X+d[1],Y=a.Y+d[2]}; break end
    end
    if not b then return refuser() end
  end
  local cible = sceau.Place(b and (inverse and 1 or -1) or 0)
  local seconde = b and sceau.Place(inverse and -1 or 1) or nil
  local chemin = sceau.Trajet(map,a,cible,kaito,b)
  local chemin2 = b and sceau.Trajet(map,b,seconde,kaito,cible) or nil
  local d_abord = false
  if b and (not chemin or not chemin2) then
    chemin = sceau.Trajet(map,a,cible,kaito,seconde)
    chemin2 = sceau.Trajet(map,b,seconde,kaito,a)
    d_abord = true
  end
  if not chemin or (b and not chemin2) then return refuser() end

  GAME:CutsceneMode(true)
  local participants = {joueur}
  if b then
    if not suivant then
      if CH('Teammate1') then GROUND:RemoveCharacter('Teammate1') end
      suivant = GROUND:CreateCharacterFromCharData('Teammate1',autre,b.X,b.Y,joueur.Direction)
      suivant.CollisionDisabled = true
    end
    AI:DisableCharacterAI(suivant)
    TASK:StopEntityTask(suivant)
    GROUND:CharEndAnim(suivant)
    participants[2] = suivant
  end
  if d_abord then marcher(suivant,chemin2) end
  marcher(joueur,chemin)
  if suivant and not d_abord then marcher(suivant,chemin2) end
  local function pose(c,p) return c.Position.X==p.X and c.Position.Y==p.Y end
  if not pose(joueur,cible) or (suivant and not pose(suivant,seconde)) then
    if suivant then equipe.Suivre(suivant,joueur) end
    GAME:CutsceneMode(false)
    return refuser()
  end
  GAME:WaitFrames(9)
  -- Une seule trappe ; Sol et Rebord sont deux calques au même point.
  local couches = RogueEssence.Content.DrawLayer
  local dessin = RogueEssence.Dungeon.DrawEffect
  effet(t[1], 'Sol', couches.Bottom, sceau.X, sceau.Y)
  effet(t[1], 'Rebord', couches.Front, sceau.X, sceau.Y)
  SOUND:PlayBattleSE('EVT_EP_Pitfall_Reveal')
  GROUND:MoveScreen(RogueEssence.Content.ScreenMover(1, 2, 14))
  GAME:WaitFrames(25)
  -- Les sprites s'enfoncent derrière la lèvre avant. Les masquer à son
  -- contact, sinon le moteur les redessine plus bas par-dessus le dallage.
  SOUND:PlayBattleSE('EVT_EP_Pitfall_Fall')
  local ombres = {}
  for i, c in ipairs(participants) do
    ombres[i] = c.HideShadow
    c.HideShadow = true
    GROUND:CharSetAnim(c, 'Hurt', false)
  end
  for f = 1, 18 do
    local profondeur = math.floor(f*f/9)
    for _, c in ipairs(participants) do
      if f == 11 then GROUND:CharSetDrawEffect(c, dessin.Transparent) end
      if f == 13 then GROUND:CharSetDrawEffect(c, dessin.Absent) end
      c:SetLocHeight(-profondeur)
    end
    GAME:WaitFrames(1)
  end
  GAME:WaitFrames(2)
  GAME:FadeOut(false, 6)
  -- Restaurer l'acteur ground dans le noir avant la présauvegarde moteur.
  for i, c in ipairs(participants) do
    GROUND:CharEndDrawEffect(c, dessin.Absent)
    GROUND:CharEndDrawEffect(c, dessin.Transparent)
    c:SetLocHeight(0)
    c.HideShadow = ombres[i]
    GROUND:CharEndAnim(c)
  end
  GAME:CutsceneMode(false)
  GAME:EnterDungeon(M.Zone, segment, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Progress, false, true)
  return true
end

function M.Retour(result, segment)
  local t = types[segment+1]
  local R = RogueEssence.Data.GameProgress.ResultType
  if t then
    local e = etat()
    local fin = result == R.Cleared and 'victoire'
      or ((result == R.Failed or result == R.Downed) and 'ko')
      or (result == R.TimedOut and 'temps') or 'abandon'
    e.Dernier = {Type = t[1], Issue = fin}
    if fin == 'victoire' then e.Reussis[t[1]] = true end
  end
  -- Progress (et non None/Risk) conserve l'EXP et ne déclenche aucune mise.
  -- Ce marqueur, ajouté en dernier, est loin des seuils et des deux portes.
  local ville, salle, entree = 'town02_waterfallvillage', 17, 3
  GAME:EndDungeonRun(result, ville, -1, salle, entree, false, false)
  GAME:EnterZone(ville, -1, salle, entree)
end

return M
