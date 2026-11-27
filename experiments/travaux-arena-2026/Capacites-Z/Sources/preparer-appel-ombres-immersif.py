#!/usr/bin/env python3
# Banc jetable : remplace l'ancien overlay Petal_Blizzard par une brume originale Spectre.
from pathlib import Path
from PIL import Image
import io,struct,json,subprocess,shutil
H=Path('/home/user');G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Appel-des-Ombres-Eternelles/Generation-PMDO'
subprocess.run(['python',str(H/'Capacites-Z/Sources/preparer-appel-ombres-multicibles.py')],check=True)
# Le générateur a produit une texture opaque ; on lui donne une transparence modérée.
# Répétition miroir pour éviter des ruptures franches au bord du pavage.
src=Image.open(P/'brume-spectrale-source.png').convert('RGBA').resize((128,72),Image.Resampling.NEAREST)
src.putalpha(108);tex=Image.new('RGBA',(256,144));tex.alpha_composite(src,(0,0));tex.alpha_composite(src.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(128,0));tex.alpha_composite(src.transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,72));tex.alpha_composite(src.transpose(Image.Transpose.ROTATE_180),(128,72))
name='Ombres_Eternelles_Brume';tex.save(P/(name+'.png'));b=io.BytesIO();tex.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',256,144,0,1));shutil.copy2(P/(name+'.dir'),G/'Content/BG'/(name+'.dir'))
f=P/'never_ending_nightmare-zone-test-only.json';d=json.loads(f.read_text());fx=d['Object']['HitboxAction']['ActionFX'];overlay=fx['Emitter'];assert 'FiniteOverlayEmitter' in overlay['$type'];overlay['Anim']['AnimIndex']=name;overlay['Anim']['Alpha']=230;overlay['Anim']['FrameTime']=1;overlay['Movement']={'X':10,'Y':-3};overlay['FadeIn']=15;overlay['FadeOut']=30;overlay['TotalTime']=145;overlay['Layer']=0
s=json.dumps(d,ensure_ascii=False,indent=2);(P/'never_ending_nightmare-immersif-test-only.json').write_text(s);(G/'Data/Skill/never_ending_nightmare.json').write_text(s)
print('Overlay BG Spectre sur tout le cadre, alpha modéré, fondu ; aucune image Petal_Blizzard.')
