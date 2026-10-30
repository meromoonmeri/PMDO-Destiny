-- Quest destiny — point d'entrée du Ground « guilde_parvis ».
-- Le Ground est importé tel quel : ce script ne remplace aucun script d'origine,
-- il fournit seulement les rappels attendus par PMDO 0.8.12.
require 'origin.common'

local guilde_parvis = {}

function guilde_parvis.Init(map)
end

function guilde_parvis.Enter(map)
  GAME:FadeIn(20)
end

function guilde_parvis.GameLoad(map)
  GAME:FadeIn(20)
end

function guilde_parvis.Update(map, time)
end

return guilde_parvis
