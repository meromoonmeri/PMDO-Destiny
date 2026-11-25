-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/entree_caverne_cristal_sud_nord_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ekr1_entree_caverne_cristal = {}

function ekr1_entree_caverne_cristal.Init(map)
end

function ekr1_entree_caverne_cristal.Enter(map)
  GAME:FadeIn(30)
end

function ekr1_entree_caverne_cristal.GameLoad(map)
  GAME:FadeIn(30)
end

function ekr1_entree_caverne_cristal.Update(map, time)
end

return ekr1_entree_caverne_cristal
