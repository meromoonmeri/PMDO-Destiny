--[[ init.lua — cliffdaytest_crepuscule
     Carte d'ambiance de la falaise Cliff : même géométrie, mêmes collisions et
     mêmes objets que cliffdaytest ; seuls le ciel et la teinte changent.
     Aucune scène : ce n'est pas un passage de l'histoire, seulement une heure
     de la même falaise. Cadre bloqué aux limites et ressac sous la musique,
     comme sur la carte de jour.
]]

require 'origin.common'

local cliffdaytest_crepuscule = {}
local SON_MER = 'Destiny_Falaise_Mer'

function cliffdaytest_crepuscule.Init(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
end

function cliffdaytest_crepuscule.Enter(map)
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

function cliffdaytest_crepuscule.Exit(map)
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

return cliffdaytest_crepuscule
