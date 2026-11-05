--[[
  café Spinda — services du comptoir (tranche novembre 2026).

  Deux services, tous deux branchés sur les menus natifs du moteur :

  * le bar à jus de Spinda (accueil) : le joueur choisit un membre de
    l'équipe, sélectionne des ingrédients dans son sac — baies, gommes,
    graines, petits aliments — puis Spinda les presse en un jus. Les effets
    sont ceux du catalogue `COMMON.JUICE.BOOSTS` de la base (chaque
    ingrédient nourrit un peu l'expérience ou les bonus permanents) ;
    l'aperçu des gains, la sélection multiple et la fenêtre de montée de
    niveau sont ceux de `JuiceShopMenu`, `InventorySelectMenu` et
    `LevelUpMenu` ;

  * l'atelier de recyclage d'Okéoké et Qulbutoké (étage) : le joueur dépose
    jusqu'à quatre objets, l'atelier en estime la valeur de reprise, puis il
    choisit une trouvaille du jour dont le prix tient dans cette valeur. Les
    trouvailles changent à chaque journée de ville, comme les étals Kecleon.

  Toutes les valeurs (ingrédients, cote de reprise, assortiments de
  trouvailles) sont écrites ici, en français, et l'état du comptoir est
  persisté dans `SV.Destiny` : aucun fichier de données à créer, aucun
  service permanent à enregistrer.
]]--

require 'origin.common'
require 'origin.menu.juice.JuiceShopMenu'
require 'origin.menu.InventorySelectMenu'
require 'origin.menu.team.TeamSelectMenu'

local cafe = {}

-- Prix du service d'une tournée de jus, en Poké. La première est offerte.
cafe.PRIX_TOURNEE = 100

-- Nombre d'objets qu'un dépôt peut déposer à l'atelier.
cafe.MAX_DEPOT = 4

-- Ingrédients acceptés par le bar : exactement le catalogue de la base
-- (87 entrées, toutes présentes dans game/Data/Item ou base/Data/Item).
local INGREDIENTS = COMMON.JUICE.BOOSTS

--------------------------------------------------------------------------------------------------------------
-- Petits utilitaires d'affichage
--------------------------------------------------------------------------------------------------------------

function cafe.parler(acteur, emotion, texte)
  if acteur ~= nil then
    UI:SetSpeaker(acteur)
    if emotion ~= nil then UI:SetSpeakerEmotion(emotion) end
  else
    UI:ResetSpeaker()
  end
  UI:WaitShowDialogue(texte)
end

local function fiche_objet(id)
  if id == nil or id == '' then return nil end
  local ok, fiche = pcall(function() return _DATA:GetItem(id) end)
  if not ok or fiche == nil then return nil end
  return fiche
end

function cafe.nom_objet(id)
  local fiche = fiche_objet(id)
  if fiche == nil then return tostring(id) end
  local ok, nom = pcall(function() return fiche.Name:ToLocal() end)
  if ok and nom ~= nil and nom ~= '' then return nom end
  return tostring(id)
end

function cafe.prix_catalogue(id)
  local fiche = fiche_objet(id)
  if fiche == nil then return 0 end
  local ok, prix = pcall(function() return fiche.Price end)
  if ok and type(prix) == 'number' then return prix end
  return 0
end

-- Renvoie l'objet (InvItem) d'un emplacement de sac ou d'équipement.
function cafe.objet_du_slot(slot)
  if slot == nil then return nil end
  if slot.IsEquipped then
    local persos = _DATA.Save.ActiveTeam.Players
    if slot.Slot < 0 or slot.Slot >= persos.Count then return nil end
    return persos[slot.Slot].EquippedItem
  end
  if slot.Slot < 0 or slot.Slot >= _DATA.Save.ActiveTeam:GetInvCount() then return nil end
  return _DATA.Save.ActiveTeam:GetInv(slot.Slot)
end

local function valeur_sure(nombre)
  if type(nombre) ~= 'number' then return 0 end
  return nombre
end

--------------------------------------------------------------------------------------------------------------
-- 1. Le bar à jus de Spinda
--------------------------------------------------------------------------------------------------------------

-- Catégorie d'un ingrédient, pour nommer le jus obtenu.
local function categorie_de(id)
  if string.sub(id, 1, 6) == 'gummi_' then return 'gomme' end
  if string.sub(id, 1, 6) == 'berry_' then return 'baie' end
  if string.sub(id, 1, 5) == 'seed_' then return 'graine' end
  if string.sub(id, 1, 7) == 'medicine' then return 'remède' end
  if string.sub(id, 1, 5) == 'boost' then return 'fortifiant' end
  if string.sub(id, 1, 4) == 'food' then return 'fruit' end
  if string.sub(id, 1, 4) == 'herb' then return 'herbe' end
  return 'mélange'
end

local NOMS_CATEGORIE = {
  gomme = { 'Jus de gommes', 'Gomme pressée' },
  baie = { 'Jus de baies', 'Presse de baies' },
  graine = { 'Jus de graines', 'Graines infusées' },
  remede = { 'Jus fortifiant', 'Infusion de remèdes' },
  fortifiant = { 'Jus de fortifiants', 'Élixir du comptoir' },
  fruit = { 'Jus de fruits', 'Fruits pressés' },
  herbe = { 'Jus d’herbes', 'Herbes infusées' },
  melange = { 'Mélange maison', 'Jus du voyageur' },
}

-- Nom de la boisson, déduit des ingrédients réellement choisis.
function cafe.nom_du_jus(cart)
  if cart == nil or #cart == 0 then return 'Verre vide' end
  local vus = {}
  local dominant = nil
  local compte_max = 0
  for _, slot in ipairs(cart) do
    local objet = cafe.objet_du_slot(slot)
    if objet ~= nil then
      local categorie = categorie_de(objet.ID)
      vus[categorie] = (vus[categorie] or 0) + 1
      if vus[categorie] > compte_max then
        compte_max = vus[categorie]
        dominant = categorie
      end
    end
  end
  if dominant == nil then return 'Mélange maison' end
  local noms = NOMS_CATEGORIE[dominant] or NOMS_CATEGORIE.melange
  local nom = noms[1]
  if #cart >= 4 then
    nom = nom .. ' du grand comptoir'
  elseif #cart >= 2 then
    nom = nom .. ' double'
  end
  return nom
end

-- Nombre d'ingrédients utilisables (sac + objets tenus) : sert à refuser
-- poliment la commande avant d'ouvrir un menu vide.
function cafe.compter_ingredients()
  local total = 0
  local persos = _DATA.Save.ActiveTeam.Players
  for i = 0, persos.Count - 1 do
    local objet = persos[i].EquippedItem
    if objet ~= nil and INGREDIENTS[objet.ID] ~= nil then total = total + 1 end
  end
  for i = 0, _DATA.Save.ActiveTeam:GetInvCount() - 1 do
    local objet = _DATA.Save.ActiveTeam:GetInv(i)
    if objet ~= nil and INGREDIENTS[objet.ID] ~= nil then total = total + 1 end
  end
  return total
end

-- Effet total d'un panier d'ingrédients sur un membre.
-- Reprend les règles de la base : gommes selon l'affinité de type, herbes qui
-- annulent les gains, aliments avariés qui font perdre de l'expérience.
function cafe.total_boost(cart, membre)
  local total = { EXP = 0, Level = 0, HP = 0, Atk = 0, Def = 0, SpAtk = 0, SpDef = 0, Speed = 0 }
  if membre == nil or cart == nil then return total end

  local negate_exp, negate_a, negate_b, negate_c = false, false, false, false
  local form = nil
  local ok_form, fiche = pcall(function()
    return _DATA:GetMonster(membre.BaseForm.Species).Forms[membre.BaseForm.Form]
  end)
  if ok_form then form = fiche end

  for _, slot in ipairs(cart) do
    local objet = cafe.objet_du_slot(slot)
    local boost = nil
    if objet ~= nil then boost = INGREDIENTS[objet.ID] end
    if boost ~= nil then
      if boost.GummiEffect ~= nil and form ~= nil then
        -- Une gomme nourrit surtout le type qu'elle porte, et un peu tout le
        -- reste quand le Pokémon y est sensible.
        local PreTypeEvent = PMDC.Dungeon.PreTypeEvent
        local matchup = PreTypeEvent.CalculateTypeMatchup(boost.GummiEffect, form.Element1)
        matchup = matchup + PreTypeEvent.CalculateTypeMatchup(boost.GummiEffect, form.Element2)

        local principale = 'HP'
        if boost.Atk ~= nil then principale = 'Atk' end
        if boost.Def ~= nil then principale = 'Def' end
        if boost.SpAtk ~= nil then principale = 'SpAtk' end
        if boost.SpDef ~= nil then principale = 'SpDef' end
        if boost.Speed ~= nil then principale = 'Speed' end

        local touchees = {}
        local gain_principale, gain_autres = 0, 0
        if boost.GummiEffect == form.Element1 or boost.GummiEffect == form.Element2 then
          gain_principale, gain_autres = 2, 1
          touchees = { 'HP', 'Atk', 'Def', 'SpAtk', 'SpDef', 'Speed' }
        elseif matchup >= PreTypeEvent.S_E_2 then
          gain_principale, gain_autres = 2, 1
          local ordonnees = {}
          local liste = {
            { RogueEssence.Data.Stat.HP, 'HP' },
            { RogueEssence.Data.Stat.Attack, 'Atk' },
            { RogueEssence.Data.Stat.Defense, 'Def' },
            { RogueEssence.Data.Stat.MAtk, 'SpAtk' },
            { RogueEssence.Data.Stat.MDef, 'SpDef' },
            { RogueEssence.Data.Stat.Speed, 'Speed' },
          }
          for _, entree in ipairs(liste) do
            if entree[2] ~= principale then table.insert(ordonnees, entree) end
          end
          table.sort(ordonnees, function(a, b)
            return form:GetBaseStat(a[1]) > form:GetBaseStat(b[1])
          end)
          touchees = { ordonnees[1][2], ordonnees[2][2], principale }
        elseif matchup == PreTypeEvent.NRM_2 then
          gain_principale, gain_autres = 2, 0
          touchees = { principale }
        elseif matchup > PreTypeEvent.N_E_2 then
          gain_principale, gain_autres = 1, 0
          touchees = { principale }
        end

        for _, stat in ipairs(touchees) do
          if stat == principale then
            total[stat] = total[stat] + gain_principale
          else
            total[stat] = total[stat] + gain_autres
          end
        end
      else
        total.EXP = total.EXP + valeur_sure(boost.EXP)
        total.Level = total.Level + valeur_sure(boost.Level)
        total.HP = total.HP + valeur_sure(boost.HP)
        total.Atk = total.Atk + valeur_sure(boost.Atk)
        total.Def = total.Def + valeur_sure(boost.Def)
        total.SpAtk = total.SpAtk + valeur_sure(boost.SpAtk)
        total.SpDef = total.SpDef + valeur_sure(boost.SpDef)
        total.Speed = total.Speed + valeur_sure(boost.Speed)
      end

      if boost.NegateExp then negate_exp = true end
      if boost.NegateStatA then negate_a = true end
      if boost.NegateStatB then negate_b = true end
      if boost.NegateStatC then negate_c = true end
    end
  end

  if negate_exp and negate_a and negate_b and negate_c then
    total.EXP = 0
    total.Level = -100
    total.HP, total.Atk, total.Def = -256, -256, -256
    total.SpAtk, total.SpDef, total.Speed = -256, -256, -256
  else
    if negate_exp then
      total.EXP = total.EXP * -1
      total.Level = total.Level * -1
    end
    if negate_a and negate_b and negate_c then
      total.HP, total.Atk, total.Def = -256, -256, -256
      total.SpAtk, total.SpDef, total.Speed = -256, -256, -256
    elseif negate_a or negate_b or negate_c then
      total.HP = total.HP * -1
      total.Atk = total.Atk * -1
      total.Def = total.Def * -1
      total.SpAtk = total.SpAtk * -1
      total.SpDef = total.SpDef * -1
      total.Speed = total.Speed * -1
    end
  end

  return total
end

-- Applique les gains au membre qui boit, comme la base : plafonds de bonus,
-- expérience, niveau, puis fenêtre de montée de niveau native.
function cafe.boire(boost, membre)
  if membre == nil or boost == nil then return end
  local MAX = PMDC.Data.MonsterFormData.MAX_STAT_BOOST
  local any_boost = false
  local touchees = {}
  local montants = {}
  local hausse, baisse = false, false

  local ancien_niveau = membre.Level
  local anciens = {
    HP = membre.MaxHP,
    Atk = membre.BaseAtk,
    Def = membre.BaseDef,
    SpAtk = membre.BaseMAtk,
    SpDef = membre.BaseMDef,
    Speed = membre.BaseSpeed,
  }

  local function noter(stat, difference)
    if difference == 0 then return end
    table.insert(touchees, stat)
    table.insert(montants, difference)
    if difference > 0 then hausse = true else baisse = true end
  end

  if boost.HP ~= 0 then
    membre.MaxHPBonus = math.max(0, math.min(membre.MaxHPBonus + boost.HP, MAX))
    noter(RogueEssence.Data.Stat.HP, membre.MaxHP - anciens.HP)
  end
  if boost.Atk ~= 0 then
    membre.AtkBonus = math.max(0, math.min(membre.AtkBonus + boost.Atk, MAX))
    noter(RogueEssence.Data.Stat.Attack, membre.BaseAtk - anciens.Atk)
  end
  if boost.Def ~= 0 then
    membre.DefBonus = math.max(0, math.min(membre.DefBonus + boost.Def, MAX))
    noter(RogueEssence.Data.Stat.Defense, membre.BaseDef - anciens.Def)
  end
  if boost.SpAtk ~= 0 then
    membre.MAtkBonus = math.max(0, math.min(membre.MAtkBonus + boost.SpAtk, MAX))
    noter(RogueEssence.Data.Stat.MAtk, membre.BaseMAtk - anciens.SpAtk)
  end
  if boost.SpDef ~= 0 then
    membre.MDefBonus = math.max(0, math.min(membre.MDefBonus + boost.SpDef, MAX))
    noter(RogueEssence.Data.Stat.MDef, membre.BaseMDef - anciens.SpDef)
  end
  if boost.Speed ~= 0 then
    membre.SpeedBonus = math.max(0, math.min(membre.SpeedBonus + boost.Speed, MAX))
    noter(RogueEssence.Data.Stat.Speed, membre.BaseSpeed - anciens.Speed)
  end

  if boost.EXP ~= 0 then
    membre.EXP = membre.EXP + boost.EXP
    local croissance = _DATA:GetGrowth(_DATA:GetMonster(membre.BaseForm.Species).EXPTable)
    while membre.EXP < 0 do
      if membre.Level <= 1 then
        membre.EXP = 0
      else
        membre.Level = membre.Level - 1
        membre.EXP = membre.EXP + croissance:GetExpToNext(membre.Level)
      end
    end
    while true do
      if membre.Level >= _DATA.Start.MaxLevel then
        membre.EXP = 0
        break
      elseif membre.EXP >= croissance:GetExpToNext(membre.Level) then
        membre.EXP = membre.EXP - croissance:GetExpToNext(membre.Level)
        membre.Level = membre.Level + 1
      else
        break
      end
    end
  end

  if boost.Level ~= 0 then
    membre.EXP = 0
    membre.Level = math.max(1, math.min(membre.Level + boost.Level, _DATA.Start.MaxLevel))
  end

  membre.HP = membre.MaxHP
  local nom = membre:GetDisplayName(true)

  if boost.EXP > 0 then
    cafe.parler(nil, nil, string.format('%s gagne %d points d’expérience.', nom, boost.EXP))
    any_boost = true
  elseif boost.EXP < 0 then
    cafe.parler(nil, nil, string.format('%s perd %d points d’expérience…', nom, boost.EXP * -1))
    any_boost = true
  end

  if membre.Level ~= ancien_niveau then
    if membre.Level > ancien_niveau then
      cafe.parler(nil, nil, string.format('%s atteint le niveau %d !', nom, membre.Level))
    else
      cafe.parler(nil, nil, string.format('%s redescend au niveau %d…', nom, membre.Level))
    end
    UI:SetCustomMenu(RogueEssence.Menu.LevelUpMenu(membre, ancien_niveau, anciens.HP,
      anciens.Speed, anciens.Atk, anciens.Def, anciens.SpAtk, anciens.SpDef))
    UI:WaitForChoice()
    any_boost = true
  elseif hausse or baisse then
    if #touchees > 1 then
      if hausse and not baisse then
        cafe.parler(nil, nil, string.format('Les statistiques de %s progressent d’un coup !', nom))
      elseif baisse and not hausse then
        cafe.parler(nil, nil, string.format('Les statistiques de %s chutent d’un coup…', nom))
      else
        cafe.parler(nil, nil, string.format('Les statistiques de %s se réorganisent.', nom))
      end
      UI:SetCustomMenu(RogueEssence.Menu.LevelUpMenu(membre, ancien_niveau, anciens.HP,
        anciens.Speed, anciens.Atk, anciens.Def, anciens.SpAtk, anciens.SpDef))
      UI:WaitForChoice()
    else
      local stat = RogueEssence.Text.ToLocal(touchees[1], nil)
      local montant = montants[1]
      if montant > 0 then
        cafe.parler(nil, nil, string.format('%s gagne %d en %s.', nom, montant, tostring(stat)))
      else
        cafe.parler(nil, nil, string.format('%s perd %d en %s…', nom, montant * -1, tostring(stat)))
      end
    end
    any_boost = true
  end

  if not any_boost then
    cafe.parler(nil, nil, string.format('%s finit son verre sans le moindre effet. Peut-être faudrait-il d’autres ingrédients ?', nom))
  end
end

-- Retire du sac (ou de l'équipement) les ingrédients réellement consommés.
local function consommer(cart)
  for ii = #cart, 1, -1 do
    local slot = cart[ii]
    if slot.IsEquipped then
      GAME:TakePlayerEquippedItem(slot.Slot, true)
    else
      GAME:TakePlayerBagItem(slot.Slot, true)
    end
  end
end

-- Commande complète d'un jus, depuis le comptoir de l'accueil.
function cafe.servir_le_jus(personnage)
  SV.Destiny = SV.Destiny or {}
  cafe.parler(personnage, 'Happy', 'Un jus ? Voilà une idée qui me plaît ! Passez-moi ce que vous avez dans le sac : je presse, je mélange, et je sers.')

  if cafe.compter_ingredients() == 0 then
    cafe.parler(personnage, 'Normal', 'Hmm… votre sac n’a rien que je puisse presser. Des baies, des gommes, une graine, un petit fruit : n’importe quoi de mangeable fera l’affaire.')
    UI:ResetSpeaker()
    return
  end

  cafe.parler(personnage, 'Normal', 'Qui boira cette tournée ? Chacun a son goût, et les gommes ne profitent pas à toutes les équipes de la même façon.')
  local membre = TeamSelectMenu.runPartyMenu()
  if membre == nil then
    UI:ResetSpeaker()
    return
  end

  local nom_membre = membre:GetDisplayName(true)
  local offerte = not SV.Destiny.TourneeOfferte
  local prix = cafe.PRIX_TOURNEE
  if offerte then prix = 0 end
  if not offerte and GAME:GetPlayerMoney() < prix then
    cafe.parler(personnage, 'Worried', string.format('Une tournée, c’est %d Poké… et il vous en manque un peu. Revenez quand la bourse ira mieux : le comptoir ne ferme pas.', prix))
    UI:ResetSpeaker()
    return
  end

  if offerte then
    cafe.parler(personnage, 'Happy', 'Et pour la première fois, c’est la maison qui régale ! Choisissez ce qui entre dans le verre.')
  else
    cafe.parler(personnage, 'Normal', string.format('La tournée coûte %d Poké. Choisissez les ingrédients.', prix))
  end

  local cart = JuiceShopMenu.run('Ingrédients du jus', membre, INGREDIENTS, true, true,
    function(liste, cible) return cafe.total_boost(liste, cible) end)
  if cart == nil or #cart == 0 then
    cafe.parler(personnage, 'Normal', 'Vous refermez le sac. Une autre fois, alors !')
    UI:ResetSpeaker()
    return
  end

  local nom_jus = cafe.nom_du_jus(cart)
  UI:ResetSpeaker()
  if prix > 0 then
    UI:ChoiceMenuYesNo(string.format('%s pour %s, et %d Poké pour le comptoir ?', nom_jus, nom_membre, prix), true)
  else
    UI:ChoiceMenuYesNo(string.format('%s pour %s, offert par la maison ?', nom_jus, nom_membre), true)
  end
  UI:WaitForChoice()
  if not UI:ChoiceResult() then
    cafe.parler(personnage, 'Normal', 'Comme vous voulez. Les ingrédients restent dans votre sac.')
    UI:ResetSpeaker()
    return
  end

  -- Le boost se calcule avant la consommation : les emplacements doivent
  -- encore exister dans le sac au moment de la lecture.
  local boost = cafe.total_boost(cart, membre)
  consommer(cart)

  if prix > 0 then GAME:RemoveFromPlayerMoney(prix) end
  if offerte then SV.Destiny.TourneeOfferte = true end
  SV.Destiny.JusDecouvert = true
  SV.Destiny.JusServis = (SV.Destiny.JusServis or 0) + 1

  UI:ResetSpeaker()
  cafe.parler(personnage, 'Happy', 'Je presse, je secoue, je décore d’une baie… et voilà !')
  SOUND:PlayBattleSE('DUN_Drink')
  cafe.parler(personnage, 'Normal', string.format('%s porte le verre à ses lèvres. Un %s, rien de moins.', nom_membre, string.lower(nom_jus)))
  cafe.boire(boost, membre)
  cafe.parler(personnage, 'Happy', 'Le comptoir est toujours ouvert. Les équipes qui reviennent sont celles qui prennent le temps de souffler.')
  UI:ResetSpeaker()
end

--------------------------------------------------------------------------------------------------------------
-- 2. L'atelier de recyclage d'Okéoké et Qulbutoké
--------------------------------------------------------------------------------------------------------------

-- Cote maison des objets les plus courants (en Poké). Elle sert deux fois :
-- la moitié donne la valeur de reprise d'un dépôt, le prix entier donne le
-- coût d'une trouvaille. Les objets absents de cette table retombent sur la
-- moitié du prix du catalogue PMDO, avec un plancher de 5 Poké.
local VALEURS = {
  food_apple = 50, food_apple_big = 150, food_apple_huge = 600, food_banana = 100,
  berry_oran = 80, berry_sitrus = 150, berry_leppa = 80, berry_lum = 150,
  berry_pecha = 80, berry_chesto = 80, berry_persim = 80, berry_rawst = 80,
  seed_pure = 400, seed_reviver = 800, seed_joy = 1200, seed_sleep = 60,
  seed_warp = 80, seed_blast = 100, seed_vile = 100, seed_decoy = 150,
  herb_mental = 100, herb_power = 100, herb_white = 100,
  orb_escape = 300, orb_scanner = 300, orb_revival = 1200,
  medicine_elixir = 300, medicine_max_elixir = 700, medicine_potion = 300,
  medicine_max_potion = 500, medicine_amber_tear = 900,
  boost_hp_up = 750, boost_protein = 750, boost_iron = 750,
  boost_calcium = 750, boost_zinc = 750, boost_carbos = 750, boost_nectar = 900,
  gummi_red = 250, gummi_blue = 250, gummi_white = 250, gummi_black = 250,
  gummi_green = 250, gummi_brown = 250, gummi_yellow = 250, gummi_purple = 250,
  gummi_pink = 250, gummi_gray = 250, gummi_gold = 250, gummi_silver = 250,
  gummi_clear = 250, gummi_grass = 250, gummi_orange = 250, gummi_royal = 250,
  gummi_sky = 250, gummi_magenta = 250, gummi_wonder = 500,
}

-- Trois trouvailles par journée de ville, comme les étals Kecleon. Chaque
-- assortiment garde une entrée à 40 Poké : une seule baie déposée (80 Poké
-- de cote, donc 40 de reprise) suffit déjà à repartir avec quelque chose.
local ASSORTIMENTS = {
  { { index = 'food_apple', prix = 40 }, { index = 'berry_oran', prix = 80 }, { index = 'gummi_red', prix = 250 } },
  { { index = 'berry_leppa', prix = 40 }, { index = 'berry_lum', prix = 150 }, { index = 'seed_pure', prix = 400 } },
  { { index = 'food_banana', prix = 40 }, { index = 'gummi_white', prix = 250 }, { index = 'orb_escape', prix = 300 } },
  { { index = 'berry_pecha', prix = 40 }, { index = 'medicine_elixir', prix = 300 }, { index = 'seed_reviver', prix = 800 } },
  { { index = 'berry_sitrus', prix = 40 }, { index = 'gummi_wonder', prix = 500 }, { index = 'medicine_max_elixir', prix = 700 } },
}

-- Valeur de reprise (Poké) d'un objet déposé.
function cafe.valeur_de_reprise(objet)
  if objet == nil or objet.ID == nil or objet.ID == '' then return 0 end
  local fiche = fiche_objet(objet.ID)
  if fiche == nil then return 0 end
  local ok_drop, interdit = pcall(function() return fiche.CannotDrop end)
  if ok_drop and interdit then return 0 end
  local cote = VALEURS[objet.ID]
  if cote == nil then
    local prix = cafe.prix_catalogue(objet.ID)
    if prix <= 0 then return 0 end
    cote = prix
  end
  return math.max(5, math.floor(cote / 2))
end

-- Trouvailles proposées aujourd'hui.
function cafe.trouvailles_du_jour()
  local jour = (SV.Destiny and SV.Destiny.JourneeVille) or 0
  return ASSORTIMENTS[(jour % #ASSORTIMENTS) + 1]
end

local function filtre_recyclable(slot)
  return cafe.valeur_de_reprise(cafe.objet_du_slot(slot)) > 0
end

-- Nombre d'objets du sac que l'atelier accepterait : évite d'ouvrir un menu
-- où tout serait grisé.
function cafe.compter_recyclables()
  local total = 0
  for i = 0, _DATA.Save.ActiveTeam:GetInvCount() - 1 do
    if cafe.valeur_de_reprise(_DATA.Save.ActiveTeam:GetInv(i)) > 0 then
      total = total + 1
    end
  end
  return total
end

-- Dépôt complet à l'atelier du premier étage.
function cafe.ouvrir_atelier(personnage, acolyte)
  SV.Destiny = SV.Destiny or {}

  local function repondre(emotion, texte)
    cafe.parler(personnage, emotion, texte)
  end

  if SV.Destiny.AtelierDecouvert then
    repondre('Happy', 'Ah, un habitué de l’atelier ! Les caisses sont rangées depuis belle lurette : déposez, on s’occupe du reste.')
  else
    repondre('Happy', 'Bienvenue à l’atelier de recyclage ! Ici, rien ne se perd : ce que les équipes ne veulent plus devient une trouvaille pour quelqu’un d’autre.')
    if acolyte ~= nil then
      cafe.parler(acolyte, 'Normal', 'Quatre objets au maximum par dépôt. On estime la valeur, et vous choisissez dans la réserve du jour.')
    end
    SV.Destiny.AtelierDecouvert = true
  end

  if GAME:GetPlayerBagCount() == 0 then
    repondre('Normal', 'Votre sac est vide ! Les objets tenus restent sur vous, on ne les touche pas. Revenez avec de quoi échanger.')
    UI:ResetSpeaker()
    return
  end

  if cafe.compter_recyclables() == 0 then
    repondre('Normal', 'Rien là-dedans n’a de valeur de reprise : les objets de quête et les pièces uniques restent chez vous. Des baies, des graines, une gomme ? Voilà qui nous intéresse.')
    UI:ResetSpeaker()
    return
  end

  repondre('Normal', string.format('Montrez-moi ce que vous voulez laisser (%d objets au plus).', cafe.MAX_DEPOT))
  local panier = InventorySelectMenu.run('Objets à recycler', filtre_recyclable, 'Recycler', false, cafe.MAX_DEPOT)
  if panier == nil or #panier == 0 then
    repondre('Normal', 'Vous remportez tout. À bientôt !')
    UI:ResetSpeaker()
    return
  end

  -- Estimation du dépôt.
  local credit = 0
  local details = {}
  for _, slot in ipairs(panier) do
    local objet = cafe.objet_du_slot(slot)
    local cote = cafe.valeur_de_reprise(objet)
    credit = credit + cote
    table.insert(details, string.format('%s (%d)', cafe.nom_objet(objet.ID), cote))
  end

  UI:ResetSpeaker()
  repondre('Normal', string.format('Voyons voir… %s. Cela fait une valeur de reprise de %d Poké.', table.concat(details, ', '), credit))

  -- Trouvailles abordables avec ce dépôt.
  local abordables = {}
  for _, trouvee in ipairs(cafe.trouvailles_du_jour()) do
    if trouvee.prix <= credit then table.insert(abordables, trouvee) end
  end

  if #abordables == 0 then
    if acolyte ~= nil then
      cafe.parler(acolyte, 'Worried', 'Ce dépôt ne vaut pas encore une trouvaille du jour. Gardez vos objets, revenez avec un peu plus : la réserve ne bouge pas avant la prochaine journée.')
    else
      repondre('Worried', 'Ce dépôt ne vaut pas encore une trouvaille du jour. Gardez vos objets pour un prochain passage.')
    end
    UI:ResetSpeaker()
    return
  end

  local choix = {}
  for _, trouvee in ipairs(abordables) do
    table.insert(choix, string.format('%s — %d Poké', cafe.nom_objet(trouvee.index), trouvee.prix))
  end
  table.insert(choix, 'Ne rien prendre')

  repondre('Happy', 'La réserve du jour : choisissez ce qui vous intéresse, dans la limite de votre dépôt.')
  if personnage ~= nil then UI:SetSpeaker(personnage) end
  UI:BeginChoiceMenu(string.format('Pour %d Poké de reprise, que prenez-vous ?', credit), choix, 1, #choix)
  UI:WaitForChoice()
  local rang = UI:ChoiceResult()
  if rang == nil or rang < 1 or rang > #abordables then
    repondre('Normal', 'Vous repartez avec vos objets. Revenez quand vous voudrez.')
    UI:ResetSpeaker()
    return
  end

  local trouvee = abordables[rang]

  -- Consommation puis remise : le sac se libère avant de recevoir.
  consommer(panier)
  GAME:GivePlayerItem(trouvee.index, 1)
  SOUND:PlayBattleSE('DUN_Money')

  SV.Destiny.RecyclageDons = (SV.Destiny.RecyclageDons or 0) + 1

  UI:ResetSpeaker()
  repondre('Happy', string.format('Échange conclu : %s contre vos objets. Bonne route !', cafe.nom_objet(trouvee.index)))

  if acolyte ~= nil then
    cafe.parler(acolyte, 'Normal', 'Regarde, il reste même de la place dans les caisses.')
  end

  -- Petit rabiot tous les cinq dépôts : une baie de la maison.
  if SV.Destiny.RecyclageDons % 5 == 0 then
    if GAME:GetPlayerBagCount() < GAME:GetPlayerBagLimit() then
      GAME:GivePlayerItem('berry_oran', 1)
      repondre('Joyous', 'Et comme c’est votre cinquième dépôt, la maison ajoute une baie Oran. Cadeau de l’atelier !')
    else
      repondre('Happy', 'C’est votre cinquième dépôt ! Revenez avec un peu de place dans le sac, la maison vous doit une baie Oran.')
    end
  end

  UI:ResetSpeaker()
end

return cafe
