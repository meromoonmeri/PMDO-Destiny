-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/ruines_enfouies_entree_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ruines_enfouies_entree = {}

function ruines_enfouies_entree.Init(map)
end

function ruines_enfouies_entree.Enter(map)
  GAME:FadeIn(30)
end

function ruines_enfouies_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function ruines_enfouies_entree.Update(map, time)
end

return ruines_enfouies_entree
