-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_mystifying_forest_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fmy1_fin_mystifying_forest = {}

function fmy1_fin_mystifying_forest.Init(map)
end

function fmy1_fin_mystifying_forest.Enter(map)
  GAME:FadeIn(30)
end

function fmy1_fin_mystifying_forest.GameLoad(map)
  GAME:FadeIn(30)
end

function fmy1_fin_mystifying_forest.Update(map, time)
end

return fmy1_fin_mystifying_forest
