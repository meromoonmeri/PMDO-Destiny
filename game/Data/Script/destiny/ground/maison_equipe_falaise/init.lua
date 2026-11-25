-- Maison de l'équipe sur cliffdaytest. Coque issue du PMDO de base (InsideHut).
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'
local maison = {}
local sortie_en_cours = false

function maison.Init(map)
  sortie_en_cours = false

end
function maison.Enter(map) suivi_interieurs.Activer(map); GAME:FadeIn(20) end
function maison.GameLoad(map) if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end; suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function maison.Exit(map) end
function maison.Update(map, time) end
function maison.GameSave(map) end

function maison.SortieMaison_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RetourMaisonEquipe = true
  local retour_falaise = meteo_reverie.CarteCliff()
  SV.Destiny.FalaiseAmbiance = retour_falaise
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('destiny_cliff_tests', retour_falaise, 'Pichu_Home_Door', true)
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
