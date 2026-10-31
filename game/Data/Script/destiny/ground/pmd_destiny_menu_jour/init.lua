-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/pmd_destiny_fangame_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local pmd_destiny_menu_jour = {}

function pmd_destiny_menu_jour.Init(map)
end

function pmd_destiny_menu_jour.Enter(map)
  GAME:FadeIn(30)
end

function pmd_destiny_menu_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function pmd_destiny_menu_jour.Update(map, time)
end

return pmd_destiny_menu_jour
