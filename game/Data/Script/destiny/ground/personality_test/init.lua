--[[ init.lua — Quiz de personnalité PMD Destiny (map personality_test)
     Arrivée : enchaînement depuis intro_halo (intro halo arc-en-ciel +
     titres voice-over + transition blanche) — voir
     Data/Script/destiny/ground/intro_halo/init.lua.
     Flux (schéma de sélection complet, code entièrement rédigé pour
     PMD Destiny) :
       purge de l'équipe par défaut → 20 questions sans compteur affiché
       → nature (max de points, réponses récentes en départage) → étoile
       déjà formée mais sans couleur, puis clic du joueur : l'animation de
       couleur jaillit au point cliqué, teintée selon le type du starter
       → recommandation selon la nature ou choix libre
       → sexe → talent → confirmation → choix du partenaire (pool complet, espèce
       différente du héros) → sexe + talent du partenaire → NOM du
       partenaire (NameMenu + confirmation) → la faille du rêve : héros
       endormi dans la prairie du réveil (zrv2_zone_reveil_nuit), puis scène
       du partenaire sur cliffdaytest (version nuit) → donjon Lost Wood
       (7 étages) → retrouvailles dans la même prairie.
     Données : questions et recommandations dans quiz_data.lua ; 85 choix
     source dans starters_source.lua, plus les choix Destiny sans doublon.
]]

require 'origin.common'

local quiz_data = require 'destiny.ground.personality_test.quiz_data'
local starters_source = require 'destiny.ground.personality_test.starters_source'
local talents_depart = require 'destiny.talents_depart'

local personality_test = {}

-- Entrées FrameInput.InputType de RogueEssence (PMDC 0.8.12) :
-- 0 = Confirm, 30 = RightMouse. IsInputDown lit l'état de la frame courante.
local INPUT_CONFIRM = 0
local INPUT_RIGHT_MOUSE = 30
local CHARGE_MAX = 150 -- secours sans VFX : environ 2,5 s à 60 images/s

-- Animation fluide : progression continue calculée à chaque frame, sans
-- jamais remplacer le fond Dream de la carte. Les particules ont toutes
-- rejoint le point à 70 % ; l'étoile ne commence donc à se matérialiser
-- qu'après cette convergence. Les ondes bouclent à leur propre rythme,
-- le halo suit la charge et l'étoile finit par seize poses scintillantes.
local FLUIDE_FRAMES = 192 -- environ 3,2 secondes de maintien à 60 images/s
local FLUIDE_CONVERGENCE = 0.70
local FLUIDE_PARTICULES = 72
local FLUIDE_HALO_POSES = 81
local FLUIDE_ONDES_POSES = 36
local FLUIDE_ETOILE_POSES = 73
local FLUIDE_ETOILE_MATERISATION_FIN = 56
local FLUIDE_HALO_TAILLE = 192
local FLUIDE_ONDES_TAILLE = 224
local FLUIDE_PARTICULE_TAILLE = 24
local FLUIDE_ETOILE_L, FLUIDE_ETOILE_H = 192, 216

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

local function hex_rgb(hex)
  if type(hex) ~= 'string' then return nil end
  local r = tonumber(hex:sub(2, 3), 16)
  local g = tonumber(hex:sub(4, 5), 16)
  local b = tonumber(hex:sub(6, 7), 16)
  if r == nil or g == nil or b == nil then return nil end
  return r, g, b
end

local function melanger_hex(debut_hex, fin_hex, ratio)
  local r1, g1, b1 = hex_rgb(debut_hex)
  local r2, g2, b2 = hex_rgb(fin_hex)
  if r1 == nil or r2 == nil then return debut_hex or fin_hex or '#FFFFFF' end
  ratio = math.max(0, math.min(1, ratio or 0))
  return string.format('#%02X%02X%02X',
    math.floor(r1 + (r2 - r1) * ratio + 0.5),
    math.floor(g1 + (g2 - g1) * ratio + 0.5),
    math.floor(b1 + (b2 - b1) * ratio + 0.5))
