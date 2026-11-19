-- Tests comportementaux Lua pour Fosse Cascade (doublures d'API).
local root = assert(arg[1])

package.preload['origin.common'] = function() return {} end
package.preload['origin.menu.skill.SkillSelectMenu'] = function() return {} end
package.preload['origin.menu.team.AssemblySelectMenu'] = function() return {} end
package.preload['destiny.recrutement'] = function() return {synchroniser=function() end} end
package.preload['destiny.meteo_reverie'] = function()
  return {Appliquer=function() end, SynchroniserZone=function() end, Description=function() return 'Ciel clair.' end}
end
package.preload['destiny.suivi_interieurs'] = function() return {Lancer=function() end, Terminer=function() end} end
package.preload['destiny.equipe_scene'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/equipe_scene.lua'))() end
package.preload['destiny.statue_kangourex'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/statue_kangourex.lua'))()
end
package.preload['destiny.cinematique'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/cinematique.lua'))() end
package.preload['destiny.missions_reverie'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/missions_reverie.lua'))() end

local events = {}
local function ev(k, ...) events[#events+1] = {k, ...} end

local tick_val = 480 * 2 -- démarrer volontairement hors phase 0 pour tester l'attente synchrone
DEBUG = {EnableDbgCoro=function() end}
Direction = {Up=4, Down=0, Left=2, Right=6, UpLeft=3, UpRight=5, DownLeft=1, DownRight=7}
Gender = {Male=1, Female=2, Genderless=0}
RogueElements = {Rect=function(x,y,w,h) return {X=x,Y=y,W=w,H=h} end}
RogueEssence = {
  Content = {
    GraphicsManager = {TotalFrameTick = tick_val},
    ScreenMover = function(dx, dy, dur) return {dx=dx,dy=dy,dur=dur} end,
    FlashEmitter = function() return {FadeInTime=0, HoldTime=0, FadeOutTime=0, Color=nil, Layer=nil, Anim=nil} end,
    BGAnimData = function(name, fr) return {name=name, fr=fr} end,
    AnimData = function(name, fr) return {name=name, fr=fr} end,
    SingleEmitter = function(anim, cycles) return {Anim=anim, cycles=cycles, Layer=nil} end,
  },
  Data = {
    Gender = {Unknown=0, Male=1, Female=2},
    GameProgress = {
      DungeonStakes = {Risk='Risk'},
      ResultType = {Cleared='Cleared', Downed='Downed', Failed='Failed'},
    },
  },
  Ground = {
    GroundObject = function()
      local o = {OnMapInit=function()end, SetTriggerType=function()end}
      return o
    end,
    GroundChar = function(data, loc, dir, name)
      local a = {EntName=name, Position={X=loc.X, Y=loc.Y}, Direction=dir, EntEnabled=true, CollisionDisabled=false, Data=data}
      function a:GetDisplayName() return self.EntName end
      function a:ReloadEvents() self.reloaded = true end
      return a
    end,
    GroundEntity = {EEntityTriggerTypes={Touch=2, Action=1}},
  },
  Dungeon = {
    BaseMap = {ScrollEdge={Clamp=1}},
    -- Énumération réelle du moteur (StatusEffect.cs) : le script demande
    -- DrawEffect.Shaking pour faire trembler Nilo de façon visible.
    DrawEffect = {None=-1, Sleeping=0, Stopped=1, Shaking=2, Charging=3, Absent=4,
                  Spinning=5, Hurt=6, Transparent=7, Trembling=8},
    CharData = function() return {} end,
    MonsterID = function(sp, f, sk, g) return {Species=sp, Form=f, Skin=sk, Gender=g} end,
    Character = function(d) return {Data=d} end,
    InvItem = function(id, cursed, amt) return {ID=id, Cursed=cursed, Amount=amt, GetDisplayName=function() return id end} end,
  },
}
RogueElements.Loc = function(x, y) return {X=x, Y=y} end
function Color(r, g, b, a) return {r=r, g=g, b=b, a=a} end
DrawLayer = {Top='Top', Front='Front'}

local actors = {}
local function make_actor(n, x, y, sp)
  local a = {EntName=n, Position={X=x or 0, Y=y or 0}, Direction=Direction.Down, EntEnabled=true, CollisionDisabled=false, Data={Nickname=n, BaseForm={Species=sp}}}
  function a:GetDisplayName() return self.EntName end
  function a:ReloadEvents() self.reloaded = true end
  actors[n] = a
  return a
end
function CH(n) return actors[n] end

GROUND = {
  CreateCharacterFromCharData = function(_, n, d, x, y, dir) local a = make_actor(n, x, y); a.Data = d.Data; a.Direction = dir; return a end,
  RemoveCharacter = function(_, n) actors[n] = nil; return true end,
  TeleportTo = function(_, a, x, y, dir) a.Position = {X=x, Y=y}; a.Direction = dir end,
  MoveToPosition = function(_, a, x, y, walk, speed) a.Position = {X=x, Y=y}; ev('move', a.EntName, x, y, speed) end,
  EntTurn = function(_, a, dir) a.Direction = dir end,
  CharAnimateTurnTo = function(_, a, dir) a.Direction = dir end,
  CharTurnToCharAnimated = function() end,
  CharTurnToChar = function() end,
  CharSetAnim = function(_, a, anim, loop) ev('anim', a and a.EntName or '?', anim, loop) end,
  CharEndAnim = function(_, a) ev('end_anim', a and a.EntName or '?') end,
  CharSetEmote = function(_, a, em) ev('emote', a.EntName, em) end,
  CharSetDrawEffect = function(_, a, ef) ev('draw_effect', a.EntName, ef) end,
  CharEndDrawEffect = function(_, a, ef) ev('end_draw_effect', a.EntName, ef) end,
  MoveScreen = function(_, m) ev('shake', m.dy, m.dur) end,
  PlayVFX = function(_, em, x, y) ev('vfx', em.Anim.name, x, y) end,
  Hide = function(_, n) if actors[n] then actors[n].EntEnabled = false end; ev('hide', n) end,
  Unhide = function(_, n) if actors[n] then actors[n].EntEnabled = true end; ev('unhide', n) end,
  AnimateInDirection = function(_, a, anim, animdir, dir, dur, aspd, spd)
    a.Direction = animdir
    ev('anim_move', a.EntName, anim, dir, dur, spd)
  end,
}
AI = {DisableCharacterAI=function()end, EnableCharacterAI=function()end, SetCharacterAI=function()end}
TASK = {BranchCoroutine=function(_, f) f(); return true end, JoinCoroutines=function() end}
SOUND = {
  PlayBGM=function(_, m) ev('bgm', m) end,
  FadeOutBGM=function(_, t) ev('fade_bgm', t) end,
  StopBGM=function() ev('stop_bgm') end,
  PlayBattleSE=function(_, s) ev('se', s) end,
  PlayFanfare=function(_, f) ev('fanfare', f) end,
}
local choice_ret = true
UI = {
  SetSpeaker=function() end, SetSpeakerLoc=function() end, SetSpeakerEmotion=function() end,
  SetCenter=function(_, b) ev('center', b) end,
  ResetSpeaker=function() end, WaitShowDialogue=function(_, t) ev('dlg', t) end,
  WaitShowTitle=function() end, WaitHideTitle=function() end,
  BeginChoiceMenu=function() end,
  ChoiceMenuYesNo=function() end, WaitForChoice=function() end,
  ChoiceResult=function() return choice_ret end,
}
local unlocked = {}
GAME = {
  CutsceneMode=function() end,
  MoveCamera=function() end,
  FadeIn=function() end,
  FadeOut=function() end,
  WaitFrames=function(_, n)
    tick_val = tick_val + (n or 1) * 120
    RogueEssence.Content.GraphicsManager.TotalFrameTick = tick_val
    ev('wait', n)
  end,
  GetPlayerPartyCount=function() return 2 end,
  GetTeamLeaderIndex=function() return 0 end,
  GetPlayerPartyMember=function(_, i) return {Importance=i==0 and 'Hero' or 'Partner', Data={}} end,
  GetCurrentGround=function() return {Name={ToLocal=function() return 'Fosse Cascade Fond' end}} end,
  GetCameraCenter=function() return {X=240, Y=180} end,
  DungeonUnlocked=function(_, id) return unlocked[id] == true end,
  UnlockDungeon=function(_, id) unlocked[id] = true; ev('unlock', id) end,
  SetRescueAllowed=function() end,
  EnterDungeon=function(_, ...) ev('enter_dungeon', ...) end,
  ContinueDungeon=function(_, ...) ev('continue_dungeon', ...) end,
  EndDungeonRun=function(_, ...) ev('end_run', ...) end,
  EnterZone=function(_, ...) ev('enter_zone', ...) end,
}
COMMON = {
  Rescued=function() end,
  BeginDungeon=function() end,
  ExitDungeonMissionCheck=function() return false end,
  BossTransition=function(p) ev('boss_transition', p) end,
  GiftItem=function(hero, item)
    assert(type(item) == 'table' and type(item.GetDisplayName) == 'function', 'InvItem attendu pour GiftItem')
    ev('gift', item.ID)
  end,
  CreateWalkArea=function() end,
  EndDungeonDay=function(res, z, s, m, e) ev('end_day', res, z, s, m, e) end,
  ShowTeamStorageMenu=function() appels_stockage = (appels_stockage or 0) + 1 end,
}
function LTBL(m) return {Importance=m.Importance} end

local function make_ewc3_map()
  local m = {AssetName='ewc3_entree_waterfall_cave', Layers={}, Objects={}}
  for i = 0, 20 do m.Layers[i] = {Visible=(i ~= 13 and i ~= 14 and i ~= 18)} end
  function m:FindObject(n) return self.Objects[n] end
  function m:AddObject(o) self.Objects[o.EntName] = o end
  return m
end

-- 1. ewc3 : 1re arrivée (fermée -> ouverture synchrone -> ouverte) puis 2e visite (déjà ouverte)
SV = {Destiny={AlerteShinx='a_secourir'}}
make_actor('PLAYER', 392, 544)
local ewc3 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/ewc3_entree_waterfall_cave/init.lua'))()
local m_ewc3 = make_ewc3_map()
ewc3.Init(m_ewc3)
assert(m_ewc3.Layers[12].Visible and m_ewc3.Layers[17].Visible and not m_ewc3.Layers[14].Visible)
assert(m_ewc3.Objects.SeuilDonjon and m_ewc3.Objects.SortieRetourReverie and m_ewc3.Objects.Statue_Kangourex)
ewc3.Enter(m_ewc3)
assert(SV.Destiny.GrotteVerdoyanteOuverte == true)
assert(SV.Destiny.StatueKangourexExpliquee == true, 'La Statue Kangourex doit être expliquée dès la cinématique d’arrivée')
assert(not m_ewc3.Layers[12].Visible and not m_ewc3.Layers[13].Visible and m_ewc3.Layers[14].Visible)
assert(actors.Luxray_Ewc3 and actors.Luxray_Ewc3.Position.X == 400 and actors.Luxray_Ewc3.Position.Y == 260 and actors.Luxray_Ewc3.reloaded == true)
assert(actors.PLAYER.Position.X == 384 and actors.PLAYER.Position.Y == 248 and actors.PLAYER.CollisionDisabled == false)
local hero_q, hero_sw, statue_quiproquo, statue_reserve = false, false, false, false
for _, e in ipairs(events) do
  if e[1] == 'emote' and e[2] == 'PLAYER' and e[3] == 'question' then hero_q = true end
  if e[1] == 'emote' and e[2] == 'PLAYER' and e[3] == 'sweatdrop' then hero_sw = true end
  if e[1] == 'dlg' and tostring(e[2]):find('pierre pour un vrai Pokémon', 1, true) then statue_quiproquo = true end
  if e[1] == 'dlg' and tostring(e[2]):find('Statue Kangourex', 1, true) then statue_reserve = true end
end
assert(hero_q and hero_sw and statue_quiproquo and statue_reserve, 'Incompréhension muette du héros ou explication de la Statue Kangourex manquante')

-- Une fois expliquée, l'interaction directe ne répète pas le tutoriel mais ouvre
-- le stockage de l'équipe (dépôt, retrait, tout déposer, argent).
appels_stockage = 0
local n_avant = #events
ewc3.Statue_Kangourex_Action(m_ewc3.Objects.Statue_Kangourex, actors.PLAYER)
assert(#events == n_avant, 'Statue_Kangourex_Action ne doit pas rejouer le dialogue quand StatueKangourexExpliquee == true')
assert(appels_stockage == 1, 'Statue_Kangourex_Action doit ouvrir le stockage, ouvert ' .. tostring(appels_stockage) .. ' fois')

-- Repli ancienne sauvegarde (cascade déjà ouverte, statue pas encore expliquée) :
-- explication unique puis stockage, une seule fois chacun.
SV.Destiny.StatueKangourexExpliquee = nil
appels_stockage = 0
n_avant = #events
ewc3.Statue_Kangourex_Action(m_ewc3.Objects.Statue_Kangourex, actors.PLAYER)
assert(SV.Destiny.StatueKangourexExpliquee == true, 'Le repli Statue_Kangourex_Action doit marquer StatueKangourexExpliquee')
assert(#events > n_avant, 'Le repli doit jouer l’explication de la statue')
assert(appels_stockage == 1, 'Le repli doit ouvrir le stockage une seule fois')

-- SeuilDonjon et SortieRetourReverie
ewc3.SeuilDonjon_Touch(nil, actors.PLAYER)
assert(events[#events][1] == 'enter_dungeon' and events[#events][2] == 'grotte_verdoyante')
ewc3.Init(m_ewc3) -- reset sortie_en_cours et vérifie ouverture persistante
assert(m_ewc3.Layers[14].Visible and not m_ewc3.Layers[12].Visible)
ewc3.SortieRetourReverie_Touch(nil, actors.PLAYER)
assert(events[#events][1] == 'enter_zone' and events[#events][2] == 'town02_waterfallvillage' and SV.Destiny.ArriveeVille == 'batiment')

-- Un pas de plus dans le collider pendant que le menu est ouvert rappelle le
-- gestionnaire (GroundChar.Collide -> Interact pour chaque « Touch ») : le verrou
-- doit absorber l'appel au lieu d'empiler un second menu.
ewc3.Init(m_ewc3)
local menu_oui_non, wait_choice = UI.ChoiceMenuYesNo, UI.WaitForChoice
local menus_ouverts, reinsere = 0, false
UI.ChoiceMenuYesNo = function(_, texte) menus_ouverts = menus_ouverts + 1; ev('menu', texte) end
UI.WaitForChoice = function()
  if menus_ouverts == 1 and not reinsere then
    reinsere = true
    ewc3.SeuilDonjon_Touch(nil, actors.PLAYER) -- pas suivant, en pleine attente de choix
  end
end
choice_ret = false
ewc3.SeuilDonjon_Touch(nil, actors.PLAYER)
assert(menus_ouverts == 1, 'un second pas dans le seuil ne doit pas empiler un menu')
assert(reinsere, 'le test doit reproduire une ré-entrance du déclencheur')
UI.ChoiceMenuYesNo, UI.WaitForChoice = menu_oui_non, wait_choice
choice_ret = true

-- Lyra est persistante dans la carte sauvegardée : après le sauvetage elle doit
-- disparaître de l'entrée au lieu d'y rester en fantôme.
SV.Destiny.GrotteVerdoyanteOuverte = true
SV.Destiny.AlerteShinx = 'termine'
actors.Luxray_Ewc3 = make_actor('Luxray_Ewc3', 400, 260, 'luxray')
ewc3.Init(m_ewc3)
assert(actors.Luxray_Ewc3 == nil, 'Luxray_Ewc3 doit être retirée une fois le sauvetage terminé')
SV.Destiny.AlerteShinx = 'a_secourir'
ewc3.Init(m_ewc3)
assert(actors.Luxray_Ewc3 and actors.Luxray_Ewc3.Position.X == 400 and actors.Luxray_Ewc3.Position.Y == 260,
  'Luxray_Ewc3 doit être replacée devant la cascade pendant le sauvetage')

-- 2. zone/grotte_verdoyante : Seg 0/1 échec -> respawn devant ewc3_entree_waterfall_cave (Laying -> Wake + réaction Lyra) ; Seg 0/1 succès -> fgv1
local zone = assert(loadfile(root .. '/game/Data/Script/destiny/zone/grotte_verdoyante/init.lua'))()
local zobj = {ID='grotte_verdoyante'}
SV.Destiny = {AlerteShinx='a_secourir', ExplorationReverie=true, GrotteVerdoyanteOuverte=true}
events = {}
zone.ExitSegment(zobj, 'Downed', false, 0, 0)
assert(SV.Destiny.AlerteShinx == 'a_secourir' and SV.Destiny.LuxrayAttente == 'sortie')
assert(SV.Destiny.ExplorationReverie == nil, 'ExplorationReverie doit être relâché après un échec (branche visite libre de lost_wood)')
assert(events[#events][1] == 'end_day' and events[#events][2] == 'Downed' and events[#events][3] == 'grotte_verdoyante')
assert(SV.Destiny.GrotteVerdoyanteRetourEchec and SV.Destiny.GrotteVerdoyanteRetourEchec.cause == 'ko' and SV.Destiny.GrotteVerdoyanteRetourEchec.segment == 0)
assert(SV.Destiny.GrotteVerdoyanteNbKO == 1 and SV.Destiny.GrotteVerdoyanteDernierKO == true)

-- Cinématique de respawn K.O. sur ewc3 (étages 1F-8F, avec Lyra)
actors = {}; make_actor('PLAYER', 384, 544); make_actor('Teammate1', 368, 544)
events = {}
ewc3.Init(m_ewc3)
ewc3.Enter(m_ewc3)
assert(SV.Destiny.GrotteVerdoyanteRetourEchec == nil, 'GrotteVerdoyanteRetourEchec doit être consommé')
assert(actors.PLAYER.Position.X == 368 and actors.PLAYER.Position.Y == 248 and actors.PLAYER.CollisionDisabled == false)
assert(actors.Teammate1.Position.X == 344 and actors.Teammate1.Position.Y == 256)
assert(actors.Luxray_Ewc3 and actors.Luxray_Ewc3.Position.X == 400 and actors.Luxray_Ewc3.Position.Y == 260 and actors.Luxray_Ewc3.Direction == Direction.Up and actors.Luxray_Ewc3.CollisionDisabled == false)
local lay_p, lay_t, wake_p, wake_t, end_p, end_t, lyra_ko_dlg, partner_ko_dlg = false, false, false, false, false, false, false, false
for _, e in ipairs(events) do
  if e[1] == 'anim' and e[2] == 'PLAYER' and e[3] == 'Laying' then lay_p = true end
  if e[1] == 'anim' and e[2] == 'Teammate1' and e[3] == 'Laying' then lay_t = true end
  if e[1] == 'anim' and e[2] == 'PLAYER' and e[3] == 'Wake' then wake_p = true end
  if e[1] == 'anim' and e[2] == 'Teammate1' and e[3] == 'Wake' then wake_t = true end
  if e[1] == 'end_anim' and e[2] == 'PLAYER' then end_p = true end
  if e[1] == 'end_anim' and e[2] == 'Teammate1' then end_t = true end
  if e[1] == 'dlg' and tostring(e[2]):find('bout de forces', 1, true) then
    assert(not wake_p and not wake_t, 'Lyra doit interpeller le duo avant leur réveil')
    lyra_ko_dlg = true
  end
  if e[1] == 'dlg' and tostring(e[2]):find('Aïe', 1, true) then
    assert(wake_p and wake_t and end_p and end_t, 'Aucun portrait/dialogue du duo avant Wake + CharEndAnim')
    partner_ko_dlg = true
  end
end
assert(lay_p and lay_t and wake_p and wake_t and end_p and end_t and lyra_ko_dlg and partner_ko_dlg, 'séquence K.O. -> Wake devant ewc3 incomplète')

-- Dialogue post-K.O. de Lyra (Luxray_Ewc3_Action)
events = {}
ewc3.Luxray_Ewc3_Action(actors.Luxray_Ewc3, actors.PLAYER)
local post_ko_action_ok = false
for _, e in ipairs(events) do
  if e[1] == 'dlg' and tostring(e[2]):find('sonnés', 1, true) then post_ko_action_ok = true end
end
assert(post_ko_action_ok, 'dialogue post-K.O. de Lyra manquant')

-- Un aller-retour en ville remet l'état à zéro : au retour, Lyra ne doit plus
-- croire le duo « encore sonné » et reprend sa réplique habituelle.
assert(SV.Destiny.GrotteVerdoyanteDernierKO == true)
events = {}
ewc3.SortieRetourReverie_Touch(nil, actors.PLAYER)
assert(events[#events][1] == 'enter_zone' and events[#events][2] == 'town02_waterfallvillage')
assert(SV.Destiny.GrotteVerdoyanteDernierKO == nil,
       'le retour en ville doit effacer GrotteVerdoyanteDernierKO')
ewc3.Init(m_ewc3) -- réarme le verrou des déclencheurs
events = {}
ewc3.Luxray_Ewc3_Action(actors.Luxray_Ewc3, actors.PLAYER)
local lyra_normale = false
for _, e in ipairs(events) do
  if e[1] == 'dlg' and tostring(e[2]):find('grand ouvert', 1, true) then lyra_normale = true end
end
assert(lyra_normale, 'après un retour en ville, Lyra doit reprendre sa réplique normale')

events = {}
zone.ExitSegment(zobj, 'Cleared', false, 0, 7)
assert(#events == 1 and events[1][1] == 'enter_zone' and events[1][2] == 'grotte_verdoyante' and events[1][4] == 1,
  'la fin du 8F ne clôt pas l’expédition')

zone.ExitSegment(zobj, 'Failed', false, 1, 0)
assert(SV.Destiny.GrotteVerdoyantePhase == 1 and SV.Destiny.AlerteShinx == 'a_secourir')
assert(SV.Destiny.GrotteVerdoyanteRetourEchec and SV.Destiny.GrotteVerdoyanteRetourEchec.segment == 1)
events = {}
ewc3.Init(m_ewc3)
ewc3.Enter(m_ewc3)
local boss_ko_dlg = false
for _, e in ipairs(events) do
  if e[1] == 'dlg' and tostring(e[2]):find('Kabutops', 1, true) then boss_ko_dlg = true end
end
assert(boss_ko_dlg, 'variante K.O. 9F Kabutops manquante sur ewc3')

-- K.O. post-scénario (sans Lyra) : réveil du duo seul devant la cascade
SV.Destiny.AlerteShinx = 'termine'
zone.ExitSegment(zobj, 'Downed', false, 0, 0)
actors = {}; make_actor('PLAYER', 384, 544); make_actor('Teammate1', 368, 544)
events = {}
ewc3.Init(m_ewc3)
ewc3.Enter(m_ewc3)
assert(actors.Luxray_Ewc3 == nil and actors.PLAYER.Position.Y == 248 and actors.Teammate1.Position.Y == 256)
SV.Destiny.AlerteShinx = 'a_secourir'

events = {}
zone.ExitSegment(zobj, 'Cleared', false, 1, 0)
assert(SV.Destiny.GrotteVerdoyantePhase == 3 and #events == 1 and events[1][1] == 'enter_zone' and events[1][4] == 1,
  'les retrouvailles précèdent le bilan')

-- 3. fgv1 : PreBattle (réveil Nilo + UN éclair blanc d'incompréhension + DOUBLE éclair
--    blanc d'apparition, sans aucune animation d'eau, Lixy tremblant visiblement,
--    boss sur le sable et non sur les vasques) -> revanche / -dev
--    -> PostBattle (fuite au sud en courant) -> EmptyReturn
local fgv1 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/fgv1_fin_grotte_vasques/init.lua'))()
actors = {}; make_actor('PLAYER', 240, 344); make_actor('Teammate1', 216, 344)
SV.Destiny = {AlerteShinx='a_secourir', JourneeVille=0}
-- Un petit calque natif simulé : l'animation doit vraiment être suspendue
-- pendant chaque retour à l'image, puis remise quand l'écran est noir.
local reflet = {FrameLength=8, Frames={Count=12}}
local autre = {FrameLength=9, Frames={Count=4}}
local bulles = {Name='07 bulles source 24 phases', Visible=true}
local carte_fosse = {AssetName='fgv1_fin_grotte_vasques', Layers={Count=2,
  [0]={Name='06 reflets vasques 12 phases', Width=1, Height=1,
       Tiles={[0]={[0]={Layers={Count=2, [0]=reflet, [1]=autre}}}}},
  [1]=bulles}}
local fn_fade_in, fn_fade_out = GAME.FadeIn, GAME.FadeOut
GAME.FadeIn = function(_, duree)
  assert(reflet.FrameLength == 0 and not bulles.Visible, 'eau visible en mouvement au pré-combat')
  ev('fade_in', duree)
end
GAME.FadeOut = function(_, blanc, duree) ev('fade_out', blanc, duree) end
events = {}
fgv1.Enter(carte_fosse)
GAME.FadeIn, GAME.FadeOut = fn_fade_in, fn_fade_out
assert(reflet.FrameLength == 8 and autre.FrameLength == 9 and bulles.Visible, 'calques non restaurés à la sortie')
assert(SV.Destiny.GrotteVerdoyantePhase == 1)
assert(actors.Kabutops_Boss and actors.Kabutops_Boss.EntEnabled == true)
-- Le boss n'apparaît JAMAIS sur la bande des vasques en terrasses (y = 136..208).
assert(actors.Kabutops_Boss.Position.X == 244 and actors.Kabutops_Boss.Position.Y == 244,
       'ancre terrain identique au centre de la case de combat (10,10)')
local saw_hide, saw_unhide, saw_stop_bgm, saw_rising_fear, saw_slash, boss_bgm_ok, wake_dlg_ok, unseen_voice_ok =
  false, false, false, false, false, false, false, false
local eaux_interdites = {'Water_Column_Ranger', 'Water_Spout_Splash', 'Wave_Circle_Blue', 'Bubbles_Blue'}
local geysers_interdits = {'EVT_CH05_Waterfall_Cave_Geyser', 'EVT_CH05_Hot_Spring_Splash'}
local eau_vue, geyser_vu = false, false
local flashes = 0
local tremble_nilo, tremble_fini = false, false
local noir, voix, blanc_revelation, apparition
for i, e in ipairs(events) do
  if e[1] == 'fade_out' and e[2] == false and noir == nil then noir = i end
  if e[1] == 'fade_out' and e[2] == true then blanc_revelation = i end
  if e[1] == 'hide' and e[2] == 'Kabutops_Boss' then saw_hide = true end
  if e[1] == 'unhide' and e[2] == 'Kabutops_Boss' then saw_unhide, apparition = true, i end
  if e[1] == 'stop_bgm' then saw_stop_bgm = true end
  if e[1] == 'bgm' and e[2] == 'Rising Fear.ogg' then saw_rising_fear = true end
  if e[1] == 'se' and e[2] == 'DUN_Slash' then saw_slash = true end
  if e[1] == 'bgm' and e[2] == 'Boss Battle 2.ogg' then boss_bgm_ok = true end
  -- Nilo ne se reveille plus : il est deja debout et supplie qu'on recule.
  if e[1] == 'dlg' and tostring(e[2]):find('Reculez', 1, true) then wake_dlg_ok = true end
  if e[1] == 'dlg' and tostring(e[2]):find('premier grondement', 1, true) then unseen_voice_ok, voix = true, i end
  if e[1] == 'vfx' then
    for _, n in ipairs(eaux_interdites) do if e[2] == n then eau_vue = true end end
  end
  if e[1] == 'se' then
    for _, n in ipairs(geysers_interdits) do if e[2] == n then geyser_vu = true end end
    if e[2] == 'EVT_Battle_Flash' then flashes = flashes + 1 end
  end
  if e[1] == 'draw_effect' and e[2] == 'Nilo_Grotte' and e[3] == 2 then tremble_nilo = true end
  if e[1] == 'end_draw_effect' and e[2] == 'Nilo_Grotte' then tremble_fini = true end
end
assert(saw_hide and saw_unhide and saw_stop_bgm and saw_rising_fear and saw_slash and boss_bgm_ok and wake_dlg_ok and unseen_voice_ok,
       'cinématique d’apparition Kabutops incomplète')
assert(noir < voix and voix < blanc_revelation and apparition == blanc_revelation + 1,
       'voix hors champ dans le noir, puis révélation pendant le dernier blanc')
assert(not eau_vue and not geyser_vu,
       'aucune animation ni son d’eau ne doit accompagner l’apparition du boss')
assert(flashes == 3,
       'il faut UN éclair blanc (incompréhension) puis un DOUBLE éclair blanc (apparition), soit 3 au total')
assert(tremble_nilo and tremble_fini,
       'Nilo doit trembler de façon visible (DrawEffect.Shaking) puis être relâché')

-- 3 bis. Nilo n'est plus endormi : il est debout, sur les marches nord
-- (les vasques en terrasses montent jusqu'à y = 192), et tremble dès l'arrivée.
local sommeil_rejoue, recul_demande = false, false
for _, e in ipairs(events) do
  if e[1] == 'anim' and e[2] == 'Nilo_Grotte' and e[3] == 'EventSleep' then sommeil_rejoue = true end
end
assert(not sommeil_rejoue, 'Nilo ne doit plus être endormi à l’arrivée du duo')
-- Aucun déplacement de Nilo ne doit le faire descendre dans la salle.
for _, e in ipairs(events) do
  if e[1] == 'move' and e[2] == 'Nilo_Grotte' then
    assert(e[4] <= 224, 'Nilo doit rester sur la partie nord (marches), pas descendre dans la salle')
  end
end
assert(actors.Nilo_Grotte.Position.Y <= 224,
       'Nilo doit rester sur la partie nord (marches des vasques), pas au centre de la salle')
for _, e in ipairs(events) do
  if e[1] == 'dlg' and tostring(e[2]):find('Reculez', 1, true) then recul_demande = true end
end
assert(recul_demande, 'Nilo doit demander de reculer dès l’arrivée')
assert(events[#events][1] == 'continue_dungeon' and events[#events][2] == 'grotte_verdoyante' and events[#events][3] == 1)

-- 3 ter. Une scene INTERROMPUE ne doit jamais se rejouer entierement.
-- C'est le cas reel du journal : le moteur recycle la zone pendant la scene
-- (ScriptEvent.Apply(): Coroutine for event interrupted by break command!),
-- puis la carte est reentree. Sans garde, tout l'avertissement, l'eclair et
-- la revelation repartent. On simule l'interruption au 2e dialogue.
SV.Destiny = {AlerteShinx='a_secourir', JourneeVille=0}
local cinematique_module = require('destiny.cinematique')
local dire = cinematique_module.Dire
local appels = 0
if dire ~= nil then
  cinematique_module.Dire = function(...)
    appels = appels + 1
    if appels == 1 then error('interruption simulee du moteur', 0) end
    return dire(...)
  end
end
events = {}
pcall(function() fgv1.Enter(carte_fosse) end)
if dire ~= nil then cinematique_module.Dire = dire end
assert(appels >= 1, 'la scene interrompue doit avoir commence')
-- La phase doit deja valoir 1 : la decouverte est engagee, elle ne repartira pas.
assert(SV.Destiny.GrotteVerdoyantePhase == 1,
       'une scene interrompue doit laisser la phase a 1 pour ne pas se rejouer')
events = {}
fgv1.Enter(carte_fosse)
local flashes_2, sommeil_2 = 0, false
for _, e in ipairs(events) do
  if e[1] == 'se' and e[2] == 'EVT_Battle_Flash' then flashes_2 = flashes_2 + 1 end
  if e[1] == 'anim' and e[2] == 'Nilo_Grotte' and e[3] == 'EventSleep' then sommeil_2 = true end
end
assert(flashes_2 == 0, 'la decouverte de Nilo ne doit pas se rejouer a la reentree')
assert(not sommeil_2, 'aucun sommeil a rejouer a la reentree')

-- En test Ground Editor (-dev : _ZONE.InDevZone == true), la revanche/transition doit appeler EnterDungeon (forceNewZone = true)
_ZONE = {InDevZone = true}
events = {}
fgv1.Enter(carte_fosse)
for _, e in ipairs(events) do
  assert(not (e[1] == 'se' and e[2] == 'EVT_Battle_Flash'), 'pas de révélation rejouée en revanche')
  assert(not (e[1] == 'anim' and e[2] == 'Nilo_Grotte' and e[3] == 'EventSleep'), 'pas de réveil rejoué')
end
assert(events[#events][1] == 'enter_dungeon' and events[#events][2] == 'grotte_verdoyante' and events[#events][3] == 1,
       'en mode -dev (InDevZone), lancer_duel_boss doit utiliser EnterDungeon pour éviter ReturnToEditor')
_ZONE = nil

-- La carte des vasques ne déclare pas de piste : le chargement d'une sauvegarde
-- doit relancer l'ambiance au lieu de laisser le silence.
events = {}
SV.Destiny.GrotteVerdoyantePhase = nil
fgv1.GameLoad({AssetName='fgv1_fin_grotte_vasques'})
local game_load_bgm = false
for _, e in ipairs(events) do
  if e[1] == 'bgm' and e[2] == 'Lower Spring Cave.ogg' then game_load_bgm = true end
end
assert(game_load_bgm, 'fgv1.GameLoad doit relancer Lower Spring Cave.ogg')
-- Pendant la revelation de Kabutops (phase 1), la scene tient la musique :
-- GameLoad ne doit pas la remplacer sous la scene en cours.
events = {}
SV.Destiny.GrotteVerdoyantePhase = 1
fgv1.GameLoad({AssetName='fgv1_fin_grotte_vasques'})
for _, e in ipairs(events) do
  assert(not (e[1] == 'bgm' and e[2] == 'Lower Spring Cave.ogg'),
         'GameLoad ne doit pas relancer la musique pendant la revelation')
end

SV.Destiny.GrotteVerdoyantePhase = 3
events = {}
fgv1.Enter({AssetName='fgv1_fin_grotte_vasques'})
assert(SV.Destiny.AlerteShinx == 'termine' and SV.Destiny.CelebrationNilo == 'en_attente' and SV.Destiny.GrotteVerdoyanteBossVaincu == true and SV.Destiny.GrotteVerdoyantePhase == 4)
assert(SV.Destiny.JourneeVille == 1 and unlocked.grotte_verdoyante == true)
assert(actors.Lyra_Grotte == nil and actors.Nilo_Grotte == nil and actors.Kabutops_Boss == nil, 'acteurs temporaires fgv1 doivent être retirés')
-- Kabutops vaincu fuit vers le sud EN COURANT (3 px/image, jusqu'à y >= 344) et
-- aucune animation d'eau n'accompagne plus son départ (plus de plongeon).
local fuite_sud, fuite_vitesse, eau_post = false, nil, false
for _, e in ipairs(events) do
  if e[1] == 'move' and e[2] == 'Kabutops_Boss' and e[3] == 240 and e[4] >= 344 then
    fuite_sud = true
    fuite_vitesse = e[5]
  end
  if e[1] == 'vfx' and (e[2] == 'Water_Spout_Splash' or e[2] == 'Wave_Circle_Blue'
      or e[2] == 'Bubbles_Blue' or e[2] == 'Water_Column_Ranger') then
    eau_post = true
  end
end
assert(fuite_sud and fuite_vitesse == 3, 'Kabutops doit fuir vers le sud en courant (3 px/image)')
assert(not eau_post, 'la fuite de Kabutops ne doit déclencher aucune animation d’eau')

local saw_lyra_reunion, fins = false, 0
for _, e in ipairs(events) do
  if e[1] == 'dlg' and tostring(e[2]):find('précipitée dans la grotte', 1, true) then saw_lyra_reunion = true end
  assert(not (e[1] == 'bgm' and e[2] == 'Job Clear!.ogg'), 'aucun jingle doublant le bilan natif')
  assert(not (e[1] == 'dlg' and tostring(e[2]):find('Journal d’Exploration', 1, true)), 'aucun faux journal')
  if e[1] == 'end_day' then fins = fins + 1 end
end
assert(saw_lyra_reunion and fins == 1 and SV.Destiny.AvisOuvertureFosse, 'retrouvailles puis une seule clôture PMDO')
assert(events[#events][1] == 'end_day' and events[#events][2] == 'Cleared' and events[#events][3] == 'town02_waterfallvillage')

events = {}
fgv1.Enter({AssetName='fgv1_fin_grotte_vasques'})
assert(events[#events][1] == 'end_day' and not actors.Kabutops_Boss)

-- 4. Réverie post-sauvetage : CelebrationNilo (accueil des habitants, Léo/Lyra/Nilo, cadeau gummi_royal), Nilo_Shinx + tente Bellossom
local ville = assert(loadfile(root .. '/game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'))()
local centre = {
  AssetName='reverie_centre', characters={}, objects={},
  GetMapChar=function(self, n) return self.characters[n] end,
  FindObject=function(self, n) return self.objects[n] end,
  AddObject=function(self, o) self.objects[o.EntName] = o end,
  GetObstacle=function() return 0 end,
  Width=200, Height=500,
}
actors = {}; make_actor('PLAYER', 800, 1160); make_actor('Teammate1', 772, 1160)
centre.characters.NewObject_7 = make_actor('NewObject_7', 808, 1116, 'lombre')
centre.characters.NewObject_8 = make_actor('NewObject_8', 782, 1104, 'ludicolo')
centre.characters.Roserade_Fleuriste = make_actor('Roserade_Fleuriste', 748, 1112, 'roserade')
centre.characters.NewObject_4 = make_actor('NewObject_4', 372, 1172, 'alakazam')
centre.characters.NewObject_14 = make_actor('NewObject_14', 857, 1179, 'tyranitar')
centre.characters.NewObject_16 = make_actor('NewObject_16', 827, 1178, 'charizard')
SV.Destiny = {AlerteShinx='termine', CelebrationNilo='en_attente', GrotteVerdoyanteBossVaincu=true, RetourAccompli=true, JourneeVille=1, VisiteVille='terminee', PlacementHabitantsReverie={reverie_centre=true}, PassageQuartier={x=1552, y=1600, px=1524, py=1600, dir='Down'}}
events = {}
ville.Init(centre)
local ax0, ay0 = actors.NewObject_4.Position.X, actors.NewObject_4.Position.Y
assert(actors.Bellossom_Boutique and centre.objects.ComptoirBellossom, 'Bellossom_Boutique ou ComptoirBellossom manquant')
ville.Enter(centre)
local saw_gift, saw_rescue_bgm, saw_town_bgm, saw_villagers_congrats, saw_leo = false, false, false, false, false
for _, e in ipairs(events) do
  if e[1] == 'gift' and e[2] == 'gummi_royal' then saw_gift = true end
  if e[1] == 'bgm' and e[2] == 'A Successful Rescue.ogg' then saw_rescue_bgm = true end
  if e[1] == 'bgm' and e[2] == 'Treasure Town.ogg' then saw_town_bgm = true end
  if e[1] == 'dlg' and tostring(e[2]):find('fière de vous compter', 1, true) then saw_villagers_congrats = true end
  if e[1] == 'dlg' and tostring(e[2]):find('rentrés tous ensemble', 1, true) then saw_leo = true end
end
assert(saw_gift and saw_rescue_bgm and saw_town_bgm and saw_villagers_congrats and saw_leo and SV.Destiny.CelebrationNilo == 'termine', 'CelebrationNilo enrichie non jouée complètement')
assert(SV.Destiny.PassageQuartier == nil, 'PassageQuartier transitoire doit être nettoyé')
assert(actors.Lyra_Celebration == nil and actors.Leo_Celebration == nil and actors.Nilo_Celebration == nil, 'acteurs de célébration non nettoyés')
assert(actors.NewObject_4.Position.X == ax0 and actors.NewObject_4.Position.Y == ay0, 'Alakazam doit retrouver son comptoir après la célébration')

local res = {
  AssetName='reverie_residentiel', characters={}, objects={},
  GetMapChar=function(self, n) return self.characters[n] end,
  FindObject=function(self, n) return self.objects[n] end,
  AddObject=function(self, o) self.objects[o.EntName] = o end,
  GetObstacle=function() return 0 end,
  Width=200, Height=500,
}
actors = {}; make_actor('PLAYER', 800, 1160); make_actor('Teammate1', 772, 1160)
res.characters.NewObject_9 = make_actor('NewObject_9', 733, 2391)
res.characters.NewObject_10 = make_actor('NewObject_10', 709, 2391)
SV.Destiny = {AlerteShinx='termine', GrotteVerdoyanteBossVaincu=true, RetourAccompli=true, JourneeVille=1, PlacementHabitantsReverie={reverie_residentiel=true}}
ville.Init(res)
assert(actors.Nilo_Shinx and actors.Nilo_Shinx.Position.X == 721 and actors.Nilo_Shinx.Position.Y == 2412 and actors.Nilo_Shinx.reloaded == true)
events = {}
ville.Nilo_Shinx_Action(actors.Nilo_Shinx, actors.PLAYER)
local saw_nilo_dlg = false
for _, e in ipairs(events) do if e[1] == 'dlg' and tostring(e[2]):find('Kabutops', 1, true) then saw_nilo_dlg = true end end
assert(saw_nilo_dlg)

local cafe = assert(loadfile(root .. '/game/Data/Script/destiny/ground/caféspindaaccueil/init.lua'))()
actors = {}; make_actor('PLAYER', 200, 300); make_actor('Spinda', 200, 220); make_actor('Kirlia', 160, 220)
events = {}
choice_ret = 4
cafe.Kirlia_Action(actors.Kirlia, actors.PLAYER)
local saw_kirlia_termine = false
for _, e in ipairs(events) do if e[1] == 'dlg' and tostring(e[2]):find('Nilo est rentré', 1, true) then saw_kirlia_termine = true end end
assert(saw_kirlia_termine)

local missions = package.preload['destiny.missions_reverie']()
unlocked.lost_wood = true
assert(missions.ZoneOffre() == 'grotte_verdoyante' and missions.Accepter())
assert(missions.Actuelle().Zone == 'grotte_verdoyante')

print('PASS test_grotte_verdoyante.lua : cascade 24f synchrone, zone 9F, boss, sauvetage Nilo, ville et missions.')
