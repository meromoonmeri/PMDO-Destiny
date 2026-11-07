-- Maison de l'équipe sur cliffdaytest. Coque issue du PMDO de base (InsideHut).
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local maison = {}
local sortie_en_cours = false

function maison.Init(map)
  sortie_en_cours = false
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local partenaire = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Up)
    if partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  end
end
function maison.Enter(map) GAME:FadeIn(20) end
function maison.GameLoad(map) sortie_en_cours = false; GAME:FadeIn(20) end
function maison.Exit(map) end
function maison.Update(map, time) end
function maison.GameSave(map) end

function maison.SortieMaison_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RetourMaisonEquipe = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest', 'Pichu_Home_Door', true)
end

local function sauvegarder(activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  UI:ResetSpeaker()
  UI:ChoiceMenuYesNo('Sauvegarder votre aventure ?', true)
  UI:WaitForChoice()
  if UI:ChoiceResult() then
    GAME:GroundSave()
    UI:WaitShowDialogue('Votre aventure a été sauvegardée.')
  end
end
function maison.LitEquipe_Action(obj, activator) sauvegarder(activator) end
function maison.LitPartenaire_Action(obj, activator) sauvegarder(activator) end
return maison
