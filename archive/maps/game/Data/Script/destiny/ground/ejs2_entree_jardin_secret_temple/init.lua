-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ejs2_entree_jardin_secret_temple = {}

function ejs2_entree_jardin_secret_temple.Init(map)
end

function ejs2_entree_jardin_secret_temple.Enter(map)
  GAME:FadeIn(30)
end

function ejs2_entree_jardin_secret_temple.GameLoad(map)
  GAME:FadeIn(30)
end

function ejs2_entree_jardin_secret_temple.Update(map, time)
end

return ejs2_entree_jardin_secret_temple
