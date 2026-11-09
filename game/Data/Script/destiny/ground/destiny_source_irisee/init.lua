-- Source irisée : adaptation de la carte de référence et des calques d'atelier.
-- Le sol et les collisions d'origine sont conservés ; voir docs/SOURCE_IRISEE.md.
-- Une liaison réversible vers la clairière existante est un accès provisoire,
-- pas un raccordement narratif considéré comme final.
require 'origin.common'
local evolution_native = require 'origin.ground.luminous_spring.init'
local source_menu = require 'destiny.source_menu'
local destiny_source_irisee = {}

function destiny_source_irisee.Init(map)
  SV.luminous_spring = SV.luminous_spring or { Returning = false }
  COMMON.RespawnAllies()
end

function destiny_source_irisee.Enter(map)
  SV.luminous_spring.Returning = false
  GAME:FadeIn(20)
end

function destiny_source_irisee.GameLoad(map)
  GAME:FadeIn(20)
end

function destiny_source_irisee.Update(map, time)
end

function destiny_source_irisee.Spring_Touch(obj, activator)
  GAME:CutsceneMode(true)
  -- Montrer la colonne irisée avant le choix, comme dans le rituel natif.
  GAME:MoveCamera(300, 152, 45, false)
  UI:ResetSpeaker()
  local choix = { 'Évoluer', 'Mégaévoluer ou consulter le QI', 'Partir' }
  UI:BeginChoiceMenu('La Source irisée pulse doucement...', choix, 1, #choix)
  UI:WaitForChoice()
  local resultat = UI:ChoiceResult()
  GAME:CutsceneMode(false)
  if resultat == 1 then
    -- Conserve le système, les exigences et la cinématique d'évolution natifs.
    evolution_native.Spring_Touch(obj, activator)
  elseif resultat == 2 then
    source_menu.action(nil)
  end
  -- Le rituel natif remet la caméra à zéro ; retrouver le cadrage de la Source.
  GAME:CutsceneMode(true)
  GAME:MoveCamera(0, -64, 30, true)
  GAME:CutsceneMode(false)
end

function destiny_source_irisee.South_Exit_Touch(obj, activator)
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('chapitres_destiny', 'destiny_clairiere_source_lumineuse', 'entrance')
end

function destiny_source_irisee.Assembly_Action(obj, activator)
  evolution_native.Assembly_Action(obj, activator)
end

function destiny_source_irisee.Storage_Action(obj, activator)
  evolution_native.Storage_Action(obj, activator)
end

function destiny_source_irisee.Teammate1_Action(chara, activator)
  COMMON.GroundInteract(activator, chara)
end
function destiny_source_irisee.Teammate2_Action(chara, activator)
  COMMON.GroundInteract(activator, chara)
end
function destiny_source_irisee.Teammate3_Action(chara, activator)
  COMMON.GroundInteract(activator, chara)
end

return destiny_source_irisee
