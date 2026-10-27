-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- Carte convertie au format natif PMDO depuis un export « AssetLayers » de
-- l'atelier (voir docs/IMPORT_CREATION_PMDO.md) ; animations natives par tuiles.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Raccordements, rencontres et cinématiques : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local entree_promontoire_nuages_sud_nord_v1 = {}

function entree_promontoire_nuages_sud_nord_v1.Init(map)
end

function entree_promontoire_nuages_sud_nord_v1.Enter(map)
  GAME:FadeIn(30)
end

function entree_promontoire_nuages_sud_nord_v1.GameLoad(map)
  GAME:FadeIn(30)
end

function entree_promontoire_nuages_sud_nord_v1.Update(map, time)
end

return entree_promontoire_nuages_sud_nord_v1
