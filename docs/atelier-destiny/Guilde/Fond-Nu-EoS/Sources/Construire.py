"""Extract the bare PMDO file and the EoS cloud-only kit without editing either game.

Usage: pip install skytemple-files==1.8.5
       python Sources/Construire.py [--cache PATH] [--planche PATH]
"""
from __future__ import annotations
from argparse import ArgumentParser
from base64 import b64encode
from hashlib import sha256
from io import BytesIO
from itertools import chain
from pathlib import Path
from struct import unpack_from
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep
from PIL import Image
import json
import re
import shutil
from ExtraireWAN import decode, transitions

ROOT = Path(__file__).resolve().parents[1]
PRET = '9fa563873cec324993a614ea8ce03433add10e46'
PMDO = '37b2157ed730d958d83afe2fa1bb974570ecb46b'
BASE_SOURCE = f'https://raw.githubusercontent.com/meromoonmeri/projet-pmdo/{PMDO}/source/user_committed_map_background.png'
BASE_SHA = '67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3'
PRET_URL = f'https://raw.githubusercontent.com/pret/pmd-sky/{PRET}/'
NATIVE = 'files/MAP_BG/s01p01a.'
MARKERS = [15,25,30,35,42,47,68]
SIZE = (504,336)
DS = (256,192)


def frame_box(i):
    x = i%2*504
    y = i//2*336
    return x,y,x+504,y+336


def fetch(url, f):
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        for n in range(3):
            try:
                with urlopen(url, timeout=15) as r:
                    f.write_bytes(r.read())
                break
            except URLError:
                if n >= 2: raise
                sleep(n+1)
    return f


def digest(w):
    return sha256(w.read_bytes()).hexdigest()


def inline_png(p):
    return 'data:image/png;base64,' + b64encode(p.read_bytes()).decode('ascii')


def coordinates(p):
    text = p.read_text().split('\nMAP_MARKER_PLACEMENTS:', 1)[1]
    raw = b''.join(bytes.fromhex(' '.join(re.findall(r'0x([0-9a-fA-F]{2})\b',l)))
                   for l in text.splitlines()[:120] if l.strip().startswith('.byte'))
    E = lambda n: unpack_from('<4h', raw, n*8)
    def coords(n):
        m, alias, x, y = E(n)
        if alias >= 0 and alias != n:
            _, _, x, y = E(alias)
        return {'id':n,'carte':{268:'S01P01A',269:'S01P01B'}[m],'position':[x,y]}
    return {n:coords(n) for n in [*MARKERS,184]}


