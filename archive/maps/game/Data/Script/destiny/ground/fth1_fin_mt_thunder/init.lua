-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_mt_thunder_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fth1_fin_mt_thunder = {}

function fth1_fin_mt_thunder.Init(map)
end

function fth1_fin_mt_thunder.Enter(map)
  GAME:FadeIn(30)
end

function fth1_fin_mt_thunder.GameLoad(map)
  GAME:FadeIn(30)
end

function fth1_fin_mt_thunder.Update(map, time)
end

return fth1_fin_mt_thunder
