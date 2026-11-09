-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fmb9_fin_mt_blaze = {}

function fmb9_fin_mt_blaze.Init(map)
end

function fmb9_fin_mt_blaze.Enter(map)
  GAME:FadeIn(30)
end

function fmb9_fin_mt_blaze.GameLoad(map)
  GAME:FadeIn(30)
end

function fmb9_fin_mt_blaze.Update(map, time)
end

return fmb9_fin_mt_blaze
