-- Finales : zéro changement au plateau, à la troupe et à BeginBattleEvent.
-- Seuls le cadre, le noir, la parole et les signaux précèdent le spectacle existant.
local plans = require 'destiny.dojo_kingambit_plans'
local M = {}
local FONDU, NOIR = 26, 32
local SOURCES = {{180,92},{132,116},{228,116}}
local VOLANTES = {
  charizard=true,altaria=true,swablu=true,gastly=true,haunter=true,shuppet=true,
  glalie=true,metang=true,beldum=true,beedrill=true,
}

local function finale(context, args)
  if not context or context.User ~= nil or not args or not plans[args.Type] then return end
  local z, m = _ZONE.CurrentZone, _ZONE.CurrentMap
  if not z or z.ID ~= 'dojo_kingambit_dedales' or not z.CurrentMapID or z.CurrentMapID.ID ~= 2 then return end
  if not m or m.Element ~= args.Type or m.MapTeams.Count ~= 1 or m.MapTeams[0].Players.Count ~= 3 then return end
  return m, plans[args.Type]
end

local function cadre(m, scene, x, y, t)
  -- GAME:MoveCamera est réservé au Ground dans PMDO 0.8.12. En donjon,
  -- ViewCenter est le point monde (Loc?), et le moteur borne le ViewRect.
  local p,v = m.ViewCenter,scene.ViewRect
  local a,b = p and p.X or v.X+math.floor(v.Width/2),p and p.Y or v.Y+math.floor(v.Height/2)
  for i=1,t do
    local s=i/t; s=s*s*(3-2*s)
    m.ViewCenter=RogueElements.Loc(math.floor(a+(x-a)*s+.5),math.floor(b+(y-b)*s+.5))
    GAME:WaitFrames(1)
  end
end

local function portrait(chef,plan)
  local forme=chef.Appearance
  UI:ResetSpeaker()
  UI:SetSpeaker(plan.chef,true,forme.Species,forme.Form,forme.Skin,forme.Gender)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue(plan.replique)
  UI:ResetSpeaker()
end

local function detonner(plan, num)
  local son=plan.sons[num]
  -- Les trois voies ne se superposent pas. Le son est un accent, pas une attaque.
  SOUND:PlayBattleSE(son)
end

local function lumieres(plan, id, scene, map, etat, lancer)
  local c=RogueEssence.Content
  local nom='Kingambit_Signaux_'..id
  local sheet=c.GraphicsManager.GetBackground(nom)
  if not sheet or sheet.TileWidth~=384 or sheet.TileHeight~=288 or sheet.TotalFrames~=16 then
    error('la banque de lumière '..id..' est absente ou ne correspond pas à la scène')
  end
  -- Omnipresent désactive le culling de 24 px du Top ; le dessin
  -- soustrait toujours ViewRect.Start. Le voile reste fixé aux cases.
  local voile=c.OverlayAnim(RogueElements.Loc(-12,-12),c.BGAnimData(nom,6,0,15),
    Color(255,255,255,255),true,RogueElements.Loc(0,0),96,0,0,false,false)
  etat.voile=voile
  DUNGEON:PlayVFXAnim(voile,c.DrawLayer.Top)
  lancer()
  -- Le voile commence pendant le fondu. Chaque marche est de 3 poses × 6 ticks.
  GAME:FadeIn(12)
  etat.noir=false
  GAME:WaitFrames(6)
  for i, idx in ipairs(plan.ordre) do
    detonner(plan,i)
    local x=SOURCES[idx][1]
    cadre(map,scene,180+math.floor((x-180)/4),127,18)
  end
  cadre(map,scene,180,128,18)
  GAME:WaitFrames(8) -- inclut la dernière pose transparente du voile
end

