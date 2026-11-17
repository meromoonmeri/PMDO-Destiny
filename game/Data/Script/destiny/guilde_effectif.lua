--[[
  guilde_effectif.lua — Effectif de la Guilde de Réverie Town (10 membres),
  emote de repas « eating » et pose de service de Mélofée.

  Les noms d'acteurs (`id`) sont les identifiants sans accent à donner aux
  personnages dans les cartes de la Guilde : `CH('Gardevoir')`, `CH('Melofee')`…
  `nom` garde l'orthographe affichée (Mélofée, Pandespiègle).

  Emote de repas — calquée sur Halcyon
  -------------------------------------
  `game/Data/Emote/eating.json`  -> AnimIndex `Emote_Eating`, FrameTime 3,
  LocHeight 10, AnimDir 0 (vers le bas).
  `game/Content/Particle/Emote_Eating.dir` -> 6 images de 32x32 (miettes qui
  montent vers la bouche). Halcyon s'en sert en boucle dans sa salle à manger :
  `GROUND:CharSetEmote(chara, "eating", 0)` — 0 = cycle infini — et coupe avec
  un identifiant vide : `GROUND:CharSetEmote(chara, "", 0)`.
  L'émote dure 6 x 3 = 18 images par bouchée.

  Pose spéciale de Mélofée — calquée sur Audino dans Halcyon
  ----------------------------------------------------------
  Halcyon fige ses PNJ de guilde en pose avec
  `GROUND:CharSetAction(chara, RogueEssence.Ground.PoseGroundAction(
      chara.Position, chara.Direction,
      RogueEssence.Content.GraphicsManager.GetAnimIndex("Pose")))`
  (cf. guild_third_floor_lobby, guild_dining_room). `guilde_effectif.Poser`
  reprend exactement ce mécanisme pour l'infirmière de garde.
]]

local guilde_effectif = {}

guilde_effectif.EMOTE_REPAS = 'eating'
-- Pose de service de Mélofée : calot posé sur la tête (LocHeight 6), créé pour
-- imiter la pose spéciale d'Audino dans Halcyon.
guilde_effectif.EMOTE_POSE = 'pose_infirmiere'
-- Cloche de réveil, jouée par l'infirmière à la tournée du matin.
guilde_effectif.EMOTE_REVEIL = 'reveil'
-- 18 images par bouchée (6 images x FrameTime 3), valeur utile pour caler
-- les pauses d'une scène de repas sur l'animation réelle.
guilde_effectif.IMAGES_PAR_BOUCHEE = 18

