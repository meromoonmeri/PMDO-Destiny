-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- NOTE : cette falaise porte la cinématique « Pichu & la Team Dazzling » dans l'atelier ;
-- volontairement INACTIVE ici (décision Partie 2) — les personnages placés sur la carte
-- restent immobiles. Le script d'origine est dans l'atelier (voir docs/IMPORT_CREATION_PMDO.md).
require 'origin.common'

local cliffdaytest_nuit = {}

function cliffdaytest_nuit.Init(map)
end

function cliffdaytest_nuit.Enter(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function cliffdaytest_nuit.Update(map, time)
end

return cliffdaytest_nuit
