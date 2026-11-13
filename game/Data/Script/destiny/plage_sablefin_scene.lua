-- Scène partagée des 4 ambiances de Plage Sablefin (plage_sablefin_*).
-- Raccords :
--   * SortieCarrefour       -> reverie / crossroadreverietown2 / entree_plage
--   * SeuilPassageAquatique -> donjon passage_aquatique (1F-10F)
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local scene = {}
local SON_MER = 'Destiny_Falaise_Mer'
local MUSIQUES = {
  jour = 'Surrounded Sea.ogg',
  aube = 'On the Beach at Dusk.ogg',
  crepuscule = 'On the Beach at Dusk.ogg',
  nuit = 'At the End of the Day.ogg',
}

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function case_libre(map, x, y)
  if x < 0 or y < 0 then return false end
  if map == nil or map.Width == nil or map.Height == nil or map.GetObstacle == nil then
    return x <= 688 and y <= 456
  end
  if x + 16 > map.Width * 8 or y + 16 > map.Height * 8 then return false end
  for cx = math.floor(x / 8), math.floor((x + 15) / 8) do
    for cy = math.floor(y / 8), math.floor((y + 15) / 8) do
      if map:GetObstacle(cx, cy) ~= 0 then return false end
    end
  end
  return true
end

function scene.PositionPartenaire(map, hx, hy)
  local candidats = {
    {24, 0}, {0, 24}, {-24, 0}, {0, -24},
    {16, 16}, {-16, 16}, {16, -16}, {-16, -16},
  }
  for _, d in ipairs(candidats) do
    local px, py = hx + d[1], hy + d[2]
    if case_libre(map, px, py) then return px, py end
  end
  return hx, hy
end

function scene.InitCarte(map, amb, state)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  state.sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
    if map.SetDestinyAmbiance ~= nil then
      pcall(function() map:SetDestinyAmbiance(amb, false) end)
    end
  end
  local hero = CH('PLAYER')
  if hero ~= nil and GAME ~= nil and GAME.GetPlayerPartyCount ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local px, py = scene.PositionPartenaire(map, hero.Position.X, hero.Position.Y)
    local partner = equipe_scene.Partenaire(px, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function scene.SynchroniserAmbiance(carte, state, avec_fondu)
  if not avec_fondu and meteo_reverie.AccesDirectDevSansScenario ~= nil
      and meteo_reverie.AccesDirectDevSansScenario() then
    return false
  end
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  local attendu = meteo_reverie.CartePlageSablefin()
  if attendu == carte then return false end
  if state.sortie_en_cours then return true end
  state.sortie_en_cours = true
  local hero = CH('PLAYER')
  if hero ~= nil and (hero.Position.X > 0 or hero.Position.Y > 0) then
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.PassageAmbiancePlageSablefin = {
      carte = attendu,
      x = hero.Position.X,
      y = hero.Position.Y,
      dir = hero.Direction,
    }
  end
  arreter_mer()
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterZone('passage_aquatique', -1, meteo_reverie.IndexPlageSablefin(), 0)
  return true
end

function scene.RestaurerPassage(map, carte)
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbiancePlageSablefin or nil
  if passage ~= nil and passage.carte == carte then
    SV.Destiny.PassageAmbiancePlageSablefin = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        local px, py = scene.PositionPartenaire(map, passage.x, passage.y)
        GROUND:TeleportTo(partenaire, px, py, passage.dir or hero.Direction)
      end
    end
  end
end

function scene.EnterCarte(map, amb, carte, state)
  state.sortie_en_cours = false
  if scene.SynchroniserAmbiance(carte, state, false) then return end
  scene.RestaurerPassage(map, carte)
  demarrer_mer()
  GAME:FadeIn(20)
  SOUND:PlayBGM(MUSIQUES[amb] or 'Surrounded Sea.ogg', true)
end

function scene.GameLoadCarte(map, amb, carte, state)
  scene.InitCarte(map, amb, state)
  if scene.SynchroniserAmbiance(carte, state, false) then return end
  scene.RestaurerPassage(map, carte)
  demarrer_mer()
  GAME:FadeIn(20)
  SOUND:PlayBGM(MUSIQUES[amb] or 'Surrounded Sea.ogg', true)
end

function scene.ExitCarte()
  arreter_mer()
end

function scene.UpdateCarte(carte, state)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil
      and meteo_reverie.CartePlageSablefin() ~= carte then
    scene.SynchroniserAmbiance(carte, state, true)
  end
end

function scene.SortieCarrefour_Touch(activator, state)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if state.sortie_en_cours then return end
  state.sortie_en_cours = true
  arreter_mer()
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('reverie', 'crossroadreverietown2', 'entree_plage')
end

function scene.SeuilPassageAquatique_Touch(activator, state)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if state.sortie_en_cours then return end
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Entrer dans le Passage Aquatique ?', true)
  UI:WaitForChoice()
  if not UI:ChoiceResult() then return end
  state.sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ExplorationPassageAquatique = true
  arreter_mer()
  SOUND:FadeOutBGM(20)
  GAME:FadeOut(false, 20)
  GAME:EnterDungeon('passage_aquatique', 0, 0, 0, RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
end

return scene