--[[
  cycles : nombre de bouchées (0 = repas continu, comme Halcyon)
  delai  : désynchronisation au démarrage, en images (0 = premier servi)
  apres  : émote facultative une fois la dernière bouchée terminée
  pose   : le membre garde une pose figée de service hors repas
]]
guilde_effectif.MEMBRES = {
  {
    id = 'Gardevoir', nom = 'Gardevoir', espece = 'gardevoir',
    role = 'Maîtresse de guilde', bloc = 'direction', genre = 'f',
    type = 'Psy / Fée',
    caractere = 'Paisible, professionnelle, élégante et diplomate',
    cycles = 0, delai = 14, apres = nil, pose = false,
  },
  {
    id = 'Canarticho', nom = 'Canarticho', espece = 'farfetchd',
    role = 'Second', bloc = 'direction', genre = 'm',
    type = 'Normal / Vol',
    caractere = 'Sérieux, méthodique, exigeant et médiateur',
    cycles = 0, delai = 6, apres = nil, pose = false,
  },
  {
    id = 'Simisage', nom = 'Simisage', espece = 'simisage',
    role = 'Cuisinier', bloc = 'vie_quotidienne', genre = 'm',
    type = 'Plante',
    caractere = 'Extraverti, enthousiaste et passionné par sa cuisine',
    cycles = 2, delai = 22, apres = 'happy', pose = false,
  },
  {
    id = 'Melofee', nom = 'Mélofée', espece = 'clefairy',
    role = 'Infirmière et responsable du réveil', bloc = 'vie_quotidienne', genre = 'f',
    type = 'Fée',
    caractere = 'Douce, attentionnée, organisée et enthousiaste',
    cycles = 0, delai = 10, apres = 'happy', pose = true,
  },
  {
    id = 'Cizayox', nom = 'Cizayox', espece = 'scizor',
    role = 'Combattant', bloc = 'explorateurs', genre = 'm',
    type = 'Insecte / Acier',
    caractere = 'Discipliné, stoïque et perfectionniste',
    cycles = 1, delai = 8, apres = nil, pose = false,
  },
  {
    id = 'Noctali', nom = 'Noctali', espece = 'umbreon',
    role = 'Explorateur', bloc = 'explorateurs', genre = 'm',
    type = 'Ténèbres',
    caractere = 'Réservé, calme, prudent et observateur',
    cycles = 1, delai = 18, apres = nil, pose = false,
  },
  {
    id = 'Dimoret', nom = 'Dimoret', espece = 'weavile',
    role = 'Éclaireuse', bloc = 'explorateurs', genre = 'f',
    type = 'Ténèbres / Glace',
    caractere = 'Sarcastique, rusée, indépendante et compétitive (loyale envers ses compagnons)',
    cycles = 2, delai = 4, apres = 'notice', pose = false,
  },
  {
    id = 'Draby', nom = 'Draby', espece = 'bagon',
    role = 'Jeune recrue (leader de la Team Star)', bloc = 'recrues', genre = 'm',
    type = 'Dragon',
    caractere = 'Rêveur, déterminé et impulsif',
    cycles = 3, delai = 2, apres = 'glowing', pose = false,
  },
  {
    id = 'Pandespiegle', nom = 'Pandespiègle', espece = 'pancham',
    role = 'Jeune recrue', bloc = 'recrues', genre = 'm',
    type = 'Combat',
    caractere = 'Provocateur, fier et turbulent, mais sensible au fond',
    cycles = 2, delai = 5, apres = 'notice', pose = false,
  },
  {
    id = 'Capumain', nom = 'Capumain', espece = 'aipom',
    role = 'Recrue', bloc = 'recrues', genre = 'f',
    type = 'Normal',
    caractere = 'Espiègle, curieux et malicieux',
    cycles = 2, delai = 12, apres = 'happy', pose = false,
  },
}

-- Ordre d'apparition dans les cartes (direction, vie quotidienne, explorateurs, recrues).
guilde_effectif.ORDRE = {
  'Gardevoir', 'Canarticho', 'Simisage', 'Melofee',
  'Cizayox', 'Noctali', 'Dimoret',
  'Draby', 'Pandespiegle', 'Capumain',
}

guilde_effectif.BLOCS = {
  direction = { 'Gardevoir', 'Canarticho' },
  vie_quotidienne = { 'Simisage', 'Melofee' },
  explorateurs = { 'Cizayox', 'Noctali', 'Dimoret' },
  recrues = { 'Draby', 'Pandespiegle', 'Capumain' },
}

-- Les trois jeunes recrues forment la Team Star.
guilde_effectif.TEAM_STAR = { 'Draby', 'Pandespiegle', 'Capumain' }

local function minuscule(texte)
  if texte == nil then return '' end
  return tostring(texte):lower()
end

-- Accepte un identifiant, une espèce ou une entrée de MEMBRES.
function guilde_effectif.Membre(reference)
  if type(reference) == 'table' then
    if reference.cycles ~= nil or reference.espece ~= nil then return reference end
    return nil
  end
  local cible = minuscule(reference)
  if cible == '' then return nil end
  for _, membre in ipairs(guilde_effectif.MEMBRES) do
    if minuscule(membre.id) == cible or minuscule(membre.espece) == cible
        or minuscule(membre.nom) == cible then
      return membre
    end
  end
  return nil
end

function guilde_effectif.ParBloc(bloc)
  local sortie = {}
  for _, id in ipairs(guilde_effectif.BLOCS[bloc] or {}) do
    local membre = guilde_effectif.Membre(id)
    if membre ~= nil then table.insert(sortie, membre) end
  end
  return sortie
end

-- Genre du membre dans l'énumération du moteur (repli sans erreur).
function guilde_effectif.Genre(reference)
  local membre = guilde_effectif.Membre(reference)
  local code = membre ~= nil and membre.genre or 'm'
  local ok, valeur = pcall(function()
    if code == 'f' then return Gender.Female end
    return Gender.Male
  end)
  if ok then return valeur end
  return nil
