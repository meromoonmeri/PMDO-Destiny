-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/grotte_ouest_sanctuaire_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local grotte_ouest_sanctuaire_mewtwo = {}

function grotte_ouest_sanctuaire_mewtwo.Init(map)
end

function grotte_ouest_sanctuaire_mewtwo.Enter(map)
  GAME:FadeIn(30)
end

function grotte_ouest_sanctuaire_mewtwo.GameLoad(map)
  GAME:FadeIn(30)
end

function grotte_ouest_sanctuaire_mewtwo.Update(map, time)
end

return grotte_ouest_sanctuaire_mewtwo
