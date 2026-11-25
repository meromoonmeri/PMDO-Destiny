-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/zekrom_montagne_entree_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local zekrom_montagne_entree = {}

function zekrom_montagne_entree.Init(map)
end

function zekrom_montagne_entree.Enter(map)
  GAME:FadeIn(30)
end

function zekrom_montagne_entree.GameLoad(map)
  GAME:FadeIn(30)
end

function zekrom_montagne_entree.Update(map, time)
end

return zekrom_montagne_entree