end

--[[
  Les acteurs réellement présents sur la carte courante.
  `liste` : nil (tout l'effectif), liste d'identifiants, ou liste d'acteurs.
]]
function guilde_effectif.Acteurs(liste)
  local cibles = liste or guilde_effectif.ORDRE
  local presents = {}
  for _, reference in ipairs(cibles) do
    local acteur = nil
    local membre = nil
    if type(reference) == 'table' and reference.EntName ~= nil then
      acteur = reference
      membre = guilde_effectif.Membre(reference.EntName)
    else
      membre = guilde_effectif.Membre(reference)
      if membre ~= nil and CH ~= nil then
        acteur = CH(membre.id) or CH(membre.espece)
      end
    end
    if acteur ~= nil and membre ~= nil then
      table.insert(presents, {membre = membre, acteur = acteur})
    end
  end
  return presents
end

-- Vérifie qu'une planche de personnage possède vraiment l'animation demandée :
-- GetAnimIndex rend -1 (ou la feuille ne référence pas l'index) pour les
-- espèces dépourvues de l'animation, et dessiner dessus viderait le sprite.
local function animation_disponible(acteur, nom)
  if acteur == nil or nom == nil then return false end
  local dispo = false
  pcall(function()
    local gm = RogueEssence.Content.GraphicsManager
    local index = gm.GetAnimIndex(nom)
    if index ~= nil and index >= 0 then
      local feuille = gm.GetChara(acteur.CurrentForm:ToCharID())
      if feuille ~= nil and feuille:GetReferencedAnimIndex(index) == index then
        dispo = true
      end
    end
  end)
  return dispo
end

-- Joue une animation de la planche de l'espèce si elle existe réellement.
-- Renvoie true quand l'animation a été lancée, false quand il faut se rabattre
-- sur une émote ou sur l'attente (cas de la plupart des espèces).
function guilde_effectif.Animer(acteur, nom, boucle)
  if not animation_disponible(acteur, nom) then return false end
  return (pcall(function() GROUND:CharSetAnim(acteur, nom, boucle ~= false) end))
end

-- Pose figée de service : mécanisme exact de la pose d'Audino dans Halcyon.
function guilde_effectif.Poser(acteur, avec_calot)
  if acteur == nil then return false end
  if avec_calot == nil then avec_calot = true end
  local pose_faite = false
  pcall(function()
    local gm = RogueEssence.Content.GraphicsManager
    local index = gm.GetAnimIndex('Pose')
    if index ~= nil and index >= 0 then
      GROUND:CharSetAction(acteur, RogueEssence.Ground.PoseGroundAction(
        acteur.Position, acteur.Direction, index))
      pose_faite = true
    end
  end)
  if not pose_faite then
    pose_faite = guilde_effectif.Animer(acteur, 'Pose', true)
  end
  if not pose_faite then
    -- Dernier repli : l'attente neutre, pour ne jamais laisser le PNJ figé sur
    -- une image vide.
    pcall(function() GROUND:CharSetAnim(acteur, 'Idle', true) end)
  end
  -- Le calot est une émote : une seule émote à la fois par personnage, c'est
  -- pourquoi la cloche de réveil doit d'abord céder la place (cf. guilde_reveil).
  if avec_calot then
    pcall(function() GROUND:CharSetEmote(acteur, guilde_effectif.EMOTE_POSE, 0) end)
  end
  return pose_faite
end

function guilde_effectif.Deposer(acteur)
  if acteur == nil then return false end
  -- Le calot doit disparaître avec la pose, sinon il resterait flotter seul.
  pcall(function() GROUND:CharSetEmote(acteur, '', 0) end)
  return (pcall(function() GROUND:CharEndAnim(acteur) end))
end

-- Pose réservée aux membres marqués `pose = true` (aujourd'hui Mélofée).
function guilde_effectif.PoseDeService(acteur, reference)
  local membre = guilde_effectif.Membre(reference or (acteur ~= nil and acteur.EntName or nil))
  if membre == nil or membre.pose ~= true then return false end
  return guilde_effectif.Poser(acteur)
end

--[[
  Une bouchée (ou un repas continu si les cycles du membre valent 0).
  `cycles` force la valeur ; sinon celle du membre est utilisée.
]]
function guilde_effectif.Manger(acteur, reference, cycles)
  if acteur == nil then return false end
  local membre = guilde_effectif.Membre(reference or acteur.EntName)
  local bouchees = cycles
  if bouchees == nil then
    bouchees = (membre ~= nil and membre.cycles) or 0
  end
  local ok = pcall(function()
    GROUND:CharSetEmote(acteur, guilde_effectif.EMOTE_REPAS, bouchees)
  end)
  if not ok then return false end
  -- Le corps mâche aussi quand la planche de l'espèce a l'animation « Eat »
  -- (sinon le personnage garde simplement son attente).
  guilde_effectif.Animer(acteur, 'Eat', true)
  return true
end

-- Émote unique, un cycle, sans animation de corps (réplique de PNJ au comptoir).
function guilde_effectif.Bouchee(acteur, reference)
  return guilde_effectif.Manger(acteur, reference, 1)
end

--[[
  Repas de la Guilde : chaque membre présent démarre son émote après son
  propre délai (désynchronisation 2..22 images), puis tout le monde repose son
  émote et retrouve sa pose de service si elle lui appartient.
  `duree` : images de repas avant de couper (0 = ne pas couper).
]]
function guilde_effectif.Repas(liste, duree)
  local presents = guilde_effectif.Acteurs(liste)
  if #presents == 0 then return 0 end
  local taches = {}
  for _, entree in ipairs(presents) do
    local membre, acteur = entree.membre, entree.acteur
    table.insert(taches, TASK:BranchCoroutine(function()
      local delai = membre.delai or 0
      if delai > 0 then GAME:WaitFrames(delai) end
      guilde_effectif.Manger(acteur, membre)
    end))
  end
  TASK:JoinCoroutines(taches)
  if duree == nil then duree = 120 end
  if duree > 0 then GAME:WaitFrames(duree) end
  if duree > 0 or liste == nil then
    guilde_effectif.FinRepas(presents)
  end
  return #presents
end

--[[
  Repas déjà en cours à l'ouverture de la salle : chaque membre présent démarre
  son émote en boucle, sans coroutine ni délai (`Enter`/`Init` d'une carte ne
  sont pas des coroutines). Halcyon fait exactement cela dans sa salle à manger.
]]
function guilde_effectif.RepasImmediat(liste)
  local presents = guilde_effectif.Acteurs(liste)
  for _, entree in ipairs(presents) do
    guilde_effectif.Manger(entree.acteur, entree.membre)
  end
  return #presents
end

-- Coupe l'émote de repas (identifiant vide = StartEmote(null) dans le moteur),
-- rend le corps au repos et rétablit la pose de service de Mélofée.
function guilde_effectif.FinRepas(liste)
  local presents = guilde_effectif.Acteurs(liste)
  for _, entree in ipairs(presents) do
    local acteur, membre = entree.acteur, entree.membre
    -- Une seule émote par personnage : on efface celle du repas, on rend le
    -- corps au repos, puis on laisse l'émote de sortie du membre.
    pcall(function() GROUND:CharSetEmote(acteur, '', 0) end)
    pcall(function() GROUND:CharEndAnim(acteur) end)
    if membre.apres ~= nil then
      pcall(function() GROUND:CharSetEmote(acteur, membre.apres, 1) end)
    end
    if membre.pose == true then
      -- Corps en pose de service, mais sans le calot : celui-ci signale la
      -- prise de garde (PoseDeService), pas la fin d'un repas.
      guilde_effectif.Poser(acteur, false)
    end
  end
  return #presents
end

-- Fiche lisible d'un membre (journaux, tableau des missions, tests).
function guilde_effectif.Fiche(reference)
  local membre = guilde_effectif.Membre(reference)
  if membre == nil then return nil end
  return string.format('%s — %s · %s · %s (%s) · %d bouchée(s), délai %d images',
    membre.nom, membre.role, membre.type,
    membre.genre == 'f' and 'Féminin' or 'Masculin',
    membre.caractere, membre.cycles, membre.delai)
end

return guilde_effectif
