-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local sn4_arid_dungeon_entrance_nuit = {}

function sn4_arid_dungeon_entrance_nuit.Init(map)
end

function sn4_arid_dungeon_entrance_nuit.Enter(map)
  GAME:FadeIn(30)
end

function sn4_arid_dungeon_entrance_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function sn4_arid_dungeon_entrance_nuit.Update(map, time)
end

return sn4_arid_dungeon_entrance_nuit
