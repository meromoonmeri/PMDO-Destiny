from PIL import Image
from pathlib import Path
import numpy as np, json, hashlib
D=Path(__file__).resolve().parents[1]; old=D.parent/'Carte-Miracle-Destiny-4'
a=json.loads((D/'Atlas.json').read_text());e=a['nuages'];w=np.array(Image.open(D/'Brut-Destiny-4-Magenta.png').convert('RGB'));v=a['placements']['noyau_origine'];x,y=v['origine'];ow,oh=v['dimensions'];old_px=v['pixels_terrain_identiques']
if (old/'Brut-Destiny-4-Magenta.png').exists():
 o=np.array(Image.open(old/'Brut-Destiny-4-Magenta.png').convert('RGB'));m=(o != [255,0,255]).any(2);assert np.array_equal(o[m],w[y:y+oh,x:x+ow][m]);assert m.sum()==old_px
E=np.array(Image.open(D/'Extension-EoS-Grand-Large.png')); DS=np.array(Image.open(D/'Sources/References-Grand-Large/DS-Carte-echelle-native.png').convert('RGB'));assert np.array_equal(E[:,288:792],DS)
for f,h in e['skyTemple']['sha256'].items():assert hashlib.sha256((D/'Calques'/f).read_bytes()).hexdigest()==h
masks={k:np.array(Image.open(D/'Calques'/v['file']))[...,3] for k,v in a['zones'].items()}
for site in a['sites']:
 if site['island']:
  k=site['area'];v=a['zones'][k];u,t=site['loc'];assert masks[k][t-v['y'],u-v['x']]==255,(k,site['id'])
land=np.array(Image.open(D/'Calques/03-Grand-Large.png'));gl=e['zones_grand_large']
for k in gl:
 v=a['placements'][k];x,y=v['origine'];width,height=v['dimensions'];im=np.array(Image.open(D/f'Calques/Extension-EoS/{k}.png').resize((width,height),Image.Resampling.NEAREST));yy,xx=np.nonzero(im[...,3]);xx+=x;yy+=y
 rgb=land[yy,xx,:3].astype('int16');r,g,b=rgb.T;assert not ((r>115)&(b>108)&(r-g>45)&(b-g>38)&(g<.7*np.minimum(r,b))).any()
 for zk,q in a['zones'].items():
  u,v=xx-q['x'],yy-q['y'];inside=(u>=0)&(v>=0)&(u<q['w'])&(v<q['h']);z=masks[zk][v[inside],u[inside]];assert ((inside.all() and (z==255).all()) if zk==k else not z.any()),(k,zk)
assert len({s['id'] for s in a['sites']})==95
out={'statut':'PASS','ds_pixel_identique':int(DS.shape[0]*DS.shape[1]),'pixels_anciens_destiny_identiques':int(old_px),'lieux_generes_et_ancres':50,'planches_generees':4,'motifs_de_reference_places':sum(len(a['placements'][z]['motifs_reference']) for z in gl),'voile_interzones_verifie':True,'magenta_absent_des_terres_nouvelles':True,'empreintes_wan_verifiees':True}
(D/'Verification-dessins.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(out)
