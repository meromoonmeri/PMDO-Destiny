-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local emb9_entree_mt_blaze = {}

function emb9_entree_mt_blaze.Init(map)
end

function emb9_entree_mt_blaze.Enter(map)
  GAME:FadeIn(30)
end

function emb9_entree_mt_blaze.GameLoad(map)
  GAME:FadeIn(30)
end

function emb9_entree_mt_blaze.Update(map, time)
end

return emb9_entree_mt_blaze
