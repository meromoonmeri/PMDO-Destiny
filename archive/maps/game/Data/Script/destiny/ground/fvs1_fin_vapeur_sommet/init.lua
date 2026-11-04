-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fvs1_fin_vapeur_sommet = {}

function fvs1_fin_vapeur_sommet.Init(map)
end

function fvs1_fin_vapeur_sommet.Enter(map)
  GAME:FadeIn(30)
end

function fvs1_fin_vapeur_sommet.GameLoad(map)
  GAME:FadeIn(30)
end

function fvs1_fin_vapeur_sommet.Update(map, time)
end

return fvs1_fin_vapeur_sommet
