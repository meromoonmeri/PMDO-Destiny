-- Woosh plein écran des dix-huit finales, APRÈS l'apparition de la troupe.
-- Même principe que le Woosh Dazzling, mais sans changement de carte ni flash blanc.
-- 28 poses × 3 ticks : PNG prémultiplié dans une DirSheet BG, non répétée.
local M = {}
local W, H, POSES, TICKS = 320, 240, 28, 3
local AMORCE, FIN = 4, 2
local IDS = {
  normal=true, fire=true, water=true, grass=true, electric=true, ice=true,
  fighting=true, poison=true, ground=true, flying=true, psychic=true, bug=true,
  rock=true, ghost=true, dragon=true, dark=true, steel=true, fairy=true,
}

local function final_type(context,args)
  if not context or context.User ~= nil or not args or not IDS[args.Type] then return end
  local z,m = _ZONE.CurrentZone,_ZONE.CurrentMap
  if not z or z.ID ~= 'dojo_kingambit_dedales' or not z.CurrentMapID or z.CurrentMapID.ID ~= 2 then return end
  if not m or m.Element ~= args.Type or m.MapTeams.Count ~= 1 or m.MapTeams[0].Players.Count ~= 3 then return end
  return args.Type
end

local function passer(id)
  local c = RogueEssence.Content
  local nom = 'Kingambit_Prebataille_' .. id
  -- En cas d'installation incomplète, ne pas jouer le sprite de secours du moteur.
  local sheet = c.GraphicsManager.GetBackground(nom)
  if not sheet or sheet.TileWidth ~= W or sheet.TileHeight ~= H or sheet.TotalFrames ~= POSES then
    error('banque non chargée : ' .. nom)
  end
  GAME:WaitFrames(AMORCE)
  -- GAME:GetCameraCenter() pointe sur GroundScene. En donjon on lit le
  -- rectangle réellement affiché, y compris près des bords d'une arène.
  local v = RogueEssence.Dungeon.DungeonScene.Instance.ViewRect
  if v.Width < 1 or v.Height < 1 then error('caméra du donjon indisponible') end
  local x = v.X + math.floor((v.Width-W)/2)
  local y = v.Y + math.floor((v.Height-H)/2)
  local e = c.FiniteOverlayEmitter()
  e.Layer = c.DrawLayer.Top
  e.Anim = c.BGAnimData(nom,TICKS,0,POSES-1)
  e.RepeatX,e.RepeatY = false,false
  e.FadeIn,e.FadeOut,e.TotalTime = 0,0,POSES*TICKS
  DUNGEON:PlayVFX(e,x,y,Direction.Down)
  local sonore, err = pcall(function() SOUND:PlayBattleSE(nom) end)
  if not sonore then PrintInfo('[Destiny] Son de prébataille : ' .. tostring(err)) end
  -- Les première/dernière images sont transparentes ; l'événement natif
  -- suivant (-5) reçoit la main après expiration de l'overlay.
  GAME:WaitFrames(POSES*TICKS+FIN)
end

function M.Jouer(_owner,_ownerChar,context,args)
  local id = final_type(context,args)
  if not id then return end
  local mode = _DATA.Save.CutsceneMode
  GAME:CutsceneMode(true)
  local ok,err = pcall(passer,id)
  GAME:CutsceneMode(mode)
  if not ok then PrintInfo('[Destiny] Woosh de prébataille : ' .. tostring(err)) end
end

function M.Apres(apparition)
  return function(owner,ownerChar,context,args)
    apparition(owner,ownerChar,context,args)
    M.Jouer(owner,ownerChar,context,args)
  end
end

return M
