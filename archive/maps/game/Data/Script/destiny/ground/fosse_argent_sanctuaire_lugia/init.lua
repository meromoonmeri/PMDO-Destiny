-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fosse_argent_sanctuaire_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fosse_argent_sanctuaire_lugia = {}

function fosse_argent_sanctuaire_lugia.Init(map)
end

function fosse_argent_sanctuaire_lugia.Enter(map)
  GAME:FadeIn(30)
end

function fosse_argent_sanctuaire_lugia.GameLoad(map)
  GAME:FadeIn(30)
end

function fosse_argent_sanctuaire_lugia.Update(map, time)
end

return fosse_argent_sanctuaire_lugia