end

-- Nom du starter coloré selon son type. Pour un double type, le nom forme
-- un dégradé lettre par lettre entre les deux couleurs de types.
local function nom_colore_type(starter)
  local couleurs = starter.couleurs_types or {}
  if #couleurs == 0 and starter.couleur_type ~= nil then
    couleurs = { starter.couleur_type }
  end
  if #couleurs == 0 then return starter.nom end
  if #couleurs == 1 then
    return '[color=' .. couleurs[1] .. ']' .. starter.nom .. '[color]'
  end

  local lettres = {}
  for car in starter.nom:gmatch('[%z\1-\127\194-\244][\128-\191]*') do
    table.insert(lettres, car)
  end
  local visibles = 0
  for _, car in ipairs(lettres) do
    if car ~= ' ' and car ~= '-' then visibles = visibles + 1 end
  end
  local out, rang = {}, 0
  for _, car in ipairs(lettres) do
    if car == ' ' or car == '-' then
      table.insert(out, car)
    else
      local ratio = 0
      if visibles > 1 then ratio = rang / (visibles - 1) end
      local couleur = melanger_hex(couleurs[1], couleurs[2], ratio)
      table.insert(out, '[color=' .. couleur .. ']' .. car .. '[color]')
      rang = rang + 1
    end
  end
  return table.concat(out)
end

local function entree_maintenue(id)
  local ok, down = pcall(function() return GAME:IsInputDown(id) end)
  return ok and down == true
end

local function geste_etoile_maintenu()
  -- Le geste demandé au joueur est le maintien du clic droit. Confirm est
  -- seulement un secours discret pour les configurations sans souris.
  return entree_maintenue(INPUT_RIGHT_MOUSE) or entree_maintenue(INPUT_CONFIRM)
end

local function borner(valeur, minimum, maximum)
  if valeur < minimum then return minimum end
  if valeur > maximum then return maximum end
  return valeur
end

-- Position de la souris dans l'écran interne 320×240.
-- MouseLoc est exprimé en pixels de fenêtre : on retire le zoom de PMDO.
-- En cas d'échec, on renvoie le centre historique de l'étoile.
local function souris_ecran()
  local ok, x, y = pcall(function()
    local loc = _GAME.MetaInputManager.MouseLoc
    local zoom = RogueEssence.Content.GraphicsManager.WindowZoom
    if type(zoom) ~= "number" or zoom < 1 then zoom = 1 end
    return loc.X / zoom, loc.Y / zoom
  end)
  if ok and type(x) == "number" and type(y) == "number" then
    return borner(x, 8, 312), borner(y, 8, 232), true
  end
  return 160, 104, false
end

local function nature_par_slug(slug)
  for _, n in ipairs(quiz_data.natures) do
    if n.slug == slug then return n end
  end
  return nil
end

