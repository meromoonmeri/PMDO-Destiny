#!/usr/bin/env python3
"""A new pixel-cartographic rendering of the PSMD survey, with a tight Destiny start area.
No labels on art. Locations and routes live in the sidecar JSON, not in the painted pixels.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
from hashlib import sha256
import io, json, re, html
import numpy as np
from scipy import ndimage as nd
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1];G=ROOT.parent;USER=G.parent;W=Path.home()/'.cache/atlas-monde-destiny';W.mkdir(exist_ok=True);C=ROOT/'Calques';C.mkdir(exist_ok=True)
SIZE=(1536,1152);WIDTH,HEIGHT=SIZE;NN=Image.Resampling.NEAREST;BX=Image.Resampling.BOX;Y,X=np.indices((HEIGHT,WIDTH));Y=Y.astype('float32');X=X.astype('float32')
Z=4;RNG=np.random.default_rng(92);P=lambda col:tuple(bytes.fromhex(col));K=Image.open(W/'Sprites-reference-natifs.png').convert('RGBA')
OUT=ROOT/'Monde-Destiny-Sans-Texte-6144x4608.png';START=ROOT/'Reverie-Et-Ses-Donjons.png'

# PSMD atlas survey, then translated to the drawn 1536x1152 map. These Destiny pins are an
# authored placement, not a claim that the fangame has official worldwide coordinates.
SITES={
 'reverie':('Réverie Town',(1560,1138),32),
 'fosse':('Fosse Cascade',(1618,1100),23),
 'passage':('Passage Aquatique',(1537,1180),27),
 'guilde':('Falaise de la guilde',(1578,1079),19),
 'bois':('Bois Perdus',(1506,1116),22),
}

def xy(x,y):return round(x*.75),round(y*.75)
ANCHORS={k:xy(*r[1]) for k,r in SITES.items()}
CENTRE=ANCHORS['reverie'];START_BOX=(CENTRE[0]-141,CENTRE[1]-115,CENTRE[0]+147,CENTRE[1]+101)

def js(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def hashp(p):return sha256(Path(p).read_bytes()).hexdigest()
def layer(im,name):p=C/(name+'.png');im.save(p,optimize=True);return p

def imrgba(rgb,alpha):
    a=np.empty((*alpha.shape,4),np.uint8);a[...,:3]=rgb;a[...,3]=alpha;a[alpha==0]=0;return Image.fromarray(a)

def spec(a,l,r):return np.clip((a-l)/(r-l),0.,1.)
def smooth(a,l,r):u=spec(a,l,r);return u*u*(3-2*u)

@lru_cache(maxsize=1)
def geographic():
    a=Image.open(W/'Geographie-monde-originale.png').convert('RGB').resize(SIZE,BX);rgb=np.array(a).astype('float32');r,g,b=rgb.transpose(2,0,1)
    # The coastline is registered to Eddy's 2048 x 1536 coordinates. Keep snow, turquoise lakes,
    # miniature forest belts and the drawn geography instead of generating random continents.
    water=(b-r>26)&(b-g>4.5)&((r<123)|(b-g>22)) & (b>71)
    water=nd.binary_opening(water,np.ones((2,2))) | (water & (b-r>42) & (r<108))
    L,n=nd.label(water);big=np.bincount(L.ravel());big[0]=0
    ocean=L==int(np.argmax(big));ocean=nd.binary_closing(ocean,np.ones((3,3)),border_value=1)
    # Quiet, bright cyan basins only. The northwest's dark blue tree canopies must not
    # become lakes just because the old artwork used blue-green forest pigments.
    lake=water&~ocean&(g>144)&(b-r>34)&(r<136)
    quiet=nd.binary_opening(lake,np.ones((3,3)))
    ll,n=nd.label(quiet);ct=np.bincount(ll.ravel());ct[0]=0
    lake=(nd.binary_dilation(ct[ll]>=18,iterations=1)&lake)
    land=~ocean
    dist=nd.distance_transform_edt(land).astype('float32');dsea=nd.distance_transform_edt(ocean).astype('float32');
    snow=nd.gaussian_filter(((r>127)&(g>142)&(b>137)&(b>r+2)&land).astype('float32'),5.8)
    evergreen=spec(g-r+4,0,45)*spec(g-b,12,46)
    fogwood=(water&land&~lake).astype('float32')*spec(g,79,143)*.54
    green=nd.gaussian_filter(np.maximum(evergreen,fogwood),4.2)
    br=rgb@np.array([.24,.6,.16],dtype='float32');rough=nd.gaussian_filter(np.abs(br-nd.gaussian_filter(br,2.2)),2.6)
    rock=spec(rough,6.5,16.7)*(1-.44*green)
    flat=nd.gaussian_filter(spec(r-b,32,100)*spec(r-g,0,39),6.8)*(1-green)
    # Guarantee the new symbols' anchors are on their near-shore receiving land (except the
    # little path below the sea cave which ends in the actual bay).
    assert land.mean()>.25 and ocean.mean()>.45
    return rgb,ocean,land,lake,dist,dsea,snow,green,rock,flat


def grains():
    def noise(w,h):
        a=Image.fromarray(RNG.integers(0,255,(h,w),dtype=np.uint8));return (np.asarray(a.resize(SIZE,Image.Resampling.BILINEAR)).astype('float32')-128)/128
    sea=noise(39,29)*8+noise(125,94)*3.9+noise(13,10)*8.1
    v=RNG.random((HEIGHT,WIDTH),dtype='float32')-.48
    return sea+v*2.7


def frame_paper(rgb):
    a=np.clip(np.rint(rgb),0,255).astype(np.uint8)
    return Image.fromarray(a)


def ground():
    rgb,sea,land,lake,dt,ds,snow,wood,rock,flat=geographic();n=grains();red,g,b=rgb.transpose(2,0,1);lum=rgb@np.array([.236,.63,.134])
    # Deliberately small tonal changes on parchment, even on sea shallows. Fine squares are
    # printed like in the original EOS chart, not terrain collisions.
    grid=((X%55<1)|(Y%55<1)).astype('float32')*(.7+spec(n,-6,7)*.4)
    normal=nd.gaussian_filter(lum,2.3)
    topo=np.rint(np.clip((lum-normal)*.31,-14,14)/2)*2
    paper=np.stack([232+1.03*n-4*grid,178+1.25*n-5*grid,105+1.12*n-4*grid],axis=2)
    # Coastal washes in honey/sand; 1px ink along the crisp land edge.
    rim=(1-smooth(ds,0,10))*(sea);paper+=rim[...,None]*np.array([9,14,10]);paper[(ds==1)&sea]-=[18,29,23]
    relief=spec(normal,0,255);cliff=(.6*rock+.4*flat);v=(relief-.55)*30+n*.55+topo*.9
    earth=np.stack([209+v-44*wood+snow*17,167+v-4*wood+snow*24,92+v-12*wood+snow*74],axis=2)
    earth+=np.stack((flat*19-rock*13,flat*7-rock*10,flat*4+rock*4),axis=2)
    earth-=grid[...,None]*np.array([4,4,4])
    # Warmer / quieter clearing for the start, laid over its real slopes but not over water.
    cx,cy=CENTRE;valley=(1-smooth(np.hypot((X-cx)*.86,(Y-cy)),30,82))*(.76+.06*np.cos((X+Y)*.046))
    clear=np.stack([204+v*.44,174+v*.47,99+v*.52],axis=2);earth=earth*(1-valley[...,None])+clear*valley[...,None]
    u=np.where(land[...,None],earth,paper)
    u[(dt<=1.44)&land]-=[32,34,21]
    u[(dt>1.44)&(dt<=3.25)&land]+=[14,9,5]
    # Lakes are blue dashes rather than the blue ocean of the reference artwork.
    l=nd.distance_transform_edt(lake);p=spec(g,90,220)*12+n*.45
    aqua=np.stack([63+p*1.7,119+p,127+p*.95],axis=2);aqua[(l>0)&(l<1.5)]-=np.array([12,9,8]);u[lake]=aqua[lake]
    q=frame_paper(u)
    return q


def cut(r):
    a=K.crop(r);box=a.getbbox();assert box;return a.crop(box)

ASSETS={
 'mont':[(32,32,48,48),(83,31,109,48),(162,100,186,123)],
 'pic':[(193,52,222,79),(227,53,252,79),(164,63,189,80)],
 'desert':[(39,16,73,32),(188,101,207,123),(49,48,64,63)],
 'arbres':[(1,85,16,105),(17,85,32,97),(17,98,24,111),(24,104,32,113),(33,85,48,105),(49,85,64,97),(65,85,80,105),(81,85,96,97)],
 'buttes':[(4,65,27,80),(135,49,154,64),(112,49,128,64),(192,32,209,48),(129,65,144,79)],
 'plaine':[(113,65,127,73),(226,80,233,88),(170,80,187,94)],
 'nuage':[(210,0,252,24)],
 'tourbillon':[(116,0,141,17)],
 'volcan':[(3,4,28,27),(4,35,27,60)],'tour':[(162,0,176,18),(185,4,205,26)],'site':[(111,48,129,64),(134,47,154,64),(143,0,162,15),(128,100,159,125)],
}

@lru_cache(maxsize=180)
def icon(f,j,n,m=False):
    a=cut(ASSETS[f][j]);a=a.resize((n,max(4,round(a.height*n/a.width))),NN);a=ImageOps.mirror(a) if m else a
    q=np.array(a);a0=q[...,:3].astype(float)
    # Small sampled atlas icons share a quieter palette when distributed hundreds of times.
    a0=a0*.89+np.array([22,16,8]);q[...,:3]=np.rint(a0).clip(0,255);q[q[...,3]==0]=0
    return Image.fromarray(q)


def place(out,a,x,y):out.alpha_composite(a,(round(x-a.width/2),round(y-a.height)))


def scatter():
    s=Image.new('RGBA',SIZE);seed=np.random.default_rng(93853);_,sea,land,lake,dist,dsea,snow,wood,rock,flat=geographic()
    zones=[];keepout=np.zeros((HEIGHT,WIDTH),bool)
    # One compact region, with the rest of the world remaining on the same tiny icon scale.
    for x,y in ANCHORS.values():keepout |= ((X-x)/25)**2+((Y-y+8)/23)**2<1
    cx,cy=CENTRE;keepout |= (abs(X-cx)<52)&(abs(Y-cy)<19)
    for y in range(8,HEIGHT-5,12):
        for x in range(4,WIDTH-5,15):
            xx=int(np.clip(x+seed.integers(-6,7),3,WIDTH-3));yy=int(np.clip(y+seed.integers(-4,5),3,HEIGHT-3))
            if not land[yy,xx] or dist[yy,xx]<3.2 or keepout[yy,xx] or lake[yy,xx]:continue
            s0,g,r,a=[a[yy,xx] for a in (snow,wood,rock,flat)];p=seed.random();
            if s0>.37 and seed.random()<.67:k='pic';w=int(seed.integers(12,25))
            elif g>.36 and p<.77:
                k='arbres';w=int(seed.integers(8,19))
            elif r>.28 and p<.81:k='mont';w=int(seed.integers(12,25))
            elif a>.32 and p<.54:k='desert';w=int(seed.integers(10,26))
            elif p<.34:k='plaine' if p<.18 else 'buttes';w=int(seed.integers(6,16))
            else:continue
            j=int(seed.integers(0,len(ASSETS[k])))
            if k=='arbres':
                base=cut(ASSETS[k][j]);w=int(np.clip(round(base.width*seed.uniform(.70,1.00)),5,15))
            a=icon(k,j,w,bool(seed.random()>.64))
            if np.mean(land[max(0,yy-a.height):yy,max(0,xx-w//2):min(WIDTH,xx+(w+1)//2)])<.74:continue
            zones.append((yy,xx,a))
    # Twelve historical silhouettes accompany the new coast, without printed labels or pins.
    historic=[('Donjon des flammes','volcan',0,21,(1339,176)),('Grand Glacier','pic',2,24,(322,265)),('Tour du ciel','tour',0,15,(1294,60)),('Tour de l’île du Mystère','tour',0,17,(596,144)),('Volcan Géant','volcan',0,23,(987,714)),('Vestige de la tour','tour',1,20,(988,875)),('Village tranquille','site',0,18,(669,431)),('Cité de l’Eau','site',2,20,(830,422)),('Havre de l’Air','site',1,16,(1080,344)),('Halte du Sable','site',3,22,(239,936)),('Arbre du Monde','arbres',6,19,(1358,344)),('Cratère','volcan',1,19,(954,679))]
    for y,x,z in sorted(zones,key=lambda o:o[:2]):place(s,z,x,y)
    for _,kind,j,w,(x,y) in historic:place(s,icon(kind,j,w),x,y)
    return s,len(zones)+len(historic)


def glyph(what,width):
    if what=='bois':
        a=Image.new('RGBA',(32,21));a.alpha_composite(cut(ASSETS['arbres'][0]),(1,1));a.alpha_composite(cut(ASSETS['arbres'][6]),(14,3));
        d=ImageDraw.Draw(a);d.rectangle((12,14,17,18),fill='#5e4e37');d.rectangle((13,15,16,17),fill='#3b352a');d.point((13,18),fill='#c3a253');return a.resize((width,round(a.height*width/a.width)),NN)
    if what=='guilde':
        sheet=Image.open(G/'Falaise-Ombre-et-Lune/Calques/jour/Cime-au-premier-plan.png').convert('RGBA');sh=sheet.crop(sheet.getbbox());
        img=Image.open(G/'Falaise-Ombre-et-Lune/Plans/Cliff-jour.png').convert('RGB');a=Image.new('RGBA',(257,256));
        # The guild tracer keeps its actual oak silhouette, with a little cliff plinth at its feet.
        try:
            import sys
            sys.path.insert(0,str(G/'Comptoirs-et-Falaise/Sources'));from Falaise import obj
            a=obj('Object','Guilde_HD_Jour')[0].copy();a=a.crop(a.getbbox())
        except (FileNotFoundError,ImportError):a=sh
        a=a.resize((width,round(width*.93)),BX);b=Image.new('RGBA',(width+5,a.height+7));d=ImageDraw.Draw(b)
        d.polygon([(0,a.height-2),(4,a.height-6),(width+2,a.height-5),(width+4,a.height-2),(width,a.height+6),(5,a.height+6)],fill='#9f7544',outline='#765432')
        d.line((3,a.height-2,width+1,a.height-3),fill='#d0a861');d.line((5,a.height+2,width-2,a.height+1),fill='#bc8f51');d.line((6,a.height+4,width-1,a.height+4),fill='#86613f');d.rectangle((width//2-2,a.height-1,width//2+3,a.height+6),fill='#bc9559');d.line((width//2-2,a.height+2,width//2+3,a.height+2),fill='#73583d');d.line((width//2-2,a.height+5,width//2+3,a.height+5),fill='#e1b870');b.alpha_composite(a,(2,0));return b
    name={'reverie':'Reverie','fosse':'Fosse','passage':'Passage'}[what];img=Image.open(W/f'Symbole-{name}-brut.png').convert('RGB');q=np.asarray(img).astype('int16');r,g,b=q.transpose(2,0,1);key=(r>g+32)&(b>g+35)&(b>151)&(r>142)&(abs(r-b)<82)
    L,n=nd.label(~key,np.ones((3,3)));ct=np.bincount(L.ravel());ct[0]=0
    r0=int(L[702,890]) if what=='reverie' else int(np.argmax(ct));assert r0>0 and ct[r0]>2000,(name,r0,ct[r0])
    m=L==r0;res=imrgba(q.astype(np.uint8),m.astype(np.uint8)*255);a=res.crop(res.getbbox());a=a.resize((width,max(8,round(width*a.height/a.width))),BX)
    v=np.array(a);ok=v[...,3]>=120;v[~ok]=0;v[ok,3]=255
    pal=v[...,:3].astype(float);pal=pal*.91+np.array([13,8,4]);v[...,:3]=np.round(pal).clip(0,255);v[~ok]=0
    a=Image.fromarray(v).quantize(48,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).convert('RGBA')
    v=np.array(a);v[~ok]=0;v[ok,3]=255
    return Image.fromarray(v)

# All start-map routes are a hand laid, short web on the same littoral, not voyages.
ROUTES={
 'fosse':[(1560,1138),(1576,1134),(1587,1124),(1603,1120),(1618,1100)],
 'passage':[(1560,1138),(1553,1147),(1543,1153),(1539,1166),(1537,1180)],
 'guilde':[(1560,1138),(1549,1123),(1552,1106),(1563,1091),(1578,1079)],
 'bois':[(1560,1138),(1541,1141),(1524,1132),(1515,1124),(1506,1116)]
}

def tracks():
    a=Image.new('RGBA',SIZE);d=ImageDraw.Draw(a);_,sea,land,lake,dist,dsea,*_=geographic()
    for k,path in ROUTES.items():
        p=[xy(*v) for v in path];d.line(p,fill='#99804e',width=3,joint='curve');d.line(p,fill='#e6be80',width=1,joint='curve')
        for i,j in p[1:-1]:d.point((i-1,j),fill='#bb914f')
    # The water ribbon connects two pools but not the separate sea cave.
    rivers=[[(1214,824),(1210,826),(1202,828),(1194,824),(1188,821),(1179,822),(1173,828),(1167,830)],[(1159,852),(1161,860),(1166,865),(1172,872),(1172,878),(1170,888),(1172,900)]]
    for river in rivers:
        d.line(river,fill='#9c7e54',width=5,joint='curve');d.line(river,fill='#599ba1',width=3,joint='curve');d.line(river,fill='#83b4af',width=1,joint='curve')
    # Bridge planks on the village trail, wherever it crosses the exit ribbon.
    d.rectangle((1157,856,1165,858),fill='#a07844');d.line((1157,856,1165,856),fill='#d9af69');d.point((1161,857),fill='#856440')
    q=np.array(a);q[sea|(dist<1)]=0;return Image.fromarray(q)


def paper_fog():
    # Pale paper and etched clouds, like the concealed areas in the user's reveal sheet.
    rng=np.random.default_rng(7842);n=grains();col=np.stack([245+n*.42,213+n*.65,151+n*.73],axis=2);a=frame_paper(col).convert('RGBA')
    c=cut(ASSETS['nuage'][0]);al=c.getchannel('A');z=np.array(c);v=z[...,:3]@np.array([.2126,.7152,.0722]);R=np.where(v<178,210,np.where(v<218,231,247));g=np.where(v<178,163,np.where(v<218,192,220));b=np.where(v<178,105,np.where(v<218,126,162));n=np.stack([R,g,b],axis=2).astype(np.uint8);base=imrgba(n,np.rint(z[...,3]*.53).astype(np.uint8))
    outlines=Image.new('RGBA',SIZE)
    for yy in range(-12,HEIGHT,61):
        for xx in range(-16,WIDTH,79):
            if rng.random()<.18:continue
            x=xx+int(rng.integers(-14,31));y=yy+int(rng.integers(-8,22));w=int(rng.integers(27,80));z=base.resize((w,round(w*base.height/base.width)),NN);
            if rng.random()>.57:z=ImageOps.mirror(z)
            outlines.alpha_composite(z,(x,y))
    a.alpha_composite(outlines);layer(outlines,'Nuages-graves');return a.convert('RGB')


def wave_ink(z,seed=447):
    _,sea,land,lake,dist,dsea,*_=geographic();r=np.random.default_rng(seed);d=ImageDraw.Draw(z)
    for y in range(19,HEIGHT,33):
        for x in range(20,WIDTH,38):
            x0=x+int(r.integers(-12,13));y0=y+int(r.integers(-7,8))
            if dsea[y0,x0]<11 or r.random()<.56:continue
            a=int(r.integers(4,12));d.line([(x0,y0),(x0+a,y0),(x0+a+2,y0-1)],fill='#c78d56');d.line((x0+1,y0+1,x0+a-1,y0+1),fill='#edc089')
    for x,y in [(894,846),(620,1004),(1288,740),(389,637),(1310,392),(922,156)]:
        if not sea[y,x] or dsea[y,x]<15:continue
        p=icon('tourbillon',0,24).copy();v=np.array(p);v[...,:3]=[155,99,59];v[...,3]//=2;v[v[...,3]==0]=0;z.alpha_composite(Image.fromarray(v),(x-12,y-10))


def corners_soft(a):
    q=np.array(a).astype('float32');edge=np.minimum.reduce([X,Y,WIDTH-1-X,HEIGHT-1-Y]);u=(1-smooth(edge,-5,47))*0.16
    q[...,:3]=np.clip(q[...,:3]*(1-u[...,None])+np.array([199,138,79])*u[...,None],0,255);return Image.fromarray(q.astype('uint8'))


def build():
    terrain=ground().convert('RGBA');wave_ink(terrain);detail,count=scatter();assert count>700,count
    routes=tracks();symbols=Image.new('RGBA',SIZE);ps={};bboxes=[];z0=terrain.copy();z0.alpha_composite(detail);z0.alpha_composite(routes)
    for key,(title,_,w) in sorted(SITES.items(),key=lambda e:ANCHORS[e[0]][1]):
        ifirst=ANCHORS[key];a=glyph(key,w);x,y=ifirst;sl=[x-a.width//2,y-a.height];bbox=[*sl,sl[0]+a.width,sl[1]+a.height];
        # Keep the handmade site silhouettes distinct. No overlapping atlas cutouts.
        assert all(bbox[2]<=l or r<=bbox[0] or bbox[3]<=t or b<=bbox[1] for l,t,r,b in bboxes),(key,bbox,bboxes)
        bboxes.append(bbox);symbols.alpha_composite(a,tuple(sl));layer(a,'Lieu-'+key)
        ps[key]={'nom':title,'ancre':list(ifirst),'rectangle':bbox,'fichier':f'Calques/Lieu-{key}.png','distance_reverie':round(float(np.hypot(x-CENTRE[0],y-CENTRE[1])),2),'croquis_ia':key in ('reverie','fosse','passage')}
        if key!='reverie':assert 21<ps[key]['distance_reverie']<61
    total=z0.copy();total.alpha_composite(symbols);assert total.getextrema()[3]==(255,255)
    layer(terrain,'Parchemin-relief');layer(detail,'Reliefs-et-forets');layer(routes,'Sentiers-et-ruisseau');layer(symbols,'Lieux-Destiny');layer(paper_fog(),'Carte-non-devoilee');layer(z0.convert('RGB'),'Monde-sans-lieux');layer(total.convert('RGB'),'Monde-1x');
    total=total.convert('RGB');total.resize((WIDTH*Z,HEIGHT*Z),NN).save(OUT,compress_level=7);total.crop(START_BOX).resize(((START_BOX[2]-START_BOX[0])*5,(START_BOX[3]-START_BOX[1])*5),NN).save(START,optimize=True)
    a=total.resize((1152,864),Image.Resampling.BOX);a.save(W/'Carte-examen.png',optimize=True)
    raw=(W/'Eddy.html').read_text();m=re.findall(r'<[^<>]*class="poi marker"[^<>]+left:\s*(\d+)px;\s*top:\s*(\d+)px[^<>]*>\s*<img[^<>]+src="([^"]+)"[^<>]*>\s*<a href="([^"]+)"[^<>]*>(.*?)</a>',raw,re.S)
    reprs=[{'ancre':xy(int(x),int(y)),'serie':ico,'lien':url,'nom':html.unescape(re.sub('<[^>]+>',' ',n)).strip()} for x,y,ico,url,n in m]
    js(ROOT/'Reperes-separes.json',{'contenu':'Coordonnées uniquement ; aucune inscription sur les images et le film.', 'carte_px':SIZE,'plein_format_px':[WIDTH*Z,HEIGHT*Z],'echelle_png':Z,'cadre_depart':START_BOX,'lieux_destiny':ps,'chemins':{k:[xy(*v) for v in path] for k,path in ROUTES.items()},'decorations':count,'positions_eddy_reference_non_affichees':reprs,'croquis_generes_sha256':{k:hashp(W/f'Symbole-{k}-brut.png') for k in ('Reverie','Fosse','Passage')},'references':['https://eddyk28.github.io/PMD%20Map/','https://projectpokemon.org/home/gallery/image/74067-world-map/','uploads/image-10.png','Carte Explorateurs du Ciel fournie par l’utilisateur']})
    print(f'{count} vignettes de relief, {len(ps)} motifs Destiny ; proximité des donjons : '+', '.join(f'{k} {ps[k]["distance_reverie"]} px' for k in ('fosse','passage','bois')),flush=True)

if __name__=='__main__':build()
