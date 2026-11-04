-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fmf1_clairiere_mystifying = {}

function fmf1_clairiere_mystifying.Init(map)
end

function fmf1_clairiere_mystifying.Enter(map)
  GAME:FadeIn(30)
end

function fmf1_clairiere_mystifying.GameLoad(map)
  GAME:FadeIn(30)
end

function fmf1_clairiere_mystifying.Update(map, time)
end

return fmf1_clairiere_mystifying
