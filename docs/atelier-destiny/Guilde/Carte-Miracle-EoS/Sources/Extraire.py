"""Extract a read-only, minimal EoS Wonder Map demo. Python 3.11+, Pillow, skytemple-files==1.8.5, ffmpeg.
No ROM required. Downloads the individual resources cited in the dossier into a cache, not a game folder.
"""
from __future__ import annotations
from argparse import ArgumentParser
from hashlib import sha256
from itertools import chain
from pathlib import Path
from struct import iter_unpack, unpack_from
from urllib.parse import quote
from urllib.request import Request, urlopen
import json, re, shutil, subprocess, sys
from PIL import Image
from ExtraireWAN import decode, transitions

ROOT = Path(__file__).resolve().parents[1]
PRET = '9fa563873cec324993a614ea8ce03433add10e46'
BASE = 'https://raw.githubusercontent.com/pret/pmd-sky/'+PRET+'/'
BARE = 'https://raw.githubusercontent.com/meromoonmeri/projet-pmdo/37b2157ed730d958d83afe2fa1bb974570ecb46b/source/user_committed_map_background.png'
BARE_SHA = '67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3'
ARCHIVE = 'https://archive.org/download/pmd-eos-complete-soundtrack/'
FPS = 59.8261
SIZE=(504,336)

def fetch(url, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=35) as r:
            tmp=dest.with_suffix(dest.suffix+'.part'); tmp.write_bytes(r.read()); tmp.replace(dest)
    return dest

def digest(path): return sha256(path.read_bytes()).hexdigest()
def rel(path): return path.relative_to(ROOT).as_posix()
def dump(data, path): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def path(file):
    p=ROOT/'Calques'/file; p.parent.mkdir(parents=True,exist_ok=True); return p

def save(im,file,anchor=None):
    p=path(file); im.save(p,optimize=True)
    obj={'fichier':rel(p),'taille':list(im.size)}
    if anchor is not None: obj['coin_relatif']=list(anchor)
    return obj

def table(file):
    block=file.read_text().split('\nMAP_MARKER_PLACEMENTS:',1)[1].split('.global _020A9E80',1)[0]
    data=bytes(int(h,16) for l in block.splitlines() if l.strip().startswith('.byte') for h in re.findall(r'0x([0-9a-fA-F]{2})\b',l))
    rows=list(iter_unpack('<hhhh',data)); assert len(rows)==310
    result=[]
    for i,(m,a,x,y) in enumerate(rows):
        j=a if a not in (-1,i) else i
        _,_,rx,ry=rows[j]
        result.append({'id_script':i,'indice_resolu':j,'carte':m,'alias':None if a<0 else a,
                       'coordonnees_brutes':[x,y],'position':None if m<0 or rx<0 else [rx,ry]})
    return result

def bgs(game,FileType):
    # Pillow 13's copied P palettes require a sequence instead of itertools.chain.
    orig=Image.Image.putpalette
    Image.Image.putpalette=lambda img,s,*a,**k:orig(img,list(s) if isinstance(s,chain) else s,*a,**k)
    bma=FileType.BMA.deserialize(game('files/MAP_BG/s01p01a.bma').read_bytes())
    bpc=FileType.BPC.deserialize(game('files/MAP_BG/s01p01a.bpc').read_bytes(),bma.tiling_width,bma.tiling_height)
    bpl=FileType.BPL.deserialize(game('files/MAP_BG/s01p01a.bpl').read_bytes())
    assert bma.number_of_layers==bpc.number_of_layers==2
    try:
        low=bma.to_pil_single_layer(bpc,bpl.palettes,[None]*8,0).convert('RGB')
        high=bma.to_pil_single_layer(bpc,bpl.palettes,[None]*8,1)
    finally:
        Image.Image.putpalette=orig
    assert low.size==high.size==(1008,1344)
    terrain=low.crop((0,0,*SIZE)); masks={}
    for i in range(8):
        x=i%2*504;y=i//2*336;box=(x,y,x+504,y+336)
        assert low.crop(box).tobytes()==terrain.tobytes()
        pal=high.crop(box);rgba=pal.convert('RGBA');rgba.putalpha(pal.point([0 if j%16==0 else 255 for j in range(256)],'L'))
        im=Image.new('RGBA',SIZE);im.alpha_composite(rgba)
        if i in (4,5,6,7): masks[str(i+1)]=save(im,f'Brume/Palier-{i+1:02}.png')
    return save(terrain,'Carte-DS-S01P01A.png'),masks

