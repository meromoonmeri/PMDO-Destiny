"""Export a short animated preview from two genuine player-captured cloud openings."""
from pathlib import Path
import json, subprocess

root=Path(__file__).resolve().parents[1]; report=json.loads((root/'Verification-video-nuages.json').read_text())
x,y,w,h=report['carte'];times={p['zone']:p['ms']/1000 for p in report['signals']}
filters=[]
for i,zone in enumerate(('torselune','volcans')):
 t=times[zone]
 filters.append(f'[0:v]trim=start={t-.25:g}:end={t+1.60:g},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},fps=12,scale=640:-2:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.50[c{i}]')
filters+=['[c0][c1]concat=n=2:v=1:a=0,split[v][p]', '[p]palettegen=stats_mode=diff:max_colors=224[pal]', '[v][pal]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle[out]']
out=root/'Apercu-Nuages-Destiny.gif'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(root/'Ouverture-des-nuages-Destiny.mp4'),'-filter_complex',';'.join(filters),'-map','[out]','-loop','0',str(out)],check=True)
print(out.name, f'{out.stat().st_size:,} octets')