local function calculer_nature(scores, historique)
  local best_score = -1
  for _, n in ipairs(quiz_data.natures) do
    local s = scores[n.slug] or 0
    if s > best_score then best_score = s end
  end

  local candidats = {}
  for _, n in ipairs(quiz_data.natures) do
    if (scores[n.slug] or 0) == best_score then
      table.insert(candidats, n.slug)
    end
  end

  -- En cas d'égalité parfaite, ce sont les réponses les plus récentes qui
  -- départagent les natures encore à égalité (et non l'ordre de la liste).
  historique = historique or {}
  for idx = #historique, 1, -1 do
    if #candidats <= 1 then break end
    local points = historique[idx] or {}
    local meilleur_local = -1
    for _, slug in ipairs(candidats) do
      local s = points[slug] or 0
      if s > meilleur_local then meilleur_local = s end
    end
    local retenus = {}
    for _, slug in ipairs(candidats) do
      if (points[slug] or 0) == meilleur_local then
        table.insert(retenus, slug)
      end
    end
    candidats = retenus
  end

  return candidats[1]
end

-- Animation principale de la révélation.
--
-- ScriptableMenu est un InteractableMenu de RogueEssence dont le callback
-- Lua est appelé à chaque frame. Ce callback ne doit jamais attendre : il
-- déplace seulement les MenuDirTex, choisit les poses du halo/de l'étoile,
-- lit les entrées courantes, puis ferme le menu quand la scène est terminée.
-- Le script principal reprend ensuite après UI:WaitForChoice().
--
-- Le menu hôte est placé entièrement hors écran. L'overlay plein écran est
-- volontairement débordant (-16 en x/y) afin qu'un sprite centré ou presque
-- sur le point de la souris ne soit pas coupé par la zone du menu.
local function former_etoile_fluide(starter, options)
  options = options or {}
  -- Phase « incolore » : l'étoile est déjà formée avec les assets « Normal »
  -- (blancs, sans couleur) ; un clic du joueur la referme et déclenche ensuite
  -- l'animation de couleur (phase « auto », au point cliqué).
  local type_slug = starter.etoile_type or 'Normal'
  if options.incolore then type_slug = 'Normal' end
  local etat = {
    progression = options.incolore and 1 or 0,
    temps = 0,
    frames = 0,
    final_frames = 0,
    ancre_x = 160,
    ancre_y = 104,
    ancre_prete = false,
    clic_droit_precedent = false,
    clic_arme = false,
    confirmer_precedent = false,
    confirmer_arme = false,
    phase_incolore = options.incolore == true,
    auto_couleur = options.auto == true,
    entree_vue = false,
    mode_secours = false,
    son_materisation = false,
    ferme = false,
    termine = false,
    erreur = false,
    pose_halo = -1,
    pose_etoile = -1,
    ondes_anim = nil,
    ondes_element = nil,
    halo_anim = nil,
    halo_element = nil,
    etoile_anim = nil,
    etoile_element = nil,
  }

  -- Particules déterministes : chaque type garde la même constellation
  -- d'une session à l'autre, sans dépendre du hasard global du jeu.
  local base_hasard = 17.31
  for i = 1, #type_slug do
    base_hasard = base_hasard + string.byte(type_slug, i) * 0.731
  end
  local function hasard(n)
    local v = math.sin(base_hasard + n * 12.9898) * 43758.5453
    return v - math.floor(v)
  end

  local particules = {}
  for i = 1, FLUIDE_PARTICULES do
    particules[i] = {
      angle = hasard(i * 7 + 1) * math.pi * 2,
      rayon = 82 + hasard(i * 7 + 2) * 82,
      depart = hasard(i * 7 + 3) * 0.12,
      arrivee = 0.48 + hasard(i * 7 + 4) * 0.20, -- toutes arrivent avant 0,70
      rotation = 0.45 + hasard(i * 7 + 5) * 1.35,
      orbite = 0.22 + hasard(i * 7 + 6) * 0.38,
      anneau = 50 + hasard(i * 7 + 7) * 34,
      phase = (i - 1) % 16,
      element = nil,
    }
  end

  local fermer
  fermer = function()
    if etat.ferme then return end
    etat.ferme = true
    local ok = pcall(function() _MENU:RemoveMenu() end)
    if not ok then etat.erreur = true end
  end

  -- Les coordonnées d'un MenuDirTex sont relatives au SummaryMenu, lui-même
  -- dessiné depuis (-16, -16). On ajoute donc 16 pour obtenir un sprite
  -- centré sur les coordonnées écran réelles demandées.
  local function placer_elements()
    if etat.ondes_element == nil or etat.halo_element == nil or etat.etoile_element == nil then return end
    local cx, cy = etat.ancre_x, etat.ancre_y
    etat.ondes_element.Loc = RogueElements.Loc(
      math.floor(cx - FLUIDE_ONDES_TAILLE / 2 + 16 + 0.5),
      math.floor(cy - FLUIDE_ONDES_TAILLE / 2 + 16 + 0.5))
    etat.halo_element.Loc = RogueElements.Loc(
      math.floor(cx - FLUIDE_HALO_TAILLE / 2 + 16 + 0.5),
      math.floor(cy - FLUIDE_HALO_TAILLE / 2 + 16 + 0.5))
    etat.etoile_element.Loc = RogueElements.Loc(
      math.floor(cx - FLUIDE_ETOILE_L / 2 + 16 + 0.5),
      math.floor(cy - FLUIDE_ETOILE_H / 2 + 16 + 0.5))

    -- Halo : une pose par frame de progression, avec une légère pulsation
    -- une fois l'étoile complètement formée.
    local halo_t
    if etat.final_frames > 0 then
      halo_t = 0.82 + 0.12 * math.sin(etat.final_frames * 0.16)
    else
      halo_t = 0.08 + 0.92 * etat.progression
    end
    local pose_halo = borner(math.floor(halo_t * (FLUIDE_HALO_POSES - 1) + 0.5),
      0, FLUIDE_HALO_POSES - 1)
    if pose_halo ~= etat.pose_halo then
      etat.halo_anim.StartFrame = pose_halo
      etat.halo_anim.EndFrame = pose_halo
      etat.pose_halo = pose_halo
    end

    -- Étoile : invisible tant que la convergence n'est pas terminée.
    -- Les poses 1 à 56 la matérialisent ; les poses 57 à 72 forment ensuite
    -- une courte boucle de scintillement pendant le maintien final.
    local pose_etoile = 0
    if etat.final_frames > 0 then
      local poses_finales = FLUIDE_ETOILE_POSES - FLUIDE_ETOILE_MATERISATION_FIN - 1
      pose_etoile = FLUIDE_ETOILE_MATERISATION_FIN + 1 +
        (math.floor(etat.final_frames / 3) % poses_finales)
    elseif etat.progression > FLUIDE_CONVERGENCE then
      local t = (etat.progression - FLUIDE_CONVERGENCE) / (1 - FLUIDE_CONVERGENCE)
      pose_etoile = 1 + math.floor(t * (FLUIDE_ETOILE_MATERISATION_FIN - 1) + 0.5)
    end
    if pose_etoile ~= etat.pose_etoile then
      etat.etoile_anim.StartFrame = pose_etoile
      etat.etoile_anim.EndFrame = pose_etoile
      etat.pose_etoile = pose_etoile
    end

    for _, p in ipairs(particules) do
      if p.element ~= nil then
        local locale = 0
        if etat.progression > p.depart then
          locale = math.min(1, (etat.progression - p.depart) / (p.arrivee - p.depart))
        end
        -- Smoothstep : les particules restent réparties au début, puis
        -- accélèrent et ralentissent juste avant le point de convergence.
        local ease = locale * locale * (3 - 2 * locale)
        local rayon = p.rayon * (1 - ease)
        local angle = p.angle + p.rotation * ease + etat.temps * p.orbite * (1 - ease)

        if etat.final_frames > 0 then
          -- Après la formation, les étincelles ressortent en douceur et
          -- tournent en anneau autour de l'étoile au lieu de disparaître.
          local ft = math.min(1, etat.final_frames / 50)
          local fe = 1 - (1 - ft) ^ 3
          rayon = p.anneau * fe
          angle = p.angle + p.rotation + etat.final_frames * 0.012 * (0.6 + p.orbite)
        end

        local px = cx + math.cos(angle) * rayon
        local py = cy + math.sin(angle) * rayon * 0.76
        p.element.Loc = RogueElements.Loc(
          math.floor(px - FLUIDE_PARTICULE_TAILLE / 2 + 16 + 0.5),
          math.floor(py - FLUIDE_PARTICULE_TAILLE / 2 + 16 + 0.5))
      end
    end
  end

  local function maj_interne()
    if etat.ferme then return end

    etat.frames = etat.frames + 1
    etat.temps = etat.temps + (1 / 60)

    local mx, my, souris_ok = souris_ecran()
    local clic_droit = entree_maintenue(INPUT_RIGHT_MOUSE)
    local confirmer_brut = entree_maintenue(INPUT_CONFIRM)
    -- Confirm ne sert qu'en secours : on exige de le voir relâché une fois
    -- après la voice-over pour ne pas compter la pression qui l'a fermée.
    if not confirmer_brut then etat.confirmer_arme = true end
    if not clic_droit then etat.clic_arme = true end
    local confirmer = confirmer_brut and etat.confirmer_arme

    if clic_droit or confirmer then etat.entree_vue = true end
    if etat.frames >= 2700 and not etat.entree_vue then etat.mode_secours = true end
    local maintenu = clic_droit or confirmer or etat.mode_secours or etat.auto_couleur

    -- Phase incolore : l'étoile blanche attend le clic du joueur (appui franc,
    -- entrées préalablement relâchées) pour laisser jaillir sa couleur.
    if etat.phase_incolore then
      local appui_clic = clic_droit and not etat.clic_droit_precedent and etat.clic_arme
      local appui_conf = confirmer and not etat.confirmer_precedent
      if appui_clic or appui_conf or etat.mode_secours then
        etat.termine = true
        placer_elements()
        fermer()
        return
      end
    end
    etat.confirmer_precedent = confirmer

    if etat.auto_couleur then
      -- Phase couleur : l'ancre reste le point du clic qui l'a déclenchée.
      if not etat.ancre_prete then
        etat.ancre_x, etat.ancre_y = options.ancre_x or mx, options.ancre_y or my
        etat.ancre_prete = true
      end
    -- Le point où le clic droit commence devient immédiatement l'ancre.
    -- Pendant le maintien, les particules suivent ensuite la souris avec un
    -- léger amortissement pour éviter tout tremblement.
    if not etat.ancre_prete then
      etat.ancre_x, etat.ancre_y = mx, my
      etat.ancre_prete = true
    elseif clic_droit and not etat.clic_droit_precedent and souris_ok then
      etat.ancre_x, etat.ancre_y = mx, my
    else
      local cible_x, cible_y = etat.ancre_x, etat.ancre_y
      if not etat.auto_couleur and (clic_droit or (souris_ok and not confirmer_brut)) then
        cible_x, cible_y = mx, my
      end
      if etat.mode_secours and not clic_droit then
        cible_x, cible_y = 160, 104
      end
      local suivi = maintenu and 0.20 or 0.38
      etat.ancre_x = etat.ancre_x + (cible_x - etat.ancre_x) * suivi
      etat.ancre_y = etat.ancre_y + (cible_y - etat.ancre_y) * suivi
    end
    end
    etat.clic_droit_precedent = clic_droit

    if etat.progression >= 1 then
      etat.final_frames = etat.final_frames + 1
      if etat.final_frames >= 55 and not etat.phase_incolore then
        etat.termine = true
        placer_elements()
        fermer()
        return
      end
    elseif maintenu then
      local avant = etat.progression
      etat.progression = math.min(1, etat.progression + (1 / FLUIDE_FRAMES))
      if not etat.son_materisation and avant < FLUIDE_CONVERGENCE and etat.progression >= FLUIDE_CONVERGENCE then
        etat.son_materisation = true
        pcall(function() SOUND:PlaySE('Menu/Skip') end)
      end
    else
      -- Relâcher fait repartir les particules en arrière sans saut, et
      -- l'étoile repasse ses poses de matérialisation dans l'autre sens.
      etat.progression = math.max(0, etat.progression - (0.35 / FLUIDE_FRAMES))
      if etat.progression < FLUIDE_CONVERGENCE - 0.08 then
        etat.son_materisation = false
      end
    end

    placer_elements()
  end

  -- Toute erreur NLua dans le callback ferme proprement ce menu ; le
  -- secours temporisé ci-dessous ne remplace jamais le fond de la carte.
  local function maj_menu(_input)
    local ok = pcall(maj_interne)
    if not ok then
      etat.erreur = true
      fermer()
    end
  end

  local ok_construction, hote = pcall(function()
    local menu = RogueEssence.Menu.ScriptableMenu('DESTINY_QUIZ_ETOILE', 400, 400, 16, 16, maj_menu)
    local overlay = RogueEssence.Menu.SummaryMenu('DESTINY_QUIZ_ETOILE_OVERLAY',
      RogueElements.Rect.FromPoints(RogueElements.Loc(-16, -16), RogueElements.Loc(336, 256)))

    local tex = RogueEssence.Menu.MenuDirTex.TexType
    local type_objet = tex.Object or tex.OBJ
    local type_particule = tex.Particle

    -- Les ondes sont le calque le plus profond : leur AnimData boucle seul
    -- pendant que le callback déplace l'ensemble autour du point choisi.
    etat.ondes_anim = RogueEssence.Content.AnimData('Quiz_Etoile_Ondes_' .. type_slug, 2)
    etat.ondes_anim.StartFrame = 0
    etat.ondes_anim.EndFrame = FLUIDE_ONDES_POSES - 1
    etat.ondes_element = RogueEssence.Menu.MenuDirTex('DESTINY_QUIZ_ONDES',
      RogueElements.Loc(64, 24), 0, type_objet, etat.ondes_anim)
    overlay.Elements:Add(etat.ondes_element)

    etat.halo_anim = RogueEssence.Content.AnimData('Quiz_Etoile_Halo_' .. type_slug, 999)
    etat.halo_anim.StartFrame = 0
    etat.halo_anim.EndFrame = 0
    etat.halo_element = RogueEssence.Menu.MenuDirTex('DESTINY_QUIZ_HALO',
      RogueElements.Loc(96, 40), 0, type_objet, etat.halo_anim)
    overlay.Elements:Add(etat.halo_element)

    local particule_index = 'Quiz_Etoile_Particule_' .. type_slug
    for i, p in ipairs(particules) do
      local anim = RogueEssence.Content.AnimData(particule_index, 3 + (i % 3))
      anim.StartFrame = p.phase
      anim.EndFrame = p.phase + 7
      p.element = RogueEssence.Menu.MenuDirTex('DESTINY_QUIZ_PARTICULE_' .. i,
        RogueElements.Loc(16, 16), 0, type_particule, anim)
      overlay.Elements:Add(p.element)
    end

    etat.etoile_anim = RogueEssence.Content.AnimData('Quiz_Etoile_Forme_' .. type_slug, 999)
    etat.etoile_anim.StartFrame = 0
    etat.etoile_anim.EndFrame = 0
    etat.etoile_element = RogueEssence.Menu.MenuDirTex('DESTINY_QUIZ_ETOILE',
      RogueElements.Loc(96, 28), 0, type_objet, etat.etoile_anim)
    overlay.Elements:Add(etat.etoile_element)

    -- LowerSummaryMenus est l'emplacement déjà utilisé par le service du
    -- titre Destiny pour ses overlays plein écran.
    menu.LowerSummaryMenus:Insert(0, overlay)
    return menu
  end)

  if not ok_construction or hote == nil then return false end

  etat.ancre_x, etat.ancre_y = souris_ecran()
  if options.ancre_x ~= nil and options.ancre_y ~= nil then
    etat.ancre_x, etat.ancre_y = options.ancre_x, options.ancre_y
  end
  etat.ancre_prete = true
  local ok_premier_placement = pcall(placer_elements)
  if not ok_premier_placement then return false end

  -- Aucun fond de substitution et aucune consigne en surimpression : les
  -- quatre calques du VFX se dessinent directement sur Dream_Back et
  -- Dream_Front, déjà animés par la carte personality_test.
  local ok_menu = pcall(function() UI:SetCustomMenu(hote) end)
  if not ok_menu then return false end
  UI:WaitForChoice()

  return etat.termine and not etat.erreur, etat.ancre_x, etat.ancre_y
