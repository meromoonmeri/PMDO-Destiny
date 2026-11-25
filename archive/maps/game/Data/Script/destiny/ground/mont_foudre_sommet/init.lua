-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local mont_foudre_sommet = {}

function mont_foudre_sommet.Init(map)
end

function mont_foudre_sommet.Enter(map)
  GAME:FadeIn(30)
end

function mont_foudre_sommet.GameLoad(map)
  GAME:FadeIn(30)
end

function mont_foudre_sommet.Update(map, time)
end

return mont_foudre_sommet
