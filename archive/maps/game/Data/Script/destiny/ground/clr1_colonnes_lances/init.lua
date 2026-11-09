-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local clr1_colonnes_lances = {}

function clr1_colonnes_lances.Init(map)
end

function clr1_colonnes_lances.Enter(map)
  GAME:FadeIn(30)
end

function clr1_colonnes_lances.GameLoad(map)
  GAME:FadeIn(30)
end

function clr1_colonnes_lances.Update(map, time)
end

return clr1_colonnes_lances
