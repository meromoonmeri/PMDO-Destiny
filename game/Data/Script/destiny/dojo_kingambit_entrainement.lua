-- Accueil et chutes du dojo ; le dédale et ses combats restent natifs à PMDO.
local types = require 'destiny.dojo_kingambit_types'
local equipe = require 'destiny.equipe_scene'
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
  UI:BeginChoiceMenu('Dédale ' .. t[3] .. ' (' .. t[2] .. ').\nDeux étages, puis le maître. On descend ?', {'Descendre', 'Pas maintenant'}, 2, 2)
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

local function obstacle(map, maitre, x, y)
  if x < 0 or y < 0 or x+16 > map.TexWidth*8 or y+16 > map.TexHeight*8 then return true end
  local p = maitre.Position
  if math.abs(x-p.X) < 16 and math.abs(y-p.Y) < 16 then return true end
  for a = math.floor(x/8), math.floor((x+15)/8) do
    for b = math.floor(y/8), math.floor((y+15)/8) do
      if map:GetObstacle(a,b) ~= 0 then return true end
    end
  end
  return false
end

function M.Descendre(segment, maitre, hero, map)
  local t = types[segment+1]
  if not t then return end
  local partenaire = CH('Teammate1')
  local participants = {hero}
  GAME:CutsceneMode(true)
  -- Le héros n'est jamais déplacé, même quand on aborde Kaito de côté.
  local x, y = hero.Position.X, hero.Position.Y
  if partenaire then
    AI:DisableCharacterAI(partenaire)
    TASK:StopEntityTask(partenaire)
    GROUND:CharEndAnim(partenaire)
    local cote = partenaire.Position.X >= x and 1 or -1
    for _, signe in ipairs({cote, -cote}) do
      local px = x + 22*signe
      if not obstacle(map, maitre, px, y) then
        -- Une courte approche vers le flanc dégagé. En cas de position
        -- inhabituelle, la trappe s'ouvre aussi sous le partenaire, sur place.
        if math.abs(partenaire.Position.X-px) + math.abs(partenaire.Position.Y-y) <= 72 then
          GROUND:MoveToPosition(partenaire, px, y, false, 2)
        end
        break
      end
    end
    participants[2] = partenaire
  end
  local couches = RogueEssence.Content.DrawLayer
  local dessin = RogueEssence.Dungeon.DrawEffect
  local origines = {{x+8, y+12}}
  if partenaire then
    local p = partenaire.Position
    if math.abs(p.X-x) <= 36 and math.abs(p.Y-y) <= 4 then
      origines = {{math.floor((p.X+x)/2)+8, math.floor((p.Y+y)/2)+12}}
    else
      origines[2] = {p.X+8,p.Y+12}
    end
  end
  for _, p in ipairs(origines) do
    effet(t[1], 'Sol', couches.Bottom, p[1],p[2])
    effet(t[1], 'Rebord', couches.Front, p[1],p[2])
  end
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
  if partenaire then equipe.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
  GAME:EnterDungeon(M.Zone, segment, 0, 0,
    RogueEssence.Data.GameProgress.DungeonStakes.Progress, false, true)
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
