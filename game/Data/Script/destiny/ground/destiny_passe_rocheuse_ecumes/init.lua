-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte reconstruite depuis son pipeline d'atelier (voir docs/IMPORT_CREATION_PMDO.md).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local destiny_passe_rocheuse_ecumes = {}

function destiny_passe_rocheuse_ecumes.Init(map)
end

function destiny_passe_rocheuse_ecumes.Enter(map)
  GAME:FadeIn(30)
end

function destiny_passe_rocheuse_ecumes.GameLoad(map)
  GAME:FadeIn(30)
end

function destiny_passe_rocheuse_ecumes.Update(map, time)
end

return destiny_passe_rocheuse_ecumes
