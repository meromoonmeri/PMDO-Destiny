-- Tests de bout en bout du prologue sans ressources moteur :
-- sommeil du héros sur zrv2_zone_reveil_nuit -> départ du partenaire sur le chemin
-- de cliffdaytest_nuit -> Lost Wood aller -> grande cinématique PMD de rencontre sur
-- zrv2_zone_reveil_nuit (héros muet en pensées (...), saisie du prénom, lent travelling
-- vers la montagne avec portrait Inspired, choix multiples, Réverie Town capitale des
-- explorateurs, pose finale au nord + texte blanc sur fond noir) -> Lost Wood retour en
-- sens inverse (étage 6 = 7F) -> arrivée de jour sur cliffdaytest -> ville.
-- Usage depuis la racine du dépôt : lua tools/tests/test_lost_wood.lua
package.path = 'game/Data/Script/?.lua;game/Data/Script/?/init.lua;' .. package.path
package.preload['origin.common'] = function() return {} end

local function noop() end
Gender = { Genderless = 0, Male = 1, Female = 2 }
Direction = { Down = 4, DownLeft = 5, Left = 6, UpLeft = 7, Up = 0, UpRight = 1, Right = 2, DownRight = 3 }
RogueEssence = {
  Data = {
    GameProgress = {
      ResultType = { Cleared = 2, Downed = 0, Failed = 1, GaveUp = 5, Escaped = 3 },
      DungeonStakes = { Risk = 2 },
    },
  },
}

local hero = { name = '', Nickname = '', IsFounder = true, data = { Importance = 'Hero' }, held = 'baie', exp = 123, CurrentForm = { Species = 'riolu', Form = 0, Skin = 'normal', Gender = Gender.Male } }
local partner = { name = 'PARTNER', Nickname = 'PARTNER', IsFounder = true, data = { Importance = 'Partner' }, exp = 234, CurrentForm = { Species = 'eevee', Form = 0, Skin = 'normal', Gender = Gender.Female } }
local recruit = { name = 'RECRUE', IsFounder = false, data = {} }
local other = { name = 'AUTRE', IsFounder = false, data = {} }
local party, assembly, leader, actors, events, dialogues, voiceovers, menus = {}, {}, 0, {}, {}, {}, {}, {}
local choice_queue = {}
local current_speaker, current_keysound, current_emotion = nil, true, 'Normal'

SV = { Destiny = {} }
LTBL = function(ch) return ch and ch.data end
CH = function(n) return actors[n] end
MRKR = function(n)
  if n == 'Pichu_Home_Door' then return { Position = { X = 600, Y = 442 } } end
  if n == 'Dazzling_Exit_East' then return { Position = { X = 960, Y = 468 } } end
  if n == 'Pichu_Crossroads' then return { Position = { X = 640, Y = 518 } } end
  return { Position = { X = 666, Y = 516 } }
end

local function actor(ch, x, y)
  return {
    Data = ch,
    CurrentForm = ch and ch.CurrentForm or nil,
    Position = { X = x or 0, Y = y or 0 },
    GetDisplayName = function()
      local n = ch and (ch.Nickname ~= '' and ch.Nickname or ch.name) or 'Inconnu'
      return n ~= '' and n or 'Riolu'
    end,
  }
end

