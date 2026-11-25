import subprocess,os,sys
jobs=[('pcp','audit/zips_to_fetch.txt'),('gtp','audit/zips_to_fetch_gtp.txt')]
os.makedirs('stage/zips',exist_ok=True)
for repo,lst in jobs:
    for line in open(lst):
        oid,path=line.strip().split(' ',1)
        out='stage/zips/'+repo+'__'+path.replace('/','__')
        if os.path.exists(out) and os.path.getsize(out)>0: continue
        with open(out,'wb') as f:
            r=subprocess.run(['git','-C',repo,'cat-file','blob',oid],stdout=f)
        print(repo,path,os.path.getsize(out),r.returncode,flush=True)
print('ZIPS_DONE')