def get_hero(game,FileType):
    md=FileType.MD.deserialize(game('files/BALANCE/monster.md').read_bytes())
    entry=md.entries[25]; assert entry.md_index==25 and entry.sprite_index==26
    bank=FileType.BIN_PACK.deserialize(game('files/language-specific/US/MONSTER/m_ground.bin').read_bytes())
    wan=FileType.WAN.deserialize(bytes(bank[entry.sprite_index]))
    out={}; seq=[]
    for anim in wan.anim_groups[0]:
        r=[]
        for f in anim.frames:
            p=f.frame_id
            if str(p) not in out:
                im,_=wan.render_frame(wan.frames[p]); bb=im.getbbox(alpha_only=True)
                frags=wan.frames[p].fragments
                minx=min(x.offset_x for x in frags);miny=min(x.offset_y for x in frags)
                assert bb is not None
                out[str(p)]=save(im.crop(bb),f'Pikachu/Marche-{p:02}.png',(minx+bb[0],miny+bb[1]))
            r.append({'pose':p,'ticks':f.duration,'offset':[f.offset_x,f.offset_y]})
        assert [f['ticks'] for f in r]==[8,10,8,10]
        seq.append(r)
    assert len(seq)==8 and len(out)==24
    return out,seq

def native_script_proof(game,FileType,Pmd2XmlReader):
    scenes={
     'P01P01A/s02p0101': [('worldmap_SetMode',3),('worldmap_SetLevel',6),('worldmap_ChangeLevel',7),('worldmap_SetCamera',47),('worldmap_BlinkMark',47),('worldmap_SetArrow',47),('me_Play',6),('WaitMe',6),('worldmap_SetLevel',8)],
     'G01P04A/m23a0101': [('worldmap_SetMode',1),('worldmap_SetMark',184),('worldmap_SetMark',36),('worldmap_SetCamera',184),('worldmap_MoveCamera',36),('worldmap_SetMessagePlace',36)],
    }
    proof={}
    for scene,wanted in scenes.items():
        regional={}
        # Retain instruction names/arguments, not the entire copyrighted dialogue.
        for reg,cfg in [('US','EoS_NA'),('EU','EoS_EU')]:
            rf=game(f'files/language-specific/{reg}/SCRIPT/{scene}.ssb'); xml=Pmd2XmlReader.load_default(cfg,translate_strings=False)
            ssb=FileType.SSB.deserialize(rf.read_bytes(),xml)
            rs=[(op.op_code.name, int(op.params[0])) for routine in ssb.routine_ops for op in routine if op.op_code.name.startswith('worldmap_') or (op.op_code.name in ('me_Play','WaitMe') and list(map(str,op.params))==['6'])]
            assert rs==wanted,(scene,reg,rs)
            regional[reg]=rs
        proof[scene]=regional
    return proof

def audio_clip(source,dest,start,length,slow=False):
    cmd=['ffmpeg','-hide_banner','-v','error','-y','-ss',str(start),'-i',str(source),'-map','0:a:0','-t',str(length*(2 if slow else 1)), '-ar','44100','-ac','2']
    if slow: cmd+=['-af','atempo=0.5']
    subprocess.run(cmd+['-c:a','libmp3lame','-b:a','128k','-map_metadata','-1',str(dest)],check=True)
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)]))
    assert data['streams'][0]['sample_rate']=='44100'
    return {'fichier':rel(dest),'duree':round(float(data['format']['duration']),6),'sha256':digest(dest)}

