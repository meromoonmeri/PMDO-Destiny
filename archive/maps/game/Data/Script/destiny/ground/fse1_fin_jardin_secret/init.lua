-- Squelette de script Destiny pour une carte reconstruite depuis l'atelier projet-creation-pmdo (projet-creation-pmdo source/fin_jardin_secret_v1/build.py).
-- Le script d'origine du paquet généré était une table vide (aucun callback).
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fse1_fin_jardin_secret = {}

function fse1_fin_jardin_secret.Init(map)
end

function fse1_fin_jardin_secret.Enter(map)
  GAME:FadeIn(30)
end

function fse1_fin_jardin_secret.GameLoad(map)
  GAME:FadeIn(30)
end

function fse1_fin_jardin_secret.Update(map, time)
end

return fse1_fin_jardin_secret
