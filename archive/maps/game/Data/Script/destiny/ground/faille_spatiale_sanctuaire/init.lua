-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local faille_spatiale_sanctuaire = {}

function faille_spatiale_sanctuaire.Init(map)
end

function faille_spatiale_sanctuaire.Enter(map)
  GAME:FadeIn(30)
end

function faille_spatiale_sanctuaire.GameLoad(map)
  GAME:FadeIn(30)
end

function faille_spatiale_sanctuaire.Update(map, time)
end

return faille_spatiale_sanctuaire
