#!/usr/bin/env python3
"""18 bruitages d'entrée originaux (pas un pack de sons recolorés).

Sources mathématiques uniquement : frottements filtrés, impacts, grains
panoramiques, résonances, petits délais. Chaque type a sa propre partition.
Export PMDO : Battle/*.ogg Vorbis stéréo 44,1 kHz. Graine fixe par type.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt
from dojo_kingambit_troupes import TROUPES

SR=44100
DUREES=dict(normal=1.10,fire=1.18,water=1.27,grass=1.23,electric=1.07,ice=1.22,
            fighting=1.13,poison=1.32,ground=1.19,flying=1.05,psychic=1.58,bug=1.18,
            rock=1.20,ghost=1.28,dragon=1.32,dark=1.08,steel=1.25,fairy=1.37)


def fade(t,entree=.08,sortie=.17):
    return np.clip(t/entree,0,1)**2*(np.clip((1-t)/sortie,0,1)**2)


class Son:
    def __init__(self,typ):
        seed=403343+1073*list(TROUPES).index(typ)
        self.rng=np.random.default_rng(seed); self.bus=np.zeros((round(DUREES[typ]*SR),2))
    def time(self,dt): return np.arange(max(2,round(dt*SR)))/(dt*SR)
    def bruits(self,n,filtre):
        lo,hi=filtre
        x=sosfilt(butter(2,(lo,hi),btype='bandpass',fs=SR,output='sos'),self.rng.normal(0,1,n))
        return x/max(np.sqrt(np.mean(x*x)),1e-10)
    def mix(self,start,src,vol,pan):
        start=round(start*SR); n=min(len(self.bus)-start,len(src))
        if n<=0: return
        # Panoramique à puissance constante ; pan peut être une trajectoire.
        lr=(np.asarray(pan)+1)*np.pi/4
        if np.ndim(lr): lr=lr[:n]
        self.bus[start:start+n,:]+=vol*(src[:n,None]*np.stack((np.cos(lr),np.sin(lr)),axis=-1))
    def vent(self,start,dt,bands,vol,pan=(0,0),shape=(0,.30,.60,.32,0)):
        t=self.time(dt); out=np.zeros_like(t)
        piv=np.linspace(.02,.98,len(bands))
        for j,(lo,hi) in enumerate(bands):
            env=np.exp(-.5*((t-piv[j])/(.83/len(bands)))**2)
            out+=self.bruits(len(t),(lo,hi))*env
        out*=fade(t)*np.interp(t,np.linspace(0,1,len(shape)),shape)
        self.mix(start,out,vol,np.linspace(*pan,len(t)))
    def note(self,start,dt,f0,f1,vol,pan=0,decay=4.2,partiels=(1,),am=0,shape=1):
        t=self.time(dt)
        phase=2*np.pi*dt*np.cumsum(f0+(f1-f0)*t**shape)/len(t)
        osc=sum(rel*np.sin(phase*(i+1)) for i,rel in enumerate(partiels) if rel)
        env=fade(t,.028,.23)*np.exp(-decay*t)
        if am: env*=.62+.38*np.cos(2*np.pi*am*t*dt)
        self.mix(start,osc*env,vol,pan)
    def grain(self,start,dt,lo,hi,vol,pan=0,decay=2.5):
        t=self.time(dt)
        self.mix(start,self.bruits(len(t),(lo,hi))*np.exp(-decay*t)*fade(t,.06,.40),vol,pan)
    def echo(self,seconds,gain):
        n=round(seconds*SR); self.bus[n:,:]+=gain*self.bus[:-n,::-1].copy()
    def pcm(self):
        x=self.bus
        # Retire le continu, limite doucement les grains, puis bordures muettes.
        x=sosfilt(butter(2,40,'highpass',fs=SR,output='sos'),x,axis=0)
        x=np.tanh(1.45*x)
        x*=fade(self.time(len(x)/SR),.015,.055)[:,None]
        peak=np.max(np.abs(x)); assert peak>.025
        return (np.clip(x*.69/peak,-1,1)*32767).astype('<i2')


def normal(s):
    s.vent(.02,.85,[(180,550),(400,1300),(700,2200),(260,850)],.43,(-.55,.50))
    for i in range(3):
        s.grain(.30+i*.13,.18,220+i*47,650+i*180,.19/(1+i*.2),(-1)**i*.4)
        s.note(.30+i*.13,.19,140+i*13,80+i*7,.14/(1+i*.3),decay=5)
    s.echo(.115,.22)


def fire(s):
    s.vent(0,1.04,[(170,540),(250,1120),(620,2100),(400,1280)],.43,(-.15,.38),(0,.22,.78,.34,0))
    for i in range(19):
        t=.22+i*.039+s.rng.uniform(0,.032)
        s.grain(t,.052,1000+i*35,3200+i*49,.11+s.rng.uniform(0,.070),s.rng.uniform(-.55,.55))
    s.note(.42,.43,150,64,.25,am=29,partiels=(1,.23,.08))


def water(s):
    s.vent(.03,1.10,[(260,775),(530,1650),(1300,3600),(450,1100),(200,570)],.40,(-.58,.51),(0,.20,.72,.39,0))
    for i,p in enumerate((-.5,.5,-.35,.34,-.1,.2)):
        s.note(.19+i*.102,.17,263+i*71,760+i*94,.19,p,4,(1,.14),0,.48)
        if i>=2:s.grain(.26+i*.103,.12,1600+i*186,5400,.12,p)


def grass(s):
    s.vent(.01,1.00,[(190,820),(820,2400),(1300,5300),(480,2400)],.32,(-.45,.42))
    for i in range(9):
        s.grain(.15+i*.08,.074,1200+i*95,3400+i*160,.16,(-1)**i*.54,1.1)
    for i,f in enumerate((340,431,569,680)):
        s.note(.31+i*.112,.26,f,f*.91,.12,(-1)**i*.26,3,(1,.11,.08),9)


def electric(s):
    s.vent(.035,.86,[(1200,2500),(1800,5800),(3000,9000),(1100,4100)],.39,(-.2,.32),(0,.19,.82,.25,0))
    for i in range(7):
        s.grain(.22+i*.068,.066,2800+i*203,9800,.16 if i!=3 else .32,(-1)**i*.41,1.4)
    s.note(.325,.38,980,222,.27,decay=3,partiels=(1,.51,.31,.15),am=81)
    s.echo(.083,.12)


def ice(s):
    s.vent(.02,.96,[(290,1000),(910,3170),(1900,6500),(910,3500)],.33,(-.52,.60))
    for i,hz in enumerate((671,1083,1329,1946,1535,2215)):
        s.note(.25+i*.105,.37,hz,hz*.989,.14,(-1)**i*.44,3.4,(1,.04,.26))
        if i in (2,4):s.grain(.19+i*.105,.057,2200,8200,.18,(-1)**i*.23)
    s.echo(.09,.18)


def fighting(s):
    s.vent(.04,.56,[(230,720),(620,2200),(1100,3650)],.44,(-.64,.49),(0,.32,.69,.24,0))
    for i,start in enumerate((.40,.56,.71)):
        s.note(start,.32,139-i*12,48,.36-i*.05,(-1)**i*.29,5,(1,.24,.04))
        s.grain(start,.175,330,1420,.27-i*.04,(-1)**i*.29,3.0)


def poison(s):
    s.vent(.02,1.13,[(150,440),(440,990),(850,2350),(110,540)],.35,(-.39,.45),(0,.39,.64,.42,0))
    s.note(.22,.65,161,108,.25,.02,1.9,(1,.1,.23),23)
    for i in range(6):
        s.note(.23+i*.116,.16,280+i*47,89+i*26,.18,(-1)**i*.47,3.1,(1,.09),7,.6)
        s.grain(.37+i*.109,.105,780,3200,.13,(-1)**i*.4)


def ground(s):
    s.vent(0,1.04,[(110,350),(190,860),(580,1530),(340,1020)],.37,(-.4,.51),(0,.34,.67,.48,0))
    s.note(.29,.70,112,44,.34,0,2.5,(1,.23,.13),31)
    for i in range(12):
        s.grain(.16+i*.061,.13,240+i*53,1200+i*113,.17,(-1)**i*(.22+i*.026),1.8)


def flying(s):
    s.vent(.006,.83,[(660,2450),(1450,4500),(630,2000),(260,1050)],.41,(-.72,.78),(0,.66,.82,.19,0))
    for i in range(3):
        s.note(.097+i*.105,.34,1480-i*162,564-i*60,.18,(-1)**i*.52,2.42,(1,.12),7)
        s.grain(.33+i*.12,.112,610,3100,.13,(-1)**i*.56)


def psychic(s):
    s.vent(.00,.334,[(300,950),(850,2300),(2100,4700)],.33,(-.32,.24))
    s.note(.083,.22,390,1350,.21,0,1.1,(1,.08,.23),25)
    # Coupe sèche : départ -> silence -> nouveau point d'impact.
    s.vent(.36,.81,[(480,1200),(1300,3660),(980,3200),(410,1550)],.39,(.48,-.43),(0,.22,.77,.31,0))
    for i,t in enumerate((.67,.77,.87)):
        s.note(t,.54,610+i*208,305+i*143,.23,(-1)**i*.35,3.25,(1,.32,.14),13)
    s.echo(.122,.19)


def bug(s):
    s.vent(.027,.97,[(350,1100),(920,2800),(1200,4100),(380,1580)],.35,(.39,-.46))
    for i in range(13):
        s.grain(.16+i*.057,.083,1650+i*10,3900+i*70,.15,(-1)**i*.42,1.7)
    s.note(.34,.53,279,368,.28,0,2.2,(1,.12,.27,.10),78)
    s.note(.50,.42,845,298,.14,.28,3.2,(1,.22),43)


def rock(s):
    s.vent(.026,.94,[(85,280),(290,900),(480,1330),(140,540)],.36,(-.38,.36),(0,.31,.81,.41,0))
    for i in range(7):
        s.note(.33+i*.092,.29,128+i*23,53+i*7,.23/(1+i*.19),(-1)**i*.27,4.1,(1,.41,.13),7)
        s.grain(.33+i*.091,.131,330+i*100,1550+i*130,.26/(1+i*.23),(-1)**i*.49)
    s.echo(.077,.17)


def ghost(s):
    s.vent(.017,1.15,[(90,290),(240,790),(460,1620),(90,540)],.36,(.37,-.58),(0,.17,.77,.4,0))
    s.note(.12,1.04,219,100,.20,-.27,1.0,(1,.22,.04),11,.56)
    s.note(.20,.92,159,76,.25,.29,1.4,(1,.17,.16),7,.73)
    s.note(.44,.65,371,269,.14,.11,2.1,(1,.07,.06),16)
    s.echo(.139,.25)


def dragon(s):
    s.vent(.019,1.12,[(105,396),(380,1260),(980,3000),(320,960)],.37,(-.6,.57),(0,.37,.71,.4,0))
    s.note(.17,.94,106,65,.34,-.18,1.6,(1,.69,.28,.23,.08),36)
    s.note(.36,.69,239,162,.16,.34,2.5,(1,.42,.24),13)
    for i in range(4):s.grain(.39+i*.13,.146,430+i*110,1490+i*290,.15,(-1)**i*.46)


def dark(s):
    s.vent(.025,.55,[(245,800),(1100,3400),(470,1700)],.47,(-.88,.79),(0,.30,.88,.29,0))
    s.vent(.36,.64,[(300,950),(960,3520),(170,680)],.31,(.71,-.69),(0,.19,.75,.19,0))
    s.note(.29,.46,311,87,.21,.13,3.22,(1,.21,.38),31)
    s.grain(.53,.22,630,2770,.20,-.52,3.4)


def steel(s):
    s.vent(.016,1.02,[(390,1140),(960,2100),(1800,5800),(750,2300)],.35,(-.34,.37))
    for i,(f,dt) in enumerate(((289,.47),(832,.38),(1239,.47),(1837,.42),(437,.38))):
        s.note(.28+i*.109,dt,f,f*.96,.22 if i<2 else .14,(-1)**i*.46,3.1,(1,.36,0,.12),19)
        s.grain(.32+i*.109,.068,1700,7200,.19 if i%2 else .12,(-1)**i*.24)
    s.echo(.119,.18)


def fairy(s):
    s.vent(.015,1.20,[(550,1580),(1300,3500),(1700,4400),(710,2900)],.30,(-.40,.40),(0,.53,.68,.29,0))
    for i,f in enumerate((669,877,1163,1502,1241,1767,985)):
        d=.31 if i%2 else .42
        s.note(.11+i*.126,d,f*.97,f*1.006,.13+(.035 if i>3 else 0),(-1)**i*.54,3.3,(1,.06,0,.10),5)
        s.grain(.20+i*.10,.098,1900+i*180,6200,.083,(-1)**i*.39)
    s.echo(.147,.22)


PARTITIONS=dict(normal=normal,fire=fire,water=water,grass=grass,electric=electric,ice=ice,fighting=fighting,
                poison=poison,ground=ground,flying=flying,psychic=psychic,bug=bug,rock=rock,ghost=ghost,
                dragon=dragon,dark=dark,steel=steel,fairy=fairy)


def run(out):
    out.mkdir(exist_ok=True,parents=True)
    for typ in TROUPES:
        s=Son(typ);PARTITIONS[typ](s);pcm=s.pcm()
        p=out/f'Kingambit_Whoosh_{typ}.ogg'
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-f','s16le','-ar',str(SR),
                        '-ac','2','-i','pipe:0','-map_metadata','-1','-fflags','+bitexact','-flags:a','+bitexact',
                        '-c:a','libvorbis','-q:a','5',str(p)],input=pcm.tobytes(),check=True)
        db=20*np.log10(np.sqrt(np.mean((pcm.astype(float)/32768)**2)))
        print(f'{typ:8s} {DUREES[typ]:.2f}s  {db:5.1f} dBFS rms  {p.stat().st_size:5d} octets')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    run(parser.parse_args().out)
