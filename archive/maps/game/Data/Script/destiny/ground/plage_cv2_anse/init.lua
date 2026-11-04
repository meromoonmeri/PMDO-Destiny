-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local plage_cv2_anse = {}

function plage_cv2_anse.Init(map)
end

function plage_cv2_anse.Enter(map)
  GAME:FadeIn(30)
end

function plage_cv2_anse.GameLoad(map)
  GAME:FadeIn(30)
end

function plage_cv2_anse.Update(map, time)
end

return plage_cv2_anse
