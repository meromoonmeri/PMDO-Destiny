-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/great_canyon_fin_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local great_canyon_fin = {}

function great_canyon_fin.Init(map)
end

function great_canyon_fin.Enter(map)
  GAME:FadeIn(30)
end

function great_canyon_fin.GameLoad(map)
  GAME:FadeIn(30)
end

function great_canyon_fin.Update(map, time)
end

return great_canyon_fin
