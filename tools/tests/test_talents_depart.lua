-- À lancer depuis la racine du dépôt : lua tools/tests/test_talents_depart.lua
-- Le moteur est simulé ici ; des essais en jeu complètent ce test.
local definitions = {
  premier = { Released = true, nom = 'Premier' },
  second = { Released = true, nom = 'Second' },
  cache = { Released = true, nom = 'Caché' },
  inactif = { Released = false, nom = 'Inactif' },
}
for _, info in pairs(definitions) do
  function info:GetColoredName() return self.nom end
end

local forms = {
  [0] = { Intrinsic1 = 'premier', Intrinsic2 = 'second', Intrinsic3 = 'cache' },
  [1] = { Intrinsic1 = 'none', Intrinsic2 = 'second', Intrinsic3 = 'cache' },
  [2] = { Intrinsic1 = 'premier', Intrinsic2 = 'premier', Intrinsic3 = 'none' },
  [3] = { Intrinsic1 = 'inactif', Intrinsic2 = 'second', Intrinsic3 = 'cache' },
  [4] = { Intrinsic1 = '', Intrinsic2 = 'none', Intrinsic3 = nil },
  [5] = { Intrinsic1 = 'absent', Intrinsic2 = 'none', Intrinsic3 = 'cache' },
}
_DATA = {
  GetMonster = function(_, id) assert(id == 'test'); return { Forms = forms } end,
  GetIntrinsic = function(_, id) return definitions[id] end,
}

local reponses, menus, confirmations, messages = {}, {}, {}, {}
UI = {
  WaitShowVoiceOver = function(_, texte) table.insert(messages, texte) end,
  BeginChoiceMenu = function(_, texte, etiquettes, defaut, annulation)
    table.insert(menus, { texte = texte, etiquettes = etiquettes, defaut = defaut, annulation = annulation })
  end,
  ChoiceMenuYesNo = function(_, texte, defaut_non)
    table.insert(confirmations, { texte = texte, defaut_non = defaut_non })
  end,
  WaitForChoice = function() end,
  ChoiceResult = function()
    assert(#reponses > 0, 'réponse simulée manquante')
    return table.remove(reponses, 1)
  end,
}
local talent = dofile('game/Data/Script/destiny/talents_depart.lua')
local function reset(choix)
  reponses, menus, confirmations, messages = choix, {}, {}, {}
end
local function verifie(valeur, attendu) assert(valeur == attendu, tostring(valeur) .. ' ~= ' .. tostring(attendu)) end

-- Un refus permet de choisir un autre talent, notamment le talent caché.
reset({ 2, false, 3, true })
verifie(talent.choisir('test', 0, 'Exemple', 'héros'), 'cache')
verifie(#menus, 2); verifie(menus[1].texte, 'Choisis le talent du héros :\nExemple')
verifie(menus[1].etiquettes[3], 'Caché (caché)'); verifie(menus[2].defaut, 2)
verifie(confirmations[1].defaut_non, false); verifie(#reponses, 0)

-- La forme choisie, et pas seulement l'espèce, détermine les talents proposés.
reset({ 1, true })
verifie(talent.choisir('test', 1, 'Forme régionale', 'partenaire'), 'second')
verifie(menus[1].etiquettes[1], 'Second'); verifie(menus[1].etiquettes[2], 'Caché (caché)')
verifie(menus[1].texte, 'Choisis le talent du partenaire :\nForme régionale')

-- Un talent unique et les doublons : un seul choix reste visible et confirmé.
reset({ 1, true })
verifie(talent.choisir('test', 2, 'Unique', 'héros'), 'premier')
verifie(#menus[1].etiquettes, 1); verifie(#confirmations, 1)

-- Les talents non finalisés et manquants sont signalés et non proposés.
reset({ 2, true })
verifie(talent.choisir('test', 3, 'Test', 'partenaire'), 'cache')
verifie(#messages, 1); verifie(#menus[1].etiquettes, 2); verifie(menus[1].etiquettes[1], 'Second')
reset({ 1, true })
verifie(talent.choisir('test', 5, 'Test', 'héros'), 'cache')
verifie(#messages, 1); verifie(#menus[1].etiquettes, 1)

-- Filet de sécurité sans talent renseigné ; aucun effet inventé.
reset({})
verifie(talent.choisir('test', 4, 'Test', 'héros'), 'none')
verifie(#messages, 1); verifie(#menus, 0)
print('Tests des choix de talents : OK')
