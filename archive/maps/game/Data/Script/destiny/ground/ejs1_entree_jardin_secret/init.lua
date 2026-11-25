-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ejs1_entree_jardin_secret = {}

function ejs1_entree_jardin_secret.Init(map)
end

function ejs1_entree_jardin_secret.Enter(map)
  GAME:FadeIn(30)
end

function ejs1_entree_jardin_secret.GameLoad(map)
  GAME:FadeIn(30)
end

function ejs1_entree_jardin_secret.Update(map, time)
end

return ejs1_entree_jardin_secret
