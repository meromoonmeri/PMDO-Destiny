require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'
local guilde_effectif = require 'destiny.guilde_effectif'

local guilde_destiny_refectoire = {}
local sortie_en_cours = false

-- Deux rangs sur le plancher existant ; les accès est et central restent libres.
local places = {
  {'Canarticho', 184, 216, 'Down'}, {'Gardevoir', 232, 216, 'Down'},
  {'Simisage', 280, 216, 'Down'}, {'Melofee', 328, 216, 'Down'},
  {'Noctali', 376, 216, 'Down'}, {'Cizayox', 184, 280, 'Up'},
  {'Dimoret', 232, 280, 'Up'}, {'Draby', 280, 280, 'Up'},
  {'Pandespiegle', 328, 280, 'Up'}, {'Capumain', 376, 280, 'Up'},
}

local function repas_en_cours()
  for _, place in ipairs(places) do
    guilde_effectif.InstallerConvive(guilde_effectif.Membre(place[1]), place[2], place[3], Direction[place[4]])
  end
  guilde_effectif.RepasImmediat()
end

for _, place in ipairs(places) do
  local membre = guilde_effectif.Membre(place[1])
  guilde_destiny_refectoire[membre.id .. '_Action'] = function(acteur, activator)
    if activator == nil or activator.EntName ~= 'PLAYER' then return end
    GROUND:CharEndAnim(acteur)
    GROUND:CharSetEmote(acteur, '', 0)
    GROUND:CharTurnToChar(acteur, activator)
    UI:SetSpeaker(acteur)
    UI:WaitShowDialogue(membre.role .. '.\n' .. membre.accueil)
    UI:ResetSpeaker()
    GROUND:EntTurn(acteur, Direction[place[4]])
    guilde_effectif.Manger(acteur, membre, 0)
  end
end

function guilde_destiny_refectoire.Init(map)
  sortie_en_cours = false
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_refectoire')
end

function guilde_destiny_refectoire.Enter(map)
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_refectoire')
  suivi_interieurs.Activer(map)
  repas_en_cours()
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_refectoire.GameLoad(map)
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_refectoire')
  suivi_interieurs.Activer(map)
  repas_en_cours()
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_refectoire.Exit(map)
end

function guilde_destiny_refectoire.Update(map)
  guilde_decors.SynchroniserAmbiance(map, 'guilde_destiny_refectoire')
end

function guilde_destiny_refectoire.SortieEst_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_carrefour', 'EntreeOuestMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 4, 0) end
end

return guilde_destiny_refectoire
