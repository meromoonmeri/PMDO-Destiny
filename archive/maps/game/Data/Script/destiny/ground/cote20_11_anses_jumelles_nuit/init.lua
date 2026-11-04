-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local cote20_11_anses_jumelles_nuit = {}

function cote20_11_anses_jumelles_nuit.Init(map)
end

function cote20_11_anses_jumelles_nuit.Enter(map)
  GAME:FadeIn(30)
end

function cote20_11_anses_jumelles_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function cote20_11_anses_jumelles_nuit.Update(map, time)
end

return cote20_11_anses_jumelles_nuit
