#!/usr/bin/env python3
"""Contrôles statiques des entrées : ne remplacent pas le gameplay PMDO."""
from collections import deque
from pathlib import Path
import json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];GAME=ROOT/'game'
city=(GAME/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8')
assert city==(GAME/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8')
# nom, quartier, destination, marqueur, seuil de contact, retour joueur et partenaire
D=[('PortePosteBekipan','reverie_nord','reverie_post_office','entrance_south',56,504,32,8,80,528,56,528),('PorteCitrouilleNordOuest','reverie_nord','reverie_inn','Main_Entrance_Marker',400,592,48,8,432,616,408,616),('PorteHutteNordEst','reverie_nord','reverie_water_home','Main_Entrance_Marker',1048,648,32,8,1064,680,1040,680),('PorteDojoKingambit','reverie_nord','dojo_kingambit','MarowakDojoExitMarker',1440,392,48,8,1460,416,1436,416),('PorteHutteSud','reverie_centre','reverie_hutte_aquatique','Main_Entrance_Marker',648,1720,32,8,656,1744,680,1744),('PorteMaisonPierre','reverie_residentiel','reverie_rock_home','Main_Entrance_Marker',448,2336,32,8,456,2360,472,2344),('PorteMaisonPlanteSud','reverie_residentiel','reverie_grass_home','Main_Entrance_Marker',576,2544,24,8,584,2568,560,2568),('PorteCitrouilleSud','reverie_residentiel','reverie_fire_home','Main_Entrance_Marker',760,2528,40,8,776,2552,752,2552)]
assert 'PorteMaisonEquipe' not in city and 'PorteMaisonArcanine' not in city
assert "installer_contact_porte(map, 'PorteCafeSpinda', 1056, 1344, 32, 8)" in city
assert "ville[porte.nom .. '_Touch']" in city and 'function ville.PorteCafeSpinda_Touch' in city
assert "SV.Destiny.RetourBatimentPartenaire = nil" in city
cafe=(GAME/'Data/Script/destiny/ground/caféspindaaccueil/init.lua').read_text(encoding='utf8')
assert 'function cafespindaaccueil.PorteSortieCafe_Touch' in cafe and 'function cafespindaaccueil.PorteSortieCafe_Action' not in cafe
z=json.loads((GAME/'Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf-8-sig'))['Object']['GroundMaps']
for n,zone,dest,marker,x,y,w,h,rx,ry,px,py in D:
 line=next(l for l in city.splitlines() if "nom = '"+n+"'" in l)
 for snippet in (f"interieur = '{dest}'",f"marqueur = '{marker}'",f'retour_x = {rx}',f'retour_y = {ry}',f'contact_x = {x}',f'contact_y = {y}',f'contact_w = {w}',f'contact_h = {h}',f'partenaire_x = {px}',f'partenaire_y = {py}'):assert snippet in line,(n,snippet)
 assert zone in z and dest in z and (abs(rx-px)>=16 or abs(ry-py)>=16)
 interior=json.loads((GAME/'Data/Ground'/f'{dest}.rsground').read_text(encoding='utf-8-sig'))['Object'];markers=interior['Entities'][0]['Markers'];assert any(m['EntName']==marker for m in markers),(n,marker)
 pos=next(m['Collider'] for m in markers if m['EntName']==marker);grid=interior['obstacles'];ix,iy=pos['X'],pos['Y']
 assert all(grid[a][b]['Tags']==0 for a in range(ix//8,(ix+15)//8+1) for b in range(iy//8,(iy+15)//8+1)),(dest,'entrée bloquée')
for name in ['reverie_post_office','reverie_inn','reverie_water_home','reverie_rock_home','reverie_grass_home','reverie_fire_home','reverie_hutte_aquatique','dojo_kingambit']:
 text=(GAME/'Data/Script/destiny/ground'/name/'init.lua').read_text(encoding='utf8');assert 'sortie_en_cours = false; GAME:FadeIn(20)' in text,name
# Obstacle statique 16x16 : on atteint chaque capteur depuis les retours
# d'escaliers de son quartier, et chaque retour n'est pas dans le capteur.
starts={'reverie_nord':[(120,888),(776,808),(1200,808)],'reverie_centre':[(800,1320),(120,952),(776,872),(1200,872),(700,1904)],'reverie_residentiel':[(700,1976),(1120,2456)]}
for name,seeds in starts.items():
 raw=(GAME/'Data/Ground'/f'{name}.rsground').read_bytes();i=raw.index(b'"obstacles":')+len(b'"obstacles":');j=raw.index(b',"rand":',i);g=json.loads(raw[i:j]);grid=[bytes(c['Tags'] for c in col) for col in g];del g,raw
 def free(x,y):return 0<=x<=1584 and 0<=y<=3984 and all(grid[a][b]==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))
 seen=set(p for p in seeds if free(*p));q=deque(seen)
 while q:
  x,y=q.popleft()
  for p in ((x+4,y),(x-4,y),(x,y+4),(x,y-4)):
   if p not in seen and free(*p):seen.add(p);q.append(p)
 for n,zone,dest,marker,x,y,w,h,rx,ry,px,py in D:
  if zone!=name:continue
  assert free(rx,ry) and free(px,py),(n,'retour bloqué')
  assert all(not (a<x+w and a+16>x and b<y+h and b+16>y) for a,b in ((rx,ry),(px,py))),(n,'retour dans le capteur')
  assert any((a,y+h) in seen and a<x+w and a+16>x for a in range((x//4-4)*4,x+w,4)),(n,'contact inaccessible dans le quartier')
 print('PASS',name,'contacts et retours sur grille statique')
if shutil.which('lua5.4'):
 subprocess.run(['lua5.4',str(ROOT/'tools/tests/test_entrees_reverie.lua'),str(ROOT)],check=True)
else:print('Lua 5.4 absent : tests avec doublures à lancer séparément.')
print('PASS destinations, marqueurs, seuils, retours ; gameplay non testé')
