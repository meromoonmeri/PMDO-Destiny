-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local zrv2_zone_reveil_crepuscule = {}

function zrv2_zone_reveil_crepuscule.Init(map)
end

function zrv2_zone_reveil_crepuscule.Enter(map)
  GAME:FadeIn(30)
end

function zrv2_zone_reveil_crepuscule.GameLoad(map)
  GAME:FadeIn(30)
end

function zrv2_zone_reveil_crepuscule.Update(map, time)
end

return zrv2_zone_reveil_crepuscule
