-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local mine_magma_arene = {}

function mine_magma_arene.Init(map)
end

function mine_magma_arene.Enter(map)
  GAME:FadeIn(30)
end

function mine_magma_arene.GameLoad(map)
  GAME:FadeIn(30)
end

function mine_magma_arene.Update(map, time)
end

return mine_magma_arene
