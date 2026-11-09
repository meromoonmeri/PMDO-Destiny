-- Carte Destiny préexistante : conserver ses calques et ses marqueurs.
-- La Source Méga ajoute un point d'interaction invisible sans réécrire le Ground.
-- Les raccordements scénaristiques et la sortie de la clairière restent à faire.
require 'origin.common'
local source_menu = require 'destiny.source_menu'
local destiny_clairiere_source_lumineuse = {}

local function installer_source(map)
  if map:FindObject('SourceMega') then return end
  local source = RogueEssence.Ground.GroundObject()
  source.EntName = 'SourceMega'
  -- Bord sud du bassin ; le terrain adjacent est accessible depuis les marches.
  source.Collider = RogueElements.Rect(360, 304, 48, 16)
  source:OnMapInit()
  map:AddObject(source)
end

function destiny_clairiere_source_lumineuse.Init(map)
  installer_source(map)
end

function destiny_clairiere_source_lumineuse.Enter(map)
  GAME:FadeIn(30)
end

function destiny_clairiere_source_lumineuse.GameLoad(map)
  installer_source(map)
  GAME:FadeIn(30)
end

function destiny_clairiere_source_lumineuse.Update(map, time)
end

function destiny_clairiere_source_lumineuse.SourceMega_Action(obj, activator)
  -- Passage explicite et réversible, sans inventer de raccord scénaristique.
  source_menu.action(function()
    GAME:FadeOut(false, 20)
    GAME:EnterGroundMap('chapitres_destiny', 'destiny_source_irisee', 'entrance_south')
  end)
end

return destiny_clairiere_source_lumineuse
