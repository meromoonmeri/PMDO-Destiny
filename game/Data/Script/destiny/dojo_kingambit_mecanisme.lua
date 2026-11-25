-- Serrurerie et chute : un seul ancrage, deux plans et aucune collision nouvelle.
local M = {}
local SCENE = {frames=24, ticks=4, chute=52, decalage=4, fondu=12}
local ANCIENNE = {frames=10,ticks=5,chute=25,decalage=0,fondu=6}

local function banque(nom, poses)
  local f=RogueEssence.Content.GraphicsManager.GetAttackSheet(nom)
  return f and f.TileWidth==96 and f.TileHeight==80 and f.TotalFrames==poses
end

local function motif(typ)
  local n='Kingambit_Mecanisme_'..typ..'_'
  if banque(n..'Sol',SCENE.frames) and banque(n..'Rebord',SCENE.frames) then return n,SCENE end
  return 'Kingambit_Trappe_'..typ..'_',ANCIENNE
end

local function lancer(nom, f, couche, x,y)
  local c=RogueEssence.Content
  local e=c.SingleEmitter()
  e.Layer=couche
  e.Anim=c.StaticAnim(c.AnimData(nom,f.ticks,0,f.frames-1),1,f.frames*f.ticks)
  GROUND:PlayVFX(e,x,y)
end

local function animation(typ,participants,places,x,y,s)
  local c = RogueEssence.Content
  local d = RogueEssence.Dungeon.DrawEffect
  GAME:WaitFrames(9)
  local pref, f = motif(typ)
  if f==SCENE then
    -- Départ hors des pistes collision : le trajet des acteurs est déjà fini.
    local map=_ZONE.CurrentGround
    s.camera={carte=map,centre=map.ViewCenter,decalage=map.ViewOffset}
    GAME:MoveCamera(x,y-12,26,false)
    GAME:WaitFrames(16)
  end
  lancer(pref..'Sol',f,c.DrawLayer.Bottom,x,y)
  lancer(pref..'Rebord',f,c.DrawLayer.Front,x,y)
  if f==SCENE then
    -- Deux clacs au mouvement réel des pênes ; coulissement audible au retrait des feuilles.
    GAME:WaitFrames(12)
    SOUND:PlayBattleSE('EVT_Chest_Click')
    GAME:WaitFrames(8)
    SOUND:PlayBattleSE('_UNK_DUN_Clank')
    GAME:WaitFrames(12)
    SOUND:PlayBattleSE('EVT_EP_Pitfall_Reveal')
    GROUND:MoveScreen(c.ScreenMover(0,2,14))
    GAME:WaitFrames(f.chute-32)
  else
    SOUND:PlayBattleSE('EVT_EP_Pitfall_Reveal')
    GROUND:MoveScreen(c.ScreenMover(1,2,14))
    GAME:WaitFrames(f.chute)
  end
  -- Le duo ne tombe plus exactement sur la même image. La lèvre cache
  -- chaque acteur à son contact ; aucun sprite ne ressort en bas du plan.
  SOUND:PlayBattleSE('EVT_EP_Pitfall_Fall')
  for _,p in ipairs(places) do p.touche=true end
  local duree=18+(#participants-1)*f.decalage
  for t=1,duree do
    for i,c in ipairs(participants) do
      local p=t-(i-1)*f.decalage
      if p==1 then
        if places[i].ombre~=nil then c.HideShadow=true end
        GROUND:CharSetAnim(c,'Hurt',false)
      end
      if p==11 then GROUND:CharSetDrawEffect(c,d.Transparent) end
      if p==13 then
        GROUND:CharSetDrawEffect(c,d.Absent)
        -- Le moteur Destiny sait masquer l'ombre seule. PMDO d'origine
        -- ne dessine plus le sprite ni son ombre si l'acteur est désactivé.
        if places[i].ombre==nil then c.EntEnabled=false end
      end
      if p>=1 and p<=18 then c:SetLocHeight(-math.floor(p*p/9)) end
    end
    GAME:WaitFrames(1)
  end
  GAME:WaitFrames(f==SCENE and 6 or 2)
  s.noir=true
  GAME:FadeOut(false,f.fondu)
  -- Respiration de changement de plan : chute, noir, puis l'atterrissage natif.
  GAME:WaitFrames(30)
end

function M.Jouer(typ, participants, x,y)
  local etat, places={},{}
  for i,c in ipairs(participants) do
    places[i]={ombre=c.HideShadow, actif=c.EntEnabled}
  end
  local ok,err=pcall(animation,typ,participants,places,x,y,etat)
  local d=RogueEssence.Dungeon.DrawEffect
  for i,c in ipairs(participants) do
    if places[i].touche then
      GROUND:CharEndDrawEffect(c,d.Absent)
      GROUND:CharEndDrawEffect(c,d.Transparent)
      c:SetLocHeight(0)
      if places[i].ombre~=nil then c.HideShadow=places[i].ombre
      else c.EntEnabled=places[i].actif end
      GROUND:CharEndAnim(c)
    end
  end
  if etat.camera then
    local vue=etat.camera
    vue.carte.ViewCenter,vue.carte.ViewOffset=vue.centre,vue.decalage
  end
  if not ok then
    PrintInfo('[Destiny] Mécanisme de la trappe : '..tostring(err))
    if not etat.noir then GAME:FadeOut(false,12) end
    GAME:WaitFrames(30)
  end
end

return M
