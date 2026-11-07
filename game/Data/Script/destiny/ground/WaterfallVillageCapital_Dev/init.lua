-- Réverie Town : arrivée après les Bois Perdus et présentation des lieux existants.
-- La version town02 étendue contient ses habitants, objets et marqueurs ;
-- Kecleon et Kangourex sérialisés sont réutilisés, avec création en repli
-- uniquement si une ancienne sauvegarde/carte ne les fournit pas.
require 'origin.common'
require 'origin.menu.skill.SkillSelectMenu'
require 'origin.menu.team.AssemblySelectMenu'
local equipe_scene = require 'destiny.equipe_scene'
local cinematique = require 'destiny.cinematique'
local missions_reverie = require 'destiny.missions_reverie'

local ville = {}
local ENTREE_X, ENTREE_Y = 800, 1320
local PLACE_X, PLACE_Y = 800, 1160

-- Habitants sérialisés dans la carte town02 étendue.  Leurs positions
-- initiales sont relevées à l'Init afin que chacun déambule autour de son
-- propre quartier sans traverser toute la ville.
local habitants_vivants = {
  'Kecleon', 'Kecleon_Violet', 'NewObject_3', 'NewObject_4', 'Kangourex',
  'NewObject_6', 'NewObject_7', 'NewObject_8', 'NewObject_9', 'NewObject_10',
  'NewObject_12', 'NewObject_13', 'NewObject_14', 'Doyen', 'Drifloon',
  'NewObject_16', 'NewObject_11', 'NewObject_18', 'NewObject_20',
  'NewObject_21', 'NewObject_15', 'NewObject_17', 'NewObject_22',
  'NewObject_23', 'NewObject_24',
  'Pijako_Livreur', 'Cradopaud_Pecheur', 'Roserade_Fleuriste',
  'Magneton_Garde', 'Babimanta_Enfant', 'Goinfrex_Voyageur',
}
local positions_habitants = {}
local vie_ville_activee = false

-- Services extérieurs : ils restent à leur comptoir ou devant leur bâtiment,
-- sans IA de déambulation, donc dans leur idle par défaut.
local marchands_fixes = {
  Kecleon = true,          -- boutique verte
  Kecleon_Violet = true,   -- boutique violette
  Kangourex = true,        -- réserve d'objets
  NewObject_3 = true,      -- Mordudor, banque
  NewObject_4 = true,      -- Alakazam, souvenirs de capacités
  NewObject_24 = true,     -- Forgelina, ouverture des boîtes
}

-- Discussions réelles : dialogues partagés (Lombre/Ludicolo, Luxio/Luxray)
-- ou duo déjà placé côte à côte (Doyen/Baudrive). Les anciennes paires
-- d'ambiance séparées par plusieurs centaines de pixels ne font plus
-- semblant de discuter à travers la ville.
local paires_discussion = {
  {'NewObject_7', 'NewObject_8'},  -- Lombre et Ludicolo
  {'NewObject_10', 'NewObject_9'}, -- Luxio et Luxray
  {'Doyen', 'Drifloon'},           -- le Doyen et Baudrive
}
local partenaires_discussion = {}
for _, paire in ipairs(paires_discussion) do
  partenaires_discussion[paire[1]] = paire[2]
  partenaires_discussion[paire[2]] = paire[1]
end

local function est_fixe(nom)
  return marchands_fixes[nom] == true or partenaires_discussion[nom] ~= nil
end

local function tourner_vers(acteur, cible)
  if acteur == nil or cible == nil or acteur == cible then return end
  pcall(function() GROUND:CharTurnToChar(acteur, cible) end)
end

local function orienter_discussion(nom)
  local autre_nom = partenaires_discussion[nom]
  if autre_nom == nil then return end
  local acteur, autre = CH(nom), CH(autre_nom)
  tourner_vers(acteur, autre)
  tourner_vers(autre, acteur)
end

local function restaurer_orientation(nom, acteur)
  acteur = acteur or CH(nom)
  if nom == nil or acteur == nil then return end
  if partenaires_discussion[nom] ~= nil then
    orienter_discussion(nom)
    return
  end
  if marchands_fixes[nom] then
    local depart = positions_habitants[nom]
    if depart ~= nil and depart.dir ~= nil then
      pcall(function() GROUND:EntTurn(acteur, depart.dir) end)
    end
  end
end

local function figer_habitant(nom, acteur)
  acteur = acteur or CH(nom)
  if nom == nil or acteur == nil then return end
  pcall(function()
    AI:DisableCharacterAI(acteur)
    GROUND:CharEndAnim(acteur) -- idle par défaut, sans déplacement
  end)
  restaurer_orientation(nom, acteur)
end

-- Tout habitant abordé se tourne vers le joueur avant la première boîte.
-- Les marchands et les duos en discussion reprennent ensuite leur
-- orientation normale ; les promeneurs sont rendus à leur IA.
local function commencer_dialogue(personnage, activator)
  local joueur = CH('PLAYER') or activator
  tourner_vers(personnage, joueur)
  if personnage ~= nil then GROUND:CharSetAnim(personnage, 'Idle', true) end
end

local function terminer_dialogue(personnage, nom)
  if personnage ~= nil then GROUND:CharEndAnim(personnage) end
  restaurer_orientation(nom, personnage)
end

-- Jour de ville courant : la sieste au café Spinda fait passer au jour
-- suivant (même compteur que la rotation des étals Kecleon).
local function jour_actuel()
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.JourneeVille ~= nil then
    return SV.Destiny.JourneeVille
  end
  return 0
end

