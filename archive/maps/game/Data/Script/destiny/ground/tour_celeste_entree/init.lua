-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local tour_celeste_entree = {}

function tour_celeste_entree.Init(map)
end

function tour_celeste_entree.Enter(map)
  GAME:FadeIn(30)
end

function tour_celeste_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function tour_celeste_entree.Update(map, time)
end

return tour_celeste_entree
