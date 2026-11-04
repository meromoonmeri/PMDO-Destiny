-- Séquences de cinématique réutilisables de Destiny.
-- Les valeurs suivent les standards PMDO/EoS retenus pour le projet :
-- rotation à 4 frames par pas de 45°, désynchronisations courtes et
-- respiration d'environ 20 frames après une séquence de dialogues.
local cinematique = {}

-- PMDO dessine en 320x240. Le portrait standard fait 56x56 bordure comprise
-- et se place à (8,132), juste au-dessus de la boîte de dialogue. Son
-- pendant de droite est le miroir horizontal (256,132) ; SetSpeakerEmotion
-- reçoit alors reverse=true pour orienter le visage vers le centre.
local PORTRAITS = {
  standard = {8, 132, false},
  droite = {256, 132, true},
}

local function portrait(placement)
  return PORTRAITS[placement or 'standard'] or PORTRAITS.standard
end

function cinematique.PlacerPortrait(placement)
  local p = portrait(placement)
  UI:SetSpeakerLoc(p[1], p[2])
  return p[3]
end

function cinematique.Dire(personnage, emotion, texte, placement)
  UI:SetSpeaker(personnage)
  local reverse = cinematique.PlacerPortrait(placement)
  UI:SetSpeakerEmotion(emotion, reverse)
  UI:WaitShowDialogue(texte)
end

-- Laisser une action ou une fermeture de boîte respirer. 20 frames est le
-- repère PMDO après une séquence de dialogues ; les appels peuvent choisir
-- 10 pour une réaction vive ou 30 pour un moment plus grave.
function cinematique.Respirer(frames)
  GAME:WaitFrames(frames or 20)
end

-- actions : {personnage, Direction, délai, vitesse}. Les rotations se
-- chevauchent au lieu d'attendre chacune la fin de la précédente.
function cinematique.TournerGroupe(actions)
  local taches = {}
  for _, action in ipairs(actions) do
    local a = action
    if a[1] ~= nil then
      table.insert(taches, TASK:BranchCoroutine(function()
        if a[3] ~= nil and a[3] > 0 then GAME:WaitFrames(a[3]) end
        GROUND:CharAnimateTurnTo(a[1], a[2], a[4] or 4)
      end))
    end
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end
end

-- actions : {personnage, cible, délai, vitesse}.
function cinematique.RegarderGroupe(actions)
  local taches = {}
  for _, action in ipairs(actions) do
    local a = action
    if a[1] ~= nil and a[2] ~= nil then
      table.insert(taches, TASK:BranchCoroutine(function()
        if a[3] ~= nil and a[3] > 0 then GAME:WaitFrames(a[3]) end
        GROUND:CharTurnToCharAnimated(a[1], a[2], a[4] or 4)
      end))
    end
  end
  if #taches > 0 then TASK:JoinCoroutines(taches) end
end

-- Le son reste optionnel : lorsqu'un groupe réagit ensemble, un seul appel
-- doit le fournir afin de ne pas couper le SFX précédent.
function cinematique.Emote(personnage, emote, son)
  if personnage == nil then return end
  UI:ResetSpeaker()
  if son ~= nil then SOUND:PlayBattleSE(son) end
  GROUND:CharSetEmote(personnage, emote, 1)
end

-- Prénoms en couleur selon le type principal du Pokémon, comme les noms
-- d'espèces colorés du moteur. La teinte est lue dans le nom coloré
-- renvoyé par _DATA (GetColoredName), avec une table de repli par type.
local COULEURS_TYPES = {
  normal = '#A8A77A', fire = '#EE8130', water = '#6390F0',
  electric = '#F7D02C', grass = '#7AC74C', ice = '#96D9D6',
  fighting = '#C22E28', poison = '#A33EA1', ground = '#E2BF65',
  flying = '#A98FF3', psychic = '#F95587', bug = '#A6B91A',
  rock = '#B6A136', ghost = '#735797', dragon = '#6F35FC',
  dark = '#705746', steel = '#B7B7CE', fairy = '#D685AD',
}
local cache_couleurs_especes = {}

local function hex_depuis_nom_colore(texte)
  if texte == nil then return nil end
  local ok, hex = pcall(function() return tostring(texte):match('%[color=(#%x+)') end)
  if ok then return hex end
  return nil
end

local function couleur_espece(espece)
  if espece == nil or espece == '' then return nil end
  -- Les identifiants d'espèces PMDO sont canoniques en minuscules.
  espece = tostring(espece):lower()
  local en_cache = cache_couleurs_especes[espece]
  if en_cache ~= nil then return en_cache ~= false and en_cache or nil end
  local hex = nil
  local ok, nom = pcall(function() return _DATA:GetMonster(espece):GetColoredName() end)
  if ok then hex = hex_depuis_nom_colore(nom) end
  if hex == nil then
    local ok2, element = pcall(function() return _DATA:GetMonster(espece).Forms[0].Element1 end)
    if ok2 and element ~= nil then hex = COULEURS_TYPES[tostring(element):lower()] end
  end
  cache_couleurs_especes[espece] = hex or false
  return hex
end

local function couleur_reference(reference)
  if type(reference) == 'string' then return couleur_espece(reference) end
  if reference == nil then return nil end
  local ok, espece = pcall(function() return reference.BaseForm.Species end)
  if ok and espece ~= nil then
    local hex = couleur_espece(tostring(espece))
    if hex ~= nil then return hex end
  end
  local ok2, element = pcall(function() return reference.Element1 end)
  if ok2 and element ~= nil then
    local ok3, nom_element = pcall(function() return _DATA:GetElement(element):GetColoredName() end)
    if ok3 then
      local hex = hex_depuis_nom_colore(nom_element)
      if hex ~= nil then return hex end
    end
    return COULEURS_TYPES[tostring(element):lower()]
  end
  return nil
end

-- Colore un prénom (héros, partenaire ou PNJ) selon le type principal :
-- reference peut être un membre d'équipe ou un identifiant d'espèce.
function cinematique.NomColore(nom, reference)
  if nom == nil or nom == '' then return nom end
  local hex = couleur_reference(reference)
  if hex ~= nil then return '[color=' .. hex .. ']' .. nom .. '[color]' end
  return nom
end

-- Nom d'espèce localisé déjà coloré par le moteur (ex. Kangourex, Bekipan).
function cinematique.NomEspece(espece, repli)
  espece = tostring(espece):lower()
  local ok, nom = pcall(function() return _DATA:GetMonster(espece):GetColoredName() end)
  if ok and nom ~= nil and tostring(nom) ~= '' then return tostring(nom) end
  return cinematique.NomColore(repli or espece, espece)
end

return cinematique
