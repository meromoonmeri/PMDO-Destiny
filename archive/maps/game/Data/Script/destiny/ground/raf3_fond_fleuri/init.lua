-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local raf3_fond_fleuri = {}

function raf3_fond_fleuri.Init(map)
end

function raf3_fond_fleuri.Enter(map)
  GAME:FadeIn(30)
end

function raf3_fond_fleuri.GameLoad(map)
  GAME:FadeIn(30)
end

function raf3_fond_fleuri.Update(map, time)
end

return raf3_fond_fleuri
