-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local zrv2_zone_reveil_jour = {}

function zrv2_zone_reveil_jour.Init(map)
end

function zrv2_zone_reveil_jour.Enter(map)
  GAME:FadeIn(30)
end

function zrv2_zone_reveil_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function zrv2_zone_reveil_jour.Update(map, time)
end

return zrv2_zone_reveil_jour
