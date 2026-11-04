-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local vp1_ia3_arene_glace_boreale = {}

function vp1_ia3_arene_glace_boreale.Init(map)
end

function vp1_ia3_arene_glace_boreale.Enter(map)
  GAME:FadeIn(30)
end

function vp1_ia3_arene_glace_boreale.GameLoad(map)
  GAME:FadeIn(30)
end

function vp1_ia3_arene_glace_boreale.Update(map, time)
end

return vp1_ia3_arene_glace_boreale
