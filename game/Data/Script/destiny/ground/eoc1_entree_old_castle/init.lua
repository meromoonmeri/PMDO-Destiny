-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/entree_old_castle_sud_nord_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local eoc1_entree_old_castle = {}

function eoc1_entree_old_castle.Init(map)
end

function eoc1_entree_old_castle.Enter(map)
  GAME:FadeIn(30)
end

function eoc1_entree_old_castle.GameLoad(map)
  GAME:FadeIn(30)
end

function eoc1_entree_old_castle.Update(map, time)
end

return eoc1_entree_old_castle
