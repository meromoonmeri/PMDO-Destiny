-- À lancer depuis la racine du dépôt : lua tools/tests/test_quiz_revelation.lua
-- Le moteur est simulé ici ; des essais en jeu complètent ce test.
-- Couvre : quiz_data.lua (20 questions PMD, choix de personnalité) et
-- revelation_etoile.lua (maintien du clic droit → étoile → révélation).

-- ------------------------------------------------------------------ outils
local function verifie(valeur, attendu)
  assert(valeur == attendu, tostring(valeur) .. ' ~= ' .. tostring(attendu))
end
local function contient(texte, fragment)
  return texte:find(fragment, 1, true) ~= nil
end

-- ------------------------------------------------------- quiz_data : format
local quiz_data = dofile('game/Data/Script/destiny/ground/personality_test/quiz_data.lua')

verifie(#quiz_data.questions, 20)

local natures_par_slug = {}
for _, n in ipairs(quiz_data.natures) do natures_par_slug[n.slug] = n end
verifie(#quiz_data.natures, 16)

local cinq_choix, oui_non, multi_phrases, dominantes = 0, 0, 0, {}
for numero, q in ipairs(quiz_data.questions) do
  assert(type(q.texte) == 'string' and #q.texte > 0, 'question ' .. numero)
  -- Aucun compteur « 12/20 » dans le texte affiché.
  assert(not q.texte:find('%d+/%d+'), 'compteur dans la question ' .. numero)
  local n = #q.choix
  assert(n >= 2 and n <= 5, 'choix hors bornes question ' .. numero)
  if n == 5 then cinq_choix = cinq_choix + 1 end
  if n == 2 then oui_non = oui_non + 1 end
  for _, c in ipairs(q.choix) do
    assert(type(c.texte) == 'string' and #c.texte > 0)
    if contient(c.texte, '\n') or #c.texte > 80 then multi_phrases = multi_phrases + 1 end
    local total, dominante, meilleur = 0, nil, 0
    for slug, pts in pairs(c.points) do
      assert(natures_par_slug[slug], 'nature inconnue ' .. tostring(slug) .. ' q' .. numero)
      assert(pts == 2 or pts == 4, 'points invalides q' .. numero)
      total = total + pts
      if pts > meilleur then dominante, meilleur = slug, pts end
    end
    verifie(total, 6) -- +4 dominante / +2 secondaire
    dominantes[dominante] = (dominantes[dominante] or 0) + 1
  end
end

-- Format PMD Sky / Red : majorité de questions à 5 choix de personnalité,
-- quelques « Oui / Non » et des réponses en plusieurs phrases.
assert(cinq_choix >= 14, '5 choix attendus sur la majorité des questions : ' .. cinq_choix)
assert(oui_non >= 2, 'questions oui/non attendues : ' .. oui_non)
assert(multi_phrases >= 5, 'réponses multi-phrases attendues : ' .. multi_phrases)

-- Chaque nature est la dominante d'au moins 3 choix pour équilibrer le score.
for _, n in ipairs(quiz_data.natures) do
  assert((dominantes[n.slug] or 0) >= 3, 'nature sous-représentée : ' .. n.slug)
end

-- mapping ↔ starters ↔ natures cohérents.
verifie((function() local c = 0; for _ in pairs(quiz_data.mapping) do c = c + 1 end; return c end)(), 16)
for slug, cle in pairs(quiz_data.mapping) do
  assert(natures_par_slug[slug], 'mapping : nature inconnue ' .. slug)
  assert(quiz_data.starters[cle], 'mapping : starter inconnu ' .. cle)
end

-- Couleurs de types pour la révélation (nom coloré du Pokémon).
for type_id, info in pairs(quiz_data.couleurs_types) do
  assert(info.hex:find('^#%x%x%x%x%x%x$'), 'hex invalide pour ' .. type_id)
  assert(type(info.fr) == 'string' and #info.fr > 0)
end
verifie(quiz_data.couleurs_types['fire'].hex, '#F08030')
verifie(quiz_data.couleurs_types['grass'].hex, '#78C850')

-- ------------------------------------------- revelation_etoile : moteur mock
package.loaded['destiny.ground.personality_test.quiz_data'] = quiz_data

local appels = {}
local function note(nom, ...)
  table.insert(appels, { nom = nom, args = { ... } })
end
local function positions(nom)
  local liste = {}
  for i, appel in ipairs(appels) do
    if appel.nom == nom then table.insert(liste, i) end
  end
  return liste
end
local maintien_actif = true
GAME = {
  IsInputDown = function(_, id) note('IsInputDown', id); return maintien_actif end,
  WaitFrames = function(_, n) note('WaitFrames', n) end,
  FadeOut = function(_, white, temps) note('FadeOut', white, temps) end,
  FadeIn = function(_, temps) note('FadeIn', temps) end,
}
UI = {
  WaitShowVoiceOver = function(_, texte) note('WaitShowVoiceOver', texte) end,
  WaitShowBG = function(_, nom, frameTime, fadeIn) note('WaitShowBG', nom, frameTime, fadeIn) end,
  WaitHideBG = function(_, temps) note('WaitHideBG', temps) end,
  TextPopUp = function(_, texte, ...) note('TextPopUp', texte) end,
  SetSpeaker = function(_, nom, keysound, espece, forme, skin, genre)
    note('SetSpeaker', nom, keysound, espece, forme, skin, genre)
  end,
  WaitShowDialogue = function(_, texte) note('WaitShowDialogue', texte) end,
  ResetSpeaker = function(_) note('ResetSpeaker') end,
}
SOUND = { PlayFanfare = function(_, nom) note('PlayFanfare', nom) end }
Gender = { Unknown = 0, Male = 1, Female = 2 }

local etoile = dofile('game/Data/Script/destiny/ground/personality_test/revelation_etoile.lua')

-- Constantes d'entrée : clic droit = 30 (FrameInput.InputType.RightMouse).
verifie(etoile.INPUT_CLIC_DROIT, 30)
verifie(etoile.INPUT_ACTION, 0)

-- Nom coloré selon le type (Element1) du Pokémon.
verifie(etoile.nom_colore('Goupix', 'fire'), '[color=#F08030]Goupix[color]')
verifie(etoile.nom_colore('Bulbizarre', 'grass'), '[color=#78C850]Bulbizarre[color]')
verifie(etoile.nom_colore('Inconnu', 'steel'), '[color=#B8B8D0]Inconnu[color]')

-- Type primaire lu sur la fiche du jeu.
_DATA = {
  GetMonster = function(_, id)
    verifie(id, 'vulpix')
    return { Forms = { [0] = { Element1 = 'fire' }, [1] = { Element1 = 'ice' } } }
  end,
}
verifie(etoile.type_du_starter({ espece = 'vulpix', forme = 0 }), 'fire')
verifie(etoile.type_du_starter({ espece = 'vulpix', forme = 1 }), 'ice')

-- Barre de progression : pleins puis vides, 10 cases.
verifie(etoile.barre(0, 150), 'Lumière de l\'étoile : [----------]')
verifie(etoile.barre(150, 150), 'Lumière de l\'étoile : [##########]')

-- Séquence complète, clic droit maintenu du début à la fin.
local starter = { espece = 'vulpix', forme = 0, nom = 'Goupix' }
appels = {}
maintien_actif = true
etoile.derouler(starter, { element = 'fire', besoin = 60 })

local function ordonnee(nom_a, nom_b)
  local a, b = positions(nom_a)[1], positions(nom_b)[1]
  assert(a and b and a < b, nom_a .. ' doit précéder ' .. nom_b)
end
ordonnee('FadeOut', 'WaitShowVoiceOver')
ordonnee('WaitShowVoiceOver', 'WaitShowBG')
-- paliers d'animation : 1 puis 2 puis 3 (60/2 = 30 frames maintenues)
local bg = {}
for _, i in ipairs(positions('WaitShowBG')) do
  local nom = appels[i].args[1]
  if nom:find('quiz_star_lumiere_', 1, true) then table.insert(bg, nom) end
end
verifie(#bg, 3)
verifie(bg[1], 'quiz_star_lumiere_1')
verifie(bg[2], 'quiz_star_lumiere_2')
verifie(bg[3], 'quiz_star_lumiere_3')
ordonnee('WaitShowBG', 'WaitHideBG')
-- étoile finale à la couleur du type + fanfare + portrait
local trouve_etoile, trouve_fanfare, trouve_speaker, trouve_revelation = false, false, false, false
for _, appel in ipairs(appels) do
  if appel.nom == 'WaitShowBG' and appel.args[1] == 'quiz_star_fire' then trouve_etoile = true end
  if appel.nom == 'PlayFanfare' and appel.args[1] == 'Fanfare/JoinTeam' then trouve_fanfare = true end
  if appel.nom == 'SetSpeaker' and appel.args[3] == 'vulpix' and appel.args[4] == 0 then trouve_speaker = true end
  if appel.nom == 'WaitShowDialogue' then
    local texte = appel.args[1]
    if contient(texte, "Quelqu'un comme toi serait")
      and contient(texte, '[color=#F08030]Goupix[color]') then
      trouve_revelation = true
    end
  end
end
assert(trouve_etoile, 'étoile quiz_star_fire absente')
assert(trouve_fanfare, 'fanfare absente')
assert(trouve_speaker, 'SetSpeaker (portrait) absent')
assert(trouve_revelation, 'texte de révélation coloré absent')
ordonnee('WaitShowBG', 'PlayFanfare')
ordonnee('PlayFanfare', 'SetSpeaker')
ordonnee('SetSpeaker', 'WaitShowDialogue')
ordonnee('WaitShowDialogue', 'ResetSpeaker')
ordonnee('ResetSpeaker', 'FadeIn')
-- la progression passe par la popup, jamais par un compteur de questions
local trouve_barre = false
for _, i in ipairs(positions('TextPopUp')) do
  if contient(appels[i].args[1], 'Lumière de l\'étoile') then trouve_barre = true end
end
assert(trouve_barre, 'barre de progression absente')

-- Maintien réel : IsInputDown(30) est bien interrogé (clic droit).
local trouve_clic = false
for _, i in ipairs(positions('IsInputDown')) do
  if appels[i].args[1] == 30 then trouve_clic = true end
end
assert(trouve_clic, 'GAME:IsInputDown(30) jamais appelé')

-- Sans maintien : la charge retombe, puis le secours termine l'animation
-- (personne ne reste bloqué si la souris ne répond pas).
appels = {}
maintien_actif = false
etoile.derouler(starter, { element = 'fire', besoin = 20, delai_secours = 40 })
local trouve_etoile2 = false
for _, appel in ipairs(appels) do
  if appel.nom == 'WaitShowBG' and appel.args[1] == 'quiz_star_fire' then trouve_etoile2 = true end
end
assert(trouve_etoile2, 'secours anti-blocage : animation non terminée')

print('test_quiz_revelation : OK')
