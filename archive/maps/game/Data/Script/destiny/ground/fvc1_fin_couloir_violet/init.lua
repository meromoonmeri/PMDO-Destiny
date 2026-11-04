-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_couloir_violet_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fvc1_fin_couloir_violet = {}

function fvc1_fin_couloir_violet.Init(map)
end

function fvc1_fin_couloir_violet.Enter(map)
  GAME:FadeIn(30)
end

function fvc1_fin_couloir_violet.GameLoad(map)
  GAME:FadeIn(30)
end

function fvc1_fin_couloir_violet.Update(map, time)
end

return fvc1_fin_couloir_violet
