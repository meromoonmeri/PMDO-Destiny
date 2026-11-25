"""Register the exact WAN assets/timing used by the EoS Glacier (6 → 7) scene."""
from pathlib import Path
from hashlib import sha256
import shutil,json

def installer(src,calques,art):
    data=json.loads((src/'Calques/Trajectoires.json').read_text()); seq=next(t for t in data['transitions'] if t['palier']==7)
    poses={};mov=[];crcs={}
    for t in [*reversed(seq['petits_nuages']),seq['banc']]:
        i=data['sequences'][t['sequence']][0]['pose'];r=data['poses'][str(i)];p=src/r['fichier'];target=f'WAN-SkyTemple-{i:02}.png';key='sky'+str(i)
        if i not in poses:
            shutil.copyfile(p,calques/target);art[key]=target;crcs[target]=sha256(p.read_bytes()).hexdigest()
            poses[i]={'asset':key,'size':r['taille'],'offset':r['coin_relatif']}
        mov.append({'pose':i,'origine':t['origine'],'vitesse':t['vitesse_8_8']})
    out={'source':'s01p01a1.wan / SetMode(3), palier 6 → 7, Île Blizzard','revision':data['source'],'fps':data['rafraichissement_hz'],
         'noir_sortie':data['voile_noir_sortie_ticks'],'noir_entree':data['voile_noir_entree_ticks'],'compteur':data['compteur_objets_ticks'],'delai':data['delai_objets_ticks'],
         'centre_banc_ds':[96,280],'poses':poses,'objets':mov,'sha256':crcs}
    return out
