-- Les 85 choix de la ROM privée Explorers Remixed 2.3.28.
-- Miaouss, préexistant dans Destiny, est ajouté par init.lua, sans doublon.
-- Les talents et graphiques sont cherchés par espèce + forme dans les données PMDO.
local M = {}
M.starters = {
  { espece = "bulbasaur", forme = 0, nom = "Bulbizarre", gen = 1, mega_famille = true },  -- 01 / Bulbasaur
  { espece = "charmander", forme = 0, nom = "Salamèche", gen = 1, mega_famille = true },  -- 02 / Charmander
  { espece = "squirtle", forme = 0, nom = "Carapuce", gen = 1, mega_famille = true },  -- 03 / Squirtle
  { espece = "pikachu", forme = 0, nom = "Pikachu", gen = 1, mega_famille = true },  -- 04 / Pikachu
  { espece = "vulpix", forme = 0, nom = "Goupix de Kanto", gen = 1, mega_famille = false },  -- 05 / Kantonian Vulpix
  { espece = "growlithe", forme = 0, nom = "Caninos de Kanto", gen = 1, mega_famille = false },  -- 06 / Kantonian Growlithe
  { espece = "eevee", forme = 0, nom = "Évoli", gen = 1, mega_famille = true },  -- 07 / Eevee
  { espece = "dratini", forme = 0, nom = "Minidraco", gen = 1, mega_famille = true },  -- 08 / Dratini
  { espece = "chikorita", forme = 0, nom = "Germignon", gen = 2, mega_famille = true },  -- 09 / Chikorita
  { espece = "cyndaquil", forme = 0, nom = "Héricendre", gen = 2, mega_famille = false },  -- 10 / Cyndaquil
  { espece = "totodile", forme = 0, nom = "Kaiminus", gen = 2, mega_famille = true },  -- 11 / Totodile
  { espece = "togepi", forme = 0, nom = "Togepi", gen = 2, mega_famille = false },  -- 12 / Togepi
  { espece = "mareep", forme = 0, nom = "Wattouat", gen = 2, mega_famille = false },  -- 13 / Mareep
  { espece = "wooper", forme = 0, nom = "Axoloto de Johto", gen = 2, mega_famille = false },  -- 14 / Johtonian Wooper
  { espece = "murkrow", forme = 0, nom = "Cornèbre", gen = 2, mega_famille = false },  -- 15 / Murkrow
  { espece = "sneasel", forme = 0, nom = "Farfuret de Johto", gen = 2, mega_famille = false },  -- 16 / Johtonian Sneasel
  { espece = "phanpy", forme = 0, nom = "Phanpy", gen = 2, mega_famille = false },  -- 17 / Phanpy
  { espece = "larvitar", forme = 0, nom = "Embrylex", gen = 2, mega_famille = false },  -- 18 / Larvitar
  { espece = "treecko", forme = 0, nom = "Arcko", gen = 3, mega_famille = true },  -- 19 / Treecko
  { espece = "torchic", forme = 0, nom = "Poussifeu", gen = 3, mega_famille = true },  -- 20 / Torchic
  { espece = "mudkip", forme = 0, nom = "Gobou", gen = 3, mega_famille = true },  -- 21 / Mudkip
  { espece = "ralts", forme = 0, nom = "Tarsal", gen = 3, mega_famille = true },  -- 22 / Ralts
  { espece = "skitty", forme = 0, nom = "Skitty", gen = 3, mega_famille = false },  -- 23 / Skitty
  { espece = "swablu", forme = 0, nom = "Tylton", gen = 3, mega_famille = true },  -- 24 / Swablu
  { espece = "snorunt", forme = 0, nom = "Stalgamin", gen = 3, mega_famille = true },  -- 25 / Snorunt
  { espece = "beldum", forme = 0, nom = "Terhal", gen = 3, mega_famille = true },  -- 26 / Beldum
  { espece = "turtwig", forme = 0, nom = "Tortipouss", gen = 4, mega_famille = false },  -- 27 / Turtwig
  { espece = "chimchar", forme = 0, nom = "Ouisticram", gen = 4, mega_famille = false },  -- 28 / Chimchar
  { espece = "piplup", forme = 0, nom = "Tiplouf", gen = 4, mega_famille = false },  -- 29 / Piplup
  { espece = "shinx", forme = 0, nom = "Lixy", gen = 4, mega_famille = false },  -- 30 / Shinx
  { espece = "budew", forme = 0, nom = "Rozbouton", gen = 4, mega_famille = false },  -- 31 / Budew
  { espece = "buneary", forme = 0, nom = "Laporeille", gen = 4, mega_famille = true },  -- 32 / Buneary
  { espece = "gible", forme = 0, nom = "Griknot", gen = 4, mega_famille = false },  -- 33 / Gible
  { espece = "riolu", forme = 0, nom = "Riolu", gen = 4, mega_famille = true },  -- 34 / Riolu
  { espece = "snivy", forme = 0, nom = "Vipélierre", gen = 5, mega_famille = false },  -- 35 / Snivy
  { espece = "tepig", forme = 0, nom = "Gruikui", gen = 5, mega_famille = true },  -- 36 / Tepig
  { espece = "oshawott", forme = 0, nom = "Moustillon", gen = 5, mega_famille = false },  -- 37 / Oshawott
  { espece = "sandile", forme = 0, nom = "Mascaïman", gen = 5, mega_famille = false },  -- 38 / Sandile
  { espece = "zorua", forme = 0, nom = "Zorua d'Unys", gen = 5, mega_famille = false },  -- 39 / Unovan Zorua
  { espece = "minccino", forme = 0, nom = "Chinchidou", gen = 5, mega_famille = false },  -- 40 / Minccino
  { espece = "joltik", forme = 0, nom = "Statitik", gen = 5, mega_famille = false },  -- 41 / Joltik
  { espece = "litwick", forme = 0, nom = "Funécire", gen = 5, mega_famille = true },  -- 42 / Litwick
  { espece = "axew", forme = 0, nom = "Coupenotte", gen = 5, mega_famille = false },  -- 43 / Axew
  { espece = "golett", forme = 0, nom = "Gringolem", gen = 5, mega_famille = true },  -- 44 / Golett
  { espece = "pawniard", forme = 0, nom = "Scalpion", gen = 5, mega_famille = false },  -- 45 / Pawniard
  { espece = "larvesta", forme = 0, nom = "Pyronille", gen = 5, mega_famille = false },  -- 46 / Larvesta
  { espece = "chespin", forme = 0, nom = "Marisson", gen = 6, mega_famille = true },  -- 47 / Chespin
  { espece = "fennekin", forme = 0, nom = "Feunnec", gen = 6, mega_famille = true },  -- 48 / Fennekin
  { espece = "froakie", forme = 0, nom = "Grenousse", gen = 6, mega_famille = true },  -- 49 / Froakie
  { espece = "pancham", forme = 0, nom = "Pandespiègle", gen = 6, mega_famille = false },  -- 50 / Pancham
  { espece = "espurr", forme = 0, nom = "Psystigri", gen = 6, mega_famille = true },  -- 51 / Espurr
  { espece = "goomy", forme = 0, nom = "Mucuscule", gen = 6, mega_famille = false },  -- 52 / Goomy
  { espece = "phantump", forme = 0, nom = "Brocélôme", gen = 6, mega_famille = false },  -- 53 / Phantump
  { espece = "pumpkaboo", forme = 0, nom = "Pitrouille", gen = 6, mega_famille = false },  -- 54 / Pumpkaboo
  { espece = "noibat", forme = 0, nom = "Sonistrelle", gen = 6, mega_famille = false },  -- 55 / Noibat
  { espece = "rowlet", forme = 0, nom = "Brindibou", gen = 7, mega_famille = false },  -- 56 / Rowlet
  { espece = "litten", forme = 0, nom = "Flamiaou", gen = 7, mega_famille = false },  -- 57 / Litten
  { espece = "popplio", forme = 0, nom = "Otaquin", gen = 7, mega_famille = false },  -- 58 / Popplio
  { espece = "vulpix", forme = 1, nom = "Goupix d'Alola", gen = 7, mega_famille = false },  -- 59 / Alolan Vulpix
  { espece = "rockruff", forme = 0, nom = "Rocabot", gen = 7, mega_famille = false },  -- 60 / Rockruff
  { espece = "salandit", forme = 0, nom = "Tritox", gen = 7, mega_famille = false },  -- 61 / Salandit
  { espece = "stufful", forme = 0, nom = "Nounourson", gen = 7, mega_famille = false },  -- 62 / Stufful
  { espece = "wimpod", forme = 0, nom = "Sovkipou", gen = 7, mega_famille = true },  -- 63 / Wimpod
  { espece = "jangmo_o", forme = 0, nom = "Bébécaille", gen = 7, mega_famille = false },  -- 64 / Jangmo-o
  { espece = "cosmog", forme = 0, nom = "Cosmog", gen = 7, mega_famille = false },  -- 65 / Cosmog
  { espece = "grookey", forme = 0, nom = "Ouistempo", gen = 8, mega_famille = false },  -- 66 / Grookey
  { espece = "scorbunny", forme = 0, nom = "Flambino", gen = 8, mega_famille = false },  -- 67 / Scorbunny
  { espece = "sobble", forme = 0, nom = "Larméléon", gen = 8, mega_famille = false },  -- 68 / Sobble
  { espece = "rookidee", forme = 0, nom = "Minisange", gen = 8, mega_famille = false },  -- 69 / Rookidee
  { espece = "nickit", forme = 0, nom = "Goupilou", gen = 8, mega_famille = false },  -- 70 / Nickit
  { espece = "applin", forme = 0, nom = "Verpom", gen = 8, mega_famille = false },  -- 71 / Applin
  { espece = "hatenna", forme = 0, nom = "Bibichut", gen = 8, mega_famille = false },  -- 72 / Hatenna
  { espece = "snom", forme = 0, nom = "Frissonille", gen = 8, mega_famille = false },  -- 73 / Snom
  { espece = "dreepy", forme = 0, nom = "Fantyrm", gen = 8, mega_famille = false },  -- 74 / Dreepy
  { espece = "growlithe", forme = 1, nom = "Caninos de Hisui", gen = 8, mega_famille = false },  -- 75 / Hisuian Growlithe
  { espece = "sneasel", forme = 1, nom = "Farfuret de Hisui", gen = 8, mega_famille = false },  -- 76 / Hisuian Sneasel
  { espece = "zorua", forme = 1, nom = "Zorua de Hisui", gen = 8, mega_famille = false },  -- 77 / Hisuian Zorua
  { espece = "sprigatito", forme = 0, nom = "Poussacha", gen = 9, mega_famille = false },  -- 78 / Sprigatito
  { espece = "fuecoco", forme = 0, nom = "Chochodile", gen = 9, mega_famille = false },  -- 79 / Fuecoco
  { espece = "quaxly", forme = 0, nom = "Coiffeton", gen = 9, mega_famille = false },  -- 80 / Quaxly
  { espece = "wooper", forme = 1, nom = "Axoloto de Paldea", gen = 9, mega_famille = false },  -- 81 / Paldean Wooper
  { espece = "pawmi", forme = 0, nom = "Pohm", gen = 9, mega_famille = false },  -- 82 / Pawmi
  { espece = "fidough", forme = 0, nom = "Pâtachiot", gen = 9, mega_famille = false },  -- 83 / Fidough
  { espece = "charcadet", forme = 0, nom = "Charbambin", gen = 9, mega_famille = false },  -- 84 / Charcadet
  { espece = "tinkatink", forme = 0, nom = "Forgerette", gen = 9, mega_famille = false },  -- 85 / Tinkatink
}
return M
