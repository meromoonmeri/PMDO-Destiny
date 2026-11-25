-- Interactions secondaires, jamais appelées à l'entrée d'une carte.
-- Les planches et les comptoirs restent à leur place ; on cadre ce qui existe.
local recit = require 'destiny.reverie_recit'
local cine = require 'destiny.cinematique'
local saynetes = {}

local function pret(a)
  return a ~= nil and a.EntEnabled ~= false and a.Position ~= nil
end

local function est_vue(d, acte, id)
  local v = d.SaynetesReverieVues
  return type(v) == 'table' and type(v[acte]) == 'table' and v[acte][id] == true
end

local function marquer(d, acte, id)
  if type(d.SaynetesReverieVues) ~= 'table' then d.SaynetesReverieVues = {} end
  local v = d.SaynetesReverieVues
  if type(v[acte]) ~= 'table' then v[acte] = {} end
  v[acte][id] = true
end

local function jouer(scene, acte, declencheur, case_libre)
  local hero, partenaire = CH('PLAYER'), CH('Teammate1')
  if not pret(hero) or GAME.GetCurrentGround == nil or GAME.MoveCamera == nil
      or (_DATA and _DATA.Save and _DATA.Save.CutsceneMode) then return false end
  local map = GAME:GetCurrentGround()
  if map == nil then return false end

  -- Pas d'acteur de remplacement ni de téléportation pour assembler le cadre.
  -- Sur une ancienne carte incomplète, la réplique individuelle reste disponible.
  local acteurs, arret = {}, {}
  local minx, maxx, miny, maxy = hero.Position.X, hero.Position.X, hero.Position.Y, hero.Position.Y
  local function memoriser(a)
    local p = a.Position
    minx, maxx = math.min(minx, p.X), math.max(maxx, p.X)
    miny, maxy = math.min(miny, p.Y), math.max(maxy, p.Y)
    arret[#arret+1] = {a=a, dir=a.Direction, ai=a.AIEnabled}
  end
  memoriser(hero)
  if pret(partenaire) and math.abs(partenaire.Position.X-minx) <= 80
      and math.abs(partenaire.Position.Y-miny) <= 64 then
    memoriser(partenaire)
  else
    partenaire = nil
  end
  for i, nom in ipairs(scene.acteurs) do
    local a = CH(nom)
    if not pret(a) or (a.IsInteracting and a ~= declencheur) then return false end
    acteurs[i] = a
    memoriser(a)
  end
  if maxx-minx > 184 or maxy-miny > 100 then return false end
  local axe = math.floor((minx+maxx)/2) + 8
  local hauteur = math.floor((miny+maxy)/2) + 20
  local em = acte == 'alerte' and 'Worried' or (acte == 'nilo' and 'Happy' or 'Normal')
  local initiateur, dernier = acteurs[1], acteurs[#acteurs]
  local function dire(a, emotion, t)
    if t == nil then return end
    cine.Dire(a, emotion, t, a.Position.X + 8 > axe and 'droite' or 'standard')
  end
  local function respirer(f)
    UI:ResetSpeaker()
    cine.Respirer(f)
  end
  local pas, px, py, mobile = scene.pas

  GAME:CutsceneMode(true)
  local ok, erreur = pcall(function()
    for _, s in ipairs(arret) do AI:DisableCharacterAI(s.a) end
    GAME:MoveCamera(axe, hauteur, 18, false)
    cine.RegarderGroupe({{initiateur, hero, 0, 4}, {hero, initiateur, 6, 4}, {partenaire, initiateur, 10, 4}})
    cine.Respirer(10)
    dire(initiateur, em, scene.ouverture)
    respirer(acte == 'alerte' and 21 or 12)

    -- Pip avance jusqu'au carnet, uniquement sur un trajet libre vérifié au sol.
    if pas ~= nil and case_libre ~= nil then
      local a = CH(pas[1])
      local x, y = a.Position.X, a.Position.Y
      if case_libre(map, pas[1], x+pas[2]/2, y+pas[3]/2)
          and case_libre(map, pas[1], x+pas[2], y+pas[3]) then
        mobile, px, py = a, x, y
        GROUND:MoveToPosition(a, x+pas[2], y+pas[3], false, 1)
        cine.Respirer(8)
      end
    end

    if #acteurs > 1 then
      -- Réponse visible avant le changement de portrait : l'un regarde,
      -- l'autre lève la tête quelques images plus tard.
      cine.RegarderGroupe({{dernier, initiateur, 0, 4}, {initiateur, dernier, 5, 4}})
    elseif scene.emote == 'question' then
      cine.TournerGroupe({{initiateur, Direction.Left, 0, 4}})
      cine.Respirer(8)
      cine.RegarderGroupe({{initiateur, hero, 0, 4}})
    end
    if scene.emote ~= nil then cine.Emote(dernier, scene.emote) end
    cine.Respirer(scene.emote == 'happy' and 14 or 19)
    for i, a in ipairs(acteurs) do
      local cible = acteurs[i+1] or hero
      cine.RegarderGroupe({{a, cible, 0, 4}, {cible, a, 4, 4}})
      dire(a, em, recit.Replique(scene.acteurs[i], acte))
      respirer(i == #acteurs and 15 or 8)
    end
    if scene.chute ~= nil then
      cine.RegarderGroupe({{initiateur, hero, 0, 4}, {hero, initiateur, 6, 4}})
      dire(initiateur, em, scene.chute)
      respirer(16)
    end
  end)

  -- Le registre n'est écrit qu'après cette sortie. Ni verrou, ni IA
  -- coupée, ni caméra arrachée au joueur si l'événement n'a pu se jouer.
  UI:ResetSpeaker()
  if mobile ~= nil then
    pcall(function()
      if case_libre(map, pas[1], px, py) then GROUND:MoveToPosition(mobile, px, py, false, 1) end
    end)
  end
  for _, s in ipairs(arret) do
    if s.dir ~= nil then pcall(function() GROUND:EntTurn(s.a, s.dir) end) end
    if s.ai then pcall(function() AI:EnableCharacterAI(s.a) end) end
  end
  pcall(function() GAME:MoveCamera(0, 0, 20, true) end)
  GAME:CutsceneMode(false)
  if not ok then print('[Destiny] saynète Réverie ('..scene.id..') : '..tostring(erreur)) end
  return ok
end

function saynetes.Reagir(d, nom, personne, service, case_libre)
  if d == nil or not pret(personne) or (_DATA and _DATA.Save and _DATA.Save.CutsceneMode) then return false end
  local acte = recit.Acte(d)
  local crique = recit.Crique(d) and 'crique' or nil
  local phases = {}
  if acte then phases[#phases+1] = acte end
  if crique then phases[#phases+1] = crique end
  -- Jouer d'abord le jalon principal. Une nouvelle de la plage ne masque
  -- jamais une saynète de retrouvailles qui n'a pas encore été jouée.
  for _, phase in ipairs(phases) do
    local scene = recit.Scene(nom, phase)
    if scene and not est_vue(d, phase, scene.id) and jouer(scene, phase, personne, case_libre) then
      marquer(d, phase, scene.id)
      return true
    end
  end
  local dernier = crique or acte
  local replique = recit.Replique(nom, dernier)
  if replique == nil then return false end
  if service then
    local scene = recit.Scene(nom, dernier)
    if (scene and est_vue(d, dernier, scene.id)) or est_vue(d, dernier, 'mot:'..nom) then return false end
  end
  UI:SetSpeaker(personne)
  UI:SetSpeakerEmotion(dernier == 'alerte' and 'Worried' or 'Normal')
  UI:WaitShowDialogue(replique)
  UI:ResetSpeaker()
  if service then marquer(d, dernier, 'mot:'..nom) end
  return true
end

return saynetes
