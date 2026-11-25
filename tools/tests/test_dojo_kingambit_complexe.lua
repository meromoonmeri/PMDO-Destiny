-- Vérification comportementale du complexe Dojo Kingambit (accueil, portes coulissantes sans bris, arène et reliques).
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
package.preload['origin.common'] = function() return {} end
package.preload['destiny.suivi_interieurs'] = function() return {Activer = function() end} end

SV = {Destiny = {}}
local transitions = {}
local steps = {}
local layers = {}
for i = 0, 14 do layers[i] = {Visible = (i <= 8 or i == 11 or i == 14)} end
local mock_map = {Layers = layers}
_ZONE = {CurrentGround = mock_map}
CH = function(n) return {EntName = n, Data = {Nickname = n}} end
Direction = {Up = 4, Down = 0}
GROUND = {EntTurn = function() end}
SOUND = {PlayBattleSE = function(_, se) table.insert(steps, 'SE:' .. se) end}
UI = {
  SetSpeaker = function() end, SetSpeakerEmotion = function() end,
  ResetSpeaker = function() end, WaitShowDialogue = function() end,
}
GAME = {
  CutsceneMode = function() end,
  FadeIn = function() end,
  FadeOut = function() end,
  WaitFrames = function(_, f)
    table.insert(steps, {f, layers[8].Visible, layers[9].Visible, layers[10].Visible, layers[11].Visible, layers[12].Visible, layers[13].Visible})
  end,
  EnterZone = function(_, z) table.insert(transitions, {'zone', z}) end,
  EnterGroundMap = function(_, z, g, m, p) table.insert(transitions, {z, g, m, p}) end,
}

local acc = require('destiny.ground.dojo_kingambit.init')
local are = require('destiny.ground.dojo_kingambit_arene.init')
local rel = require('destiny.ground.dojo_kingambit_reliques.init')

acc.Init(mock_map)
acc.Enter(mock_map)
assert(layers[8].Visible == true and layers[9].Visible == false and layers[10].Visible == false)
assert(layers[11].Visible == true and layers[12].Visible == false and layers[13].Visible == false)

-- Un équipier ne déclenche aucune porte
acc.MarowakDojoDungeonEntrance_Touch({}, {EntName = 'Teammate1'})
acc.KingambitDojoNorthDoorRight_Touch({}, {EntName = 'Teammate1'})
assert(#transitions == 0 and layers[8].Visible == true and layers[11].Visible == true)

-- 1re porte (gauche) : coulisse proprement (8 -> 9 -> 10 -> ouverte) puis mène à l'arène
acc.MarowakDojoDungeonEntrance_Touch({}, {EntName = 'PLAYER'})
assert(SV.Destiny.DojoKingambitPorteGaucheOuverte == true)
assert(layers[8].Visible == false and layers[9].Visible == false and layers[10].Visible == false)
assert(layers[11].Visible == true)
assert(#transitions == 1 and transitions[1][1] == 'dojo_kingambit_salles' and transitions[1][2] == 'dojo_kingambit_arene' and transitions[1][3] == 'entree_sud')

-- Arène -> retour devant la porte gauche déjà ouverte
are.Enter({})
are.EstradeArbitre_Action({}, {EntName = 'PLAYER'})
are.SortieArene_Touch({}, {EntName = 'Teammate1'})
assert(#transitions == 1)
are.SortieArene_Touch({}, {EntName = 'PLAYER'})
assert(#transitions == 2 and transitions[2][1] == 'town02_waterfallvillage' and transitions[2][2] == 'dojo_kingambit' and transitions[2][3] == 'MarowakDojoDungeonEntranceMarker')

-- 2e porte (droite) : coulisse proprement (11 -> 12 -> 13 -> ouverte) puis mène aux reliques
acc.Enter(mock_map)
assert(layers[8].Visible == false and layers[11].Visible == true)
acc.KingambitDojoNorthDoorRight_Touch({}, {EntName = 'PLAYER'})
assert(SV.Destiny.DojoKingambitPorteDroiteOuverte == true)
assert(layers[11].Visible == false and layers[12].Visible == false and layers[13].Visible == false)
assert(#transitions == 3 and transitions[3][1] == 'dojo_kingambit_salles' and transitions[3][2] == 'dojo_kingambit_reliques' and transitions[3][3] == 'entree_sud')

-- Reliques -> inspection et retour devant la porte droite ouverte
rel.Enter({})
rel.MonumentRunesNord_Action({}, {EntName = 'PLAYER'})
rel.ParcheminAncienNE_Action({}, {EntName = 'PLAYER'})
rel.CoffreReliqueNO_Action({}, {EntName = 'PLAYER'})
rel.CoffreReliqueSO_Action({}, {EntName = 'PLAYER'})
rel.CoffreReliqueSE_Action({}, {EntName = 'PLAYER'})
rel.SteleArchiveOuest_Action({}, {EntName = 'PLAYER'})
rel.SteleArchiveEst_Action({}, {EntName = 'PLAYER'})
rel.SortieReliques_Touch({}, {EntName = 'Teammate1'})
assert(#transitions == 3)
rel.SortieReliques_Touch({}, {EntName = 'PLAYER'})
assert(#transitions == 4 and transitions[4][1] == 'town02_waterfallvillage' and transitions[4][2] == 'dojo_kingambit' and transitions[4][3] == 'KingambitDojoNorthDoorRightMarker')

print('PASS test_dojo_kingambit_complexe.lua : portes coulissantes sans bris, arene, reliques et retours OK.')
