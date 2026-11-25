-- Les deux comptoirs de Réverie. Chaque étal tire des articles par famille
-- et utilise les vrais menus ShopMenu / SellMenu.
local boutiques = {}
local VERSION_STOCK = 1
local InvItem = function(id, quantite)
  return RogueEssence.Dungeon.InvItem(id, false, quantite)
end

local provisions = {
  {'food_apple_big', 24}, {'food_banana', 10},
  {'gummi_blue', 1}, {'gummi_green', 1}, {'gummi_red', 1}, {'gummi_yellow', 1},
}
local soins = {
  {'berry_leppa', 25}, {'seed_reviver', 10}, {'seed_warp', 5},
  {'seed_sleep', 5}, {'seed_blast', 8}, {'seed_decoy', 6},
  {'medicine_potion', 8}, {'medicine_full_heal', 6},
  {'berry_sitrus', 3}, {'berry_lum', 2},
}
local projectiles = {{'ammo_geo_pebble', 5}, {'ammo_stick', 5}, {'ammo_iron_thorn', 5}}
local equipements = {
  {'held_power_band', 10}, {'held_special_band', 10}, {'held_defense_scarf', 10},
  {'held_zinc_band', 10}, {'held_heal_ribbon', 10}, {'held_cover_band', 10},
  {'held_reunion_cape', 2},
}
local ct = {
  {'tm_secret_power', 10}, {'tm_echoed_voice', 10}, {'tm_protect', 5},
  {'tm_roar', 10}, {'tm_facade', 10}, {'tm_safeguard', 10}, {'tm_payback', 10},
  {'tm_venoshock', 5}, {'tm_thunder_wave', 5}, {'tm_thief', 10},
  {'tm_water_pulse', 2}, {'tm_dig', 2}, {'tm_rock_tomb', 4},
}
local orbes = {
  {'orb_escape', 50}, {'orb_cleanse', 10}, {'orb_foe_hold', 10}, {'orb_slumber', 10},
  {'orb_totter', 10}, {'orb_scanner', 10}, {'orb_luminous', 10}, {'orb_spurn', 10},
  {'orb_rollcall', 15}, {'orb_trawl', 5}, {'orb_all_aim', 10},
}
local baguettes = {
  {'wand_path', 10}, {'wand_pounce', 10}, {'wand_whirlwind', 10},
  {'wand_switcher', 10}, {'wand_lure', 10}, {'wand_slow', 10},
  {'wand_warp', 5}, {'wand_purge', 5},
}
local annonces = {
  vert = {
    accueil = 'Bienvenue chez Zig ! Il vous faut des provisions pour la route ?',
    infos = 'Pommes, baies, graines, projectiles et équipement : je m’occupe du sac de voyage. Mon frère Zag tient l’autre comptoir.',
  },
  violet = {
    accueil = 'Bienvenue chez Zag ! Une CT, une orbe ou une baguette pour votre prochaine expédition ?',
    infos = 'Une CT, trois orbes et deux lots de baguettes chaque jour. Pour des pommes et des baies, voyez mon frère Zig !',
  },
}

local function preparer_article(id, limite)
  local data = _DATA:GetItem(id)
  if data == nil or not data.Released or data.Price <= 0 then return nil end
  local nombre = math.min(limite, math.max(1, data.MaxStack))
  return {Index = id, Amount = nombre, Price = InvItem(id, nombre):GetSellValue() * 5}
end

