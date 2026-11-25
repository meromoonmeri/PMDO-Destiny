-- Variante PMD des finales Kingambit. Porte BossTransition (Ground) en Dungeon.
-- Format : 4 tiers 256x64, puis leurs miroirs. Seules les traînées changent par type.
local M = {}
local AMORCE, FONDU, BLANC, RETOUR = 4, 30, 10, 12
local GROUPES = {{-32}, {-64, 0}, {-112,48}, {-144,80}, {-176,112}}
local VITESSE = {
  normal={360,360,360,360,360}, fire={336,366,396,426,450}, water={318,336,354,366,378},
  grass={330,360,366,378,396}, electric={408,444,492,468,510}, ice={396,414,426,438,450},
  fighting={330,390,426,450,468}, poison={294,306,330,342,366}, ground={294,312,330,336,360},
  flying={390,420,444,468,486}, psychic={336,378,390,414,426}, bug={372,414,378,432,450},
  rock={294,300,324,342,360}, ghost={300,336,348,372,384}, dragon={342,372,396,420,450},
  dark={330,354,384,426,450}, steel={324,384,384,432,432}, fairy={336,366,396,414,438},
}

local function type_finale(context, args)
  if not context or context.User ~= nil or not args or not VITESSE[args.Type] then return end
  local z,m = _ZONE.CurrentZone,_ZONE.CurrentMap
  if not z or z.ID ~= 'dojo_kingambit_dedales' or not z.CurrentMapID or z.CurrentMapID.ID ~= 2 then return end
  if not m or m.Element ~= args.Type or m.MapTeams.Count ~= 1 or m.MapTeams[0].Players.Count ~= 3 then return end
  return args.Type
end

local function son(nom)
  local ok,err=pcall(function() SOUND:PlayBattleSE(nom) end)
  if not ok then PrintInfo('[Destiny] Son de prébataille : '..tostring(err)) end
end

local function flash(c,x,y)
  local e=c.FlashEmitter()
  e.FadeInTime,e.HoldTime,e.FadeOutTime=2,2,2
  e.StartColor=Color(0,0,0,0)
  e.Layer=c.DrawLayer.Top
  e.Anim=c.BGAnimData('White',0)
  DUNGEON:PlayVFX(e,x,y,Direction.Down)
  son('EVT_Battle_Flash')
end

local function glisser(c,nom,miroirs,x,y,g,id)
  local e=c.FiniteOverlayEmitter()
  local signe=g%2==1 and 1 or -1
  local tier=math.max(0,g-2)
  if miroirs and signe<0 then tier=tier+4 end
  e.Anim=c.BGAnimData(nom,1,tier,tier)
  e.Layer=c.DrawLayer.Top
  e.Movement=RogueElements.Loc(signe*VITESSE[id][g],0)
  e.RepeatX,e.RepeatY=true,false
  e.FadeIn,e.FadeOut=30,0
  -- Le moteur ajoute FadeIn à TotalTime. Les bandes expirent sous le blanc,
  -- deux ticks après le fondu, bien avant de dévoiler le plateau jouable.
  e.TotalTime=92-(g-1)*5-e.FadeIn
  DUNGEON:PlayVFX(e,x,y,Direction.Down)
end

local function passer(id,etat)
  local c=RogueEssence.Content
  local nom='Kingambit_Prebataille_PMD_'..id
  local sheet=c.GraphicsManager.GetBackground(nom)
  local miroirs=sheet and sheet.TileWidth==256 and sheet.TileHeight==64 and sheet.TotalFrames==8
  if not miroirs then
    -- Repli sur les vraies bandes par défaut, pas sur la tuile d’erreur.
    nom='Pre_Battle'
    sheet=c.GraphicsManager.GetBackground(nom)
    if not sheet or sheet.TileWidth~=256 or sheet.TileHeight~=64 or sheet.TotalFrames~=4 then
      error('banques de woosh indisponibles')
    end
  end
  GAME:WaitFrames(AMORCE)
  local v=RogueEssence.Dungeon.DungeonScene.Instance.ViewRect
  if not v or v.Width<1 or v.Height<1 then error('caméra du donjon indisponible') end
  local x,y=v.X+math.floor(v.Width/2),v.Y+math.floor(v.Height/2)
  -- Les deux impulsions et les délais sont ceux de COMMON.BossTransition.
  flash(c,x,y)
  GAME:WaitFrames(16)
  flash(c,x,y)
  GAME:WaitFrames(46)
  son('EVT_Battle_Transition')
  for g,hauteurs in ipairs(GROUPES) do
    if g>1 then GAME:WaitFrames(5) end
    for _,dy in ipairs(hauteurs) do glisser(c,nom,miroirs,x,y+dy,g,id) end
  end
  GAME:WaitFrames(40)
  etat.blanc=true
  GAME:FadeOut(true,FONDU)
  GAME:WaitFrames(BLANC)
  GAME:FadeIn(RETOUR)
  etat.blanc=false
end

function M.Jouer(_owner,_ownerChar,context,args)
  local id=type_finale(context,args)
  if not id then return end
  local mode=_DATA.Save.CutsceneMode
  local etat={blanc=false}
  GAME:CutsceneMode(true)
  local ok,err=pcall(passer,id,etat)
  if etat.blanc then
    -- Une erreur pendant le raccord ne doit pas bloquer le joueur sur le blanc.
    pcall(function() GAME:FadeIn(0) end)
  end
  GAME:CutsceneMode(mode)
  if not ok then PrintInfo('[Destiny] Woosh de prébataille : '..tostring(err)) end
end

function M.Apres(apparition)
  return function(owner,ownerChar,context,args)
    apparition(owner,ownerChar,context,args)
    M.Jouer(owner,ownerChar,context,args)
  end
end

return M
