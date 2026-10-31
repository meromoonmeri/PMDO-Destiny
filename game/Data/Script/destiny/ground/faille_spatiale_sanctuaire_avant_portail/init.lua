-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/faille_spatiale_sanctuaire_avant_portail_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local faille_spatiale_sanctuaire_avant_portail = {}

function faille_spatiale_sanctuaire_avant_portail.Init(map)
end

function faille_spatiale_sanctuaire_avant_portail.Enter(map)
  GAME:FadeIn(30)
end

function faille_spatiale_sanctuaire_avant_portail.GameLoad(map)
  GAME:FadeIn(30)
end

function faille_spatiale_sanctuaire_avant_portail.Update(map, time)
end

return faille_spatiale_sanctuaire_avant_portail