local function voilette(scene, map, plan, args, etat, lancer)
  local equipe=scene.ActiveTeam.Players
  local leader=scene.FocusedCharacter
  local second
  for i=0,equipe.Count-1 do
    if equipe[i] ~= leader and not equipe[i].Dead then second=equipe[i];break end
  end
  GAME:WaitFrames(16) -- une vue d'ensemble avant l'extinction
  SOUND:FadeOutBGM(FONDU)
  etat.silence=true;etat.noir=true
  GAME:FadeOut(false,FONDU)
  -- On recadre dans le noir, pas de saut de caméra au rallumage.
  map.ViewCenter=RogueElements.Loc(180,128)
  GAME:WaitFrames(NOIR)
  UI:ResetSpeaker()
  UI:SetSpeaker('???',true,'',-1,'',RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue(plan.noir)
  UI:ResetSpeaker()
  GAME:WaitFrames(20)
  lumieres(plan,args.Type,scene,map,etat,lancer)
  TASK:JoinCoroutines({etat.entree})
  -- Regard et réaction décalés. Aucun déplacement de case, même en solo.
  local chef=map.MapTeams[0].Players[0]
  if leader then DUNGEON:CharSetEmote(leader,'notice',1) end
  if second then
    GAME:WaitFrames(6)
    if leader then DUNGEON:CharTurnToChar(second,leader) end
    DUNGEON:CharSetEmote(second,'question',1)
    GAME:WaitFrames(14)
    DUNGEON:CharTurnToChar(second,chef)
  else
    GAME:WaitFrames(20)
  end
  if leader then DUNGEON:CharTurnToChar(leader,chef) end
end

local function parole(map, plan)
  local ennemis=map.MapTeams[0].Players
  local chef=ennemis[0]
  -- Pour le portrait les acteurs au sol sont immobiles ; les flottants
  -- reprennent explicitement leur Idle d'espèce malgré CutsceneMode.
  local a=RogueEssence.Dungeon
  local idle=RogueEssence.Content.GraphicsManager.IdleAction
  for i=0,2 do
    local ch=ennemis[i]
    if VOLANTES[ch.CurrentForm.Species] then
      DUNGEON:CharSetAction(ch,a.IdleAnimAction(ch.CharLoc,ch.CharDir,idle))
    else
      DUNGEON:CharSetAction(ch,a.CharAnimNone(ch.CharLoc,ch.CharDir))
    end
  end
  GAME:WaitFrames(24)
  portrait(chef,plan)
  GAME:WaitFrames(20) -- laisser disparaître la boîte avant les bandes
end

function M.Avec(apparition, woosh)
  return function(owner, char, context, args)
    local map,plan=finale(context,args)
    if not map then return end
    local scene=RogueEssence.Dungeon.DungeonScene.Instance
    local mode=_DATA.Save.CutsceneMode
    local centre=map.ViewCenter
    local chanson=SOUND:GetCurrentSong()
    if not chanson or chanson=='' then chanson=map.Music end
    local poses={}
    for i=0,scene.ActiveTeam.Players.Count-1 do
      local ch=scene.ActiveTeam.Players[i]
      poses[#poses+1]={acteur=ch,dir=ch.CharDir}
    end
    local etat={noir=false,silence=false}
    local function apparition_sure()
      local ok,err=pcall(apparition,owner,char,context,args)
      if not ok then
        PrintInfo('[Destiny] Entrée du dojo : '..tostring(err))
        for i=0,2 do DUNGEON:CharEndAnim(map.MapTeams[0].Players[i]) end
      end
    end
    local function lancer()
      -- Recouvrement avec le 3e signal, sans modifier l'animation d'entrée.
      local attente=({fire=32,water=34,flying=44,dragon=48,psychic=44})[args.Type] or args.Pose*4
      etat.entree=TASK:BranchCoroutine(function()
        GAME:WaitFrames(math.max(18,62-attente))
        apparition_sure()
      end)
    end
    GAME:CutsceneMode(true)
    local ok,err=pcall(voilette,scene,map,plan,args,etat,lancer)
    if not ok then
      PrintInfo('[Destiny] Lumières du dojo : '..tostring(err))
      if etat.voile then etat.voile:EndAnim() end
    end
    if etat.noir then pcall(function() GAME:FadeIn(0) end) end
    UI:ResetSpeaker()
    -- Même en l'absence d'un asset, les combattants masqués à -11 sont
    -- toujours restitués par le script d'apparition. Ne jamais le jouer deux fois.
    if not etat.entree then apparition_sure() elseif not ok then TASK:JoinCoroutines({etat.entree}) end
    if ok then
      ok,err=pcall(parole,map,plan)
      if not ok then PrintInfo('[Destiny] Dialogue du dojo : '..tostring(err)) end
    end
    UI:ResetSpeaker()
    for _,p in ipairs(poses) do
      p.acteur.CharDir=p.dir
      DUNGEON:CharSetEmote(p.acteur,'',1)
    end
    for i=0,2 do
      local ch=map.MapTeams[0].Players[i]
      DUNGEON:CharEndAnim(ch)
    end
    map.ViewCenter=centre
    GAME:CutsceneMode(mode)
    woosh(owner,char,context,args)
    if etat.silence and chanson and chanson~='' then SOUND:PlayBGM(chanson,false) end
  end
end

return M
