import subprocess,os,json,sys
OUT='stage/extra'
def cat(repo,oid,dest):
    os.makedirs(os.path.dirname(dest),exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest)>0: return
    with open(dest,'wb') as f:
        r=subprocess.run(['git','-C',repo,'cat-file','blob',oid],stdout=f)
    assert r.returncode==0,(repo,oid,dest)
def lstree(repo,commit,path):
    out=subprocess.run(['git','-C',repo,'-c','core.quotepath=false','ls-tree','-r',commit,'--',path],capture_output=True,text=True).stdout
    res={}
    for l in out.splitlines():
        meta,p=l.split('\t',1); res[p]=meta.split()[2]
    return res
log=[]
# 1. tour celeste packages (same commit a35f9a3d for etc1/rtc1 ; 106b6e49 for stc1)
for commit,pkg in [('a35f9a3d1a6136b45402ee1ca8a62dc56a2b6543','renders/tour_celeste_entree_v1/package'),('a35f9a3d1a6136b45402ee1ca8a62dc56a2b6543','renders/tour_celeste_relais_v1/package'),('106b6e49517e6cb6b2d107519c4e35b4b263e386','renders/tour_celeste_sommet_v1/package')]:
    t=lstree('pcp',commit,pkg)
    for p,o in t.items():
        rel=p[len(pkg)+1:]
        if rel.startswith('Content/Tile/') and rel.endswith('.tile') or rel.startswith('Data/Ground/') or rel.startswith('Content/BG/') or rel.startswith('Data/Script/'):
            cat('pcp',o,f'{OUT}/tour_celeste/{rel}'); log.append(('pcp',commit,p,o))
# 2. forest exports gtp
for commit,pkg in [('45d18a48033cdd7565754cfd52c69ec055fa4b46','exports/forest_cave_magenta_v1_pmdo'),('b2bf19202e3d01786f6e06c065153b0c0edf4273','exports/forest_cave_render_v1_pmdo')]:
    t=lstree('gtp',commit,pkg)
    for p,o in t.items():
        if p.endswith('.tile') or p.endswith('.rsground') or p.endswith('.dir') or p.endswith('.lua') or p.endswith('README.md'):
            rel=p[len(pkg)+1:]
            cat('gtp',o,f'{OUT}/forest/{rel}'); log.append(('gtp',commit,p,o))
# 3. rvt v1 exports: find tiles RVT_* in gtp exports
tidx=json.load(open('audit/tile_dir_index_all.json'))
for name in ['RVT_NE_JOUR_OBJETS','RVT_NE_NUIT_ANIM','RVT_NE_NUIT_OBJETS','RVT_NO_JOUR_OBJETS','RVT_NO_NUIT_ANIM','RVT_NO_NUIT_OBJETS']:
    occ=[x for x in tidx[name+'.tile'] if x[0]=='gtp']
    r,o,p=occ[0]; cat(r,o,f'{OUT}/rvt/Content/Tile/{name}.tile'); log.append((r,None,p,o))
# 4. town02 head tiles
for name in ['00_ciel','Altere_Pond_Cliffs','INVERSEPATHWAY','D06p11a_Base']:
    occ=[x for x in tidx[name+'.tile'] if x[0]=='town02']
    r,o,p=occ[0]; cat('town02',o,f'{OUT}/town02/Content/Tile/{name}.tile'); log.append((r,'origin/main',p,o))
# 5. nuit pack versions (commit 9d95a275 animated ; e6c22020 compat)
for commit,tag in [('9d95a27507f9f7935eaf7c838e368860be0a616b','nuit_animee'),('e6c22020842db6f0d8088e35953f3ab02ce15c42','nuit_compat')]:
    t=lstree('pcp',commit,'livrables_cliff_nord_nuit_pmdo/MOD_CLIFF_NORD_NUIT_PMDO')
    for p,o in t.items():
        rel=p.split('MOD_CLIFF_NORD_NUIT_PMDO/',1)[1]
        if rel.endswith(('.tile','.rsground','.dir','.lua')):
            cat('pcp',o,f'{OUT}/{tag}/{rel}'); log.append(('pcp',commit,p,o))
# 6. compat jour b40eaa93 (branch 637b0828 root)
cat('pcp','b40eaa93daaa3a7612d4350e85d6e7d9291338d7',f'{OUT}/jour_compat/Data/Ground/cliffnordouesttest1.rsground')
# 7. cliffdaytest_source (ppmdo root)
cat('ppmdo','cd276dab669a92521d2c2c417d39341d62616cd4',f'{OUT}/ppmdo/Data/Ground/cliffdaytest.rsground')
json.dump(log,open('audit/fetch_extra_log.json','w'),indent=0)
print('EXTRA_DONE',len(log))
