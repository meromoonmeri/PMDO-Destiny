-- Crique cachée au bout des 10 étages du Passage Aquatique (passage_aquatique_fond).
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local passage_aquatique_fond = {}
local SON_MER = 'Destiny_Falaise_Mer'
local sortie_en_cours = false

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function position_partenaire(map, hx, hy)
  local candidats = {{0, 24}, {-24, 0}, {24, 0}, {0, -24}}
  for _, d in ipairs(candidats) do
    local px, py = hx + d[1], hy + d[2]
    local libre = true
    if map ~= nil and map.GetObstacle ~= nil then
      for cx = math.floor(px / 8), math.floor((px + 15) / 8) do
        for cy = math.floor(py / 8), math.floor((py + 15) / 8) do
          if map:GetObstacle(cx, cy) ~= 0 then libre = false end
        end
      end
    end
    if libre then return px, py end
  end
  return hx, hy
end

function passage_aquatique_fond.Init(map)
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  local hero = CH('PLAYER')
  if hero ~= nil and GAME ~= nil and GAME.GetPlayerPartyCount ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local px, py = position_partenaire(map, hero.Position.X, hero.Position.Y)
    local partner = equipe_scene.Partenaire(px, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function passage_aquatique_fond.Enter(map)
  sortie_en_cours = false
  demarrer_mer()
  GAME:FadeIn(20)
  SOUND:PlayBGM('On the Beach at Dusk.ogg', true)
end

function passage_aquatique_fond.GameLoad(map)
  passage_aquatique_fond.Init(map)
  demarrer_mer()
  GAME:FadeIn(20)
  SOUND:PlayBGM('On the Beach at Dusk.ogg', true)
end

function passage_aquatique_fond.Exit(map)
  arreter_mer()
end

function passage_aquatique_fond.GameSave(map) end
function passage_aquatique_fond.Update(map, time) end

function passage_aquatique_fond.PointVueOcean_Action(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  UI:ResetSpeaker()
  UI:WaitShowDialogue("Au bout du tunnel marin, une crique secrète s'ouvre sur l'océan infini.")
end

function passage_aquatique_fond.PointVueOcean_Touch(obj, activator)
end

function passage_aquatique_fond.SortieTunnelSud_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Revenir vers Plage Sablefin ?', true)
  UI:WaitForChoice()
  if not UI:ChoiceResult() then return end
  sortie_en_cours = true
  arreter_mer()
  SOUND:FadeOutBGM(20)
  GAME:FadeOut(false, 20)
  local en_donjon = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.ExplorationPassageAquatique == true
  if en_donjon then
    SV.Destiny.ExplorationPassageAquatique = nil
    local idx_plage = meteo_reverie.IndexPlageSablefin ~= nil and meteo_reverie.IndexPlageSablefin() or 0
    COMMON.EndDungeonDay(RogueEssence.Data.GameProgress.ResultType.Cleared, 'passage_aquatique', -1, idx_plage, 2)
  else
    local carte_plage = meteo_reverie.CartePlageSablefin ~= nil and meteo_reverie.CartePlageSablefin() or 'plage_sablefin_jour'
    GAME:EnterGroundMap('passage_aquatique', carte_plage, 'retour_grotte')
  end
end

return passage_aquatique_fond
