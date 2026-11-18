-- Retour des habitants à leurs rôles sans bloquer ni détourner le joueur.
local root = (arg[1] or '.') .. '/game/Data/Script/destiny/'
for _, key in ipairs({'origin.common', 'origin.menu.skill.SkillSelectMenu', 'origin.menu.team.AssemblySelectMenu',
                      'destiny.equipe_scene', 'destiny.cinematique', 'destiny.meteo_reverie', 'destiny.missions_reverie'}) do
  package.preload[key] = function() return {} end
end
local acteurs = {}
local function acteur(nom, x, y)
  acteurs[nom] = {EntName=nom, Position={X=x,Y=y}, EntEnabled=true}
  return acteurs[nom]
end
CH = function(nom) return acteurs[nom] end
local hero = acteur('PLAYER', 800, 1120)
local lombre = acteur('NewObject_7', 782, 1102)
local ludicolo = acteur('NewObject_8', 817, 1103)
local marchand = acteur('Kecleon', 620, 960)
local pose = {X=marchand.Position.X,Y=marchand.Position.Y}
local menu = {MenuCount=0}
local journal = {}
_DATA = {Save={CutsceneMode=false}}
SV = {Destiny={VisiteVille='terminee'}}
RogueEssence = {Menu={MenuManager={Instance=menu}}}
GROUND = {
  CharTurnToChar=function(_, a, b) journal[#journal+1] = {'tourne', a.EntName, b.EntName} end,
  CharSetEmote=function(_, a, emotion) journal[#journal+1] = {'emote', a.EntName, emotion} end,
}
SOUND = {PlayBGM=function() end}
GAME = {GetPlayerPartyCount=function() return 1 end, MoveCamera=function() end, FadeIn=function() end,
  CutsceneMode=function(_, b) _DATA.Save.CutsceneMode=b end}
local ville = assert(loadfile(root .. 'ground/WaterfallVillageCapital/init.lua'))()
local carte = {AssetName='reverie_centre'}
local function pas(n)
  for i=1,n do ville.Update(carte,i) end
end
local function reprendre()
  ville.Exit(carte)
  ville.Enter(carte)
  journal={}
end

ville.Enter(carte)
pas(131); assert(#journal==0)
pas(1); assert(#journal==2 and journal[1][2]==lombre.EntName and journal[2][1]=='emote')
pas(29); assert(#journal==2)
pas(1); assert(#journal==4 and journal[3][2]==ludicolo.EntName and journal[4][1]=='emote')

reprendre()
pas(132); assert(#journal==2)
menu.MenuCount=1
pas(30); assert(#journal==2, 'menu ouvert : la réponse doit être annulée')
menu.MenuCount=0
pas(89); assert(#journal==2)

reprendre()
_DATA.Save.CutsceneMode=true; pas(132); assert(#journal==0)
_DATA.Save.CutsceneMode=false
ludicolo.IsInteracting=true; pas(90); assert(#journal==0, 'le client ne doit pas être détourné du joueur')
ludicolo.IsInteracting=false
ludicolo.EntEnabled=false; pas(60); assert(#journal==0, 'PNJ caché : pas de discussion')
ludicolo.EntEnabled=true

reprendre()
hero.Position={X=630,Y=965}; pas(132)
assert(#journal==1 and journal[1][1]=='emote' and journal[1][2]==marchand.EntName)
assert(marchand.Position.X==pose.X and marchand.Position.Y==pose.Y, 'pas de déplacement du comptoir')
ville.Exit(carte); pas(700); assert(#journal==1, 'aucun geste différé sur une carte quittée')

reprendre()
hero.Position={X=1200,Y=2000}; pas(1000)
assert(#journal==0, 'pas d’émote hors de la zone visible')
print('PASS Réverie : réponses décalées, quartier visible, scènes et interactions prioritaires, comptoirs fixes.')