TASK = {
  BranchCoroutine = function(_, fn) fn(); return true end,
  JoinCoroutines = noop,
}
GAME = {
  GetPlayerPartyCount = function() return #party end,
  GetPlayerPartyMember = function(_, i) assert(party[i + 1]); return party[i + 1] end,
  GetPlayerAssemblyCount = function() return #assembly end,
  GetPlayerAssemblyMember = function(_, i) assert(assembly[i + 1]); return assembly[i + 1] end,
  GetTeamLeaderIndex = function() return leader end,
  SetTeamLeaderIndex = function(_, i) leader = i; actors.PLAYER = actor(party[i + 1]) end,
  SetCharacterNickname = function(_, ch, nick) ch.Nickname = nick; ch.name = nick end,
  AddPlayerTeam = function(_, ch) table.insert(party, ch) end,
  RemovePlayerAssembly = function(_, i) table.remove(assembly, i + 1) end,
  AddPlayerAssembly = function(_, ch) table.insert(assembly, 1, ch) end,
  SetRescueAllowed = noop,
  UnlockDungeon = noop,
  EndDungeonRun = function(_, r, z, segment, map, entry, display, fanfare) table.insert(events, { 'end', r, z, map }) end,
  EnterZone = function(_, z, seg, map, entry) table.insert(events, { 'enter', z, map, seg, entry }) end,
  EnterGroundMap = function(_, z, name, entry) table.insert(events, { 'ground', z, name, entry }) end,
  EnterDungeon = function(_, z, seg, mapid, entry) table.insert(events, { 'dungeon', z, seg, mapid, entry }) end,
  MoveCamera = function(_, x, y, duration, to_player) table.insert(events, { 'camera', x, y, to_player, duration }) end,
  CutsceneMode = function(_, v) table.insert(events, { 'cutscene', v }) end,
  FadeOut = function(_, white, dur) table.insert(events, { 'fadeout', white, dur }) end,
  FadeIn = function(_, dur) table.insert(events, { 'fadein', dur }) end,
  WaitFrames = noop,
}
GROUND = {
  RemoveCharacter = function(_, n) actors[n] = nil end,
  CreateCharacterFromCharData = function(_, n, ch, x, y, dir) actors[n] = actor(ch, x, y); return actors[n] end,
  TeleportTo = function(_, ch, x, y, dir) assert(ch); ch.Position = { X = x, Y = y }; table.insert(events, { 'tp', ch.Data, x, y }) end,
  MoveToPosition = function(_, ch, x, y, run, spd) assert(ch); ch.Position = { X = x, Y = y }; table.insert(events, { 'walk', ch.Data, x, y }) end,
  CharSetAnim = function(_, ch, anim_name, loop) table.insert(events, { 'anim', ch and ch.Data, anim_name, loop }) end,
  CharEndAnim = noop,
  Hide = noop,
  RefreshPlayer = noop,
  EntTurn = function(_, ch, dir) table.insert(events, { 'turn', ch and ch.Data, dir }) end,
  CharAnimateTurnTo = function(_, ch, dir) table.insert(events, { 'turn', ch and ch.Data, dir }) end,
  CharSetEmote = noop,
}
AI = {
  DisableCharacterAI = noop,
  EnableCharacterAI = noop,
  SetCharacterAI = function(_, ch, path) assert(ch); ch.ai = path end,
}
UI = {
  ResetSpeaker = function() current_speaker = nil; current_keysound = true; current_emotion = 'Normal' end,
  SetSpeaker = function(_, a, ks)
    assert(a ~= nil)
    current_speaker = a
    current_keysound = (ks == nil) and true or ks
  end,
  SetSpeakerEmotion = function(_, emo) current_emotion = emo end,
  WaitShowDialogue = function(_, txt)
    table.insert(dialogues, { speaker = current_speaker, keysound = current_keysound, emotion = current_emotion, text = txt })
  end,
  WaitShowVoiceOver = function(_, txt, dur)
    table.insert(voiceovers, { text = txt, dur = dur })
  end,
  NameMenu = function(_, title, desc)
    table.insert(menus, { type = 'name', title = title, desc = desc })
  end,
  BeginChoiceMenu = function(_, prompt, opts)
    table.insert(menus, { type = 'choice', prompt = prompt, options = opts })
  end,
  ChoiceMenuYesNo = function(_, prompt, default_no)
    table.insert(menus, { type = 'yesno', prompt = prompt, default_no = default_no })
  end,
  WaitShowTitle = noop,
  WaitHideTitle = noop,
  WaitForChoice = noop,
  ChoiceResult = function()
    if #choice_queue > 0 then return table.remove(choice_queue, 1) end
    return false
  end,
}
SOUND = { FadeOutBGM = noop, PlayBGM = noop, StopBGM = noop, PlayBattleSE = noop }

local equipe = require 'destiny.equipe_scene'
local zone = require 'destiny.zone.lost_wood.init'
local reveil_zrv2 = require 'destiny.ground.zrv2_zone_reveil_nuit.init'
local cliff_nuit = require 'destiny.ground.cliffdaytest_nuit.init'
local cliff_jour = require 'destiny.ground.cliffdaytest.init'

local R = RogueEssence.Data.GameProgress.ResultType

