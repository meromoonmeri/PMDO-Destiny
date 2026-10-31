--[[ init.lua — Quiz de personnalité PMD Destiny (map personality_test)
     Arrivée : enchaînement depuis intro_halo (intro halo arc-en-ciel +
     titres voice-over + transition blanche) — voir
     Data/Script/destiny/ground/intro_halo/init.lua.
     Flux (schéma de sélection complet, code entièrement rédigé pour
     PMD Destiny) :
       purge de l'équipe par défaut → 15 questions → nature (max de points)
       → badge étoile coloré → recommandation selon la nature ou choix libre
       → sexe → talent → confirmation → choix du partenaire (pool complet, espèce
       différente du héros) → sexe + talent du partenaire → NOM du
       partenaire (NameMenu + confirmation) → la faille du rêve : scène du
       partenaire sur cliffdaytest (version nuit) → donjon Lost Wood
       (7 étages) → clairière du réveil (reveil_nuit).
     Données : questions et recommandations dans quiz_data.lua ; 85 choix
     source dans starters_source.lua, plus les choix Destiny sans doublon.
]]

require 'origin.common'

local quiz_data = require 'destiny.ground.personality_test.quiz_data'
local starters_source = require 'destiny.ground.personality_test.starters_source'
local talents_depart = require 'destiny.talents_depart'

local personality_test = {}

-- ----------------------------------------------------------------- helpers

