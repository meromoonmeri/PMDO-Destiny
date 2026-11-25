-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local guild_path = {}

function guild_path.Init(map)
end

function guild_path.Enter(map)
  GAME:FadeIn(30)
end

function guild_path.GameLoad(map)
  GAME:FadeIn(30)
end

function guild_path.Update(map, time)
end

return guild_path
