-- Banc isolé : expérimentation d'une reconstitution de la variante 04.
-- Le fichier ne doit pas être installé tel quel dans Destiny.
local M = {}
function M.jouer()
  local scene = RogueEssence.Dungeon.DungeonScene.Instance
  local ch = scene.FocusedCharacter
  if not ch or ch.BaseForm.Species ~= 'charizard' or ch.BaseForm.Form ~= 0 then
    error('Le leader du banc doit être un Dracaufeu de forme 0')
  end
  local c = RogueEssence.Content
  local loc = ch.CharLoc
  local etat_scene = _DATA.Save.CutsceneMode
  GAME:CutsceneMode(true)
  PrintInfo('[BANC MEGA] début base=' .. ch.BaseForm.Form)
  GAME:WaitFrames(45)
  local e = c.SingleEmitter()
  e.Layer = c.DrawLayer.Front
  e.Anim = c.StaticAnim(c.AnimData('Eclipse_Prism_Test', 2, 0, 143), 1, 288)
  DUNGEON:PlayVFX(e, loc.X*24+12, loc.Y*24+4, Direction.Down)
  SOUND:PlayBattleSE('Eclipse_Prism_Test')
  GAME:WaitFrames(124)
  LTBL(ch).DestinyQI = 410 -- uniquement sur cette sauvegarde jetable
  local ok, raison = require('destiny.mega').evoluer(ch, 1)
  if not ok then error('Promotion impossible : ' .. tostring(raison)) end
  PrintInfo('[BANC MEGA] promotion base=' .. ch.BaseForm.Form)
  GAME:WaitFrames(164)
  GAME:WaitFrames(30)
  local dialogue=dofile('/home/user/Mega-Evolution-in-game/Sources/dialogue_mega_degrade.lua')
  dialogue.afficher_dracaufeu_x()
  GAME:CutsceneMode(etat_scene)
  PrintInfo('[BANC MEGA] dialogue terminé')
end
return M