end

-- Révélation interactive : les particules convergent vers le point du clic
-- droit puis l'étoile se matérialise au même endroit. Aucun pourcentage
-- n'est affiché : seule la lumière raconte la progression.
local function reveler_starter(nature, starter)
  UI:ResetSpeaker()
  UI:WaitShowVoiceOver("L'analyse est terminée...", -1)
  UI:WaitShowVoiceOver("Une étoile sans couleur s'est déjà formée au-dessus de toi...\nElle attend la teinte de ton aura.", -1)
  UI:WaitShowVoiceOver("Quand tu seras prêt, [color=#FFE16A]clique[color] (clic droit) :\nla couleur de ton étoile jaillira.", -1)

  -- Phase 1 : l'étoile est déjà visible, blanche et scintillante (assets
  -- « Normal »). Le clic du joueur referme cette attente et déclenche la
  -- phase 2 : la même animation, mais colorée selon le type du starter et
  -- jouée automatiquement au point cliqué.
  local ok_incolore, ancre_x, ancre_y = former_etoile_fluide(starter, { incolore = true })
  if not ok_incolore then ancre_x, ancre_y = nil, nil end

  -- Chemin normal : animation continue au point du clic droit, directement
  -- sur le fond de la carte. Le secours ci-dessous ne sert que si le menu
  -- scriptable ou l'un de ses sprites ne peut pas être construit ; même
  -- dans ce cas, aucun fond n'est remplacé et rien n'est écrit en bas.
  if not former_etoile_fluide(starter, { auto = true, ancre_x = ancre_x, ancre_y = ancre_y }) then
    -- Évite qu'une pression déjà maintenue pour fermer la boîte de dialogue
    -- soit comptée comme le début du geste (attente bornée à deux secondes).
    local attente_relachement = 0
    while geste_etoile_maintenu() and attente_relachement < 120 do
      GAME:WaitFrames(1)
      attente_relachement = attente_relachement + 1
    end

    local charge = 0
    local seuil_sonore = 0
    local frames_total = 0
    local entree_vue = false
    local mode_secours = false

    while charge < CHARGE_MAX do
      local maintenu = geste_etoile_maintenu()
      if maintenu then entree_vue = true end

      if mode_secours or maintenu then
        charge = math.min(CHARGE_MAX, charge + 1)
      else
        charge = math.max(0, charge - 0.35)
      end

      frames_total = frames_total + 1
      -- Dernier anti-blocage : si aucune entrée n'a jamais été détectée
      -- (configuration ou rejeu sans souris), la scène finit seule.
      if frames_total >= 2700 and not entree_vue then
        mode_secours = true
      end

      local nouveau_seuil = math.floor((charge / CHARGE_MAX) * 5)
      if nouveau_seuil > seuil_sonore then
        seuil_sonore = nouveau_seuil
        if seuil_sonore < 5 then SOUND:PlaySE('Menu/Skip') end
      elseif nouveau_seuil < seuil_sonore then
        seuil_sonore = nouveau_seuil
      end
      GAME:WaitFrames(1)
    end
  end
  SOUND:PlayBattleSE('EVT_Battle_Flash')
  GAME:FadeOut(true, 8)
  GAME:FadeIn(24)
  GAME:WaitFrames(35)

  -- Le fond Dream de la carte n'a jamais été remplacé : il reste donc tel
  -- quel derrière le portrait natif du starter. Le nom vide évite le
  -- préfixe « Nom : » ; la phrase porte le nom coloré selon le type.
  UI:SetSpeaker('', false, starter.espece, starter.forme, 'normal', Gender.Genderless)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Quelqu’un comme toi serait ' .. nom_colore_type(starter) .. ' !')
  UI:ResetSpeaker()

  UI:WaitShowVoiceOver('Nature [color=' .. nature.hex .. ']' .. nature.fr .. '[color].\n' ..
    (nature.description or ''), -1)
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

