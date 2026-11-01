-- Ancienne carte de réveil conservée en secours de compatibilité :
-- redirige toute sauvegarde existante vers zrv2_zone_reveil_nuit.
require 'origin.common'

local reveil_nuit = {}

function reveil_nuit.Init(map) end

function reveil_nuit.Enter(map)
  GAME:FadeOut(false, 1)
  GAME:EnterGroundMap('reverie', 'zrv2_zone_reveil_nuit', 'reveil')
end

function reveil_nuit.Exit(map) end
function reveil_nuit.Update(map) end
function reveil_nuit.GameSave(map) end
function reveil_nuit.GameLoad(map)
  GAME:EnterGroundMap('reverie', 'zrv2_zone_reveil_nuit', 'reveil')
end

return reveil_nuit
