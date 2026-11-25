-- Tests comportementaux Lua pour la tournee de reveil (doublures d'API).
local root = assert(arg[1])

package.preload['origin.common'] = function() return {} end
package.preload['destiny.guilde_effectif'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_effectif.lua'))()
end
package.preload['destiny.guilde_reveil'] = function()
  return assert(loadfile(root .. '/game/Data/Script/destiny/guilde_reveil.lua'))()
end

Gender = {Genderless = 0, Male = 1, Female = 2}
-- Index d'animation absents des planches (5 = Wake), pour tester les replis.
local indices_bloques = {}
RogueEssence = {
  Content = {
    GraphicsManager = {
      GetAnimIndex = function(nom)
        local index = ({Idle = 0, Walk = 1, Eat = 2, Pose = 3, Sleep = 4, Wake = 5})[nom]
        if index == nil then return -1 end
        return index
      end,
      GetChara = function(charid)
        return {
          GetReferencedAnimIndex = function(_, index)
            if indices_bloques[index] then return -1 end
            return index
          end,
        }
      end,
    },
  },
  Ground = {PoseGroundAction = function(pos, dir, index) return {index = index} end},
}

local evenements = {}
local function ev(k, ...) evenements[#evenements + 1] = {k, ...} end

local PRESENTS = {}
local function acteur(nom)
  PRESENTS[nom] = {
    EntName = nom,
    CurrentForm = {ToCharID = function() return nom .. '_CHARA' end},
    Position = {X = 3, Y = 4}, Direction = 0,
  }
  return PRESENTS[nom]
end
CH = function(nom) return PRESENTS[nom] end

GROUND = {
  CharSetEmote = function(_, a, id, cycles) ev('emote', a.EntName, id, cycles) end,
  CharSetAnim = function(_, a, nom, boucle) ev('anim', a.EntName, nom, boucle) end,
  CharEndAnim = function(_, a) ev('fin_anim', a.EntName) end,
  CharSetAction = function(_, a, action) ev('action', a.EntName, action.index) end,
}
GAME = {WaitFrames = function(_, n) ev('attente', n) end}
TASK = {
  BranchCoroutine = function(_, f) f() return {} end,
  JoinCoroutines = function() end,
}

local guilde = require 'destiny.guilde_effectif'
local reveil = require 'destiny.guilde_reveil'

local function indice(k, ...)
  local motif, nb = {}, select('#', ...)
  for i = 1, nb do motif[i] = (select(i, ...)) end
  for i, e in ipairs(evenements) do
    if e[1] == k then
      local ok = true
      for j = 1, nb do
        if motif[j] ~= nil and e[j + 1] ~= motif[j] then ok = false end
      end
      if ok then return i end
    end
  end
  return nil
end

local function compter(k, ...)
  local motif, nb, total = {}, select('#', ...), 0
  for i = 1, nb do motif[i] = (select(i, ...)) end
  for _, e in ipairs(evenements) do
    if e[1] == k then
      local ok = true
      for j = 1, nb do
        if motif[j] ~= nil and e[j + 1] ~= motif[j] then ok = false end
      end
      if ok then total = total + 1 end
    end
  end
  return total
end

local melofee = acteur('Melofee')
local draby = acteur('Draby')

-- 1. La tournee de reveil, dans l'ordre.
assert(reveil.Reveiller(melofee, draby) == true)
local sommeil = assert(indice('anim', 'Draby', 'Sleep'), 'le dormeur doit dormir')
local attente_sommeil = assert(indice('attente', reveil.SOMMEIL), 'un temps de sommeil')
local pose = assert(indice('action', 'Melofee'), 'la pose d Audino sur Melofee')
local cloche = assert(indice('emote', 'Melofee', 'reveil', reveil.SONNERIES), 'la cloche sonne')
local attente_cloche = assert(indice('attente', reveil.SONNERIE), 'la cloche dure')
local reveil_anim = assert(indice('anim', 'Draby', 'Wake'), 'le dormeur se reveille')
local attente_reveil = assert(indice('attente', reveil.REVEIL))
local debout = assert(indice('fin_anim', 'Draby'), 'le dormeur se releve')
local calot = assert(indice('emote', 'Melofee', 'pose_infirmiere', 0), 'le calot reprend apres la cloche')

assert(sommeil < attente_sommeil, 'on dort avant d attendre')
assert(attente_sommeil < pose, 'la pose vient apres le sommeil')
assert(pose < cloche, 'la cloche suit la pose')
assert(cloche < attente_cloche and attente_cloche < reveil_anim, 'la cloche precede le reveil')
assert(reveil_anim < attente_reveil and attente_reveil < debout, 'on se reveille puis on se releve')
assert(debout < calot, 'le calot ne revient qu a la fin')

-- 2. Une seule emotes a la fois : la cloche et le calot ne se chevauchent pas.
local emote_melofee = 0
for _, e in ipairs(evenements) do
  -- on ne compte que les emotes reellement posees (pas les effacements)
  if e[1] == 'emote' and e[2] == 'Melofee' and e[3] ~= '' then
    emote_melofee = emote_melofee + 1
  end
end
assert(emote_melofee == 2, 'deux emotes pour Melofee : la cloche puis le calot, recu ' .. emote_melofee)
assert(compter('emote', 'Melofee', 'pose_infirmiere') == 1, 'un seul calot')

-- 3. Dormeur sans animation Wake : sursaut par l'emote exclaim.
evenements = {}
indices_bloques[5] = true          -- la planche de Draby n'a pas « Wake »
assert(reveil.Reveiller(melofee, draby) == true)
indices_bloques[5] = nil
assert(compter('emote', 'Draby', 'exclaim', 1) == 1, 'sursaut quand Wake manque')
assert(compter('anim', 'Draby', 'Wake') == 0, 'aucune animation Wake')

-- 4. Tournee : on saute l'infirmiere et les absents.
evenements = {}
local nondali = acteur('Noctali')
local cizayox = acteur('Cizayox')
local dormeurs = reveil.Tournee(melofee, {'Melofee', 'Draby', 'Noctali', 'Cizayox', 'Cizayox_absent'}, {pause = 12})
assert(dormeurs == 3, 'trois dormeurs reveilles, recu ' .. tostring(dormeurs))
assert(compter('anim', 'Melofee', 'Sleep') == 0, 'l infirmiere ne se reveille pas elle-meme')
assert(compter('attente', 12) == 3, 'une pause entre chaque reveil')

print('guilde_reveil : 4 groupes de tests OK')