def main():
    from skytemple_files.common.types.file_types import FileType
    from skytemple_files.common.ppmdu_config.xml_reader import Pmd2XmlReader
    ap=ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path,default=Path.home()/'.cache/atlas-eos-vierge');ns=ap.parse_args()
    hashes={}
    def game(f):
        p=fetch(BASE+f,ns.cache/'pret'/f);hashes[f]=digest(p);return p
    original=fetch(BARE,ns.cache/'projet-pmdo__user_committed_map_background.png'); assert digest(original)==BARE_SHA
    bp=path('Fond-nu-EoS-556x366.png');shutil.copyfile(original,bp);assert Image.open(bp).size==(556,366)
    bare={'fichier':rel(bp),'taille':[556,366],'sha256':BARE_SHA}
    terrain,masks=bgs(game,FileType)
    locations=table(game('asm/main_rodata_020A2808.s'))
    located={}
    for i,name,pos in [(184,'Bourg-Trésor',[212,180]),(47,'Île Blizzard',[76,276]),(36,'Caverne Saline',[196,156])]:
        m=locations[i]; assert m['carte']==268 and m['position']==pos
        located[str(i)]=dict(m,nom=name)
    dump({'provenance':BASE+'asm/main_rodata_020A2808.s','unite':'pixel DS, position native avant caméra',
          'note':'Identifiants scripts (1…180 = identifiant donjon + 1). Alias résolu d’un saut. Ces lignes n’indiquent pas quels lieux une sauvegarde a ouverts.',
          'lieux_demonstration':located,'table_native':locations},path('Coordonnees-des-reperes.json'))
    of,os=decode(game('files/GROUND/s01p01a2.wan'))
    assert len(of)==10 and len(os)==15
    assert [r['pose'] for r in os[11]]==[2,9,4,9,2] and {r['ticks'] for r in os[11]}=={4}
    assert [r['pose'] for r in os[13]]==[5,6] and {r['ticks'] for r in os[13]}=={20}
    found={};names={2:'Repère-jaune',3:'Repère-bleu',4:'Repère-rouge',5:'Flèche-01',6:'Flèche-02',7:'Flèche-03',8:'Flèche-04',9:'Repère-jaune-atténué'}
    for i,n in names.items(): found[str(i)]=save(of[i][0],f'Repères/{n}.png',of[i][1])
    mf=game('asm/overlay_11_022ECD24_data.s');raw=mf.read_text().split('ov11_02323310:',1)[1];assert re.search(r'0x09, 0x08, 0x09, 0x08, 0x0B, 0x08',raw)
    tr=transitions(mf)[5];assert tr['palier']==7 and tr['banc']['ticks']==240 and len(tr['petits_nuages'])==4
    cf,cs=decode(game('files/GROUND/s01p01a1.wan'));cl={}
    for q in [tr['banc'],*tr['petits_nuages']]:
        seq=cs[q['sequence']];assert len(seq)==1 and seq[0]['offset']==[0,0]
        pose=seq[0]['pose'];q['pose']=pose
        if str(pose) not in cl:cl[str(pose)]=save(cf[pose][0],f'Brume/Nuage-mobile-{pose:02}.png',cf[pose][1])
    hposes,hseq=get_hero(game,FileType)
    proof=native_script_proof(game,FileType,Pmd2XmlReader)
    m=game('files/SOUND/ME/me0006.smd').read_bytes();assert m[:4]==b'smdl' and m[32:47]==b'ME_NUM_DUNGEON_'
    bank=game('files/SOUND/ME/me.swd').read_bytes();assert bank[:4]==b'swdl'
    bgm='011. Wigglytuff\'s Guild Remix.mp3';me='150. Area Uncovered.flac'
    j_src=fetch(ARCHIVE+quote(me),ns.cache/'audio'/me);b_src=fetch(ARCHIVE+quote(bgm),ns.cache/'audio'/bgm)
    audio={}
    for k,src,maxlen,title in [('me',j_src,1.609,'Jingle-ME-06'),('bgm',b_src,6.0,'Extrait-Guilde-Remix')]:
        audio[k]={}
        for rate,suffix in [('1',''),('0.5','-ralenti')]:
            audio[k][rate]=audio_clip(src,path(f'Audio/{title}{suffix}.mp3'),0,maxlen,rate=='0.5')
        audio[k]['source']=ARCHIVE+quote(src.name)
    spec={'version':1,'fps':FPS,'carte':[504,336],'ds':[256,192],'revision':PRET,'fond_nu':bare,'terrain':terrain,'masques':masks,
          'reperes':found,'sequences_reperes':{str(i):os[i] for i in [9,10,11,12,13,14]},'brume_mobile':cl,'transition':tr,
          'pikachu':{'espece':25,'index_wan':26,'groupe':0,'poses':hposes,'sequences':hseq},'lieux':located,'audio':audio,
          'deblocage':{'id':47,'palier_avant':6,'palier_apres':7,'fondu_initial':16,'change':54,'nuage_depart':70,'nuage_fin':310,
                       'texte2':376,'jingle':400,'fin_lecture':540,'ticks':555},
          'trajets':{'blizzard':{'depart':184,'but':47,'palier':8,'attente_depart':30,'canonique':False,'nom':'Île Blizzard'},
                     'saline':{'depart':184,'but':36,'palier':5,'attente_depart':60,'canonique':True,'nom':'Caverne Saline'}}}
    dump(spec,path('Animation.json'))
    dump({'revision_pret':PRET,'fond_identique':digest(bp)==BARE_SHA,'coordonnees':located,'table_n':len(locations),'obj_155_sequences':spec['sequences_reperes'],
          'poses_pikachu':len(hposes),'scene_ops_US_EU':proof,'source_son':{me:digest(j_src),bgm:digest(b_src)},'binaires_sha256':hashes},ROOT/'Verification-des-sources.json')
    print('Repères, nuages, Pikachu, deux scènes EU/US et deux extraits : OK')

if __name__=='__main__':main()
