-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local atf1_arene_terapagos_fleurie = {}

function atf1_arene_terapagos_fleurie.Init(map)
end

function atf1_arene_terapagos_fleurie.Enter(map)
  GAME:FadeIn(30)
end

function atf1_arene_terapagos_fleurie.GameLoad(map)
  GAME:FadeIn(30)
end

function atf1_arene_terapagos_fleurie.Update(map, time)
end

return atf1_arene_terapagos_fleurie
