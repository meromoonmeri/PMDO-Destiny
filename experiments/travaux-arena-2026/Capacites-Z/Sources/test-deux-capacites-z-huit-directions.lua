-- Banc de test : deux VFX directionnels et des dégâts fixes de démonstration.
-- Ni sélection de capacité, ni formule Z, ni intégration en partie normale.
local M={}
function M.jouer()
  local d=RogueEssence.Dungeon;local c=RogueEssence.Content
  local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
  assert(hero,'Il faut être dans un donjon')
  GAME:CutsceneMode(true)
  -- Trouver une pièce dégagée sur 3x3 pour que les 8 cibles soient accessibles.
  local loc=nil
  for y=2,map.Height-3 do
    for x=2,map.Width-3 do
      local ok=true
      for dy=-1,1 do for dx=-1,1 do
        if map:TileBlocked(RogueElements.Loc(x+dx,y+dy)) then ok=false end
      end end
      if ok then loc=RogueElements.Loc(x,y);break end
    end
    if loc then break end
  end
  assert(loc,'Pas de salle 3x3 libre trouvée')
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(loc,Direction.Down))
  map:UpdateExploration(hero)
  local team=d.MonsterTeam()
  local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('snorlax',0,'normal',Gender.Male),50,'',0)
  team.Players:Add(enemy)
  enemy.CharLoc=RogueElements.Loc(loc.X,loc.Y+1);enemy.CharDir=Direction.Up;enemy:UpdateFrame()
  _DUNGEON:AddTeam(d.Faction.Foe,team);enemy:RefreshTraits();enemy:FullRestore()
  local dirs={{'bas',0,1,Direction.Down,Direction.Up},{'bas-gauche',-1,1,Direction.DownLeft,Direction.UpRight},
    {'gauche',-1,0,Direction.Left,Direction.Right},{'haut-gauche',-1,-1,Direction.UpLeft,Direction.DownRight},
    {'haut',0,-1,Direction.Up,Direction.Down},{'haut-droite',1,-1,Direction.UpRight,Direction.DownLeft},
    {'droite',1,0,Direction.Right,Direction.Left},{'bas-droite',1,1,Direction.DownRight,Direction.UpLeft}}
  local moves={{'PYRO','Pyro_Z_Impact','DUN_Fire_Blast',false},
               {'TOURBILLON','Tourbillon_Z_Cible','DUN_Whirlpool',true}}
  for _,move in ipairs(moves) do
    PrintInfo('[Z 8X] début '..move[1])
    for _,v in ipairs(dirs) do
      local target=RogueElements.Loc(loc.X+v[2],loc.Y+v[3])
      enemy.CharLoc=target;enemy.CharDir=v[5];enemy:UpdateFrame();enemy:FullRestore()
      DUNGEON:CharSetAction(hero,d.CharAnimIdle(loc,v[4]));map:UpdateExploration(hero)
      GAME:WaitFrames(16)
      DUNGEON:CharSetAction(hero,d.CharAnimAction(loc,v[4],5))
      local fx=c.SingleEmitter();fx.Layer=c.DrawLayer.Front
      fx.Anim=c.StaticAnim(c.AnimData(move[2],2,0,31),1,64)
      local origin=move[4] and target or loc
      DUNGEON:PlayVFX(fx,origin.X*24+12,origin.Y*24+4,v[4])
      SOUND:PlayBattleSE(move[3])
      GAME:WaitFrames(30)
      local before=enemy.HP
      TASK:WaitTask(enemy:InflictDamage(10,true))
      PrintInfo('[Z 8X] '..move[1]..' '..v[1]..' '..before..' -> '..enemy.HP)
      GAME:WaitFrames(18)
    end
  end
  DUNGEON:CharEndAnim(hero);GAME:CutsceneMode(false)
  PrintInfo('[Z 8X] fin')
end
return M
