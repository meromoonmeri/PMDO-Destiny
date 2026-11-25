-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/sinister_woods_entree_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local sinister_woods_entree = {}

function sinister_woods_entree.Init(map)
end

function sinister_woods_entree.Enter(map)
  GAME:FadeIn(30)
end

function sinister_woods_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function sinister_woods_entree.Update(map, time)
end

return sinister_woods_entree
