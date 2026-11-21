-- Deux événements locaux à chaque finale : préparer avant le fondu natif
-- (-11), jouer après (-9). Le combat natif commence ensuite (-5).
local POSES, TICKS = 16, 4
local PAS = 24
local M = {}

local function troupe(context,args)
  if not context or context.User ~= nil or not args or not _ZONE.CurrentZone
      or _ZONE.CurrentZone.ID ~= 'dojo_kingambit_dedales' then return end
  local map = _ZONE.CurrentMap
  if not map or _ZONE.CurrentZone.CurrentMapID.ID ~= 2 or map.Element ~= args.Type then return end
  if map.MapTeams.Count ~= 1 or map.MapTeams[0].Players.Count ~= 3 then return end
  return map.MapTeams[0].Players
end

local function poser(ch,loc,visible)
  local d = RogueEssence.Dungeon
  local anim = visible and d.CharAnimIdle(loc, Direction.Down) or d.CharAbsentAnim(loc, Direction.Down)
  DUNGEON:CharSetAction(ch,anim)
end

local function jouer_effet(nom,layer,loc,poses)
  local c = RogueEssence.Content
  local e = c.SingleEmitter()
  e.Layer = layer
  e.Anim = c.StaticAnim(c.AnimData('Kingambit_Entree_' .. nom,TICKS,0,poses-1),1,TICKS*poses)
  DUNGEON:PlayVFX(e,loc.X*PAS+PAS/2,loc.Y*PAS+PAS/2,Direction.Down)
end

local function reveler(ch,mode,de,vers)
  local d = RogueEssence.Dungeon
  local anim
  if mode=='jump' then
    anim=d.CharAnimJump()
    anim.FromLoc, anim.ToLoc, anim.CharDir = de, vers, Direction.Down
  elseif mode=='walk' or mode=='shadow' then
    local direction = Direction.Down
    if de.X < vers.X then direction=Direction.Right elseif de.X > vers.X then direction=Direction.Left end
    anim=d.CharAnimWalk(de,vers,direction,1)
  elseif mode=='drop' then
    anim=d.CharAnimDrop()
    anim.AnimLoc, anim.CharDir = vers, Direction.Down
  else
    anim=d.CharAnimIdle(vers,Direction.Down)
  end
  DUNGEON:CharSetAction(ch,anim)
end

local function choregraphie(ennemis,args,places)
  local c = RogueEssence.Content
  local origines = {}
  for i=1,3 do
    local p=args.Origines[i]
    origines[i]=RogueElements.Loc(p[1],p[2])
  end
  SOUND:PlayBattleSE('Kingambit_Whoosh_' .. args.Type)
  if args.Mode=='warp' then
    -- Un départ et une arrivée distincts : les corps disparaissent de leurs
    -- cases à l'arrière au lieu de simplement s'afficher sous la lumière.
    for i=1,3 do poser(ennemis[i-1],origines[i],true) end
    GAME:WaitFrames(8)
    for i=1,3 do jouer_effet('psychic_Depart',c.DrawLayer.Front,origines[i],6) end
    GAME:WaitFrames(8)
    for i=1,3 do poser(ennemis[i-1],origines[i],false) end
    GAME:WaitFrames(4)
  end
  local rythme={0,6,12}
  local apparition=args.Pose*TICKS
  local t=0
  local function avancer(cible)
    if cible>t then GAME:WaitFrames(cible-t); t=cible end
  end
  for i,delai in ipairs(rythme) do
    avancer(delai)
    jouer_effet(args.Type .. '_Sol',c.DrawLayer.Bottom,places[i],POSES)
    jouer_effet(args.Type .. '_Air',c.DrawLayer.Front,places[i],POSES)
  end
  for i,delai in ipairs(rythme) do
    avancer(delai+apparition)
    reveler(ennemis[i-1],args.Mode,origines[i],places[i])
  end
  avancer(rythme[3]+POSES*TICKS)
end

function M.Masquer(_owner,_ownerChar,context,args)
  local ennemis=troupe(context,args)
  if not ennemis then return end
  for i=0,2 do poser(ennemis[i],ennemis[i].CharLoc,false) end
end

function M.Jouer(_owner,_ownerChar,context,args)
  local ennemis=troupe(context,args)
  if not ennemis then return end
  local places={ennemis[0].CharLoc,ennemis[1].CharLoc,ennemis[2].CharLoc}
  local cinematique=_DATA.Save.CutsceneMode
  GAME:CutsceneMode(true)
  local ok,err=pcall(choregraphie,ennemis,args,places)
  -- Rétablir positions et poses même si une ressource de scène manque. Ni
  -- combats, ni PP, ni statuts, ni ordre des tours ne dépendent de la scène.
  for i,p in ipairs(places) do poser(ennemis[i-1],p,true) end
  GAME:CutsceneMode(cinematique)
  if not ok then PrintInfo('[Destiny] Introduction de troupe : ' .. tostring(err)) end
end

return M
