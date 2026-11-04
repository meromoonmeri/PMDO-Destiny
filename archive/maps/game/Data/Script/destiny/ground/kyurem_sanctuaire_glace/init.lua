-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/kyurem_sanctuaire_glace_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local kyurem_sanctuaire_glace = {}

function kyurem_sanctuaire_glace.Init(map)
end

function kyurem_sanctuaire_glace.Enter(map)
  GAME:FadeIn(30)
end

function kyurem_sanctuaire_glace.GameLoad(map)
  GAME:FadeIn(30)
end

function kyurem_sanctuaire_glace.Update(map, time)
end

return kyurem_sanctuaire_glace
