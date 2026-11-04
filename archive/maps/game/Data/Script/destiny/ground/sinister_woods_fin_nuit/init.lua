-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/sinister_woods_fin_nuit_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local sinister_woods_fin_nuit = {}

function sinister_woods_fin_nuit.Init(map)
end

function sinister_woods_fin_nuit.Enter(map)
  GAME:FadeIn(30)
end

function sinister_woods_fin_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function sinister_woods_fin_nuit.Update(map, time)
end

return sinister_woods_fin_nuit
