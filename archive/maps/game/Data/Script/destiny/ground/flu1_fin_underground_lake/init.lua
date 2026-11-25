-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_underground_lake_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local flu1_fin_underground_lake = {}

function flu1_fin_underground_lake.Init(map)
end

function flu1_fin_underground_lake.Enter(map)
  GAME:FadeIn(30)
end

function flu1_fin_underground_lake.GameLoad(map)
  GAME:FadeIn(30)
end

function flu1_fin_underground_lake.Update(map, time)
end

return flu1_fin_underground_lake
