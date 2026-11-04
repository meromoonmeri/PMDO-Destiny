-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_clairiere_tropicale_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fct1_fin_clairiere_tropicale = {}

function fct1_fin_clairiere_tropicale.Init(map)
end

function fct1_fin_clairiere_tropicale.Enter(map)
  GAME:FadeIn(30)
end

function fct1_fin_clairiere_tropicale.GameLoad(map)
  GAME:FadeIn(30)
end

function fct1_fin_clairiere_tropicale.Update(map, time)
end

return fct1_fin_clairiere_tropicale