def main():
    from skytemple_files.common.types.file_types import FileType
    from skytemple_files.common.ppmdu_config.xml_reader import Pmd2XmlReader
    p = ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/atlas-eos-vierge')
    p.add_argument('--planche',type=Path,help='Optional user-provided Spriters Resource sheet for the pixel-by-pixel check')
    a = p.parse_args()
    cache = a.cache
    fetched = {}
    def game(rel):
        f=fetch(PRET_URL+rel,cache/'pret'/rel); fetched[rel]=digest(f); return f
    raw_base = fetch(BASE_SOURCE, cache/'projet-pmdo__user_committed_map_background.png')
    assert digest(raw_base) == BASE_SHA
    with Image.open(raw_base) as im:
        assert im.size == (556,366) and im.mode == 'RGB'
    blank = ROOT/'Fond-nu-EoS-556x366.png'
    shutil.copyfile(raw_base,blank)
    assert digest(blank)==BASE_SHA

    # Pillow 13 accepts a chain as a palette but its subsequent copy() needs a sequence.
    original = Image.Image.putpalette
    def fixed(img, data, *args, **kwargs):
        return original(img, list(data) if isinstance(data, chain) else data, *args, **kwargs)
    Image.Image.putpalette = fixed
    bma = FileType.BMA.deserialize(game(NATIVE+'bma').read_bytes())
    bpc = FileType.BPC.deserialize(game(NATIVE+'bpc').read_bytes(), tiling_width=bma.tiling_width,tiling_height=bma.tiling_height)
    bpl = FileType.BPL.deserialize(game(NATIVE+'bpl').read_bytes())
    assert bma.number_of_layers==2 and not bpl.has_palette_animation
    assert bpc.number_of_layers==2
    deck = bma.to_pil_single_layer(bpc,bpl.palettes,[None]*8,1)
    low = bma.to_pil_single_layer(bpc,bpl.palettes,[None]*8,0).convert('RGB')
    assert deck.size == low.size == (1008,1344)
    assert len({low.crop(frame_box(i)).tobytes() for i in range(8)})==1
    assert {i for _,i in deck.getcolors(16)} == {208,216,217,218,219,220}

    masks = ROOT/'Calques'/'Etats-fixes-504x336'
    objs = ROOT/'Calques'/'Sprites-mobiles'
    for target in (masks, objs): target.mkdir(parents=True,exist_ok=True)
    ref = Image.open(a.planche).convert('RGB') if a.planche else None
    statics=[]
    for i in range(8):
        layer = deck.crop(frame_box(i))
        mask = layer.point([0 if j%16 == 0 else 255 for j in range(256)],'L')
        rgba = layer.convert('RGBA'); rgba.putalpha(mask)
        # Zero out hidden RGB for interoperability, without modifying visible pixels.
        clear = Image.new('RGBA',SIZE); clear.alpha_composite(rgba)
        fn = masks/f'Palier-{i+1:02}.png'
        clear.save(fn,optimize=True)
        if ref:
            x,y=i%2*507,i//2*339
            compose = low.crop(frame_box(i)).convert('RGBA'); compose.alpha_composite(clear)
            assert compose.convert('RGB').tobytes()==ref.crop((x,y,x+504,y+336)).tobytes(),i
        coverage = mask.histogram()[255]
        statics.append({'palier':i+1,'origine_source':list(frame_box(i)[:2]),'fichier':str(fn.relative_to(ROOT)),
                        'pixels_voiles':coverage,'couverture':coverage/(504*336)})
    assert statics[-1]['pixels_voiles']==0
    assert sorted([x['pixels_voiles'] for x in statics],reverse=True)==[x['pixels_voiles'] for x in statics]

    wan = game('files/GROUND/s01p01a1.wan')
    table = game('asm/overlay_11_022ECD24_data.s')
    cams = coordinates(game('asm/main_rodata_020A2808.s'))
    positions = transitions(table)
    frames, sequences = decode(wan); sequences=sequences[:9]
    pal = {tuple(px[:3]) for p in (frames[:2]+frames[10:]) for _,px in p[0].getcolors(256) if px[3]}
    assert pal == {tuple(deck.getpalette()[i*3:i*3+3]) for i in (216,217,218,219,220)}
    pose_paths={}
    for sq in sequences:
        assert len(sq)==1 and sq[0]['ticks']==4 and sq[0]['offset']==[0,0]
        fid=sq[0]['pose']; im, anchored=frames[fid]; fn=objs/f'Pose-{fid:02}.png'; im.save(fn,optimize=True)
        pose_paths[str(fid)]={'fichier':str(fn.relative_to(ROOT)),'coin_relatif':list(anchored),'taille':list(im.size)}
    for rec, cam in zip(positions,MARKERS):
        rec['camera_test'] = cams[cam]
    # The regional test scripts have the same instruction/argument stream.
    scripts=[]
    for region,config in [('US','EoS_NA'),('EU','EoS_EU')]:
        path=game(f'files/language-specific/{region}/SCRIPT/V00P02/m01a06a.ssb')
        const=Pmd2XmlReader.load_default(config,translate_strings=False)
        s=FileType.SSB.deserialize(path.read_bytes(),const)
        ops=[(op.offset,op.op_code.name,[str(x) for x in op.params]) for op in s.routine_ops[0]]
        scripts.append(ops)
    assert scripts[0]==scripts[1]
    txt=(ROOT/'Sources'/'Script-test.exps')
    txt.write_text(s.to_explorerscript()[0],encoding='utf-8')
    needed = ['asm/overlay_11.s','asm/overlay_11_0230CE30.s','src/overlay_11_022E9A78.c',
              'asm/main_0200B33C.s','asm/main_rodata_020925A0.s','src/dungeon_init_2.c']
    for pth in needed: game(pth)
    native_fps=59.8261
    spec={'source':PRET,'taille_carte':SIZE,'taille_ecran_ds':DS,'rafraichissement_hz':native_fps,
          'voile_noir_sortie_ticks':16,'voile_noir_entree_ticks':16,'compteur_objets_ticks':240,'delai_objets_ticks':30,
          'coordonnees':'Pixels natifs, origine en haut à gauche. Les vitesses sont des entiers signés sur 8 bits fractionnaires, par image.',
          'etats':statics,'transitions':positions,'sequences':sequences,'poses':pose_paths}
    data=ROOT/'Calques'/'Trajectoires.json'
    data.write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    audit={'fond_nu':{'source':BASE_SOURCE,'identique_octet_par_octet':True,'sha256':BASE_SHA,'taille_px':[556,366]},
           'extraction':{'revision_pret':PRET,'sha256_sources':fetched,'calques_fixes':8,'poses_mobiles':len(pose_paths),
                         'calques_rgb_composes_identiques_planche':8 if ref else None,'couche_terrain_identique_aux_8_paliers':True,
                         'opcodes_et_arguments_US_EU_identiques':True,'instructions_test':len(scripts[0])},
           'contenu':{'geographie':None,'fond_dessin':str(blank.name),'coordonnees_destiny':None}}
    (ROOT/'Verification-assets.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n', encoding='utf-8')
    spec['fond']=inline_png(blank)
    for im in [*statics, *pose_paths.values()]: im['uri']=inline_png(ROOT/im['fichier'])
    src=ROOT/'Sources'
    template=(src/'Atelier.html').read_text(encoding='utf-8')
    page=template.replace('/*STYLE*/',(src/'Atelier.css').read_text(encoding='utf-8')).replace('/*DATA*/',json.dumps(spec,ensure_ascii=False,separators=(',',':'))).replace('/*SCRIPT*/',(src/'Atelier.js').read_text(encoding='utf-8'))
    (ROOT/'Fond-nu-et-nuages-EoS.html').write_text(page,encoding='utf-8')
    print('OK:',blank.name,len(positions),'transitions,',len(pose_paths),'sprites,',len(statics),'états, 0 terre')

if __name__=='__main__':
    main()
