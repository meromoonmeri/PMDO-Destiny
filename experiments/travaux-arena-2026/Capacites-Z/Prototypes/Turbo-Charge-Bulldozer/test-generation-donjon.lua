-- VFX générés, dans un banc de test en donjon. Aucun dégât ni mouvement Z.
local M={}
function M.jouer()
  local ch=RogueEssence.Dungeon.DungeonScene.Instance.FocusedCharacter
  assert(ch,'Pokémon actif requis dans un donjon.')
  local loc=ch.CharLoc
  local d=RogueEssence.Dungeon
  local c=RogueEssence.Content
  local dirs={{'bas',Direction.Down},{'bas-gauche',Direction.DownLeft},{'gauche',Direction.Left},
    {'haut-gauche',Direction.UpLeft},{'haut',Direction.Up},{'haut-droite',Direction.UpRight},
    {'droite',Direction.Right},{'bas-droite',Direction.DownRight}}
  GAME:CutsceneMode(true)
  GAME:WaitFrames(20)
  for _,v in ipairs(dirs) do
    PrintInfo('[Z GENERE] '..v[1])
    ch.CharDir=v[2]
    DUNGEON:CharSetAction(ch,d.CharAnimIdle(loc,v[2]))
    for _,spec in ipairs({{'Turbo_Genere_Arriere',c.DrawLayer.Bottom},{'Turbo_Genere_Avant',c.DrawLayer.Front}}) do
      local e=c.SingleEmitter();e.Layer=spec[2]
      e.Anim=c.StaticAnim(c.AnimData(spec[1],2,0,31),1,64)
      DUNGEON:PlayVFX(e,loc.X*24+12,loc.Y*24+4,v[2])
    end
    SOUND:PlayBattleSE('DUN_Giga_Impact')
    GAME:WaitFrames(82)
  end
  DUNGEON:CharEndAnim(ch);GAME:CutsceneMode(false)
  PrintInfo('[Z GENERE] fin des huit directions')
end
return M
