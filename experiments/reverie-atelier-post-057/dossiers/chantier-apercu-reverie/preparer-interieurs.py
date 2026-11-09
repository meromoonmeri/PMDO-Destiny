from pathlib import Path
R=Path(__file__).resolve().parent; B=R/'travail/game/Data/Script/destiny/ground'
# Les destinations de ces salles appartiennent toutes au même segment Ground town02.
for name in ['reverie_electric_home','reverie_fire_home','reverie_grass_home','reverie_hutte_aquatique','reverie_inn','reverie_normal_home','reverie_post_office','reverie_rock_home','reverie_water_home','dojo_kingambit']:
 p=B/name/'init.lua';s=p.read_text();old="GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)";assert s.count(old)==1;s=s.replace(old,'GAME:EnterGroundMap(0, 0, true)');p.write_text(s)
for name in ['caféspindaaccueil','spindacaféétage1','spindacaféétage1salle2']:
 p=B/name/'init.lua';s=p.read_text();old="GAME:EnterZone('town02_waterfallvillage', -1, index_carte, 0)";assert s.count(old)==1;s=s.replace(old,'GAME:EnterGroundMap(index_carte, 0, true)')
 if name=='caféspindaaccueil':
  old="SV.Destiny.ArriveeVille = 'cafe'"; assert s.count(old)==1
  s=s.replace(old,"SV.Destiny.ArriveeVille = SV.Destiny.CafeRetourMemorise and 'batiment' or 'cafe'\n  SV.Destiny.CafeRetourMemorise = nil")
 p.write_text(s)
for name in ['WaterfallVillageCapital','WaterfallVillageCapital_Dev']:
 p=B/name/'init.lua';s=p.read_text()
 old="""function ville.PorteCafeSpinda_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if entree_batiment_en_cours then return end
  entree_batiment_en_cours = true
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 2, 0)
end"""
 new="""-- Capture les positions réellement occupées lorsque c'est sûr ; en cas de
-- contact avec le seuil, collision ou membre absent, conserve les replis
-- préexistants. Cela évite un retour qui déclencherait de nouveau la porte.
local function memoriser_retour_batiment(porte)
  SV.Destiny = SV.Destiny or {}
  local hx, hy = porte.retour_x, porte.retour_y
  local px, py = porte.partenaire_x or hx-28, porte.partenaire_y or hy
  local map, h, p = GAME:GetCurrentGround(), CH('PLAYER'), CH('Teammate1')
  local function admissible(a)
    if a == nil or a.Position == nil or map == nil then return false end
    local x,y=a.Position.X,a.Position.Y
    if math.abs(x-hx)>96 or math.abs(y-hy)>96 or not case_libre(map,x,y) then return false end
    if porte.contact_x ~= nil and x < porte.contact_x+porte.contact_w and x+16 > porte.contact_x
      and y < porte.contact_y+porte.contact_h and y+16 > porte.contact_y then return false end
    return true
  end
  if admissible(h) then hx,hy=h.Position.X,h.Position.Y end
  if admissible(p) and (math.abs(p.Position.X-hx)>=16 or math.abs(p.Position.Y-hy)>=16) then
    px,py=p.Position.X,p.Position.Y
  elseif math.abs(px-hx)<16 and math.abs(py-hy)<16 then
    -- Le repli du partenaire chevauche la position capturée : revenir aux
    -- deux points de sortie historiques prévus pour ce bâtiment.
    hx,hy=porte.retour_x,porte.retour_y
    px,py=porte.partenaire_x or hx-28,porte.partenaire_y or hy
  end
  SV.Destiny.MusiqueContinueMaison = true
  SV.Destiny.RetourBatimentX, SV.Destiny.RetourBatimentY = hx,hy
  SV.Destiny.RetourBatimentPartenaire = {x=hx,y=hy,px=px,py=py}
end

function ville.PorteCafeSpinda_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if entree_batiment_en_cours then return end
  entree_batiment_en_cours = true
  memoriser_retour_batiment({retour_x=1080,retour_y=1360,partenaire_x=1052,partenaire_y=1360,
    contact_x=1056,contact_y=1344,contact_w=32,contact_h=8})
  SV.Destiny.CafeRetourMemorise = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap(2, 0, true)
end"""
 assert s.count(old)==1;s=s.replace(old,new)
 old2="""    SV.Destiny.RetourBatimentX = porte.retour_x
    SV.Destiny.RetourBatimentY = porte.retour_y
    SV.Destiny.RetourBatimentPartenaire = {x=porte.retour_x, y=porte.retour_y, px=porte.partenaire_x or porte.retour_x-28, py=porte.partenaire_y or porte.retour_y}"""
 assert s.count(old2)==1;s=s.replace(old2,'    memoriser_retour_batiment(porte)')
 old3="GAME:EnterGroundMap('town02_waterfallvillage', porte.interieur, porte.marqueur)";assert s.count(old3)==1;s=s.replace(old3,"GAME:EnterGroundMap('town02_waterfallvillage', porte.interieur, porte.marqueur, true)")
 # Le moteur no-op déjà pour le même morceau en l'absence de fondu ;
 # cette garde évite aussi la modification d'un fondu musical déjà en cours.
 old4="  SOUND:PlayBGM('Treasure Town.ogg', true)\n  GAME:FadeIn(20)\n  retour_au_joueur(hero, partenaire)"
 assert s.count(old4)==1;s=s.replace(old4,"  if not SV.Destiny.MusiqueContinueMaison then SOUND:PlayBGM('Treasure Town.ogg', true) end\n  SV.Destiny.MusiqueContinueMaison = nil\n  GAME:FadeIn(20)\n  retour_au_joueur(hero, partenaire)")
 p.write_text(s)
assert (B/'WaterfallVillageCapital/init.lua').read_bytes()==(B/'WaterfallVillageCapital_Dev/init.lua').read_bytes()
print('PASS préparation locale : intérieurs, musique, retours et variantes')
