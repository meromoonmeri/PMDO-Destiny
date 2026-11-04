-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/great_canyon_entree_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local great_canyon_entree = {}

function great_canyon_entree.Init(map)
end

function great_canyon_entree.Enter(map)
  GAME:FadeIn(30)
end

function great_canyon_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function great_canyon_entree.Update(map, time)
end

return great_canyon_entree
