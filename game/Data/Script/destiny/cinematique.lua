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

return cinematique