-- Vérifie que chaque réplique du héros est une pensée intérieure entre parenthèses sans son de voix.
local function verifier_heros_muet(liste_dialogues)
  for _, d in ipairs(liste_dialogues) do
    local est_heros = (type(d.speaker) == 'table' and d.speaker.Data == hero)
      or (type(d.speaker) == 'string' and d.speaker:find('???', 1, true) ~= nil)
    if est_heros then
      assert(d.keysound == false, 'le héros ne doit jamais parler à voix haute : ' .. d.text)
      assert(d.text:sub(1, 1) == '(' and d.text:sub(-1) == ')', 'les pensées du héros doivent être entre parenthèses : ' .. d.text)
    end
  end
end

-- 1. Cinématique de sommeil du héros sur zrv2_zone_reveil_nuit juste avant le partenaire.
party = { hero, partner }; assembly = { other }; leader = 0
actors = { PLAYER = actor(hero) }; events = {}; dialogues = {}; voiceovers = {}; menus = {}
SV = { Destiny = { IntroReveilHerosFait = false } }
reveil_zrv2.Init()
reveil_zrv2.Enter()
assert(SV.Destiny.IntroReveilHerosFait == true)
assert(#dialogues == 4)
assert(dialogues[1].speaker == nil and dialogues[1].text:find('Où suis-je', 1, true))
assert(dialogues[2].speaker == nil and dialogues[2].text:find('Qui suis-je', 1, true))
assert(dialogues[3].speaker == nil and dialogues[3].text:find('Tout me semble si flou', 1, true))
assert(dialogues[4].speaker == nil and dialogues[4].text:find("J'ai sommeil", 1, true))
assert(events[#events][1] == 'ground' and events[#events][2] == 'destiny_cliff_tests' and events[#events][3] == 'cliffdaytest_nuit')

-- 2. Départ du partenaire sur cliffdaytest_nuit : sort de la maison et marche sur le chemin est vers Lost Wood.
events = {}; dialogues = {}
_DATA = { Save = { ActiveTeam = { Players = { RemoveAt = function(_, i) table.remove(party, i + 1) end } } } }
local spawn_data
GROUND.SpawnerSetSpawn = function(_, name, ch) spawn_data = ch end
GROUND.SpawnerDoSpawn = function(_, name) return actor(spawn_data) end
cliff_nuit.ScenePartenaire()
assert(#party == 1 and party[1] == partner and leader == 0 and assembly[1] == hero and assembly[2] == other)
assert(SV.Destiny.HeroAssemblyIndex == 0 and hero.held == 'baie' and hero.exp == 123)
local a_marche_chemin_est = false
for _, ev in ipairs(events) do
  if ev[1] == 'walk' and ev[2] == partner and ev[3] >= 850 and ev[4] == 468 then
    a_marche_chemin_est = true
  end
end
assert(a_marche_chemin_est, 'le partenaire doit marcher le long du chemin est vers Lost Wood')
assert(events[#events][1] == 'dungeon' and events[#events][2] == 'lost_wood' and events[#events][4] == 0)

-- 3. KO / abandon à l'aller solo : héros toujours hors du plan, pause et reprise à l'entrée est.
local function setup_solo()
  party = { partner }; assembly = { hero, other }; leader = 0; actors = { PLAYER = actor(partner) }; events = {}
  SV = { Destiny = { LostWoodTrip = 'aller', PartenaireParti = true, HeroAssemblyIndex = 0 } }
end
for _, case in ipairs({ { R.Downed, 'ko' }, { R.Failed, 'ko' }, { R.GaveUp, 'abandon' }, { R.Escaped, 'abandon' } }) do
  setup_solo(); zone.ExitSegment(nil, case[1], false, 0, 0)
  assert(#party == 1 and party[1] == partner and assembly[1] == hero)
  assert(SV.Destiny.LostWoodTrip == 'echec_aller' and SV.Destiny.LostWoodCause == case[2])
  assert(events[#events][1] == 'enter' and events[#events][2] == 'destiny_cliff_tests' and events[#events][3] == 4)
  choice_queue = { false }; cliff_nuit.SceneEchecPartenaire()
  assert(actors.PLAYER.Data == partner and actors.Teammate1 == nil and assembly[1] == hero)
  assert(actors.PLAYER.Position.X == 864 and actors.PLAYER.Position.Y == 468)
  assert(SV.Destiny.LostWoodTrip == 'pause_aller')
  local camera = events[#events - 1]
  assert(camera[1] == 'camera' and camera[2] == 0 and camera[3] == 0 and camera[4] == true)
  actors.PLAYER.Position.X = 948; cliff_nuit.Update()
  assert(SV.Destiny.LostWoodTrip == 'aller' and events[#events][1] == 'dungeon')
end

-- 4. Succès de l'aller solo -> arrivée sur zrv2_zone_reveil_nuit (reverie, map 10).
setup_solo(); zone.ExitSegment(nil, R.Cleared, false, 0, 0)
assert(#party == 1 and assembly[1] == hero and SV.Destiny.LostWoodTrip == 'rencontre')
assert(events[#events][1] == 'enter' and events[#events][2] == 'reverie' and events[#events][3] == 10)

-- 5. Grande cinématique de rencontre PMD sur zrv2_zone_reveil_nuit :
--    prénom saisi, joli prénom, marche vers montagne + caméra + portrait Inspired,
--    choix multiples (option 3 « J'ai des projets haha… »), Réverie Town capitale des explorateurs,
--    héros 100% muet en pensées (...), pose finale des deux au nord, fondu noir + texte blanc.
table.insert(assembly, 1, recruit)
events = {}; dialogues = {}; voiceovers = {}; menus = {}
-- Saisie du prénom 'Sacha' -> confirmation Oui -> choix multiple 3 ("J'ai des projets haha… ouais t'en fais pas !")
choice_queue = { 'Sacha', true, 3 }
reveil_zrv2.Init()
assert(#party == 2 and party[2] == hero and assembly[1] == recruit and assembly[2] == other)
assert(leader == 1 and hero.held == 'baie' and hero.exp == 123 and partner.exp == 234)
assert(equipe.RestaurerHeros() and #party == 2) -- idempotent au rechargement
reveil_zrv2.Enter()

assert(hero.Nickname == 'Sacha', 'le prénom saisi par le joueur doit être enregistré sur le héros')
assert(#dialogues >= 55, 'la cinématique de rencontre doit être étoffée (attendu >= 55 boîtes)')
verifier_heros_muet(dialogues)

-- Vérifier le menu de prénom et le menu à choix multiples PMD
local vu_menu_nom, vu_menu_choix = false, false
for _, m in ipairs(menus) do
  if m.type == 'name' then vu_menu_nom = true end
  if m.type == 'choice' then
    vu_menu_choix = true
    assert(#m.options >= 3)
    assert(m.options[1]:find('Je sais pas', 1, true))
    assert(m.options[2]:find('Je verrai bien', 1, true))
    assert(m.options[3]:find("J'ai des projets haha", 1, true))
  end
end
assert(vu_menu_nom and vu_menu_choix)

-- Vérifier les temps forts narratifs et visuels de la rencontre
local texte_rencontre = ''
local vu_portrait_emerveille = false
for _, d in ipairs(dialogues) do
  texte_rencontre = texte_rencontre .. '\n' .. d.text
  if d.speaker == actors.Teammate1 and d.emotion == 'Inspired' and d.text:find('montagne', 1, true) then
    vu_portrait_emerveille = true
  end
end
assert(vu_portrait_emerveille, 'le partenaire doit afficher son portrait émerveillé (Inspired) face à la montagne')
assert(texte_rencontre:find('joli prénom', 1, true))
assert(texte_rencontre:find("équipe d'explorateurs", 1, true))
assert(texte_rencontre:find('capitale des explorateurs', 1, true))
assert(texte_rencontre:find('comment je suis arrivé ici', 1, true))

-- Vérifier la marche vers la montagne, le lent mouvement caméra nord, les hochements, la pose finale et le texte blanc sur fond noir
local vu_cam_montagne, vu_nod_heros, pose_heros, pose_partenaire = false, false, false, false
for _, ev in ipairs(events) do
  if ev[1] == 'camera' and ev[2] == 384 and ev[3] == 120 and (ev[5] or 0) >= 180 then
    vu_cam_montagne = true
  end
  if ev[1] == 'anim' and ev[2] == hero and ev[3] == 'Nod' then vu_nod_heros = true end
  if ev[1] == 'anim' and ev[2] == hero and ev[3] == 'Pose' and ev[4] == true then pose_heros = true end
  if ev[1] == 'anim' and ev[2] == partner and ev[3] == 'Pose' and ev[4] == true then pose_partenaire = true end
end
assert(vu_cam_montagne, 'la caméra doit monter lentement vers la montagne')
assert(vu_nod_heros, 'le héros doit répondre par des mouvements/hochements de tête')
assert(pose_heros and pose_partenaire, 'le héros et le partenaire doivent prendre la pose devant le paysage nord')
assert(#voiceovers >= 3 and voiceovers[#voiceovers].text:find('nouvelle histoire commença', 1, true))

assert(SV.Destiny.RetrouvaillesFaites == true and SV.Destiny.LostWoodTrip == 'retour')
assert(events[#events][1] == 'dungeon' and events[#events][2] == 'lost_wood' and events[#events][3] == 0 and events[#events][4] == 6)

-- 6. Retour duo : échec renvoie sur zrv2_zone_reveil_nuit (map 10), succès envoie de jour sur cliffdaytest (map 0) !
for _, case in ipairs({ { R.Failed, false }, { R.GaveUp, false }, { R.Cleared, true } }) do
  party = { partner, hero }; assembly = { other }; leader = 1; events = {}; dialogues = {}
  SV = { Destiny = { LostWoodTrip = 'retour', RetrouvaillesFaites = true } }
  zone.ExitSegment(nil, case[1], false, 0, 0)
  assert(party[1] == partner and party[2] == hero and hero.held == 'baie')
  if case[2] then
    assert(events[#events][2] == 'destiny_cliff_tests' and events[#events][3] == 0)
    assert(SV.Destiny.RetourAccompli == true)
  else
    assert(events[#events][2] == 'reverie' and events[#events][3] == 10)
    assert(SV.Destiny.LostWoodRetourEchec == true)
    reveil_zrv2.Enter()
    verifier_heros_muet(dialogues)
    assert(events[#events][1] == 'dungeon' and events[#events][4] == 6)
  end
end

-- 7. Scène de jour sur cliffdaytest : héros toujours muet en pensées (...), maison du partenaire,
--    orpheline/orphelin + Tatie Kangourex, Réverie Town, équipes de secours/explorateurs et Guildes.
party = { partner, hero }; assembly = { other }; leader = 1
actors = { PLAYER = actor(hero), Pichu = actor(other, 600, 476) }
events = {}; dialogues = {}
SV = { Destiny = { RetourAccompli = true, FinaleDestiny = false } }
cliff_jour.Init()
cliff_jour.Enter()
verifier_heros_muet(dialogues)
assert(SV.Destiny.FinaleDestiny == true and SV.Destiny.VisiteVille == 'en_route')
assert(actors.Teammate1.Data == partner and actors.Teammate1.ai == 'origin.ai.ground_partner')
local texte_complet = ''
for _, d in ipairs(dialogues) do texte_complet = texte_complet .. '\n' .. d.text end
assert(texte_complet:find('Voilà ma maison', 1, true))
assert(texte_complet:find('orpheline', 1, true))
assert(texte_complet:find('Tatie Kangourex', 1, true))
assert(texte_complet:find('Réverie Town', 1, true))
assert(texte_complet:find('équipes de secours', 1, true) and texte_complet:find("équipes d'explorateurs", 1, true))
assert(texte_complet:find('à travers le monde entier, il existe des Guildes', 1, true))
assert(events[#events][1] == 'enter' and events[#events][2] == 'town02_waterfallvillage' and events[#events][3] == 0)

-- 8. Ne pas sélectionner un mauvais héros si plusieurs fondateurs sont ambigus.
party = { partner }; assembly = { { IsFounder = true, data = {} }, { IsFounder = true, data = {} } }; leader = 0; SV = { Destiny = {} }
assert(not equipe.RestaurerHeros() and #party == 1 and #assembly == 2)

print('Lost Wood & Prologue PMD : sommeil zrv2, départ chemin est, rencontre complète (prénom, pensées, montagne, choix, pose, texte blanc), retour inverse 7F->1F et falaise de jour OK.')
