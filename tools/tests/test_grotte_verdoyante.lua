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
package.preload['destiny.fosse_cascade_scene'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/fosse_cascade_scene.lua'))() end
package.preload['destiny.missions_reverie'] = function() return assert(loadfile(root .. '/game/Data/Script/destiny/missions_reverie.lua'))() end

local events = {}
local title_calls = 0
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
    BGAnimData = function(name, fr, first, last) return {name=name, fr=fr, first=first, last=last} end,
    FiniteOverlayEmitter = function() return {} end,
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
Color = {
  Transparent = {r=0, g=0, b=0, a=0},
  Black = {r=0, g=0, b=0, a=255},
  Multiply = function(c, f) return {r=c.r*f, g=c.g*f, b=c.b*f, a=c.a*f} end,
}
DrawLayer = {Top='Top', Front='Front'}

local actors = {}
local function make_actor(n, x, y, sp)
  local a = {EntName=n, Position={X=x or 0, Y=y or 0}, Direction=Direction.Down, EntEnabled=true, CollisionDisabled=false, Data={Nickname=n, BaseForm={Species=sp}}}
  function a:GetDisplayName() return self.EntName end
  function a:ReloadEvents() self.reloaded = true end
  function a:SetLocHeight(h) self.LocHeight = h; ev('hauteur', self.EntName, h, tick_val) end
  actors[n] = a
  return a
end
function CH(n) return actors[n] end

GROUND = {
  CreateCharacterFromCharData = function(_, n, d, x, y, dir)
    local a = make_actor(n, x, y)
    a.Data = d.Data
    a.Direction = dir
    ev('create', n, dir, x, y)
    return a
  end,
  RemoveCharacter = function(_, n)
    local a = actors[n]
    if a then ev('remove', n, a.Position.X, a.Position.Y, a.Direction) end
    actors[n] = nil
    return true
  end,
  TeleportTo = function(_, a, x, y, dir) a.Position = {X=x, Y=y}; a.Direction = dir; ev('teleport', a.EntName, x, y) end,
  MoveToPosition = function(_, a, x, y, walk, speed) a.Position = {X=x, Y=y}; ev('move', a.EntName, x, y, speed) end,
  EntTurn = function(_, a, dir) a.Direction = dir end,
  CharAnimateTurnTo = function(_, a, dir) a.Direction = dir end,
  CharTurnToCharAnimated = function(_, a, cible) ev('regard', a.EntName, cible.EntName) end,
  CharTurnToChar = function() end,
  CharSetAnim = function(_, a, anim, loop) ev('anim', a and a.EntName or '?', anim, loop, tick_val) end,
  CharEndAnim = function(_, a) ev('end_anim', a and a.EntName or '?') end,
  CharSetEmote = function(_, a, em) ev('emote', a.EntName, em) end,
  CharSetDrawEffect = function(_, a, ef) ev('draw_effect', a.EntName, ef) end,
  CharEndDrawEffect = function(_, a, ef) ev('end_draw_effect', a.EntName, ef) end,
  MoveScreen = function(_, m) ev('shake', m.dy, m.dur) end,
  PlayVFX = function(_, em, x, y, dir) ev('vfx', em.Anim.name, x, y, em, tick_val, dir) end,
  AnimateToPosition = function(_, a, anim, face, x, y, anim_speed, speed)
    a.Position = {X=x, Y=y}; a.Direction = face
    ev('glisse', a.EntName, x, y, anim, speed, face)
  end,
  Hide = function(_, n) if actors[n] then actors[n].EntEnabled = false end; ev('hide', n) end,
  Unhide = function(_, n)
    if actors[n] then actors[n].EntEnabled = true end
    local h, p, b = actors.PLAYER, actors.Teammate1, actors[n]
    ev('unhide', n, tick_val, b and b.Position, h and h.Position, p and p.Position,
      b and b.LocHeight, b and b.HideShadow)
  end,
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
  PlayBattleSE=function(_, s) ev('se', s, tick_val) end,
  PlayFanfare=function(_, f) ev('fanfare', f) end,
}
local choice_ret = true
UI = {
  SetSpeaker=function(_, acteur, keysound, espece, forme)
    ev('speaker', type(acteur) == 'string' and acteur or acteur and acteur.EntName, espece, forme)
  end,
  SetSpeakerLoc=function() end, SetSpeakerEmotion=function() end,
  SetCenter=function(_, b) ev('center', b) end,
  ResetSpeaker=function() end, WaitShowDialogue=function(_, t) ev('dlg', t) end,
  WaitShowTitle=function() title_calls = title_calls + 1 end, WaitHideTitle=function() end,
  BeginChoiceMenu=function() end,
  ChoiceMenuYesNo=function() end, WaitForChoice=function() end,
  ChoiceResult=function() return choice_ret end,
}
local unlocked = {}
local camera = {X=240,Y=180}
GAME = {
  CutsceneMode=function() end,
  MoveCamera=function(_, x, y, temps, joueur) camera = {X=x,Y=y}; ev('cam', x, y, temps, joueur) end,
  FadeIn=function(_, duree) ev('fade_in', duree) end,
  FadeOut=function(_, blanc, duree) ev('fade_out', blanc, duree) end,
  WaitFrames=function(_, n)
    tick_val = tick_val + (n or 1) * 120
    RogueEssence.Content.GraphicsManager.TotalFrameTick = tick_val
    ev('wait', n)
  end,
  GetPlayerPartyCount=function() return 2 end,
  GetTeamLeaderIndex=function() return 0 end,
  GetPlayerPartyMember=function(_, i) return {Importance=i==0 and 'Hero' or 'Partner', Data={}} end,
  GetCurrentGround=function() return {Name={ToLocal=function() return 'Fosse Cascade Fond' end}} end,
  GetCameraCenter=function() return camera end,
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

-- 3. fgv1 : PreBattle (Nilo tremble, accusation sans preuve et deux avertissements
--    anonymes avant Tunnel, l’impact et le choix du héros, sans titre de zone)
--    -> revanche / -dev -> PostBattle (fuite au sud en courant) -> EmptyReturn
local fgv1 = assert(loadfile(root .. '/game/Data/Script/destiny/ground/fgv1_fin_grotte_vasques/init.lua'))()
actors = {}; make_actor('PLAYER', 222, 492); make_actor('Teammate1', 198, 484)
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
local fn_fade_in = GAME.FadeIn
GAME.FadeIn = function(_, duree)
  assert(reflet.FrameLength == 0 and not bulles.Visible, 'eau visible en mouvement au pré-combat')
  ev('fade_in', duree)
end

-- Le son et la première bande partent ensemble et ne sont jamais dupliqués.
-- Le moteur déclenche la musique et le fondu d'entrée au BeginFloor.
local function verifier_woosh(chemin)
  local son, noir, duree, nb = nil, nil, 0, 0
  local premiere_bande, derniere_bande, gauche, droite
  for i, e in ipairs(events) do
    if e[1] == 'se' and e[2] == 'EVT_Battle_Transition' then
      assert(not son and events[i - 1][1] == 'fade_bgm', 'un seul woosh sur la sortie BGM')
      son = i
    elseif e[1] == 'vfx' and e[2] == 'Pre_Battle' then
      local bande, tick = e[5], e[6]
      assert(son and not noir and bande.Layer == DrawLayer.Top and bande.RepeatX)
      premiere_bande, derniere_bande = premiere_bande or tick, tick
      gauche, droite = gauche or bande.Movement.X < 0, droite or bande.Movement.X > 0
      nb = nb + 1
    elseif son and e[1] == 'fade_out' then
      assert(not e[2], 'pas de deuxième éclair de transition')
      noir = i
      duree = duree + e[3]
    elseif son and e[1] == 'wait' then
      duree = duree + e[2]
    end
    assert(not (e[1] == 'bgm' and e[2] == 'Boss Battle 2.ogg'), 'la piste du duel appartient à l’arène')
    assert(not (son and (e[1] == 'dlg' or e[1] == 'fade_in' or e[1] == 'se' and i > son)),
      'le woosh ne doit être ni interrompu ni couvert')
  end
  assert(son and noir and nb == 9 and gauche and droite and premiere_bande == events[son][3]
    and derniere_bande > premiere_bande and duree >= 187 and duree <= 195,
    'raccord audiovisuel incomplet ou désynchronisé')
  local e = events[#events]
  assert(e[1] == chemin and e[2] == 'grotte_verdoyante' and e[3] == 1 and e[4] == 0 and e[5] == 0)
  assert(title_calls == 0, 'pas de carton en ground')
end

events = {}
title_calls = 0
fgv1.Enter(carte_fosse)
GAME.FadeIn = fn_fade_in
verifier_woosh('continue_dungeon')
assert(reflet.FrameLength == 8 and autre.FrameLength == 9 and bulles.Visible, 'calques non restaurés à la sortie')
assert(SV.Destiny.GrotteVerdoyantePhase == 1)
assert(actors.Kabutops_Boss and actors.Kabutops_Boss.EntEnabled == true)
local saw_hide, saw_rising_fear = false, false
local seuil, terrasse, premier_dlg, pano_duel, ombre, depart_woosh
local presentation, cherche_maman, innocence, confusion, question, regard_h, regard_p, locuteur
local danger, depart_familles, secours, accusation, menace, plainte, choix, reponse, regard_hero_vers_boss, regard_hero_vers_p
local terre, tremor, apparition, faux, impact, recul_h, recul_p, reposition, haut, reception
local avertissements, reactions = {}, {}
local eaux_interdites = {'Water_Column_Ranger', 'Water_Spout_Splash', 'Wave_Circle_Blue', 'Bubbles_Blue'}
local geysers_interdits = {'EVT_CH05_Waterfall_Cave_Geyser', 'EVT_CH05_Hot_Spring_Splash'}
for i, e in ipairs(events) do
  if e[1] == 'cam' then
    if e[2] == 278 and e[3] == 372 and e[4] > 1 then seuil = i end
    if e[2] == 300 and e[3] == 216 and e[4] > 1 then terrasse = i end
    if e[2] == 300 and e[3] == 240 then pano_duel = i end
  elseif e[1] == 'vfx' and e[2] == 'White' then
    assert(e[5].EndColor.r == 0 and e[5].EndColor.g == 0 and e[5].EndColor.b == 0
      and e[5].StartColor.a == 0 and e[5].EndColor.a > 0 and e[5].EndColor.a < 140,
      'assombrissement modéré : ne pas blanchir la sortie')
    ombre = i
  elseif e[1] == 'vfx' and e[2] == 'Dig' and e[3] == 288 and e[4] == 210 then
    assert(not terre and e[5].Layer == DrawLayer.Front)
    terre = i
  elseif e[1] == 'shake' and not tremor then
    tremor = i
  elseif e[1] == 'unhide' and e[2] == 'Kabutops_Boss' then
    assert(not apparition)
    apparition = i
    local b, h, p = e[4], e[5], e[6]
    assert(b.X * 2 == h.X + p.X and b.Y + 24 == h.Y and h.Y == p.Y,
      'Kabutops doit surgir juste devant le milieu du duo')
    assert(e[7] < 0 and e[8], 'Kabutops commence sous la terre sans ombre en l’air')
  elseif e[1] == 'hauteur' and e[2] == 'Kabutops_Boss' and apparition then
    if e[3] >= 16 then haut = i end
    if e[3] == 0 then reception = i end
  elseif e[1] == 'move' and e[2] == 'Kabutops_Boss' then
    assert(recul_h and recul_p and e[3] == 292 and e[4] == 196, 'pas d’arrivée depuis la rive : juste le raccord à l’arène')
    reposition = i
  end
  if e[1] == 'hide' and e[2] == 'Kabutops_Boss' then saw_hide = true end
  if e[1] == 'bgm' and e[2] == 'Rising Fear.ogg' then saw_rising_fear = true end
  if e[1] == 'se' and e[2] == 'EVT_Battle_Transition' then depart_woosh = i end
  if e[1] == 'anim' and e[2] == 'Kabutops_Boss' and e[3] == 'Attack' then faux = i end
  if e[1] == 'se' and e[2] == 'DUN_Gust_Trap' then impact = i end
  if e[1] == 'vfx' then
    for _, n in ipairs(eaux_interdites) do assert(e[2] ~= n, 'pas de geyser à la révélation') end
  end
  if e[1] == 'se' then
    assert(e[2] ~= 'EVT_Battle_Flash', 'le jaillissement est visible sans plein écran blanc')
    for _, n in ipairs(geysers_interdits) do assert(e[2] ~= n, 'pas de bruit d’eau à la révélation') end
  end
  if e[1] == 'regard' and e[2] == 'PLAYER' and e[3] == 'Teammate1' then
    if #avertissements == 1 then regard_h = i end
    if plainte and not choix then regard_hero_vers_p = i end
  end
  if e[1] == 'regard' and e[2] == 'Teammate1' and e[3] == 'PLAYER' and #avertissements == 1 then regard_p = i end
  if e[1] == 'regard' and e[2] == 'PLAYER' and e[3] == 'Kabutops_Boss' and plainte and not choix then regard_hero_vers_boss = i end
  if e[1] == 'emote' and e[3] == 'question' then question = i end
  if e[1] == 'emote' and terre then reactions[e[2]] = true end
  if e[1] == 'speaker' then
    locuteur = e[2]
    if locuteur == '???' then assert(e[3] == '' and e[4] == -1, 'aucun portrait pour la voix cachée') end
  end
  if e[1] == 'dlg' then
    premier_dlg = premier_dlg or i
    local texte = tostring(e[2])
    local function contient(mot) return texte:find(mot, 1, true) ~= nil end
    if i == premier_dlg then assert(locuteur == 'Nilo_Grotte' and contient('êtes qui') and contient('Pourquoi')) end
    if locuteur == '???' then
      assert(not apparition, 'les avertissements précèdent la révélation')
      avertissements[#avertissements + 1] = i
    elseif locuteur == 'Nilo_Grotte' then
      if contient('Je la cherchais') then cherche_maman = i end
      if contient('rien touché') then innocence = i end
      if contient('je ne comprends pas') then plainte = i end
      assert(not contient('ai touché') or contient('rien touché'), 'pas d’aveu de Nilo')
    elseif locuteur == 'Kabutops_Boss' then
      assert(apparition, 'Kabutops ne doit pas être identifié avant son apparition')
      if contient('sentiers ne sont plus sûrs') then danger = i end
      if contient('quitté la vallée') then depart_familles = i end
      if contient('sûrement de lui') and contient('près de la source') then accusation = i end
      if contient('ne contrôle plus ses éclairs') and contient('village en aval') then menace = i end
    elseif locuteur == 'Teammate1' then
      if contient('équipe de secours') then presentation = i end
      if contient('qui parle ?') then confusion = i end
      if contient('pas dire qu’il y a touché') then secours = i end
      if contient('on ne t’abandonne pas') then reponse = i end
    elseif locuteur == 'PLAYER' then
      assert(texte == "Ce Pokémon est beaucoup trop en colère pour entendre raison... Nous n'avons pas le choix.")
      choix = i
    else
      error('réplique sans le bon locuteur : '..texte)
    end
  end
  if e[1] == 'glisse' and e[5] == 'Hurt' and e[4] == 244 then
    if e[2] == 'PLAYER' then
      assert(e[3] == 292 and e[7] == Direction.UpLeft, 'recul dans l’axe, regard vers le boss')
      recul_h = i
    elseif e[2] == 'Teammate1' then
      assert(e[3] == 268 and e[7] == Direction.UpRight, 'le partenaire ne tourne pas le dos')
      recul_p = i
    end
  end
end
local premier, second = table.unpack(avertissements)
assert(#avertissements == 2 and events[premier][2]:find('Pas un pas de plus', 1, true)
  and events[premier][2]:find('a déréglé le courant', 1, true)
  and events[second][2]:find('reculez', 1, true), 'exactement deux avertissements de ???')
assert(seuil and terrasse and premier_dlg and presentation and cherche_maman
  and seuil < terrasse and terrasse < premier_dlg and premier_dlg < presentation
  and presentation < cherche_maman and cherche_maman < premier, 'la rencontre précède la menace')
assert(regard_h and regard_p and question and confusion and innocence
  and premier < regard_h and premier < regard_p and regard_h < question and regard_p < question
  and question < confusion and confusion < innocence and innocence < second,
  'le duo se cherche du regard et Nilo se défend entre les deux avertissements')
assert(saw_hide and saw_rising_fear and ombre and tremor and terre and apparition and faux and impact
  and second < ombre and ombre < tremor and tremor < terre and terre < apparition and apparition < faux and faux < impact,
  'la secousse et la terre doivent précéder l’impulsion et l’impact de la faux')
-- Les doublures parcourent les branches en série. Mesurer la courbe elle-même ;
-- le vrai chevauchement du recul et de la réception est vérifié en capture.
assert(haut and reception and apparition < haut and haut < reception
  and events[reception][4] - events[apparition][3] <= 24 * 120
  and reactions.PLAYER and reactions.Nilo_Grotte and not actors.Kabutops_Boss.HideShadow,
  'courbe d’élévation et réactions à la sortie du sol')
assert(recul_h and recul_p and danger and depart_familles and secours and reposition and accusation and menace
  and impact < recul_h and recul_h < recul_p and recul_p < danger and danger < depart_familles
  and depart_familles < secours and secours < reposition and reposition < accusation and accusation < menace,
  'l’explication de la vallée suit le recul ; la faute n’est qu’un soupçon')
assert(plainte and choix and regard_hero_vers_boss and regard_hero_vers_p and reponse and pano_duel and depart_woosh
  and menace < plainte and plainte < regard_hero_vers_boss and regard_hero_vers_boss < regard_hero_vers_p
  and regard_hero_vers_p < choix and choix < reponse and reponse < pano_duel and pano_duel < depart_woosh,
  'le héros observe et se tourne vers son partenaire avant la décision, le duel attend la réaction')
assert(actors.PLAYER.Position.X == 292 and actors.PLAYER.Position.Y == 244
  and actors.Teammate1.Position.X == 268 and actors.Teammate1.Position.Y == 244
  and actors.Kabutops_Boss.Position.X == 292 and actors.Kabutops_Boss.Position.Y == 196,
  'la formation du duel retrouve les positions de combat')

-- Les figurants apparaissent APRES le recul du duo. Chacun avance deux fois
-- et finit à la même case/direction que l'ennemi sérialisé en arène.
local garde_attendue = {
  {'Kabuto_Flanc_G',8,9,Direction.DownRight}, {'Kabuto_Flanc_D',11,9,Direction.DownLeft},
  {'Kabuto_Arriere_G',9,12,Direction.Up}, {'Kabuto_Arriere_D',10,12,Direction.Up},
}
local function verifier_garde(revanche)
  local data = require('destiny.fosse_cascade_scene')
  local griffes, regards = 0, 0
  for i, attendu in ipairs(garde_attendue) do
    local nom, col, ligne, dir = table.unpack(attendu)
    local spec = data.GARDE[i]
    assert(spec.nom == nom and spec.x == col and spec.y == ligne and Direction[spec.face] == dir)
    local x, y = data.AncreAuSol(spec)
    local creation, cache, sortie, terre_k, retraite, noir, contour
    local pas = {}
    for j, e in ipairs(events) do
      if e[1] == 'vfx' and e[2] == 'Dig' and e[3] == spec.depart[1]+8 and e[4] == spec.depart[2]+14 then
        assert(e[5].Layer == DrawLayer.Front); terre_k = j
      end
      if i == 1 and e[1] == 'vfx' and e[2] == 'Scratch' then
        assert(e[5].Layer == DrawLayer.Front and e[5].Offset > 0 and e[7] ~= nil)
        griffes = griffes + 1
      end
      if e[1] == 'fade_out' then noir = j end
      if e[1] == 'regard' and e[3] == nom and (e[2] == 'PLAYER' or e[2] == 'Teammate1') then
        regards = regards + 1
      end
      if e[2] == nom then
        if e[1] == 'create' then assert(e[3] == dir); creation = e
        elseif e[1] == 'hide' then cache = j
        elseif e[1] == 'unhide' then
          assert(not sortie and e[7] < 0 and e[8], 'Kabuto commence dans la terre, ombre masquée')
          sortie = j
        elseif e[1] == 'move' then
          assert(e[3] == spec.passage[1] and e[4] == spec.passage[2]); contour = j
        elseif e[1] == 'glisse' then
          assert(e[5] == 'Attack' and contour and contour < j)
          assert(e[7] == (#pas == 0 and Direction[spec.avance] or dir))
          pas[#pas+1] = e
        elseif e[1] == 'remove' and noir then
          assert(e[3] == x and e[4] == y and e[5] == dir)
          retraite = j
        end
      end
    end
    assert(creation and retraite and not actors[nom], 'garde nettoyée au noir du raccord')
    if revanche then
      assert(not cache and not sortie and not terre_k and #pas == 0 and creation[4] == x and creation[5] == y)
    else
      assert(cache and terre_k and sortie and recul_p < cache and cache < terre_k and terre_k < sortie and sortie < danger)
      assert(creation[4] == spec.depart[1] and creation[5] == spec.depart[2])
      assert(#pas == 2 and pas[1][3] == spec.menace[1] and pas[1][4] == spec.menace[2] and pas[2][3] == x and pas[2][4] == y)
    end
  end
  assert(griffes == (revanche and 0 or 4))
  assert(revanche or regards == 4, 'le duo regarde les flancs et le passage arrière')
end
verifier_garde(false)

-- Toute émote jouée doit exister dans base/Data/Emote : un identifiant inconnu
-- donnerait une EmoteData nulle et ferait planter StartEmote en jeu.
local EMOTES_EXISTANTES = {
  angry = true, eating = true, exclaim = true, glowing = true, happy = true,
  notice = true, pose_infirmiere = true, question = true, reveil = true,
  shock = true, sweatdrop = true, sweating = true,
}
for _, e in ipairs(events) do
  if e[1] == 'emote' then
    assert(EMOTES_EXISTANTES[e[3]] == true,
      'émote inconnue jouée par '..tostring(e[2])..' : '..tostring(e[3]))
  end
end

-- Nilo est créé sur la terrasse et ne change jamais de position pendant le pré-combat.
local DEPART_NILO = {x = 304, y = 152}
local depart_vu, nilo_a_bouge, nilo_tremble = false, false, false
for i, e in ipairs(events) do
  if e[1] == 'create' and e[2] == 'Nilo_Grotte' then
    depart_vu = true
    assert(e[4] == DEPART_NILO.x and e[5] == DEPART_NILO.y,
      'Nilo doit rester sur la terrasse ('..DEPART_NILO.x..','..DEPART_NILO.y..')')
  end
  if (e[1] == 'move' or e[1] == 'glisse') and e[2] == 'Nilo_Grotte' then nilo_a_bouge = true end
  if e[1] == 'draw_effect' and e[2] == 'Nilo_Grotte' and e[3] == RogueEssence.Dungeon.DrawEffect.Shaking then
    assert(i < terrasse, 'le tremblement est actif avant de montrer la terrasse')
    nilo_tremble = true
  end
end
assert(depart_vu and actors.Nilo_Grotte.Position.X == DEPART_NILO.x and actors.Nilo_Grotte.Position.Y == DEPART_NILO.y,
       'Nilo doit rester à sa position d’approche')
assert(not nilo_a_bouge and nilo_tremble, 'Nilo tremble sans quitter la terrasse')
assert(events[#events][1] == 'continue_dungeon' and events[#events][2] == 'grotte_verdoyante' and events[#events][3] == 1,
       'le combat Kabutops doit bien se lancer après la cinématique')

-- 3 ter. Une scene INTERROMPUE ne doit jamais se rejouer entierement.
-- C'est le cas reel du journal : le moteur recycle la zone pendant la scene
-- (ScriptEvent.Apply(): Coroutine for event interrupted by break command!),
-- puis la carte est reentrée. On simule l’interruption au premier dialogue.
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
local tunnel_2, tremble_revanche = false, false
for _, e in ipairs(events) do
  if e[1] == 'vfx' and e[2] == 'Dig' then tunnel_2 = true end
  if e[1] == 'draw_effect' and e[2] == 'Nilo_Grotte' then tremble_revanche = e[3] == 2 end
end
assert(not tunnel_2 and tremble_revanche, 'la revanche garde le témoin, pas l’apparition')
verifier_woosh('continue_dungeon')
local repl = 0
for _, e in ipairs(events) do
  if e[1] == 'dlg' then repl = repl + 1 end
  assert(not (e[1] == 'glisse' or e[1] == 'se' and (e[2] == 'DUN_Gust_Trap' or e[2] == 'DUN_Dig')
    or e[1] == 'cam' and e[3] > 300 or e[1] == 'vfx' and e[2] == 'White'
    or e[1] == 'speaker' and e[2] == '???'), 'pas de découverte ni de souffle en revanche')
end
assert(repl == 1, 'la revanche doit rester courte')
verifier_garde(true)
assert(reflet.FrameLength == 8 and autre.FrameLength == 9 and bulles.Visible,
  'la revanche restaure les vasques même après une coupure sur la même instance')

-- En test Ground Editor (-dev : _ZONE.InDevZone == true), la revanche/transition doit appeler EnterDungeon (forceNewZone = true)
_ZONE = {InDevZone = true}
events = {}
fgv1.Enter(carte_fosse)
for _, e in ipairs(events) do
  assert(not (e[1] == 'se' and e[2] == 'EVT_Battle_Flash'), 'pas de révélation rejouée en revanche')
  assert(not (e[1] == 'anim' and e[2] == 'Nilo_Grotte' and e[3] == 'EventSleep'), 'pas de réveil rejoué')
end
verifier_woosh('enter_dungeon') -- zone réelle au lieu d'un ReturnToEditor
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
-- Après le K.O. de toute la garde, les quatre Kabuto expriment leur peur,
-- reculent et replongent. Kabutops ferme la marche, et Nilo attend sa sortie.
local fosse_scene = require('destiny.fosse_cascade_scene')
local derniere_sortie, descente_nilo, nb_terre, bruits = nil, nil, 0, 0
for i, e in ipairs(events) do
  assert(not (e[1] == 'move' and e[2] == 'Kabutops_Boss'), 'plus de course de Kabutops vers le sud')
  assert(not (e[1] == 'vfx' and (e[2] == 'Water_Spout_Splash' or e[2] == 'Wave_Circle_Blue'
      or e[2] == 'Bubbles_Blue' or e[2] == 'Water_Column_Ranger')), 'pas d’eau pendant le Tunnel')
  if e[1] == 'vfx' and e[2] == 'Dig' then nb_terre = nb_terre + 1 end
  if e[1] == 'se' and e[2] == 'DUN_Dig' then bruits = bruits + 1 end
  if e[1] == 'remove' and e[2] == 'Kabutops_Boss' then derniere_sortie = i end
  if e[1] == 'move' and e[2] == 'Nilo_Grotte' then descente_nilo = i end
end
assert(derniere_sortie and descente_nilo and derniere_sortie < descente_nilo and nb_terre == 5 and bruits == 3)
local function verifier_plongeon(nom, x, y, peur)
  local emote, tremble, repli, terre, negatif, masque, retire
  for i, e in ipairs(events) do
    if e[1] == 'vfx' and e[2] == 'Dig' and e[3] == x+8 and e[4] == y+14 then
      assert(e[5].Layer == DrawLayer.Front); terre = i
    end
    if e[2] == nom then
      if e[1] == 'emote' and (e[3] == 'shock' or e[3] == 'sweating') then emote = i end
      if e[1] == 'draw_effect' and e[3] == 2 then tremble = i end
      if e[1] == 'glisse' and e[5] == 'Hurt' then assert(e[3] == x and e[4] == y); repli = i end
      if e[1] == 'hauteur' and e[3] <= -16 then negatif = i end
      if e[1] == 'hide' then masque = i end
      if e[1] == 'remove' then retire = i end
    end
  end
  assert(terre and negatif and masque and retire and terre < negatif and negatif < masque and masque < retire)
  assert(not actors[nom])
  if peur then assert(emote and tremble and repli and emote < tremble and tremble < repli and repli < terre and retire < derniere_sortie) end
end
for _, spec in ipairs(fosse_scene.GARDE) do
  local x,y = fosse_scene.AncreAuSol(spec)
  verifier_plongeon(spec.nom, x+spec.recul[1], y+spec.recul[2], true)
end
verifier_plongeon('Kabutops_Boss', 292, 196, false)

local saw_lyra_reunion, fins, locuteur_post = false, 0, nil
for _, e in ipairs(events) do
  if e[1] == 'speaker' then locuteur_post = e[2] end
  if e[1] == 'dlg' and locuteur_post == 'Lyra_Grotte' and tostring(e[2]):find('Tu es là.', 1, true) then saw_lyra_reunion = true end
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
