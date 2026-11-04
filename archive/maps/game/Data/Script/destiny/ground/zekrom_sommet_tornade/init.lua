-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/zekrom_sommet_tornade_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local zekrom_sommet_tornade = {}

function zekrom_sommet_tornade.Init(map)
end

function zekrom_sommet_tornade.Enter(map)
  GAME:FadeIn(30)
end

function zekrom_sommet_tornade.GameLoad(map)
  GAME:FadeIn(30)
end

function zekrom_sommet_tornade.Update(map, time)
end

return zekrom_sommet_tornade
