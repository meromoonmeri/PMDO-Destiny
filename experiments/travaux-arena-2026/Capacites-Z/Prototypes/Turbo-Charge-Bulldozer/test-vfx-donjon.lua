-- Test isolé du VFX ; pas une capacité Z jouable.
local M={}
function M.jouer()
  local ch=RogueEssence.Dungeon.DungeonScene.Instance.FocusedCharacter
  assert(ch,'Il faut un Pokémon actif dans un donjon.')
  local loc=ch.CharLoc
  local d=RogueEssence.Dungeon
  local c=RogueEssence.Content
  local dirs={{'bas',Direction.Down},{'bas-gauche',Direction.DownLeft},{'gauche',Direction.Left},
    {'haut-gauche',Direction.UpLeft},{'haut',Direction.Up},{'haut-droite',Direction.UpRight},
    {'droite',Direction.Right},{'bas-droite',Direction.DownRight}}
  GAME:CutsceneMode(true)
  GAME:WaitFrames(20)
  for _,v in ipairs(dirs) do
    PrintInfo('[Z TEST] '..v[1])
    ch.CharDir=v[2]
    DUNGEON:CharSetAction(ch,d.CharAnimIdle(loc,v[2]))
    local e=c.SingleEmitter()
    e.Layer=c.DrawLayer.Front
    e.Anim=c.StaticAnim(c.AnimData('Turbo_Charge_Z',2,0,23),1,48)
    DUNGEON:PlayVFX(e,loc.X*24+12,loc.Y*24+4,v[2])
    GAME:WaitFrames(60)
  end
  DUNGEON:CharEndAnim(ch)
  GAME:CutsceneMode(false)
  PrintInfo('[Z TEST] fini')
end
return M
