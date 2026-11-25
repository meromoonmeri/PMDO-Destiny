-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/grotte_ouest_entree_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local grotte_ouest_entree = {}

function grotte_ouest_entree.Init(map)
end

function grotte_ouest_entree.Enter(map)
  GAME:FadeIn(30)
end

function grotte_ouest_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function grotte_ouest_entree.Update(map, time)
end

return grotte_ouest_entree
