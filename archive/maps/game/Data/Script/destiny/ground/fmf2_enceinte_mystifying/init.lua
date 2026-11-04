-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fmf2_enceinte_mystifying = {}

function fmf2_enceinte_mystifying.Init(map)
end

function fmf2_enceinte_mystifying.Enter(map)
  GAME:FadeIn(30)
end

function fmf2_enceinte_mystifying.GameLoad(map)
  GAME:FadeIn(30)
end

function fmf2_enceinte_mystifying.Update(map, time)
end

return fmf2_enceinte_mystifying
