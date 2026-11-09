-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/ruines_enfouies_sanctuaire_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ruines_enfouies_sanctuaire_mew = {}

function ruines_enfouies_sanctuaire_mew.Init(map)
end

function ruines_enfouies_sanctuaire_mew.Enter(map)
  GAME:FadeIn(30)
end

function ruines_enfouies_sanctuaire_mew.GameLoad(map)
  GAME:FadeIn(30)
end

function ruines_enfouies_sanctuaire_mew.Update(map, time)
end

return ruines_enfouies_sanctuaire_mew
