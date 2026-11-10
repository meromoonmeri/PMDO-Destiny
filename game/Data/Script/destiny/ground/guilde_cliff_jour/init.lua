require 'origin.common'
local guilde_cliff_jour = {}

function guilde_cliff_jour.Init(map)
  GAME:FadeIn(20)
  COMMON.RespawnAllies()
  -- Guilde Cliff v5.9 : portail de retour vers WaterfallVillageCapital (pont sud).
  local retour = RogueEssence.Ground.GroundObject()
  retour.EntName = 'RetourVille'
  retour.Collider = RogueElements.Rect(208, 470, 64, 16)
  retour.Passable = false
  retour:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  retour:OnMapInit()
  map:AddObject(retour)
end

function guilde_cliff_jour.RetourVille_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

return guilde_cliff_jour