-- Chaque lettre reçoit une couleur de l'arc-en-ciel (itération UTF-8 sûre).
local function arc_en_ciel(texte)
  local teintes = { '#FF4D4D', '#FF9E2B', '#FFE12B', '#8CE02B', '#2BD9FF', '#3B76FF', '#A64DFF' }
  local out, i = {}, 0
  for car in texte:gmatch('[%z\1-\127\194-\244][\128-\191]*') do
    if car == ' ' or car == '-' then
      table.insert(out, car)
    else
      table.insert(out, '[color=' .. teintes[(i % #teintes) + 1] .. ']' .. car .. '[color]')
      i = i + 1
    end
  end
  return table.concat(out)
end

local function nature_par_slug(slug)
  for _, n in ipairs(quiz_data.natures) do
    if n.slug == slug then return n end
  end
  return nil
end

local function calculer_nature(scores)
  local best, best_score = nil, -1
  for _, n in ipairs(quiz_data.natures) do
    local s = scores[n.slug] or 0
    if s > best_score then
      best, best_score = n.slug, s
    end
  end
  return best
end

-- Réunit les choix source et ceux du quiz préexistant. La clé comprend la
-- forme : un Goupix d'Alola n'est pas confondu avec celui de Kanto.
local function construire_pool(espece_exclue)
  local pool, deja_vu = {}, {}
  local function ajouter(s)
    local key = s.espece .. ':' .. tostring(s.forme)
    if s.espece ~= espece_exclue and not deja_vu[key] then
      deja_vu[key] = true
      table.insert(pool, s)
    end
  end
  for _, s in ipairs(starters_source.starters) do ajouter(s) end
  for _, s in pairs(quiz_data.starters) do ajouter(s) end
  table.sort(pool, function(a, b)
    if a.gen ~= b.gen then return a.gen < b.gen end
    return a.nom < b.nom
  end)
  return pool
end

-- MultiPageMenu accepte des libellés explicites, contrairement au menu
-- MonsterID qui n'affiche que le nom d'espèce et masque les formes régionales.
local function choisir_dans_pool(pool, titre)
  local labels = {}
  for _, s in ipairs(pool) do table.insert(labels, s.nom) end
  UI:BeginMultiPageMenu(16, 16, 224, titre, labels, 8, 1, -1)
  UI:WaitForChoice()
  return pool[UI:ChoiceResult()]
end

local function choisir_genre(question)
  UI:BeginChoiceMenu(question, { "Garçon", "Fille", "Non-binaire" }, 1, 1)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == 2 then return Gender.Female end
  if choix == 3 then return Gender.Genderless end
  return Gender.Male
end

-- ------------------------------------------------------------- map callbacks

function personality_test.Init(map)
end

function personality_test.Enter(map)
  personality_test.PlotScripting()
end

function personality_test.Exit(map)
end

function personality_test.Update(map)
end

function personality_test.GameSave(map)
end

function personality_test.GameLoad(map)
  personality_test.PlotScripting()
end

function personality_test.PlotScripting()
  if SV.Destiny ~= nil and (SV.Destiny.ReveilFait or SV.Destiny.PartenaireParti) then
    -- la séquence du rêve est déjà engagée : ne jamais renvoyer le héros
    -- vers une autre ville pendant qu'il est encore allongé.
    return
  end
  personality_test.Quiz()
end

-- ------------------------------------------------------------ scène du quiz

function personality_test.Quiz()
  GAME:CutsceneMode(true)
  -- Seul le fond du rêve et les menus doivent être visibles pendant le quiz.
  GROUND:Hide('PLAYER')
  UI:ResetSpeaker()
  -- arrivée depuis l'intro halo : le fondu blanc se lève sur le fond Dream
  SOUND:PlayBGM("Welcome to the World of Pokémon!.ogg", true)
  GAME:FadeIn(40)
  GAME:WaitFrames(20)

  -- purge de l'équipe par défaut créée par la Nouvelle partie (missingno) :
  -- le héros est créé par le quiz lui-même
  local party_count = _DATA.Save.ActiveTeam.Players.Count
  for ii = 1, party_count, 1 do
    _DATA.Save.ActiveTeam.Players:RemoveAt(0)
  end
  local assembly_count = GAME:GetPlayerAssemblyCount()
  for i = 1, assembly_count, 1 do
    _DATA.Save.ActiveTeam.Assembly:RemoveAt(0)
  end

  -- 15 questions — chaque choix distribue +4/+2 sur les 16 natures
  local scores = {}
  for _, n in ipairs(quiz_data.natures) do scores[n.slug] = 0 end

  for num, q in ipairs(quiz_data.questions) do
    local intitules = {}
    for _, c in ipairs(q.choix) do table.insert(intitules, c.texte) end
    UI:BeginChoiceMenu('(' .. num .. '/15) ' .. q.texte, intitules, 1, 1)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    for slug, pts in pairs(q.choix[choix].points) do
      scores[slug] = (scores[slug] or 0) + pts
    end
  end

  -- nature = score maximal ; le badge étoile prend sa couleur
  local slug = calculer_nature(scores)
  local nature = nature_par_slug(slug)
  local starter_id = quiz_data.mapping[slug]
  local starter = quiz_data.starters[starter_id]

  UI:WaitShowVoiceOver("L'analyse est terminée...", -1)
  UI:WaitShowVoiceOver("Ton aura révèle une nature de couleur\n" .. nature.couleur ..
    " ! Le badge étoile s'illumine.", -1)
  -- TODO visuel : afficher Content/UI/quiz_badges/badge_etoile_<slug>.png
  -- (menu image custom) — la scène est fonctionnelle en dialogues sans.

  UI:WaitShowVoiceOver("Le starter qui te correspond est...\n" .. starter.nom .. " !", -1)
  UI:ChoiceMenuYesNo("Veux-tu garder ce résultat ?\nSinon, choisis librement ton Pokémon.", true)
  UI:WaitForChoice()
  local pool_heros = construire_pool(nil)
  if not UI:ChoiceResult() then
    starter = choisir_dans_pool(pool_heros, "Choisis ton héros")
  else
    -- Réutilise l'entrée complète source correspondant à la recommandation.
    for _, s in ipairs(pool_heros) do
      if s.espece == starter.espece and s.forme == starter.forme then starter = s; break end
    end
  end

  local genre, talent
  local ok = false
  while not ok do
    genre = choisir_genre("Quel est ton sexe ?")
    talent = talents_depart.choisir(starter.espece, starter.forme, starter.nom, 'héros')
    local msg = "Êtes-vous sûr de sélectionner ce Pokémon ?\n" .. starter.nom
    if starter.mega_famille then
      msg = msg .. "\nUne évolution de cette lignée possède une forme de " .. arc_en_ciel(quiz_data.mega_texte) .. "."
    end
    UI:ChoiceMenuYesNo(msg, true)
    UI:WaitForChoice()
    ok = UI:ChoiceResult()
    if not ok then starter = choisir_dans_pool(pool_heros, "Choisis ton héros") end
  end

  -- création du héros (niveau 5, talent choisi)
  local mon_id = RogueEssence.Dungeon.MonsterID(starter.espece, starter.forme, 'normal', genre)
  -- "none" est le rang initial de Destiny (StartParams.xml) ; "unranked"
  -- est un identifiant de projet de Palikadude absent des données de cette Quest.
  _DATA.Save.ActiveTeam:SetRank("none")
  _DATA.Save.ActiveTeam.Money = 0
  _DATA.Save.NoSwitching = true
  _DATA.Save.ActiveTeam.Players:Add(_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand, mon_id, 5, talent, 0))
  _DATA.Save.ActiveTeam.Players[0].IsFounder = true
  GAME:SetTeamLeaderIndex(0)
  -- Le changement de meneur recrée l'entité PLAYER : la recacher jusqu'à la
  -- transition, pour ne pas superposer le sprite aux textes du rêve.
  GROUND:Hide('PLAYER')

  -- ---------------------------------------------------- choix du partenaire
  UI:WaitShowVoiceOver("Un Pokémon ne part jamais seul...\nQui sera ton partenaire ?", -1)

  -- La règle Destiny interdit toujours la même espèce pour le partenaire.
  -- Les formes régionales restent clairement identifiées dans les libellés.
  local pool_partenaire = construire_pool(starter.espece)
  local partenaire, ok_partenaire
  repeat
    partenaire = choisir_dans_pool(pool_partenaire, "Choisis ton partenaire")
    UI:ChoiceMenuYesNo("Est-ce que " .. partenaire.nom .. " convient comme partenaire ?", true)
    UI:WaitForChoice()
    ok_partenaire = UI:ChoiceResult()
  until ok_partenaire

  local pgenre = choisir_genre("Quel est le sexe de ton partenaire ?")
  local partner_id = RogueEssence.Dungeon.MonsterID(partenaire.espece, partenaire.forme, 'normal', pgenre)
  local ptalent = talents_depart.choisir(partenaire.espece, partenaire.forme, partenaire.nom, 'partenaire')

  -- création du partenaire
  _DATA.Save.ActiveTeam.Players:Add(_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand, partner_id, 5, ptalent, 0))

  -- ------------------------------------------------------- nom du partenaire
  local nom = ""
  local ok_nom = false
  while not ok_nom do
    UI:NameMenu("Quel est le nom de ton partenaire ?", "Un petit surnom, et l'aventure est lancée.", 60)
    UI:WaitForChoice()
    nom = UI:ChoiceResult()
    if nom == "" then
      nom = _DATA:GetMonster(partner_id.Species).Name:ToLocal()
    end
    UI:ChoiceMenuYesNo("Le nom [color=#FFFF00]" .. nom .. "[color] convient-il ?", true)
    UI:WaitForChoice()
    ok_nom = UI:ChoiceResult()
  end

  local hero = GAME:GetPlayerPartyMember(0)
  local partner = GAME:GetPlayerPartyMember(1)
  GAME:SetCharacterNickname(partner, nom)
  GAME:SetTeamName(nom)

  -- les deux restent dans l'équipe (fondateurs / partenaires inséparables)
  _DATA.Save.ActiveTeam.Players[0].IsFounder = true
  _DATA.Save.ActiveTeam.Players[0].IsPartner = true
  _DATA.Save.ActiveTeam.Players[1].IsFounder = true
  _DATA.Save.ActiveTeam.Players[1].IsPartner = true
  _DATA.Save.ActiveTeam.Players[0]:FullRestore()
  _DATA.Save.ActiveTeam.Players[1]:FullRestore()
  local hTbl = LTBL(hero)
  local pTbl = LTBL(partner)
  hTbl.Importance = 'Hero'
  pTbl.Importance = 'Partner'

  -- ------------------------------------- la faille : le rêve se fend
  -- pendant que le héros est encore allongé, on rejoint celui qui hésite
  -- encore à devenir explorateur (map cliffdaytest, version nuit)
  UI:WaitShowVoiceOver("Une faille s'ouvre dans le rêve...", -1)
  UI:WaitShowVoiceOver("...quelque part, quelqu'un hésite encore\n à devenir explorateur.", -1)
  SOUND:FadeOutBGM(120)
  GAME:FadeOut(false, 120)
  GAME:WaitFrames(60)
  GAME:CutsceneMode(false)
  GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Crossroads')
end

return personality_test