-- Le menu de sélection natif PMDO utilise le même portrait bordé que le
-- sélecteur du projet de référence. Les libellés propres à Destiny gardent la
-- distinction entre formes et le replay continue d'enregistrer un indice.
local function choisir_dans_pool(pool, titre)
  local labels = {}
  for _, s in ipairs(pool) do table.insert(labels, s.nom) end

  if _DATA.CurrentReplay ~= nil then
    UI:BeginMultiPageMenu(16, 16, 112, titre, labels, 12, 1, -1)
    UI:WaitForChoice()
    return pool[UI:ChoiceResult()]
  end

  local ListType = luanet.import_type('System.Collections.Generic.List`1')
  local StartChar = luanet.import_type('RogueEssence.Data.StartChar')
  local choix = LUA_ENGINE:MakeGenericType(ListType, { StartChar }, {})
  for _, s in ipairs(pool) do
    local id = RogueEssence.Dungeon.MonsterID(s.espece, s.forme, 'normal', Gender.Genderless)
    choix:Add(StartChar(id, s.nom))
  end
  local function selection(index)
    local code = index + 1
    _DATA:LogUIPlay(code)
    UI:GetChoiceAction(code):Invoke()
  end
  local menu = RogueEssence.Menu.ChooseMonsterMenu(titre, choix, 0, selection, nil, false, 12)
  UI:SetCustomMenu(menu)
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

  -- 20 questions — chaque choix distribue +4/+2 sur les 16 natures.
  -- Aucun compteur n'est affiché : seules les situations comptent.
  local scores = {}
  local historique_reponses = {}
  for _, n in ipairs(quiz_data.natures) do scores[n.slug] = 0 end

  for _, q in ipairs(quiz_data.questions) do
    local intitules = {}
    for _, c in ipairs(q.choix) do table.insert(intitules, c.texte) end
    UI:BeginChoiceMenu(q.texte, intitules, 1, 1)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    local points_choisis = q.choix[choix].points
    table.insert(historique_reponses, points_choisis)
    for slug, pts in pairs(points_choisis) do
      scores[slug] = (scores[slug] or 0) + pts
    end
  end

  -- nature = score maximal, départagée par les réponses récentes.
  local slug = calculer_nature(scores, historique_reponses)
  local nature = nature_par_slug(slug)
  local starter_id = quiz_data.mapping[slug]
  local starter = quiz_data.starters[starter_id]

  reveler_starter(nature, starter)

  UI:ChoiceMenuYesNo("Veux-tu garder ce résultat ?\nSinon, choisis librement ton Pokémon.", true)
  UI:WaitForChoice()
  local pool_heros = construire_pool(nil)
  if not UI:ChoiceResult() then
    starter = choisir_dans_pool(pool_heros, "Ton héros")
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
    if not ok then starter = choisir_dans_pool(pool_heros, "Ton héros") end
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
    partenaire = choisir_dans_pool(pool_partenaire, "Partenaire")
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
  -- Avant de rejoindre le partenaire, la faille dépose le héros, déjà
  -- endormi, au marqueur reveil de la prairie ZRV2. Son monologue intérieur
  -- se joue sur fond noir, puis le fondu se lève brièvement sur lui avant
  -- de basculer vers la maison du partenaire.
  -- La musique du questionnaire s'éteint avant la première voix de la
  -- cinématique. Elle ne reprendra pas sur les cartes nocturnes.
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PrologueHeros = 'a_voir'
  SOUND:FadeOutBGM(60)
  GAME:WaitFrames(60)
  UI:WaitShowVoiceOver("Une faille s'ouvre dans le rêve...", -1)
  GAME:FadeOut(false, 120)
  GAME:WaitFrames(60)
  GAME:CutsceneMode(false)
  GAME:EnterGroundMap('reverie', 'zrv2_zone_reveil_nuit', 'reveil')
end

return personality_test
