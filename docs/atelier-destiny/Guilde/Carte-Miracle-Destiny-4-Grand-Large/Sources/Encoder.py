"""Encode the filmed excerpt, with the existing discovery jingle only at filmed arrivals."""
from pathlib import Path
import subprocess,sys,json
D=Path(__file__).resolve().parents[1];C=Path(sys.argv[1]);cap=json.loads((C/'capture.json').read_text());duration=cap['frames']/cap['fps'];m=len(cap['signals']);assert m==2 and cap['ouvertures_reelles'] and cap['carte_entiere_non_affichee']
spec=['[1:a]asplit='+str(m)+''.join(f'[s{i}]' for i in range(m))];spec.extend(f'[s{i}]adelay={v["ms"]}:all=1[a{i}]' for i,v in enumerate(cap['signals']));spec.append(''.join(f'[a{i}]' for i in range(m))+f'amix=inputs={m}:normalize=0,apad,alimiter=limit=0.9:level=0:latency=1[son]')
mp4=D/'Destiny-4-Levee-des-nuages.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(cap['fps']),'-i',str(C/'%05d.jpg'),'-i',str(D/'Calques/Signal-Decouverte.mp3'),'-filter_complex',';'.join(spec),'-map','0:v','-map','[son]','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-preset','fast','-crf','22','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','118k','-ar','48000','-t',str(duration),'-movflags','+faststart',str(mp4)],check=True)
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]));v,a=p['streams'];assert int(v['nb_frames'])==cap['frames'] and v['codec_name']=='h264' and a['codec_name']=='aac' and v['pix_fmt']=='yuv420p'
(D/'Verification-video.json').write_text(json.dumps({'statut':'PASS','duree':duration,**cap},ensure_ascii=False,indent=2)+'\n');print(mp4.name,duration,'secondes',mp4.stat().st_size,'octets')
