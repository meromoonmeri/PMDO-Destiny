-- Dojo Kingambit : salle d'accueil raccordée à Réverie Town (Destiny),
-- avec deux portes sarcelle coulissantes au nord (sans bris ni débris) :
--   * Porte gauche (MarowakDojoDungeonEntrance) -> dojo_kingambit_arene (Arène de combat)
--   * Porte droite (KingambitDojoNorthDoorRight) -> dojo_kingambit_reliques (Salle des reliques et archives)
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local dojo_kingambit = {}
local sortie_en_cours = false
local carte_active = nil

local LAYER_GAUCHE_FERMEE = 8
local LAYER_GAUCHE_COULISSE_1 = 9
local LAYER_GAUCHE_COULISSE_2 = 10

local LAYER_DROITE_FERMEE = 11
local LAYER_DROITE_COULISSE_1 = 12
local LAYER_DROITE_COULISSE_2 = 13

local function layer_at(map, idx)
  if map == nil or map.Layers == nil then return nil end
  local ok, lyr = pcall(function() return map.Layers[idx] end)
  if ok and lyr ~= nil then return lyr end
  ok, lyr = pcall(function() return map.Layers:get_Item(idx) end)
  if ok and lyr ~= nil then return lyr end
  return nil
end

local function set_layer_visible(map, idx, vis)
  local lyr = layer_at(map, idx)
  if lyr ~= nil then
    lyr.Visible = vis
  end
end

local function etat_porte_gauche_ouverte()
  return SV ~= nil and SV.Destiny ~= nil and SV.Destiny.DojoKingambitPorteGaucheOuverte == true
end

local function etat_porte_droite_ouverte()
  return SV ~= nil and SV.Destiny ~= nil and SV.Destiny.DojoKingambitPorteDroiteOuverte == true
end

local function appliquer_porte_gauche(map, ouverte)
  set_layer_visible(map, LAYER_GAUCHE_FERMEE, not ouverte)
  set_layer_visible(map, LAYER_GAUCHE_COULISSE_1, false)
  set_layer_visible(map, LAYER_GAUCHE_COULISSE_2, false)
end

local function appliquer_porte_droite(map, ouverte)
  set_layer_visible(map, LAYER_DROITE_FERMEE, not ouverte)
  set_layer_visible(map, LAYER_DROITE_COULISSE_1, false)
  set_layer_visible(map, LAYER_DROITE_COULISSE_2, false)
end

local function appliquer_portes(map)
  carte_active = map or (_ZONE ~= nil and _ZONE.CurrentGround or carte_active)
  appliquer_porte_gauche(carte_active, etat_porte_gauche_ouverte())
  appliquer_porte_droite(carte_active, etat_porte_droite_ouverte())
end

local function jouer_son(se)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    pcall(function() SOUND:PlayBattleSE(se) end)
  end
end

local function attendre(frames)
  if GAME ~= nil and GAME.WaitFrames ~= nil then
    GAME:WaitFrames(frames)
  end
end

local function orienter_joueur_nord()
  if CH == nil or GROUND == nil or Direction == nil then return end
  local ok, hero = pcall(function() return CH('PLAYER') end)
  if ok and hero ~= nil and GROUND.EntTurn ~= nil then
    pcall(function() GROUND:EntTurn(hero, Direction.Up) end)
  end
end

local function coulisser_porte(l_fermee, l_coul1, l_coul2)
  local map = (_ZONE ~= nil and _ZONE.CurrentGround) or carte_active
  orienter_joueur_nord()
  jouer_son('EVT_CH05_Waterfall_Gem_Click')
  attendre(10)
  jouer_son('EVT_Tower_Tremor_Weak')
  set_layer_visible(map, l_fermee, false)
  set_layer_visible(map, l_coul1, true)
  set_layer_visible(map, l_coul2, false)
  attendre(12)
  set_layer_visible(map, l_coul1, false)
  set_layer_visible(map, l_coul2, true)
  attendre(12)
  set_layer_visible(map, l_coul2, false)
  attendre(14)
end

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

local function franchir_porte_gauche(activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  if not etat_porte_gauche_ouverte() then
    if GAME ~= nil and GAME.CutsceneMode ~= nil then pcall(function() GAME:CutsceneMode(true) end) end
    coulisser_porte(LAYER_GAUCHE_FERMEE, LAYER_GAUCHE_COULISSE_1, LAYER_GAUCHE_COULISSE_2)
    SV.Destiny.DojoKingambitPorteGaucheOuverte = true
    if GAME ~= nil and GAME.CutsceneMode ~= nil then pcall(function() GAME:CutsceneMode(false) end) end
  end
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('dojo_kingambit_salles', 'dojo_kingambit_arene', 'entree_sud', true)
end

local function franchir_porte_droite(activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  if not etat_porte_droite_ouverte() then
    if GAME ~= nil and GAME.CutsceneMode ~= nil then pcall(function() GAME:CutsceneMode(true) end) end
    coulisser_porte(LAYER_DROITE_FERMEE, LAYER_DROITE_COULISSE_1, LAYER_DROITE_COULISSE_2)
    SV.Destiny.DojoKingambitPorteDroiteOuverte = true
    if GAME ~= nil and GAME.CutsceneMode ~= nil then pcall(function() GAME:CutsceneMode(false) end) end
  end
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('dojo_kingambit_salles', 'dojo_kingambit_reliques', 'entree_sud', true)
end

local function nommer_maitre()
  local acteur = CH('Kingambit')
  if acteur ~= nil and acteur.Data ~= nil then acteur.Data.Nickname = 'Kaito' end
end
function dojo_kingambit.Init(map) carte_active = map; nommer_maitre(); appliquer_portes(map) end
function dojo_kingambit.Enter(map) appliquer_portes(map); suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit.GameLoad(map) nommer_maitre(); appliquer_portes(map); suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function dojo_kingambit.Update(map, time) end
function dojo_kingambit.MarowakDojoExit_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  sortir()
end

function dojo_kingambit.Kingambit_Action(chara, activator)
  UI:SetSpeaker(chara); UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue("Bienvenue au Dojo Kingambit. Ici, chaque pas compte : on n'entre pas dans l'arène sans savoir pourquoi l'on avance.")
  UI:WaitShowDialogue("À gauche s'ouvre l'arène octogonale des duels ; à droite reposent les reliques et les traités anciens du dojo.")
  UI:ResetSpeaker()
end

function dojo_kingambit.MarowakDojoDungeonEntrance_Touch(obj, activator)
  franchir_porte_gauche(activator)
end
function dojo_kingambit.MarowakDojoDungeonEntrance_Action(obj, activator)
  franchir_porte_gauche(activator)
end

function dojo_kingambit.KingambitDojoNorthDoorRight_Touch(obj, activator)
  franchir_porte_droite(activator)
end
function dojo_kingambit.KingambitDojoNorthDoorRight_Action(obj, activator)
  franchir_porte_droite(activator)
end

return dojo_kingambit
