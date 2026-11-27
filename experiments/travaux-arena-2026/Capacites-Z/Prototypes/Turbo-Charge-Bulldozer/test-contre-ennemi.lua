-- Banc de test ponctuel : ennemi réel, choc animé et PV réellement réduits.
-- Scénario scripté, dégâts fixes de test ; ce n'est pas la mécanique Z jouable.
local M={}
function M.jouer()
  local d=RogueEssence.Dungeon
  local c=RogueEssence.Content
  local hero=d.DungeonScene.Instance.FocusedCharacter
  assert(hero,'Le joueur doit être dans un donjon.')
  local start=hero.CharLoc
  local map=_ZONE.CurrentMap
  local candidates={
    {1,0,Direction.Right,Direction.Left},
    {0,1,Direction.Down,Direction.Up},
    {-1,0,Direction.Left,Direction.Right},
    {0,-1,Direction.Up,Direction.Down}}
  local choisi=nil
  for _,v in ipairs(candidates) do
    local a=RogueElements.Loc(start.X+v[1],start.Y+v[2])
    local b=RogueElements.Loc(start.X+2*v[1],start.Y+2*v[2])
    if not map:TileBlocked(a) and not map:TileBlocked(b) then choisi=v;break end
  end
  assert(choisi,'Pas de trajectoire libre de deux cases pour le test')
  local dir,rev=choisi[3],choisi[4]
  local cible=RogueElements.Loc(start.X+2*choisi[1],start.Y+2*choisi[2])
  local arrivee=RogueElements.Loc(start.X+choisi[1],start.Y+choisi[2])
  GAME:CutsceneMode(true)
  local team=d.MonsterTeam()
  local id=d.MonsterID('snorlax',0,'normal',Gender.Male)
  local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,id,50,'',0)
  team.Players:Add(enemy)
  enemy.CharLoc=cible
  enemy.CharDir=rev
  enemy:UpdateFrame()
  _DUNGEON:AddTeam(d.Faction.Foe,team)
  map:UpdateExploration(hero)
  PrintInfo('[Z COMBAT] équipe ajoutée')
  enemy:RefreshTraits()
  enemy:FullRestore()
  local before=enemy.HP
  PrintInfo('[Z COMBAT] ennemi Snorlax, PV='..before)
  hero.CharDir=dir
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(start,dir))
  PrintInfo('[Z COMBAT] pose hero ok')
  GAME:WaitFrames(85)
  _DUNGEON:LogMsg('Dracaufeu utilise Turbo-Charge Bulldozer !')
  for _,spec in ipairs({{'Turbo_Genere_Arriere',c.DrawLayer.Bottom},{'Turbo_Genere_Avant',c.DrawLayer.Front}}) do
    local e=c.SingleEmitter();e.Layer=spec[2]
    e.Anim=c.StaticAnim(c.AnimData(spec[1],2,0,31),1,64)
    DUNGEON:PlayVFX(e,arrivee.X*24+12,arrivee.Y*24+4,dir)
  end
  SOUND:PlayBattleSE('DUN_Giga_Impact')
  GAME:WaitFrames(23)
  TASK:WaitTask(hero:StartAnim(d.CharAnimWalk(start,arrivee,dir,3)))
  GAME:WaitFrames(5)
  SOUND:PlayBattleSE('DUN_Hit_Neutral')
  local hit=c.SingleEmitter();hit.Layer=c.DrawLayer.Front
  hit.Anim=c.StaticAnim(c.AnimData('Hit_Neutral',3),1,24)
  DUNGEON:PlayVFX(hit,cible.X*24+12,cible.Y*24+8,dir)
  TASK:WaitTask(enemy:InflictDamage(73,true))
  PrintInfo('[Z COMBAT] touche: PV '..before..' -> '..enemy.HP..' (dégâts fixes scriptés)')
  GAME:WaitFrames(110)
  DUNGEON:CharEndAnim(hero)
  GAME:CutsceneMode(false)
  PrintInfo('[Z COMBAT] FIN')
end
return M
