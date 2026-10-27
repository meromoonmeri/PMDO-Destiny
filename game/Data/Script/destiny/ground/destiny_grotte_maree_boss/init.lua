-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local destiny_grotte_maree_boss = {}

function destiny_grotte_maree_boss.Init(map)
end

function destiny_grotte_maree_boss.Enter(map)
  GAME:FadeIn(30)
end

function destiny_grotte_maree_boss.GameLoad(map)
  GAME:FadeIn(30)
end

function destiny_grotte_maree_boss.Update(map, time)
end

return destiny_grotte_maree_boss
