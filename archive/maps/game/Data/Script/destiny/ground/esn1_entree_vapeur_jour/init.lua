-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local esn1_entree_vapeur_jour = {}

function esn1_entree_vapeur_jour.Init(map)
end

function esn1_entree_vapeur_jour.Enter(map)
  GAME:FadeIn(30)
end

function esn1_entree_vapeur_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function esn1_entree_vapeur_jour.Update(map, time)
end

return esn1_entree_vapeur_jour