-- Un générateur local, propre à chaque comptoir. Ni l'ordre d'ouverture des
-- boutiques ni la graine de la dernière expédition ne changent l'étal du jour.
local function generer(cle, jour)
  local articles = {}
  local etat = (jour * 104729 + (cle == 'vert' and 27183 or 62831)) % 2147483646 + 1
  local function tirer(liste, compte, limite)
    local panier = {}
    for _, entree in ipairs(liste) do
      local lot = preparer_article(entree[1], limite)
      if lot ~= nil then panier[#panier + 1] = {lot, entree[2]} end
    end
    for _ = 1, math.min(compte, #panier) do
      local total = 0
      for _, entree in ipairs(panier) do total = total + entree[2] end
      etat = (etat * 48271) % 2147483647
      local ticket = etat % total
      for i, entree in ipairs(panier) do
        ticket = ticket - entree[2]
        if ticket < 0 then
          articles[#articles + 1] = entree[1]
          table.remove(panier, i)
          break
        end
      end
    end
  end
  if cle == 'vert' then
    -- Les deux indispensables ne disparaissent jamais du réassort.
    tirer({{'food_apple', 1}}, 1, 1)
    tirer(provisions, 1, 1)
    tirer({{'berry_oran', 1}}, 1, 1)
    tirer(soins, 3, 1)
    tirer(projectiles, 1, math.huge)
    tirer(equipements, 1, 1)
  else
    tirer(ct, 1, 1)
    tirer(orbes, 3, 1)
    tirer(baguettes, 2, 4)
  end
  return {Jour = jour, Version = VERSION_STOCK, Articles = articles}
end

function boutiques.Stock(cle)
  assert(annonces[cle] ~= nil, 'Comptoir Kecleon inconnu')
  SV.Destiny = SV.Destiny or {}
  local destiny = SV.Destiny
  destiny.StocksKecleon = destiny.StocksKecleon or {}
  local jour = math.max(0, math.floor(tonumber(destiny.JourneeVille) or 0))
  local stock = destiny.StocksKecleon[cle]
  if not stock or stock.Jour ~= jour or stock.Version ~= VERSION_STOCK then
    stock = generer(cle, jour)
    destiny.StocksKecleon[cle] = stock
  end
  return stock
end

-- Le moteur remplit d'abord les piles existantes. Prévoir les places avant
-- de toucher aux Poké ; GivePlayerItem(id, quantité) empile une unité à la fois.
local function place_pour(lots)
  local places = _DATA.Save.ActiveTeam:GetMaxInvSlots(_ZONE.CurrentZone) - GAME:GetPlayerBagCount()
  local place_par_item = {}
  for _, lot in ipairs(lots) do
    local maximum = math.max(1, _DATA:GetItem(lot.ID).MaxStack)
    local reste = lot.Amount
    if maximum > 1 then
      local espace = place_par_item[lot.ID]
      if espace == nil then
        espace = 0
        for i = 0, GAME:GetPlayerBagCount() - 1 do
          local item = GAME:GetPlayerBagItem(i)
          if item.ID == lot.ID and not item.Cursed then
            espace = espace + math.max(0, maximum - item.Amount)
          end
        end
      end
      local ajout = math.max(0, reste - espace)
      local piles = math.ceil(ajout / maximum)
      places = places - piles
      place_par_item[lot.ID] = espace + piles * maximum - reste
    else
      places = places - reste
    end
  end
  return places >= 0
end

local function confirmer(question, total)
  UI:ChoiceMenuYesNo(question .. ' ' .. total .. ' Poké ?', false)
  UI:WaitForChoice()
  return UI:ChoiceResult() == true
end

local function acheter(personnage, stock)
  if #stock.Articles == 0 then
    UI:WaitShowDialogue('Mon étal est épuisé pour aujourd’hui. Revenez demain !')
    return
  end
  local catalogue = {}
  for i, article in ipairs(stock.Articles) do
    catalogue[i] = {Item = InvItem(article.Index, article.Amount), Price = article.Price}
  end
  UI:ShopMenu(catalogue)
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if not choix or #choix == 0 then return end
  UI:SetSpeaker(personnage)
  local total, lots, indices, vus = 0, {}, {}, {}
  for _, index in ipairs(choix) do
    local article = catalogue[index]
    if article == nil or vus[index] then return end
    vus[index] = true
    indices[#indices + 1] = index
    lots[#lots + 1] = article.Item
    total = total + article.Price
  end
  if total > GAME:GetPlayerMoney() then
    UI:WaitShowDialogue('Il vous manque des Poké pour cet achat.')
  elseif not place_pour(lots) then
    UI:WaitShowDialogue('Il n’y a pas assez de place dans votre sac.')
  elseif confirmer('Acheter pour', total) then
    for _, lot in ipairs(lots) do GAME:GivePlayerItem(lot.ID, lot.Amount, false) end
    GAME:RemoveFromPlayerMoney(total)
    table.sort(indices, function(a, b) return a > b end)
    for _, index in ipairs(indices) do table.remove(stock.Articles, index) end
    SOUND:PlayBattleSE('DUN_Money')
    UI:WaitShowDialogue('Merci et bonne expédition !')
  end
end

local function vendre(personnage)
  if GAME:GetPlayerBagCount() + GAME:GetPlayerEquippedCount() == 0 then
    UI:WaitShowDialogue('Vous n’avez rien à vendre pour l’instant.')
    return
  end
  UI:SellMenu()
  UI:WaitForChoice()
  local choix = UI:ChoiceResult()
  if not choix or #choix == 0 then return end
  UI:SetSpeaker(personnage)
  local total, sac, equipes, vus = 0, {}, {}, {}
  for _, place in ipairs(choix) do
    local equipe, index = place.IsEquipped, place.Slot
    local cle = tostring(equipe) .. ':' .. index
    if vus[cle] then return end
    vus[cle] = true
    local item = equipe and GAME:GetPlayerEquippedItem(index) or GAME:GetPlayerBagItem(index)
    if item == nil or item:GetSellValue() <= 0 then return end
    total = total + item:GetSellValue()
    local liste = equipe and equipes or sac
    liste[#liste + 1] = index
  end
  if not confirmer('Vendre pour', total) then return end
  -- SellMenu affiche le prix de la pile entière, pas d’une unité.
  table.sort(sac, function(a, b) return a > b end)
  for _, index in ipairs(sac) do GAME:TakePlayerBagItem(index, true) end
  for _, index in ipairs(equipes) do GAME:TakePlayerEquippedItem(index, true) end
  GAME:AddToPlayerMoney(total)
  SOUND:PlayBattleSE('DUN_Money')
  UI:WaitShowDialogue('Voici vos Poké. Merci !')
end

function boutiques.Ouvrir(personnage, cle)
  local stock = boutiques.Stock(cle)
  local texte = annonces[cle]
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  UI:WaitShowDialogue(texte.accueil)
  while true do
    UI:SetSpeaker(personnage)
    UI:BeginChoiceMenu('Que souhaitez-vous faire ?', {'Acheter', 'Vendre', 'Infos', 'Quitter'}, 1, 4)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 1 then acheter(personnage, stock)
    elseif choix == 2 then vendre(personnage)
    elseif choix == 3 then
      UI:WaitShowDialogue(texte.infos)
      UI:WaitShowDialogue('Le stock revient le lendemain. Une sieste au Café Spinda fait passer au jour suivant.')
    else break end
  end
  UI:ResetSpeaker()
end

return boutiques