-- Choisit la variante de dialogue du jour parmi une liste de variantes.
local function repliques_du_jour(variantes)
  if variantes == nil or #variantes == 0 then return {} end
  return variantes[(jour_actuel() % #variantes) + 1]
end

-- La carte sérialise la plupart des habitants sous des noms d'entité
-- génériques (NewObject_*) : on leur donne leur vrai nom affiché en
-- dialogue, sans toucher à la carte.
local noms_habitants = {
  Kecleon = 'Basil', Kecleon_Violet = 'Félix',
  NewObject_3 = 'Écu', NewObject_4 = '', Kangourex = 'Mado',
  NewObject_6 = 'Céleste', NewObject_7 = 'Nino', NewObject_8 = 'Marcel',
  NewObject_9 = 'Lyra', NewObject_10 = 'Léo', NewObject_12 = 'Hector',
  NewObject_13 = 'Azur', NewObject_14 = '', Doyen = 'Aurèle',
  Drifloon = 'Plume', NewObject_16 = '', NewObject_11 = 'Sillage',
  NewObject_18 = 'Gaston', NewObject_20 = 'Atlas', NewObject_21 = 'Suzie',
  NewObject_15 = 'Margot', NewObject_17 = 'Gustave', NewObject_22 = 'Ophélie',
  NewObject_23 = 'Capucine', NewObject_24 = 'Iris',
  Pijako_Livreur = 'Pip', Cradopaud_Pecheur = 'Marius',
  Roserade_Fleuriste = 'Rose', Magneton_Garde = 'Volt',
  Babimanta_Enfant = 'Ondine', Goinfrex_Voyageur = 'Moka',
}

-- Une Baudrive de la carte publiée n’a pas d’identifiant d’entité. Lui
-- donner un prénom sans changer son identité technique ni ses événements.
local function nommer_baudrive_sans_identifiant(map)
  if map == nil or map.Entities == nil then return end
  for couche in luanet.each(map.Entities) do
    for acteur in luanet.each(couche.MapChars) do
      if acteur.EntName == '' and acteur.Data ~= nil and acteur.Data.BaseForm ~= nil
        and acteur.Data.BaseForm.Species == 'drifloon' then
        acteur.Data.Nickname = 'Nuage'
      end
    end
  end
end

local function nommer_habitants(map)
  for nom, prenom in pairs(noms_habitants) do
    local acteur = CH(nom)
    if acteur ~= nil and acteur.Data ~= nil then acteur.Data.Nickname = prenom end
  end
  local mere = CH('Luxray_Alerte')
  if mere ~= nil and mere.Data ~= nil then mere.Data.Nickname = 'Lyra' end
  nommer_baudrive_sans_identifiant(map)
end

local function habitant(nom, espece, genre, x, y)
  local acteur = CH(nom)
  if acteur == nil then
    local donnees = RogueEssence.Dungeon.CharData()
    donnees.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
    donnees.Nickname = nom
    donnees.Level = 5
    acteur = GROUND:CreateCharacterFromCharData(nom, RogueEssence.Dungeon.Character(donnees), x, y, Direction.Down)
  end
  AI:DisableCharacterAI(acteur)
  acteur:ReloadEvents()
  return acteur
end

local function partenaire_pour(hero)
  local partenaire = CH('Teammate1')
  if partenaire == nil and hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
  end
  return partenaire
end

-- Portes des bâtiments : la carte town02 ne sérialise aucune sortie, on
-- installe donc un objet invisible sur chaque seuil (coordonnées relevées
-- sur le rendu de la carte, à confirmer au runtime). Chaque porte mène à
-- l'intérieur correspondant et mémorise le point de retour devant la façade.
local portes_batiments = {
  {nom = 'PortePosteBekipan', titre = 'Poste Bekipan', x = 56, y = 464, largeur = 32, hauteur = 40, retour_x = 80, retour_y = 528, interieur = 'reverie_post_office', marqueur = 'entrance_south', contact_x = 56, contact_y = 504, contact_w = 32, contact_h = 8, partenaire_x = 56, partenaire_y = 528},
  {nom = 'PorteCitrouilleNordOuest', titre = 'Auberge', x = 400, y = 544, largeur = 48, hauteur = 48, retour_x = 432, retour_y = 616, interieur = 'reverie_inn', marqueur = 'Main_Entrance_Marker', contact_x = 400, contact_y = 592, contact_w = 48, contact_h = 8, partenaire_x = 408, partenaire_y = 616},
  {nom = 'PorteHutteNordEst', titre = 'Hutte du nord-est', x = 1048, y = 592, largeur = 32, hauteur = 56, retour_x = 1064, retour_y = 680, interieur = 'reverie_water_home', marqueur = 'Main_Entrance_Marker', contact_x = 1048, contact_y = 648, contact_w = 32, contact_h = 8, partenaire_x = 1040, partenaire_y = 680},
  {nom = 'PorteDojoKingambit', titre = 'Dojo Kingambit', x = 1440, y = 344, largeur = 48, hauteur = 48, retour_x = 1460, retour_y = 416, interieur = 'dojo_kingambit', marqueur = 'MarowakDojoExitMarker', contact_x = 1440, contact_y = 392, contact_w = 48, contact_h = 8, partenaire_x = 1436, partenaire_y = 416},
  {nom = 'PorteHutteSud', titre = 'Hutte aquatique', x = 608, y = 1680, largeur = 72, hauteur = 40, retour_x = 656, retour_y = 1744, interieur = 'reverie_hutte_aquatique', marqueur = 'Main_Entrance_Marker', contact_x = 648, contact_y = 1720, contact_w = 32, contact_h = 8, partenaire_x = 680, partenaire_y = 1744},
  {nom = 'PorteTenteCentre', titre = 'Campement des explorateurs', x = 788, y = 1688, retour_x = 812, retour_y = 1740, interieur = 'reverie_inn', marqueur = 'Main_Entrance_Marker'},
  {nom = 'PorteMaisonPierre', titre = 'Maison de Pierre', x = 440, y = 2296, largeur = 40, hauteur = 40, retour_x = 456, retour_y = 2360, interieur = 'reverie_rock_home', marqueur = 'Main_Entrance_Marker', contact_x = 448, contact_y = 2336, contact_w = 32, contact_h = 8, partenaire_x = 472, partenaire_y = 2344},
  {nom = 'PorteMaisonPlanteSud', titre = 'Maison plante', x = 568, y = 2472, largeur = 32, hauteur = 72, retour_x = 584, retour_y = 2568, interieur = 'reverie_grass_home', marqueur = 'Main_Entrance_Marker', contact_x = 576, contact_y = 2544, contact_w = 24, contact_h = 8, partenaire_x = 560, partenaire_y = 2568},
  {nom = 'PorteCitrouilleSud', titre = 'Maison citrouille du sud', x = 756, y = 2496, largeur = 48, hauteur = 32, retour_x = 776, retour_y = 2552, interieur = 'reverie_fire_home', marqueur = 'Main_Entrance_Marker', contact_x = 760, contact_y = 2528, contact_w = 40, contact_h = 8, partenaire_x = 752, partenaire_y = 2552},
}

local quartier_pour, objet_dans_quartier

local function installer_une_porte(map, nom, x, y, largeur, hauteur)
  if map == nil then return end
  if not objet_dans_quartier(map, x + (largeur or 56)/2, y + (hauteur or 20)/2) then
    if map:FindObject(nom) then GROUND:RemoveObject(nom) end
    return
  end
  if map:FindObject(nom) then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = nom
  porte.Collider = RogueElements.Rect(x, y, largeur or 56, hauteur or 20)
  porte:OnMapInit()
  map:AddObject(porte)
end

-- Remplacer aussi les anciens objets Action conservés dans une sauvegarde.
-- L'objet reste invisible : seule la bande libre juste devant le seuil détecte
-- le contact, sans toucher aux collisions ni aux graphismes du bâtiment.
local function installer_contact_porte(map, nom, x, y, largeur, hauteur)
  if map == nil then return end
  if map:FindObject(nom) then GROUND:RemoveObject(nom) end
  if not objet_dans_quartier(map, x + largeur/2, y + hauteur/2) then return end
  local porte = RogueEssence.Ground.GroundObject()
  porte.EntName = nom
  porte.Collider = RogueElements.Rect(x, y, largeur, hauteur)
  porte.Passable = false
  porte:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  porte:OnMapInit()
  map:AddObject(porte)
end

-- Cinq liaisons confirmées : N1, N2 et N3 nord-centre, S et P au sud.
-- Chaque sens conserve les coordonnées du paysage et une place au partenaire.
local liaisons_quartiers = {
  {nom='EscalierSVersCentre', carte='reverie_residentiel', x=688,y=1952,w=40,h=8, destination='reverie_centre', ax=700,ay=1904,px=700,py=1880,dir='Up'},
  {nom='EscalierSVersResidentiel', carte='reverie_centre', x=688,y=1920,w=40,h=8, destination='reverie_residentiel', ax=700,ay=1976,px=700,py=2000,dir='Down'},
  {nom='EscalierPVersEtang', carte='reverie_residentiel', x=1104,y=2400,w=48,h=8, destination='reverie_etang', ax=1120,ay=2352,px=1120,py=2328,dir='Up'},
  {nom='EscalierPVersResidentiel', carte='reverie_etang', x=1104,y=2376,w=48,h=8, destination='reverie_residentiel', ax=1120,ay=2432,px=1120,py=2456,dir='Down'},
}
local changement_quartier = false
local entree_batiment_en_cours = false

local function interpoler(x, points)
  for i = 2, #points do
    local a, b = points[i-1], points[i]
    if x <= b[1] then return a[2] + (b[2]-a[2]) * (x-a[1]) / (b[1]-a[1]) end
  end
  return points[#points][2]
end

quartier_pour = function(x, y)
  if x < 840 then return y < 1944 and 'reverie_centre' or 'reverie_residentiel' end
  if y < 1872 then return 'reverie_centre' end
  local limite_etang = interpoler(x, {{840,2392},{1128,2392},{1250,2360},{1600,2220}})
  return y < limite_etang and 'reverie_etang' or 'reverie_residentiel'
end

local quartiers_reverie = {
  reverie_centre=true, reverie_nord=true, reverie_residentiel=true, reverie_etang=true,
}
local function secteur_fusion(nom)
  return nom == 'reverie_nord' and 'reverie_centre' or nom
end
objet_dans_quartier = function(map, x, y)
  if map == nil or not quartiers_reverie[map.AssetName] then return true end
  return quartier_pour(x,y) == secteur_fusion(map.AssetName)
end

-- Liste exhaustive des personnages de la carte historique et des six ajouts
-- du script. Leur appartenance est déterminée depuis leur position d'origine.
local habitants_par_quartier = {
  {nom="Kecleon", secteur="reverie_centre", x=599, y=922},
  {nom="Kecleon_Violet", secteur="reverie_centre", x=625, y=922},
  {nom="NewObject_3", secteur="reverie_centre", x=516, y=1092},
  {nom="NewObject_4", secteur="reverie_centre", x=372, y=1172},
  {nom="Kangourex", secteur="reverie_centre", x=932, y=1004},
  {nom="NewObject_6", secteur="reverie_nord", x=404, y=652},
  {nom="NewObject_7", secteur="reverie_centre", x=808, y=1116},
  {nom="NewObject_8", secteur="reverie_centre", x=782, y=1104},
  {nom="NewObject_9", secteur="reverie_residentiel", x=718, y=2527},
  {nom="NewObject_10", secteur="reverie_residentiel", x=709, y=2391},
  {nom="NewObject_12", secteur="reverie_centre", x=691, y=1098},
  {nom="NewObject_13", secteur="reverie_centre", x=652, y=1724},
  {nom="NewObject_14", secteur="reverie_centre", x=857, y=1179},
  {nom="Doyen", secteur="reverie_nord", x=1068, y=308},
  {nom="", secteur="reverie_nord", x=956, y=279},
  {nom="Drifloon", secteur="reverie_nord", x=1084, y=308},
  {nom="NewObject_16", secteur="reverie_centre", x=827, y=1178},
  {nom="NewObject_11", secteur="reverie_residentiel", x=449, y=2378},
  {nom="NewObject_18", secteur="reverie_centre", x=1125, y=1802},
  {nom="NewObject_20", secteur="reverie_residentiel", x=528, y=2372},
  {nom="NewObject_21", secteur="reverie_centre", x=1097, y=1398},
  {nom="NewObject_15", secteur="reverie_centre", x=724, y=1095},
  {nom="NewObject_17", secteur="reverie_residentiel", x=172, y=2616},
  {nom="NewObject_22", secteur="reverie_centre", x=542, y=1373},
  {nom="NewObject_23", secteur="reverie_centre", x=1071, y=1444},
  {nom="NewObject_24", secteur="reverie_centre", x=1103, y=994},
  {nom="Pijako_Livreur", secteur="reverie_nord", x=116, y=508},
  {nom="Cradopaud_Pecheur", secteur="reverie_centre", x=186, y=1496},
  {nom="Roserade_Fleuriste", secteur="reverie_centre", x=748, y=1112},
  {nom="Magneton_Garde", secteur="reverie_residentiel", x=760, y=2052},
  {nom="Babimanta_Enfant", secteur="reverie_centre", x=1112, y=1668},
  {nom="Goinfrex_Voyageur", secteur="reverie_centre", x=1012, y=1404},
}
local proprietaire_habitant = {}
for _, h in ipairs(habitants_par_quartier) do proprietaire_habitant[h.nom] = h end

local function preparer_habitants_quartier(map)
  if map == nil or not quartiers_reverie[map.AssetName] then return end
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PlacementHabitantsReverie = SV.Destiny.PlacementHabitantsReverie or {}
  local premiere_correction = not SV.Destiny.PlacementHabitantsReverie[map.AssetName]
  for _, h in ipairs(habitants_par_quartier) do
    local acteur = map:GetMapChar(h.nom)
    if secteur_fusion(h.secteur) ~= secteur_fusion(map.AssetName) then
      -- Nettoie aussi les PNJ résiduels des sauvegardes de la 0.4.14.
      -- Le joueur et son partenaire ne figurent jamais dans cette liste.
      local garde = 0
      while acteur ~= nil and garde < 32 do
        pcall(function() AI:DisableCharacterAI(acteur) end)
        if not GROUND:RemoveCharacter(h.nom) then break end
        garde = garde + 1
        acteur = map:GetMapChar(h.nom)
      end
    elseif acteur ~= nil then
      local position = acteur.Position
      if premiere_correction or quartier_pour(position.X+8, position.Y+8) ~= secteur_fusion(map.AssetName) then
        GROUND:TeleportTo(acteur, h.x, h.y, acteur.Direction)
      end
    end
  end
  SV.Destiny.PlacementHabitantsReverie[map.AssetName] = true
end

local function habitant_du_quartier(map, nom, espece, genre, x, y)
  local h = proprietaire_habitant[nom]
  if map ~= nil and quartiers_reverie[map.AssetName] and (h == nil or secteur_fusion(h.secteur) ~= secteur_fusion(map.AssetName)) then return nil end
  if h ~= nil and map ~= nil and quartiers_reverie[map.AssetName] then x,y=h.x,h.y end
  return habitant(nom, espece, genre, x, y)
end

-- Une instance distincte garde son poste sur le centre pendant l’alerte.
-- L’originale du quartier résidentiel reste conservée, mais cachée.
local function installer_luxray_attente(map)
  if map == nil then return end
  SV.Destiny = SV.Destiny or {}
  local attente = SV.Destiny.AlerteShinx == 'a_secourir'
  if map.AssetName == 'reverie_residentiel' then
    if CH('NewObject_9') ~= nil then
      if attente then GROUND:Hide('NewObject_9') else GROUND:Unhide('NewObject_9') end
    end
    return
  end
  if map.AssetName ~= 'reverie_centre' then return end
  if not attente then
    if CH('Luxray_Alerte') ~= nil then GROUND:RemoveCharacter('Luxray_Alerte') end
    return
  end
  local x, y = 800, 1224
  if SV.Destiny.LuxrayAttente == 'sortie' then x,y=1504,1584 end
  local acteur = habitant('Luxray_Alerte', 'luxray', Gender.Female, x, y)
  if acteur.Data ~= nil then acteur.Data.Nickname = 'Lyra' end
  GROUND:TeleportTo(acteur, x, y, Direction.Up)
end

local function case_libre(map, x, y)
  if x < 0 or y < 0 or x+16 > map.Width*8 or y+16 > map.Height*8 then return false end
  for cx=math.floor(x/8),math.floor((x+15)/8) do
    for cy=math.floor(y/8),math.floor((y+15)/8) do
      if map:GetObstacle(cx,cy) ~= 0 then return false end
    end
  end
  return true
end

local function case_proche(map, x, y)
  if case_libre(map,x,y) then return x,y end
  for rayon=8,32,8 do
    for dx=-rayon,rayon,8 do
      for dy=-rayon,rayon,8 do
        if math.max(math.abs(dx),math.abs(dy)) == rayon and case_libre(map,x+dx,y+dy) then
          return x+dx,y+dy
        end
      end
    end
  end
  return x,y
end

local function demander_quartier(destination, x, y, px, py, dir)
  if changement_quartier then return end
  changement_quartier = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PassageQuartier = {x=x,y=y,px=px,py=py,dir=dir}
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('town02_waterfallvillage', destination, 'entrance', true)
end

local function installer_liaisons_quartiers(map)
  if map == nil then return end
  -- Retirer les anciens capteurs internes encore présents dans une sauvegarde.
  if map.AssetName == 'reverie_centre' or map.AssetName == 'reverie_nord' then
    for _, nom in ipairs({'EscalierN1VersNord','EscalierN1VersCentre','EscalierN2VersNord','EscalierN2VersCentre','EscalierN3VersNord','EscalierN3VersCentre'}) do
      if map:FindObject(nom) then GROUND:RemoveObject(nom) end
    end
  end
  for _, def in ipairs(liaisons_quartiers) do
    if map.AssetName == def.carte and not map:FindObject(def.nom) then
      local sortie = RogueEssence.Ground.GroundObject()
      sortie.EntName = def.nom
      sortie.Collider = RogueElements.Rect(def.x,def.y,def.w,def.h)
      sortie.Passable = false
      sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
      sortie:OnMapInit()
      map:AddObject(sortie)
    end
  end
end

for _, voie_def in ipairs(liaisons_quartiers) do
  local voie = voie_def
  ville[voie.nom .. '_Touch'] = function(obj, activator)
    if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
    demander_quartier(voie.destination, voie.ax, voie.ay, voie.px, voie.py, voie.dir)
  end
end

local function installer_sortie_carrefour(map)
  if map ~= nil and not objet_dans_quartier(map, 40, 1589) then
    if map:FindObject('SortieCarrefour') then GROUND:RemoveObject('SortieCarrefour') end
    return
  end
  if map == nil or map:FindObject('SortieCarrefour') then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = 'SortieCarrefour'
  -- Bord ouest du chemin existant, face au marqueur d'entrée de la ville.
  sortie.Collider = RogueElements.Rect(8, 1544, 8, 48)
  sortie.Passable = true
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

local function installer_sortie_e2(map)
  if map ~= nil and not objet_dans_quartier(map, 1592, 1600) then
    if map:FindObject('SortieExplorationE2') then GROUND:RemoveObject('SortieExplorationE2') end
    return
  end
  if map == nil or map:FindObject('SortieExplorationE2') then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = 'SortieExplorationE2'
  sortie.Collider = RogueElements.Rect(1584, 1584, 16, 32)
  sortie.Passable = false
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

local function installer_portes(map)
  -- Ancien raccord non confirmé vers un dojo extérieur au projet : retirer
  -- uniquement le capteur résiduel, sans effacer la carte ni ses sauvegardes.
  if map ~= nil and map:FindObject('PorteTenteEst') then GROUND:RemoveObject('PorteTenteEst') end
  installer_sortie_carrefour(map)
  installer_sortie_e2(map)
  installer_liaisons_quartiers(map)
  -- Les deux tableaux existants proposent missions et gazette.
  installer_une_porte(map, 'TableauReverieNord', 144, 400, 56, 48)
  installer_une_porte(map, 'TableauReverieCentre', 400, 1512, 48, 56)
  -- Café Spinda : tapis rouge de l'annexe (centre x≈1188, y≈1605).
  installer_contact_porte(map, 'PorteCafeSpinda', 1056, 1344, 32, 8)
  for _, porte in ipairs(portes_batiments) do
    if porte.contact_x ~= nil then
      installer_contact_porte(map, porte.nom, porte.contact_x, porte.contact_y, porte.contact_w, porte.contact_h)
    else
      -- Les tentes n'ont pas encore de correspondance extérieure/intérieure confirmée.
      installer_une_porte(map, porte.nom, porte.x, porte.y, porte.largeur, porte.hauteur)
    end
  end
end

-- Comptoirs des boutiques, façon Reverie Town : chaque marchand se tient
-- dans sa boutique, derrière son comptoir, et le joueur lui parle en
-- interagissant devant le comptoir. Le comptoir est un objet invisible
-- infranchissable posé sur la devanture (déjà bloquée par les collisions
-- town02, sauf la terrasse de la forge) ; le poste est l’alcôve fermée de
-- la boutique relevée dans ces mêmes collisions. Les deux Kecleon sont
-- déjà sérialisés derrière leur comptoir : aucun poste à corriger pour
-- eux. Les seuils d’Alakazam, de Kangourex et de la forge deviennent des
-- comptoirs : leurs anciennes portes d’intérieur sont donc retirées.
local comptoirs = {
  {nom = 'ComptoirKecleon', marchand = 'Kecleon', x = 584, y = 936, w = 32, h = 16},
  {nom = 'ComptoirKecleonViolet', marchand = 'Kecleon_Violet', x = 616, y = 936, w = 32, h = 16},
  {nom = 'ComptoirBanqueMordudor', marchand = 'NewObject_3', x = 480, y = 1072, w = 64, h = 16, poste_x = 504, poste_y = 1040},
  {nom = 'ComptoirAlakazam', marchand = 'NewObject_4', x = 352, y = 1120, w = 32, h = 16, poste_x = 360, poste_y = 1100},
  {nom = 'ComptoirKangourex', marchand = 'Kangourex', x = 928, y = 952, w = 40, h = 16, poste_x = 940, poste_y = 930},
  {nom = 'ComptoirForgeTinkaton', marchand = 'NewObject_24', x = 1080, y = 1008, w = 64, h = 16, poste_x = 1104, poste_y = 992},
}

local function installer_comptoirs(map)
  if map == nil then return end
  for _, comptoir_def in ipairs(comptoirs) do
    if not objet_dans_quartier(map, comptoir_def.x + comptoir_def.w/2, comptoir_def.y + comptoir_def.h/2) then
      if map:FindObject(comptoir_def.nom) then GROUND:RemoveObject(comptoir_def.nom) end
    elseif not map:FindObject(comptoir_def.nom) then
      local comptoir = RogueEssence.Ground.GroundObject()
      comptoir.EntName = comptoir_def.nom
      comptoir.Collider = RogueElements.Rect(comptoir_def.x, comptoir_def.y, comptoir_def.w, comptoir_def.h)
      pcall(function()
        comptoir.Passable = false
        comptoir:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Action)
      end)
      comptoir:OnMapInit()
      map:AddObject(comptoir)
    end
  end
end

-- Chaque marchand prend son poste derrière son comptoir, face à la rue
-- (sud). Le poste devient sa position de repos mémorisée : après un
-- dialogue, il reprend cette orientation sans jamais quitter la boutique.
local function placer_marchands_aux_comptoirs()
  for _, comptoir_def in ipairs(comptoirs) do
    if comptoir_def.poste_x ~= nil then
      local marchand = CH(comptoir_def.marchand)
      if marchand ~= nil then
        GROUND:TeleportTo(marchand, comptoir_def.poste_x, comptoir_def.poste_y, Direction.Down)
        positions_habitants[comptoir_def.marchand] = {
          x = comptoir_def.poste_x, y = comptoir_def.poste_y, dir = Direction.Down,
        }
      end
    end
  end
end

function ville.Init(map)
  changement_quartier = false
  entree_batiment_en_cours = false
  preparer_habitants_quartier(map)
  installer_luxray_attente(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  installer_portes(map)
  installer_comptoirs(map)
  habitant_du_quartier(map, 'Kecleon', 'kecleon', Gender.Male, 599, 922)
  habitant_du_quartier(map, 'Kangourex', 'kangaskhan', Gender.Female, 940, 930)
  -- Habitants ajoutés (ville vivante) : créés s'ils ne sont pas sérialisés
  -- dans la carte (positions relevées sur le rendu, à confirmer au runtime).
  habitant_du_quartier(map, 'Pijako_Livreur', 'chatot', Gender.Male, 116, 508)
  habitant_du_quartier(map, 'Cradopaud_Pecheur', 'croagunk', Gender.Male, 186, 1496)
  habitant_du_quartier(map, 'Roserade_Fleuriste', 'roserade', Gender.Female, 748, 1112)
  habitant_du_quartier(map, 'Magneton_Garde', 'magneton', Gender.Genderless, 772, 2052)
  habitant_du_quartier(map, 'Babimanta_Enfant', 'mantyke', Gender.Female, 1112, 1668)
  habitant_du_quartier(map, 'Goinfrex_Voyageur', 'munchlax', Gender.Male, 1012, 1404)
  -- Luxio et Luxray partagent un vrai dialogue, mais la carte les place à
  -- 136 px l'un de l'autre, de part et d'autre de la maison citrouille sud.
  -- Luxray est donc posé juste à l'est de Luxio, sur l'herbe libre au nord
  -- de la maison ; ils peuvent enfin se faire face sans se déplacer.
  local luxio, luxray = CH('NewObject_10'), CH('NewObject_9')
  if luxio ~= nil and luxray ~= nil then
    GROUND:TeleportTo(luxray, luxio.Position.X + 24, luxio.Position.Y,
      Direction.Left)
    GROUND:EntTurn(luxio, Direction.Right)
  end
  placer_marchands_aux_comptoirs()
  -- Rétablit le marchand si une précédente scène a été interrompue.
  if CH('NewObject_4') ~= nil then GROUND:Unhide('NewObject_4') end
  positions_habitants = {}
  for _, nom in ipairs(habitants_vivants) do
    local acteur = CH(nom)
    if acteur ~= nil then
      positions_habitants[nom] = {
        x = acteur.Position.X, y = acteur.Position.Y, dir = acteur.Direction,
      }
      if est_fixe(nom) then figer_habitant(nom, acteur) end
    end
  end
  nommer_habitants(map)
  vie_ville_activee = false
  partenaire_pour(CH('PLAYER'))
  -- Ombres de nuages sur toute la ville : même statut natif que la ville de base PMDO.
  GROUND:AddMapStatus('clouds_overhead')
end

local function parler(personnage, emotion, texte, placement)
  if personnage == nil then return end
  cinematique.Dire(personnage, emotion, texte, placement or 'standard')
end

-- Pour les accueils de la visite : aucun déplacement pendant la réplique ;
-- l'Idle explicite est la préférence demandée pour ces PNJ de la place.
local function parler_accueil(personnage, emotion, texte, placement)
  if personnage == nil then return end
  AI:DisableCharacterAI(personnage)
  GROUND:CharSetAnim(personnage, 'Idle', true)
  parler(personnage, emotion, texte, placement)
  GROUND:CharEndAnim(personnage)
end

-- Le héros ne parle pas pendant la visite : le partenaire lit ses gestes.
-- Les rotations restent à la vitesse 4 des cinématiques Destiny, et un
-- geste adressé au partenaire se termine en le regardant.
local function geste_heros(hero, geste, partenaire)
  if hero == nil then return end
  UI:ResetSpeaker()
  local function vers_partenaire()
    if partenaire ~= nil then
      GROUND:CharTurnToCharAnimated(hero, partenaire, 4)
    else
      GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    end
  end
  if geste == 'question' then
    SOUND:PlayBattleSE('EVT_Emote_Confused')
    GROUND:CharSetEmote(hero, 'question', 1)
    vers_partenaire()
    GAME:WaitFrames(28)
  elseif geste == 'autour' then
    GROUND:CharAnimateTurnTo(hero, Direction.Left, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Right, 4)
    GAME:WaitFrames(14)
    GROUND:CharAnimateTurnTo(hero, Direction.Up, 4)
    GAME:WaitFrames(10)
    vers_partenaire()
    GAME:WaitFrames(12)
  else -- oui : regard vers le partenaire, deux inclinaisons, puis retour.
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
    GAME:WaitFrames(7)
    GROUND:CharAnimateTurnTo(hero, Direction.Down, 4)
    GAME:WaitFrames(9)
    vers_partenaire()
    GAME:WaitFrames(16)
  end
end

local function se_faire_face_ville(a, b)
  cinematique.RegarderGroupe({
    {a, b, 0, 4},
    {b, a, 5, 4},
  })
  cinematique.Respirer(10)
end

local function regarder_lieu_ville(hero, partenaire, direction)
  cinematique.TournerGroupe({
    {partenaire, direction, 0, 4},
    {hero, direction, 5, 4},
  })
end

local function activer_vie_ville()
  if vie_ville_activee then return end
  vie_ville_activee = true
  for _, nom in ipairs(habitants_vivants) do
    local acteur, depart = CH(nom), positions_habitants[nom]
    if acteur ~= nil and depart ~= nil then
      if est_fixe(nom) then
        -- Marchands à leur comptoir et duos en discussion : aucune zone de
        -- marche, IA coupée, idle par défaut et orientation de repos.
        figer_habitant(nom, acteur)
      else
        local rayon = 56
        local cx, cy = depart.x, depart.y
        -- Chaque jour, quelques flâneurs changent de quartier de déambulation.
        local vagabonds = {
          Pijako_Livreur = {{0, 0}, {72, 0}, {-72, 0}},
          Cradopaud_Pecheur = {{0, 0}, {0, 72}, {0, -72}},
          Goinfrex_Voyageur = {{0, 0}, {72, 0}, {-72, 0}},
        }
        local decalages = vagabonds[nom]
        if decalages ~= nil then
          local d = decalages[(jour_actuel() % #decalages) + 1]
          cx, cy = cx + d[1], cy + d[2]
        end
        COMMON.CreateWalkArea(nom,
          math.max(0, cx - rayon), math.max(0, cy - rayon),
          rayon * 2, rayon * 2)
        AI:EnableCharacterAI(acteur)
      end
    end
  end
end

local function retour_au_joueur(hero, partenaire)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:MoveCamera(0, 0, 45, true)
  activer_vie_ville()
  if hero ~= nil and partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
end

-- Réactions en vagues : pas seulement les habitants nommés à l'avance.
-- Les personnages réellement cachés et les protagonistes sont traités ailleurs.
local function temoins_de_la_visite(map, hero, partenaire, alakazam)
  local liste, vus = {}, {}
  local function ajouter(a)
    if a == nil or a == hero or a == partenaire or a == alakazam then return end
    local nom = a.EntName
    if nom == 'PLAYER' or nom == 'Teammate1' or nom == 'NewObject_4' or nom == 'NewObject_9' or nom == 'Luxray_Alerte' then return end
    if a.EntEnabled == false or vus[a] then return end
    vus[a] = true
    table.insert(liste, a)
  end
  if map ~= nil and map.Entities ~= nil then
    for couche in luanet.each(map.Entities) do
      if couche.Visible ~= false then
        for acteur in luanet.each(couche.MapChars) do ajouter(acteur) end
        for acteur in luanet.each(couche.TemporaryChars) do ajouter(acteur) end
      end
    end
  else
    -- Utilisé uniquement si l'appelant n'a pas fourni de carte (doublures).
    for _, nom in ipairs(habitants_vivants) do ajouter(CH(nom)) end
    ajouter(CH(''))
  end
  return liste
end

local function reagir_ville(temoins, hero, partenaire, phase)
  UI:ResetSpeaker()
  SOUND:PlayBattleSE(phase == 'cri' and 'EVT_Emote_Exclaim_2' or 'EVT_Emote_Shock')
  -- Le partenaire réagit en premier ; le héros lui répond visuellement.
  GROUND:CharSetEmote(partenaire, phase == 'cri' and 'exclaim' or 'shock', 1)
  GAME:WaitFrames(5)
  -- Le héros manifeste une surprise plus contenue que le partenaire.
  GROUND:CharSetEmote(hero, 'exclaim', 1)
  -- Quatre vagues éparpillées : chaque témoin actif a une réaction, mais
  -- tous ne font pas exactement le même geste au même instant.
  for vague = 1, 4 do
    for index, acteur in ipairs(temoins) do
      if (index - 1) % 4 == vague - 1 then
        local emote
        if phase == 'cri' then emote = (index % 3 == 0) and 'question' or 'exclaim'
        else emote = (index % 3 == 0) and 'sweatdrop' or 'shock' end
        GROUND:CharSetEmote(acteur, emote, 1)
      end
    end
    if vague < 4 then GAME:WaitFrames(5) end
  end
  GAME:WaitFrames(22)
end

function ville.Visite(map)
  local hero = CH('PLAYER')
  local partenaire = partenaire_pour(hero)
  if hero == nil or partenaire == nil then
    -- Ne pas marquer la visite comme terminée si l'équipe est incomplète.
    GAME:FadeIn(20)
    print('[Destiny] Visite de la ville suspendue : partenaire absent de l’équipe.')
    return
  end
  local kecleon, kangourex = CH('Kecleon'), CH('Kangourex')
  local alakazam, mordudor, forgelina = CH('NewObject_4'), CH('NewObject_3'), CH('NewObject_24')
  local dracaufeu, lombre, ludicolo = CH('NewObject_16'), CH('NewObject_7'), CH('NewObject_8')
  local roserade = CH('Roserade_Fleuriste')
  -- Une ancienne sauvegarde peut placer Rose ailleurs : ne pas l'appeler ni
  -- la téléporter depuis l'autre côté de la ville.
  if roserade ~= nil and (roserade.EntEnabled == false or roserade.Position == nil
    or math.abs(roserade.Position.X - 800) > 160
    or math.abs(roserade.Position.Y - 1180) > 120) then roserade = nil end
  local guide_hors_champ = false
  local function parler_guide(emotion, texte)
    if guide_hors_champ then
      -- Même nom dynamique que SetSpeaker(GroundChar), mais sans portrait
      -- lorsque la caméra montre un comptoir loin du duo.
      UI:ResetSpeaker()
      UI:SetSpeaker(partenaire:GetDisplayName(), true, '', -1, '', RogueEssence.Data.Gender.Unknown)
      UI:WaitShowDialogue(texte)
    else
      cinematique.Dire(partenaire, emotion, texte, 'droite')
    end
  end
  -- Orienter seulement les auditeurs présents vers le locuteur de ce temps
  -- dramatique. Les regards se chevauchent, sans synchronisation mécanique.
  local function ecouter_scene(locuteur, ...)
    if locuteur == nil or locuteur.EntEnabled == false then return end
    local regards, vus = {}, {}
    for i = 1, select('#', ...) do
      local auditeur = select(i, ...)
      if auditeur ~= nil and auditeur ~= locuteur and auditeur.EntEnabled ~= false and not vus[auditeur] then
        vus[auditeur] = true
        table.insert(regards, {auditeur, locuteur, (#regards * 5), 4})
      end
    end
    if #regards > 0 then
      UI:ResetSpeaker()
      cinematique.RegarderGroupe(regards)
    end
  end
  -- Les passants visibles conservent un idle discret pendant les plans de
  -- découverte ; les acteurs de l'échange, les services et Lyra ne sont
  -- pas touchés. Aucune IA de marche n'est activée pendant la cinématique.
  local fond_anime = {}
  local exclus_fond = {
    PLAYER=true, Teammate1=true, Kecleon=true, Kecleon_Violet=true,
    Kangourex=true, NewObject_3=true, NewObject_4=true, NewObject_7=true,
    NewObject_8=true, NewObject_9=true, NewObject_14=true, NewObject_16=true,
    NewObject_24=true, Roserade_Fleuriste=true, Luxray_Alerte=true,
  }
  local function arreter_fond()
    for _, acteur in ipairs(fond_anime) do
      if acteur ~= nil then pcall(function() GROUND:CharEndAnim(acteur) end) end
    end
    fond_anime = {}
  end
  local function animer_fond(cx, cy)
    arreter_fond()
    if map == nil or map.Entities == nil then return end
    local vus = {}
    -- Si la liste des entités n'est pas exploitable, aucun mouvement forcé.
    pcall(function()
      local function ajouter_fond(acteur)
        if acteur ~= nil and acteur ~= hero and acteur ~= partenaire
          and acteur.EntEnabled ~= false and acteur.Position ~= nil
          and not exclus_fond[acteur.EntName] and not vus[acteur]
          and math.abs(acteur.Position.X-cx) <= 160
          and math.abs(acteur.Position.Y-cy) <= 120 then
          vus[acteur] = true
          local ok = pcall(function() GROUND:CharSetAnim(acteur, 'Idle', true) end)
          if ok then table.insert(fond_anime, acteur) end
        end
      end
      for couche in luanet.each(map.Entities) do
        if couche.Visible ~= false then
          for acteur in luanet.each(couche.MapChars) do ajouter_fond(acteur) end
          for acteur in luanet.each(couche.TemporaryChars) do ajouter_fond(acteur) end
        end
      end
    end)
  end
  local function regarder_alerte(temoins)
    local regards = {}
    for _, acteur in ipairs(temoins) do
      if acteur.Position ~= nil and acteur.EntEnabled ~= false
        and math.abs(acteur.Position.X-832) <= 160
        and math.abs(acteur.Position.Y-1208) <= 120 then
        table.insert(regards, {acteur, Direction.Down, ((#regards % 4) * 4), 4})
      end
    end
    if #regards > 0 then cinematique.TournerGroupe(regards) end
  end
  GAME:CutsceneMode(true)
  -- Son comptoir reste vide pendant la visite ; on conserve son instance.
  if alakazam ~= nil then GROUND:Hide('NewObject_4') end
  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  GROUND:TeleportTo(hero, ENTREE_X - 8, ENTREE_Y, Direction.Up)
  GROUND:TeleportTo(partenaire, ENTREE_X + 12, ENTREE_Y - 20, Direction.Up)
  GAME:MoveCamera(ENTREE_X, ENTREE_Y - 30, 1, false)
  SOUND:PlayBGM('Treasure Town.ogg', true)
  GAME:FadeIn(45)
  GAME:WaitFrames(20) -- laisser apparaître la place avant le premier échange

  se_faire_face_ville(partenaire, hero)
  parler_guide('Happy', 'Nous y voilà ! Bienvenue à [color=#F5D27A]Réverie Town[color].')
  parler_guide('Normal', 'Le jour se lève. Reste avec moi : je vais te montrer les endroits importants.')
  geste_heros(hero, 'oui', partenaire)
  parler_guide('Happy', 'Après cette nuit, tu n’arrives pas ici tout seul. On avance ensemble.')

  -- Les deux habitants restent à leur place. Le partenaire quitte l’axe
  -- de Dracaufeu avant de monter ; le héros le suit à distance.
  local tyranocif_accueil = CH('NewObject_14')
  local function chevauche_trajet(acteur)
    if acteur == nil then return false end
    local x, y = acteur.Position.X, acteur.Position.Y
    local function sur_segment(x1,y1,x2,y2)
      return x < math.max(x1,x2)+16 and x+16 > math.min(x1,x2)
         and y < math.max(y1,y2)+16 and y+16 > math.min(y1,y2)
    end
    return sur_segment(812,1300,812,1224) or sur_segment(812,1224,784,1224)
      or sur_segment(784,1224,784,1152) or sur_segment(792,1320,792,1176)
      or sur_segment(792,1176,760,1176)
  end
  if chevauche_trajet(dracaufeu) or chevauche_trajet(tyranocif_accueil) then
    if alakazam ~= nil then GROUND:Unhide('NewObject_4') end
    UI:ResetSpeaker()
    retour_au_joueur(hero, partenaire)
    print('[Destiny] Visite suspendue : un habitant occupe le trajet.')
    return
  end
  if tyranocif_accueil ~= nil then AI:DisableCharacterAI(tyranocif_accueil) end
  if dracaufeu ~= nil then
    GAME:MoveCamera(800, 1240, 45, false)
    AI:DisableCharacterAI(dracaufeu)
    GROUND:CharAnimateTurnTo(dracaufeu, Direction.Down, 4)
  end
  local avance_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, 812, 1224, false, 1.5)
    GROUND:MoveToPosition(partenaire, 784, 1224, false, 1.5)
    GROUND:MoveToPosition(partenaire, 784, 1152, false, 1.5)
  end)
  local avance_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(25)
    GROUND:MoveToPosition(hero, 792, 1176, false, 1.5)
    GROUND:MoveToPosition(hero, 760, 1176, false, 1.5)
  end)
  local suivi = TASK:BranchCoroutine(function() GAME:MoveCamera(PLACE_X, PLACE_Y + 20, 100, false) end)
  TASK:JoinCoroutines({avance_partenaire, avance_hero, suivi})
  GAME:WaitFrames(16) -- le duo finit sa marche avant de découvrir la place
  animer_fond(800, 1160)
  -- Ces deux habitants sont déjà sur la place. On ne déplace ni Dracaufeu
  -- ni Tyranocif. Les coordonnées ne sont utilisées que depuis leur place
  -- connue et après contrôle des personnages présents sur chaque segment.
  local avances = {}
  local function passage_libre(acteur, points)
    if map == nil or map.Entities == nil or acteur == nil or acteur.EntEnabled == false then return false end
    local function croise(autre)
      if autre == nil or autre == acteur or autre.EntEnabled == false or autre.Position == nil then return false end
      local x, y = autre.Position.X, autre.Position.Y
      for i = 1, #points - 1 do
        local a, b = points[i], points[i + 1]
        if x < math.max(a[1], b[1]) + 16 and x + 16 > math.min(a[1], b[1])
          and y < math.max(a[2], b[2]) + 16 and y + 16 > math.min(a[2], b[2]) then return true end
      end
      return false
    end
    if croise(hero) or croise(partenaire) then return false end
    -- En cas d'API de carte indisponible, ne pas risquer un déplacement forcé.
    local ok, libre = pcall(function()
      for couche in luanet.each(map.Entities) do
        if couche.Visible then
          for autre in luanet.each(couche.MapChars) do if croise(autre) then return false end end
          for autre in luanet.each(couche.TemporaryChars) do if croise(autre) then return false end end
        end
      end
      return true
    end)
    return ok and libre
  end
  local function approcher(acteur, origine_x, origine_y, points)
    if acteur == nil or acteur.EntEnabled == false or acteur.Position == nil
      or acteur.Position.X ~= origine_x or acteur.Position.Y ~= origine_y
      or not passage_libre(acteur, points) then return end
    local depart = {acteur=acteur, x=origine_x, y=origine_y, dir=acteur.Direction, points=points}
    AI:DisableCharacterAI(acteur)
    for i = 2, #points do
      if not passage_libre(acteur, {points[i-1], points[i]}) then break end
      GROUND:MoveToPosition(acteur, points[i][1], points[i][2], false, 1)
    end
    table.insert(avances, depart)
  end
  -- Le duo arrive pendant une conversation déjà en cours, visible dans le
  -- même plan : Rose n'est ni téléportée ni forcée à rejoindre la place.
  if roserade ~= nil and lombre ~= nil and lombre.EntEnabled ~= false
    and lombre.Position ~= nil
    and math.abs(roserade.Position.X-lombre.Position.X) <= 96
    and math.abs(roserade.Position.Y-lombre.Position.Y) <= 64 then
    GROUND:CharTurnToCharAnimated(roserade, lombre, 4)
    ecouter_scene(roserade, lombre, ludicolo)
    GAME:WaitFrames(10)
    parler_accueil(roserade, 'Happy', 'J’ai terminé les guirlandes pour le retour de la guilde. J’espère qu’elles leur plairont !')
    GAME:WaitFrames(10)
    GROUND:CharTurnToCharAnimated(lombre, roserade, 4)
    ecouter_scene(lombre, roserade, ludicolo)
    parler_accueil(lombre, 'Happy', 'Avec toutes ces fleurs, la place leur fera une belle surprise !')
    GAME:WaitFrames(14)
  end
  -- Ludicolo remarque le duo en premier, puis se tourne vers lui. Le son
  -- n'est joué qu'une fois et les autres prennent le temps de suivre.
  if ludicolo ~= nil and ludicolo.EntEnabled ~= false then
    UI:ResetSpeaker()
    SOUND:PlayBattleSE('EVT_Emote_Exclaim_2')
    GROUND:CharSetEmote(ludicolo, 'exclaim', 1)
    GAME:WaitFrames(8)
    GROUND:CharTurnToCharAnimated(ludicolo, partenaire, 4)
  end
  -- Deux trajets courts contrôlés en présence des occupants. Le trajet
  -- vertical de Ludicolo laisse intacte la place de Roserade à l'ouest.
  approcher(lombre, 808, 1116, {{808,1116},{808,1136}})
  GAME:WaitFrames(8)
  approcher(ludicolo, 782, 1104, {{782,1104},{782,1128}})
  GAME:WaitFrames(12)
  if ludicolo ~= nil and ludicolo.EntEnabled ~= false then
    ecouter_scene(ludicolo, partenaire, hero, roserade, lombre, dracaufeu, tyranocif_accueil)
    GROUND:CharTurnToCharAnimated(ludicolo, partenaire, 4)
    parler_accueil(ludicolo, 'Happy', 'Oh, vous voilà ! Prenez votre temps, vous êtes ici chez vous !')
    GAME:WaitFrames(14)
  end
  if dracaufeu ~= nil then
    ecouter_scene(dracaufeu, partenaire, hero, tyranocif_accueil, lombre, ludicolo, roserade)
    GROUND:CharTurnToCharAnimated(dracaufeu, partenaire, 4)
    parler_accueil(dracaufeu, 'Happy', 'Bienvenue à Réverie Town ! Vous arrivez au bon moment : la ville se réveille tout juste.', 'droite')
    GAME:WaitFrames(18)
  end
  regarder_lieu_ville(hero, partenaire, Direction.Up)
  parler_guide('Happy', 'Voici la place. Les chemins, les ponts et les boutiques se rejoignent ici.')
  if lombre ~= nil then
    ecouter_scene(lombre, partenaire, hero, ludicolo, roserade, dracaufeu, tyranocif_accueil)
    GROUND:CharTurnToCharAnimated(lombre, partenaire, 4)
    parler_accueil(lombre, 'Happy', 'Bienvenue ! C’est un plaisir de vous voir à Réverie.')
  end
  if roserade ~= nil then
    ecouter_scene(roserade, partenaire, hero, lombre, ludicolo, dracaufeu, tyranocif_accueil)
    GROUND:CharTurnToCharAnimated(roserade, partenaire, 4)
    parler_accueil(roserade, 'Happy', 'Bienvenue ! Si vous cherchez votre chemin, nous serons ravis de vous aider.')
  end
  if tyranocif_accueil ~= nil then
    ecouter_scene(tyranocif_accueil, partenaire, hero, roserade, lombre, ludicolo, dracaufeu)
    GROUND:CharTurnToCharAnimated(tyranocif_accueil, partenaire, 4)
    parler_accueil(tyranocif_accueil, 'Normal', 'Prenez le temps de découvrir la ville. Vous y trouverez toujours quelqu’un à qui parler.', 'droite')
  end
  -- Le duo est arrivé tôt : information, pas ouverture de guilde inventée.
  local hote_guilde = lombre or ludicolo or dracaufeu
  if hote_guilde ~= nil then
    GAME:WaitFrames(20)
    ecouter_scene(hote_guilde, partenaire, hero, roserade, lombre, ludicolo, dracaufeu, tyranocif_accueil)
    -- L'hôte indique le nord, puis revient à ses interlocuteurs.
    GROUND:CharAnimateTurnTo(hote_guilde, Direction.Up, 4)
    GAME:WaitFrames(12)
    GROUND:CharTurnToCharAnimated(hote_guilde, partenaire, 4)
    parler_accueil(hote_guilde, 'Normal', 'La guilde se trouve en haut de l’escalier nord.\nElle est encore fermée : vous êtes en avance ! Elle ouvrira plus tard dans la journée.')
    GAME:WaitFrames(16)
    ecouter_scene(partenaire, hero, hote_guilde, roserade, lombre, ludicolo, dracaufeu, tyranocif_accueil)
    parler_guide('Normal', 'Les membres de la guilde sont déjà partis ?')
    if ludicolo ~= nil and ludicolo ~= hote_guilde then
      ecouter_scene(ludicolo, partenaire, hero, hote_guilde, roserade, dracaufeu, tyranocif_accueil)
      parler_accueil(ludicolo, 'Normal', 'Oui, ils sont en expédition. La place sera plus animée quand ils rentreront.')
    end
    parler_guide('Happy', 'Alors nous reviendrons les rencontrer plus tard. En attendant, je vais te montrer la ville !')
    GAME:WaitFrames(20)
  end

  regarder_lieu_ville(hero, partenaire, Direction.UpLeft)
  guide_hors_champ = true
  animer_fond(616, 925)
  GAME:MoveCamera(616, 925, 160, false)
  parler_guide('Normal', 'Là-bas, c’est la boutique de Basil et Félix. Ces deux frères Kecleon vendent des provisions pour les expéditions.')
  if kecleon ~= nil then
    GROUND:CharAnimateTurnTo(kecleon, Direction.Down, 4)
    parler_accueil(kecleon, 'Happy', 'Bienvenue ! Une pomme ou une baie peut toujours être utile en chemin.')
  end
  GAME:WaitFrames(12) -- le duo est hors champ : aucun geste invisible
  parler_guide('Happy', 'C’est ça : on vérifiera notre sac avant chaque départ.')

  regarder_lieu_ville(hero, partenaire, Direction.UpRight)
  animer_fond(936, 940)
  GAME:MoveCamera(936, 940, 180, false)
  parler_guide('Normal', 'Et voici Mado, la Kangourex. Elle garde les objets que nous préférons laisser en sécurité.')
  if kangourex ~= nil then
    GROUND:CharAnimateTurnTo(kangourex, Direction.Down, 4)
    parler_accueil(kangourex, 'Happy', 'Confiez-moi vos affaires et revenez les chercher quand vous voudrez.')
  end
  GAME:WaitFrames(12) -- ne pas animer le héros hors champ
  parler_guide('Normal', 'Exactement : ce que nous laissons à tatie Mado n’a pas à traverser le donjon avec nous.')

  regarder_lieu_ville(hero, partenaire, Direction.UpRight)
  animer_fond(1100, 950)
  GAME:MoveCamera(1100, 950, 90, false)
  parler_guide('Happy', 'Juste à côté, il y a aussi cet étal aux couleurs vives. Le quartier du marché est plein de surprises !')
  if forgelina ~= nil then
    GAME:MoveCamera(1104, 992, 45, false)
    parler_guide('Normal', 'Voici aussi Iris. Cette Forgelina ouvre les boîtes trouvées en exploration.')
    GROUND:CharAnimateTurnTo(forgelina, Direction.Down, 4)
    parler_accueil(forgelina, 'Happy', 'Rapportez-moi vos boîtes ! Mon marteau et moi, on s’occupera des serrures.')
  end
  regarder_lieu_ville(hero, partenaire, Direction.UpLeft)
  animer_fond(500, 1010)
  GAME:MoveCamera(500, 1010, 300, false)
  parler_guide('Normal', 'Et de l’autre côté de la place, d’autres comptoirs nous attendent. Nous aurons le temps de les découvrir ensemble.')
  if alakazam ~= nil then
    animer_fond(360, 1100)
    GAME:MoveCamera(360, 1100, 90, false)
    parler_guide('Normal', 'Ici, Alakazam aide les Pokémon à retrouver des capacités oubliées.')
    GAME:WaitFrames(20)
    parler_guide('Worried', 'Tiens… il n’est pas à son comptoir. C’est étrange, il est pourtant toujours là à cette heure-ci.')
  end
  if mordudor ~= nil then
    animer_fond(504, 1040)
    GAME:MoveCamera(504, 1040, 80, false)
    parler_guide('Normal', 'Et voici Écu, le Mordudor qui veille sur notre argent à la banque.')
    GROUND:CharAnimateTurnTo(mordudor, Direction.Down, 4)
    parler_accueil(mordudor, 'Happy', 'Des pièces, des pièces ! Confiez-moi vos Poké : je les garderai en sécurité.')
  end
  -- La visite reste dans le centre : les autres quartiers seront découverts plus tard.
  animer_fond(PLACE_X, PLACE_Y)
  GAME:MoveCamera(PLACE_X, PLACE_Y, 175, false)
  guide_hors_champ = false
  geste_heros(hero, 'autour', partenaire)
  se_faire_face_ville(partenaire, hero)
  parler_guide('Normal', 'Tu ne te souviens toujours pas de ton passé, mais tu commences à trouver tes repères. Ça se voit.')
  parler_guide('Happy', 'Tu n’as pas besoin de tout retenir d’un coup. On explorera la ville et les alentours à notre rythme.')
  parler_guide('Normal', 'Pour l’instant, reposons-nous. Notre prochaine aventure commencera quand nous serons prêts.')

  -- La ville entend un cri avant d'en voir l'origine.
  GAME:WaitFrames(30)
  GAME:MoveCamera(832, 1208, 50, false)
  local temoins = temoins_de_la_visite(map, hero, partenaire, alakazam)
  -- Le cri fait entrer les passants dans la scène ; arrêter leur idle avant
  -- leurs réactions, sans toucher à leur IA ni à leurs positions.
  arreter_fond()
  -- Laisser le thème de ville se terminer avant le cri, sans remplacer brutalement un morceau.
  SOUND:FadeOutBGM(45)
  GAME:WaitFrames(55)
  UI:SetSpeaker('???', true, '', -1, '', RogueEssence.Data.Gender.Unknown)
  UI:WaitShowDialogue('À l’aide ! Quelqu’un… au secours !')
  GAME:WaitFrames(20)
  SOUND:PlayBGM('Threat.ogg', false)
  reagir_ville(temoins, hero, partenaire, 'cri')
  regarder_alerte(temoins)
  regarder_lieu_ville(hero, partenaire, Direction.Down)
  parler_guide('Worried', 'Vous avez entendu ? D’où ça venait ?')
  GAME:WaitFrames(16)
  if lombre ~= nil then
    GROUND:CharAnimateTurnTo(lombre, Direction.Down, 4)
    parler_accueil(lombre, 'Worried', 'Cette voix… On dirait Lyra, la Luxray !')
  end
  if ludicolo ~= nil then
    GROUND:CharAnimateTurnTo(ludicolo, Direction.Down, 4)
    parler_accueil(ludicolo, 'Worried', 'Ça venait du sud !')
  end
  GAME:WaitFrames(20)
  local luxray = CH('NewObject_9')
  local luxray_temporaire = luxray == nil
  local luxray_depart = nil
  if luxray ~= nil then
    luxray_depart = {x=luxray.Position.X, y=luxray.Position.Y, dir=luxray.Direction}
    AI:DisableCharacterAI(luxray)
    GROUND:TeleportTo(luxray, 800, 1328, Direction.Up)
  else
    luxray = habitant('Luxray_Alerte', 'luxray', Gender.Female, 800, 1328)
    if luxray.Data ~= nil then luxray.Data.Nickname = 'Lyra' end
  end
  -- La course commence hors du cadre et s'arrête avant le groupe.
  GROUND:MoveToPosition(luxray, 800, 1224, true, 2)
  GROUND:CharAnimateTurnTo(luxray, Direction.Up, 4)
  GROUND:CharSetEmote(luxray, 'sweating', 2)
  -- À l'arrivée, les proches cherchent Lyra du regard, en décalé.
  ecouter_scene(luxray, partenaire, hero, lombre, ludicolo, roserade, tyranocif_accueil, dracaufeu)
  GAME:WaitFrames(20)
  parler_accueil(luxray, 'Worried', 'Hah… Hah… S’il vous plaît… Mon petit !')
  GAME:WaitFrames(20)
  parler_guide('Worried', 'Lyra ? Qu’est-ce qui s’est passé ?')
  GAME:WaitFrames(16)
  GROUND:CharTurnToCharAnimated(luxray, partenaire, 4)
  parler_accueil(luxray, 'Worried', 'Nous étions ensemble… Il a glissé avant que je puisse le retenir !')
  parler_accueil(luxray, 'Sad', 'Mon petit Nilo est tombé dans un fossé. Je l’entends encore en bas…')
  GAME:WaitFrames(16)
  parler_accueil(luxray, 'Worried', 'J’ai essayé de descendre le rejoindre, mais le passage est trop dangereux. Je n’arrive pas jusqu’à lui…')
  GAME:WaitFrames(20)
  reagir_ville(temoins, hero, partenaire, 'shinx')
  GAME:WaitFrames(10)
  parler_accueil(luxray, 'Worried', 'La guilde… Je vous en prie, demandez à la guilde de venir nous aider !')
  GAME:WaitFrames(22)
  if lombre ~= nil then
    ecouter_scene(lombre, luxray, partenaire, hero, ludicolo, roserade, tyranocif_accueil, dracaufeu)
    GROUND:CharTurnToCharAnimated(lombre, luxray, 4)
    parler_accueil(lombre, 'Worried', 'Les membres de la guilde sont partis en expédition… Ils ne sont pas encore revenus.')
  end
  if ludicolo ~= nil then
    ecouter_scene(ludicolo, luxray, partenaire, hero, lombre, roserade, tyranocif_accueil, dracaufeu)
    GROUND:CharTurnToCharAnimated(ludicolo, luxray, 4)
    parler_accueil(ludicolo, 'Worried', 'On ne peut pas attendre leur retour…')
  end
  GAME:WaitFrames(20)
  local tyranocif = CH('NewObject_14')
  if tyranocif ~= nil then
    GROUND:CharTurnToCharAnimated(tyranocif, luxray, 4)
    parler_accueil(tyranocif, 'Worried', 'Où est-ce que Nilo est tombé, Lyra ?', 'droite')
  end
  if dracaufeu ~= nil then
    GROUND:CharTurnToCharAnimated(dracaufeu, luxray, 4)
    parler_accueil(dracaufeu, 'Normal', 'Est-ce que tu peux nous montrer le chemin ?', 'droite')
  end
  GAME:WaitFrames(16)
  parler_accueil(luxray, 'Worried', 'Oui ! Je vous indiquerai le chemin… Mais faites vite, je vous en prie !')
  GAME:WaitFrames(20)
  GROUND:CharTurnToCharAnimated(partenaire, luxray, 4)
  ecouter_scene(partenaire, luxray, hero, lombre, ludicolo, roserade, tyranocif, dracaufeu)
  parler_guide('Determined', 'On va l’aider ! Nous pouvons y aller, nous aussi !')
  geste_heros(hero, 'oui', partenaire)
  GAME:WaitFrames(16)
  if tyranocif ~= nil then
    ecouter_scene(tyranocif, dracaufeu, partenaire, hero, luxray, lombre, ludicolo)
    GROUND:CharTurnToCharAnimated(tyranocif, dracaufeu or partenaire, 4)
    parler_accueil(tyranocif, 'Normal', 'Dracaufeu… On pourrait reformer notre ancienne équipe, avec Alakazam.', 'droite')
  end
  if dracaufeu ~= nil then
    GROUND:CharTurnToCharAnimated(dracaufeu, tyranocif or partenaire, 4)
    parler_accueil(dracaufeu, 'Normal', 'Oui. Tous les trois, nous avons déjà affronté bien des dangers.', 'droite')
  end
  -- Recentrer le groupe avant de préparer une entrée par la gauche.
  GAME:WaitFrames(30)
  -- 320 px de large : x=840 garde le point d'arrivée x=720 dans le plan,
  -- et place le départ x=648 à gauche du cadre (sprite à vérifier en jeu).
  GAME:MoveCamera(840, 1208, 45, false)
  GAME:WaitFrames(15)
  if alakazam ~= nil then
    -- Position préparée masquée, puis marche dans l'axe de la place.
    GROUND:TeleportTo(alakazam, 648, 1152, Direction.Right)
    GROUND:Unhide('NewObject_4')
    GROUND:MoveToPosition(alakazam, 720, 1152, false, 1.5)
    GROUND:CharAnimateTurnTo(alakazam, Direction.Right, 4)
    ecouter_scene(alakazam, tyranocif, dracaufeu, partenaire, hero, luxray, lombre, ludicolo, roserade)
    GAME:WaitFrames(30)
    parler_accueil(alakazam, 'Normal', 'Laisse donc ces jeunes y aller, mon vieil ami.')
    GAME:WaitFrames(30)
    parler_accueil(alakazam, 'Normal', 'Ils ont entendu Lyra et se sont proposés sans hésiter. Laissons-leur cette chance.')
    GAME:WaitFrames(16)
    ecouter_scene(partenaire, alakazam, hero, luxray, tyranocif, dracaufeu, lombre, ludicolo, roserade)
    GROUND:CharTurnToCharAnimated(partenaire, alakazam, 4)
    parler_guide('Determined', 'Nous ferons de notre mieux. Nilo ne restera pas seul !')
    GAME:WaitFrames(20)
    -- Lyra baisse un instant les yeux avant de remercier l'équipe.
    GROUND:CharAnimateTurnTo(luxray, Direction.Down, 4)
    GAME:WaitFrames(16)
    ecouter_scene(luxray, partenaire, hero, alakazam, lombre, ludicolo)
    GROUND:CharTurnToCharAnimated(luxray, partenaire, 4)
    parler_accueil(luxray, 'Sad', 'Merci… Je vous en prie, ramenez mon petit.')
    GAME:WaitFrames(20)
    ecouter_scene(alakazam, partenaire, hero, luxray)
    GROUND:CharTurnToCharAnimated(alakazam, partenaire, 4)
    parler_accueil(alakazam, 'Normal', 'Préparez-vous bien et écoutez les indications de Lyra. Nous resterons ici si vous avez besoin de nous.')
  else
    GAME:WaitFrames(20)
    ecouter_scene(luxray, partenaire, hero, tyranocif, dracaufeu)
    GROUND:CharTurnToCharAnimated(luxray, partenaire, 4)
    parler_accueil(luxray, 'Sad', 'Merci… Je vous en prie, ramenez mon petit.')
    ecouter_scene(partenaire, luxray, hero, tyranocif, dracaufeu)
    GROUND:CharTurnToCharAnimated(partenaire, luxray, 4)
    parler_guide('Determined', 'Nous ferons de notre mieux. Nilo ne restera pas seul !')
  end
  -- Lombre ne disparaît pas de l'échange une fois les aînés intervenus.
  if lombre ~= nil and lombre.EntEnabled ~= false then
    GAME:WaitFrames(12)
    ecouter_scene(lombre, luxray, partenaire, hero, ludicolo)
    GROUND:CharTurnToCharAnimated(lombre, luxray, 4)
    parler_accueil(lombre, 'Worried', 'Courage, Lyra. Nous pensons tous à Nilo.')
  end
  GAME:WaitFrames(30)
  -- Fin progressive de la tension ; aucune musique de victoire avant le sauvetage.
  SOUND:FadeOutBGM(90)
  GAME:WaitFrames(100)
  -- La caméra s'éloigne avant la remise en place hors champ. Le joueur
  -- retrouve ensuite caméra, IA et musique habituelle de la ville.
  GAME:MoveCamera(1000, 1160, 70, false)
  -- Les habitants repartent hors champ. Contrôler à nouveau chaque segment :
  -- un obstacle apparu entre-temps ne doit jamais bloquer la cinématique.
  for _, depart in ipairs(avances) do
    local acteur, points = depart.acteur, depart.points
    if acteur ~= nil and acteur.EntEnabled ~= false then
      for i = #points, 2, -1 do
        if acteur.Position.X == points[i][1] and acteur.Position.Y == points[i][2]
          and passage_libre(acteur, {points[i], points[i-1]}) then
          GROUND:MoveToPosition(acteur, points[i-1][1], points[i-1][2], false, 1)
        end
      end
      if acteur.Position.X == depart.x and acteur.Position.Y == depart.y then
        GROUND:EntTurn(acteur, depart.dir)
      end
    end
  end
  if alakazam ~= nil then
    GROUND:Hide('NewObject_4')
    GROUND:TeleportTo(alakazam, 360, 1100, Direction.Down)
    GROUND:Unhide('NewObject_4')
  end
  if not luxray_temporaire and luxray_depart ~= nil then
    GROUND:TeleportTo(luxray, luxray_depart.x, luxray_depart.y, luxray_depart.dir)
  end
  -- Après un temps de silence, revenir au thème du quartier, sans superposition.
  GAME:WaitFrames(30)
  SOUND:PlayBGM('Treasure Town.ogg', false)
  -- Ce drapeau ne crée pas de mission ni de donjon automatiquement.
  SV.Destiny.AlerteShinx = 'a_secourir'
  SV.Destiny.LuxrayAttente = 'place'
  SV.Destiny.VisiteVille = 'terminee'
  parler_guide('Normal', 'On peut passer chez Basil et Félix pour les courses, puis chez Mado pour déposer les objets des Bois Perdus. Ce n’est pas obligatoire : rejoignons Lyra quand nous serons prêts.')
  UI:ResetSpeaker()
  retour_au_joueur(hero, partenaire)
end

local function position_partenaire_retour(x, y)
  local p = SV.Destiny.RetourBatimentPartenaire
  if p ~= nil and p.x == x and p.y == y then return p.px, p.py end
  return x-28, y
end

local function rediriger_ancienne_ville(map, hero, partenaire)
  if map == nil or hero == nil then return false end
  if changement_quartier then return true end
  -- Ancienne carte nord : rejoindre la carte fusionnée sans perdre la position.
  if map.AssetName == 'reverie_nord' then
    local x,y = hero.Position.X,hero.Position.Y
    local px,py = x-28,y
    local dir = 'Down'
    if partenaire ~= nil then px,py = partenaire.Position.X,partenaire.Position.Y end
    local ancien_passage = SV.Destiny.PassageQuartier
    if ancien_passage ~= nil then
      x,y,px,py,dir = ancien_passage.x,ancien_passage.y,ancien_passage.px,ancien_passage.py,ancien_passage.dir or 'Down'
    end
    if not case_libre(map,x,y) then return false end
    demander_quartier('reverie_centre',x,y,px,py,dir)
    return true
  end
  if map.AssetName ~= 'WaterfallVillageCapital' then return false end
  local x,y = hero.Position.X, hero.Position.Y
  local px,py = x-28,y
  if partenaire ~= nil then px,py = partenaire.Position.X,partenaire.Position.Y end
  if SV.Destiny.ArriveeVille == 'cafe' then
    x,y,px,py = 1080,1360,1052,1360
  elseif SV.Destiny.ArriveeVille == 'batiment' then
    x,y = SV.Destiny.RetourBatimentX or PLACE_X, SV.Destiny.RetourBatimentY or PLACE_Y
    px,py = position_partenaire_retour(x,y)
  elseif x == 0 and y == 0 then
    x,y,px,py = PLACE_X,PLACE_Y,PLACE_X-28,PLACE_Y
  end
  -- Ne pas déplacer une ancienne sauvegarde depuis une position déjà bloquée.
  if not case_libre(map,x,y) then return false end
  local destination = quartier_pour(x+8,y+8)
  -- Une ancienne sauvegarde à cheval sur une frontière reste sur la carte
  -- historique : ne jamais déplacer son héros à travers la rivière.
  for cx=math.floor(x/8),math.floor((x+15)/8) do
    for cy=math.floor(y/8),math.floor((y+15)/8) do
      if quartier_pour(cx*8+4,cy*8+4) ~= destination then return false end
    end
  end
  SV.Destiny.ArriveeVille = nil
  SV.Destiny.RetourBatimentPartenaire = nil
  demander_quartier(destination,x,y,px,py,'Down')
  return true
end

local function entrer(map)
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.VisiteVille == 'en_route' then
    ville.Visite(map)
    if SV.Destiny.VisiteVille == 'terminee' then
      local hero = CH('PLAYER')
      rediriger_ancienne_ville(map, hero, partenaire_pour(hero))
    end
    return
  end
  local hero = CH('PLAYER')
  local partenaire = partenaire_pour(hero)
  if rediriger_ancienne_ville(map,hero,partenaire) then return end
  local passage = SV.Destiny.PassageQuartier
  if passage ~= nil then
    SV.Destiny.PassageQuartier = nil
    local dir = passage.dir == 'Up' and Direction.Up or Direction.Down
    if hero ~= nil then
      local x,y = case_proche(map, passage.x, passage.y)
      GROUND:TeleportTo(hero,x,y,dir)
    end
    if partenaire ~= nil then
      local x,y = case_proche(map, passage.px, passage.py)
      GROUND:TeleportTo(partenaire,x,y,dir)
    end
  elseif hero ~= nil and hero.Position.X == 0 and hero.Position.Y == 0 then
    GROUND:TeleportTo(hero, PLACE_X, PLACE_Y, Direction.Up)
  end
  if SV.Destiny.ArriveeVille == 'cafe' or SV.Destiny.ArriveeVille == 'batiment' then
    local arrivee_x, arrivee_y = 1080,1360
    if SV.Destiny.ArriveeVille == 'batiment' then
      arrivee_x = SV.Destiny.RetourBatimentX or PLACE_X
      arrivee_y = SV.Destiny.RetourBatimentY or PLACE_Y
    end
    local retour_batiment = SV.Destiny.ArriveeVille == 'batiment'
    SV.Destiny.ArriveeVille = nil
    if hero ~= nil then GROUND:TeleportTo(hero, arrivee_x, arrivee_y, Direction.Down) end
    if partenaire ~= nil then
      local px,py = position_partenaire_retour(arrivee_x,arrivee_y)
      if not retour_batiment then px,py = arrivee_x-28,arrivee_y end
      GROUND:TeleportTo(partenaire, px, py, Direction.Down)
    end
    SV.Destiny.RetourBatimentPartenaire = nil
  end
  SOUND:PlayBGM('Treasure Town.ogg', true)
  GAME:FadeIn(20)
  retour_au_joueur(hero, partenaire)
end

function ville.Enter(map) entrer(map) end
function ville.GameLoad(map)
  entree_batiment_en_cours = false
  -- Une ancienne sauvegarde peut contenir l'ancienne instance du centre :
  -- le moteur initialise l'instance sauvegardée avant cet événement. Une
  -- entrée normale recharge la carte publiée et ses personnages d'origine.
  -- Cette migration ne s'applique qu'au chargement, jamais aux visites normales.
  if map ~= nil and map.AssetName == 'reverie_centre' then
    local ancien_masque = map:GetObstacle(15,101) ~= 0
    local habitants_manquants = map:GetMapChar('NewObject_6') == nil
      or map:GetMapChar('Doyen') == nil or map:GetMapChar('Drifloon') == nil
    if ancien_masque or habitants_manquants then
      SV.Destiny = SV.Destiny or {}
      local hero = CH('PLAYER')
      if hero ~= nil then
        local partenaire = partenaire_pour(hero)
        local x,y = hero.Position.X,hero.Position.Y
        local px,py = x-28,y
        if partenaire ~= nil then px,py = partenaire.Position.X,partenaire.Position.Y end
        local dir = hero.Direction == Direction.Up and 'Up' or 'Down'
        local passage = SV.Destiny.PassageQuartier
        if passage ~= nil then
          x,y,px,py,dir = passage.x,passage.y,passage.px,passage.py,passage.dir or 'Down'
        end
        demander_quartier('reverie_centre',x,y,px,py,dir)
        return
      end
    end
  end
  installer_portes(map)
  installer_comptoirs(map)
  installer_luxray_attente(map)
  nommer_habitants(map)
  placer_marchands_aux_comptoirs()
  if CH('NewObject_4') ~= nil then GROUND:Unhide('NewObject_4') end
  entrer(map)
end
function ville.Exit(map) end
function ville.Update(map, time) tic_ambiance() end


-- Ambiance vivante (non bloquante) : les marchands s'animent comme dans la
-- ville de base PMDO (émotes périodiques) et des paires d'habitants
-- discutent entre eux par émotes, en se tournant l'un vers l'autre.
-- Les paires et les gestes tournent avec le temps… et avec le jour courant.
local horloge_ambiance = 0
local function geste_ambiance(nom, emote)
  local acteur = CH(nom)
  if acteur == nil then return end
  pcall(function()
    if acteur.IsInteracting then return end
    GROUND:CharSetEmote(acteur, emote, 1)
  end)
end
local function discussion_ambiance(cycle)
  local paire = paires_discussion[((cycle + jour_actuel()) % #paires_discussion) + 1]
  local a1, a2 = CH(paire[1]), CH(paire[2])
  if a1 == nil or a2 == nil then return end
  -- Ne jamais détourner du joueur un PNJ déjà en interaction.
  if a1.IsInteracting or a2.IsInteracting then return end
  orienter_discussion(paire[1])
  GROUND:CharSetAnim(a1, 'Idle', true)
  GROUND:CharSetAnim(a2, 'Idle', true)
  if cycle % 2 == 0 then
    geste_ambiance(paire[1], 'question')
    geste_ambiance(paire[2], 'happy')
  else
    geste_ambiance(paire[1], 'happy')
    geste_ambiance(paire[2], 'glowing')
  end
end
local function tic_ambiance()
  if not vie_ville_activee then return end
  horloge_ambiance = horloge_ambiance + 1
  if horloge_ambiance % 540 == 0 then
    local cycle = math.floor(horloge_ambiance / 540) % 6
    if cycle == 0 then
      geste_ambiance('Kecleon', 'happy')
      geste_ambiance('Kecleon_Violet', 'glowing')
    elseif cycle == 1 then geste_ambiance('Kangourex', 'happy')
    elseif cycle == 2 then geste_ambiance('NewObject_24', 'exclaim')
    elseif cycle == 3 then geste_ambiance('NewObject_4', 'glowing')
    elseif cycle == 4 then geste_ambiance('NewObject_3', 'glowing')
    else geste_ambiance('Kecleon_Violet', 'exclaim') end
  end
  if horloge_ambiance % 900 == 0 then
    discussion_ambiance(math.floor(horloge_ambiance / 900))
  end
end

function ville.SortieCarrefour_Touch(obj, activator)
  -- Le premier trajet scénarisé et la visite guidée restent inchangés.
  if SV.Destiny == nil or SV.Destiny.VisiteVille ~= 'terminee' then return end
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('reverie', 'crossroadreverietown2', 'entree_ville')
end

-- La seule zone de donjon publiée et raccordée par Destiny à ce jour.
-- Ne pas intégrer ici les combats narratifs, les cartes de test ou Halcyon.
local destinations_reverie = {'lost_wood'}

local function missions_par_donjon()
  local dests = {}
  if SV.TakenBoard ~= nil then
    for i = 1, 8 do
      local mission = SV.TakenBoard[i]
      if mission ~= nil and mission.Taken and mission.Zone ~= nil and mission.Zone ~= '' then
        dests[mission.Zone] = true
      end
    end
  end
  local mission = missions_reverie.Actuelle()
  if mission ~= nil and mission.Etat == 'en_cours' then dests[mission.Zone] = true end
  return dests
end

function ville.SortieExplorationE2_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  SV.Destiny = SV.Destiny or {}
  -- Le retour des Bois Perdus a déjà été accompli dans l'histoire.
  if SV.Destiny.RetourAccompli and not GAME:DungeonUnlocked('lost_wood') then
    GAME:UnlockDungeon('lost_wood')
  end
  -- Sans zone Grotte Verdoyante, ne pas fabriquer un ZoneLoc inexistant.
  if SV.Destiny.AlerteShinx == 'a_secourir' and SV.Destiny.DepartShinxAccepte then
    UI:ResetSpeaker()
    UI:BeginChoiceMenu('Choisir une destination', {
      STRINGS:Format('\\uE111 ') .. 'Grotte Verdoyante', 'Autres donjons', 'Retour',
    }, 1, 3)
    UI:WaitForChoice()
    local selection = UI:ChoiceResult()
    if selection == 1 then
      UI:ResetSpeaker()
      UI:WaitShowDialogue('La Grotte Verdoyante n’est pas encore disponible dans cette version.')
      return
    elseif selection ~= 2 then
      return
    end
  end
  local missions = missions_par_donjon()
  local histoire = SV.Destiny.DonjonHistoireCourant
  if histoire == nil and SV.ChapterProgression ~= nil then
    histoire = SV.ChapterProgression.CurrentStoryDungeon
  end
  local destinations = {}
  for _, id in ipairs(destinations_reverie) do
    if GAME:DungeonUnlocked(id) then
      local resume = _DATA.DataIndices[RogueEssence.Data.DataManager.DataType.Zone]:Get(id)
      local titre = resume:GetColoredName()
      local libelle = titre
      if id == histoire then
        libelle = STRINGS:Format('\\uE111 ') .. titre
      elseif missions[id] then
        libelle = STRINGS:Format('\\uE10F ') .. titre
      end
      table.insert(destinations, {Name=libelle, Title=titre, Dest=RogueEssence.Dungeon.ZoneLoc(id, 0, 0, 0), Id=id})
    end
  end
  UI:ResetSpeaker()
  if #destinations == 0 then
    UI:WaitShowDialogue('Aucun donjon accessible pour le moment.')
    return
  end
  UI:DestinationMenu(destinations, 1)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == nil or destinations[choix] == nil then return end
  local destination = destinations[choix]
  UI:ChoiceMenuYesNo('Partir vers ' .. destination.Title .. ' ?', true)
  UI:WaitForChoice()
  if not UI:ChoiceResult() then return end
  SV.Destiny.ExplorationReverie = true
  SOUND:FadeOutBGM(20)
  GAME:FadeOut(false, 20)
  GAME:EnterDungeon(destination.Id, 0, 0, 0, RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)
end

function ville.TableauReverieNord_Action(obj, activator) missions_reverie.OuvrirTableau() end
function ville.TableauReverieCentre_Action(obj, activator) missions_reverie.OuvrirTableau() end

function ville.PorteCafeSpinda_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if entree_batiment_en_cours then return end
  entree_batiment_en_cours = true
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 2, 0)
end

for _, porte_def in ipairs(portes_batiments) do
  local porte = porte_def
  local function entrer_batiment()
    if entree_batiment_en_cours then return end
    entree_batiment_en_cours = true
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.RetourBatimentX = porte.retour_x
    SV.Destiny.RetourBatimentY = porte.retour_y
    SV.Destiny.RetourBatimentPartenaire = {x=porte.retour_x, y=porte.retour_y, px=porte.partenaire_x or porte.retour_x-28, py=porte.partenaire_y or porte.retour_y}
    GAME:FadeOut(false, 20)
    GAME:EnterGroundMap('town02_waterfallvillage', porte.interieur, porte.marqueur)
  end
  if porte.contact_x ~= nil then
    ville[porte.nom .. '_Touch'] = function(obj, activator)
      if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
      entrer_batiment()
    end
  else
    -- Les deux associations des tentes sont conservées à titre historique,
    -- sans les rendre automatiques avant confirmation de leur destination.
    ville[porte.nom .. '_Action'] = function(obj, activator)
      UI:ResetSpeaker()
      UI:ChoiceMenuYesNo('Entrer : ' .. porte.titre .. ' ?', true)
      UI:WaitForChoice()
      if UI:ChoiceResult() then entrer_batiment() end
    end
  end
end

-- Interagir devant un comptoir revient à s’adresser au marchand posté
-- derrière : même dialogue et même service que l’Action du personnage.
for _, comptoir_def in ipairs(comptoirs) do
  local comptoir = comptoir_def
  ville[comptoir.nom .. '_Action'] = function(obj, activator)
    local marchand = CH(comptoir.marchand)
    local action = ville[comptoir.marchand .. '_Action']
    if marchand ~= nil and action ~= nil then action(marchand, activator) end
  end
end

-- Actualité tant que Nilo attend du secours. Le départ accepté ne signifie
-- pas que le donjon a été parcouru ou que le sauvetage est terminé.
local nouvelles_nilo = {
  Kangourex = 'Lyra m’a parlé de Nilo. Je peux garder ce qui vous encombre pendant que vous vous préparez.',
  Kecleon = 'Pour rejoindre Nilo, vérifiez vos provisions. Mes baies et mes pommes sont là si besoin.',
  Kecleon_Violet = 'Lyra attend de vos nouvelles. Regardez mes articles avant de partir, si cela peut vous aider.',
  NewObject_3 = 'Pour Nilo, préparez-vous d’abord ! Je garde vos Poké en sécurité si vous en avez besoin.',
  NewObject_4 = 'Lyra compte sur vous. Gardez la tête froide et écoutez ses indications sur le chemin.',
  NewObject_24 = 'Je pense à Nilo. Si vos préparatifs vous amènent à la forge, je suis là.',
  NewObject_6 = 'J’ai entendu le cri de Lyra depuis la place… J’espère que Nilo tient bon.',
  NewObject_12 = 'Si Lyra a besoin de matériel pour Nilo, je peux aider à porter les caisses.',
  NewObject_13 = 'Je regarderai la route. J’espère voir bientôt Lyra et Nilo revenir ensemble.',
  NewObject_14 = 'Alakazam vous fait confiance. Vérifiez votre sac, puis suivez Lyra jusqu’à Nilo.',
  NewObject_16 = 'Je reste ici avec les autres. Soyez prudents en allant chercher Nilo.',
  NewObject_15 = 'Pauvre Lyra… J’espère que Nilo l’entend quand elle l’appelle.',
  NewObject_22 = 'Un passage dangereux ? Restez ensemble et écoutez bien Lyra.',
  NewObject_23 = 'Je garde mes décorations pour plus tard. Pour l’instant, je pense à Nilo.',
  Pijako_Livreur = 'Si des nouvelles de Nilo arrivent, je les porterai aussi vite que possible.',
  Goinfrex_Voyageur = 'Même moi, je pense à autre chose qu’au goûter. J’espère que Nilo va bien.',
}
local function reaction_actualite(personnage, nom)
  if SV.Destiny == nil or SV.Destiny.AlerteShinx ~= 'a_secourir' or personnage == nil then return false end
  local phrase = nouvelles_nilo[nom] or 'Tout le monde pense à Lyra et à Nilo. Soyez prudents sur le chemin.'
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Worried')
  UI:WaitShowDialogue(phrase)
  UI:ResetSpeaker()
  return true
end

-- Les habitants sont visibles pendant la visite et restent utilisables après.
-- Kangourex ne garde que les objets : dépôt et retrait, jamais l'argent.
-- La banque est assurée par Gimmighoul (NewObject_3), plus bas.
function ville.Kangourex_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'Kangourex')
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Bienvenue, mes petits. Je garde vos objets bien au sec, loin des donjons.')
  while true do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion('Normal')
    UI:BeginChoiceMenu('Souhaitez-vous déposer ou retirer des objets ?', {
      'Déposer des objets', 'Retirer des objets', 'Quitter',
    }, 1, 3)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 1 then
      UI:ResetSpeaker()
      UI:StorageMenu()
      UI:WaitForChoice()
    elseif choix == 2 then
      UI:ResetSpeaker()
      UI:WithdrawMenu()
      UI:WaitForChoice()
    else
      break
    end
  end
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Vos affaires vous attendront ici. Revenez quand vous voulez.')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'Kangourex')
end

-- Petits assortiments de départ : menus, argent et sac sont ceux de PMDO.
-- Les deux frères Kecleon ne proposent pas les mêmes marchandises.
local assortiments_kecleon_vert = {
  {{id = 'food_apple', prix = 50}, {id = 'berry_oran', prix = 80}, {id = 'berry_leppa', prix = 80}},
  {{id = 'food_apple_big', prix = 100}, {id = 'berry_pecha', prix = 80}, {id = 'berry_chesto', prix = 80}},
  {{id = 'food_banana', prix = 100}, {id = 'berry_lum', prix = 150}, {id = 'berry_persim', prix = 80}},
}
local assortiments_kecleon_violet = {
  {{id = 'berry_sitrus', prix = 150}, {id = 'medicine_elixir', prix = 300}, {id = 'seed_reviver', prix = 800}},
  {{id = 'medicine_max_elixir', prix = 650}, {id = 'orb_escape', prix = 300}, {id = 'seed_joy', prix = 1200}},
  {{id = 'medicine_max_potion', prix = 500}, {id = 'orb_scanner', prix = 300}, {id = 'seed_pure', prix = 400}},
}

-- Stock du jour, persisté dans la sauvegarde : les achats épuisent l'étal,
-- et la sieste au café Spinda fait passer à l'assortiment suivant.
local function stock_kecleon(cle, assortiments, decalage)
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.StocksKecleon = SV.Destiny.StocksKecleon or {}
  local jour = SV.Destiny.JourneeVille or 0
  local stock = SV.Destiny.StocksKecleon[cle]
  if stock == nil or stock.Jour ~= jour then
    stock = {Jour = jour, Articles = {}}
    local assortiment = assortiments[((jour + decalage) % #assortiments) + 1]
    for _, article in ipairs(assortiment) do
      table.insert(stock.Articles, {Index = article.id, Amount = 1, Price = article.prix})
    end
    SV.Destiny.StocksKecleon[cle] = stock
  end
  return stock
end

local function ouvrir_boutique(personnage, cle, assortiments, decalage, accueil)
  local stock = stock_kecleon(cle, assortiments, decalage)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue(accueil)
  UI:WaitShowDialogue('Mon assortiment change chaque jour. Après une sieste au café Spinda, revenez voir le nouvel étal !')
  while true do
    UI:SetSpeaker(personnage)
    if #stock.Articles == 0 then
      UI:WaitShowDialogue('Mon étal du jour est épuisé. Revenez demain !')
      break
    end
    local catalogue = {}
    for _, article in ipairs(stock.Articles) do
      table.insert(catalogue, {
        Item = RogueEssence.Dungeon.InvItem(article.Index, false, article.Amount),
        Price = article.Price,
      })
    end
    UI:ShopMenu(catalogue)
    UI:WaitForChoice()
    local panier = UI:ChoiceResult()
    if panier == nil or #panier == 0 then break end
    UI:SetSpeaker(personnage)
    if GAME:GetPlayerBagCount() >= GAME:GetPlayerBagLimit() then
      UI:WaitShowDialogue('Votre sac est plein. Faites un peu de place avant de revenir.')
    else
      local total = 0
      for ii = 1, #panier do total = total + catalogue[panier[ii]].Price end
      if total > GAME:GetPlayerMoney() then
        UI:WaitShowDialogue('Il vous manque un peu d’argent pour tout cela.')
      else
        UI:ChoiceMenuYesNo('Acheter pour ' .. total .. ' Poké ?', false)
        UI:WaitForChoice()
        if UI:ChoiceResult() then
          GAME:RemoveFromPlayerMoney(total)
          for ii = 1, #panier do
            local objet = catalogue[panier[ii]].Item
            GAME:GivePlayerItem(objet.ID, objet.Amount, false)
          end
          for ii = #panier, 1, -1 do table.remove(stock.Articles, panier[ii]) end
          SOUND:PlayBattleSE('DUN_Money')
          UI:SetSpeaker(personnage)
          UI:WaitShowDialogue('Merci ! Prenez soin de vous sur les chemins.')
        end
      end
    end
  end
  UI:ResetSpeaker()
end

function ville.Kecleon_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'Kecleon')
  ouvrir_boutique(personnage, 'vert', assortiments_kecleon_vert, 0,
    'Bienvenue à la boutique Kecleon ! Des provisions simples, mais qui ont sauvé plus d’une expédition.')
  terminer_dialogue(personnage, 'Kecleon')
end

function ville.Kecleon_Violet_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'Kecleon_Violet')
  ouvrir_boutique(personnage, 'violet', assortiments_kecleon_violet, 1,
    'Mon étal violet garde les articles précieux. Ils coûtent plus cher, mais ils peuvent changer une traversée.')
  terminer_dialogue(personnage, 'Kecleon_Violet')
end

-- Banque de Réverie Town : Mordudor sert les clients à son comptoir.
function ville.NewObject_3_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'NewObject_3')
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Des pièces, des pièces ! Je peux garder votre argent dans mon coffre et vous le rendre au Poké près.')
  UI:ResetSpeaker()
  UI:BankMenu()
  UI:WaitForChoice()
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Normal')
  UI:WaitShowDialogue('Votre trésor est compté. Mado garde les objets ; moi, je veille sur les Poké.')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_3')
end

local function dialogue_simple(personnage, repliques)
  for _, replique in ipairs(repliques) do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion(replique[1])
    UI:WaitShowDialogue(replique[2])
  end
  UI:ResetSpeaker()
end

local function conversation(acteurs, repliques)
  -- Les deux partenaires de discussion restent animés même lorsqu'un seul parle.
  for i = 1, 2 do
    local acteur = acteurs[i]
    if acteur ~= nil then GROUND:CharSetAnim(acteur, 'Idle', true) end
  end
  for _, replique in ipairs(repliques) do
    local acteur = acteurs[replique[1]]
    if acteur ~= nil then
      UI:SetSpeaker(acteur)
      UI:SetSpeakerEmotion(replique[2])
      UI:WaitShowDialogue(replique[3])
    end
  end
  UI:ResetSpeaker()
  for i = 1, 2 do
    local acteur = acteurs[i]
    if acteur ~= nil then GROUND:CharEndAnim(acteur) end
  end
end

-- Alakazam : réapprendre une capacité oubliée (250 Poké) ou en oublier une
-- (gratuit), avec les menus natifs utilisés par le tuteur de PMDO.
local function alakazam_se_souvenir(personnage)
  local prix = 250
  if GAME:GetPlayerMoney() < prix then
    UI:SetSpeaker(personnage)
    UI:WaitShowDialogue('Il vous faut ' .. prix .. ' Poké pour éveiller un souvenir. Revenez quand votre bourse sera prête, elle aussi.')
    return
  end
  local etat, membre, capacite = 0, nil, ''
  while etat > -1 do
    if etat == 0 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Qui doit se souvenir d’une capacité ?')
      local choisi = AssemblySelectMenu.run(function(m) return GAME:CanRelearn(m) end, false)
      if choisi ~= nil then membre, etat = choisi, 1 else etat = -1 end
    elseif etat == 1 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Quelle capacité ' .. membre:GetDisplayName(true) .. ' doit-il retrouver ?')
      local resultat = SkillSelectMenu.runRelearnMenu(membre)
      if resultat ~= '' then capacite, etat = resultat, 2 else etat = 0 end
    else
      local entree = _DATA:GetSkill(capacite)
      local appris = COMMON.LearnMoveFlow(membre, capacite,
        membre:GetDisplayName(true) .. ' doit oublier une capacité pour retrouver celle-ci.')
      if appris then
        SOUND:PlayBattleSE('DUN_Money')
        GAME:RemoveFromPlayerMoney(prix)
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Concentrez-vous… laissez le geste remonter, comme un rêve que l’on rattrape au réveil.')
        SOUND:PlayFanfare('Fanfare/LearnSkill')
        UI:WaitShowDialogue(membre:GetDisplayName(true) .. ' se souvient de ' .. entree:GetIconName() .. ' !')
        etat = -1
      else
        etat = 1
      end
    end
  end
end

local function alakazam_oublier(personnage)
  local etat, membre = 0, nil
  while etat > -1 do
    if etat == 0 then
      UI:SetSpeaker(personnage)
      UI:WaitShowDialogue('Qui doit oublier une capacité ?')
      local choisi = AssemblySelectMenu.run(function(m) return GAME:CanForget(m) end, false)
      if choisi ~= nil then
        membre, etat = choisi, 1
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Quelle capacité ' .. membre:GetDisplayName(true) .. ' doit-il laisser partir ?')
      else
        etat = -1
      end
    else
      UI:ForgetMenu(membre)
      UI:WaitForChoice()
      local resultat = UI:ChoiceResult()
      if resultat > -1 then
        local capacite = GAME:GetCharacterSkill(membre, resultat)
        local entree = _DATA:GetSkill(capacite)
        GAME:ForgetSkill(membre, resultat)
        UI:SetSpeaker(personnage)
        UI:WaitShowDialogue('Voilà… un geste s’efface, et l’esprit respire.')
        SOUND:PlayFanfare('Fanfare/LearnSkill')
        UI:WaitShowDialogue(membre:GetDisplayName(true) .. ' a oublié ' .. entree:GetIconName() .. '.')
        etat = -1
      else
        etat = 0
      end
    end
  end
end

function ville.NewObject_4_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'NewObject_4')
  dialogue_simple(personnage, {
    {'Normal', 'Une capacité oubliée n’est pas effacée : elle dort dans la mémoire du corps, en attendant un déclic.'},
  })
  UI:SetSpeaker(personnage)
  UI:BeginChoiceMenu('Puis-je vous aider ? Se souvenir coûte 250 Poké ; oublier est gratuit.', {
    'Se souvenir (250 Poké)', 'Oublier une capacité', 'Quitter',
  }, 1, 3)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix == 1 then alakazam_se_souvenir(personnage)
  elseif choix == 2 then alakazam_oublier(personnage) end
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_4')
end

-- Ouverture façon Tinkaton : elle se retourne vers le fond de son échoppe
-- extérieure, abat son marteau sur les boîtes, puis revient face au client.
-- Son Attack dure 36 ticks et sa frame d'impact (HitFrame 3) commence au
-- tick 16 : l'explosion et le tremblement d'écran natif PMDO (amplitude 12,
-- 30 ticks, celle de l'expertise de base) partent exactement à cet instant.
local function frapper_boites_forgelina(personnage)
  if personnage == nil then return end
  UI:ResetSpeaker()
  GROUND:CharAnimateTurnTo(personnage, Direction.Up, 4)
  GROUND:CharSetAnim(personnage, 'Attack', false)
  GAME:WaitFrames(16)
  GROUND:MoveScreen(RogueEssence.Content.ScreenMover(0, 12, 30))
  SOUND:PlayBattleSE('DUN_Explosion')
  GAME:WaitFrames(20)
  GROUND:CharEndAnim(personnage)
  GROUND:CharAnimateTurnTo(personnage, Direction.Down, 4)
end

-- Tinkaton : ouvrir les boîtes au trésor (150 Poké par boîte), avec le menu
-- natif d'expertise de PMDO.
function ville.NewObject_24_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  reaction_actualite(personnage, 'NewObject_24')
  local prix = 150
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Une boîte récalcitrante ? Rien ne résiste longtemps à mon marteau… ni à un peu de patience.')
  while true do
    UI:SetSpeaker(personnage)
    UI:SetSpeakerEmotion('Normal')
    UI:BeginChoiceMenu('J’ouvre vos boîtes pour ' .. prix .. ' Poké pièce. Que faire ?', {
      'Ouvrir des boîtes', 'Explications', 'Quitter',
    }, 1, 3)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 3 then
      break
    elseif choix == 2 then
      UI:WaitShowDialogue('Les explorateurs rapportent des boîtes scellées des donjons. Personne ne sait ce qu’elles contiennent avant ouverture.')
      UI:WaitShowDialogue('Choisissez vos boîtes, je m’occupe de la serrure. Le contenu vous revient, bien entendu.')
    else
      if GAME:GetPlayerBagCount() + GAME:GetPlayerEquippedCount() == 0 then
        UI:WaitShowDialogue('Votre sac est vide. Rapportez-moi une boîte d’un donjon, et nous verrons ce qu’elle cache.')
      else
        UI:WaitShowDialogue('Montrez-moi les boîtes à ouvrir.')
        UI:AppraiseMenu()
        UI:WaitForChoice()
        local panier = UI:ChoiceResult()
        if panier ~= nil and #panier > 0 then
          local total = #panier * prix
          if total > GAME:GetPlayerMoney() then
            UI:SetSpeaker(personnage)
            UI:WaitShowDialogue('Il vous manque des Poké pour ouvrir tout cela. Choisissez moins de boîtes, ou revenez plus riche.')
          else
            UI:SetSpeaker(personnage)
            UI:ChoiceMenuYesNo('Ouvrir ' .. #panier .. ' boîte(s) pour ' .. total .. ' Poké ?', false)
            UI:WaitForChoice()
            if UI:ChoiceResult() then
              local tresor = {}
              for ii = #panier, 1, -1 do
                local boite
                if panier[ii].IsEquipped then
                  boite = GAME:GetPlayerEquippedItem(panier[ii].Slot)
                  GAME:TakePlayerEquippedItem(panier[ii].Slot, true)
                else
                  boite = GAME:GetPlayerBagItem(panier[ii].Slot)
                  GAME:TakePlayerBagItem(panier[ii].Slot, true)
                end
                local objet_cache = boite.HiddenValue
                local entree = _DATA:GetItem(objet_cache)
                table.insert(tresor, {
                  Box = boite,
                  Item = RogueEssence.Dungeon.InvItem(objet_cache, false, entree.MaxStack),
                })
                if entree.Rarity > 0 and SV.unlocked_trades ~= nil then
                  SV.unlocked_trades[objet_cache] = true
                end
              end
              SOUND:PlayBattleSE('DUN_Money')
              GAME:RemoveFromPlayerMoney(total)
              UI:SetSpeaker(personnage)
              UI:SetSpeakerEmotion('Happy')
              UI:WaitShowDialogue('Reculez un peu… et voilà le travail !')
              frapper_boites_forgelina(personnage)
              SOUND:PlayFanfare('Fanfare/Treasure')
              UI:SpoilsMenu(tresor)
              UI:WaitForChoice()
              for ii = 1, #tresor do
                local objet = tresor[ii].Item
                GAME:GivePlayerItem(objet.ID, objet.Amount, false, objet.HiddenValue)
              end
            end
          end
        end
      end
    end
  end
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue('Chaque coffre a son secret. Revenez m’en montrer d’autres !')
  UI:ResetSpeaker()
  terminer_dialogue(personnage, 'NewObject_24')
end

local dialogues_lombre_ludicolo = {
  {
    {1, 'Normal', 'La cascade chante plus fort ce matin. Les ponts vont encore être glissants.'},
    {2, 'Happy', 'Alors dansons lentement en les traversant. Réverie Town récompense ceux qui gardent le rythme.'},
    {1, 'Happy', 'Facile à dire pour toi ! Mais je suivrai tes pas, comme toujours.'},
  },
  {
    {1, 'Normal', 'Les filaments de la rivière glissent tout seuls aujourd’hui. On dirait qu’elle respire.'},
    {2, 'Happy', 'Elle danse, mon ami ! Et quand la rivière danse, les poissons suivent la mesure.'},
    {1, 'Happy', 'Alors je lancerai ma ligne en rythme. Une-deux, une-deux…'},
  },
  {
    {1, 'Worried', 'Le marché était bondé ce matin. J’ai failli perdre une feuille dans la foule.'},
    {2, 'Happy', 'C’est la preuve que la ville vit ! Demain, nous irons tôt, avant les équipes.'},
    {1, 'Normal', 'D’accord. Mais c’est toi qui porteras les baies, cette fois.'},
  },
}
local function dialogue_lombre_ludicolo(premier, second)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    conversation({premier, second}, {
      {1, 'Worried', 'Nilo est encore dans ce fossé… J’espère que Lyra pourra le retrouver bientôt.'},
      {2, 'Normal', 'Les jeunes ont promis de l’aider. Laissons-les se préparer, puis suivons les nouvelles.'},
    })
  else
    conversation({premier, second}, repliques_du_jour(dialogues_lombre_ludicolo))
  end
end
function ville.NewObject_7_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lombre_ludicolo(personnage, CH('NewObject_8'))
  terminer_dialogue(personnage, 'NewObject_7')
end
function ville.NewObject_8_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  dialogue_lombre_ludicolo(CH('NewObject_7'), personnage)
  terminer_dialogue(personnage, 'NewObject_8')
end

local dialogues_lux = {
  {
    {1, 'Worried', 'Dis… les Bois Perdus font vraiment aussi peur qu’on le raconte ?'},
    {2, 'Normal', 'Il demande du respect, pas de la peur. On y entre préparé, et jamais en se croyant invincible.'},
    {1, 'Happy', 'Alors je m’entraînerai encore. Un jour, je traverserai à tes côtés.'},
  },
  {
    {1, 'Happy', 'J’ai couru jusqu’au pont de l’est sans m’arrêter ! Tu as vu ?'},
    {2, 'Happy', 'Je regardais, oui. Encore un peu de souffle, et tu tiendras une vraie patrouille.'},
    {1, 'Normal', 'Demain, je vise la place et retour. Chronomètre-moi !'},
  },
  {
    {1, 'Worried', 'Et si une équipe se perd, un jour ? Qui ira la chercher ?'},
    {2, 'Normal', 'Ceux qui connaissent les chemins… et qui ont appris à revenir. C’est pour cela qu’on s’entraîne.'},
    {1, 'Happy', 'Alors un jour, ce sera nous. Promis ?'},
    {2, 'Happy', 'Promis, petit frère.'},
  },
}
local function dialogue_lux(second, premier)
  conversation({second, premier}, repliques_du_jour(dialogues_lux))
end
-- Après les préparatifs, un oui lance une courte marche visible. Le fondu
-- représente le trajet entre l’escalier sud et la sortie est déjà raccordée.
function ville.Luxray_Alerte_Action(personnage, activator)
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.AlerteShinx ~= 'a_secourir' then return end
  local hero = CH('PLAYER') or activator
  local partenaire = partenaire_pour(hero)
  if hero == nil or partenaire == nil then return end
  commencer_dialogue(personnage, activator)
  parler_accueil(personnage, 'Worried', 'Mon petit Nilo est toujours là-bas… Est-ce que vous êtes prêts à partir ?')
  UI:ResetSpeaker()
  UI:BeginChoiceMenu('Prêts à partir ?', {
    'Oui, carrément, totalement prêts !',
    'Pas encore, je dois vérifier quelques trucs avant de partir.',
  }, 1, 2)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if choix ~= 1 then
    parler_accueil(personnage, 'Worried', 'D’accord… Préparez-vous, je vous attends ici. Mais s’il vous plaît, ne tardez pas trop.')
    UI:ResetSpeaker()
    terminer_dialogue(personnage, 'Luxray_Alerte')
    return
  end
  parler_accueil(personnage, 'Worried', 'Merci ! Venez, je vais vous montrer la route.')
  cinematique.Dire(partenaire, 'Determined', 'On y va ! Tiens bon, Nilo, on arrive !', 'droite')
  UI:ResetSpeaker()
  SV.Destiny.DepartShinxAccepte = true
  GAME:CutsceneMode(true)
  AI:DisableCharacterAI(partenaire)
  hero.CollisionDisabled = true
  GAME:FadeOut(false, 20)
  GROUND:TeleportTo(personnage, 800, 1272, Direction.Down)
  GROUND:TeleportTo(partenaire, 800, 1248, Direction.Down)
  GROUND:TeleportTo(hero, 800, 1224, Direction.Down)
  GAME:MoveCamera(800, 1284, 1, false)
  GAME:FadeIn(20)
  GAME:WaitFrames(12)
  local mere = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(personnage, 800, 1352, false, 1)
  end)
  local guide = TASK:BranchCoroutine(function()
    GAME:WaitFrames(4)
    GROUND:MoveToPosition(partenaire, 800, 1328, false, 1)
  end)
  local joueur = TASK:BranchCoroutine(function()
    GAME:WaitFrames(8)
    GROUND:MoveToPosition(hero, 800, 1304, false, 1)
  end)
  local camera = TASK:BranchCoroutine(function() GAME:MoveCamera(800, 1320, 80, false) end)
  TASK:JoinCoroutines({mere, guide, joueur, camera})
  GAME:WaitFrames(12)
  GAME:FadeOut(false, 20)
  GROUND:TeleportTo(personnage, 1504, 1584, Direction.Right)
  GROUND:TeleportTo(partenaire, 1528, 1592, Direction.Right)
  GROUND:TeleportTo(hero, 1552, 1592, Direction.Right)
  SV.Destiny.LuxrayAttente = 'sortie'
  GAME:MoveCamera(1544, 1592, 1, false)
  GAME:FadeIn(20)
  cinematique.Dire(partenaire, 'Normal', 'C’est par ici qu’on choisit habituellement notre route vers les donjons. Cherchons la Grotte Verdoyante.', 'droite')
  -- Une destination existante peut changer de scène sans reprise de coroutine.
  UI:ResetSpeaker()
  retour_au_joueur(hero, partenaire)
  ville.SortieExplorationE2_Touch(nil, hero)
end

function ville.NewObject_9_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    parler_accueil(personnage, 'Worried', 'Mon petit Nilo attend toujours là-bas… Je vous en prie, ne tardez pas trop.')
    UI:ResetSpeaker()
  else
    dialogue_lux(CH('NewObject_10'), personnage)
  end
  terminer_dialogue(personnage, 'NewObject_9')
end
function ville.NewObject_10_Action(personnage, activator)
  commencer_dialogue(personnage, activator)
  if SV.Destiny ~= nil and SV.Destiny.AlerteShinx == 'a_secourir' then
    parler_accueil(personnage, 'Worried', 'Lyra est partie chercher de l’aide pour Nilo… J’espère qu’il va bien.')
    UI:ResetSpeaker()
    terminer_dialogue(personnage, 'NewObject_10')
    return
  end
  dialogue_lux(personnage, CH('NewObject_9'))
  terminer_dialogue(personnage, 'NewObject_10')
end

local dialogues_habitants = {
  NewObject_6 = {
    {{'Happy', 'De là-haut, on voit les toits, les chutes et même un morceau de la falaise. Réverie Town tient dans un battement d’ailes.'}},
    {{'Happy', 'Ce matin, le vent porte jusqu’à la forêt d’ambre. Parfait pour les ailes… et pour les nouvelles.'}},
    {{'Normal', 'Les courants chauds tournent au-dessus de la rivière. Quand ils glissent vers l’est, le beau temps suit toujours.'}},
  },
  NewObject_12 = {
    {{'Normal', 'Je porte les caisses du marché le matin. L’après-midi, je laisse mes bras raconter qu’ils ont bien travaillé.'}},
    {{'Worried', 'Deux livraisons pour Basil et Félix, une pour la forge… Mes quatre bras ont leur propre emploi du temps, aujourd’hui.'}},
    {{'Happy', 'Une caisse bien portée ne casse jamais. C’est ma devise. Bon, sauf celle de la semaine dernière. Une seule !'}},
  },
  NewObject_13 = {
    {{'Happy', 'J’adore suivre les reflets sur l’eau. Quand une équipe revient de mission, toute la place semble briller.'}},
    {{'Happy', 'Les filets bleu foncé de la rivière voyagent le long des berges. Je les suis du regard jusqu’au pont !'}},
    {{'Normal', 'Aujourd’hui, je compte les équipes qui partent. Demain, je compterai celles qui reviennent. C’est mon rituel.'}},
  },
  NewObject_14 = {
    {{'Normal', 'Les explorateurs pressés oublient souvent de vérifier leur sac. Mado, Basil et Félix peuvent les aider à bien se préparer.'}},
    {{'Normal', 'Un sac vérifié le matin vaut deux jambes reposées. Notez-le quelque part, ça vous servira en donjon.'}},
    {{'Worried', 'On prévoit du vent sur les hauteurs. Les équipes sages attendront demain, les autres… apprendront vite.'}},
  },
  Doyen = {
    {{'Normal', 'Je connais chaque courant qui passe au-dessus des cascades. La ville change, mais le vent se souvient.'}},
    {{'Normal', 'Chaque jour, la rivière déplace ses filaments d’un souffle. Rien ne reste, tout continue. Méditez-y.'}},
    {{'Happy', 'Les jeunes Baudrive me demandent des histoires. Je leur raconte la ville… un quartier par jour.'}},
  },
  Drifloon = {
    {{'Happy', 'Le vent m’emmène d’un quartier à l’autre. Aujourd’hui, il a décidé de rester près du Doyen.'}},
    {{'Happy', 'Aujourd’hui, le vent sent les baies du marché. Demain, il sentira peut-être la pluie. Moi, je suivrai !'}},
    {{'Worried', 'Le Doyen dit que le vent se souvient de tout. Alors je lui confie mes secrets… il les garde là-haut.'}},
  },
  NewObject_16 = {
    {{'Normal', 'Je surveille les chemins qui montent vers les hauteurs. Un ciel dégagé annonce souvent une bonne journée d’expédition.'}},
    {{'Normal', 'Ronde du matin terminée : ponts dégagés, sentiers secs. Les équipes peuvent partir tranquilles.'}},
    {{'Worried', 'Des nuages s’accrochent à la falaise. Si vous montez aujourd’hui, restez sur les chemins balisés.'}},
  },
  NewObject_11 = {
    {{'Normal', 'Mon équipe se repose. Savoir s’arrêter à Réverie Town fait aussi partie du métier d’explorateur.'}},
    {{'Happy', 'Hier, les grottes ; aujourd’hui, la place et un vrai repas. Demain ? On verra ce que dit le tableau des missions.'}},
    {{'Normal', 'Je révise nos cartes au bord de l’eau. Le courant m’aide à réfléchir, allez savoir pourquoi.'}},
  },
  NewObject_18 = {
    {{'Normal', 'Zzz… prévenez-moi quand le café Spinda servira le goûter… Zzz…'}},
    {{'Normal', 'Zzz… encore cinq minutes… ou cinq siestes… Zzz…'}},
    {{'Happy', 'Hmm ? On a parlé de goûter ? Non ? Alors je rendors… Zzz…'}},
  },
  NewObject_20 = {
    {{'Normal', 'Les jeunes équipes regardent toujours l’horizon. C’est bon signe : la ville a besoin de rêves neufs.'}},
    {{'Normal', 'De mon temps, on partait avec une carte griffonnée sur une écorce. Vous avez bien de la chance, aujourd’hui.'}},
    {{'Happy', 'Je vois passer les équipes chaque jour. Chacune repart un peu plus grande qu’à l’arrivée. Ça me suffit.'}},
  },
  NewObject_21 = {
    {{'Happy', 'Le parfum des baies du marché me donne des idées de desserts pour tout le quartier !'}},
    {{'Happy', 'Aujourd’hui : tarte aux Baies Pecha. Demain… tarte aux Baies Pecha aussi. On ne change pas un succès !'}},
    {{'Worried', 'Mes réserves de baies fondent plus vite que prévu. Quelqu’un ici fait des réserves dans MON garde-manger ?'}},
  },
  NewObject_15 = {
    {{'Happy', 'Un bon lait chaud après une mission, et les pattes tremblent déjà moins.'}},
    {{'Happy', 'Le lait du matin est le meilleur, parole d’Écrémeuh. Passez avant les expéditions, il part vite !'}},
    {{'Normal', 'Charmilly veut ma crème pour ses décorations. Entre voisines, on s’arrange toujours.'}},
  },
  NewObject_17 = {
    {{'Normal', 'Je fais ma ronde entre les ponts. Si vous cherchez la place, suivez le bruit des boutiques.'}},
    {{'Normal', 'Ronde du jour : ponts, place, berges. La rivière glisse vite aujourd’hui, surveillez vos pas près des quais.'}},
    {{'Happy', 'Les petits m’utilisent comme point de repère. « Au troisième Arcanin, tournez à gauche », disent-ils. Il n’y en a qu’un…'}},
  },
  NewObject_22 = {
    {{'Normal', 'On dit que les ombres des Bois Perdus se déplacent. Moi, je dis surtout de garder une Baie Lum à portée de patte.'}},
    {{'Normal', 'Près de ma grotte, l’air change selon les jours. Quand il sent la mousse froide, les Bois Perdus s’agitent. Restez prudents.'}},
    {{'Worried', 'Les filaments de la rivière fuient vers le sud, comme s’ils évitaient la forêt. Intéressant… non ?'}},
  },
  NewObject_23 = {
    {{'Happy', 'Je décorerais bien la place pour le retour des équipes. Il suffit de peu pour qu’une ville sourie.'}},
    {{'Happy', 'Programme du jour : un ruban de crème sur la fontaine, deux sur le pont. Réverie mérite sa douceur quotidienne !'}},
    {{'Normal', 'Écrémeuh me garde sa meilleure crème. Demain, la place aura droit à une vraie fête des couleurs.'}},
  },
  Pijako_Livreur = {
    {{'Happy', 'Une lettre lue au bon moment peut sauver une expédition. Enfin, presque. Je livre vite, quand même !'}},
    {{'Happy', 'Tournée du jour : poste, place, café, et retour avant midi ! Le courrier de Réverie n’attend jamais.'}},
    {{'Worried', 'Le vent a failli emporter une lettre au-dessus de la chute. Failli ! Un Pijako ne perd jamais son courrier.'}},
  },
  Cradopaud_Pecheur = {
    {{'Normal', 'Les filets d’eau racontent la rivière : quand ils s’agitent, les poissons ne sont pas loin.'}},
    {{'Normal', 'Regardez les filaments descendre le courant : là où ils ralentissent, les poissons se reposent. C’est mon coin, aujourd’hui.'}},
    {{'Happy', 'Hier, trois prises avant le déjeuner. Aujourd’hui, je vise le double… ou une belle sieste. Verdict au couchant.'}},
  },
  Roserade_Fleuriste = {
    {{'Happy', 'Je tresse des guirlandes pour les maisons de la ville. Réverie mérite des fleurs fraîches chaque matin.'}},
    {{'Happy', 'Les fleurs des berges suivent les filaments de la rivière. Là où l’eau glisse douce, elles ouvrent plus tôt.'}},
    {{'Normal', 'Une guirlande par jour, une porte à la fois. Au bout d’une saison, toute la ville fleurit.'}},
  },
  Magneton_Garde = {
    {{'Normal', 'Bzz… Pont surveillé. Passage libre pour les équipes en règle. Bzz.'}},
    {{'Normal', 'Bzz… Contrôle du jour : sacs fermés, badges visibles. Merci de votre coopération. Bzz.'}},
    {{'Worried', 'Bzz… Interférences près de la cascade. Mes trois unités ne sont pas d’accord sur la cause. Bzz.'}},
  },
  Babimanta_Enfant = {
    {{'Happy', 'Quand je serai grand, je traverserai la grande chute en nageant ! Enfin… peut-être en bateau.'}},
    {{'Happy', 'Je fais la course avec les filaments de la rivière ! Ils vont vite… mais moi aussi !'}},
    {{'Worried', 'Marill dit qu’elle comptera les équipes avec moi. Moi, je compte les reflets. On s’échangera nos totaux demain.'}},
  },
  Goinfrex_Voyageur = {
    {{'Happy', 'On m’a dit que le café Spinda servait les meilleurs goûters du pays. Je vérifie. Rigoureusement.'}},
    {{'Happy', 'Jour deux de mes vérifications : le goûter du café Spinda est toujours excellent. La science avance.'}},
    {{'Normal', 'Je devais repartir ce matin… puis Cupcanaille a parlé de tarte. Je reste un jour de plus. Pour la science, toujours.'}},
  },
}
for nom, variantes in pairs(dialogues_habitants) do
  local nom_action, choix = nom, variantes
  ville[nom .. '_Action'] = function(personnage, activator)
    commencer_dialogue(personnage, activator)
    if not reaction_actualite(personnage, nom_action) then
      dialogue_simple(personnage, repliques_du_jour(choix))
    end
    terminer_dialogue(personnage, nom_action)
  end
end

return ville
