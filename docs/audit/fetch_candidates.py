import json,subprocess,os,sys
idx=json.load(open('audit/rsground_index_all.json'))
names=['cliff_centre_01_grand_cap_panoramique_jour','cliff_centre_01_grand_cap_panoramique_nuit','cliffnordouesttest1','cliffnordouesttest1_nuit','etc1_tour_celeste','gma1_tour_celeste','gme1_tour_celeste','grotte_meteore_arene','grotte_meteore_entree','metano_gen_accueil','metano_gen_cafe','metano_gen_casino','metano_gen_salon_bas','metano_gen_salon_haut','metano_reseau_accueil','metano_reseau_cafe','metano_reseau_casino','metano_reseau_salon_bas','metano_reseau_salon_haut','rtc1_tour_celeste','stc1_tour_celeste','v50812_beach_cave_entrance_v2','spindacafetest','forest_magenta_v1','forest_render_v1','rvt_ne_jour','rvt_ne_nuit','rvt_no_jour','rvt_no_nuit','guild_path_\u0068alcyon','guild_path_\u0068alcyon_layers','guild_path_\u0068alcyon_palika','luminous_spring_pmdo','plage_pmd_sky_large','mer_houleuse_entree','mer_houleuse_sanctuaire','tour_celeste_relais','tour_du_temps_entree','tour_du_temps_pinacle']
extra=[('caféspindaaccueil','pcp','490832c343b3c40048a219b429661c21df0efe77','caféspindaaccueil.rsground'),('spindacaféétage1','pcp','0052a0ae668db36f072b18f169100172a7fdc152','spindacaféétage1.rsground'),('spindacaféétage1salle2','pcp','20b4fe53ca645833f5718fc8bbc58920ac525ab0','spindacaféétage1salle2.rsground')]
items=[]
for n in names:
    for repo,oid,path in idx[n]:
        if repo in ('pcp','gtp') and not path.startswith(('town02/','base/')) and '/references' not in path and '/refs/' not in path:
            items.append((n,repo,oid,path))
items+=extra
os.makedirs('stage/candidates',exist_ok=True)
done=set()
manifest=[]
for n,repo,oid,path in items:
    if oid in done: continue
    done.add(oid)
    out=f'stage/candidates/{n}__{oid[:8]}.rsground'
    if not os.path.exists(out):
        with open(out,'wb') as f:
            subprocess.run(['git','-C',repo,'cat-file','blob',oid],stdout=f,check=True)
    manifest.append({'name':n,'repo':repo,'oid':oid,'paths':sorted(set(p for nn,r,o,p in items if o==oid)),'file':out,'bytes':os.path.getsize(out)})
    print('ok',out,os.path.getsize(out),flush=True)
json.dump(manifest,open('audit/candidates_manifest.json','w'),ensure_ascii=False,indent=1)
print('FETCH_DONE',len(manifest))
