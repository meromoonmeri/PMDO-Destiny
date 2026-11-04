-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/tiny_woods_fin_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local tiny_woods_fin = {}

function tiny_woods_fin.Init(map)
end

function tiny_woods_fin.Enter(map)
  GAME:FadeIn(30)
end

function tiny_woods_fin.GameLoad(map)
  GAME:FadeIn(30)
end

function tiny_woods_fin.Update(map, time)
end

return tiny_woods_fin
