-- Deux événements locaux à chaque finale : préparer avant le fondu natif
-- (-11), jouer après (-9). Le combat natif commence ensuite (-5).
local POSES, TICKS = 16, 4
local PAS = 24
local M = {}
-- Ces durées ne s'appliquent qu'aux quatre entrées révisées.
local CYCLONE = {flying={poses=24, reveler=11, geste='drop'},
                 dragon={poses=24, reveler=12, geste='jump'}}
local METEO = {water={poses=26, amorce=10}, fire={poses=26, amorce=8}}

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

local function jouer_nappe(nom,loc,poses)
  local c = RogueEssence.Content
  local e = c.FiniteOverlayEmitter()
  local n = poses or POSES
  e.Layer = c.DrawLayer.Top
  e.Anim = c.BGAnimData('Kingambit_Entree_' .. nom .. '_Ecran',TICKS,0,n-1)
  e.TotalTime = n*TICKS
  e.RepeatX, e.RepeatY = true, true
  -- Le défilement est dessiné dans chaque pose de la tuile sans raccord.
  DUNGEON:PlayVFX(e,loc.X*PAS+PAS/2,loc.Y*PAS+PAS/2,Direction.Down)
end

local function reveler(ch,mode,de,vers)
  local d = RogueEssence.Dungeon
  local anim
  if mode=='jump' or mode=='emerge' then
    anim=d.CharAnimJump()
    anim.FromLoc, anim.ToLoc, anim.CharDir = de, vers, Direction.Down
  elseif mode=='walk' or mode=='shadow' or mode=='column' then
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
  local cyclone=CYCLONE[args.Type]
  local meteo=METEO[args.Type]
  local amorce=meteo and meteo.amorce or 0
  local poses=cyclone and cyclone.poses or POSES
  local geste=cyclone and cyclone.geste or args.Mode
  local rythme={0,6,12}
  local apparition=(cyclone and cyclone.reveler or args.Pose)*TICKS
  local t=0
  local function avancer(cible)
    if cible>t then GAME:WaitFrames(cible-t); t=cible end
  end
  if meteo then
    jouer_nappe(args.Type,places[1],meteo.poses)
  elseif args.Mode=='whiteout' or args.Mode=='mist' then
    jouer_nappe(args.Type,places[1])
  end
  if args.Mode=='storm' then
    -- Un seul impact ; le Sol dessine le champ statique sur les trois cases.
    jouer_effet(args.Type .. '_Sol',c.DrawLayer.Bottom,places[1],POSES)
    jouer_effet(args.Type .. '_Air',c.DrawLayer.Front,places[1],POSES)
  elseif args.Mode~='whiteout' then
    for i,delai in ipairs(rythme) do
      avancer(amorce+delai)
      -- Chaque membre a son cyclone ou sa colonne. Les colonnes partent
      -- au nord de la formation ; les cyclones restent sur les cases d'arrivée.
      local pivot = (args.Mode=='column' or args.Mode=='emerge') and origines[i] or places[i]
      jouer_effet(args.Type .. '_Sol',c.DrawLayer.Bottom,pivot,poses)
      jouer_effet(args.Type .. '_Air',c.DrawLayer.Front,pivot,poses)
    end
  end
  local delais_revelation = args.Mode=='whiteout' and {0,4,8} or rythme
  for i,delai in ipairs(delais_revelation) do
    avancer(amorce+delai+apparition)
    reveler(ennemis[i-1],geste,cyclone and places[i] or origines[i],places[i])
  end
  local fin = amorce+rythme[3]+poses*TICKS
  avancer(meteo and math.max(fin,meteo.poses*TICKS) or fin)
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
